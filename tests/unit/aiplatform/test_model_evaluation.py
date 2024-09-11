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

import datetime
import importlib
import pytest
import yaml
import json
from google.protobuf import json_format
from google.protobuf import struct_pb2

from unittest import mock
from urllib import request
from google.api_core import datetime_helpers
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform.metadata import constants

from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform.utils import gcs_utils

from google.cloud.aiplatform.compat.services import (
    model_service_client,
    metadata_service_client_v1 as metadata_service_client,
    job_service_client_v1 as job_service_client,
)
from google.cloud.aiplatform.model_evaluation import model_evaluation_job

from google.cloud.aiplatform_v1.services.pipeline_service import (
    client as pipeline_service_client_v1,
)

from google.cloud.aiplatform.compat.types import model as gca_model

from google.cloud.aiplatform_v1 import Execution as GapicExecution
from google.cloud.aiplatform_v1 import MetadataServiceClient

from google.cloud.aiplatform.compat.types import (
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
    model_evaluation as gca_model_evaluation,
    context as gca_context,
    artifact as gca_artifact,
    batch_prediction_job as gca_batch_prediction_job,
)

import constants as test_constants

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_MODEL_NAME = "test-model"
_TEST_MODEL_ID = test_constants.ModelConstants._TEST_ID
_TEST_EVAL_ID = "1028944691210842622"
_TEST_EXPERIMENT = "test-experiment"
_TEST_BATCH_PREDICTION_JOB_ID = "614161631630327111"
_TEST_COMPONENT_IDENTIFIER = "fpc-model-evaluation"

_TEST_MODEL_RESOURCE_NAME = test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME

_TEST_MODEL_EVAL_RESOURCE_NAME = (
    model_service_client.ModelServiceClient.model_evaluation_path(
        _TEST_PROJECT,
        _TEST_LOCATION,
        _TEST_MODEL_ID,
        _TEST_EVAL_ID,
    )
)

_TEST_BATCH_PREDICTION_RESOURCE_NAME = (
    job_service_client.JobServiceClient.batch_prediction_job_path(
        _TEST_PROJECT, _TEST_LOCATION, _TEST_BATCH_PREDICTION_JOB_ID
    )
)

_TEST_MODEL_EVAL_METRICS = test_constants.ModelConstants._TEST_MODEL_EVAL_METRICS

_TEST_INVALID_MODEL_RESOURCE_NAME = (
    f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_MODEL_ID}"
)

# pipeline job
_TEST_ID = "1028944691210842416"
_TEST_PIPELINE_JOB_DISPLAY_NAME = "sample-pipeline-job-display-name"
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
_TEST_GCS_BUCKET_NAME = "my-bucket"
_TEST_CREDENTIALS = auth_credentials.AnonymousCredentials()
_TEST_SERVICE_ACCOUNT = "abcde@my-project.iam.gserviceaccount.com"
_TEST_PIPELINE_ROOT = f"gs://{_TEST_GCS_BUCKET_NAME}/pipeline_root"
_TEST_PIPELINE_CREATE_TIME = datetime.datetime.now()

_TEST_KFP_TEMPLATE_URI = "https://us-kfp.pkg.dev/vertex-evaluation/pipeline-templates/evaluation-automl-tabular-classification-pipeline/1.0.0"

_TEST_TEMPLATE_REF = {
    "base_uri": "https://us-kfp.pkg.dev/vertex-evaluation/pipeline-templates/evaluation",
    "tag": "20230713_1737",
}
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_ID}"

_TEST_PIPELINE_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"
_TEST_INVALID_PIPELINE_JOB_NAME = (
    f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_PIPELINE_JOB_ID}"
)
_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME = "test-eval-job"
_TEST_EVAL_RESOURCE_DISPLAY_NAME = "my-eval-resource-display-name"

_TEST_MODEL_EVAL_METADATA = {"pipeline_job_resource_name": _TEST_PIPELINE_JOB_NAME}

