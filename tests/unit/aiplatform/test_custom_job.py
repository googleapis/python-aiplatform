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

import pytest

import copy
from importlib import reload
from unittest import mock
from unittest.mock import patch

from google.protobuf import duration_pb2  # type: ignore
from google.rpc import status_pb2

import test_training_jobs
from test_training_jobs import mock_python_package_to_gcs  # noqa: F401

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import custom_job as gca_custom_job_compat
from google.cloud.aiplatform.compat.types import (
    custom_job_v1beta1 as gca_custom_job_v1beta1,
)
from google.cloud.aiplatform.compat.types import io as gca_io_compat
from google.cloud.aiplatform.compat.types import job_state as gca_job_state_compat
from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec_compat,
)
from google.cloud.aiplatform_v1.services.job_service import client as job_service_client
from google.cloud.aiplatform_v1beta1.services.job_service import (
    client as job_service_client_v1beta1,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "my_job_1234"

_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

_TEST_CUSTOM_JOB_NAME = f"{_TEST_PARENT}/customJobs/{_TEST_ID}"
_TEST_TENSORBOARD_NAME = f"{_TEST_PARENT}/tensorboards/{_TEST_ID}"

_TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"

_TEST_RUN_ARGS = ["-v", "0.1", "--test=arg"]

_TEST_WORKER_POOL_SPEC = [
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

_TEST_STAGING_BUCKET = "gs://test-staging-bucket"
_TEST_BASE_OUTPUT_DIR = f"{_TEST_STAGING_BUCKET}/{_TEST_DISPLAY_NAME}"

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec_compat.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"


_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_ID}"

_TEST_TIMEOUT = 8000
_TEST_RESTART_JOB_ON_WORKER_RESTART = True

_TEST_LABELS = {"my_key": "my_value"}

_TEST_BASE_CUSTOM_JOB_PROTO = gca_custom_job_compat.CustomJob(
    display_name=_TEST_DISPLAY_NAME,
    job_spec=gca_custom_job_compat.CustomJobSpec(
        worker_pool_specs=_TEST_WORKER_POOL_SPEC,
        base_output_directory=gca_io_compat.GcsDestination(
            output_uri_prefix=_TEST_BASE_OUTPUT_DIR
        ),
        scheduling=gca_custom_job_compat.Scheduling(
            timeout=duration_pb2.Duration(seconds=_TEST_TIMEOUT),
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
        ),
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
    ),
    labels=_TEST_LABELS,
    encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
)


def _get_custom_job_proto(state=None, name=None, error=None, version="v1"):
    custom_job_proto = copy.deepcopy(_TEST_BASE_CUSTOM_JOB_PROTO)
    custom_job_proto.name = name
    custom_job_proto.state = state
    custom_job_proto.error = error

    if version == "v1beta1":
        v1beta1_custom_job_proto = gca_custom_job_v1beta1.CustomJob()
        v1beta1_custom_job_proto._pb.MergeFromString(
            custom_job_proto._pb.SerializeToString()
        )
        custom_job_proto = v1beta1_custom_job_proto
        custom_job_proto.job_spec.tensorboard = _TEST_TENSORBOARD_NAME

    return custom_job_proto


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
def create_custom_job_mock_fail():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.side_effect = RuntimeError("Mock fail")
        yield create_custom_job_mock


@pytest.fixture
def create_custom_job_v1beta1_mock():
    with mock.patch.object(
        job_service_client_v1beta1.JobServiceClient, "create_custom_job"
    ) as create_custom_job_mock:
        create_custom_job_mock.return_value = _get_custom_job_proto(
            name=_TEST_CUSTOM_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            version="v1beta1",
        )
        yield create_custom_job_mock


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
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        job.wait()

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT, custom_job=expected_custom_job
        )

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
        assert job.network == _TEST_NETWORK

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
            )

            job.wait()

        # shouldn't fail
        job.wait_for_resource_creation()
        assert job.resource_name == _TEST_CUSTOM_JOB_NAME

        expected_custom_job = _get_custom_job_proto()

        create_custom_job_mock.assert_called_once_with(
            parent=_TEST_PARENT, custom_job=expected_custom_job
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

        get_custom_job_mock.assert_called_once_with(name=_TEST_CUSTOM_JOB_NAME)
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_PENDING
        )
        assert job.job_spec == _TEST_BASE_CUSTOM_JOB_PROTO.job_spec

    @pytest.mark.usefixtures("mock_python_package_to_gcs")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_from_local_script(
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
            script_path=test_training_jobs._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

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

            # configuration on this is tested in test_training_jobs.py
            job = aiplatform.CustomJob.from_local_script(  # noqa: F841
                display_name=_TEST_DISPLAY_NAME,
                script_path=test_training_jobs._TEST_LOCAL_SCRIPT_FILE_NAME,
                container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_custom_job_with_tensorboard(
        self, create_custom_job_v1beta1_mock, get_custom_job_mock, sync
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
        )

        job.wait()

        expected_custom_job = _get_custom_job_proto(version="v1beta1")

        create_custom_job_v1beta1_mock.assert_called_once_with(
            parent=_TEST_PARENT, custom_job=expected_custom_job
        )

        expected_custom_job = _get_custom_job_proto()

        assert job.job_spec == expected_custom_job.job_spec
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    def test_create_custom_job_without_base_output_dir(self,):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = aiplatform.CustomJob(
            display_name=_TEST_DISPLAY_NAME, worker_pool_specs=_TEST_WORKER_POOL_SPEC,
        )

        assert job.job_spec.base_output_directory.output_uri_prefix.startswith(
            f"{_TEST_STAGING_BUCKET}/aiplatform-custom-job"
        )

    @pytest.mark.usefixtures("mock_python_package_to_gcs")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_from_local_script_with_all_args(
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
            script_path=test_training_jobs._TEST_LOCAL_SCRIPT_FILE_NAME,
            container_uri=_TEST_TRAINING_CONTAINER_IMAGE,
            args=_TEST_RUN_ARGS,
            requirements=test_training_jobs._TEST_REQUIREMENTS,
            environment_variables=test_training_jobs._TEST_ENVIRONMENT_VARIABLES,
            replica_count=test_training_jobs._TEST_REPLICA_COUNT,
            machine_type=test_training_jobs._TEST_MACHINE_TYPE,
            accelerator_type=test_training_jobs._TEST_ACCELERATOR_TYPE,
            accelerator_count=test_training_jobs._TEST_ACCELERATOR_COUNT,
            boot_disk_type=test_training_jobs._TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=test_training_jobs._TEST_BOOT_DISK_SIZE_GB,
            base_output_dir=_TEST_BASE_OUTPUT_DIR,
            labels=_TEST_LABELS,
        )

        job.run(sync=sync)

        job.wait()

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
