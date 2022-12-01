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

import datetime
import json
import pytest
from unittest import mock

from google.auth import credentials as auth_credentials
from google.protobuf import json_format
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.utils import gcs_utils

from google.cloud.aiplatform_v1.services.pipeline_service import (
    client as pipeline_service_client_v1,
)
from google.cloud.aiplatform_v1.types import (
    pipeline_job as gca_pipeline_job_v1,
)
from google.cloud.aiplatform_v1.types import (
    pipeline_state as gca_pipeline_state_v1,
)

from google.cloud.aiplatform._pipeline_based_service import (
    pipeline_based_service,
)

from google.cloud.aiplatform_v1 import Execution as GapicExecution
from google.cloud.aiplatform_v1 import MetadataServiceClient


# pipeline job
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PIPELINE_JOB_DISPLAY_NAME = "sample-pipeline-job-display-name"
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_CREDENTIALS = auth_credentials.AnonymousCredentials()
_TEST_SERVICE_ACCOUNT = "abcde@my-project.iam.gserviceaccount.com"
_TEST_COMPONENT_IDENTIFIER = "fake-pipeline-based-service"
_TEST_PIPELINE_NAME_IDENTIFIER = "my-pipeline"
_TEST_INVALID_PIPELINE_NAME_IDENTIFIER = "not-a-valid-pipeline-name"
_TEST_PIPELINE_CREATE_TIME = datetime.datetime.now()


_TEST_TEMPLATE_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}/job_spec.json"
_TEST_TEMPLATE_REF = {"test_pipeline_type": _TEST_TEMPLATE_PATH}
_TEST_PIPELINE_ROOT = f"gs://{_TEST_GCS_BUCKET_NAME}/pipeline_root"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_ID}"

_TEST_PIPELINE_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"
_TEST_INVALID_PIPELINE_JOB_NAME = (
    f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_PIPELINE_JOB_ID}"
)

# executions: this is used in test_list_pipeline_based_service
_TEST_EXECUTION_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)

_TEST_RUN = "run-1"
_TEST_OTHER_RUN = "run-2"
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}"
_TEST_EXECUTION_NAME = f"{_TEST_EXECUTION_PARENT}/executions/{_TEST_EXECUTION_ID}"


_TEST_OTHER_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_OTHER_RUN}"
_TEST_OTHER_EXECUTION_NAME = (
    f"{_TEST_EXECUTION_PARENT}/executions/{_TEST_OTHER_EXECUTION_ID}"
)

# execution metadata parameters: used in test_list_pipeline_based_service
_TEST_PARAM_KEY_1 = "learning_rate"
_TEST_PARAM_KEY_2 = "dropout"
_TEST_PIPELINE_PARAM_KEY = "pipeline_job_resource_name"
_TEST_PARAMS = {
    _TEST_PARAM_KEY_1: 0.01,
    _TEST_PARAM_KEY_2: 0.2,
    _TEST_PIPELINE_PARAM_KEY: _TEST_PIPELINE_JOB_NAME,
}
_TEST_OTHER_PARAMS = {_TEST_PARAM_KEY_1: 0.02, _TEST_PARAM_KEY_2: 0.3}


# pipeline based service template json
_TEST_PIPELINE_PARAMETER_VALUES = {
    "string_param": "hello world",
    "bool_param": True,
    "double_param": 12.34,
    "int_param": 5678,
    "list_int_param": [123, 456, 789],
    "list_string_param": ["lorem", "ipsum"],
    "struct_param": {"key1": 12345, "key2": 67890},
}

_TEST_PIPELINE_SPEC_JSON = json.dumps(
    {
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
)

_TEST_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {"parameterValues": {}},
        "pipelineSpec": json.loads(_TEST_PIPELINE_SPEC_JSON),
    }
)


