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
"""Uploads a TensorBoard logdir to TensorBoard.gcp."""
import contextlib
import functools
import json
import os
import time
import re
from typing import Callable, Dict, FrozenSet, Generator, Iterable, Optional, Tuple
import uuid

import grpc
from tensorboard.backend import process_graph
from tensorboard.backend.event_processing.plugin_event_accumulator import (
    directory_loader,
)
from tensorboard.backend.event_processing.plugin_event_accumulator import (
    event_file_loader,
)
from tensorboard.backend.event_processing.plugin_event_accumulator import io_wrapper
from tensorboard.compat.proto import graph_pb2
from tensorboard.compat.proto import summary_pb2
from tensorboard.compat.proto import types_pb2
from tensorboard.plugins.graph import metadata as graph_metadata
from tensorboard.uploader import logdir_loader
from tensorboard.uploader import upload_tracker
from tensorboard.uploader import util
from tensorboard.uploader.proto import server_info_pb2
from tensorboard.util import tb_logging
from tensorboard.util import tensor_util
import tensorflow as tf

from google.api_core import exceptions
from google.cloud import storage
from google.cloud.aiplatform.compat.services import tensorboard_service_client_v1beta1
from google.cloud.aiplatform.compat.types import (
    tensorboard_data_v1beta1 as tensorboard_data,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_experiment_v1beta1 as tensorboard_experiment,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_run_v1beta1 as tensorboard_run,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_service_v1beta1 as tensorboard_service,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series_v1beta1 as tensorboard_time_series,
)
from google.protobuf import message
from google.protobuf import timestamp_pb2 as timestamp

TensorboardServiceClient = tensorboard_service_client_v1beta1.TensorboardServiceClient

# Minimum length of a logdir polling cycle in seconds. Shorter cycles will
# sleep to avoid spinning over the logdir, which isn't great for disks and can
# be expensive for network file systems.
_MIN_LOGDIR_POLL_INTERVAL_SECS = 1

# Maximum length of a base-128 varint as used to encode a 64-bit value
# (without the "msb of last byte is bit 63" optimization, to be
# compatible with protobuf and golang varints).
_MAX_VARINT64_LENGTH_BYTES = 10

# Default minimum interval between initiating WriteTensorbordRunData RPCs in
# milliseconds.
_DEFAULT_MIN_SCALAR_REQUEST_INTERVAL = 10

# Default maximum WriteTensorbordRunData request size in bytes.
_DEFAULT_MAX_SCALAR_REQUEST_SIZE = 24 * (2 ** 10)  # 24KiB

# Default minimum interval between initiating WriteTensorbordRunData RPCs in
# milliseconds.
_DEFAULT_MIN_TENSOR_REQUEST_INTERVAL = 10

# Default minimum interval between initiating WriteTensorbordRunData RPCs in
# milliseconds.
_DEFAULT_MIN_BLOB_REQUEST_INTERVAL = 10

# Default maximum WriteTensorbordRunData request size in bytes.
_DEFAULT_MAX_TENSOR_REQUEST_SIZE = 512 * (2 ** 10)  # 512KiB

_DEFAULT_MAX_BLOB_REQUEST_SIZE = 4 * (2 ** 20) - 256 * (2 ** 10)  # 4MiB-256KiB

# Default maximum tensor point size in bytes.
_DEFAULT_MAX_TENSOR_POINT_SIZE = 16 * (2 ** 10)  # 16KiB

_DEFAULT_MAX_BLOB_SIZE = 10 * (2 ** 30)  # 10GiB

logger = tb_logging.get_logger()


