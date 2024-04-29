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

import pytest
import json

from unittest import mock
from importlib import reload
from unittest.mock import patch
from urllib import request
from datetime import datetime

from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.constants import pipeline as pipeline_constants
from google.cloud.aiplatform_v1 import Context as GapicContext
from google.cloud.aiplatform_v1 import MetadataStore as GapicMetadataStore
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform_v1 import MetadataServiceClient
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform.compat.types import pipeline_failure_policy
from google.cloud.aiplatform.utils import gcs_utils
from google.cloud import storage
from google.protobuf import json_format
from google.protobuf import field_mask_pb2 as field_mask

from google.cloud.aiplatform.compat.services import (
    pipeline_service_client,
)
from google.cloud.aiplatform_v1beta1.types import (
    pipeline_service as PipelineServiceV1Beta1,
)
from google.cloud.aiplatform_v1.types import (
    pipeline_service as PipelineServiceV1,
)
from google.cloud.aiplatform_v1beta1.services import (
    pipeline_service as v1beta1_pipeline_service,
)
from google.cloud.aiplatform_v1beta1.types import (
    pipeline_job as v1beta1_pipeline_job,
    pipeline_state as v1beta1_pipeline_state,
    context as v1beta1_context,
)
from google.cloud.aiplatform.preview.pipelinejob import (
    pipeline_jobs as preview_pipeline_jobs,
)
from google.cloud.aiplatform.compat.types import (
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
    context as gca_context,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PIPELINE_JOB_DISPLAY_NAME = "sample-pipeline-job-display-name"
_TEST_PIPELINE_JOB_DISPLAY_NAME_2 = "sample-pipeline-job-display-name-2"
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
_TEST_PIPELINE_JOB_ID_2 = "sample-test-pipeline-202111112"
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_GCS_OUTPUT_DIRECTORY = f"gs://{_TEST_GCS_BUCKET_NAME}/output_artifacts/"
_TEST_CREDENTIALS = auth_credentials.AnonymousCredentials()
_TEST_SERVICE_ACCOUNT = "abcde@my-project.iam.gserviceaccount.com"

_TEST_TEMPLATE_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}/job_spec.json"
_TEST_AR_TEMPLATE_PATH = "https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"
_TEST_HTTPS_TEMPLATE_PATH = "https://raw.githubusercontent.com/repo/pipeline.json"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_ID}"
_TEST_RESERVED_IP_RANGES = ["vertex-ai-ip-range"]

_TEST_PIPELINE_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"
_TEST_PIPELINE_JOB_NAME_2 = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID_2}"
_TEST_PIPELINE_JOB_LIST_READ_MASK = field_mask.FieldMask(
    paths=pipeline_constants._READ_MASK_FIELDS
)

_TEST_PIPELINE_PARAMETER_VALUES_LEGACY = {"string_param": "hello"}
_TEST_PIPELINE_PARAMETER_VALUES = {
    "string_param": "hello world",
    "bool_param": True,
    "double_param": 12.34,
    "int_param": 5678,
    "list_int_param": [123, 456, 789],
    "list_string_param": ["lorem", "ipsum"],
    "struct_param": {"key1": 12345, "key2": 67890},
}

_TEST_PIPELINE_INPUT_ARTIFACTS = {
    "vertex_model": "456",
}

