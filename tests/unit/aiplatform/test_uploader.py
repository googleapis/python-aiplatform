# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests for uploader.py."""

import datetime
import functools
import logging
import os
import re
import tempfile
import threading
import time
from unittest import mock

from google.api_core import datetime_helpers
from google.cloud import storage
from google.cloud.aiplatform.compat.services import (
    tensorboard_service_client,
)
from google.cloud.aiplatform.compat.types import tensorboard_data
from google.cloud.aiplatform.compat.types import (
    tensorboard_experiment as tensorboard_experiment_type,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_run as tensorboard_run_type,
)
from google.cloud.aiplatform.compat.types import tensorboard_service
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series as tensorboard_time_series_type,
)
from google.cloud.aiplatform.tensorboard import uploader as uploader_lib
from google.cloud.aiplatform.tensorboard import uploader_utils
from google.cloud.aiplatform.tensorboard.plugins.tf_profiler import (
    profile_uploader,
)
from google.cloud.aiplatform_v1.services.tensorboard_service.transports import (
    grpc as transports_grpc,
)
import grpc
import grpc_testing
import tensorflow as tf

from google.protobuf import timestamp_pb2
from google.protobuf import message
from tensorboard.compat.proto import event_pb2
from tensorboard.compat.proto import graph_pb2
from tensorboard.compat.proto import meta_graph_pb2
from tensorboard.compat.proto import summary_pb2
from tensorboard.compat.proto import tensor_pb2
from tensorboard.compat.proto import types_pb2
from tensorboard.plugins.graph import metadata as graphs_metadata
from tensorboard.plugins.scalar import metadata as scalars_metadata
from tensorboard.summary import v1 as summary_v1
from tensorboard.uploader import logdir_loader
from tensorboard.uploader import upload_tracker
from tensorboard.uploader import util
from tensorboard.uploader.proto import server_info_pb2

data_compat = uploader_lib.event_file_loader.data_compat
dataclass_compat = uploader_lib.event_file_loader.dataclass_compat
scalar_v2_pb = summary_v1._scalar_summary.scalar_pb
image_pb = summary_v1._image_summary.pb

_SCALARS_HISTOGRAMS_AND_GRAPHS = frozenset(
    (
        scalars_metadata.PLUGIN_NAME,
        graphs_metadata.PLUGIN_NAME,
    )
)

# Sentinel for `_create_*` helpers, for arguments for which we want to
# supply a default other than the `None` used by the code under test.
_USE_DEFAULT = object()

_TEST_EXPERIMENT_NAME = "test-experiment"
_TEST_TENSORBOARD_RESOURCE_NAME = (
    "projects/test_project/locations/us-central1/tensorboards/test_tensorboard"
)
_TEST_LOG_DIR_NAME = "/logs/foo"
_TEST_RUN_NAME = "test-run"
_TEST_ONE_PLATFORM_EXPERIMENT_NAME = "{}/experiments/{}".format(
    _TEST_TENSORBOARD_RESOURCE_NAME, _TEST_EXPERIMENT_NAME
)
_TEST_ONE_PLATFORM_RUN_NAME = "{}/runs/{}".format(
    _TEST_ONE_PLATFORM_EXPERIMENT_NAME, _TEST_RUN_NAME
)
_TEST_TIME_SERIES_NAME = "test-time-series"
_TEST_ONE_PLATFORM_TIME_SERIES_NAME = "{}/timeSeries/{}".format(
    _TEST_ONE_PLATFORM_RUN_NAME, _TEST_TIME_SERIES_NAME
)
_TEST_BLOB_STORAGE_FOLDER = "test_folder"


def _create_example_graph_bytes(large_attr_size):
    graph_def = graph_pb2.GraphDef()
    graph_def.node.add(name="alice", op="Person")
    graph_def.node.add(name="bob", op="Person")

    graph_def.node[1].attr["small"].s = b"small_attr_value"
    graph_def.node[1].attr["large"].s = b"l" * large_attr_size
    graph_def.node.add(name="friendship", op="Friendship", input=["alice", "bob"])
    return graph_def.SerializeToString()


class AbortUploadError(Exception):
    """Exception used in testing to abort the upload process."""


def _create_mock_client():
    # Create a stub instance (using a test channel) in order to derive a mock
    # from it with autospec enabled. Mocking TensorBoardWriterServiceStub itself
    # doesn't work with autospec because grpc constructs stubs via metaclassing.

    def create_experiment_response(
        tensorboard_experiment_id=None,
        tensorboard_experiment=None,  # pylint: disable=unused-argument
        parent=None,
    ):  # pylint: disable=unused-argument
        tensorboard_experiment_id = (
            "{}/experiments/{}".format(parent, tensorboard_experiment_id)
            if parent
            else tensorboard_experiment_id
        )
        return tensorboard_experiment_type.TensorboardExperiment(
            name=tensorboard_experiment_id
        )

    def create_run_response(
        tensorboard_run=None,  # pylint: disable=unused-argument
        tensorboard_run_id=None,
        parent=None,
    ):  # pylint: disable=unused-argument
        tensorboard_run_id = (
            "{}/runs/{}".format(parent, tensorboard_run_id)
            if parent
            else tensorboard_run_id
        )
        return tensorboard_run_type.TensorboardRun(name=tensorboard_run_id)

    def create_tensorboard_time_series(
        tensorboard_time_series=None, parent=None
    ):  # pylint: disable=unused-argument
        name = (
            "{}/timeSeries/{}".format(parent, tensorboard_time_series.display_name)
            if parent
            else tensorboard_time_series.display_name
        )
        return tensorboard_time_series_type.TensorboardTimeSeries(
            name=name,
            display_name=tensorboard_time_series.display_name,
        )

    test_channel = grpc_testing.channel(
        service_descriptors=[], time=grpc_testing.strict_real_time()
    )
    mock_client = mock.Mock(
        spec=tensorboard_service_client.TensorboardServiceClient(
            transport=transports_grpc.TensorboardServiceGrpcTransport(
                channel=test_channel
            )
        )
    )
    mock_client.create_tensorboard_experiment.side_effect = create_experiment_response
    mock_client.create_tensorboard_run.side_effect = create_run_response
    mock_client.create_tensorboard_time_series.side_effect = (
        create_tensorboard_time_series
    )
    return mock_client


def _create_mock_blob_storage():
    mock_blob_storage = mock.Mock()
    mock_blob_storage.mock_add_spec(storage.Bucket)

    return mock_blob_storage


def _create_uploader(
    writer_client=_USE_DEFAULT,
    logdir=None,
    max_scalar_request_size=_USE_DEFAULT,
    max_tensor_request_size=_USE_DEFAULT,
    max_tensor_point_size=_USE_DEFAULT,
    max_blob_request_size=_USE_DEFAULT,
    max_blob_size=_USE_DEFAULT,
    logdir_poll_rate_limiter=_USE_DEFAULT,
    rpc_rate_limiter=_USE_DEFAULT,
    experiment_name=_TEST_EXPERIMENT_NAME,
    tensorboard_resource_name=_TEST_TENSORBOARD_RESOURCE_NAME,
    blob_storage_bucket=None,
    blob_storage_folder=_TEST_BLOB_STORAGE_FOLDER,
    description=None,
    verbosity=0,  # Use 0 to minimize littering the test output.
    one_shot=None,
    allowed_plugins=_SCALARS_HISTOGRAMS_AND_GRAPHS,
    run_name_prefix=None,
):
    if writer_client is _USE_DEFAULT:
        writer_client = _create_mock_client()
    if max_scalar_request_size is _USE_DEFAULT:
        max_scalar_request_size = 128000
    if max_tensor_request_size is _USE_DEFAULT:
        max_tensor_request_size = 512000
    if max_blob_request_size is _USE_DEFAULT:
        max_blob_request_size = 128000
    if max_blob_size is _USE_DEFAULT:
        max_blob_size = 12345
    if max_tensor_point_size is _USE_DEFAULT:
        max_tensor_point_size = 16000
    if logdir_poll_rate_limiter is _USE_DEFAULT:
        logdir_poll_rate_limiter = util.RateLimiter(0)
    if rpc_rate_limiter is _USE_DEFAULT:
        rpc_rate_limiter = util.RateLimiter(0)

    upload_limits = server_info_pb2.UploadLimits(
        max_scalar_request_size=max_scalar_request_size,
        max_tensor_request_size=max_tensor_request_size,
        max_tensor_point_size=max_tensor_point_size,
        max_blob_request_size=max_blob_request_size,
        max_blob_size=max_blob_size,
    )

    return uploader_lib.TensorBoardUploader(
        experiment_name=experiment_name,
        tensorboard_resource_name=tensorboard_resource_name,
        writer_client=writer_client,
        logdir=logdir,
        allowed_plugins=allowed_plugins,
        upload_limits=upload_limits,
        blob_storage_bucket=blob_storage_bucket,
        blob_storage_folder=blob_storage_folder,
        logdir_poll_rate_limiter=logdir_poll_rate_limiter,
        rpc_rate_limiter=rpc_rate_limiter,
        description=description,
        verbosity=verbosity,
        one_shot=one_shot,
        run_name_prefix=run_name_prefix,
    )