class TensorBoardUploader(object):
    """Uploads a TensorBoard logdir to TensorBoard.gcp."""

    def __init__(
        self,
        experiment_name: str,
        tensorboard_resource_name: str,
        blob_storage_bucket: storage.Bucket,
        blob_storage_folder: str,
        writer_client: TensorboardServiceClient,
        logdir: str,
        allowed_plugins: FrozenSet[str],
        experiment_display_name: Optional[str] = None,
        upload_limits: Optional[server_info_pb2.UploadLimits] = None,
        logdir_poll_rate_limiter: Optional[util.RateLimiter] = None,
        rpc_rate_limiter: Optional[util.RateLimiter] = None,
        tensor_rpc_rate_limiter: Optional[util.RateLimiter] = None,
        blob_rpc_rate_limiter: Optional[util.RateLimiter] = None,
        description: Optional[str] = None,
        verbosity: int = 1,
        one_shot: bool = False,
        event_file_inactive_secs: Optional[int] = None,
        run_name_prefix=None,
    ):
        """Constructs a TensorBoardUploader.

        Args:
          experiment_name: Name of this experiment. Unique to the given
            tensorboard_resource_name.
          tensorboard_resource_name: Name of the Tensorboard resource with this
            format
            projects/{project}/locations/{location}/tensorboards/{tensorboard}
          writer_client: a TensorBoardWriterService stub instance
          logdir: path of the log directory to upload
          experiment_display_name: The display name of the experiment.
          allowed_plugins: collection of string plugin names; events will only be
            uploaded if their time series's metadata specifies one of these plugin
            names
          upload_limits: instance of tensorboard.service.UploadLimits proto.
          logdir_poll_rate_limiter: a `RateLimiter` to use to limit logdir polling
            frequency, to avoid thrashing disks, especially on networked file
            systems
          rpc_rate_limiter: a `RateLimiter` to use to limit write RPC frequency.
            Note this limit applies at the level of single RPCs in the Scalar and
            Tensor case, but at the level of an entire blob upload in the Blob
            case-- which may require a few preparatory RPCs and a stream of chunks.
            Note the chunk stream is internally rate-limited by backpressure from
            the server, so it is not a concern that we do not explicitly rate-limit
            within the stream here.
          description: String description to assign to the experiment.
          verbosity: Level of verbosity, an integer. Supported value: 0 - No upload
            statistics is printed. 1 - Print upload statistics while uploading data
            (default).
          one_shot: Once uploading starts, upload only the existing data in the
            logdir and then return immediately, instead of the default behavior of
            continuing to listen for new data in the logdir and upload them when it
            appears.
          event_file_inactive_secs: Age in seconds of last write after which an
            event file is considered inactive. If none then event file is never
            considered inactive.
          run_name_prefix: If present, all runs created by this invocation will have
            their name prefixed by this value.
        """
        self._experiment_name = experiment_name
        self._experiment_display_name = experiment_display_name
        self._tensorboard_resource_name = tensorboard_resource_name
        self._blob_storage_bucket = blob_storage_bucket
        self._blob_storage_folder = blob_storage_folder
        self._api = writer_client
        self._logdir = logdir
        self._allowed_plugins = frozenset(allowed_plugins)
        self._run_name_prefix = run_name_prefix

        self._upload_limits = upload_limits
        if not self._upload_limits:
            self._upload_limits = server_info_pb2.UploadLimits()
            self._upload_limits.max_scalar_request_size = (
                _DEFAULT_MAX_SCALAR_REQUEST_SIZE
            )
            self._upload_limits.min_scalar_request_interval = (
                _DEFAULT_MIN_SCALAR_REQUEST_INTERVAL
            )
            self._upload_limits.min_tensor_request_interval = (
                _DEFAULT_MIN_TENSOR_REQUEST_INTERVAL
            )
            self._upload_limits.max_tensor_request_size = (
                _DEFAULT_MAX_TENSOR_REQUEST_SIZE
            )
            self._upload_limits.max_tensor_point_size = _DEFAULT_MAX_TENSOR_POINT_SIZE
            self._upload_limits.min_blob_request_interval = (
                _DEFAULT_MIN_BLOB_REQUEST_INTERVAL
            )
            self._upload_limits.max_blob_request_size = _DEFAULT_MAX_BLOB_REQUEST_SIZE
            self._upload_limits.max_blob_size = _DEFAULT_MAX_BLOB_SIZE

        self._description = description
        self._verbosity = verbosity
        self._one_shot = one_shot
        self._request_sender = None
        if logdir_poll_rate_limiter is None:
            self._logdir_poll_rate_limiter = util.RateLimiter(
                _MIN_LOGDIR_POLL_INTERVAL_SECS
            )
        else:
            self._logdir_poll_rate_limiter = logdir_poll_rate_limiter

        if rpc_rate_limiter is None:
            self._rpc_rate_limiter = util.RateLimiter(
                self._upload_limits.min_scalar_request_interval / 1000
            )
        else:
            self._rpc_rate_limiter = rpc_rate_limiter

        if tensor_rpc_rate_limiter is None:
            self._tensor_rpc_rate_limiter = util.RateLimiter(
                self._upload_limits.min_tensor_request_interval / 1000
            )
        else:
            self._tensor_rpc_rate_limiter = tensor_rpc_rate_limiter

        if blob_rpc_rate_limiter is None:
            self._blob_rpc_rate_limiter = util.RateLimiter(
                self._upload_limits.min_blob_request_interval / 1000
            )
        else:
            self._blob_rpc_rate_limiter = blob_rpc_rate_limiter

        def active_filter(secs):
            return (
                not bool(event_file_inactive_secs)
                or secs + event_file_inactive_secs >= time.time()
            )

        directory_loader_factory = functools.partial(
            directory_loader.DirectoryLoader,
            loader_factory=event_file_loader.TimestampedEventFileLoader,
            path_filter=io_wrapper.IsTensorFlowEventsFile,
            active_filter=active_filter,
        )
        self._logdir_loader = logdir_loader.LogdirLoader(
            self._logdir, directory_loader_factory
        )
        self._tracker = upload_tracker.UploadTracker(verbosity=self._verbosity)

    def _create_or_get_experiment(self) -> tensorboard_experiment.TensorboardExperiment:
        """Create an experiment or get an experiment.

        Attempts to create an experiment. If the experiment already exists and
        creation fails then the experiment will be retrieved.

        Returns:
          The created or retrieved experiment.
        """
        logger.info("Creating experiment")

        tb_experiment = tensorboard_experiment.TensorboardExperiment(
            description=self._description, display_name=self._experiment_display_name
        )

        try:
            experiment = self._api.create_tensorboard_experiment(
                parent=self._tensorboard_resource_name,
                tensorboard_experiment=tb_experiment,
                tensorboard_experiment_id=self._experiment_name,
            )
        except exceptions.AlreadyExists:
            logger.info("Creating experiment failed. Retrieving experiment.")
            experiment_name = os.path.join(
                self._tensorboard_resource_name, "experiments", self._experiment_name
            )
            experiment = self._api.get_tensorboard_experiment(name=experiment_name)
        return experiment

    def create_experiment(self):
        """Creates an Experiment for this upload session and returns the ID."""

        experiment = self._create_or_get_experiment()
        self._experiment = experiment
        self._request_sender = _BatchedRequestSender(
            self._experiment.name,
            self._api,
            allowed_plugins=self._allowed_plugins,
            upload_limits=self._upload_limits,
            rpc_rate_limiter=self._rpc_rate_limiter,
            tensor_rpc_rate_limiter=self._tensor_rpc_rate_limiter,
            blob_rpc_rate_limiter=self._blob_rpc_rate_limiter,
            blob_storage_bucket=self._blob_storage_bucket,
            blob_storage_folder=self._blob_storage_folder,
            tracker=self._tracker,
        )

    def get_experiment_resource_name(self):
        return self._experiment.name

    def start_uploading(self):
        """Blocks forever to continuously upload data from the logdir.

        Raises:
          RuntimeError: If `create_experiment` has not yet been called.
          ExperimentNotFoundError: If the experiment is deleted during the
            course of the upload.
        """
        if self._request_sender is None:
            raise RuntimeError("Must call create_experiment() before start_uploading()")
        while True:
            self._logdir_poll_rate_limiter.tick()
            self._upload_once()
            if self._one_shot:
                break
        if self._one_shot and not self._tracker.has_data():
            logger.warning(
                "One-shot mode was used on a logdir (%s) "
                "without any uploadable data" % self._logdir
            )

    def _upload_once(self):
        """Runs one upload cycle, sending zero or more RPCs."""
        logger.info("Starting an upload cycle")

        sync_start_time = time.time()
        self._logdir_loader.synchronize_runs()
        sync_duration_secs = time.time() - sync_start_time
        logger.info("Logdir sync took %.3f seconds", sync_duration_secs)

        run_to_events = self._logdir_loader.get_run_events()
        if self._run_name_prefix:
            run_to_events = {
                self._run_name_prefix + k: v for k, v in run_to_events.items()
            }
        with self._tracker.send_tracker():
            self._request_sender.send_requests(run_to_events)


