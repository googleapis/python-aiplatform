# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

import pytest
import logging

import copy
from importlib import reload
from unittest import mock
from unittest.mock import patch, mock_open

from google.api_core import exceptions
import constants as test_constants

from google.rpc import status_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job_compat,
    io,
)

from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state_compat,
    encryption_spec as gca_encryption_spec_compat,
    execution as gca_execution,
)
from google.cloud.aiplatform.compat.services import job_service_client
from google.cloud.aiplatform_v1 import (
    MetadataServiceClient,
    Context as GapicContext,
)
from google.cloud.aiplatform.metadata import constants

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME

_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_CUSTOM_JOB_NAME = f"{_TEST_PARENT}/customJobs/{_TEST_ID}"
_TEST_TENSORBOARD_NAME = f"{_TEST_PARENT}/tensorboards/{_TEST_ID}"
_TEST_ENABLE_WEB_ACCESS = test_constants.TrainingJobConstants._TEST_ENABLE_WEB_ACCESS
_TEST_WEB_ACCESS_URIS = test_constants.TrainingJobConstants._TEST_WEB_ACCESS_URIS
_TEST_TRAINING_CONTAINER_IMAGE = (
    test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE
)
_TEST_PREBUILT_CONTAINER_IMAGE = "gcr.io/cloud-aiplatform/container:image"
_TEST_SPOT_STRATEGY = test_constants.TrainingJobConstants._TEST_SPOT_STRATEGY

_TEST_RUN_ARGS = test_constants.TrainingJobConstants._TEST_RUN_ARGS
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXPERIMENT_RUN = "test-experiment-run"
_TEST_TIMEOUT_SECONDS = test_constants.TrainingJobConstants._TEST_TIMEOUT_SECONDS

_TEST_WORKER_POOL_SPEC = test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC

_TEST_WORKER_POOL_SPEC_WITH_EXPERIMENTS = [
    {
        "machine_spec": {
            "machine_type": "n1-standard-4",
            "accelerator_type": "NVIDIA_TESLA_K80",
            "accelerator_count": 1,
        },
        "replica_count": 1,
        "disk_spec": {"boot_disk_type": "pd-ssd", "boot_disk_size_gb": 100},
        "container_spec": {
            "image_uri": _TEST_TRAINING_CONTAINER_IMAGE,
            "command": [],
            "args": _TEST_RUN_ARGS,
        },
    }
]

_TEST_WORKER_POOL_SPEC_WITH_TPU_V5E = (
    test_constants.TrainingJobConstants._TEST_TPU_V5E_WORKER_POOL_SPEC
)
_TEST_WORKER_POOL_SPEC_WITH_TPU_V3 = (
    test_constants.TrainingJobConstants._TEST_TPU_V3_WORKER_POOL_SPEC
)

_TEST_PYTHON_PACKAGE_SPEC = gca_custom_job_compat.PythonPackageSpec(
    executor_image_uri=_TEST_PREBUILT_CONTAINER_IMAGE,
    package_uris=[test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH],
    python_module=test_constants.TrainingJobConstants._TEST_MODULE_NAME,
)

_TEST_CONTAINER_SPEC = gca_custom_job_compat.ContainerSpec(
    image_uri=_TEST_TRAINING_CONTAINER_IMAGE,
    command=[
        "sh",
        "-c",
        "pip install --upgrade pip && "
        + f"pip3 install -q --user {test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH} && ".replace(
            "gs://", "/gcs/"
        )
        + f"python3 -m {test_constants.TrainingJobConstants._TEST_MODULE_NAME}",
    ],
)

_TEST_STAGING_BUCKET = test_constants.TrainingJobConstants._TEST_STAGING_BUCKET
_TEST_BASE_OUTPUT_DIR = test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec_compat.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT


_TEST_NETWORK = test_constants.TrainingJobConstants._TEST_NETWORK

_TEST_TIMEOUT = test_constants.TrainingJobConstants._TEST_TIMEOUT
_TEST_RESTART_JOB_ON_WORKER_RESTART = (
    test_constants.TrainingJobConstants._TEST_RESTART_JOB_ON_WORKER_RESTART
)
_TEST_DISABLE_RETRIES = test_constants.TrainingJobConstants._TEST_DISABLE_RETRIES
_TEST_MAX_WAIT_DURATION = test_constants.TrainingJobConstants._TEST_MAX_WAIT_DURATION