_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES = {
    "batch_predict_gcs_source_uris": ["gs://my-bucket/my-prediction-data.csv"],
    "dataflow_service_account": _TEST_SERVICE_ACCOUNT,
    "batch_predict_instances_format": "csv",
    "model_name": _TEST_MODEL_RESOURCE_NAME,
    "evaluation_display_name": _TEST_EVAL_RESOURCE_DISPLAY_NAME,
    "project": _TEST_PROJECT,
    "location": _TEST_LOCATION,
    "batch_predict_gcs_destination_output_uri": _TEST_GCS_BUCKET_NAME,
    "target_field_name": "predict_class",
}

_TEST_MODEL_EVAL_PREDICTION_TYPE = "classification"

_TEST_JSON_FORMATTED_MODEL_EVAL_PIPELINE_PARAMETER_VALUES = {
    "batch_predict_gcs_source_uris": '["gs://sdk-model-eval/batch-pred-heart.csv"]',
    "dataflow_service_account": _TEST_SERVICE_ACCOUNT,
    "batch_predict_instances_format": "csv",
    "model_name": _TEST_MODEL_RESOURCE_NAME,
    "project": _TEST_PROJECT,
    "location": _TEST_LOCATION,
    "batch_predict_gcs_destination_output_uri": _TEST_GCS_BUCKET_NAME,
    "target_field_name": "predict_class",
}

_TEST_MODEL_EVAL_PIPELINE_SPEC = {
    "pipelineInfo": {"name": "evaluation-default-pipeline"},
    "root": {
        "dag": {"tasks": {}},
        "inputDefinitions": {
            "parameters": {
                "batch_predict_gcs_source_uris": {"type": "STRING"},
                "dataflow_service_account": _TEST_SERVICE_ACCOUNT,
                "batch_predict_instances_format": {"type": "STRING"},
                "batch_predict_machine_type": {"type": "STRING"},
                "location": {"type": "STRING"},
                "model_name": {"type": "STRING"},
                "project": {"type": "STRING"},
                "batch_predict_gcs_destination_output_uri": {"type": "STRING"},
                "target_field_name": {"type": "STRING"},
            }
        },
    },
    "schemaVersion": "2.0.0",
    "sdkVersion": "kfp-1.8.12",
    "components": {},
}

_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON = json.dumps(
    {
        "pipelineInfo": {"name": "evaluation-default-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {
                "parameters": {
                    "batch_predict_gcs_source_uris": {"type": "STRING"},
                    "dataflow_service_account": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "batch_predict_machine_type": {"type": "STRING"},
                    "evaluation_class_labels": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "project": {"type": "STRING"},
                    "batch_predict_gcs_destination_output_uri": {"type": "STRING"},
                    "target_field_name": {"type": "STRING"},
                }
            },
        },
        "schemaVersion": "2.0.0",
        "sdkVersion": "kfp-1.8.12",
        "components": {},
    }
)

_TEST_MODEL_EVAL_PIPELINE_SPEC_WITH_CACHING_OPTIONS_JSON = json.dumps(
    {
        "pipelineInfo": {"name": "evaluation-default-pipeline"},
        "root": {
            "dag": {
                "tasks": {
                    "model-evaluation-text-generation": {
                        "taskInfo": {"name": "model-evaluation-text-generation"},
                        "cachingOptions": {"enableCache": False},
                    }
                }
            },
            "inputDefinitions": {
                "parameters": {
                    "batch_predict_gcs_source_uris": {"type": "STRING"},
                    "dataflow_service_account": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "batch_predict_machine_type": {"type": "STRING"},
                    "evaluation_class_labels": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "project": {"type": "STRING"},
                    "batch_predict_gcs_destination_output_uri": {"type": "STRING"},
                    "target_field_name": {"type": "STRING"},
                }
            },
        },
        "schemaVersion": "2.0.0",
        "sdkVersion": "kfp-1.8.12",
        "components": {},
    }
)