class ExperimentNotFoundError(RuntimeError):
    pass


class PermissionDeniedError(RuntimeError):
    pass


class ExistingResourceNotFoundError(RuntimeError):
    """Resource could not be created or retrieved."""


class _OutOfSpaceError(Exception):
    """Action could not proceed without overflowing request budget.

    This is a signaling exception (like `StopIteration`) used internally
    by `_*RequestSender`; it does not mean that anything has gone wrong.
    """

    pass


class _BatchedRequestSender(object):
    """Helper class for building requests that fit under a size limit.

    This class maintains stateful request builders for each of the possible
    request types (scalars, tensors, and blobs).  These accumulate batches
    independently, each maintaining its own byte budget and emitting a request
    when the batch becomes full.  As a consequence, events of different types
    will likely be sent to the backend out of order.  E.g., in the extreme case,
    a single tensor-flavored request may be sent only when the event stream is
    exhausted, even though many more recent scalar events were sent earlier.

    This class is not threadsafe. Use external synchronization if
    calling its methods concurrently.
    """

    def __init__(
        self,
        experiment_resource_name: str,
        api: TensorboardServiceClient,
        allowed_plugins: Iterable[str],
        upload_limits: server_info_pb2.UploadLimits,
        rpc_rate_limiter: util.RateLimiter,
        tensor_rpc_rate_limiter: util.RateLimiter,
        blob_rpc_rate_limiter: util.RateLimiter,
        blob_storage_bucket: storage.Bucket,
        blob_storage_folder: str,
        tracker: upload_tracker.UploadTracker,
    ):
        """Constructs _BatchedRequestSender for the given experiment resource.

        Args:
          experiment_resource_name: Name of the experiment resource of the form
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}
          api: Tensorboard service stub used to interact with experiment resource.
          allowed_plugins: The plugins supported by the Tensorboard.gcp resource.
          upload_limits: Upload limits for for api calls.
          rpc_rate_limiter: a `RateLimiter` to use to limit write RPC frequency.
            Note this limit applies at the level of single RPCs in the Scalar and
            Tensor case, but at the level of an entire blob upload in the Blob
            case-- which may require a few preparatory RPCs and a stream of chunks.
            Note the chunk stream is internally rate-limited by backpressure from
            the server, so it is not a concern that we do not explicitly rate-limit
            within the stream here.
          tracker: Upload tracker to track information about uploads.
        """
        self._experiment_resource_name = experiment_resource_name
        self._api = api
        self._tag_metadata = {}
        self._allowed_plugins = frozenset(allowed_plugins)
        self._tracker = tracker
        self._run_to_request_sender: Dict[str, _ScalarBatchedRequestSender] = {}
        self._run_to_tensor_request_sender: Dict[str, _TensorBatchedRequestSender] = {}
        self._run_to_blob_request_sender: Dict[str, _BlobRequestSender] = {}
        self._run_to_run_resource: Dict[str, tensorboard_run.TensorboardRun] = {}
        self._scalar_request_sender_factory = functools.partial(
            _ScalarBatchedRequestSender,
            api=api,
            rpc_rate_limiter=rpc_rate_limiter,
            max_request_size=upload_limits.max_scalar_request_size,
            tracker=self._tracker,
        )
        self._tensor_request_sender_factory = functools.partial(
            _TensorBatchedRequestSender,
            api=api,
            rpc_rate_limiter=tensor_rpc_rate_limiter,
            max_request_size=upload_limits.max_tensor_request_size,
            max_tensor_point_size=upload_limits.max_tensor_point_size,
            tracker=self._tracker,
        )
        self._blob_request_sender_factory = functools.partial(
            _BlobRequestSender,
            api=api,
            rpc_rate_limiter=blob_rpc_rate_limiter,
            max_blob_request_size=upload_limits.max_blob_request_size,
            max_blob_size=upload_limits.max_blob_size,
            blob_storage_bucket=blob_storage_bucket,
            blob_storage_folder=blob_storage_folder,
            tracker=self._tracker,
        )

    def send_requests(
        self, run_to_events: Dict[str, Generator[tf.compat.v1.Event, None, None]]
    ):
        """Accepts a stream of TF events and sends batched write RPCs.

        Each sent request will be batched, the size of each batch depending on
        the type of data (Scalar vs Tensor vs Blob) being sent.

        Args:
          run_to_events: Mapping from run name to generator of `tf.compat.v1.Event`
            values, as returned by `LogdirLoader.get_run_events`.

        Raises:
          RuntimeError: If no progress can be made because even a single
          point is too large (say, due to a gigabyte-long tag name).
        """

        for (run_name, event, value) in self._run_values(run_to_events):
            time_series_key = (run_name, value.tag)

            # The metadata for a time series is memorized on the first event.
            # If later events arrive with a mismatching plugin_name, they are
            # ignored with a warning.
            metadata = self._tag_metadata.get(time_series_key)
            first_in_time_series = False
            if metadata is None:
                first_in_time_series = True
                metadata = value.metadata
                self._tag_metadata[time_series_key] = metadata

            plugin_name = metadata.plugin_data.plugin_name
            if value.HasField("metadata") and (
                plugin_name != value.metadata.plugin_data.plugin_name
            ):
                logger.warning(
                    "Mismatching plugin names for %s.  Expected %s, found %s.",
                    time_series_key,
                    metadata.plugin_data.plugin_name,
                    value.metadata.plugin_data.plugin_name,
                )
                continue
            if plugin_name not in self._allowed_plugins:
                if first_in_time_series:
                    logger.info(
                        "Skipping time series %r with unsupported plugin name %r",
                        time_series_key,
                        plugin_name,
                    )
                continue
            self._tracker.add_plugin_name(plugin_name)
            # If this is the first time we've seen this run create a new run resource
            # and an associated request sender.
            if run_name not in self._run_to_run_resource:
                self._create_or_get_run_resource(run_name)
                self._run_to_request_sender[
                    run_name
                ] = self._scalar_request_sender_factory(
                    self._run_to_run_resource[run_name].name
                )
                self._run_to_tensor_request_sender[
                    run_name
                ] = self._tensor_request_sender_factory(
                    self._run_to_run_resource[run_name].name
                )
                self._run_to_blob_request_sender[
                    run_name
                ] = self._blob_request_sender_factory(
                    self._run_to_run_resource[run_name].name
                )

            if metadata.data_class == summary_pb2.DATA_CLASS_SCALAR:
                self._run_to_request_sender[run_name].add_event(event, value, metadata)
            elif metadata.data_class == summary_pb2.DATA_CLASS_TENSOR:
                self._run_to_tensor_request_sender[run_name].add_event(
                    event, value, metadata
                )
            elif metadata.data_class == summary_pb2.DATA_CLASS_BLOB_SEQUENCE:
                self._run_to_blob_request_sender[run_name].add_event(
                    event, value, metadata
                )

        for scalar_request_sender in self._run_to_request_sender.values():
            scalar_request_sender.flush()

        for tensor_request_sender in self._run_to_tensor_request_sender.values():
            tensor_request_sender.flush()

        for blob_request_sender in self._run_to_blob_request_sender.values():
            blob_request_sender.flush()

    def _create_or_get_run_resource(self, run_name: str):
        """Creates a new Run Resource in current Tensorboard Experiment resource.

        Args:
          run_name: The display name of this run.
        """
        tb_run = tensorboard_run.TensorboardRun()
        tb_run.display_name = run_name
        try:
            tb_run = self._api.create_tensorboard_run(
                parent=self._experiment_resource_name,
                tensorboard_run=tb_run,
                tensorboard_run_id=str(uuid.uuid4()),
            )
        except exceptions.InvalidArgument as e:
            # If the run name already exists then retrieve it
            if "already exist" in e.message:
                runs_pages = self._api.list_tensorboard_runs(
                    parent=self._experiment_resource_name
                )
                for tb_run in runs_pages:
                    if tb_run.display_name == run_name:
                        break

                if tb_run.display_name != run_name:
                    raise ExistingResourceNotFoundError(
                        "Run with name %s already exists but is not resource list."
                        % run_name
                    )
            else:
                raise

        self._run_to_run_resource[run_name] = tb_run

    def _run_values(
        self, run_to_events: Dict[str, Generator[tf.compat.v1.Event, None, None]]
    ) -> Generator[
        Tuple[str, tf.compat.v1.Event, tf.compat.v1.Summary.Value], None, None
    ]:
        """Helper generator to create a single stream of work items.

        Note that `dataclass_compat` may emit multiple variants of
        the same event, for backwards compatibility.  Thus this stream should
        be filtered to obtain the desired version of each event.  Here, we
        ignore any event that does not have a `summary` field.

        Furthermore, the events emitted here could contain values that do not
        have `metadata.data_class` set; these too should be ignored.  In
        `_send_summary_value(...)` above, we switch on `metadata.data_class`
        and drop any values with an unknown (i.e., absent or unrecognized)
        `data_class`.

        Args:
          run_to_events: Mapping from run name to generator of `tf.compat.v1.Event`
            values, as returned by `LogdirLoader.get_run_events`.

        Yields:
          Tuple of run name, tf.compat.v1.Event, tf.compat.v1.Summary.Value per
          value.
        """
        # Note that this join in principle has deletion anomalies: if the input
        # stream contains runs with no events, or events with no values, we'll
        # lose that information. This is not a problem: we would need to prune
        # such data from the request anyway.
        for (run_name, events) in run_to_events.items():
            for event in events:
                _filter_graph_defs(event)
                for value in event.summary.value:
                    yield (run_name, event, value)