def _create_dispatcher(
    experiment_resource_name,
    api=None,
    allowed_plugins=_USE_DEFAULT,
    logdir=None,
):
    if api is _USE_DEFAULT:
        api = _create_mock_client()
    if allowed_plugins is _USE_DEFAULT:
        allowed_plugins = _SCALARS_HISTOGRAMS_AND_GRAPHS

    upload_limits = server_info_pb2.UploadLimits(
        max_scalar_request_size=128000,
        max_tensor_request_size=128000,
        max_tensor_point_size=52000,
        max_blob_request_size=128000,
    )

    rpc_rate_limiter = util.RateLimiter(0)
    tensor_rpc_rate_limiter = util.RateLimiter(0)
    blob_rpc_rate_limiter = util.RateLimiter(0)

    one_platform_resource_manager = uploader_utils.OnePlatformResourceManager(
        experiment_resource_name, api
    )

    request_sender = uploader_lib._BatchedRequestSender(
        experiment_resource_name=experiment_resource_name,
        api=api,
        allowed_plugins=allowed_plugins,
        upload_limits=upload_limits,
        rpc_rate_limiter=rpc_rate_limiter,
        tensor_rpc_rate_limiter=tensor_rpc_rate_limiter,
        blob_rpc_rate_limiter=blob_rpc_rate_limiter,
        blob_storage_bucket=None,
        blob_storage_folder=None,
        one_platform_resource_manager=one_platform_resource_manager,
        tracker=upload_tracker.UploadTracker(verbosity=0),
    )

    additional_senders = {}
    if "profile" in allowed_plugins:
        additional_senders["profile"] = profile_uploader.ProfileRequestSender(
            experiment_resource_name=experiment_resource_name,
            api=api,
            upload_limits=upload_limits,
            blob_rpc_rate_limiter=util.RateLimiter(0),
            blob_storage_bucket=_create_mock_blob_storage(),
            source_bucket=_create_mock_blob_storage(),
            blob_storage_folder=None,
            tracker=upload_tracker.UploadTracker(verbosity=0),
            logdir=logdir,
        )

    return uploader_lib._Dispatcher(
        request_sender=request_sender,
        additional_senders=additional_senders,
    )


def _create_scalar_request_sender(
    experiment_resource_id, api=_USE_DEFAULT, max_request_size=_USE_DEFAULT
):
    if api is _USE_DEFAULT:
        api = _create_mock_client()
    if max_request_size is _USE_DEFAULT:
        max_request_size = 128000
    return uploader_lib._ScalarBatchedRequestSender(
        experiment_resource_id=experiment_resource_id,
        one_platform_resource_manager=uploader_utils.OnePlatformResourceManager(
            experiment_resource_id, api
        ),
        api=api,
        rpc_rate_limiter=util.RateLimiter(0),
        max_request_size=max_request_size,
        tracker=upload_tracker.UploadTracker(verbosity=0),
    )


def _create_file_request_sender(
    run_resource_id,
    api=_USE_DEFAULT,
    max_blob_request_size=_USE_DEFAULT,
    max_blob_size=_USE_DEFAULT,
    blob_storage_folder=None,
    blob_storage_bucket=_USE_DEFAULT,
    source_bucket=_USE_DEFAULT,
):
    if api is _USE_DEFAULT:
        api = _create_mock_client()
    if max_blob_request_size is _USE_DEFAULT:
        max_blob_request_size = 128000
    if blob_storage_bucket is _USE_DEFAULT:
        blob_storage_bucket = _create_mock_blob_storage()
    if source_bucket is _USE_DEFAULT:
        source_bucket = _create_mock_blob_storage()
    if max_blob_size is _USE_DEFAULT:
        max_blob_size = 128000
    return profile_uploader._FileRequestSender(
        run_resource_id=run_resource_id,
        api=api,
        rpc_rate_limiter=util.RateLimiter(0),
        max_blob_request_size=max_blob_request_size,
        max_blob_size=max_blob_size,
        blob_storage_bucket=blob_storage_bucket,
        blob_storage_folder=blob_storage_folder,
        tracker=upload_tracker.UploadTracker(verbosity=0),
        source_bucket=source_bucket,
    )


def _scalar_event(tag, value):
    return event_pb2.Event(summary=scalar_v2_pb(tag, value))


def _grpc_error(code, details):
    # Monkey patch insertion for the methods a real grpc.RpcError would have.
    error = grpc.RpcError("RPC error %r: %s" % (code, details))
    error.code = lambda: code
    error.details = lambda: details
    return error


def _timestamp_pb(nanos):
    result = timestamp_pb2.Timestamp()
    result.FromNanoseconds(nanos)
    return result


class FileWriter(tf.compat.v1.summary.FileWriter):
    """FileWriter for test.

    TensorFlow FileWriter uses TensorFlow's Protobuf Python binding
    which is largely discouraged in TensorBoard. We do not want a
    TB.Writer but require one for testing in integrational style
    (writing out event files and use the real event readers).
    """

    def __init__(self, *args, **kwargs):
        # Briefly enter graph mode context so this testing FileWriter can be
        # created from an eager mode context without triggering a usage error.
        with tf.compat.v1.Graph().as_default():
            super(FileWriter, self).__init__(*args, **kwargs)

    def add_test_summary(self, tag, simple_value=1.0, step=None):
        """Convenience for writing a simple summary for a given tag."""
        value = summary_pb2.Summary.Value(tag=tag, simple_value=simple_value)
        summary = summary_pb2.Summary(value=[value])
        self.add_summary(summary, global_step=step)

    def add_test_tensor_summary(self, tag, tensor, step=None, value_metadata=None):
        """Convenience for writing a simple summary for a given tag."""
        value = summary_pb2.Summary.Value(
            tag=tag, tensor=tensor, metadata=value_metadata
        )
        summary = summary_pb2.Summary(value=[value])
        self.add_summary(summary, global_step=step)

    def add_event(self, event):
        if isinstance(event, event_pb2.Event):
            tf_event = tf.compat.v1.Event.FromString(event.SerializeToString())
        else:
            tf_event = event
            if not isinstance(event, bytes):
                logging.error(
                    "Added TensorFlow event proto. "
                    "Please prefer TensorBoard copy of the proto"
                )
        super(FileWriter, self).add_event(tf_event)

    def add_summary(self, summary, global_step=None):
        if isinstance(summary, summary_pb2.Summary):
            tf_summary = tf.compat.v1.Summary.FromString(summary.SerializeToString())
        else:
            tf_summary = summary
            if not isinstance(summary, bytes):
                logging.error(
                    "Added TensorFlow summary proto. "
                    "Please prefer TensorBoard copy of the proto"
                )
        super(FileWriter, self).add_summary(tf_summary, global_step)

    def add_session_log(self, session_log, global_step=None):
        if isinstance(session_log, event_pb2.SessionLog):
            tf_session_log = tf.compat.v1.SessionLog.FromString(
                session_log.SerializeToString()
            )
        else:
            tf_session_log = session_log
            if not isinstance(session_log, bytes):
                logging.error(
                    "Added TensorFlow session_log proto. "
                    "Please prefer TensorBoard copy of the proto"
                )
        super(FileWriter, self).add_session_log(tf_session_log, global_step)

    def add_graph(self, graph, global_step=None, graph_def=None):
        if isinstance(graph_def, graph_pb2.GraphDef):
            tf_graph_def = tf.compat.v1.GraphDef.FromString(
                graph_def.SerializeToString()
            )
        else:
            tf_graph_def = graph_def

        super(FileWriter, self).add_graph(
            graph, global_step=global_step, graph_def=tf_graph_def
        )

    def add_meta_graph(self, meta_graph_def, global_step=None):
        if isinstance(meta_graph_def, meta_graph_pb2.MetaGraphDef):
            tf_meta_graph_def = tf.compat.v1.MetaGraphDef.FromString(
                meta_graph_def.SerializeToString()
            )
        else:
            tf_meta_graph_def = meta_graph_def

        super(FileWriter, self).add_meta_graph(
            meta_graph_def=tf_meta_graph_def, global_step=global_step
        )


