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

import yaml
import pytest
import json

from unittest import mock
from importlib import reload
from unittest.mock import patch
from datetime import datetime

from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import pipeline_jobs
from google.cloud import storage
from google.protobuf import json_format

from google.cloud.aiplatform.compat.services import (
    pipeline_service_client,
)
from google.cloud.aiplatform.compat.types import (
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PIPELINE_JOB_DISPLAY_NAME = "sample-pipeline-job-display-name"
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_CREDENTIALS = auth_credentials.AnonymousCredentials()
_TEST_SERVICE_ACCOUNT = "abcde@my-project.iam.gserviceaccount.com"

_TEST_TEMPLATE_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}/job_spec.json"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_ID}"

_TEST_PIPELINE_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"

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
        )
        yield mock_create_pipeline_job


def make_pipeline_job(state):
    return gca_pipeline_job.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
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
        yield mock_list_pipeline_jobs


@pytest.fixture
def mock_load_yaml_and_json(job_spec):
    with patch.object(storage.Blob, "download_as_bytes") as mock_load_yaml_and_json:
        mock_load_yaml_and_json.return_value = job_spec.encode()
        yield mock_load_yaml_and_json


@pytest.mark.usefixtures("google_auth_mock")
class TestPipelineJob:
    class FakePipelineJob(pipeline_jobs.PipelineJob):

        _resource_noun = "fakePipelineJobs"
        _getter_method = _TEST_PIPELINE_GET_METHOD_NAME
        _list_method = _TEST_PIPELINE_LIST_METHOD_NAME
        _cancel_method = _TEST_PIPELINE_CANCEL_METHOD_NAME
        _delete_method = _TEST_PIPELINE_DELETE_METHOD_NAME
        resource_name = _TEST_PIPELINE_RESOURCE_NAME

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
    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        job_spec,
        mock_load_yaml_and_json,
        sync,
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
        job_spec,
        mock_load_yaml_and_json,
        sync,
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
        #     gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
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
        job_spec,
        mock_load_yaml_and_json,
        sync,
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
        job_spec,
        mock_load_yaml_and_json,
        sync,
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
        job_spec,
        mock_load_yaml_and_json,
        sync,
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
    def test_done_method_pipeline_service(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
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
            request={"parent": _TEST_PARENT, "filter": None}
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
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
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