class _TimeSeriesResourceManager(object):
    """Helper class managing Time Series resources."""

    def __init__(self, run_resource_id: str, api: TensorboardServiceClient):
        """Constructor for _TimeSeriesResourceManager.

        Args:
          run_resource_id: The resource id for the run with the following format
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}
          api: TensorboardServiceStub
        """
        self._run_resource_id = run_resource_id
        self._api = api
        self._tag_to_time_series_proto: Dict[
            str, tensorboard_time_series.TensorboardTimeSeries
        ] = {}

    def get_or_create(
        self,
        tag_name: str,
        time_series_resource_creator: Callable[
            [], tensorboard_time_series.TensorboardTimeSeries
        ],
    ) -> tensorboard_time_series.TensorboardTimeSeries:
        """get a time series resource with given tag_name, and create a new one on

        OnePlatform if not present.

        Args:
          tag_name: The tag name of the time series in the Tensorboard log dir.
          time_series_resource_creator: A callable that produces a TimeSeries for
            creation.
        """
        if tag_name in self._tag_to_time_series_proto:
            return self._tag_to_time_series_proto[tag_name]

        time_series = time_series_resource_creator()
        time_series.display_name = tag_name
        try:
            time_series = self._api.create_tensorboard_time_series(
                parent=self._run_resource_id, tensorboard_time_series=time_series
            )
        except exceptions.InvalidArgument as e:
            # If the time series display name already exists then retrieve it
            if "already exist" in e.message:
                list_of_time_series = self._api.list_tensorboard_time_series(
                    request=tensorboard_service.ListTensorboardTimeSeriesRequest(
                        parent=self._run_resource_id,
                        filter="display_name = {}".format(json.dumps(str(tag_name))),
                    )
                )
                num = 0
                for ts in list_of_time_series:
                    time_series = ts
                    num += 1
                    break
                if num != 1:
                    raise ValueError(
                        "More than one time series resource found with display_name: {}".format(
                            tag_name
                        )
                    )
            else:
                raise

        self._tag_to_time_series_proto[tag_name] = time_series
        return time_series