class TensorboardUploaderTest(tf.test.TestCase):
    def test_create_experiment(self):
        logdir = _TEST_LOG_DIR_NAME
        uploader = _create_uploader(_create_mock_client(), logdir)
        uploader.create_experiment()
        self.assertEqual(uploader._experiment.name, _TEST_ONE_PLATFORM_EXPERIMENT_NAME)

    def test_create_experiment_with_name(self):
        logdir = _TEST_LOG_DIR_NAME
        mock_client = _create_mock_client()
        new_name = "This is the new name"
        uploader = _create_uploader(mock_client, logdir, experiment_name=new_name)
        uploader.create_experiment()
        mock_client.create_tensorboard_experiment.assert_called_once()
        call_args = mock_client.create_tensorboard_experiment.call_args
        self.assertEqual(
            call_args[1]["tensorboard_experiment"],
            tensorboard_experiment_type.TensorboardExperiment(),
        )
        self.assertEqual(call_args[1]["parent"], _TEST_TENSORBOARD_RESOURCE_NAME)
        self.assertEqual(call_args[1]["tensorboard_experiment_id"], new_name)

    def test_create_experiment_with_description(self):
        logdir = _TEST_LOG_DIR_NAME
        mock_client = _create_mock_client()
        new_description = """
        **description**"
        may have "strange" unicode chars 🌴 \\/<>
        """
        uploader = _create_uploader(mock_client, logdir, description=new_description)
        uploader.create_experiment()
        self.assertEqual(uploader._experiment_name, _TEST_EXPERIMENT_NAME)
        mock_client.create_tensorboard_experiment.assert_called_once()
        call_args = mock_client.create_tensorboard_experiment.call_args

        tb_experiment = tensorboard_experiment_type.TensorboardExperiment(
            description=new_description
        )

        expected_call_args = mock.call(
            parent=_TEST_TENSORBOARD_RESOURCE_NAME,
            tensorboard_experiment_id=_TEST_EXPERIMENT_NAME,
            tensorboard_experiment=tb_experiment,
        )

        self.assertEqual(expected_call_args, call_args)

    def test_create_experiment_with_all_metadata(self):
        logdir = _TEST_LOG_DIR_NAME
        mock_client = _create_mock_client()
        new_description = """
        **description**"
        may have "strange" unicode chars 🌴 \\/<>
        """
        new_name = "This is a cool name."
        uploader = _create_uploader(
            mock_client, logdir, experiment_name=new_name, description=new_description
        )
        uploader.create_experiment()
        self.assertEqual(uploader._experiment_name, new_name)
        mock_client.create_tensorboard_experiment.assert_called_once()
        call_args = mock_client.create_tensorboard_experiment.call_args

        tb_experiment = tensorboard_experiment_type.TensorboardExperiment(
            description=new_description
        )
        expected_call_args = mock.call(
            parent=_TEST_TENSORBOARD_RESOURCE_NAME,
            tensorboard_experiment_id=new_name,
            tensorboard_experiment=tb_experiment,
        )
        self.assertEqual(call_args, expected_call_args)

    def test_start_uploading_without_create_experiment_fails(self):
        mock_client = _create_mock_client()
        uploader = _create_uploader(mock_client, _TEST_LOG_DIR_NAME)
        with self.assertRaisesRegex(RuntimeError, "call create_experiment()"):
            uploader.start_uploading()

    def test_start_uploading_scalars(self):
        mock_client = _create_mock_client()
        mock_rate_limiter = mock.create_autospec(util.RateLimiter)
        mock_tensor_rate_limiter = mock.create_autospec(util.RateLimiter)
        mock_blob_rate_limiter = mock.create_autospec(util.RateLimiter)
        mock_tracker = mock.MagicMock()
        with mock.patch.object(
            upload_tracker, "UploadTracker", return_value=mock_tracker
        ):
            uploader = _create_uploader(
                writer_client=mock_client,
                logdir=_TEST_LOG_DIR_NAME,
                # Send each Event below in a separate WriteScalarRequest
                max_scalar_request_size=200,
                rpc_rate_limiter=mock_rate_limiter,
                verbosity=1,  # In order to test the upload tracker.
            )
            uploader.create_experiment()

        mock_logdir_loader = mock.create_autospec(logdir_loader.LogdirLoader)
        mock_logdir_loader.get_run_events.side_effect = [
            {
                "run 1": _apply_compat(
                    [_scalar_event("1.1", 5.0), _scalar_event("1.2", 5.0)]
                ),
                "run 2": _apply_compat(
                    [_scalar_event("2.1", 5.0), _scalar_event("2.2", 5.0)]
                ),
            },
            {
                "run 3": _apply_compat(
                    [_scalar_event("3.1", 5.0), _scalar_event("3.2", 5.0)]
                ),
                "run 4": _apply_compat(
                    [_scalar_event("4.1", 5.0), _scalar_event("4.2", 5.0)]
                ),
                "run 5": _apply_compat(
                    [_scalar_event("5.1", 5.0), _scalar_event("5.2", 5.0)]
                ),
            },
            AbortUploadError,
        ]

        with mock.patch.object(
            uploader, "_logdir_loader", mock_logdir_loader
        ), self.assertRaises(AbortUploadError):
            uploader.start_uploading()
        self.assertEqual(5, mock_client.write_tensorboard_experiment_data.call_count)
        self.assertEqual(5, mock_rate_limiter.tick.call_count)
        self.assertEqual(0, mock_tensor_rate_limiter.tick.call_count)
        self.assertEqual(0, mock_blob_rate_limiter.tick.call_count)

        # Check upload tracker calls.
        self.assertEqual(mock_tracker.send_tracker.call_count, 2)
        self.assertEqual(mock_tracker.scalars_tracker.call_count, 5)
        self.assertLen(mock_tracker.scalars_tracker.call_args[0], 1)
        self.assertEqual(mock_tracker.tensors_tracker.call_count, 0)
        self.assertEqual(mock_tracker.blob_tracker.call_count, 0)

    def test_start_uploading_scalars_one_shot(self):
        """Check that one-shot uploading stops without AbortUploadError."""

        def batch_create_runs(parent, requests):
            # pylint: disable=unused-argument
            tb_runs = []
            for request in requests:
                tb_run = tensorboard_run_type.TensorboardRun(request.tensorboard_run)
                tb_run.name = "{}/runs/{}".format(
                    request.parent, request.tensorboard_run_id
                )
                tb_runs.append(tb_run)
            return tensorboard_service.BatchCreateTensorboardRunsResponse(
                tensorboard_runs=tb_runs
            )

        def batch_create_time_series(parent, requests):
            # pylint: disable=unused-argument
            tb_time_series = []
            for request in requests:
                ts = tensorboard_time_series_type.TensorboardTimeSeries(
                    request.tensorboard_time_series
                )
                ts.name = "{}/timeSeries/{}".format(
                    request.parent, request.tensorboard_time_series.display_name
                )
                tb_time_series.append(ts)
            return tensorboard_service.BatchCreateTensorboardTimeSeriesResponse(
                tensorboard_time_series=tb_time_series
            )

        mock_client = _create_mock_client()
        mock_client.batch_create_tensorboard_runs.side_effect = batch_create_runs
        mock_client.batch_create_tensorboard_time_series.side_effect = (
            batch_create_time_series
        )

        mock_rate_limiter = mock.create_autospec(util.RateLimiter)
        mock_tracker = mock.MagicMock()
        with mock.patch.object(
            upload_tracker, "UploadTracker", return_value=mock_tracker
        ):
            uploader = _create_uploader(
                writer_client=mock_client,
                logdir=_TEST_LOG_DIR_NAME,
                # Send each Event below in a separate WriteScalarRequest
                max_scalar_request_size=200,
                rpc_rate_limiter=mock_rate_limiter,
                verbosity=1,  # In order to test the upload tracker.
                one_shot=True,
                description="Test Description",
            )
            uploader.create_experiment()

        mock_logdir_loader = mock.create_autospec(logdir_loader.LogdirLoader)
        mock_logdir_loader.get_run_events.side_effect = [
            {
                "run 1": _apply_compat(
                    [_scalar_event("tag_1.1", 5.0), _scalar_event("tag_1.2", 5.0)]
                ),
                "run 2": _apply_compat(
                    [_scalar_event("tag_2.1", 5.0), _scalar_event("tag_2.2", 5.0)]
                ),
            },
            # Note the lack of AbortUploadError here.
        ]
        mock_logdir_loader_pre_create = mock.create_autospec(logdir_loader.LogdirLoader)
        mock_logdir_loader_pre_create.get_run_events.side_effect = [
            {
                "run 1": _apply_compat(
                    [_scalar_event("tag_1.1", 5.0), _scalar_event("tag_1.2", 5.0)]
                ),
                "run 2": _apply_compat(
                    [_scalar_event("tag_2.1", 5.0), _scalar_event("tag_2.2", 5.0)]
                ),
            },
            # Note the lack of AbortUploadError here.
        ]

        with mock.patch.object(uploader, "_logdir_loader", mock_logdir_loader):
            with mock.patch.object(
                uploader, "_logdir_loader_pre_create", mock_logdir_loader_pre_create
            ):
                uploader.start_uploading()

        self.assertEqual(2, mock_client.write_tensorboard_experiment_data.call_count)
        self.assertEqual(2, mock_rate_limiter.tick.call_count)

        # Check upload tracker calls.
        self.assertEqual(mock_tracker.send_tracker.call_count, 1)
        self.assertEqual(mock_tracker.scalars_tracker.call_count, 2)
        self.assertLen(mock_tracker.scalars_tracker.call_args[0], 1)
        self.assertEqual(mock_tracker.tensors_tracker.call_count, 0)
        self.assertEqual(mock_tracker.blob_tracker.call_count, 0)

    def test_upload_empty_logdir(self):
        logdir = self.get_temp_dir()
        mock_client = _create_mock_client()
        uploader = _create_uploader(mock_client, logdir)
        uploader.create_experiment()
        uploader._upload_once()
        mock_client.write_tensorboard_experiment_data.assert_not_called()

    def test_upload_polls_slowly_once_done(self):
        class SuccessError(Exception):
            pass

        mock_rate_limiter = mock.create_autospec(util.RateLimiter)
        upload_call_count_box = [0]

        def mock_upload_once():
            upload_call_count_box[0] += 1
            tick_count = mock_rate_limiter.tick.call_count
            self.assertEqual(tick_count, upload_call_count_box[0])
            if tick_count >= 3:
                raise SuccessError()

        uploader = _create_uploader(
            logdir=self.get_temp_dir(),
            logdir_poll_rate_limiter=mock_rate_limiter,
        )
        uploader._upload_once = mock_upload_once

        uploader.create_experiment()
        with self.assertRaises(SuccessError):
            uploader.start_uploading()

    def test_upload_swallows_rpc_failure(self):
        logdir = self.get_temp_dir()
        with FileWriter(logdir) as writer:
            writer.add_test_summary("foo")
        mock_client = _create_mock_client()
        uploader = _create_uploader(mock_client, logdir)
        uploader.create_experiment()
        error = _grpc_error(grpc.StatusCode.INTERNAL, "Failure")
        mock_client.write_tensorboard_experiment_data.side_effect = error
        uploader._upload_once()
        mock_client.write_tensorboard_experiment_data.assert_called_once()

    def test_upload_full_logdir(self):
        logdir = self.get_temp_dir()
        mock_client = _create_mock_client()
        uploader = _create_uploader(mock_client, logdir)
        uploader.create_experiment()

        # Convenience helpers for constructing expected requests.
        data = tensorboard_data.TimeSeriesData
        point = tensorboard_data.TimeSeriesDataPoint
        scalar = tensorboard_data.Scalar

        # First round
        writer = FileWriter(logdir)
        metadata = summary_pb2.SummaryMetadata(
            plugin_data=summary_pb2.SummaryMetadata.PluginData(
                plugin_name="scalars", content=b"12345"
            ),
            data_class=summary_pb2.DATA_CLASS_SCALAR,
        )
        writer.add_test_summary("foo", simple_value=5.0, step=1)
        writer.add_test_summary("foo", simple_value=6.0, step=2)
        writer.add_test_summary("foo", simple_value=7.0, step=3)
        writer.add_test_tensor_summary(
            "bar",
            tensor=tensor_pb2.TensorProto(dtype=types_pb2.DT_FLOAT, float_val=[8.0]),
            step=3,
            value_metadata=metadata,
        )
        writer.flush()
        writer_a = FileWriter(os.path.join(logdir, "a"))
        writer_a.add_test_summary("qux", simple_value=9.0, step=2)
        writer_a.flush()
        uploader._upload_once()
        self.assertEqual(3, mock_client.create_tensorboard_time_series.call_count)
        call_args_list = mock_client.create_tensorboard_time_series.call_args_list
        request = call_args_list[1][1]["tensorboard_time_series"]
        self.assertEqual("scalars", request.plugin_name)
        self.assertEqual(b"12345", request.plugin_data)

        self.assertEqual(1, mock_client.write_tensorboard_experiment_data.call_count)
        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list
        request1, request2 = (
            call_args_list[0][1]["write_run_data_requests"][0].time_series_data,
            call_args_list[0][1]["write_run_data_requests"][1].time_series_data,
        )
        _clear_wall_times(request1)
        _clear_wall_times(request2)

        expected_request1 = [
            data(
                tensorboard_time_series_id="foo",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[
                    point(step=1, scalar=scalar(value=5.0)),
                    point(step=2, scalar=scalar(value=6.0)),
                    point(step=3, scalar=scalar(value=7.0)),
                ],
            ),
            data(
                tensorboard_time_series_id="bar",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=3, scalar=scalar(value=8.0))],
            ),
        ]
        expected_request2 = [
            data(
                tensorboard_time_series_id="qux",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=2, scalar=scalar(value=9.0))],
            )
        ]
        self.assertProtoEquals(expected_request1[0], request1[0])
        self.assertProtoEquals(expected_request1[1], request1[1])
        self.assertProtoEquals(expected_request2[0], request2[0])

        mock_client.write_tensorboard_experiment_data.reset_mock()

        # Second round
        writer.add_test_summary("foo", simple_value=10.0, step=5)
        writer.add_test_summary("baz", simple_value=11.0, step=1)
        writer.flush()
        writer_b = FileWriter(os.path.join(logdir, "b"))
        writer_b.add_test_summary("xyz", simple_value=12.0, step=1)
        writer_b.flush()
        uploader._upload_once()
        self.assertEqual(1, mock_client.write_tensorboard_experiment_data.call_count)
        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list
        request3, request4 = (
            call_args_list[0][1]["write_run_data_requests"][0].time_series_data,
            call_args_list[0][1]["write_run_data_requests"][1].time_series_data,
        )
        _clear_wall_times(request3)
        _clear_wall_times(request4)
        expected_request3 = [
            data(
                tensorboard_time_series_id="foo",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=5, scalar=scalar(value=10.0))],
            ),
            data(
                tensorboard_time_series_id="baz",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=1, scalar=scalar(value=11.0))],
            ),
        ]
        expected_request4 = [
            data(
                tensorboard_time_series_id="xyz",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=1, scalar=scalar(value=12.0))],
            )
        ]
        self.assertProtoEquals(expected_request3[0], request3[0])
        self.assertProtoEquals(expected_request3[1], request3[1])
        self.assertProtoEquals(expected_request4[0], request4[0])
        mock_client.write_tensorboard_experiment_data.reset_mock()

        # Empty third round
        uploader._upload_once()
        mock_client.write_tensorboard_experiment_data.assert_not_called()

    def test_verbosity_zero_creates_upload_tracker_with_verbosity_zero(self):
        mock_client = _create_mock_client()
        mock_tracker = mock.MagicMock()
        with mock.patch.object(
            upload_tracker, "UploadTracker", return_value=mock_tracker
        ) as mock_constructor:
            uploader = _create_uploader(
                mock_client,
                _TEST_LOG_DIR_NAME,
                verbosity=0,  # Explicitly set verbosity to 0.
            )
            uploader.create_experiment()

        mock_logdir_loader = mock.create_autospec(logdir_loader.LogdirLoader)
        mock_logdir_loader.get_run_events.side_effect = [
            {
                "run 1": _apply_compat(
                    [_scalar_event("1.1", 5.0), _scalar_event("1.2", 5.0)]
                ),
            },
            AbortUploadError,
        ]

        with mock.patch.object(
            uploader, "_logdir_loader", mock_logdir_loader
        ), self.assertRaises(AbortUploadError):
            uploader.start_uploading()

        self.assertEqual(mock_constructor.call_count, 1)
        self.assertEqual(mock_constructor.call_args[1], {"verbosity": 0})
        self.assertEqual(mock_tracker.scalars_tracker.call_count, 1)

    def test_start_uploading_graphs(self):
        mock_client = _create_mock_client()
        mock_rate_limiter = mock.create_autospec(util.RateLimiter)
        mock_bucket = mock.create_autospec(storage.Bucket)
        mock_blob = mock.create_autospec(storage.Blob)
        mock_bucket.blob.return_value = mock_blob
        mock_tracker = mock.MagicMock()

        def create_time_series(tensorboard_time_series, parent=None):
            return tensorboard_time_series_type.TensorboardTimeSeries(
                name=_TEST_ONE_PLATFORM_TIME_SERIES_NAME,
                display_name=tensorboard_time_series.display_name,
            )

        mock_client.create_tensorboard_time_series.side_effect = create_time_series
        with mock.patch.object(
            upload_tracker, "UploadTracker", return_value=mock_tracker
        ):
            uploader = _create_uploader(
                writer_client=mock_client,
                logdir=_TEST_LOG_DIR_NAME,
                max_blob_request_size=1000,
                rpc_rate_limiter=mock_rate_limiter,
                blob_storage_bucket=mock_bucket,
                verbosity=1,  # In order to test tracker.
            )
            uploader.create_experiment()

        # Of course a real Event stream will never produce the same Event twice,
        # but is this test context it's fine to reuse this one.
        graph_event = event_pb2.Event(graph_def=_create_example_graph_bytes(950))
        expected_graph_def = graph_pb2.GraphDef.FromString(graph_event.graph_def)
        mock_logdir_loader = mock.create_autospec(logdir_loader.LogdirLoader)
        mock_logdir_loader.get_run_events.side_effect = [
            {
                "run 1": _apply_compat([graph_event, graph_event]),
                "run 2": _apply_compat([graph_event, graph_event]),
            },
            {
                "run 3": _apply_compat([graph_event, graph_event]),
                "run 4": _apply_compat([graph_event, graph_event]),
                "run 5": _apply_compat([graph_event, graph_event]),
            },
            AbortUploadError,
        ]

        with mock.patch.object(
            uploader, "_logdir_loader", mock_logdir_loader
        ), self.assertRaises(AbortUploadError):
            uploader.start_uploading()

        self.assertEqual(1, mock_client.create_tensorboard_experiment.call_count)
        self.assertEqual(10, mock_bucket.blob.call_count)

        blob_ids = set()
        for call in mock_bucket.blob.call_args_list:
            request = call[0][0]
            m = re.match(
                "test_folder/tensorboard-.*/test-experiment/.*/{}/(.*)".format(
                    _TEST_TIME_SERIES_NAME
                ),
                request,
            )
            self.assertIsNotNone(m)
            blob_ids.add(m[1])

        for call in mock_blob.upload_from_string.call_args_list:
            request = call[0][0]
            actual_graph_def = graph_pb2.GraphDef.FromString(request)
            self.assertProtoEquals(expected_graph_def, actual_graph_def)

        for call in mock_client.write_tensorboard_experiment_data.call_args_list:
            kargs = call[1]
            time_series_data = kargs["write_run_data_requests"][0].time_series_data
            self.assertEqual(len(time_series_data), 1)
            self.assertEqual(
                time_series_data[0].tensorboard_time_series_id, _TEST_TIME_SERIES_NAME
            )
            self.assertEqual(len(time_series_data[0].values), 2)
            blobs = time_series_data[0].values[0].blobs.values
            self.assertEqual(len(blobs), 1)
            self.assertIn(blobs[0].id, blob_ids)

        # Check upload tracker calls.
        self.assertEqual(mock_tracker.send_tracker.call_count, 2)
        self.assertEqual(mock_tracker.scalars_tracker.call_count, 0)
        self.assertEqual(mock_tracker.tensors_tracker.call_count, 0)
        self.assertEqual(mock_tracker.blob_tracker.call_count, 12)

    def test_filter_graphs(self):
        # Three graphs: one short, one long, one corrupt.
        bytes_0 = _create_example_graph_bytes(123)
        bytes_1 = _create_example_graph_bytes(9999)
        # invalid (truncated) proto: length-delimited field 1 (0x0a) of
        # length 0x7f specified, but only len("bogus") = 5 bytes given
        # <https://developers.google.com/protocol-buffers/docs/encoding>
        bytes_2 = b"\x0a\x7fbogus"

        logdir = self.get_temp_dir()
        for (i, b) in enumerate([bytes_0, bytes_1, bytes_2]):
            run_dir = os.path.join(logdir, "run_%04d" % i)
            event = event_pb2.Event(step=0, wall_time=123 * i, graph_def=b)
            with FileWriter(run_dir) as writer:
                writer.add_event(event)

        limiter = mock.create_autospec(util.RateLimiter)
        limiter.tick.side_effect = [None, AbortUploadError]
        mock_bucket = mock.create_autospec(storage.Bucket)
        mock_blob = mock.create_autospec(storage.Blob)
        mock_bucket.blob.return_value = mock_blob
        mock_client = _create_mock_client()

        def create_time_series(tensorboard_time_series, parent=None):
            return tensorboard_time_series_type.TensorboardTimeSeries(
                name=_TEST_ONE_PLATFORM_TIME_SERIES_NAME,
                display_name=tensorboard_time_series.display_name,
            )

        mock_client.create_tensorboard_time_series.side_effect = create_time_series
        uploader = _create_uploader(
            mock_client,
            logdir,
            logdir_poll_rate_limiter=limiter,
            blob_storage_bucket=mock_bucket,
        )
        uploader.create_experiment()

        with self.assertRaises(AbortUploadError):
            uploader.start_uploading()

        actual_blobs = []
        for call in mock_blob.upload_from_string.call_args_list:
            requests = call[0][0]
            actual_blobs.append(requests)

        actual_graph_defs = []
        for blob in actual_blobs:
            try:
                actual_graph_defs.append(graph_pb2.GraphDef.FromString(blob))
            except message.DecodeError:
                actual_graph_defs.append(None)

        with self.subTest("graphs with small attr values should be unchanged"):
            expected_graph_def_0 = graph_pb2.GraphDef.FromString(bytes_0)
            self.assertEqual(actual_graph_defs[0], expected_graph_def_0)

        with self.subTest("large attr values should be filtered out"):
            expected_graph_def_1 = graph_pb2.GraphDef.FromString(bytes_1)
            del expected_graph_def_1.node[1].attr["large"]
            expected_graph_def_1.node[1].attr["_too_large_attrs"].list.s.append(
                b"large"
            )
            self.assertEqual(actual_graph_defs[1], expected_graph_def_1)

        with self.subTest("corrupt graphs should be skipped"):
            self.assertLen(actual_blobs, 2)

    def test_add_profile_plugin(self):
        run_name = "profile_test_run"
        with tempfile.TemporaryDirectory() as logdir:
            prof_path = os.path.join(
                logdir, run_name, profile_uploader.ProfileRequestSender.PROFILE_PATH
            )
            os.makedirs(prof_path)

            uploader = _create_uploader(
                _create_mock_client(),
                logdir,
                one_shot=True,
                allowed_plugins=frozenset(("profile",)),
                run_name_prefix=run_name,
            )

            uploader.create_experiment()
            uploader._upload_once()
            senders = uploader._dispatcher._additional_senders
            self.assertIn("profile", senders.keys())

            profile_sender = senders["profile"]
            self.assertIn(run_name, profile_sender._run_to_profile_loaders)
            self.assertIn(run_name, profile_sender._run_to_file_request_sender)