_TEST_PIPELINE_SPEC_LEGACY_JSON = json.dumps(
    {
        "pipelineInfo": {"name": "my-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {"parameters": {"string_param": {"type": "STRING"}}},
        },
        "schemaVersion": "2.0.0",
        "components": {},
    }
)
_TEST_PIPELINE_SPEC_LEGACY_YAML = """\
pipelineInfo:
  name: my-pipeline
root:
  dag:
    tasks: {}
  inputDefinitions:
    parameters:
      string_param:
        type: STRING
schemaVersion: 2.0.0
components: {}
"""
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
_TEST_PIPELINE_SPEC_YAML = """\
pipelineInfo:
  name: my-pipeline
root:
  dag:
    tasks: {}
  inputDefinitions:
    parameters:
      string_param:
        parameterType: STRING
      bool_param:
        parameterType: BOOLEAN
      double_param:
        parameterType: NUMBER_DOUBLE
      int_param:
        parameterType: NUMBER_INTEGER
      list_int_param:
        parameterType: LIST
      list_string_param:
        parameterType: LIST
      struct_param:
        parameterType: STRUCT
schemaVersion: 2.1.0
components: {}
"""
_TEST_TFX_PIPELINE_SPEC_JSON = json.dumps(
    {
        "pipelineInfo": {"name": "my-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {"parameters": {"string_param": {"type": "STRING"}}},
        },
        "schemaVersion": "2.0.0",
        "sdkVersion": "tfx-1.4.0",
        "components": {},
    }
)
_TEST_TFX_PIPELINE_SPEC_YAML = """\
pipelineInfo:
  name: my-pipeline
root:
  dag:
    tasks: {}
  inputDefinitions:
    parameters:
      string_param:
        type: STRING
schemaVersion: 2.0.0
sdkVersion: tfx-1.4.0
components: {}
"""

_TEST_PIPELINE_JOB_LEGACY = json.dumps(
    {"runtimeConfig": {}, "pipelineSpec": json.loads(_TEST_PIPELINE_SPEC_LEGACY_JSON)}
)
_TEST_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {"parameterValues": _TEST_PIPELINE_PARAMETER_VALUES},
        "pipelineSpec": json.loads(_TEST_PIPELINE_SPEC_JSON),
    }
)
_TEST_PIPELINE_JOB_TFX = json.dumps(
    {"runtimeConfig": {}, "pipelineSpec": json.loads(_TEST_TFX_PIPELINE_SPEC_JSON)}
)

_TEST_PIPELINE_GET_METHOD_NAME = "get_fake_pipeline_job"
_TEST_PIPELINE_LIST_METHOD_NAME = "list_fake_pipeline_jobs"
_TEST_PIPELINE_CANCEL_METHOD_NAME = "cancel_fake_pipeline_job"
_TEST_PIPELINE_DELETE_METHOD_NAME = "delete_fake_pipeline_job"
_TEST_PIPELINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/fakePipelineJobs/{_TEST_PIPELINE_JOB_ID}"
)
_TEST_PIPELINE_CREATE_TIME = datetime.now()

# experiments
_TEST_EXPERIMENT = "test-experiment"

_TEST_METADATASTORE = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_CONTEXT_ID = _TEST_EXPERIMENT
_TEST_CONTEXT_NAME = f"{_TEST_METADATASTORE}/contexts/{_TEST_CONTEXT_ID}"

_EXPERIMENT_MOCK = GapicContext(
    name=_TEST_CONTEXT_NAME,
    schema_title=constants.SYSTEM_EXPERIMENT,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
    metadata={**constants.EXPERIMENT_METADATA},
)


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = gca_pipeline_job.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
        )
        yield mock_create_pipeline_job


@pytest.fixture
def mock_pipeline_v1beta1_service_create():
    with mock.patch.object(
        v1beta1_pipeline_service.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = v1beta1_pipeline_job.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
        )
        yield mock_create_pipeline_job


@pytest.fixture
def mock_pipeline_v1_service_batch_cancel():
    with patch.object(
        pipeline_service_client.PipelineServiceClient, "batch_cancel_pipeline_jobs"
    ) as batch_cancel_pipeline_jobs_mock:
        batch_cancel_pipeline_jobs_mock.return_value = mock.Mock(ga_operation.Operation)
        yield batch_cancel_pipeline_jobs_mock


@pytest.fixture
def mock_pipeline_v1_service_batch_delete():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "batch_delete_pipeline_jobs"
    ) as mock_batch_pipeline_jobs:
        mock_batch_pipeline_jobs.return_value = (
            make_v1_batch_delete_pipeline_jobs_response()
        )
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = make_v1_batch_delete_pipeline_jobs_response()
        mock_batch_pipeline_jobs.return_value = mock_lro
        yield mock_batch_pipeline_jobs


