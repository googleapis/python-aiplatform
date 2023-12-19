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

import copy
from importlib import reload
from unittest import mock
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.services import (
    job_service_client_v1beta1,
)
from google.cloud.aiplatform.compat.types import custom_job_v1beta1
from google.cloud.aiplatform.compat.types import encryption_spec_v1beta1
from google.cloud.aiplatform.compat.types import io_v1beta1
from google.cloud.aiplatform.compat.types import (
    job_state_v1beta1 as gca_job_state_compat,
)
from google.cloud.aiplatform.preview import jobs
import constants as test_constants
import pytest

from google.protobuf import duration_pb2


_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME

_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_CUSTOM_JOB_NAME = f"{_TEST_PARENT}/customJobs/{_TEST_ID}"

_TEST_PREBUILT_CONTAINER_IMAGE = "gcr.io/cloud-aiplatform/container:image"

_TEST_RUN_ARGS = test_constants.TrainingJobConstants._TEST_RUN_ARGS
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXPERIMENT_RUN = "test-experiment-run"

_TEST_WORKER_POOL_SPEC = test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC

_TEST_STAGING_BUCKET = test_constants.TrainingJobConstants._TEST_STAGING_BUCKET
_TEST_BASE_OUTPUT_DIR = test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_DEFAULT_ENCRYPTION_SPEC = encryption_spec_v1beta1.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT


_TEST_NETWORK = test_constants.TrainingJobConstants._TEST_NETWORK

_TEST_TIMEOUT = test_constants.TrainingJobConstants._TEST_TIMEOUT
_TEST_RESTART_JOB_ON_WORKER_RESTART = (
    test_constants.TrainingJobConstants._TEST_RESTART_JOB_ON_WORKER_RESTART
)
_TEST_DISABLE_RETRIES = test_constants.TrainingJobConstants._TEST_DISABLE_RETRIES

_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS


# Persistent Resource
_TEST_PERSISTENT_RESOURCE_ID = "test-persistent-resource-1"
_TEST_CUSTOM_JOB_WITH_PERSISTENT_RESOURCE_PROTO = custom_job_v1beta1.CustomJob(
    display_name=_TEST_DISPLAY_NAME,
    job_spec=custom_job_v1beta1.CustomJobSpec(
        worker_pool_specs=_TEST_WORKER_POOL_SPEC,
        base_output_directory=io_v1beta1.GcsDestination(
            output_uri_prefix=_TEST_BASE_OUTPUT_DIR
        ),
        scheduling=custom_job_v1beta1.Scheduling(
            timeout=duration_pb2.Duration(seconds=_TEST_TIMEOUT),
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            disable_retries=_TEST_DISABLE_RETRIES,
        ),
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
    ),
    labels=_TEST_LABELS,
    encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
)


def _get_custom_job_proto(state=None, name=None, error=None):
    custom_job_proto = copy.deepcopy(_TEST_CUSTOM_JOB_WITH_PERSISTENT_RESOURCE_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.error = error
    return custom_job_proto


@pytest.fixture
def create_preview_custom_job_mock():
    with mock.patch.object(
        job_service_client_v1beta1.JobServiceClient, "create_custom_job"
    ) as create_preview_custom_job_mock:
        create_preview_custom_job_mock.return_value = _get_custom_job_proto(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
        )
        yield create_preview_custom_job_mock


@pytest.fixture
def get_custom_job_mock():
    with patch.object(
        job_service_client_v1beta1.JobServiceClient, "get_custom_job"
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


@pytest.mark.usefixtures("google_auth_mock")
class TestCustomJobPersistentResource:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_custom_job_with_persistent_resource(
        self, create_preview_custom_job_mock, get_custom_job_mock, sync
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = jobs.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_preview_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
        assert job.network == _TEST_NETWORK

    def test_submit_custom_job_with_persistent_resource(
        self, create_preview_custom_job_mock, get_custom_job_mock
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = jobs.CustomJob(
            display_name=_TEST_DISPLAY_NAME,
            worker_pool_specs=_TEST_WORKER_POOL_SPEC,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_preview_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_PENDING
        )
        assert job.network == _TEST_NETWORK