# TODO(b/276368161)


class _TensorBoardTrackerTest(tf.test.TestCase):
    def test_thread_continuously_uploads(self):
        """Test Tensorboard Tracker by mimicking its implementation: Call start_upload through a thread and subsequently end the thread by calling _end_uploading()."""

        logdir = self.get_temp_dir()
        mock_client = _create_mock_client()
        uploader = _create_uploader(mock_client, logdir)
        uploader.create_experiment()

        # Convenience helpers for constructing expected requests.
        data = tensorboard_data.TimeSeriesData
        point = tensorboard_data.TimeSeriesDataPoint
        scalar = tensorboard_data.Scalar

        # Directory with scalar data
        writer = FileWriter(logdir)
        metadata = summary_pb2.SummaryMetadata(
            plugin_data=summary_pb2.SummaryMetadata.PluginData(
                plugin_name="scalars", content=b"12345"
            ),
            data_class=summary_pb2.DATA_CLASS_SCALAR,
        )
        writer.add_test_summary("foo", simple_value=5.0, step=1)
        writer.add_test_summary("foo", simple_value=6.0, step=2)
        writer.add_test_summary("foo", simple_value=7.0, step=3)
        writer.add_test_tensor_summary(
            "bar",
            tensor=tensor_pb2.TensorProto(dtype=types_pb2.DT_FLOAT, float_val=[8.0]),
            step=3,
            value_metadata=metadata,
        )
        writer.flush()
        writer_a = FileWriter(os.path.join(logdir, "a"))
        writer_a.add_test_summary("qux", simple_value=9.0, step=2)
        writer_a.flush()
        uploader_thread = threading.Thread(target=uploader.start_uploading)
        uploader_thread.start()
        time.sleep(5)
        self.assertEqual(3, mock_client.create_tensorboard_time_series.call_count)
        call_args_list = mock_client.create_tensorboard_time_series.call_args_list
        request = call_args_list[1][1]["tensorboard_time_series"]
        self.assertEqual("scalars", request.plugin_name)
        self.assertEqual(b"12345", request.plugin_data)

        self.assertEqual(1, mock_client.write_tensorboard_experiment_data.call_count)
        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list
        request1, request2 = (
            call_args_list[0][1]["write_run_data_requests"][0].time_series_data,
            call_args_list[0][1]["write_run_data_requests"][1].time_series_data,
        )
        _clear_wall_times(request1)
        _clear_wall_times(request2)

        expected_request1 = [
            data(
                tensorboard_time_series_id="foo",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[
                    point(step=1, scalar=scalar(value=5.0)),
                    point(step=2, scalar=scalar(value=6.0)),
                    point(step=3, scalar=scalar(value=7.0)),
                ],
            ),
            data(
                tensorboard_time_series_id="bar",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=3, scalar=scalar(value=8.0))],
            ),
        ]
        expected_request2 = [
            data(
                tensorboard_time_series_id="qux",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=2, scalar=scalar(value=9.0))],
            )
        ]
        self.assertProtoEquals(expected_request1[0], request1[0])
        self.assertProtoEquals(expected_request1[1], request1[1])
        self.assertProtoEquals(expected_request2[0], request2[0])

        uploader._end_uploading()
        time.sleep(1)
        self.assertFalse(uploader_thread.is_alive())
        mock_client.write_tensorboard_experiment_data.reset_mock()

        # Empty directory
        uploader._upload_once()
        mock_client.write_tensorboard_experiment_data.assert_not_called()
        uploader._end_uploading()
        time.sleep(1)
        self.assertFalse(uploader_thread.is_alive())