_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS

_TEST_BASE_CUSTOM_JOB_PROTO = (
    test_constants.TrainingJobConstants._TEST_BASE_CUSTOM_JOB_PROTO
)

_TEST_TPU_V5E_CUSTOM_JOB_PROTO = (
    test_constants.TrainingJobConstants.create_tpu_job_proto(tpu_version="v5e")
)

_TEST_TPU_V3_CUSTOM_JOB_PROTO = (
    test_constants.TrainingJobConstants.create_tpu_job_proto(tpu_version="v3")
)

# Experiment args
_TEST_PARENT_METADATA = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_CONTEXT_ID = "test-experiment"
_TEST_CONTEXT_NAME = f"{_TEST_PARENT_METADATA}/contexts/{_TEST_CONTEXT_ID}"
_TEST_EXPERIMENT_DESCRIPTION = "test-experiment-description"
_TEST_RUN = "run-1"
_TEST_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}"
_TEST_EXPERIMENT_CONTEXT_NAME = f"{_TEST_PARENT_METADATA}/contexts/{_TEST_EXPERIMENT}"
_TEST_EXPERIMENT_RUN_CONTEXT_NAME = (
    f"{_TEST_PARENT_METADATA}/contexts/{_TEST_EXECUTION_ID}"
)

_EXPERIMENT_MOCK = GapicContext(
    name=_TEST_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT,
    description=_TEST_EXPERIMENT_DESCRIPTION,
    schema_title=constants.SYSTEM_EXPERIMENT,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
    metadata={**constants.EXPERIMENT_METADATA},
)


_EXPERIMENT_RUN_MOCK = GapicContext(
    name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
    display_name=_TEST_RUN,
    schema_title=constants.SYSTEM_EXPERIMENT_RUN,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT_RUN],
    metadata={
        constants._PARAM_KEY: {},
        constants._METRIC_KEY: {},
        constants._STATE_KEY: gca_execution.Execution.State.RUNNING.name,
    },
)


def _get_custom_job_proto(state=None, name=None, error=None):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.error = error
    return custom_job_proto


def _get_custom_job_proto_with_experiments(state=None, name=None, error=None):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.job_spec.worker_pool_specs = (
        _TEST_WORKER_POOL_SPEC_WITH_EXPERIMENTS
    )
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.error = error
    custom_job_proto.job_spec.experiment = _TEST_EXPERIMENT_CONTEXT_NAME
    custom_job_proto.job_spec.experiment_run = _TEST_EXPERIMENT_RUN_CONTEXT_NAME
    return custom_job_proto


def _get_custom_job_proto_with_enable_web_access(state=None, name=None, error=None):
    custom_job_proto = _get_custom_job_proto(state=state, name=name, error=error)
    custom_job_proto.job_spec.enable_web_access = _TEST_ENABLE_WEB_ACCESS
    if state == gca_job_state_compat.JobState.JOB_STATE_RUNNING:
        custom_job_proto.web_access_uris = _TEST_WEB_ACCESS_URIS
    return custom_job_proto


def _get_custom_tpu_job_proto(state=None, name=None, error=None, tpu_version=None):
    custom_job_proto = (
        copy.deepcopy(_TEST_TPU_V5E_CUSTOM_JOB_PROTO)
        if tpu_version == "v5e"
        else copy.deepcopy(_TEST_TPU_V3_CUSTOM_JOB_PROTO)
    )

    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.error = error
    return custom_job_proto


def _get_custom_job_proto_with_spot_strategy(state=None, name=None, error=None):
    custom_job_proto = _get_custom_job_proto(state=state, name=name, error=error)
    custom_job_proto.job_spec.scheduling.strategy = _TEST_SPOT_STRATEGY
    return custom_job_proto


@pytest.fixture
def mock_builtin_open():
    with patch("builtins.open", mock_open(read_data="data")) as mock_file:
        yield mock_file