def make_v1_batch_delete_pipeline_jobs_response():
    response = PipelineServiceV1.BatchDeletePipelineJobsResponse()
    response.pipeline_jobs.append(
        make_pipeline_job_with_name(
            _TEST_PIPELINE_JOB_NAME,
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
        )
    )
    response.pipeline_jobs.append(
        make_pipeline_job_with_name(
            _TEST_PIPELINE_JOB_NAME_2,
            gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
        )
    )
    return response


@pytest.fixture
def mock_pipeline_v1beta1_service_batch_delete():
    with mock.patch.object(
        v1beta1_pipeline_service.PipelineServiceClient, "batch_delete_pipeline_jobs"
    ) as mock_batch_pipeline_jobs:
        mock_batch_pipeline_jobs.return_value = (
            make_batch_delete_pipeline_jobs_response()
        )
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = make_batch_delete_pipeline_jobs_response()
        mock_batch_pipeline_jobs.return_value = mock_lro
        yield mock_batch_pipeline_jobs


def make_v1beta1_pipeline_job(name: str, state: v1beta1_pipeline_state.PipelineState):
    return v1beta1_pipeline_job.PipelineJob(
        name=name,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        job_detail=v1beta1_pipeline_job.PipelineJobDetail(
            pipeline_run_context=v1beta1_context.Context(
                name=name,
            )
        ),
    )


def make_batch_delete_pipeline_jobs_response():
    response = PipelineServiceV1Beta1.BatchDeletePipelineJobsResponse()
    response.pipeline_jobs.append(
        make_v1beta1_pipeline_job(
            _TEST_PIPELINE_JOB_NAME,
            v1beta1_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
        )
    )
    response.pipeline_jobs.append(
        make_v1beta1_pipeline_job(
            _TEST_PIPELINE_JOB_NAME_2,
            v1beta1_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
        )
    )
    return response


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


def make_pipeline_job(state):
    return gca_pipeline_job.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
        job_detail=gca_pipeline_job.PipelineJobDetail(
            pipeline_run_context=gca_context.Context(
                name=_TEST_PIPELINE_JOB_NAME,
            )
        ),
    )


def make_pipeline_job_with_name(name, state):
    return gca_pipeline_job.PipelineJob(
        name=name,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
        job_detail=gca_pipeline_job.PipelineJobDetail(
            pipeline_run_context=gca_context.Context(
                name=name,
            )
        ),
    )


@pytest.fixture
def mock_pipeline_service_get():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_pipeline_service_get_with_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_pipeline_service_cancel():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "cancel_pipeline_job"
    ) as mock_cancel_pipeline_job:
        yield mock_cancel_pipeline_job


@pytest.fixture
def mock_pipeline_service_list():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "list_pipeline_jobs"
    ) as mock_list_pipeline_jobs:
        mock_list_pipeline_jobs.return_value = [
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]
        yield mock_list_pipeline_jobs


@pytest.fixture
def mock_load_yaml_and_json(job_spec):
    with patch.object(storage.Blob, "download_as_bytes") as mock_load_yaml_and_json:
        mock_load_yaml_and_json.return_value = job_spec.encode()
        yield mock_load_yaml_and_json


@pytest.fixture
def mock_request_urlopen(job_spec):
    with patch.object(request, "urlopen") as mock_urlopen:
        mock_read_response = mock.MagicMock()
        mock_decode_response = mock.MagicMock()
        mock_decode_response.return_value = job_spec.encode()
        mock_read_response.return_value.decode = mock_decode_response
        mock_urlopen.return_value.read = mock_read_response
        yield mock_urlopen


# experiment mocks
@pytest.fixture
def get_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            name=_TEST_METADATASTORE,
        )
        yield get_metadata_store_mock


@pytest.fixture
def get_experiment_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = _EXPERIMENT_MOCK
        yield get_context_mock