class BatchedRequestSenderTest(tf.test.TestCase):
    def _populate_run_from_events(
        self, n_scalar_events, events, allowed_plugins=_USE_DEFAULT
    ):
        mock_client = _create_mock_client()
        builder = _create_dispatcher(
            experiment_resource_name="123",
            api=mock_client,
            allowed_plugins=allowed_plugins,
        )
        builder.dispatch_requests({"": _apply_compat(events)})
        scalar_requests = mock_client.write_tensorboard_experiment_data.call_args_list
        if scalar_requests:
            self.assertLen(scalar_requests, 1)
            self.assertLen(
                scalar_requests[0][1]["write_run_data_requests"][0].time_series_data,
                n_scalar_events,
            )
        return scalar_requests

    def test_empty_events(self):
        call_args_list = self._populate_run_from_events(0, [])
        self.assertProtoEquals(call_args_list, [])

    def test_scalar_events(self):
        events = [
            event_pb2.Event(summary=scalar_v2_pb("scalar1", 5.0)),
            event_pb2.Event(summary=scalar_v2_pb("scalar2", 5.0)),
        ]
        call_args_lists = self._populate_run_from_events(2, events)
        scalar_tag_counts = _extract_tag_counts(call_args_lists)
        self.assertEqual(scalar_tag_counts, {"scalar1": 1, "scalar2": 1})

    def test_skips_non_scalar_events(self):
        events = [
            event_pb2.Event(summary=scalar_v2_pb("scalar1", 5.0)),
            event_pb2.Event(file_version="brain.Event:2"),
        ]
        call_args_list = self._populate_run_from_events(1, events)
        scalar_tag_counts = _extract_tag_counts(call_args_list)
        self.assertEqual(scalar_tag_counts, {"scalar1": 1})

    def test_skips_non_scalar_events_in_scalar_time_series(self):
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
            event_pb2.Event(summary=scalar_v2_pb("scalar1", 5.0)),
            event_pb2.Event(summary=scalar_v2_pb("scalar2", 5.0)),
        ]
        call_args_list = self._populate_run_from_events(2, events)
        scalar_tag_counts = _extract_tag_counts(call_args_list)
        self.assertEqual(scalar_tag_counts, {"scalar1": 1, "scalar2": 1})

    def test_skips_events_from_disallowed_plugins(self):
        event = event_pb2.Event(
            step=1, wall_time=123.456, summary=scalar_v2_pb("foo", 5.0)
        )
        call_args_lists = self._populate_run_from_events(
            0,
            [event],
            allowed_plugins=frozenset("not-scalars"),
        )
        self.assertEqual(call_args_lists, [])

    def test_remembers_first_metadata_in_time_series(self):
        scalar_1 = event_pb2.Event(summary=scalar_v2_pb("loss", 4.0))
        scalar_2 = event_pb2.Event(summary=scalar_v2_pb("loss", 3.0))
        scalar_2.summary.value[0].ClearField("metadata")
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
            scalar_1,
            scalar_2,
        ]
        call_args_list = self._populate_run_from_events(1, events)
        scalar_tag_counts = _extract_tag_counts(call_args_list)
        self.assertEqual(scalar_tag_counts, {"loss": 2})

    def test_expands_multiple_values_in_event(self):
        event = event_pb2.Event(step=1, wall_time=123.456)
        event.summary.value.add(tag="foo", simple_value=1.0)
        event.summary.value.add(tag="foo", simple_value=2.0)
        event.summary.value.add(tag="foo", simple_value=3.0)
        call_args_list = self._populate_run_from_events(1, [event])

        time_series_data = tensorboard_data.TimeSeriesData(
            tensorboard_time_series_id="foo",
            value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
            values=[
                tensorboard_data.TimeSeriesDataPoint(
                    step=1,
                    wall_time=_timestamp_pb(123456000000),
                    scalar=tensorboard_data.Scalar(value=1.0),
                ),
                tensorboard_data.TimeSeriesDataPoint(
                    step=1,
                    wall_time=_timestamp_pb(123456000000),
                    scalar=tensorboard_data.Scalar(value=2.0),
                ),
                tensorboard_data.TimeSeriesDataPoint(
                    step=1,
                    wall_time=_timestamp_pb(123456000000),
                    scalar=tensorboard_data.Scalar(value=3.0),
                ),
            ],
        )

        self.assertProtoEquals(
            time_series_data,
            call_args_list[0][1]["write_run_data_requests"][0].time_series_data[0],
        )