_TEST_INVALID_MODEL_EVAL_PIPELINE_SPEC = json.dumps(
    {
        "pipelineInfo": {"name": "my-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {
                "parameters": {
                    "batch_predict_gcs_source_uris": {"type": "STRING"},
                    "dataflow_service_account": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "project": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "batch_predict_gcs_destination_output_uri": {"type": "STRING"},
                    "target_field_name": {"type": "STRING"},
                }
            },
        },
        "schemaVersion": "2.0.0",
        "sdkVersion": "kfp-1.8.12",
        "components": {},
    }
)

_TEST_MODEL_EVAL_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {"parameters": _TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES},
        "pipelineInfo": {"name": "evaluation-default-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {
                "parameters": {
                    "batch_predict_gcs_source_uris": {"type": "STRING"},
                    "dataflow_service_account": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "batch_predict_machine_type": {"type": "STRING"},
                    "evaluation_class_labels": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "project": {"type": "STRING"},
                    "batch_predict_gcs_destination_output_uri": {"type": "STRING"},
                    "target_field_name": {"type": "STRING"},
                }
            },
        },
        "schemaVersion": "2.0.0",
        "sdkVersion": "kfp-1.8.12",
        "components": {},
    }
)

_TEST_INVALID_MODEL_EVAL_PIPELINE_JOB = json.dumps(
    {
        "runtimeConfig": {
            "parameterValues": _TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES
        },
        "pipelineInfo": {"name": "my-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {
                "parameters": {
                    "batch_predict_gcs_source_uris": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "project": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "batch_predict_gcs_destination_output_uri": {"type": "STRING"},
                    "target_field_name": {"type": "STRING"},
                }
            },
        },
        "schemaVersion": "2.0.0",
        "sdkVersion": "kfp-1.8.12",
        "components": {"test_component": {}},
    }
)

_EVAL_GCP_RESOURCES_STR = (
    '{\n  "resources": [\n    {\n      "resourceType": "ModelEvaluation",\n      "resourceUri": "https://us-central1-aiplatform.googleapis.com/v1/'
    + _TEST_MODEL_EVAL_RESOURCE_NAME
    + '"\n    }\n  ]\n}'
)

_BP_JOB_GCP_RESOURCES_STR = (
    '{\n  "resources": [\n    {\n      "resourceType": "BatchPredictionJob",\n      "resourceUri": "https://us-central1-aiplatform.googleapis.com/v1/'
    + _TEST_BATCH_PREDICTION_RESOURCE_NAME
    + '"\n    }\n  ]\n}'
)

_TEST_PIPELINE_JOB_DETAIL_EVAL = {
    "output:evaluation_resource_name": _TEST_MODEL_EVAL_RESOURCE_NAME
}

_TEST_PIPELINE_JOB_DETAIL_BP = {
    "output:gcp_resources": _BP_JOB_GCP_RESOURCES_STR,
}

_TEST_EVAL_METRICS_ARTIFACT_NAME = (
    "projects/123/locations/us-central1/metadataStores/default/artifacts/456"
)
_TEST_EVAL_METRICS_ARTIFACT_URI = "gs://test-bucket/eval_pipeline_root/123/evaluation-default-pipeline-20220615135923/model-evaluation-2_-789/evaluation_metrics"

_TEST_EXPERIMENT = "test-experiment"
_TEST_METADATASTORE = f"{_TEST_PARENT}/metadataStores/default"
_TEST_CONTEXT_NAME = f"{_TEST_METADATASTORE}/contexts/{_TEST_EXPERIMENT}"

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

_TEST_MODEL_EVAL_CLASS_LABELS = ["0", "1", "2"]
_TEST_TARGET_FIELD_NAME = "species"


# model eval mocks
@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
        )

        yield get_model_mock