class _ScalarBatchedRequestSender(object):
    """Helper class for building requests that fit under a size limit.

    This class accumulates a current request.  `add_event(...)` may or may not
    send the request (and start a new one).  After all `add_event(...)` calls
    are complete, a final call to `flush()` is needed to send the final request.

    This class is not threadsafe. Use external synchronization if calling its
    methods concurrently.
    """

    def __init__(
        self,
        run_resource_id: str,
        api: TensorboardServiceClient,
        rpc_rate_limiter: util.RateLimiter,
        max_request_size: int,
        tracker: upload_tracker.UploadTracker,
    ):
        """Constructer for _ScalarBatchedRequestSender.

        Args:
          run_resource_id: The resource id for the run with the following format
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}
          api: TensorboardServiceStub
          rpc_rate_limiter: until.RateLimiter to limit rate of this request sender
          max_request_size: max number of bytes to send
          tracker:
        """
        self._run_resource_id = run_resource_id
        self._api = api
        self._rpc_rate_limiter = rpc_rate_limiter
        self._byte_budget_manager = _ByteBudgetManager(max_request_size)
        self._tracker = tracker

        # cache: map from Tensorboard tag to TimeSeriesData
        # cleared whenever a new request is created
        self._tag_to_time_series_data: Dict[str, tensorboard_data.TimeSeriesData] = {}

        self._time_series_resource_manager = _TimeSeriesResourceManager(
            self._run_resource_id, self._api
        )
        self._new_request()

    def _new_request(self):
        """Allocates a new request and refreshes the budget."""
        self._request = tensorboard_service.WriteTensorboardRunDataRequest()
        self._tag_to_time_series_data.clear()
        self._num_values = 0
        self._request.tensorboard_run = self._run_resource_id
        self._byte_budget_manager.reset(self._request)

    def add_event(
        self,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
        metadata: tf.compat.v1.SummaryMetadata,
    ):
        """Attempts to add the given event to the current request.

        If the event cannot be added to the current request because the byte
        budget is exhausted, the request is flushed, and the event is added
        to the next request.

        Args:
          event: The tf.compat.v1.Event event containing the value.
          value: A scalar tf.compat.v1.Summary.Value.
          metadata: SummaryMetadata of the event.
        """
        try:
            self._add_event_internal(event, value, metadata)
        except _OutOfSpaceError:
            self.flush()
            # Try again.  This attempt should never produce OutOfSpaceError
            # because we just flushed.
            try:
                self._add_event_internal(event, value, metadata)
            except _OutOfSpaceError:
                raise RuntimeError("add_event failed despite flush")

    def _add_event_internal(
        self,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
        metadata: tf.compat.v1.SummaryMetadata,
    ):
        self._num_values += 1
        time_series_data_proto = self._tag_to_time_series_data.get(value.tag)
        if time_series_data_proto is None:
            time_series_data_proto = self._create_time_series_data(value.tag, metadata)
        self._create_point(time_series_data_proto, event, value)

    def flush(self):
        """Sends the active request after removing empty runs and tags.

        Starts a new, empty active request.
        """
        request = self._request
        request.time_series_data = list(self._tag_to_time_series_data.values())
        _prune_empty_time_series(request)
        if not request.time_series_data:
            return

        self._rpc_rate_limiter.tick()

        with _request_logger(request):
            with self._tracker.scalars_tracker(self._num_values):
                try:
                    self._api.write_tensorboard_run_data(
                        tensorboard_run=self._run_resource_id,
                        time_series_data=request.time_series_data,
                    )
                except grpc.RpcError as e:
                    if (
                        hasattr(e, "code")
                        and getattr(e, "code")() == grpc.StatusCode.NOT_FOUND
                    ):
                        raise ExperimentNotFoundError()
                    logger.error("Upload call failed with error %s", e)

        self._new_request()

    def _create_time_series_data(
        self, tag_name: str, metadata: tf.compat.v1.SummaryMetadata
    ) -> tensorboard_data.TimeSeriesData:
        """Adds a time_series for the tag_name, if there's space.

        Args:
          tag_name: String name of the tag to add (as `value.tag`).

        Returns:
          The TimeSeriesData in _request proto with the given tag name.

        Raises:
          _OutOfSpaceError: If adding the tag would exceed the remaining
            request budget.
        """
        time_series_data_proto = tensorboard_data.TimeSeriesData(
            tensorboard_time_series_id=self._time_series_resource_manager.get_or_create(
                tag_name,
                lambda: tensorboard_time_series.TensorboardTimeSeries(
                    display_name=tag_name,
                    value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
                    plugin_name=metadata.plugin_data.plugin_name,
                    plugin_data=metadata.plugin_data.content,
                ),
            ).name.split("/")[-1],
            value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
        )

        self._request.time_series_data.extend([time_series_data_proto])
        self._byte_budget_manager.add_time_series(time_series_data_proto)
        self._tag_to_time_series_data[tag_name] = time_series_data_proto
        return time_series_data_proto

    def _create_point(
        self,
        time_series_proto: tensorboard_data.TimeSeriesData,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
    ):
        """Adds a scalar point to the given tag, if there's space.

        Args:
          time_series_proto: TimeSeriesData proto to which to add a point.
          event: Enclosing `Event` proto with the step and wall time data.
          value: Scalar `Summary.Value` proto with the actual scalar data.

        Raises:
          _OutOfSpaceError: If adding the point would exceed the remaining
            request budget.
        """
        scalar_proto = tensorboard_data.Scalar(
            value=tensor_util.make_ndarray(value.tensor).item()
        )
        point = tensorboard_data.TimeSeriesDataPoint(
            step=event.step,
            scalar=scalar_proto,
            wall_time=timestamp.Timestamp(
                seconds=int(event.wall_time),
                nanos=int(round((event.wall_time % 1) * 10 ** 9)),
            ),
        )
        time_series_proto.values.extend([point])
        try:
            self._byte_budget_manager.add_point(point)
        except _OutOfSpaceError:
            time_series_proto.values.pop()
            raise