class ProfileRequestSenderTest(tf.test.TestCase):
    def _create_builder(self, mock_client, logdir):
        return _create_dispatcher(
            experiment_resource_name=_TEST_ONE_PLATFORM_EXPERIMENT_NAME,
            api=mock_client,
            logdir=logdir,
            allowed_plugins=frozenset({"profile"}),
        )

    def _populate_run_from_events(
        self,
        events,
        logdir,
        mock_client=None,
        builder=None,
    ):
        if not mock_client:
            mock_client = _create_mock_client()

        if not builder:
            builder = self._create_builder(mock_client, logdir)

        builder.dispatch_requests({"": _apply_compat(events)})
        profile_requests = mock_client.write_tensorboard_run_data.call_args_list

        return profile_requests

    def test_profile_event_missing_prof_run_dirs(self):
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
        ]
        with tempfile.TemporaryDirectory() as logdir:
            call_args_list = self._populate_run_from_events(events, logdir)

        self.assertProtoEquals(call_args_list, [])

    def test_profile_event_bad_prof_path(self):
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
        ]
        prof_run_name = "bad_run_name"

        with tempfile.TemporaryDirectory() as logdir:
            prof_path = os.path.join(
                logdir, profile_uploader.ProfileRequestSender.PROFILE_PATH
            )
            os.makedirs(prof_path)

            run_path = os.path.join(prof_path, prof_run_name)
            os.makedirs(run_path)

            call_args_list = self._populate_run_from_events(events, logdir)

        self.assertProtoEquals(call_args_list, [])

    def test_profile_event_single_prof_run(self):
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
        ]
        prof_run_name = "2021_01_01_01_10_10"

        with tempfile.TemporaryDirectory() as logdir:
            prof_path = os.path.join(
                logdir, profile_uploader.ProfileRequestSender.PROFILE_PATH
            )
            os.makedirs(prof_path)

            run_path = os.path.join(prof_path, prof_run_name)
            os.makedirs(run_path)

            with tempfile.NamedTemporaryFile(suffix=".xplane.pb", dir=run_path):
                call_args_list = self._populate_run_from_events(events, logdir)

        profile_tag_counts = _extract_tag_counts_time_series(call_args_list)
        self.assertEqual(profile_tag_counts, {prof_run_name: 1})

    def test_profile_event_single_prof_run_new_files(self):
        # Check that files are not uploaded twice for the same profiling run
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
        ]
        prof_run_name = "2021_01_01_01_10_10"
        mock_client = _create_mock_client()

        with tempfile.TemporaryDirectory() as logdir:
            builder = self._create_builder(mock_client=mock_client, logdir=logdir)
            prof_path = os.path.join(
                logdir, profile_uploader.ProfileRequestSender.PROFILE_PATH
            )
            os.makedirs(prof_path)

            run_path = os.path.join(prof_path, prof_run_name)
            os.makedirs(run_path)

            with tempfile.NamedTemporaryFile(
                prefix="a", suffix=".xplane.pb", dir=run_path
            ):
                call_args_list = self._populate_run_from_events(
                    events, logdir, builder=builder, mock_client=mock_client
                )
                with tempfile.NamedTemporaryFile(
                    prefix="b", suffix=".xplane.pb", dir=run_path
                ):
                    call_args_list = self._populate_run_from_events(
                        events, logdir, builder=builder, mock_client=mock_client
                    )

        profile_tag_counts = _extract_tag_counts_time_series(call_args_list)
        self.assertEqual(profile_tag_counts, {prof_run_name: 1})

    def test_profile_event_multi_prof_run(self):
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
        ]
        prof_run_names = [
            "2021_01_01_01_10_10",
            "2021_02_02_02_20_20",
        ]

        with tempfile.TemporaryDirectory() as logdir:
            prof_path = os.path.join(
                logdir, profile_uploader.ProfileRequestSender.PROFILE_PATH
            )
            os.makedirs(prof_path)

            run_paths = [
                os.path.join(prof_path, prof_run_names[0]),
                os.path.join(prof_path, prof_run_names[1]),
            ]
            [os.makedirs(run_path) for run_path in run_paths]

            named_temp = functools.partial(
                tempfile.NamedTemporaryFile, suffix=".xplane.pb"
            )

            with named_temp(dir=run_paths[0]), named_temp(dir=run_paths[1]):
                call_args_list = self._populate_run_from_events(events, logdir)

        self.assertLen(call_args_list, 2)
        profile_tag_counts = _extract_tag_counts_time_series(call_args_list)
        self.assertEqual(profile_tag_counts, dict.fromkeys(prof_run_names, 1))

    def test_profile_event_add_consecutive_prof_runs(self):
        # Multiple profiling events happen one after another, should only update
        # new profiling runs
        events = [
            event_pb2.Event(file_version="brain.Event:2"),
        ]

        prof_run_name = "2021_01_01_01_10_10"

        mock_client = _create_mock_client()

        with tempfile.TemporaryDirectory() as logdir:
            builder = self._create_builder(mock_client=mock_client, logdir=logdir)

            prof_path = os.path.join(
                logdir, profile_uploader.ProfileRequestSender.PROFILE_PATH
            )
            os.makedirs(prof_path)

            run_path = os.path.join(prof_path, prof_run_name)
            os.makedirs(run_path)

            named_temp = functools.partial(
                tempfile.NamedTemporaryFile, suffix=".xplane.pb"
            )

            with named_temp(dir=run_path):
                call_args_list = self._populate_run_from_events(
                    events,
                    logdir,
                    mock_client=mock_client,
                    builder=builder,
                )

            self.assertLen(call_args_list, 1)
            self.assertEqual(
                call_args_list[0][1]["time_series_data"][0].tensorboard_time_series_id,
                prof_run_name,
            )

            prof_run_name_2 = "2021_02_02_02_20_20"

            run_path = os.path.join(prof_path, prof_run_name_2)
            os.makedirs(run_path)
            mock_client.write_tensorboard_run_data.reset_mock()

            with named_temp(dir=run_path):
                call_args_list = self._populate_run_from_events(
                    events,
                    logdir,
                    mock_client=mock_client,
                    builder=builder,
                )

            self.assertLen(call_args_list, 1)
            self.assertEqual(
                call_args_list[0][1]["time_series_data"][0].tensorboard_time_series_id,
                prof_run_name_2,
            )


