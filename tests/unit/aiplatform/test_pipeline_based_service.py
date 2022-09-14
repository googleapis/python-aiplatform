# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

from datetime import datetime
import pytest
import json

from unittest import mock
from unittest.mock import patch

from google.auth import credentials as auth_credentials
from google.protobuf import json_format
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base

from google.cloud.aiplatform_v1.services.pipeline_service import (
    client as pipeline_service_client_v1,
)
from google.cloud.aiplatform_v1.types import (
    pipeline_job as gca_pipeline_job_v1,
    pipeline_state as gca_pipeline_state_v1,
)

from google.cloud.aiplatform._pipeline_based_service import pipeline_based_service

# pipeline job
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PIPELINE_JOB_DISPLAY_NAME = "sample-pipeline-job-display-name"
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_CREDENTIALS = auth_credentials.AnonymousCredentials()
_TEST_SERVICE_ACCOUNT = "abcde@my-project.iam.gserviceaccount.com"

_TEST_TEMPLATE_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}/job_spec.json"

_TEST_TEMPLATE_REF = {"test_pipeline_type": _TEST_TEMPLATE_PATH}

_TEST_PIPELINE_ROOT = f"gs://{_TEST_GCS_BUCKET_NAME}/pipeline_root"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_ID}"

_TEST_PIPELINE_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"
_TEST_INVALID_PIPELINE_JOB_NAME = (
    f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_PIPELINE_JOB_ID}"
)
_TEST_PIPELINE_PARAMETER_VALUES = {
    "string_param": "hello world",
    "bool_param": True,
    "double_param": 12.34,
    "int_param": 5678,
    "list_int_param": [123, 456, 789],
    "list_string_param": ["lorem", "ipsum"],
    "struct_param": {"key1": 12345, "key2": 67890},
}

_TEST_PIPELINE_SPEC = {
    "pipelineInfo": {"name": "my-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "string_param": {"parameterType": "STRING"},
                "bool_param": {"parameterType": "BOOLEAN"},
                "double_param": {"parameterType": "NUMBER_DOUBLE"},
                "int_param": {"parameterType": "NUMBER_INTEGER"},
                "list_int_param": {"parameterType": "LIST"},
                "list_string_param": {"parameterType": "LIST"},
                "struct_param": {"parameterType": "STRUCT"},
            }
        },
    },
    "schemaVersion": "2.1.0",
    "components": {},
}

_TEST_INVALID_PIPELINE_SPEC = {
    "pipelineInfo": {"name": "my-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "string_param": {"parameterType": "STRING"},
                "bool_param": {"parameterType": "BOOLEAN"},
                "double_param": {"parameterType": "NUMBER_DOUBLE"},
                "int_param": {"parameterType": "NUMBER_INTEGER"},
                "list_int_param": {"parameterType": "LIST"},
                "list_string_param": {"parameterType": "LIST"},
                "struct_param": {"parameterType": "STRUCT"},
            }
        },
    },
    "schemaVersion": "2.0.0",
    "components": {},
}


_TEST_PIPELINE_JOB = {
    "runtimeConfig": {"parameterValues": {}},
    "pipelineInfo": {"name": "my-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "string_param": {"parameterType": "STRING"},
                "bool_param": {"parameterType": "BOOLEAN"},
                "double_param": {"parameterType": "NUMBER_DOUBLE"},
                "int_param": {"parameterType": "NUMBER_INTEGER"},
                "list_int_param": {"parameterType": "LIST"},
                "list_string_param": {"parameterType": "LIST"},
                "struct_param": {"parameterType": "STRUCT"},
            }
        },
    },
    "schemaVersion": "2.0.0",
    "components": {},
}

_TEST_PIPELINE_CREATE_TIME = datetime.now()


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = gca_pipeline_job_v1.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )
        yield mock_create_pipeline_job


def make_pipeline_job(state):
    return gca_pipeline_job_v1.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
    )


@pytest.fixture
def mock_pipeline_service_get():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_RUNNING
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_pipeline_service_get_with_fail():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_RUNNING
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_RUNNING
            ),
            make_pipeline_job(
                gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_FAILED
            ),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_load_json(job_spec_json):
    with patch.object(storage.Blob, "download_as_bytes") as mock_load_json:
        mock_load_json.return_value = json.dumps(job_spec_json).encode()
        yield mock_load_json


@pytest.fixture
def mock_pipeline_based_service_get():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_based_service:
        mock_get_pipeline_based_service.return_value = gca_pipeline_job_v1.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            pipeline_spec=_TEST_PIPELINE_SPEC,
        )
        yield mock_get_pipeline_based_service


@pytest.mark.usefixtures("google_auth_mock")
class TestPipelineBasedService:
    class FakePipelineBasedService(
        pipeline_based_service._VertexAiPipelineBasedService
    ):
        _template_ref = _TEST_TEMPLATE_REF
        _metadata_output_artifact = "TODO"
        _creation_log_message = (
            "Created PipelineJob for your fake PipelineBasedService."
        )

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "pipeline_name", [_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_NAME]
    )
    def test_init_pipeline_based_service(
        self,
        pipeline_name,
        mock_pipeline_service_get,
        mock_pipeline_based_service_get,
        mock_load_json,
        job_spec_json,
        mock_pipeline_service_create,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        self.FakePipelineBasedService(pipeline_job_name=_TEST_PIPELINE_JOB_ID)

        mock_pipeline_based_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert not mock_pipeline_service_create.called

    @pytest.mark.parametrize(
        "pipeline_name", [_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_NAME]
    )
    def test_init_pipeline_based_service_without_template_ref_raises(
        self,
        pipeline_name,
        mock_pipeline_service_get,
        mock_pipeline_service_create,
    ):
        """
        Raises TypeError since abstract properties '_template_ref' and metadata_output_artifact
        are not set, the VertexAiPipelineBasedService class should only be instantiated through
        a child class.
        """

        with pytest.raises(TypeError):
            pipeline_based_service._VertexAiPipelineBasedService(
                pipeline_job_id=pipeline_name,
            )

    def test_init_pipeline_based_service_with_invalid_pipeline_run_id_raises(
        self,
        mock_pipeline_service_get,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        with pytest.raises(ValueError):
            self.FakePipelineBasedService(
                pipeline_job_name=_TEST_INVALID_PIPELINE_JOB_NAME,
            )

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_PIPELINE_SPEC],
    )
    def test_create_and_submit_pipeline_job(
        self,
        mock_pipeline_service_get,
        mock_pipeline_service_create,
        mock_load_json,
        job_spec_json,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        test_pipeline_service = (
            self.FakePipelineBasedService._create_and_submit_pipeline_job(
                job_id=_TEST_PIPELINE_JOB_ID,
                template_params=_TEST_PIPELINE_PARAMETER_VALUES,
                template_path=_TEST_TEMPLATE_PATH,
                pipeline_root=_TEST_PIPELINE_ROOT,
                display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
            )
        )

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_PIPELINE_ROOT,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job_v1.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        pipeline_spec = job_spec_json.get("pipelineSpec") or job_spec_json

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job_v1.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.1.0",
            },
            runtime_config=runtime_config,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        assert mock_pipeline_service_create.call_count == 1

        test_backing_pipeline_job = test_pipeline_service.backing_pipeline_job

        assert mock_pipeline_service_get.call_count == 1

        assert (
            test_pipeline_service.gca_resource.name
            == test_backing_pipeline_job.resource_name
        )