class _TensorBatchedRequestSender(object):
    """Helper class for building WriteTensor() requests that fit under a size limit.

    This class accumulates a current request.  `add_event(...)` may or may not
    send the request (and start a new one).  After all `add_event(...)` calls
    are complete, a final call to `flush()` is needed to send the final request.
    This class is not threadsafe. Use external synchronization if calling its
    methods concurrently.
    """

    def __init__(
        self,
        run_resource_id: str,
        api: TensorboardServiceClient,
        rpc_rate_limiter: util.RateLimiter,
        max_request_size: int,
        max_tensor_point_size: int,
        tracker: upload_tracker.UploadTracker,
    ):
        """Constructer for _TensorBatchedRequestSender.

        Args:
          run_resource_id: The resource id for the run with the following format
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}
          api: TensorboardServiceStub
          rpc_rate_limiter: until.RateLimiter to limit rate of this request sender
          max_request_size: max number of bytes to send
          tracker:
        """
        self._run_resource_id = run_resource_id
        self._api = api
        self._rpc_rate_limiter = rpc_rate_limiter
        self._byte_budget_manager = _ByteBudgetManager(max_request_size)
        self._max_tensor_point_size = max_tensor_point_size
        self._tracker = tracker

        # cache: map from Tensorboard tag to TimeSeriesData
        # cleared whenever a new request is created
        self._tag_to_time_series_data: Dict[str, tensorboard_data.TimeSeriesData] = {}

        self._time_series_resource_manager = _TimeSeriesResourceManager(
            run_resource_id, api
        )
        self._new_request()

    def _new_request(self):
        """Allocates a new request and refreshes the budget."""
        self._request = tensorboard_service.WriteTensorboardRunDataRequest()
        self._tag_to_time_series_data.clear()
        self._num_values = 0
        self._request.tensorboard_run = self._run_resource_id
        self._byte_budget_manager.reset(self._request)
        self._num_values = 0
        self._num_values_skipped = 0
        self._tensor_bytes = 0
        self._tensor_bytes_skipped = 0

    def add_event(
        self,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
        metadata: tf.compat.v1.SummaryMetadata,
    ):
        """Attempts to add the given event to the current request.

          If the event cannot be added to the current request because the byte
          budget is exhausted, the request is flushed, and the event is added
          to the next request.
        """
        try:
            self._add_event_internal(event, value, metadata)
        except _OutOfSpaceError:
            self.flush()
            # Try again.  This attempt should never produce OutOfSpaceError
            # because we just flushed.
            try:
                self._add_event_internal(event, value, metadata)
            except _OutOfSpaceError:
                raise RuntimeError("add_event failed despite flush")

    def _add_event_internal(
        self,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
        metadata: tf.compat.v1.SummaryMetadata,
    ):
        self._num_values += 1
        time_series_data_proto = self._tag_to_time_series_data.get(value.tag)
        if time_series_data_proto is None:
            time_series_data_proto = self._create_time_series_data(value.tag, metadata)
        self._create_point(time_series_data_proto, event, value)

    def flush(self):
        """Sends the active request after removing empty runs and tags.

        Starts a new, empty active request.
        """
        request = self._request
        request.time_series_data = list(self._tag_to_time_series_data.values())
        _prune_empty_time_series(request)
        if not request.time_series_data:
            return

        self._rpc_rate_limiter.tick()

        with _request_logger(request):
            with self._tracker.tensors_tracker(
                self._num_values,
                self._num_values_skipped,
                self._tensor_bytes,
                self._tensor_bytes_skipped,
            ):
                try:
                    self._api.write_tensorboard_run_data(
                        tensorboard_run=self._run_resource_id,
                        time_series_data=request.time_series_data,
                    )
                except grpc.RpcError as e:
                    if e.code() == grpc.StatusCode.NOT_FOUND:
                        raise ExperimentNotFoundError()
                    logger.error("Upload call failed with error %s", e)

        self._new_request()

    def _create_time_series_data(
        self, tag_name: str, metadata: tf.compat.v1.SummaryMetadata
    ) -> tensorboard_data.TimeSeriesData:
        """Adds a time_series for the tag_name, if there's space.

        Args:
          tag_name: String name of the tag to add (as `value.tag`).
          metadata: SummaryMetadata of the event.

        Returns:
          The TimeSeriesData in _request proto with the given tag name.

        Raises:
          _OutOfSpaceError: If adding the tag would exceed the remaining
            request budget.
        """
        time_series_data_proto = tensorboard_data.TimeSeriesData(
            tensorboard_time_series_id=self._time_series_resource_manager.get_or_create(
                tag_name,
                lambda: tensorboard_time_series.TensorboardTimeSeries(
                    display_name=tag_name,
                    value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.TENSOR,
                    plugin_name=metadata.plugin_data.plugin_name,
                    plugin_data=metadata.plugin_data.content,
                ),
            ).name.split("/")[-1],
            value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.TENSOR,
        )

        self._request.time_series_data.extend([time_series_data_proto])
        self._byte_budget_manager.add_time_series(time_series_data_proto)
        self._tag_to_time_series_data[tag_name] = time_series_data_proto
        return time_series_data_proto

    def _create_point(
        self,
        time_series_proto: tensorboard_data.TimeSeriesData,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
    ):
        """Adds a tensor point to the given tag, if there's space.

        Args:
          tag_proto: `WriteTensorRequest.Tag` proto to which to add a point.
          event: Enclosing `Event` proto with the step and wall time data.
          value: Tensor `Summary.Value` proto with the actual tensor data.

        Raises:
          _OutOfSpaceError: If adding the point would exceed the remaining
            request budget.
        """
        point = tensorboard_data.TimeSeriesDataPoint(
            step=event.step,
            tensor=tensorboard_data.TensorboardTensor(
                value=value.tensor.SerializeToString()
            ),
            wall_time=timestamp.Timestamp(
                seconds=int(event.wall_time),
                nanos=int(round((event.wall_time % 1) * 10 ** 9)),
            ),
        )

        self._num_values += 1
        tensor_size = len(point.tensor.value)
        self._tensor_bytes += tensor_size
        if tensor_size > self._max_tensor_point_size:
            logger.warning(
                "Tensor too large; skipping. " "Size %d exceeds limit of %d bytes.",
                tensor_size,
                self._max_tensor_point_size,
            )
            self._num_values_skipped += 1
            self._tensor_bytes_skipped += tensor_size
            return

        self._validate_tensor_value(
            value.tensor, value.tag, event.step, event.wall_time
        )

        time_series_proto.values.extend([point])

        try:
            self._byte_budget_manager.add_point(point)
        except _OutOfSpaceError:
            time_series_proto.values.pop()
            raise

    def _validate_tensor_value(self, tensor_proto, tag, step, wall_time):
        """Validate a TensorProto by attempting to parse it."""
        try:
            tensor_util.make_ndarray(tensor_proto)
        except ValueError as error:
            raise ValueError(
                "The uploader failed to upload a tensor. This seems to be "
                "due to a malformation in the tensor, which may be caused by "
                "a bug in the process that wrote the tensor.\n\n"
                "The tensor has tag '%s' and is at step %d and wall_time %.6f.\n\n"
                "Original error:\n%s" % (tag, step, wall_time, error)
            )


