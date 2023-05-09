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

from datetime import datetime
from importlib import reload
import json
from unittest import mock
from unittest.mock import patch
from urllib import request

from google.auth import credentials as auth_credentials
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.services import (
    schedule_service_client_v1beta1 as schedule_service_client,
)
from google.cloud.aiplatform.compat.types import (
    pipeline_job_v1beta1 as gca_pipeline_job,
    schedule_v1beta1 as gca_schedule,
)
from google.cloud.aiplatform.constants import schedule as schedule_constants
from google.cloud.aiplatform.preview.pipelinejob import pipeline_jobs
from google.cloud.aiplatform.preview.pipelinejobschedule import (
    pipeline_job_schedules,
)
from google.cloud.aiplatform.utils import gcs_utils
import pytest

from google.protobuf import field_mask_pb2 as field_mask
from google.protobuf import json_format

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PIPELINE_JOB_DISPLAY_NAME = "sample-pipeline-job-display-name"
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_GCS_OUTPUT_DIRECTORY = f"gs://{_TEST_GCS_BUCKET_NAME}/output_artifacts/"
_TEST_CREDENTIALS = auth_credentials.AnonymousCredentials()
_TEST_SERVICE_ACCOUNT = "abcde@my-project.iam.gserviceaccount.com"

_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME = "sample-pipeline-job-schedule-display-name"
_TEST_PIPELINE_JOB_SCHEDULE_ID = "sample-test-schedule-20230417"
_TEST_PIPELINE_JOB_SCHEDULE_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/schedules/{_TEST_PIPELINE_JOB_SCHEDULE_ID}"
_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION = "* * * * *"
_TEST_PIPELINE_JOB_SCHEDULE_CRON_TZ_EXPRESSION = "TZ=America/New_York * * * * *"
_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT = 1
_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT = 2

_TEST_PIPELINE_JOB_SCHEDULE_LIST_READ_MASK = field_mask.FieldMask(
    paths=schedule_constants._PIPELINE_JOB_SCHEDULE_READ_MASK_FIELDS
)

_TEST_TEMPLATE_PATH = f"gs://{_TEST_GCS_BUCKET_NAME}/job_spec.json"
_TEST_AR_TEMPLATE_PATH = "https://us-central1-kfp.pkg.dev/proj/repo/pack/latest"
_TEST_HTTPS_TEMPLATE_PATH = "https://raw.githubusercontent.com/repo/pipeline.json"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NETWORK = (
    f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_SCHEDULE_ID}"
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
        "runtimeConfig": {"parameter_values": _TEST_PIPELINE_PARAMETER_VALUES},
        "pipelineSpec": json.loads(_TEST_PIPELINE_SPEC_JSON),
    }
)
_TEST_PIPELINE_JOB_TFX = json.dumps(
    {"runtimeConfig": {}, "pipelineSpec": json.loads(_TEST_TFX_PIPELINE_SPEC_JSON)}
)

_TEST_CREATE_PIPELINE_JOB_REQUEST = {
    "parent": _TEST_PARENT,
    "pipeline_job": {
        "runtime_config": {"parameter_values": _TEST_PIPELINE_PARAMETER_VALUES},
        "pipeline_spec": json.loads(_TEST_PIPELINE_SPEC_JSON),
    },
}


_TEST_SCHEDULE_GET_METHOD_NAME = "get_fake_schedule"
_TEST_SCHEDULE_LIST_METHOD_NAME = "list_fake_schedules"
_TEST_SCHEDULE_CANCEL_METHOD_NAME = "cancel_fake_schedule"
_TEST_SCHEDULE_DELETE_METHOD_NAME = "delete_fake_schedule"

_TEST_PIPELINE_CREATE_TIME = datetime.now()


@pytest.fixture
def mock_schedule_service_create():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "create_schedule"
    ) as mock_create_schedule:
        mock_create_schedule.return_value = gca_schedule.Schedule(
            name=_TEST_PIPELINE_JOB_SCHEDULE_NAME,
            state=gca_schedule.Schedule.State.COMPLETED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request=_TEST_CREATE_PIPELINE_JOB_REQUEST,
        )
        yield mock_create_schedule


@pytest.fixture
def mock_schedule_bucket_exists():
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