@pytest.fixture
def get_custom_job_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def get_custom_job_with_experiments_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_experiments(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def get_custom_tpu_v5e_job_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_tpu_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
                tpu_version="v5e",
            ),
            _get_custom_tpu_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                tpu_version="v5e",
            ),
            _get_custom_tpu_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
                tpu_version="v5e",
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def get_custom_tpu_v3_job_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_tpu_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
                tpu_version="v3",
            ),
            _get_custom_tpu_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                tpu_version="v3",
            ),
            _get_custom_tpu_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
                tpu_version="v3",
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def get_custom_job_mock_with_fail():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_FAILED,
                error=status_pb2.Status(message="Test Error"),
            ),
            _get_custom_job_proto(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_FAILED,
                error=status_pb2.Status(message="Test Error"),
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def get_custom_job_mock_with_enable_web_access():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def get_custom_job_mock_with_enable_web_access_succeeded():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.return_value = _get_custom_job_proto_with_enable_web_access(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
        )
        yield get_custom_job_mock


@pytest.fixture
def get_custom_job_mock_with_spot_strategy():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as get_custom_job_mock:
        get_custom_job_mock.side_effect = [
            _get_custom_job_proto_with_spot_strategy(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_custom_job_proto_with_spot_strategy(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_custom_job_proto_with_spot_strategy(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_custom_job_mock


@pytest.fixture
def create_custom_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.return_value = _get_custom_job_proto(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
        )
        yield create_custom_job_mock


@pytest.fixture
def create_custom_job_mock_with_enable_web_access():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.return_value = (
            _get_custom_job_proto_with_enable_web_access(
                name=_TEST_CUSTOM_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            )
        )
        yield create_custom_job_mock


@pytest.fixture
def create_custom_job_mock_with_tensorboard():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        custom_job_proto = _get_custom_job_proto(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
        )
        custom_job_proto.job_spec.tensorboard = _TEST_TENSORBOARD_NAME
        create_custom_job_mock.return_value = custom_job_proto
        yield create_custom_job_mock


@pytest.fixture
def create_custom_job_mock_fail():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.side_effect = RuntimeError("Mock fail")
        yield create_custom_job_mock


@pytest.fixture
def create_custom_job_mock_with_spot_strategy():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.return_value = _get_custom_job_proto_with_spot_strategy(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
        )
        yield create_custom_job_mock


_EXPERIMENT_MOCK = copy.deepcopy(_EXPERIMENT_MOCK)
_EXPERIMENT_MOCK.metadata[
    constants._BACKING_TENSORBOARD_RESOURCE_KEY
] = _TEST_TENSORBOARD_NAME

_EXPERIMENT_RUN_MOCK = copy.deepcopy(_EXPERIMENT_RUN_MOCK)


@pytest.fixture
def get_experiment_run_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK,
        ]

        yield get_context_mock


@pytest.fixture
def get_experiment_run_run_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK,
            _EXPERIMENT_RUN_MOCK,
        ]

        yield get_context_mock


@pytest.fixture
def get_experiment_run_not_found_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK,
            _EXPERIMENT_MOCK,
            exceptions.NotFound(""),
        ]

        yield get_context_mock


@pytest.fixture
def update_context_mock():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.return_value = _EXPERIMENT_RUN_MOCK
        yield update_context_mock


@pytest.fixture
def get_tensorboard_run_artifact_not_found_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.side_effect = exceptions.NotFound("")
        yield get_artifact_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestCustomJob:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_custom_job(self, create_custom_job_mock, get_custom_job_mock, sync):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
            network=_TEST_NETWORK,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
        assert job.network == _TEST_NETWORK

    def test_submit_custom_job(self, create_custom_job_mock, get_custom_job_mock):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_PENDING
        )
        assert job.network == _TEST_NETWORK

    @pytest.mark.usefixtures(
        "get_experiment_run_mock", "get_tensorboard_run_artifact_not_found_mock"
    )
    def test_submit_custom_job_with_experiments(
        self, create_custom_job_mock, get_custom_job_mock, update_context_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
            experiment=_TEST_EXPERIMENT,
            experiment_run=_TEST_RUN,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto_with_experiments()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_create_custom_job_with_timeout(
        self, create_custom_job_mock, get_custom_job_mock, sync
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=180.0,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=180.0,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_custom_job_with_timeout_not_explicitly_set(
        self, create_custom_job_mock, get_custom_job_mock, sync
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "create_custom_job_mock",
        "get_custom_job_with_experiments_mock",
        "get_experiment_run_not_found_mock",
        "get_tensorboard_run_artifact_not_found_mock",
    )
    def test_run_custom_job_with_experiment_run_warning(self, caplog):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
            experiment=_TEST_EXPERIMENT,
            experiment_run=_TEST_RUN,
            disable_retries=_TEST_DISABLE_RETRIES,
        )

        assert (
            f"Failed to end experiment run {_TEST_EXPERIMENT_RUN_CONTEXT_NAME} due to:"
            in caplog.text
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_custom_job_with_fail_raises(
        self, create_custom_job_mock, get_custom_job_mock_with_fail, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        with pytest.raises(RuntimeError) as e:
            job.wait_for_resource_creation()
        assert e.match(r"CustomJob resource is not scheduled to be created.")

        with pytest.raises(RuntimeError):
            job.run(
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
                timeout=_TEST_TIMEOUT,
                restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
                sync=sync,
                create_request_timeout=None,
                disable_retries=_TEST_DISABLE_RETRIES,
                max_wait_duration=_TEST_MAX_WAIT_DURATION,
            )

            job.wait()

        # shouldn't fail
        job.wait_for_resource_creation()
        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert job.state == gca_job_state_compat.JobState.JOB_STATE_FAILED

    @pytest.mark.usefixtures("create_custom_job_mock_fail")
    def test_run_custom_job_with_fail_at_creation(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=False,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        with pytest.raises(RuntimeError) as e:
            job.wait_for_resource_creation()
        assert e.match("Mock fail")

        with pytest.raises(RuntimeError) as e:
            job.resource_name
        assert e.match(
            "CustomJob resource has not been created. Resource failed with: Mock fail"
        )

        with pytest.raises(RuntimeError) as e:
            job.network
        assert e.match(
            "CustomJob resource has not been created. Resource failed with: Mock fail"
        )

    def test_custom_job_get_state_raises_without_run(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        with pytest.raises(RuntimeError):
            print(job.state)

    def test_no_staging_bucket_raises(self):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with pytest.raises(RuntimeError):
            job = aiplatform.CustomJob(  # noqa: F841
                display_name=_TEST_DISPLAY_NAME,
                worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            )

    def test_get_custom_job(self, get_custom_job_mock):

        job = aiplatform.CustomJob.get(_TEST_CUSTOM_JOB_NAME)

        get_custom_job_mock.assert_called_once_with(
            name=_TEST_CUSTOM_JOB_NAME, retry=base._DEFAULT_RETRY
        )
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_PENDING
        )
        assert job.job_spec == _TEST_BASE_CUSTOM_JOB_PROTO.job_spec

    @pytest.mark.usefixtures("mock_python_package_to_gcs")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_from_local_script_prebuilt_container(
        self, get_custom_job_mock, create_custom_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        # configuration on this is tested in test_training_jobs.py
        job = aiplatform.CustomJob.from_local_script(
            display_name=_TEST_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_PREBUILT_CONTAINER_IMAGE,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        assert (
            job.job_spec.worker_pool_specs[0].python_package_spec
            == _TEST_PYTHON_PACKAGE_SPEC
        )

        job.run(sync=sync)

        job.wait()

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    @pytest.mark.usefixtures("mock_python_package_to_gcs")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_from_local_script_custom_container(
        self, get_custom_job_mock, create_custom_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        # configuration on this is tested in test_training_jobs.py
        job = aiplatform.CustomJob.from_local_script(
            display_name=_TEST_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        assert job.job_spec.worker_pool_specs[0].container_spec == _TEST_CONTAINER_SPEC

        job.run(sync=sync)

        job.wait()

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    @pytest.mark.usefixtures("mock_python_package_to_gcs")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_from_local_script_raises_with_no_staging_bucket(
        self, get_custom_job_mock, create_custom_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        with pytest.raises(RuntimeError):
            job = aiplatform.CustomJob.from_local_script(  # noqa: F841
                display_name=_TEST_DISPLAY_NAME,
                script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
                container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            )

    @pytest.mark.usefixtures(
        "mock_builtin_open",
        "mock_python_package_to_gcs",
        "get_experiment_run_run_mock",
        "get_tensorboard_run_artifact_not_found_mock",
        "update_context_mock",
    )
    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_create_from_local_script_prebuilt_container_with_all_args(
        self, get_custom_job_mock, create_custom_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob.from_local_script(
            display_name=_TEST_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_PREBUILT_CONTAINER_IMAGE,
            args=_TEST_RUN_ARGS,
            requirements=test_constants.TrainingJobConstants._TEST_REQUIREMENTS,
            environment_variables=test_constants.TrainingJobConstants._TEST_ENVIRONMENT_VARIABLES,
            replica_count=test_constants.TrainingJobConstants._TEST_REPLICA_COUNT,
            machine_type=test_constants.TrainingJobConstants._TEST_MACHINE_TYPE,
            accelerator_type=test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT,
            boot_disk_type=test_constants.TrainingJobConstants._TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=test_constants.TrainingJobConstants._TEST_BOOT_DISK_SIZE_GB,
            reduction_server_replica_count=test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_REPLICA_COUNT,
            reduction_server_machine_type=test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_MACHINE_TYPE,
            reduction_server_container_uri=test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_CONTAINER_URI,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
            enable_autolog=True,
        )

        expected_python_package_spec = _TEST_PYTHON_PACKAGE_SPEC
        expected_python_package_spec.args = _TEST_RUN_ARGS
        expected_python_package_spec.env = [
            {"name": key, "value": value}
            for key, value in test_constants.TrainingJobConstants._TEST_ENVIRONMENT_VARIABLES.items()
        ]

        assert (
            job.job_spec.worker_pool_specs[0].python_package_spec
            == expected_python_package_spec
        )
        assert job._enable_autolog is True

        job.run(
            experiment=_TEST_EXPERIMENT, experiment_run=_TEST_EXPERIMENT_RUN, sync=sync
        )

        job.wait()

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    @pytest.mark.usefixtures(
        "mock_builtin_open",
        "mock_python_package_to_gcs",
        "get_experiment_run_run_mock",
        "get_tensorboard_run_artifact_not_found_mock",
        "update_context_mock",
    )
    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_create_from_local_script_custom_container_with_all_args(
        self, get_custom_job_mock, create_custom_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob.from_local_script(
            display_name=_TEST_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            args=_TEST_RUN_ARGS,
            requirements=test_constants.TrainingJobConstants._TEST_REQUIREMENTS,
            environment_variables=test_constants.TrainingJobConstants._TEST_ENVIRONMENT_VARIABLES,
            replica_count=test_constants.TrainingJobConstants._TEST_REPLICA_COUNT,
            machine_type=test_constants.TrainingJobConstants._TEST_MACHINE_TYPE,
            accelerator_type=test_constants.TrainingJobConstants._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_constants.TrainingJobConstants._TEST_ACCELERATOR_COUNT,
            boot_disk_type=test_constants.TrainingJobConstants._TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=test_constants.TrainingJobConstants._TEST_BOOT_DISK_SIZE_GB,
            reduction_server_replica_count=test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_REPLICA_COUNT,
            reduction_server_machine_type=test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_MACHINE_TYPE,
            reduction_server_container_uri=test_constants.TrainingJobConstants._TEST_REDUCTION_SERVER_CONTAINER_URI,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
            enable_autolog=True,
        )

        expected_container_spec = copy.deepcopy(_TEST_CONTAINER_SPEC)
        expected_container_spec.command[-1] += " " + " ".join(_TEST_RUN_ARGS)
        expected_container_spec.env = [
            {"name": key, "value": value}
            for key, value in test_constants.TrainingJobConstants._TEST_ENVIRONMENT_VARIABLES.items()
        ]

        assert (
            job.job_spec.worker_pool_specs[0].container_spec == expected_container_spec
        )
        assert job._enable_autolog is True

        job.run(
            experiment=_TEST_EXPERIMENT, experiment_run=_TEST_EXPERIMENT_RUN, sync=sync
        )

        job.wait()

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    @pytest.mark.usefixtures("mock_builtin_open", "mock_python_package_to_gcs")
    def test_create_from_local_script_enable_autolog_no_experiment_error(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob.from_local_script(
            display_name=_TEST_DISPLAY_NAME,
            script_path=test_constants.TrainingJobConstants._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
            enable_autolog=True,
        )

        with pytest.raises(ValueError):
            job.run()

    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_create_custom_job_with_enable_web_access(
        self,
        create_custom_job_mock_with_enable_web_access,
        get_custom_job_mock_with_enable_web_access,
        sync,
        caplog,
    ):
        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            enable_web_access=_TEST_ENABLE_WEB_ACCESS,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        job.wait()

        assert "workerpool0-0" in caplog.text

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        expected_custom_job = _get_custom_job_proto_with_enable_web_access()

        create_custom_job_mock_with_enable_web_access.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
        caplog.clear()

    def test_get_web_access_uris(self, get_custom_job_mock_with_enable_web_access):
        job = aiplatform.CustomJob.get(_TEST_CUSTOM_JOB_NAME)
        while True:
            if job.web_access_uris:
                assert job.web_access_uris == _TEST_WEB_ACCESS_URIS
                break

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_log_access_web_uris_after_get(
        self, get_custom_job_mock_with_enable_web_access
    ):
        job = aiplatform.CustomJob.get(_TEST_CUSTOM_JOB_NAME)
        job._block_until_complete()
        assert job._logged_web_access_uris == set(_TEST_WEB_ACCESS_URIS.values())

    def test_get_web_access_uris_job_succeeded(
        self, get_custom_job_mock_with_enable_web_access_succeeded
    ):
        job = aiplatform.CustomJob.get(_TEST_CUSTOM_JOB_NAME)
        assert not job.web_access_uris

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_custom_job_with_tensorboard(
        self, create_custom_job_mock_with_tensorboard, get_custom_job_mock, sync
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            tensorboard=_TEST_TENSORBOARD_NAME,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait()

        expected_custom_job = _get_custom_job_proto()
        expected_custom_job.job_spec.tensorboard = _TEST_TENSORBOARD_NAME

        create_custom_job_mock_with_tensorboard.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        expected_custom_job = _get_custom_job_proto()

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    def test_create_custom_job_without_base_output_dir(
        self,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
        )

        assert job.job_spec.base_output_directory.output_uri_prefix.startswith(
            f"{_TEST_STAGING_BUCKET}/aiplatform-custom-job"
        )

    @pytest.mark.usefixtures("get_custom_job_mock", "create_custom_job_mock")
    def test_check_custom_job_availability(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        assert not job._resource_is_available
        assert job.__repr__().startswith(
            "<google.cloud.aiplatform.jobs.CustomJob object"
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        assert job._resource_is_available
        assert "resource name" in job.__repr__()

        job.wait()

    def test_create_custom_job_tpu_v5e(
        self, create_custom_job_mock, get_custom_tpu_v5e_job_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            network=_TEST_NETWORK,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC_WITH_TPU_V5E,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        job.run(
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=_TEST_WORKER_POOL_SPEC_WITH_TPU_V5E,
                base_output_directory=io.GcsDestination(
                    output_uri_prefix=_TEST_BASE_OUTPUT_DIR
                ),
                scheduling=gca_custom_job_compat.Scheduling(
                    timeout=_TEST_TIMEOUT_SECONDS,
                    restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
                ),
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
            ),
        )

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    def test_create_custom_job_tpu_v3(
        self, create_custom_job_mock, get_custom_tpu_v3_job_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            network=_TEST_NETWORK,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC_WITH_TPU_V3,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
        )

        job.run(
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=_TEST_WORKER_POOL_SPEC_WITH_TPU_V3,
                base_output_directory=io.GcsDestination(
                    output_uri_prefix=_TEST_BASE_OUTPUT_DIR
                ),
                scheduling=gca_custom_job_compat.Scheduling(
                    timeout=_TEST_TIMEOUT_SECONDS,
                    restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
                ),
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
            ),
        )

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    def test_create_custom_job_with_spot_strategy(
        self,
        create_custom_job_mock_with_spot_strategy,
        get_custom_job_mock_with_spot_strategy,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            scheduling_strategy=_TEST_SPOT_STRATEGY,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait_for_resource_creation()

        job.wait()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        expected_custom_job = _get_custom_job_proto_with_spot_strategy()

        create_custom_job_mock_with_spot_strategy.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