class _ByteBudgetManager(object):
    """Helper class for managing the request byte budget for certain RPCs.

    This should be used for RPCs that organize data by Runs, Tags, and Points,
    specifically WriteScalar and WriteTensor.

    Any call to add_time_series() or add_point() may raise an
    _OutOfSpaceError, which is non-fatal. It signals to the caller that they
    should flush the current request and begin a new one.

    For more information on the protocol buffer encoding and how byte cost
    can be calculated, visit:

    https://developers.google.com/protocol-buffers/docs/encoding
    """

    def __init__(self, max_bytes: int):
        # The remaining number of bytes that we may yet add to the request.
        self._byte_budget = None  # type: int
        self._max_bytes = max_bytes

    def reset(self, base_request: tensorboard_service.WriteTensorboardRunDataRequest):
        """Resets the byte budget and calculates the cost of the base request.

        Args:
          base_request: Base request.

        Raises:
          _OutOfSpaceError: If the size of the request exceeds the entire
            request byte budget.
        """
        self._byte_budget = self._max_bytes
        self._byte_budget -= (
            base_request._pb.ByteSize()
        )  # pylint: disable=protected-access
        if self._byte_budget < 0:
            raise _OutOfSpaceError("Byte budget too small for base request")

    def add_time_series(self, time_series_proto: tensorboard_data.TimeSeriesData):
        """Integrates the cost of a tag proto into the byte budget.

        Args:
          time_series_proto: The proto representing a time series.

        Raises:
          _OutOfSpaceError: If adding the time_series would exceed the remaining
          request budget.
        """
        cost = (
            # The size of the tag proto without any tag fields set.
            time_series_proto._pb.ByteSize()  # pylint: disable=protected-access
            # The size of the varint that describes the length of the tag
            # proto. We can't yet know the final size of the tag proto -- we
            # haven't yet set any point values -- so we can't know the final
            # size of this length varint. We conservatively assume it is maximum
            # size.
            + _MAX_VARINT64_LENGTH_BYTES
            # The size of the proto key.
            + 1
        )
        if cost > self._byte_budget:
            raise _OutOfSpaceError()
        self._byte_budget -= cost

    def add_point(self, point_proto: tensorboard_data.TimeSeriesDataPoint):
        """Integrates the cost of a point proto into the byte budget.

        Args:
          point_proto: The proto representing a point.

        Raises:
          _OutOfSpaceError: If adding the point would exceed the remaining request
           budget.
        """
        submessage_cost = point_proto._pb.ByteSize()  # pylint: disable=protected-access
        cost = (
            # The size of the point proto.
            submessage_cost
            # The size of the varint that describes the length of the point
            # proto.
            + _varint_cost(submessage_cost)
            # The size of the proto key.
            + 1
        )
        if cost > self._byte_budget:
            raise _OutOfSpaceError()
        self._byte_budget -= cost