def make_schedule(state):
    return gca_schedule.Schedule(
        name=_TEST_PIPELINE_JOB_SCHEDULE_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
        max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
        max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
        create_pipeline_job_request=_TEST_CREATE_PIPELINE_JOB_REQUEST,
    )


@pytest.fixture
def mock_schedule_service_get():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "get_schedule"
    ) as mock_get_schedule:
        mock_get_schedule.side_effect = [
            make_schedule(gca_schedule.Schedule.State.ACTIVE),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
        ]

        yield mock_get_schedule


@pytest.fixture
def mock_schedule_service_get_with_fail():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "get_schedule"
    ) as mock_get_schedule:
        mock_get_schedule.side_effect = [
            make_schedule(gca_schedule.Schedule.State.ACTIVE),
            make_schedule(gca_schedule.Schedule.State.ACTIVE),
            make_schedule(gca_schedule.Schedule.State.STATE_UNSPECIFIED),
        ]

        yield mock_get_schedule


@pytest.fixture
def mock_schedule_service_pause():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "pause_schedule"
    ) as mock_pause_schedule:
        yield mock_pause_schedule


@pytest.fixture
def mock_schedule_service_resume():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "resume_schedule"
    ) as mock_resume_schedule:
        yield mock_resume_schedule


@pytest.fixture
def mock_schedule_service_list():
    with mock.patch.object(
        schedule_service_client.ScheduleServiceClient, "list_schedules"
    ) as mock_list_schedules:
        mock_list_schedules.return_value = [
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
            make_schedule(gca_schedule.Schedule.State.COMPLETED),
        ]
        yield mock_list_schedules


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


