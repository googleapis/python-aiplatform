# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Uploads a TensorBoard logdir to Vertex AI Tensorboard."""
import datetime
import functools
import os
import re
from typing import (
    Dict,
    List,
    Set,
)

import grpc
from tensorboard.uploader import upload_tracker
from tensorboard.uploader import util
from tensorboard.uploader.proto import server_info_pb2
from tensorboard.util import tb_logging
import tensorflow as tf

from google.cloud import storage
from google.cloud.aiplatform.compat.services import tensorboard_service_client_v1beta1
from google.cloud.aiplatform.compat.types import (
    tensorboard_data_v1beta1 as tensorboard_data,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_service_v1beta1 as tensorboard_service,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series_v1beta1 as tensorboard_time_series,
)
from google.cloud.aiplatform.tensorboard import uploader_utils
from google.protobuf import timestamp_pb2 as timestamp

TensorboardServiceClient = tensorboard_service_client_v1beta1.TensorboardServiceClient

logger = tb_logging.get_logger()


class ProfileRequestSender:
    """Helper class for building requests for the profiler plugin.

    The profile plugin does not contain values within even files like other
    event files do. In addition, these event files do not update once
    a new profile event occurs. The event is empty and only signals that a
    profile session exists.

    To verify the plugin, subdirectories need to be searched to confirm valid
    profile directories and files.

    This class is not threadsafe. Use external synchronization if
    calling its methods concurrently.
    """

    # The directory in which profiles are stored.
    PROFILE_DIR = "plugins/profile"

    def __init__(
        self,
        experiment_resource_name: str,
        api: TensorboardServiceClient,
        upload_limits: server_info_pb2.UploadLimits,
        blob_rpc_rate_limiter: util.RateLimiter,
        blob_storage_bucket: storage.Bucket,
        source_bucket: storage.Bucket,
        blob_storage_folder: str,
        tracker: upload_tracker.UploadTracker,
        logdir: str,
        run_resource_manager: uploader_utils.RunResourceManager,
    ):
        """Constructs ProfileRequestSender for the given experiment resource.

        Args:
          experiment_resource_name: Name of the experiment resource of the form
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}
          api: Tensorboard service stub used to interact with experiment resource.
          upload_limits: Upload limits for for api calls.
          blob_rpc_rate_limiter: a `RateLimiter` to use to limit write RPC frequency.
            Note this limit applies at the level of single RPCs in the Scalar and
            Tensor case, but at the level of an entire blob upload in the Blob
            case-- which may require a few preparatory RPCs and a stream of chunks.
            Note the chunk stream is internally rate-limited by backpressure from
            the server, so it is not a concern that we do not explicitly rate-limit
            within the stream here.
          blob_storage_bucket: A `storage.Bucket` to send all blob files to.
          source_bucket: The user's specified `storage.Bucket` to save events to.
          blob_storage_folder: Name of the folder to save blob files to within the blob_storage_bucket.
          tracker: Upload tracker to track information about uploads.
          logdir: The log directory for the request sender to search.
          run_resource_manager: Manages creation or retrieving of runs.
        """
        self._experiment_resource_name = experiment_resource_name
        self._api = api
        self._logdir = logdir
        self._tag_metadata = {}
        self._handlers = {}
        self._tracker = tracker
        self._run_to_file_request_sender: Dict[str, _FileRequestSender] = {}
        self._run_to_profile_loaders: Dict[str, _ProfileRunLoader] = {}
        self._run_resource_manager = run_resource_manager

        self._file_request_sender_factory = functools.partial(
            _FileRequestSender,
            api=api,
            rpc_rate_limiter=blob_rpc_rate_limiter,
            max_blob_request_size=upload_limits.max_blob_request_size,
            max_blob_size=upload_limits.max_blob_size,
            blob_storage_bucket=blob_storage_bucket,
            source_bucket=source_bucket,
            blob_storage_folder=blob_storage_folder,
            tracker=self._tracker,
        )

    def _is_valid_event(
        self, run_name: str,
    ):
        """Determines whether a profile session has occurred.

        Profile events are determined by whether a corresponding directory has
        been created for the profile plugin.

        Args:
            run_name: String representing the run name.

        Returns:
            True if is a valid profile plugin event, False otherwise.
        """

        if tf.io.gfile.isdir(self._profile_dir(run_name)):
            return True
        return False

    def _profile_dir(self, run_name: str):
        """Converts run name to full profile path.

        Args:
            run_name: Name of training run.

        Returns:
            Full path for run name.
        """
        return os.path.join(self._logdir, run_name, self.PROFILE_DIR)

    def send_request(self, run_name: str):
        """Accepts run_name and sends an RPC request if an event is detected.

        Args:
          run_name: Name of the training run. It should be previously validated
            that the run_name is a valid path which contains an event file.
        """

        if not self._is_valid_event(run_name):
            return

        # Create a profiler loader if one is not created.
        if run_name not in self._run_to_profile_loaders:
            self._run_to_profile_loaders[run_name] = _ProfileRunLoader(
                self._profile_dir(run_name)
            )

        if run_name not in self._run_resource_manager.run_to_run_resource:
            self._run_resource_manager.create_or_get_run_resource(run_name)

        if run_name not in self._run_to_file_request_sender:
            self._run_to_file_request_sender[
                run_name
            ] = self._file_request_sender_factory(
                self._run_resource_manager.run_to_run_resource[run_name].name
            )

        for prof_run, files in self._run_to_profile_loaders[
            run_name
        ].prof_run_to_files():
            try:
                event_time = datetime.datetime.strptime(prof_run, "%Y_%m_%d_%H_%M_%S")
            except ValueError:
                logger.warning(
                    "Could not get the datetime from profile run name: %s, "
                    "using current datetime instead. %s",
                    prof_run,
                )
                event_time = datetime.datetime.now()
            event_timestamp = timestamp.Timestamp().FromDatetime(event_time)

            self._run_to_file_request_sender[run_name].add_files(
                files=files,
                tag=prof_run,
                plugin="profile",
                event_timestamp=event_timestamp,
            )