class ScalarBatchedRequestSenderTest(tf.test.TestCase):
    def _add_events(self, sender, events):
        for event in events:
            for value in event.summary.value:
                sender.add_event(_TEST_RUN_NAME, event, value, value.metadata)

    def _add_events_and_flush(self, events, expected_n_time_series):
        mock_client = _create_mock_client()
        sender = _create_scalar_request_sender(
            experiment_resource_id=_TEST_EXPERIMENT_NAME,
            api=mock_client,
        )
        self._add_events(sender, events)
        sender.flush()

        requests = mock_client.write_tensorboard_experiment_data.call_args_list
        self.assertLen(requests, 1)
        call_args = requests[0]
        self.assertLen(
            call_args[1]["write_run_data_requests"][0].time_series_data,
            expected_n_time_series,
        )
        return call_args

    def test_aggregation_by_tag(self):
        def make_event(step, wall_time, tag, value):
            return event_pb2.Event(
                step=step,
                wall_time=wall_time,
                summary=scalar_v2_pb(tag, value),
            )

        events = [
            make_event(1, 1.0, "one", 11.0),
            make_event(1, 2.0, "two", 22.0),
            make_event(2, 3.0, "one", 33.0),
            make_event(2, 4.0, "two", 44.0),
            make_event(1, 5.0, "one", 55.0),  # Should preserve duplicate step=1.
            make_event(1, 6.0, "three", 66.0),
        ]
        call_args = self._add_events_and_flush(events, 3)
        ts_data = call_args[1]["write_run_data_requests"][0].time_series_data
        tag_data = {
            ts.tensorboard_time_series_id: [
                (
                    value.step,
                    value.wall_time.timestamp_pb().ToSeconds(),
                    value.scalar.value,
                )
                for value in ts.values
            ]
            for ts in ts_data
        }
        self.assertEqual(
            tag_data,
            {
                "one": [(1, 1.0, 11.0), (2, 3.0, 33.0), (1, 5.0, 55.0)],
                "two": [(1, 2.0, 22.0), (2, 4.0, 44.0)],
                "three": [(1, 6.0, 66.0)],
            },
        )

    def test_v1_summary(self):
        event = event_pb2.Event(step=1, wall_time=123.456)
        event.summary.value.add(tag="foo", simple_value=5.0)
        call_args = self._add_events_and_flush(_apply_compat([event]), 1)

        self.assertEqual(_TEST_EXPERIMENT_NAME, call_args[1]["tensorboard_experiment"])
        self.assertEqual(
            [
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="foo",
                    value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                    values=[
                        tensorboard_data.TimeSeriesDataPoint(
                            step=1,
                            wall_time=_timestamp_pb(123456000000),
                            scalar=tensorboard_data.Scalar(value=5.0),
                        )
                    ],
                )
            ],
            call_args[1]["write_run_data_requests"][0].time_series_data,
        )

    def test_v1_summary_tb_summary(self):
        tf_summary = summary_v1.scalar_pb("foo", 5.0)
        tb_summary = summary_pb2.Summary.FromString(tf_summary.SerializeToString())
        event = event_pb2.Event(step=1, wall_time=123.456, summary=tb_summary)
        call_args = self._add_events_and_flush(_apply_compat([event]), 1)

        self.assertEqual(_TEST_EXPERIMENT_NAME, call_args[1]["tensorboard_experiment"])
        self.assertEqual(
            [
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="scalar_summary",
                    value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                    values=[
                        tensorboard_data.TimeSeriesDataPoint(
                            step=1,
                            wall_time=_timestamp_pb(123456000000),
                            scalar=tensorboard_data.Scalar(value=5.0),
                        )
                    ],
                )
            ],
            call_args[1]["write_run_data_requests"][0].time_series_data,
        )

    def test_v2_summary(self):
        event = event_pb2.Event(
            step=1, wall_time=123.456, summary=scalar_v2_pb("foo", 5.0)
        )
        call_args = self._add_events_and_flush(_apply_compat([event]), 1)

        self.assertEqual(_TEST_EXPERIMENT_NAME, call_args[1]["tensorboard_experiment"])
        self.assertEqual(
            [
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="foo",
                    value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                    values=[
                        tensorboard_data.TimeSeriesDataPoint(
                            step=1,
                            wall_time=_timestamp_pb(123456000000),
                            scalar=tensorboard_data.Scalar(value=5.0),
                        )
                    ],
                )
            ],
            call_args[1]["write_run_data_requests"][0].time_series_data,
        )

    def test_propagates_experiment_deletion(self):
        event = event_pb2.Event(step=1)
        event.summary.value.add(tag="foo", simple_value=1.0)

        mock_client = _create_mock_client()
        sender = _create_scalar_request_sender("123", mock_client)
        self._add_events(sender, _apply_compat([event]))

        error = _grpc_error(grpc.StatusCode.NOT_FOUND, "nope")
        mock_client.write_tensorboard_experiment_data.side_effect = error
        with self.assertRaises(uploader_lib.ExperimentNotFoundError):
            sender.flush()

    def test_no_budget_for_base_request(self):
        mock_client = _create_mock_client()
        long_experiment_id = "A" * 12
        with self.assertRaises(uploader_lib._OutOfSpaceError) as cm:
            _create_scalar_request_sender(
                experiment_resource_id=long_experiment_id,
                api=mock_client,
                max_request_size=12,
            )
        self.assertEqual(str(cm.exception), "Byte budget too small for base request")

    def test_no_room_for_single_point(self):
        mock_client = _create_mock_client()
        event = event_pb2.Event(step=1, wall_time=123.456)
        event.summary.value.add(tag="foo", simple_value=1.0)
        sender = _create_scalar_request_sender("123", mock_client, max_request_size=12)
        with self.assertRaises(RuntimeError) as cm:
            self._add_events(sender, [event])
        self.assertEqual(str(cm.exception), "add_event failed despite flush")

    def test_break_at_run_boundary(self):
        mock_client = _create_mock_client()
        # Choose run name sizes such that one run fits in a 1024 byte request,
        # but not two.
        long_run_1 = "A" * 768
        long_run_2 = "B" * 768
        event_1 = event_pb2.Event(step=1)
        event_1.summary.value.add(tag="foo", simple_value=1.0)
        event_2 = event_pb2.Event(step=2)
        event_2.summary.value.add(tag="bar", simple_value=-2.0)

        sender_1 = _create_scalar_request_sender(
            long_run_1,
            mock_client,
            # Set a limit to request size
            max_request_size=1024,
        )

        sender_2 = _create_scalar_request_sender(
            long_run_2,
            mock_client,
            # Set a limit to request size
            max_request_size=1024,
        )
        self._add_events(sender_1, _apply_compat([event_1]))
        self._add_events(sender_2, _apply_compat([event_2]))
        sender_1.flush()
        sender_2.flush()
        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list

        for call_args in call_args_list:
            _clear_wall_times(
                call_args[1]["write_run_data_requests"][0].time_series_data
            )

        # Expect two calls despite a single explicit call to flush().

        expected = [
            [
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="foo",
                    value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                    values=[
                        tensorboard_data.TimeSeriesDataPoint(
                            step=1, scalar=tensorboard_data.Scalar(value=1.0)
                        )
                    ],
                )
            ],
            [
                tensorboard_data.TimeSeriesData(
                    tensorboard_time_series_id="bar",
                    value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                    values=[
                        tensorboard_data.TimeSeriesDataPoint(
                            step=2, scalar=tensorboard_data.Scalar(value=-2.0)
                        )
                    ],
                )
            ],
        ]

        self.assertEqual(
            expected[0],
            call_args_list[0][1]["write_run_data_requests"][0].time_series_data,
        )
        self.assertEqual(
            expected[1],
            call_args_list[1][1]["write_run_data_requests"][0].time_series_data,
        )

    def test_break_at_tag_boundary(self):
        mock_client = _create_mock_client()
        # Choose tag name sizes such that one tag fits in a 1024 byte request,
        # but not two. Note that tag names appear in both `Tag.name` and the
        # summary metadata.
        long_tag_1 = "a" * 384
        long_tag_2 = "b" * 384
        event = event_pb2.Event(step=1)
        event.summary.value.add(tag=long_tag_1, simple_value=1.0)
        event.summary.value.add(tag=long_tag_2, simple_value=2.0)

        sender = _create_scalar_request_sender(
            "train",
            mock_client,
            # Set a limit to request size
            max_request_size=1024,
        )
        self._add_events(sender, _apply_compat([event]))
        sender.flush()
        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list

        request1 = call_args_list[0][1]["write_run_data_requests"][0].time_series_data
        _clear_wall_times(request1)

        # Convenience helpers for constructing expected requests.
        data = tensorboard_data.TimeSeriesData
        point = tensorboard_data.TimeSeriesDataPoint
        scalar = tensorboard_data.Scalar

        expected_request1 = [
            data(
                tensorboard_time_series_id=long_tag_1,
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=1, scalar=scalar(value=1.0))],
            ),
            data(
                tensorboard_time_series_id=long_tag_2,
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=1, scalar=scalar(value=2.0))],
            ),
        ]
        self.assertProtoEquals(expected_request1[0], request1[0])
        self.assertProtoEquals(expected_request1[1], request1[1])

    def test_break_at_scalar_point_boundary(self):
        mock_client = _create_mock_client()
        point_count = 2000  # comfortably saturates a single 1024-byte request
        events = []
        for step in range(point_count):
            summary = scalar_v2_pb("loss", -2.0 * step)
            if step > 0:
                summary.value[0].ClearField("metadata")
            events.append(event_pb2.Event(summary=summary, step=step))

        sender = _create_scalar_request_sender(
            "train",
            mock_client,
            # Set a limit to request size
            max_request_size=1024,
        )
        self._add_events(sender, _apply_compat(events))
        sender.flush()
        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list

        for call_args in call_args_list:
            _clear_wall_times(
                call_args[1]["write_run_data_requests"][0].time_series_data
            )

        self.assertGreater(len(call_args_list), 1)
        self.assertLess(len(call_args_list), point_count)
        # This is the observed number of requests when running the test. There
        # is no reasonable way to derive this value from just reading the code.
        # The number of requests does not have to be 37 to be correct but if it
        # changes it probably warrants some investigation or thought.
        self.assertEqual(37, len(call_args_list))

        total_points_in_result = 0
        for call_args in call_args_list:
            self.assertLen(
                call_args[1]["write_run_data_requests"][0].time_series_data, 1
            )
            time_series_data = call_args[1]["write_run_data_requests"][
                0
            ].time_series_data[0]
            self.assertEqual(time_series_data.tensorboard_time_series_id, "loss")
            for point in time_series_data.values:
                self.assertEqual(point.step, total_points_in_result)
                self.assertEqual(point.scalar.value, -2.0 * point.step)
                total_points_in_result += 1
        self.assertEqual(total_points_in_result, point_count)

    def test_prunes_tags_and_runs(self):
        mock_client = _create_mock_client()
        event_1 = event_pb2.Event(step=1)
        event_1.summary.value.add(tag="foo", simple_value=1.0)
        event_2 = event_pb2.Event(step=2)
        event_2.summary.value.add(tag="bar", simple_value=-2.0)

        add_point_call_count_box = [0]

        def mock_add_point(byte_budget_manager_self, point):
            # Simulate out-of-space error the first time that we try to store
            # the second point.
            add_point_call_count_box[0] += 1
            if add_point_call_count_box[0] == 2:
                raise uploader_lib._OutOfSpaceError()

        with mock.patch.object(
            uploader_lib._ByteBudgetManager,
            "add_point",
            mock_add_point,
        ):
            sender = _create_scalar_request_sender("123", mock_client)
            self._add_events(sender, _apply_compat([event_1]))
            self._add_events(sender, _apply_compat([event_2]))
            sender.flush()

        call_args_list = mock_client.write_tensorboard_experiment_data.call_args_list
        request1, request2 = (
            call_args_list[0][1]["write_run_data_requests"][0].time_series_data,
            call_args_list[1][1]["write_run_data_requests"][0].time_series_data,
        )
        _clear_wall_times(request1)
        _clear_wall_times(request2)

        # Convenience helpers for constructing expected requests.
        data = tensorboard_data.TimeSeriesData
        point = tensorboard_data.TimeSeriesDataPoint
        scalar = tensorboard_data.Scalar

        expected_request1 = [
            data(
                tensorboard_time_series_id="foo",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=1, scalar=scalar(value=1.0))],
            )
        ]

        expected_request2 = [
            data(
                tensorboard_time_series_id="bar",
                value_type=tensorboard_time_series_type.TensorboardTimeSeries.ValueType.SCALAR,
                values=[point(step=2, scalar=scalar(value=-2.0))],
            )
        ]
        self.assertProtoEquals(expected_request1[0], request1[0])
        self.assertProtoEquals(expected_request2[0], request2[0])

    def test_wall_time_precision(self):
        # Test a wall time that is exactly representable in float64 but has enough
        # digits to incur error if converted to nanoseconds the naive way (* 1e9).
        event1 = event_pb2.Event(step=1, wall_time=1567808404.765432119)
        event1.summary.value.add(tag="foo", simple_value=1.0)
        # Test a wall time where as a float64, the fractional part on its own will
        # introduce error if truncated to 9 decimal places instead of rounded.
        event2 = event_pb2.Event(step=2, wall_time=1.000000002)
        event2.summary.value.add(tag="foo", simple_value=2.0)
        call_args = self._add_events_and_flush(_apply_compat([event1, event2]), 1)
        self.assertEqual(
            datetime_helpers.DatetimeWithNanoseconds.from_timestamp_pb(
                _timestamp_pb(1567808404765432119)
            ),
            call_args[1]["write_run_data_requests"][0]
            .time_series_data[0]
            .values[0]
            .wall_time,
        )
        self.assertEqual(
            datetime_helpers.DatetimeWithNanoseconds.from_timestamp_pb(
                _timestamp_pb(1000000002)
            ),
            call_args[1]["write_run_data_requests"][0]
            .time_series_data[0]
            .values[1]
            .wall_time,
        )