@pytest.mark.usefixtures("google_auth_mock")
class TestPipelineJobSchedule:
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
    def test_call_schedule_service_create(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
        mock_schedule_bucket_exists,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            pipeline_job_schedule.wait()

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
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=None,
        )

        assert pipeline_job_schedule._gca_resource == make_schedule(
            gca_schedule.Schedule.State.COMPLETED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_call_schedule_service_create_with_different_timezone(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
        mock_schedule_bucket_exists,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_TZ_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            pipeline_job_schedule.wait()

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
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_TZ_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=None,
        )

        assert pipeline_job_schedule._gca_resource == make_schedule(
            gca_schedule.Schedule.State.COMPLETED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_call_schedule_service_create_artifact_registry(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
        mock_schedule_bucket_exists,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            pipeline_job_schedule.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=None,
        )

        assert pipeline_job_schedule._gca_resource == make_schedule(
            gca_schedule.Schedule.State.COMPLETED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_call_schedule_service_create_https(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
        mock_schedule_bucket_exists,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            pipeline_job_schedule.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=None,
        )

        assert pipeline_job_schedule._gca_resource == make_schedule(
            gca_schedule.Schedule.State.COMPLETED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_call_schedule_service_create_with_timeout(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
        mock_schedule_bucket_exists,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            pipeline_job_schedule.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=180.0,
        )

        assert pipeline_job_schedule._gca_resource == make_schedule(
            gca_schedule.Schedule.State.COMPLETED
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_call_schedule_service_create_with_timeout_not_explicitly_set(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
        mock_schedule_bucket_exists,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            sync=sync,
        )

        if not sync:
            pipeline_job_schedule.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=None,
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_call_pipeline_job_create_schedule(
        self,
        mock_schedule_service_create,
        mock_schedule_service_get,
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        pipeline_job_schedule = job.create_schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        if not sync:
            pipeline_job_schedule.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameterValues": _TEST_PIPELINE_PARAMETER_VALUES,
            "inputArtifacts": {"vertex_model": {"artifactId": "456"}},
        }
        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec
        expected_gapic_pipeline_job_schedule = gca_schedule.Schedule(
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
            cron=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            create_pipeline_job_request={
                "parent": _TEST_PARENT,
                "pipeline_job": {
                    "runtime_config": runtime_config,
                    "pipeline_spec": {"fields": pipeline_spec},
                    "service_account": _TEST_SERVICE_ACCOUNT,
                    "network": _TEST_NETWORK,
                },
            },
        )

        mock_schedule_service_create.assert_called_once_with(
            parent=_TEST_PARENT,
            schedule=expected_gapic_pipeline_job_schedule,
            timeout=None,
        )

        assert pipeline_job_schedule._gca_resource == make_schedule(
            gca_schedule.Schedule.State.COMPLETED
        )

    @pytest.mark.usefixtures("mock_schedule_service_get")
    def test_get_schedule(self, mock_schedule_service_get):
        aiplatform.init(project=_TEST_PROJECT)
        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule.get(
            resource_name=_TEST_PIPELINE_JOB_SCHEDULE_ID
        )

        mock_schedule_service_get.assert_called_once_with(
            name=_TEST_PIPELINE_JOB_SCHEDULE_NAME, retry=base._DEFAULT_RETRY
        )
        assert isinstance(
            pipeline_job_schedule, pipeline_job_schedules.PipelineJobSchedule
        )

    @pytest.mark.usefixtures(
        "mock_schedule_service_create",
        "mock_schedule_service_get",
        "mock_schedule_bucket_exists",
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
    def test_pause_resume_schedule_service(
        self,
        mock_schedule_service_pause,
        mock_schedule_service_resume,
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
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
        )

        pipeline_job_schedule.pause()

        mock_schedule_service_pause.assert_called_once_with(
            name=_TEST_PIPELINE_JOB_SCHEDULE_NAME
        )

        pipeline_job_schedule.resume()

        mock_schedule_service_resume.assert_called_once_with(
            name=_TEST_PIPELINE_JOB_SCHEDULE_NAME
        )

    @pytest.mark.usefixtures(
        "mock_schedule_service_create",
        "mock_schedule_service_get",
        "mock_schedule_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_list_schedules(self, mock_schedule_service_list, mock_load_yaml_and_json):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

        job = pipeline_jobs.PipelineJob(
            display_name=_TEST_PIPELINE_JOB_DISPLAY_NAME,
            template_path=_TEST_TEMPLATE_PATH,
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        pipeline_job_schedule.list()

        mock_schedule_service_list.assert_called_once_with(
            request={"parent": _TEST_PARENT}
        )

    @pytest.mark.usefixtures(
        "mock_schedule_service_create",
        "mock_schedule_service_get",
        "mock_schedule_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_list_schedules_with_read_mask(
        self, mock_schedule_service_list, mock_load_yaml_and_json
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        pipeline_job_schedule.list(enable_simple_view=True)

        mock_schedule_service_list.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "read_mask": _TEST_PIPELINE_JOB_SCHEDULE_LIST_READ_MASK,
            },
        )

    @pytest.mark.usefixtures(
        "mock_schedule_service_create",
        "mock_schedule_service_get",
        "mock_schedule_bucket_exists",
    )
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_PIPELINE_SPEC_JSON, _TEST_PIPELINE_SPEC_YAML, _TEST_PIPELINE_JOB],
    )
    def test_list_schedule_jobs(
        self, mock_schedule_service_list, mock_load_yaml_and_json
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
            parameter_values=_TEST_PIPELINE_PARAMETER_VALUES,
            input_artifacts=_TEST_PIPELINE_INPUT_ARTIFACTS,
            enable_caching=True,
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        pipeline_job_schedule.create(
            cron_expression=_TEST_PIPELINE_JOB_SCHEDULE_CRON_EXPRESSION,
            max_concurrent_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_CONCURRENT_RUN_COUNT,
            max_run_count=_TEST_PIPELINE_JOB_SCHEDULE_MAX_RUN_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            create_request_timeout=None,
        )

        pipeline_job_schedule.list_jobs()

        mock_schedule_service_list.assert_called_once_with(
            request={
                "parent": _TEST_PARENT,
                "filter": f"schedule_id={_TEST_PIPELINE_JOB_SCHEDULE_ID}",
            },
        )

    @pytest.mark.usefixtures(
        "mock_schedule_service_create",
        "mock_schedule_service_get",
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
    def test_pause_pipeline_job_schedule_without_created(
        self,
        mock_schedule_service_pause,
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
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job,
            display_name=_TEST_PIPELINE_JOB_SCHEDULE_DISPLAY_NAME,
        )

        with pytest.raises(RuntimeError) as e:
            pipeline_job_schedule.pause()

        assert e.match(regexp=r"Schedule resource has not been created")