class _ProfileRunLoader(object):
    """Loader for a profile runs within a training run.
    """

    # A regular expression for the naming of a profiling path.
    PROF_PATH_REGEX = r".*\/plugins\/profile\/[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}\/?$"

    def __init__(
        self, path: str,
    ):
        """Create a loader for profiling runs with a training run.

        Args:
            path: Path to the training run, which contains one or more profiling
                runs. Path should end with '/profile/plugin'.
        """
        self._path = path

        self._prof_runs_to_files: Dict[str, Set[str]] = {}

    def _path_filter(
        self, path: str,
    ):
        """Determine which paths we should upload.

        Paths written by profiler should be of form:
        /some/path/to/dir/plugins/profile/%Y_%m_%d_%H_%M_%S

        Args:
            path: string representing a full directory path.

        Returns:
            True if matches the filter, False otherwise.
        """
        if tf.io.gfile.isdir(path) and re.match(self.PROF_PATH_REGEX, path):
            return True
        return False

    def _path_to_files(self, prof_run: str, path: str) -> List[str]:
        """Generates files that have not yet been tracked.

        Files are generated by the profiler and are added to an internal
        dictionary. For files that have not yet been uploaded, we return these
        files.

        Args:
            prof_run: string of the profiling run name.
            path: directory of the profiling run.

        Returns:
            Files that have not been tracked yet.
        """

        files = []
        for file in tf.io.gfile.listdir(path):
            full_file_path = os.path.join(path, file)
            if full_file_path not in self._prof_runs_to_files[prof_run]:
                self._prof_runs_to_files[prof_run].add(full_file_path)
                files.append(full_file_path)
        return files

    def prof_run_to_files(self):
        """Map profile runs to new files that have been created by the profiler.

        Returns:
            A dictionary mapping the profiling path name to a list of files that
                which have not yet been tracked.
        """

        paths = tf.io.gfile.listdir(self._path)

        for path in paths:
            # Remove trailing slashes in path names
            path = path if not path.endswith("/") else path[:-1]

            full_path = os.path.join(self._path, path)
            if not self._path_filter(full_path):
                continue

            files = self._path_to_files(path, full_path)

            if files:
                yield (path, files)