@pytest.fixture
def mock_model():
    model = mock.MagicMock(models.Model)
    model.name = _TEST_MODEL_ID
    model._latest_future = None
    model._exception = None
    model._gca_resource = gca_model.Model(
        display_name="test-eval-model",
        description="This is the mock Model's description",
        name=_TEST_MODEL_NAME,
    )
    yield model


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_pipeline_job:
        mock_create_pipeline_job.return_value = gca_pipeline_job.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )
        yield mock_create_pipeline_job


@pytest.fixture
def mock_model_eval_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model_evaluation"
    ) as mock_get_model_eval:
        mock_get_model_eval.return_value = gca_model_evaluation.ModelEvaluation(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME,
            metrics=_TEST_MODEL_EVAL_METRICS,
            metadata=_TEST_MODEL_EVAL_METADATA,
        )
        yield mock_get_model_eval


_TEST_MODEL_EVAL_LIST = [
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
        create_time=datetime_helpers.DatetimeWithNanoseconds(
            2023, 5, 14, 16, 24, 3, 299558, tzinfo=datetime.timezone.utc
        ),
    ),
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
        create_time=datetime_helpers.DatetimeWithNanoseconds(
            2023, 6, 14, 16, 24, 3, 299558, tzinfo=datetime.timezone.utc
        ),
    ),
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
        create_time=datetime_helpers.DatetimeWithNanoseconds(
            2023, 7, 14, 16, 24, 3, 299558, tzinfo=datetime.timezone.utc
        ),
    ),
]


@pytest.fixture
def list_model_evaluations_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "list_model_evaluations"
    ) as list_model_evaluations_mock:
        list_model_evaluations_mock.return_value = _TEST_MODEL_EVAL_LIST
        yield list_model_evaluations_mock


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


@pytest.fixture
def mock_artifact():
    artifact = mock.MagicMock(aiplatform.Artifact)
    artifact._gca_resource = gca_artifact.Artifact(
        display_name="evaluation_metrics",
        name=_TEST_EVAL_METRICS_ARTIFACT_NAME,
        uri=_TEST_EVAL_METRICS_ARTIFACT_URI,
    )
    yield artifact


@pytest.fixture
def get_artifact_mock():
    with mock.patch.object(
        metadata_service_client.MetadataServiceClient, "get_artifact"
    ) as get_artifact_mock:
        get_artifact_mock.return_value = gca_artifact.Artifact(
            display_name="evaluation_metrics",
            name=_TEST_EVAL_METRICS_ARTIFACT_NAME,
            uri=_TEST_EVAL_METRICS_ARTIFACT_URI,
        )

        yield get_artifact_mock


@pytest.fixture
def get_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_bp_job_mock:
        get_bp_job_mock.return_value = gca_batch_prediction_job.BatchPredictionJob(
            name=_TEST_BATCH_PREDICTION_RESOURCE_NAME,
        )
        yield get_bp_job_mock