class _BlobRequestSender(object):
    """Uploader for blob-type event data.

    Unlike the other types, this class does not accumulate events in batches;
    every blob is sent individually and immediately.  Nonetheless we retain
    the `add_event()`/`flush()` structure for symmetry.

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
        blob_storage_folder: str,
        tracker: upload_tracker.UploadTracker,
    ):
        self._run_resource_id = run_resource_id
        self._api = api
        self._rpc_rate_limiter = rpc_rate_limiter
        self._max_blob_request_size = max_blob_request_size
        self._max_blob_size = max_blob_size
        self._tracker = tracker
        self._time_series_resource_manager = _TimeSeriesResourceManager(
            run_resource_id, api
        )

        self._bucket = blob_storage_bucket
        self._folder = blob_storage_folder

        self._new_request()

    def _new_request(self):
        """Declares the previous event complete."""
        self._event = None
        self._value = None
        self._metadata = None

    def add_event(
        self,
        event: tf.compat.v1.Event,
        value: tf.compat.v1.Summary.Value,
        metadata: tf.compat.v1.SummaryMetadata,
    ):
        """Attempts to add the given event to the current request.

        If the event cannot be added to the current request because the byte
        budget is exhausted, the request is flushed, and the event is added
        to the next request.
        """
        if self._value:
            raise RuntimeError("Tried to send blob while another is pending")
        self._event = event  # provides step and possibly plugin_name
        self._value = value
        self._blobs = tensor_util.make_ndarray(self._value.tensor)
        if self._blobs.ndim == 1:
            self._metadata = metadata
            self.flush()
        else:
            logger.warning(
                "A blob sequence must be represented as a rank-1 Tensor. "
                "Provided data has rank %d, for run %s, tag %s, step %s ('%s' plugin) .",
                self._blobs.ndim,
                self._run_resource_id,
                self._value.tag,
                self._event.step,
                metadata.plugin_data.plugin_name,
            )
            # Skip this upload.
            self._new_request()

    def flush(self):
        """Sends the current blob sequence fully, and clears it to make way for the next."""
        if not self._value:
            self._new_request()
            return

        time_series_proto = self._time_series_resource_manager.get_or_create(
            self._value.tag,
            lambda: tensorboard_time_series.TensorboardTimeSeries(
                display_name=self._value.tag,
                value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.BLOB_SEQUENCE,
                plugin_name=self._metadata.plugin_data.plugin_name,
                plugin_data=self._metadata.plugin_data.content,
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
        for blob in self._blobs:
            self._rpc_rate_limiter.tick()
            with self._tracker.blob_tracker(len(blob)) as blob_tracker:
                blob_id = self._send_blob(blob, blob_path_prefix)
                if blob_id is not None:
                    sent_blob_ids.append(str(blob_id))
                blob_tracker.mark_uploaded(blob_id is not None)

        data_point = tensorboard_data.TimeSeriesDataPoint(
            step=self._event.step,
            blobs=tensorboard_data.TensorboardBlobSequence(
                values=[
                    tensorboard_data.TensorboardBlob(id=blob_id)
                    for blob_id in sent_blob_ids
                ]
            ),
            wall_time=timestamp.Timestamp(
                seconds=int(self._event.wall_time),
                nanos=int(round((self._event.wall_time % 1) * 10 ** 9)),
            ),
        )

        time_series_data_proto = tensorboard_data.TimeSeriesData(
            tensorboard_time_series_id=time_series_proto.name.split("/")[-1],
            value_type=tensorboard_time_series.TensorboardTimeSeries.ValueType.BLOB_SEQUENCE,
            values=[data_point],
        )
        request = tensorboard_service.WriteTensorboardRunDataRequest(
            time_series_data=[time_series_data_proto]
        )

        _prune_empty_time_series(request)
        if not request.time_series_data:
            return

        with _request_logger(request):
            try:
                self._api.write_tensorboard_run_data(
                    tensorboard_run=self._run_resource_id,
                    time_series_data=request.time_series_data,
                )
            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.NOT_FOUND:
                    raise ExperimentNotFoundError()
                logger.error("Upload call failed with error %s", e)

        self._new_request()

    def _send_blob(self, blob, blob_path_prefix):
        """Sends a single blob to a GCS bucket in the consumer project.

        The blob will not be sent if it is too large.

        Returns:
          The ID of blob successfully sent.
        """
        if len(blob) > self._max_blob_size:
            logger.warning(
                "Blob too large; skipping.  Size %d exceeds limit of %d bytes.",
                len(blob),
                self._max_blob_size,
            )
            return None

        blob_id = uuid.uuid4()
        blob_path = (
            "{}/{}".format(blob_path_prefix, blob_id) if blob_path_prefix else blob_id
        )
        self._bucket.blob(blob_path).upload_from_string(blob)
        return blob_id


@contextlib.contextmanager
def _request_logger(request: tensorboard_service.WriteTensorboardRunDataRequest):
    """Context manager to log request size and duration."""
    upload_start_time = time.time()
    request_bytes = request._pb.ByteSize()  # pylint: disable=protected-access
    logger.info("Trying request of %d bytes", request_bytes)
    yield
    upload_duration_secs = time.time() - upload_start_time
    logger.info(
        "Upload of (%d bytes) took %.3f seconds", request_bytes, upload_duration_secs,
    )


def _varint_cost(n: int):
    """Computes the size of `n` encoded as an unsigned base-128 varint.

    This should be consistent with the proto wire format:
    <https://developers.google.com/protocol-buffers/docs/encoding#varints>

    Args:
      n: A non-negative integer.

    Returns:
      An integer number of bytes.
    """
    result = 1
    while n >= 128:
        result += 1
        n >>= 7
    return result


def _prune_empty_time_series(
    request: tensorboard_service.WriteTensorboardRunDataRequest,
):
    """Removes empty time_series from request."""
    for (time_series_idx, time_series_data) in reversed(
        list(enumerate(request.time_series_data))
    ):
        if not time_series_data.values:
            del request.time_series_data[time_series_idx]


def _filter_graph_defs(event: tf.compat.v1.Event):
    """Filters graph definitions.

    Args:
      event: tf.compat.v1.Event to filter.
    """
    for v in event.summary.value:
        if v.metadata.plugin_data.plugin_name != graph_metadata.PLUGIN_NAME:
            continue
        if v.tag == graph_metadata.RUN_GRAPH_NAME:
            data = list(v.tensor.string_val)
            filtered_data = [_filtered_graph_bytes(x) for x in data]
            filtered_data = [x for x in filtered_data if x is not None]
            if filtered_data != data:
                new_tensor = tensor_util.make_tensor_proto(
                    filtered_data, dtype=types_pb2.DT_STRING
                )
                v.tensor.CopyFrom(new_tensor)


def _filtered_graph_bytes(graph_bytes: bytes):
    """Prepares the graph to be served to the front-end.

    For now, it supports filtering out attributes that are too large to be shown
    in the graph UI.

    Args:
      graph_bytes: Graph definition.

    Returns:
      Filtered graph.
    """
    try:
        graph_def = graph_pb2.GraphDef().FromString(graph_bytes)
    # The reason for the RuntimeWarning catch here is b/27494216, whereby
    # some proto parsers incorrectly raise that instead of DecodeError
    # on certain kinds of malformed input. Triggering this seems to require
    # a combination of mysterious circumstances.
    except (message.DecodeError, RuntimeWarning):
        logger.warning(
            "Could not parse GraphDef of size %d. Skipping.", len(graph_bytes),
        )
        return None
    # Use the default filter parameters:
    # limit_attr_size=1024, large_attrs_key="_too_large_attrs"
    process_graph.prepare_graph_for_ui(graph_def)
    return graph_def.SerializeToString()