class _FileRequestSender(object):
    """Uploader for file based items.

    This sender is closely related to the `_BlobRequestSender`, however it sends
    files, given a path. The APIs are slightly different in the data that is
    expected for file based requests.

    This class is not threadsafe. Use external synchronization if calling its
    methods concurrently.
    """

    def __init__(
        self,
        run_resource_id: str,
        api: TensorboardServiceClient,
        rpc_rate_limiter: util.RateLimiter,
        max_blob_request_size: int,
        max_blob_size: int,
        blob_storage_bucket: storage.Bucket,
        source_bucket: storage.Bucket,
        blob_storage_folder: str,
        tracker: upload_tracker.UploadTracker,
    ):
        self._run_resource_id = run_resource_id
        self._api = api
        self._rpc_rate_limiter = rpc_rate_limiter
        self._max_blob_request_size = max_blob_request_size
        self._max_blob_size = max_blob_size
        self._tracker = tracker
        self._time_series_resource_manager = uploader_utils.TimeSeriesResourceManager(
            run_resource_id, api
        )

        self._bucket = blob_storage_bucket
        self._folder = blob_storage_folder
        self._source_bucket = source_bucket

        self._new_request()

    def _new_request(self):
        """Declares the previous event complete."""
        self._files = []
        self._tag = None
        self._plugin = None
        self._event_timestamp = None

    def add_files(
        self,
        files: List[str],
        tag: str,
        plugin: str,
        event_timestamp: timestamp.Timestamp,
    ):
        """Attempts to add the given file to the current request.

        If a file does not exist, the file is ignored and the rest of the
        files are checked to ensure the remaining files exist. After checking
        the files, an rpc is immediately sent.

        Args:
            files: List of strings representing the path to the files to upload.
            tag: An identifier for the blob sequence.
            plugin: Name of the plugin making the request.
            event_timestamp: A `timestamp.Timestamp` object for the time the
                event is created.
        """

        for prof_file in files:
            if not tf.io.gfile.exists(prof_file):
                logger.warning(
                    "The file provided does not exist. "
                    "Will not be uploading file %s.",
                    prof_file,
                )
            else:
                self._files.append(prof_file)

        self._tag = tag
        self._plugin = plugin
        self._event_timestamp = event_timestamp
        self.flush()
        self._new_request()

    def flush(self):
        """Sends the current file fully, and clears it to make way for the next."""
        if not self._files:
            return

        time_series_proto = self._time_series_resource_manager.get_or_create(
            self._tag,
            lambda: tensorboard_time_series.TensorboardTimeSeries(
                display_name=self._tag,
                value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.BLOB_SEQUENCE,
                plugin_name=self._plugin,
            ),
        )
        m = re.match(
            ".*/tensorboards/(.*)/experiments/(.*)/runs/(.*)/timeSeries/(.*)",
            time_series_proto.name,
        )
        blob_path_prefix = "tensorboard-{}/{}/{}/{}".format(m[1], m[2], m[3], m[4])
        blob_path_prefix = (
            "{}/{}".format(self._folder, blob_path_prefix)
            if self._folder
            else blob_path_prefix
        )
        sent_blob_ids = []

        for prof_file in self._files:
            self._rpc_rate_limiter.tick()
            file_size = tf.io.gfile.stat(prof_file).length
            with self._tracker.blob_tracker(file_size) as blob_tracker:
                if not self._file_too_large(prof_file):
                    blob_id = self._copy_between_buckets(prof_file, blob_path_prefix)
                    sent_blob_ids.append(str(blob_id))
                    blob_tracker.mark_uploaded(blob_id is not None)

        data_point = tensorboard_data.TimeSeriesDataPoint(
            blobs=tensorboard_data.TensorboardBlobSequence(
                values=[
                    tensorboard_data.TensorboardBlob(id=blob_id)
                    for blob_id in sent_blob_ids
                ]
            ),
            wall_time=self._event_timestamp,
        )

        time_series_data_proto = tensorboard_data.TimeSeriesData(
            tensorboard_time_series_id=time_series_proto.name.split("/")[-1],
            value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.BLOB_SEQUENCE,
            values=[data_point],
        )
        request = tensorboard_service.WriteTensorboardRunDataRequest(
            time_series_data=[time_series_data_proto]
        )

        _prune_empty_time_series_from_blob(request)
        if not request.time_series_data:
            return

        with uploader_utils.request_logger(request):
            try:
                self._api.write_tensorboard_run_data(
                    tensorboard_run=self._run_resource_id,
                    time_series_data=request.time_series_data,
                )
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    raise uploader_utils.ExperimentNotFoundError()
                logger.error("Upload call failed with error %s", e)

    def _file_too_large(self, file):
        file_size = tf.io.gfile.stat(file).length
        if file_size > self._max_blob_size:
            logger.warning(
                "Blob too large; skipping.  Size %d exceeds limit of %d bytes.",
                file_size,
                self._max_blob_size,
            )
            return True
        return False

    def _copy_between_buckets(self, file, blob_path_prefix):
        """Move files between the user's bucket and the tenant bucket."""
        blob_id = os.path.basename(file)
        blob_name = _get_blob_from_file(file)

        source_blob = self._source_bucket.blob(blob_name)

        blob_path = (
            "{}/{}".format(blob_path_prefix, blob_id) if blob_path_prefix else blob_id
        )

        self._source_bucket.copy_blob(
            source_blob, self._bucket, blob_path,
        )

        return blob_id


def _get_blob_from_file(fp):
    m = re.match(r"gs:\/\/.*?\/(.*)", fp)
    if not m:
        logger.warning("Could not get the blob name from file %s", fp)
        return None
    return m[1]


def _prune_empty_time_series_from_blob(
    request: tensorboard_service.WriteTensorboardRunDataRequest,
):
    """Removes empty time_series from request if there are no blob files."""
    for (time_series_idx, time_series_data) in reversed(
        list(enumerate(request.time_series_data))
    ):
        if not any(x.blobs for x in time_series_data.values):
            del request.time_series_data[time_series_idx]