def make_pipeline_job(state):
    return gca_pipeline_job.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        job_detail=gca_pipeline_job.PipelineJobDetail(
            pipeline_run_context=gca_context.Context(
                name=_TEST_PIPELINE_JOB_NAME,
            ),
            task_details=[
                gca_pipeline_job.PipelineTaskDetail(
                    task_id=123,
                    task_name=_TEST_PIPELINE_JOB_ID,
                    state=gca_pipeline_job.PipelineTaskDetail.State.SUCCEEDED,
                    execution={
                        "metadata": struct_pb2.Struct(
                            fields={
                                key: struct_pb2.Value(string_value=value)
                                for key, value in _TEST_PIPELINE_JOB_DETAIL_EVAL.items()
                            },
                        ),
                    },
                ),
                gca_pipeline_job.PipelineTaskDetail(
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
def mock_pipeline_service_get():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
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
            make_pipeline_job(
                gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
            ),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_pipeline_service_get_with_fail():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_pipeline_service_get_pending():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
        ]

        yield mock_get_pipeline_job


@pytest.fixture
def mock_load_json(job_spec_json):
    with mock.patch.object(storage.Blob, "download_as_bytes") as mock_load_json:
        mock_load_json.return_value = json.dumps(job_spec_json).encode()
        yield mock_load_json


@pytest.fixture
def mock_load_yaml_and_json(job_spec):
    with mock.patch.object(
        storage.Blob, "download_as_bytes"
    ) as mock_load_yaml_and_json:
        mock_load_yaml_and_json.return_value = job_spec.encode()
        yield mock_load_yaml_and_json


@pytest.fixture
def mock_invalid_model_eval_job_get():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = gca_pipeline_job.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            # pipeline_spec=_TEST_INVALID_MODEL_EVAL_PIPELINE_SPEC,
        )
        yield mock_get_model_eval_job


@pytest.fixture
def mock_model_eval_job_create():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "create_pipeline_job"
    ) as mock_create_model_eval_job:
        mock_create_model_eval_job.return_value = gca_pipeline_job.PipelineJob(
            name=_TEST_PIPELINE_JOB_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            create_time=_TEST_PIPELINE_CREATE_TIME,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            pipeline_spec=_TEST_MODEL_EVAL_PIPELINE_SPEC,
        )
        yield mock_create_model_eval_job


@pytest.fixture
def mock_model_eval_job_get():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_get_model_eval_job


@pytest.fixture
def mock_successfully_completed_eval_job():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_get_model_eval_job


@pytest.fixture
def mock_failed_completed_eval_job():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED
        )
        yield mock_get_model_eval_job


@pytest.fixture
def mock_pending_eval_job():
    with mock.patch.object(
        pipeline_service_client_v1.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING
        )
        yield mock_get_model_eval_job


def make_failed_eval_job():
    model_evaluation_job._ModelEvaluationJob._template_ref = _TEST_TEMPLATE_REF

    eval_job_resource = model_evaluation_job._ModelEvaluationJob(
        evaluation_pipeline_run_name=_TEST_PIPELINE_JOB_NAME
    )
    eval_job_resource.backing_pipeline_job = gca_pipeline_job.PipelineJob(
        name=_TEST_PIPELINE_JOB_NAME,
        state=gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
        create_time=_TEST_PIPELINE_CREATE_TIME,
        service_account=_TEST_SERVICE_ACCOUNT,
        network=_TEST_NETWORK,
        pipeline_spec=_TEST_MODEL_EVAL_PIPELINE_SPEC,
    )
    return eval_job_resource


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
def mock_request_urlopen(job_spec):
    with mock.patch.object(request, "urlopen") as mock_urlopen:
        mock_read_response = mock.MagicMock()
        mock_decode_response = mock.MagicMock()
        mock_decode_response.return_value = job_spec.encode()
        mock_read_response.return_value.decode = mock_decode_response
        mock_urlopen.return_value.read = mock_read_response
        yield mock_urlopen