def make_pipeline_job(state):
    return gca_pipeline_job_v1.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        pipeline_spec=json.loads(_TEST_PIPELINE_SPEC_JSON),
        job_detail=gca_pipeline_job_v1.PipelineJobDetail(
            task_details=[
                gca_pipeline_job_v1.PipelineTaskDetail(
                    task_id=123,
                    execution=GapicExecution(
                        name=_TEST_EXECUTION_NAME,
                        display_name=_TEST_RUN,
                        schema_title=constants.SYSTEM_RUN,
                        schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                        metadata={"component_type": _TEST_COMPONENT_IDENTIFIER},
                    ),
                ),
            ],
        ),
    )


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = make_pipeline_job(
            gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_create_pipeline_job


@pytest.fixture
def mock_pipeline_job_get():
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
def mock_load_yaml_and_json(job_spec_json):
    with mock.patch.object(
        storage.Blob, "download_as_bytes"
    ) as mock_load_yaml_and_json:
        mock_load_yaml_and_json.return_value = job_spec_json.encode()
        yield mock_load_yaml_and_json


@pytest.fixture
def mock_pipeline_based_service_get():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_based_service:
        mock_get_pipeline_based_service.return_value = make_pipeline_job(
            gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_get_pipeline_based_service


@pytest.fixture
def get_execution_mock():
    with mock.patch.object(
        MetadataServiceClient, "get_execution"
    ) as get_execution_mock:
        get_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
            metadata={"component_type": _TEST_COMPONENT_IDENTIFIER},
        )
        yield get_execution_mock


@pytest.fixture
def list_executions_mock():
    with mock.patch.object(
        MetadataServiceClient, "list_executions"
    ) as list_executions_mock:
        list_executions_mock.return_value = [
            GapicExecution(
                name=_TEST_EXECUTION_NAME,
                display_name=_TEST_RUN,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=_TEST_PARAMS,
            ),
            GapicExecution(
                name=_TEST_OTHER_EXECUTION_NAME,
                display_name=_TEST_OTHER_RUN,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=_TEST_OTHER_PARAMS,
            ),
        ]
        yield list_executions_mock


@pytest.fixture
def mock_pipeline_bucket_exists():
    def mock_create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist(
        output_artifacts_gcs_dir=None,
        service_account=None,
        project=None,
        location=None,
        credentials=None,
    ):
        output_artifacts_gcs_dir = (
            output_artifacts_gcs_dir
            or gcs_utils.generate_gcs_directory_for_pipeline_artifacts(
                project=project,
                location=location,
            )
        )
        return output_artifacts_gcs_dir

    with mock.patch(
        "google.cloud.aiplatform.utils.gcs_utils.create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist",
        wraps=mock_create_gcs_bucket_for_pipeline_artifacts_if_it_does_not_exist,
    ) as mock_context:
        yield mock_context


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
        _component_identifier = _TEST_COMPONENT_IDENTIFIER
        _template_name_identifier = None

        @classmethod
        def submit(cls) -> pipeline_based_service._VertexAiPipelineBasedService:
            return cls._create_and_submit_pipeline_job(
                template_params={}, template_path=_TEST_TEMPLATE_PATH
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
        mock_pipeline_job_get,
        mock_pipeline_based_service_get,
        mock_load_yaml_and_json,
        job_spec_json,
        mock_pipeline_service_create,
        get_execution_mock,
        mock_pipeline_bucket_exists,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
        )

        pipeline_service = self.FakePipelineBasedService(
            pipeline_job_name=pipeline_name
        )

        mock_pipeline_based_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert get_execution_mock.call_count == 1

        # There are 2 get requests made for each item: 1 in the constructor and
        # 1 in the validation method
        assert mock_pipeline_based_service_get.call_count == 2

        assert not mock_pipeline_service_create.called

        assert pipeline_service.backing_pipeline_job._gca_resource == make_pipeline_job(
            gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "pipeline_name", [_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_NAME]
    )
    def test_init_pipeline_based_service_with_template_name_identifier(
        self,
        pipeline_name,
        mock_pipeline_job_get,
        mock_pipeline_based_service_get,
        mock_load_yaml_and_json,
        job_spec_json,
        mock_pipeline_service_create,
        get_execution_mock,
        mock_pipeline_bucket_exists,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
        )

        self.FakePipelineBasedService._template_name_identifier = (
            _TEST_PIPELINE_NAME_IDENTIFIER
        )

        self.FakePipelineBasedService(pipeline_job_name=_TEST_PIPELINE_JOB_ID)

        mock_pipeline_based_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "pipeline_name", [_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_NAME]
    )
    def test_init_pipeline_based_service_with_invalid_template_name_identifier_raises(
        self,
        pipeline_name,
        mock_pipeline_job_get,
        mock_pipeline_based_service_get,
        mock_load_yaml_and_json,
        job_spec_json,
        mock_pipeline_service_create,
        get_execution_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        self.FakePipelineBasedService._template_name_identifier = (
            _TEST_INVALID_PIPELINE_NAME_IDENTIFIER
        )

        with pytest.raises(ValueError):
            self.FakePipelineBasedService(pipeline_job_name=_TEST_PIPELINE_JOB_ID)

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "pipeline_name", [_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_NAME]
    )
    def test_init_pipeline_based_service_with_failed_pipeline_run(
        self,
        pipeline_name,
        mock_pipeline_service_get_with_fail,
        mock_load_yaml_and_json,
        job_spec_json,
        get_execution_mock,
        mock_pipeline_bucket_exists,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
        )

        self.FakePipelineBasedService._template_name_identifier = None

        self.FakePipelineBasedService(pipeline_job_name=_TEST_PIPELINE_JOB_ID)

        mock_pipeline_service_get_with_fail.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert get_execution_mock.call_count == 1

    @pytest.mark.parametrize(
        "pipeline_name", [_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_NAME]
    )
    def test_init_pipeline_based_service_without_template_ref_raises(
        self,
        pipeline_name,
        mock_pipeline_job_get,
        mock_pipeline_service_create,
    ):
        """Raises TypeError since abstract properties are not set.

        _VertexAiPipelineBasedService class should only be instantiated
        through a child class.
        """

        with pytest.raises(TypeError):
            pipeline_based_service._VertexAiPipelineBasedService(
                pipeline_job_id=pipeline_name,
            )

    def test_init_pipeline_based_service_with_invalid_pipeline_run_id_raises(
        self,
        mock_pipeline_job_get,
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
        [_TEST_PIPELINE_JOB],
    )
    def test_create_and_submit_pipeline_job(
        self,
        mock_pipeline_job_get,
        mock_pipeline_service_create,
        mock_load_yaml_and_json,
        job_spec_json,
        mock_pipeline_bucket_exists,
    ):

        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
        )

        self.FakePipelineBasedService._template_name_identifier = None

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

        job_spec_json = yaml.safe_load(job_spec_json)

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

        assert mock_pipeline_job_get.call_count == 1

        assert (
            test_pipeline_service.gca_resource.name
            == test_backing_pipeline_job.resource_name
        )

    def test_list_pipeline_based_service(
        self,
        mock_pipeline_based_service_get,
        get_execution_mock,
        list_executions_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        test_list_request = self.FakePipelineBasedService.list()

        list_executions_mock.assert_called_once_with(
            request={
                "parent": _TEST_EXECUTION_PARENT,
                "filter": f"metadata.component_type.string_value={self.FakePipelineBasedService._component_identifier}",
            }
        )

        assert isinstance(
            test_list_request[0], pipeline_based_service._VertexAiPipelineBasedService
        )

        assert (
            test_list_request[0]._template_ref
            == self.FakePipelineBasedService._template_ref
        )

        # only 1 of the 2 executions in list_executions_mock matches the
        # properties of FakePipelineBasedService
        assert len(test_list_request) == 1

    def test_list_pipeline_based_service_with_template_name_identifier(
        self,
        mock_pipeline_based_service_get,
        get_execution_mock,
        list_executions_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        self.FakePipelineBasedService._template_name_identifier = (
            _TEST_INVALID_PIPELINE_NAME_IDENTIFIER
        )

        test_list_request = self.FakePipelineBasedService.list()

        # None of the mock pipelines match the `_template_name_identifier`
        # set above, so the returned list should be empty
        assert len(test_list_request) == 0