class FileRequestSenderTest(tf.test.TestCase):
    def test_empty_files_no_messages(self):
        mock_client = _create_mock_client()
        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
        )

        sender.add_files(
            files=[], tag="my_tag", plugin="test_plugin", event_timestamp=""
        )

        self.assertEmpty(mock_client.write_tensorboard_run_data.call_args_list)

    def test_fake_files_no_sent_messages(self):
        mock_client = _create_mock_client()
        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
        )

        with mock.patch("os.path.isfile", return_value=False):
            sender.add_files(
                files=["fakefile1", "fakefile2"],
                tag="my_tag",
                plugin="test_plugin",
                event_timestamp="",
            )

        self.assertEmpty(mock_client.write_tensorboard_run_data.call_args_list)

    def test_files_too_large(self):
        mock_client = _create_mock_client()
        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
            max_blob_size=10,
        )

        with tempfile.NamedTemporaryFile() as f1:
            f1.write(b"A" * 12)
            f1.flush()
            sender.add_files(
                files=[f1.name],
                tag="my_tag",
                plugin="test_plugin",
                event_timestamp=timestamp_pb2.Timestamp().FromDatetime(
                    datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
                ),
            )

        self.assertEmpty(mock_client.write_tensorboard_run_data.call_args_list)

    def test_single_file_upload(self):
        mock_client = _create_mock_client()
        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
        )

        with tempfile.NamedTemporaryFile() as f1:
            fn = os.path.basename(f1.name)
            sender.add_files(
                files=[f1.name],
                tag="my_tag",
                plugin="test_plugin",
                event_timestamp=timestamp_pb2.Timestamp().FromDatetime(
                    datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
                ),
            )

        call_args_list = mock_client.write_tensorboard_run_data.call_args_list[0][1]
        self.assertEqual(
            fn, call_args_list["time_series_data"][0].values[0].blobs.values[0].id
        )

    def test_multi_file_upload(self):
        mock_client = _create_mock_client()
        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
        )

        files = None
        with tempfile.NamedTemporaryFile() as f1, tempfile.NamedTemporaryFile() as f2:
            files = [os.path.basename(f1.name), os.path.basename(f2.name)]
            sender.add_files(
                files=[f1.name, f2.name],
                tag="my_tag",
                plugin="test_plugin",
                event_timestamp=timestamp_pb2.Timestamp().FromDatetime(
                    datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
                ),
            )

        call_args_list = mock_client.write_tensorboard_run_data.call_args_list[0][1]

        self.assertEqual(
            files,
            [
                x.id
                for x in call_args_list["time_series_data"][0].values[0].blobs.values
            ],
        )

    def test_add_files_no_experiment(self):
        mock_client = _create_mock_client()
        mock_client.write_tensorboard_run_data.side_effect = grpc.RpcError

        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
        )

        with tempfile.NamedTemporaryFile() as f1:
            sender.add_files(
                files=[f1.name],
                tag="my_tag",
                plugin="test_plugin",
                event_timestamp=timestamp_pb2.Timestamp().FromDatetime(
                    datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
                ),
            )

        mock_client.write_tensorboard_run_data.assert_called_once()

    def test_add_files_from_local(self):
        mock_client = _create_mock_client()
        bucket = _create_mock_blob_storage()

        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
            blob_storage_bucket=bucket,
            source_bucket=None,
        )

        with tempfile.NamedTemporaryFile() as f1:
            sender.add_files(
                files=[f1.name],
                tag="my_tag",
                plugin="test_plugin",
                event_timestamp=timestamp_pb2.Timestamp().FromDatetime(
                    datetime.datetime.strptime("2020-01-01", "%Y-%m-%d")
                ),
            )

        bucket.blob.assert_called_once()

    def test_copy_blobs(self):
        mock_client = _create_mock_client()
        sender = _create_file_request_sender(
            api=mock_client,
            run_resource_id=_TEST_ONE_PLATFORM_RUN_NAME,
        )

        sender._copy_between_buckets("gs://path/to/my/file", None)
        self.assertLen(sender._source_bucket.copy_blob.call_args_list, 1)


class VarintCostTest(tf.test.TestCase):
    def test_varint_cost(self):
        self.assertEqual(uploader_lib._varint_cost(0), 1)
        self.assertEqual(uploader_lib._varint_cost(7), 1)
        self.assertEqual(uploader_lib._varint_cost(127), 1)
        self.assertEqual(uploader_lib._varint_cost(128), 2)
        self.assertEqual(uploader_lib._varint_cost(128 * 128 - 1), 2)
        self.assertEqual(uploader_lib._varint_cost(128 * 128), 3)


def _clear_wall_times(repeated_time_series_data):
    """Clears the wall_time fields in a TimeSeriesData to be deterministic.

    Args:
      repeated_time_series_data: Iterable of tensorboard_data.TimeSeriesData.
    """

    for time_series_data in repeated_time_series_data:
        for value in time_series_data.values:
            value.wall_time = None


def _apply_compat(events):
    initial_metadata = {}
    for event in events:
        event = data_compat.migrate_event(event)
        events = dataclass_compat.migrate_event(
            event, initial_metadata=initial_metadata
        )
        for migrated_event in events:
            yield migrated_event


def _extract_tag_counts(call_args_list):
    return {
        ts_data.tensorboard_time_series_id: len(ts_data.values)
        for call_args in call_args_list
        for ts_data in call_args[1]["write_run_data_requests"][0].time_series_data
    }


def _extract_tag_counts_time_series(call_args_list):
    return {
        ts_data.tensorboard_time_series_id: len(ts_data.values)
        for call_args in call_args_list
        for ts_data in call_args[1]["time_series_data"]
    }


if __name__ == "__main__":
    tf.test.main()