@pytest.mark.usefixtures("google_auth_mock")
class TestModelEvaluation:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_GCS_BUCKET_NAME,
        )

    def test_init_model_evaluation_with_only_resource_name(self, mock_model_eval_get):
        aiplatform.ModelEvaluation(evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME)

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_model_evaluation_with_eval_id_and_model_id(self, mock_model_eval_get):
        aiplatform.ModelEvaluation(
            evaluation_name=_TEST_EVAL_ID, model_id=_TEST_MODEL_ID
        )

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_model_evaluatin_with_id_project_and_location(
        self, mock_model_eval_get
    ):
        aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_model_evaluation_with_invalid_evaluation_resource_raises(
        self, mock_model_eval_get
    ):
        with pytest.raises(ValueError):
            aiplatform.ModelEvaluation(evaluation_name=_TEST_MODEL_RESOURCE_NAME)

    def test_get_model_evaluation_metrics(self, mock_model_eval_get):
        eval_metrics = aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME
        ).metrics
        assert eval_metrics == _TEST_MODEL_EVAL_METRICS

    def test_no_delete_model_evaluation_method(self, mock_model_eval_get):
        my_eval = aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME
        )

        with pytest.raises(NotImplementedError):
            my_eval.delete()

    def test_list_model_evaluations(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        metrics_list = aiplatform.ModelEvaluation.list(model=_TEST_MODEL_RESOURCE_NAME)

        assert isinstance(metrics_list[0], aiplatform.ModelEvaluation)

    def test_list_model_evaluations_with_order_by(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        metrics_list = aiplatform.ModelEvaluation.list(
            model=_TEST_MODEL_RESOURCE_NAME, order_by="create_time desc"
        )

        assert metrics_list[0].create_time > metrics_list[1].create_time

    def test_get_model_evaluation_pipeline_job(
        self, mock_model_eval_get, mock_pipeline_service_get
    ):
        eval_pipeline_job = aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )._backing_pipeline_job

        assert eval_pipeline_job.resource_name == _TEST_PIPELINE_JOB_NAME

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    def test_get_model_evaluation_bp_job(
        self,
        mock_pipeline_service_create,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        mock_artifact,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        get_artifact_mock,
        get_batch_prediction_job_mock,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            model_type="automl_tabular",
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        test_model_eval_job.wait()

        eval_resource = test_model_eval_job.get_model_evaluation()

        assert isinstance(eval_resource, aiplatform.ModelEvaluation)

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    def test_get_model_evaluation_mlmd_resource(
        self,
        mock_pipeline_service_create,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        mock_artifact,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        get_artifact_mock,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            model_type="automl_tabular",
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        test_model_eval_job.wait()

        eval_resource = test_model_eval_job.get_model_evaluation()

        assert isinstance(eval_resource, aiplatform.ModelEvaluation)


@pytest.mark.usefixtures("google_auth_mock")
class TestModelEvaluationJob:
    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_JOB],
    )
    def test_init_model_evaluation_job(
        self,
        job_spec,
        mock_load_yaml_and_json,
        mock_model_eval_job_get,
        get_execution_mock,
    ):
        model_evaluation_job._ModelEvaluationJob(
            evaluation_pipeline_run_name=_TEST_PIPELINE_JOB_NAME
        )

        mock_model_eval_job_get.assert_called_with(
            name=_TEST_PIPELINE_JOB_NAME, retry=base._DEFAULT_RETRY
        )

        assert mock_model_eval_job_get.call_count == 2

        get_execution_mock.assert_called_once

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_INVALID_MODEL_EVAL_PIPELINE_JOB],
    )
    def test_init_model_evaluation_job_with_non_eval_pipeline_raises(
        self,
        job_spec,
        mock_load_yaml_and_json,
        mock_invalid_model_eval_job_get,
    ):
        """This should fail because we're passing in `mock_invalid_model_eval_job_get`.

        That mock uses a pipeline template that doesn't have the _component_identifier
        defined in the ModelEvaluationJob class.
        """
        with pytest.raises(ValueError):
            model_evaluation_job._ModelEvaluationJob(
                evaluation_pipeline_run_name=_TEST_PIPELINE_JOB_NAME
            )

    def test_init_model_evaluation_job_with_invalid_pipeline_job_name_raises(
        self,
        mock_pipeline_service_get,
    ):
        with pytest.raises(ValueError):
            model_evaluation_job._ModelEvaluationJob(
                evaluation_pipeline_run_name=_TEST_INVALID_PIPELINE_JOB_NAME,
            )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    @pytest.mark.usefixtures("mock_pipeline_service_create")
    def test_model_evaluation_job_submit(
        self,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            model_type="automl_tabular",
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            job_id=_TEST_PIPELINE_JOB_ID,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        test_model_eval_job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameters": {
                "batch_predict_gcs_source_uris": {
                    "stringValue": '["gs://my-bucket/my-prediction-data.csv"]'
                },
                "dataflow_service_account": {"stringValue": _TEST_SERVICE_ACCOUNT},
                "batch_predict_instances_format": {"stringValue": "csv"},
                "model_name": {"stringValue": _TEST_MODEL_RESOURCE_NAME},
                "project": {"stringValue": _TEST_PROJECT},
                "location": {"stringValue": _TEST_LOCATION},
                "batch_predict_gcs_destination_output_uri": {
                    "stringValue": _TEST_GCS_BUCKET_NAME
                },
                "target_field_name": {"stringValue": "predict_class"},
            },
        }

        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.0.0",
                "sdkVersion": "kfp-1.8.12",
            },
            runtime_config=runtime_config,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            template_uri=_TEST_KFP_TEMPLATE_URI,
        )

        mock_model_eval_job_create.assert_called_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        assert mock_model_eval_job_get.called_once

        assert mock_pipeline_service_get.called_once

        assert mock_model_eval_job_get.called_once

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_WITH_CACHING_OPTIONS_JSON],
    )
    @pytest.mark.usefixtures("mock_pipeline_service_create")
    def test_model_evaluation_job_submit_with_caching_disabled(
        self,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            model_type="automl_tabular",
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            job_id=_TEST_PIPELINE_JOB_ID,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            enable_caching=False,
        )

        test_model_eval_job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameters": {
                "batch_predict_gcs_source_uris": {
                    "stringValue": '["gs://my-bucket/my-prediction-data.csv"]'
                },
                "dataflow_service_account": {"stringValue": _TEST_SERVICE_ACCOUNT},
                "batch_predict_instances_format": {"stringValue": "csv"},
                "model_name": {"stringValue": _TEST_MODEL_RESOURCE_NAME},
                "project": {"stringValue": _TEST_PROJECT},
                "location": {"stringValue": _TEST_LOCATION},
                "batch_predict_gcs_destination_output_uri": {
                    "stringValue": _TEST_GCS_BUCKET_NAME
                },
                "target_field_name": {"stringValue": "predict_class"},
            },
        }

        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.0.0",
                "sdkVersion": "kfp-1.8.12",
            },
            runtime_config=runtime_config,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            template_uri=_TEST_KFP_TEMPLATE_URI,
        )

        mock_model_eval_job_create.assert_called_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        assert mock_model_eval_job_get.called_once

        assert mock_pipeline_service_get.called_once

        assert mock_model_eval_job_get.called_once

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    def test_model_evaluation_job_submit_with_experiment(
        self,
        mock_pipeline_service_create,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        get_model_mock,
        get_experiment_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        add_context_children_mock,
        get_metadata_store_mock,
        get_context_mock,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
    ):
        test_experiment = aiplatform.Experiment(_TEST_EXPERIMENT)

        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            model_type="automl_tabular",
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            job_id=_TEST_PIPELINE_JOB_ID,
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            experiment=test_experiment,
        )

        test_model_eval_job.wait()

        expected_runtime_config_dict = {
            "gcsOutputDirectory": _TEST_GCS_BUCKET_NAME,
            "parameters": {
                "batch_predict_gcs_source_uris": {
                    "stringValue": '["gs://my-bucket/my-prediction-data.csv"]'
                },
                "dataflow_service_account": {"stringValue": _TEST_SERVICE_ACCOUNT},
                "batch_predict_instances_format": {"stringValue": "csv"},
                "model_name": {"stringValue": _TEST_MODEL_RESOURCE_NAME},
                "project": {"stringValue": _TEST_PROJECT},
                "location": {"stringValue": _TEST_LOCATION},
                "batch_predict_gcs_destination_output_uri": {
                    "stringValue": _TEST_GCS_BUCKET_NAME
                },
                "target_field_name": {"stringValue": "predict_class"},
            },
        }

        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(expected_runtime_config_dict, runtime_config)

        job_spec = yaml.safe_load(job_spec)
        pipeline_spec = job_spec.get("pipelineSpec") or job_spec

        # Construct expected request
        expected_gapic_pipeline_job = gca_pipeline_job.PipelineJob(
            display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            pipeline_spec={
                "components": {},
                "pipelineInfo": pipeline_spec["pipelineInfo"],
                "root": pipeline_spec["root"],
                "schemaVersion": "2.0.0",
                "sdkVersion": "kfp-1.8.12",
            },
            runtime_config=runtime_config,
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            template_uri=_TEST_KFP_TEMPLATE_URI,
        )

        mock_model_eval_job_create.assert_called_with(
            parent=_TEST_PARENT,
            pipeline_job=expected_gapic_pipeline_job,
            pipeline_job_id=_TEST_PIPELINE_JOB_ID,
            timeout=None,
        )

        get_context_mock.assert_called_with(
            name=_TEST_CONTEXT_NAME,
            retry=base._DEFAULT_RETRY,
        )

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    def test_get_model_evaluation_with_successful_pipeline_run_returns_resource(
        self,
        mock_pipeline_service_create,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            model_type="automl_tabular",
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        test_model_eval_job.wait()

        assert (
            test_model_eval_job.backing_pipeline_job.resource_name
            == _TEST_PIPELINE_JOB_NAME
        )

        assert isinstance(
            test_model_eval_job.backing_pipeline_job, aiplatform.PipelineJob
        )

        test_eval = test_model_eval_job.get_model_evaluation()

        assert isinstance(test_eval, aiplatform.ModelEvaluation)

        assert test_eval.metrics == _TEST_MODEL_EVAL_METRICS

        mock_model_eval_get.assert_called_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

        assert isinstance(test_eval._backing_pipeline_job, aiplatform.PipelineJob)

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    def test_model_evaluation_job_get_model_evaluation_with_failed_pipeline_run_raises(
        self,
        mock_pipeline_service_create,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_failed_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            model_type="automl_tabular",
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        with pytest.raises(RuntimeError):
            test_model_eval_job.get_model_evaluation()

    @pytest.mark.parametrize(
        "job_spec",
        [_TEST_MODEL_EVAL_PIPELINE_SPEC_JSON],
    )
    def test_model_evaluation_job_get_model_evaluation_with_pending_pipeline_run_returns_none(
        self,
        mock_pipeline_service_create,
        job_spec,
        mock_load_yaml_and_json,
        mock_model,
        get_model_mock,
        mock_model_eval_get,
        mock_model_eval_job_get,
        mock_pipeline_service_get,
        mock_model_eval_job_create,
        mock_pending_eval_job,
        mock_pipeline_bucket_exists,
        mock_request_urlopen,
    ):
        test_model_eval_job = model_evaluation_job._ModelEvaluationJob.submit(
            model_name=_TEST_MODEL_RESOURCE_NAME,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
            pipeline_root=_TEST_GCS_BUCKET_NAME,
            target_field_name=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "target_field_name"
            ],
            model_type="automl_tabular",
            evaluation_pipeline_display_name=_TEST_MODEL_EVAL_PIPELINE_JOB_DISPLAY_NAME,
            gcs_source_uris=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_gcs_source_uris"
            ],
            instances_format=_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES[
                "batch_predict_instances_format"
            ],
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
        )

        assert test_model_eval_job.get_model_evaluation() is None

    def test_get_template_url(
        self,
    ):
        template_url = model_evaluation_job._ModelEvaluationJob._get_template_url(
            model_type="automl_tabular",
            feature_attributions=False,
            prediction_type=_TEST_MODEL_EVAL_PREDICTION_TYPE,
        )

        assert template_url == _TEST_KFP_TEMPLATE_URI

        regression_template_url = (
            model_evaluation_job._ModelEvaluationJob._get_template_url(
                model_type="other",
                feature_attributions=True,
                prediction_type="regression",
            )
        )

        assert (
            regression_template_url
            == "https://us-kfp.pkg.dev/vertex-evaluation/pipeline-templates/evaluation-feature-attribution-regression-pipeline/1.0.0"
        )