@pytest.fixture
def add_context_children_mock():
    with patch.object(
        MetadataServiceClient, "add_context_children"
    ) as add_context_children_mock:
        yield add_context_children_mock


@pytest.fixture
def list_contexts_mock():
    with patch.object(MetadataServiceClient, "list_contexts") as list_contexts_mock:
        list_contexts_mock.return_value = [_EXPERIMENT_MOCK]
        yield list_contexts_mock


@pytest.fixture
def create_experiment_run_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.side_effect = [_EXPERIMENT_MOCK]
        yield create_context_mock


def make_pipeline_job_with_experiment(state):
    return gca_pipeline_job.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        job_detail=gca_pipeline_job.PipelineJobDetail(
            pipeline_run_context=gca_context.Context(
                name=_TEST_PIPELINE_JOB_NAME,
                parent_contexts=[_TEST_CONTEXT_NAME],
            ),
        ),
    )


@pytest.fixture
def mock_create_pipeline_job_with_experiment():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_pipeline_job"
    ) as mock_pipeline_with_experiment:
        mock_pipeline_with_experiment.return_value = make_pipeline_job_with_experiment(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_pipeline_with_experiment


@pytest.fixture
def mock_get_pipeline_job_with_experiment():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_pipeline_with_experiment:
        mock_pipeline_with_experiment.side_effect = [
            make_pipeline_job_with_experiment(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING
            ),
            make_pipeline_job_with_experiment(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]
        yield mock_pipeline_with_experiment


@pytest.mark.usefixtures("google_auth_mock")
class TestPipelineJob:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(pipeline_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(pipeline_jobs, "_LOG_WAIT_TIME", 1)
    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        job.run(
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
            "inputArtifacts": {"vertex_model": {"artifactId": "456"}},
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_run_with_reserved_ip_ranges(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        job.run(
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
            "inputArtifacts": {"vertex_model": {"artifactId": "456"}},
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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
            reserved_ip_ranges=_TEST_RESERVED_IP_RANGES,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_artifact_registry(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_AR_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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
            template_uri=_TEST_AR_TEMPLATE_PATH,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_https(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_HTTPS_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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
            template_uri=_TEST_HTTPS_TEMPLATE_PATH,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
        ],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_timeout(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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
            timeout=180.0,
        )

        # mock_pipeline_service_get.assert_called_with(
        #     name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        # )

        # assert job._gca_resource == make_pipeline_job(
        #     gca_pipeline_state_v1.PipelineState.PIPELINE_STATE_SUCCEEDED
        # )

    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
        ],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_timeout_not_explicitly_set(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize(
        "failure_policy",
        [
            (
                "slow",
                pipeline_failure_policy.PipelineFailurePolicy.PIPELINE_FAILURE_POLICY_FAIL_SLOW,
            ),
            (
                "fast",
                pipeline_failure_policy.PipelineFailurePolicy.PIPELINE_FAILURE_POLICY_FAIL_FAST,
            ),
        ],
    )
    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(pipeline_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(pipeline_jobs, "_LOG_WAIT_TIME", 1)
    def test_run_call_pipeline_service_create_with_failure_policy(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        failure_policy,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
            failure_policy=failure_policy[0],
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
            "failurePolicy": failure_policy[1],
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_legacy(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES_LEGACY,
            enable_caching=True,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameters": {"string_param": {"stringValue": "hello"}},
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.0.0",
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

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_TFX_PIPELINE_SPEC_JSON,
            _TEST_TFX_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB_TFX,
        ],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_tfx(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
        sync,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES_LEGACY,
            enable_caching=True,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameters": {"string_param": {"stringValue": "hello"}},
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.0.0",
                "sdkVersion": "tfx-1.4.0",
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

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_submit_call_pipeline_service_pipeline_job_create(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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

        assert not mock_pipeline_service_get.called

        job.wait()

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_submit_call_gcs_utils_get_or_create_with_correct_arguments(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
            project=_TEST_PROJECT,
            pipeline_root=_TEST_GCS_OUTPUT_DIRECTORY,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        mock_pipeline_bucket_exists.assert_called_once_with(
            output_artifacts_gcs_dir=_TEST_GCS_OUTPUT_DIRECTORY,
            service_account=_TEST_SERVICE_ACCOUNT,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_done_method_pipeline_service(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.submit(service_account=_TEST_SERVICE_ACCOUNT, network=_TEST_NETWORK)

        assert job.done() is False

        job.wait()

        assert job.done() is True

    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_submit_call_pipeline_service_pipeline_job_create_legacy(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES_LEGACY,
            enable_caching=True,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        expected_runtime_config_dict = {
            "parameters": {"string_param": {"stringValue": "hello"}},
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.0.0",
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

        assert not mock_pipeline_service_get.called

        job.wait()

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert job._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.usefixtures("mock_pipeline_service_get")
    def test_get_pipeline_job(self, mock_pipeline_service_get):
        aiplatform.init(project=_TEST_PROJECT)
        job = pipeline_jobs.PipelineJob.get(resource_name=_TEST_PIPELINE_JOB_ID)

        mock_pipeline_service_get.assert_called_once_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )
        assert isinstance(job, pipeline_jobs.PipelineJob)

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_pipeline_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_cancel_pipeline_job(
        self, mock_pipeline_service_cancel, mock_load_yaml_and_json
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        job.run()
        job.cancel()

        mock_pipeline_service_cancel.assert_called_once_with(
            name=_TEST_PIPELINE_JOB_NAME
        )

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_pipeline_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_list_pipeline_job(
        self, mock_pipeline_service_list, mock_load_yaml_and_json
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        job.run()
        job.list()

        mock_pipeline_service_list.assert_called_once_with(
            request={"parent": _TEST_PARENT}
        )

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_pipeline_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_list_pipeline_job_with_read_mask(
        self, mock_pipeline_service_list, mock_load_yaml_and_json
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        job.run()
        job.list(enable_simple_view=True)

        mock_pipeline_service_list.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "read_mask": _TEST_PIPELINE_JOB_LIST_READ_MASK,
            },
        )

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_cancel_pipeline_job_without_running(
        self,
        mock_pipeline_service_cancel,
        mock_load_yaml_and_json,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        with pytest.raises(RuntimeError) as e:
            job.cancel()

        assert e.match(regexp=r"PipelineJob resource has not been created")

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get_with_fail",
        "mock_pipeline_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(pipeline_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(pipeline_jobs, "_LOG_WAIT_TIME", 1)
    def test_pipeline_failure_raises(self, mock_load_yaml_and_json, sync):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        with pytest.raises(RuntimeError):
            job.run(
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
                sync=sync,
            )

            if not sync:
                job.wait()

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get_with_fail",
        "mock_pipeline_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_pipeline_job_has_failed_property(self, mock_load_yaml_and_json):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING
        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING
        assert job.has_failed

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_pipeline_job_has_failed_property_with_no_submit(
        self, mock_load_yaml_and_json
    ):
        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        with pytest.raises(
            RuntimeError,
            match=r"PipelineJob resource has not been created\.",
        ):
            assert job.has_failed

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_clone_pipeline_job(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        cloned = job.clone(job_id=f"cloned-{_TEST_PIPELINE_JOB_ID}")

        cloned.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
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
            pipeline_job_id=f"cloned-{_TEST_PIPELINE_JOB_ID}",
            timeout=None,
        )

        assert not mock_pipeline_service_get.called

        cloned.wait()

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert cloned._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_clone_pipeline_job_with_all_args(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        import yaml

        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        cloned = job.clone(
            display_name=f"cloned-{_TEST_PIPELINE_JOB_DISPLAY_NAME}",
            job_id=f"cloned-{_TEST_PIPELINE_JOB_ID}",
            pipeline_root=f"cloned-{_TEST_GCS_BUCKET_NAME}",
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
            credentials=_TEST_CREDENTIALS,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        cloned.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        expected_runtime_config_dict = {
            "gcsOutputDirectory": f"cloned-{_TEST_GCS_BUCKET_NAME}",
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
            "inputArtifacts": {"vertex_model": {"artifactId": "456"}},
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=f"cloned-{_TEST_PIPELINE_JOB_DISPLAY_NAME}",
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
            pipeline_job_id=f"cloned-{_TEST_PIPELINE_JOB_ID}",
            timeout=None,
        )

        assert not mock_pipeline_service_get.called

        cloned.wait()

        mock_pipeline_service_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert cloned._gca_resource == make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_get_associated_experiment_from_pipeline_returns_none_without_experiment(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        job_spec,
        mock_load_yaml_and_json,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        job.wait()

        test_experiment = job.get_associated_experiment()

        assert test_experiment is None

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_get_associated_experiment_from_pipeline_returns_experiment(
        self,
        job_spec,
        mock_load_yaml_and_json,
        add_context_children_mock,
        get_experiment_mock,
        create_experiment_run_context_mock,
        get_metadata_store_mock,
        mock_create_pipeline_job_with_experiment,
        mock_get_pipeline_job_with_experiment,
        mock_pipeline_bucket_exists,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        test_experiment = aiplatform.Experiment(_TEST_EXPERIMENT)

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        assert get_experiment_mock.call_count == 1

        job.submit(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
            experiment=test_experiment,
        )

        job.wait()

        associated_experiment = job.get_associated_experiment()

        assert associated_experiment.resource_name == _TEST_CONTEXT_NAME

        assert add_context_children_mock.call_count == 1

    @pytest.mark.usefixtures(
        "mock_pipeline_service_get",
        "mock_pipeline_v1beta1_service_batch_delete",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_create_two_and_batch_delete_pipeline_jobs_returns_response(
        self,
        mock_load_yaml_and_json,
        mock_pipeline_v1beta1_service_batch_delete,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = preview_pipeline_jobs._PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        response = job.batch_delete(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            names=[_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_ID_2],
        )

        assert mock_pipeline_v1beta1_service_batch_delete.call_count == 1
        assert len(response.pipeline_jobs) == 2

    @pytest.mark.usefixtures(
        "mock_pipeline_service_get",
        "mock_pipeline_v1_service_batch_delete",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_create_two_and_batch_delete_v1_pipeline_jobs_returns_response(
        self,
        mock_load_yaml_and_json,
        mock_pipeline_v1_service_batch_delete,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        response = job.batch_delete(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            names=[_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_ID_2],
        )

        assert mock_pipeline_v1_service_batch_delete.call_count == 1
        assert len(response.pipeline_jobs) == 2

    @pytest.mark.usefixtures(
        "mock_pipeline_service_get",
        "mock_pipeline_v1_service_batch_cancel",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [
            _TEST_PIPELINE_SPEC_JSON,
            _TEST_PIPELINE_SPEC_YAML,
            _TEST_PIPELINE_JOB,
            _TEST_PIPELINE_SPEC_LEGACY_JSON,
            _TEST_PIPELINE_SPEC_LEGACY_YAML,
            _TEST_PIPELINE_JOB_LEGACY,
        ],
    )
    def test_create_two_and_batch_cancel_v1_pipeline_jobs_returns_response(
        self,
        mock_load_yaml_and_json,
        mock_pipeline_v1_service_batch_cancel,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
        )

        job.batch_cancel(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            names=[_TEST_PIPELINE_JOB_ID, _TEST_PIPELINE_JOB_ID_2],
        )

        assert mock_pipeline_v1_service_batch_cancel.call_count == 1

    @pytest.mark.usefixtures(
        "mock_pipeline_v1beta1_service_create",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_submit_v1beta1_pipeline_job_returns_response(
        self,
        mock_load_yaml_and_json,
        job_spec,
        mock_pipeline_v1beta1_service_create,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
        )

        job = preview_pipeline_jobs._PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            job_id=_TEST_PIPELINE_JOB_ID,
            enable_preflight_validations=True,
        )

        job.submit()

        assert mock_pipeline_v1beta1_service_create.call_count == 1
