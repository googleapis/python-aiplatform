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

import importlib
from concurrent import futures
import json
import pathlib
import pytest
import requests
from datetime import datetime
from unittest import mock
from unittest.mock import patch
from urllib import request

from google.api_core import operation as ga_operation
from google.api_core import exceptions as api_exceptions
from google.auth import credentials as auth_credentials
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base, explain
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import gcs_utils
from google.cloud.aiplatform.metadata import constants as metadata_constants
from google.cloud.aiplatform import constants

from google.cloud.aiplatform.preview import models as preview_models

from google.cloud.aiplatform.compat.services import (
    deployment_resource_pool_service_client,
    deployment_resource_pool_service_client_v1beta1,
    endpoint_service_client,
    endpoint_service_client_v1beta1,
    model_service_client,
    job_service_client,
    pipeline_service_client,
)

from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_batch_prediction_job,
    deployment_resource_pool as gca_deployment_resource_pool,
    deployment_resource_pool_v1beta1 as gca_deployment_resource_pool_v1beta1,
    encryption_spec as gca_encryption_spec,
    endpoint as gca_endpoint,
    endpoint_service as gca_endpoint_service,
    endpoint_v1beta1 as gca_endpoint_v1beta1,
    endpoint_service_v1beta1 as gca_endpoint_service_v1beta1,
    env_var as gca_env_var,
    explanation as gca_explanation,
    io as gca_io,
    job_state as gca_job_state,
    machine_resources as gca_machine_resources,
    machine_resources_v1beta1 as gca_machine_resources_v1beta1,
    reservation_affinity_v1 as gca_reservation_affinity_v1,
    manual_batch_tuning_parameters as gca_manual_batch_tuning_parameters_compat,
    model as gca_model,
    model_evaluation as gca_model_evaluation,
    model_service as gca_model_service,
    pipeline_job as gca_pipeline_job,
    pipeline_state as gca_pipeline_state,
    context as gca_context,
)

from google.cloud.aiplatform.prediction import LocalModel
from google.cloud.aiplatform_v1 import Execution as GapicExecution
from google.cloud.aiplatform.model_evaluation import model_evaluation_job

from google.protobuf import (
    field_mask_pb2,
    struct_pb2,
    timestamp_pb2,
    duration_pb2,
)

import constants as test_constants

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_LOCATION_2 = "europe-west4"
_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT
_TEST_MODEL_NAME = test_constants.ModelConstants._TEST_MODEL_NAME
_TEST_MODEL_NAME_ALT = "456"
_TEST_MODEL_ID = "my-model"
_TEST_MODEL_PARENT = test_constants.ModelConstants._TEST_MODEL_PARENT
_TEST_MODEL_PARENT_ALT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_MODEL_NAME_ALT}"
)
_TEST_ARTIFACT_URI = "gs://test/artifact/uri"
_TEST_SERVING_CONTAINER_IMAGE = (
    test_constants.ModelConstants._TEST_SERVING_CONTAINER_IMAGE
)
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = "metadata"
_TEST_DESCRIPTION = "test description"
_TEST_SERVING_CONTAINER_COMMAND = ["python3", "run_my_model.py"]
_TEST_SERVING_CONTAINER_ARGS = ["--test", "arg"]
_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES = {
    "learning_rate": 0.01,
    "loss_fn": "mse",
}
_TEST_SERVING_CONTAINER_PORTS = [8888, 10000]
_TEST_SERVING_CONTAINER_GRPC_PORTS = [7777, 7000]
_TEST_SERVING_CONTAINER_DEPLOYMENT_TIMEOUT = 100
_TEST_SERVING_CONTAINER_SHARED_MEMORY_SIZE_MB = 1000
_TEST_SERVING_CONTAINER_STARTUP_PROBE_EXEC = ["a", "b"]
_TEST_SERVING_CONTAINER_STARTUP_PROBE_PERIOD_SECONDS = 5
_TEST_SERVING_CONTAINER_STARTUP_PROBE_TIMEOUT_SECONDS = 100
_TEST_SERVING_CONTAINER_HEALTH_PROBE_EXEC = ["c", "d"]
_TEST_SERVING_CONTAINER_HEALTH_PROBE_PERIOD_SECONDS = 20
_TEST_SERVING_CONTAINER_HEALTH_PROBE_TIMEOUT_SECONDS = 200
_TEST_ID = "1028944691210842416"
_TEST_LABEL = test_constants.ProjectConstants._TEST_LABELS
_TEST_APPENDED_USER_AGENT = ["fake_user_agent", "another_fake_user_agent"]

_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2
_TEST_STARTING_REPLICA_COUNT = 2
_TEST_MAX_REPLICA_COUNT = 12

_TEST_SPOT = True
_TEST_RESERVATION_AFFINITY_TYPE = "SPECIFIC_RESERVATION"
_TEST_RESERVATION_AFFINITY_KEY = "compute.googleapis.com/reservation-name"
_TEST_RESERVATION_AFFINITY_VALUES = [
    "projects/fake-project-id/zones/fake-zone/reservations/fake-reservation-name"
]

_TEST_TPU_MACHINE_TYPE = "ct5lp-hightpu-4t"
_TEST_TPU_TOPOLOGY = "2x2"

_TEST_BATCH_SIZE = 16

_TEST_PIPELINE_RESOURCE_NAME = (
    "projects/my-project/locations/us-central1/trainingPipeline/12345"
)

_TEST_BATCH_PREDICTION_GCS_SOURCE = "gs://example-bucket/folder/instance.jsonl"
_TEST_BATCH_PREDICTION_GCS_SOURCE_LIST = [
    "gs://example-bucket/folder/instance1.jsonl",
    "gs://example-bucket/folder/instance2.jsonl",
]
_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX = "gs://example-bucket/folder/output"
_TEST_BATCH_PREDICTION_BQ_PREFIX = "ucaip-sample-tests"
_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL = (
    f"bq://{_TEST_BATCH_PREDICTION_BQ_PREFIX}"
)
_TEST_BATCH_PREDICTION_DISPLAY_NAME = "test-batch-prediction-job"
_TEST_BATCH_PREDICTION_JOB_NAME = (
    job_service_client.JobServiceClient.batch_prediction_job_path(
        project=_TEST_PROJECT, location=_TEST_LOCATION, batch_prediction_job=_TEST_ID
    )
)

_TEST_INSTANCE_SCHEMA_URI = "gs://test/schema/instance.yaml"
_TEST_PARAMETERS_SCHEMA_URI = "gs://test/schema/parameters.yaml"
_TEST_PREDICTION_SCHEMA_URI = "gs://test/schema/predictions.yaml"

_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"


_TEST_EXPLANATION_METADATA = explain.ExplanationMetadata(
    inputs={
        "features": {
            "input_tensor_name": "dense_input",
            "encoding": "BAG_OF_FEATURES",
            "modality": "numeric",
            "index_feature_mapping": ["abc", "def", "ghj"],
        }
    },
    outputs={"medv": {"output_tensor_name": "dense_2"}},
)
_TEST_EXPLANATION_PARAMETERS = (
    test_constants.ModelConstants._TEST_EXPLANATION_PARAMETERS
)
_TEST_EXPLANATION_METADATA_EXAMPLES = explain.ExplanationMetadata(
    outputs={"embedding": {"output_tensor_name": "embedding"}},
    inputs={
        "my_input": {
            "input_tensor_name": "bytes_inputs",
            "encoding": "IDENTITY",
            "modality": "image",
        },
        "id": {"input_tensor_name": "id", "encoding": "IDENTITY"},
    },
)
_TEST_EXPLANATION_PARAMETERS_EXAMPLES_PRESETS = explain.ExplanationParameters(
    {
        "examples": {
            "example_gcs_source": {
                "gcs_source": {
                    "uris": ["gs://example-bucket/folder/instance1.jsonl"],
                },
            },
            "neighbor_count": 10,
            "presets": {"query": "FAST", "modality": "TEXT"},
        }
    }
)
_TEST_EXPLANATION_PARAMETERS_EXAMPLES_FULL_CONFIG = explain.ExplanationParameters(
    {
        "examples": {
            "example_gcs_source": {
                "gcs_source": {
                    "uris": ["gs://example-bucket/folder/instance1.jsonl"],
                },
            },
            "neighbor_count": 10,
            "nearest_neighbor_search_config": [
                {
                    "contentsDeltaUri": "",
                    "config": {
                        "dimensions": 50,
                        "approximateNeighborsCount": 10,
                        "distanceMeasureType": "SQUARED_L2_DISTANCE",
                        "featureNormType": "NONE",
                        "algorithmConfig": {
                            "treeAhConfig": {
                                "leafNodeEmbeddingCount": 1000,
                                "leafNodesToSearchPercent": 100,
                            }
                        },
                    },
                }
            ],
        }
    }
)

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

_TEST_MODEL_RESOURCE_NAME = test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT = (
    model_service_client.ModelServiceClient.model_path(
        _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
    )
)
_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION = (
    model_service_client.ModelServiceClient.model_path(
        _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
    )
)

_TEST_OUTPUT_DIR = "gs://my-output-bucket"
_TEST_CONTAINER_REGISTRY_DESTINATION = (
    "us-central1-docker.pkg.dev/projectId/repoName/imageName"
)

_TEST_EXPORT_FORMAT_ID_IMAGE = "custom-trained"
_TEST_EXPORT_FORMAT_ID_ARTIFACT = "tf-saved-model"

_TEST_SUPPORTED_EXPORT_FORMATS_IMAGE = [
    gca_model.Model.ExportFormat(
        id=_TEST_EXPORT_FORMAT_ID_IMAGE,
        exportable_contents=[gca_model.Model.ExportFormat.ExportableContent.IMAGE],
    )
]

_TEST_SUPPORTED_EXPORT_FORMATS_ARTIFACT = [
    gca_model.Model.ExportFormat(
        id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
        exportable_contents=[gca_model.Model.ExportFormat.ExportableContent.ARTIFACT],
    )
]

_TEST_SUPPORTED_EXPORT_FORMATS_BOTH = [
    gca_model.Model.ExportFormat(
        id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
        exportable_contents=[
            gca_model.Model.ExportFormat.ExportableContent.ARTIFACT,
            gca_model.Model.ExportFormat.ExportableContent.IMAGE,
        ],
    )
]

_TEST_SUPPORTED_EXPORT_FORMATS_UNSUPPORTED = []

# Model Evaluation
_TEST_MODEL_EVAL_RESOURCE_NAME = f"{_TEST_MODEL_RESOURCE_NAME}/evaluations/{_TEST_ID}"
_TEST_MODEL_EVAL_METRICS = test_constants.ModelConstants._TEST_MODEL_EVAL_METRICS

_TEST_MODEL_EVAL_LIST = [
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
    ),
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
    ),
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
    ),
]

# model.evaluate
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"
_TEST_PIPELINE_JOB_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/pipelineJobs/{_TEST_PIPELINE_JOB_ID}"
_TEST_PIPELINE_CREATE_TIME = datetime.now()
_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_PIPELINE_JOB_ID}"
_TEST_MODEL_EVAL_CLASS_LABELS = ["dog", "cat", "rabbit"]
_TEST_BIGQUERY_EVAL_INPUT_URI = "bq://my-project.my-dataset.my-table"
_TEST_BIGQUERY_EVAL_DESTINATION_URI = "bq://my-project.my-dataset"
_TEST_EVAL_RESOURCE_DISPLAY_NAME = "my-eval-resource-display-name"
_TEST_GCS_BUCKET_NAME = "my-bucket"

_TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES = {
    "batch_predict_gcs_source_uris": ["gs://my-bucket/my-prediction-data.csv"],
    "dataflow_service_account": _TEST_SERVICE_ACCOUNT,
    "batch_predict_instances_format": "csv",
    "model_name": _TEST_MODEL_RESOURCE_NAME,
    "evaluation_display_name": _TEST_EVAL_RESOURCE_DISPLAY_NAME,
    "prediction_type": "classification",
    "project": _TEST_PROJECT,
    "location": _TEST_LOCATION,
    "batch_predict_gcs_destination_output_uri": _TEST_GCS_BUCKET_NAME,
    "target_field_name": "predict_class",
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
                    "location": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "prediction_type": {"type": "STRING"},
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
                    "evaluation_class_labels": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "batch_predict_machine_type": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "prediction_type": {"type": "STRING"},
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

_TEST_MODEL_EVAL_PIPELINE_JOB_WITH_BQ_INPUT = json.dumps(
    {
        "runtimeConfig": {"parameters": _TEST_MODEL_EVAL_PIPELINE_PARAMETER_VALUES},
        "pipelineInfo": {"name": "evaluation-default-pipeline"},
        "root": {
            "dag": {"tasks": {}},
            "inputDefinitions": {
                "parameters": {
                    "batch_predict_gcs_source_uris": {"type": "STRING"},
                    "dataflow_service_account": {"type": "STRING"},
                    "evaluation_class_labels": {"type": "STRING"},
                    "batch_predict_instances_format": {"type": "STRING"},
                    "batch_predict_predictions_format": {"type": "STRING"},
                    "batch_predict_bigquery_source_uri": {"type": "STRING"},
                    "batch_predict_bigquery_destination_output_uri": {"type": "STRING"},
                    "batch_predict_machine_type": {"type": "STRING"},
                    "location": {"type": "STRING"},
                    "model_name": {"type": "STRING"},
                    "prediction_type": {"type": "STRING"},
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

_TEST_LOCAL_MODEL = LocalModel(
    serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
    serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
    serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
)

_TEST_VERSION_ID = test_constants.ModelConstants._TEST_VERSION_ID
_TEST_VERSION_ALIAS_1 = test_constants.ModelConstants._TEST_VERSION_ALIAS_1
_TEST_VERSION_ALIAS_2 = test_constants.ModelConstants._TEST_VERSION_ALIAS_2
_TEST_MODEL_VERSION_DESCRIPTION_1 = "My version 1 description"
_TEST_MODEL_VERSION_DESCRIPTION_2 = (
    test_constants.ModelConstants._TEST_MODEL_VERSION_DESCRIPTION_2
)
_TEST_MODEL_VERSION_DESCRIPTION_3 = "My version 3 description"

_TEST_MODEL_VERSIONS_LIST = [
    gca_model.Model(
        version_id="1",
        create_time=timestamp_pb2.Timestamp(),
        update_time=timestamp_pb2.Timestamp(),
        display_name=_TEST_MODEL_NAME,
        name=f"{_TEST_MODEL_PARENT}@1",
        version_aliases=["default"],
        version_description=_TEST_MODEL_VERSION_DESCRIPTION_1,
    ),
    gca_model.Model(
        version_id="2",
        create_time=timestamp_pb2.Timestamp(),
        update_time=timestamp_pb2.Timestamp(),
        display_name=_TEST_MODEL_NAME,
        name=f"{_TEST_MODEL_PARENT}@2",
        version_aliases=[_TEST_VERSION_ALIAS_1, _TEST_VERSION_ALIAS_2],
        version_description=_TEST_MODEL_VERSION_DESCRIPTION_2,
    ),
    gca_model.Model(
        version_id="3",
        create_time=timestamp_pb2.Timestamp(),
        update_time=timestamp_pb2.Timestamp(),
        display_name=_TEST_MODEL_NAME,
        name=f"{_TEST_MODEL_PARENT}@3",
        version_aliases=[],
        version_description=_TEST_MODEL_VERSION_DESCRIPTION_3,
        labels=_TEST_LABEL,
    ),
]
_TEST_MODEL_VERSIONS_WITH_FILTER_LIST = [_TEST_MODEL_VERSIONS_LIST[2]]

_TEST_MODELS_LIST = _TEST_MODEL_VERSIONS_LIST + [
    gca_model.Model(
        version_id="1",
        create_time=timestamp_pb2.Timestamp(),
        update_time=timestamp_pb2.Timestamp(),
        display_name=_TEST_MODEL_NAME_ALT,
        name=_TEST_MODEL_PARENT_ALT,
        version_aliases=["default"],
        version_description=_TEST_MODEL_VERSION_DESCRIPTION_1,
    ),
]

_TEST_MODEL_OBJ_WITH_VERSION = (
    test_constants.ModelConstants._TEST_MODEL_OBJ_WITH_VERSION
)

_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_ID}"

_TEST_RAW_PREDICT_URL = f"https://{_TEST_LOCATION}-{constants.base.API_BASE_PATH}/v1/projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}:rawPredict"
_TEST_RAW_PREDICT_DATA = b""
_TEST_RAW_PREDICT_HEADER = {"Content-Type": "application/json"}

_TEST_DRP_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/deploymentResourcePools/{_TEST_ID}"

_TEST_METRIC_NAME_CPU_UTILIZATION = (
    "aiplatform.googleapis.com/prediction/online/cpu/utilization"
)
_TEST_METRIC_NAME_GPU_UTILIZATION = (
    "aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle"
)


@pytest.fixture
def mock_model():
    model = mock.MagicMock(models.Model)
    model.name = _TEST_ID
    model._latest_future = None
    model._exception = None
    model._gca_resource = gca_model.Model(
        display_name=_TEST_MODEL_NAME, description=_TEST_DESCRIPTION, labels=_TEST_LABEL
    )
    yield model


@pytest.fixture
def update_model_mock(mock_model):
    with patch.object(model_service_client.ModelServiceClient, "update_model") as mock:
        mock.return_value = mock_model
        yield mock


@pytest.fixture
def authorized_session_mock():
    with patch(
        "google.auth.transport.requests.AuthorizedSession"
    ) as MockAuthorizedSession:
        mock_auth_session = MockAuthorizedSession(_TEST_CREDENTIALS)
        yield mock_auth_session


@pytest.fixture
def raw_predict_mock(authorized_session_mock):
    with patch.object(authorized_session_mock, "post") as mock_post:
        mock_post.return_value = requests.models.Response()
        yield mock_post


@pytest.fixture
def get_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        test_endpoint_resource_name = (
            endpoint_service_client.EndpointServiceClient.endpoint_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
        )
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_MODEL_NAME,
            name=test_endpoint_resource_name,
        )
        yield get_endpoint_mock


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
def get_model_with_custom_location_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_custom_project_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT,
            artifact_uri=_TEST_ARTIFACT_URI,
            description=_TEST_DESCRIPTION,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_training_job():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT,
            training_pipeline=_TEST_PIPELINE_RESOURCE_NAME,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_supported_export_formats_image():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_IMAGE,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_supported_export_formats_artifact():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_ARTIFACT,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_supported_export_formats_artifact_and_version():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_ARTIFACT,
            version_id=_TEST_VERSION_ID,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_both_supported_export_formats():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_BOTH,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_unsupported_export_formats():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_UNSUPPORTED,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_version():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = _TEST_MODEL_OBJ_WITH_VERSION
        yield get_model_mock


@pytest.fixture
def upload_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def upload_model_with_version_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME, model_version_id=_TEST_VERSION_ID
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def upload_model_with_custom_project_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def upload_model_with_custom_location_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def export_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "export_model"
    ) as export_model_mock:
        export_model_lro_mock = mock.Mock(ga_operation.Operation)
        export_model_lro_mock.metadata = gca_model_service.ExportModelOperationMetadata(
            output_info=gca_model_service.ExportModelOperationMetadata.OutputInfo(
                artifact_output_uri=_TEST_OUTPUT_DIR
            )
        )
        export_model_lro_mock.result.return_value = None
        export_model_mock.return_value = export_model_lro_mock
        yield export_model_mock


@pytest.fixture
def delete_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "delete_model"
    ) as delete_model_mock:
        delete_model_lro_mock = mock.Mock(ga_operation.Operation)
        delete_model_lro_mock.result.return_value = (
            gca_model_service.DeleteModelRequest()
        )
        delete_model_mock.return_value = delete_model_lro_mock
        yield delete_model_mock


@pytest.fixture
def copy_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "copy_model"
    ) as copy_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.CopyModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION
        )
        copy_model_mock.return_value = mock_lro
        yield copy_model_mock


@pytest.fixture
def deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = gca_endpoint.DeployedModel(
            model=_TEST_MODEL_RESOURCE_NAME,
            display_name=_TEST_MODEL_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = (
            gca_endpoint_service.DeployModelResponse(
                deployed_model=deployed_model,
            )
        )
        deploy_model_mock.return_value = deploy_model_lro_mock
        yield deploy_model_mock


@pytest.fixture
def get_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        batch_prediction_mock = mock.Mock(
            spec=gca_batch_prediction_job.BatchPredictionJob
        )
        batch_prediction_mock.state = gca_job_state.JobState.JOB_STATE_SUCCEEDED
        batch_prediction_mock.name = _TEST_BATCH_PREDICTION_JOB_NAME
        get_batch_prediction_job_mock.return_value = batch_prediction_mock
        yield get_batch_prediction_job_mock


@pytest.fixture
def create_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_batch_prediction_job"
    ) as create_batch_prediction_job_mock:
        batch_prediction_job_mock = mock.Mock(
            spec=gca_batch_prediction_job.BatchPredictionJob
        )
        batch_prediction_job_mock.name = _TEST_BATCH_PREDICTION_JOB_NAME
        create_batch_prediction_job_mock.return_value = batch_prediction_job_mock
        yield create_batch_prediction_job_mock


@pytest.fixture
def get_training_job_non_existent_mock():
    with patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as get_training_job_non_existent_mock:
        get_training_job_non_existent_mock.side_effect = api_exceptions.NotFound("404")

        yield get_training_job_non_existent_mock


@pytest.fixture
def create_client_mock():
    with mock.patch.object(
        initializer.global_config, "create_client"
    ) as create_client_mock:
        api_client_mock = mock.Mock(spec=model_service_client.ModelServiceClient)
        api_client_mock.get_model.return_value = _TEST_MODEL_OBJ_WITH_VERSION
        create_client_mock.return_value = api_client_mock
        yield create_client_mock


@pytest.fixture
def mock_storage_blob_upload_from_filename():
    with patch(
        "google.cloud.storage.Blob.upload_from_filename"
    ) as mock_blob_upload_from_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_upload_from_filename


# ModelEvaluation mocks
@pytest.fixture
def mock_model_eval_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model_evaluation"
    ) as mock_get_model_eval:
        mock_get_model_eval.return_value = gca_model_evaluation.ModelEvaluation(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME,
            metrics=_TEST_MODEL_EVAL_METRICS,
            metadata={"pipeline_job_resource_name": _TEST_PIPELINE_JOB_NAME},
        )
        yield mock_get_model_eval


@pytest.fixture
def mock_get_model_evaluation():
    with mock.patch.object(
        aiplatform.model_evaluation._ModelEvaluationJob, "get_model_evaluation"
    ) as mock_get_model_eval:
        mock_get_model_eval.return_value = aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME
        )
        yield mock_get_model_eval


@pytest.fixture
def list_model_evaluations_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "list_model_evaluations"
    ) as list_model_evaluations_mock:
        list_model_evaluations_mock.return_value = _TEST_MODEL_EVAL_LIST
        yield list_model_evaluations_mock


@pytest.fixture
def list_model_versions_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "list_model_versions"
    ) as list_model_versions_mock:
        list_model_versions_mock.return_value = _TEST_MODEL_VERSIONS_LIST
        yield list_model_versions_mock


@pytest.fixture
def list_model_versions_with_filter_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "list_model_versions"
    ) as list_model_versions_mock:
        list_model_versions_mock.return_value = _TEST_MODEL_VERSIONS_WITH_FILTER_LIST
        yield list_model_versions_mock


@pytest.fixture
def list_models_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "list_models"
    ) as list_models_mock:
        list_models_mock.return_value = _TEST_MODELS_LIST
        yield list_models_mock


@pytest.fixture
def delete_model_version_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "delete_model_version"
    ) as delete_model_version_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        delete_model_version_mock.return_value = mock_lro
        yield delete_model_version_mock


@pytest.fixture
def merge_version_aliases_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "merge_version_aliases"
    ) as merge_version_aliases_mock:
        merge_version_aliases_mock.return_value = _TEST_MODEL_OBJ_WITH_VERSION
        yield merge_version_aliases_mock


# model.evaluate fixtures
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


_TEST_COMPONENT_IDENTIFIER = "fpc-model-evaluation"
_TEST_BATCH_PREDICTION_JOB_ID = "614161631630327111"

_TEST_BATCH_PREDICTION_RESOURCE_NAME = (
    job_service_client.JobServiceClient.batch_prediction_job_path(
        _TEST_PROJECT, _TEST_LOCATION, _TEST_BATCH_PREDICTION_JOB_ID
    )
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
    "output:gcp_resources": _EVAL_GCP_RESOURCES_STR,
    "component_type": _TEST_COMPONENT_IDENTIFIER,
}

_TEST_PIPELINE_JOB_DETAIL_BP = {
    "output:gcp_resources": _BP_JOB_GCP_RESOURCES_STR,
}

_TEST_EVAL_METRICS_ARTIFACT_NAME = (
    "projects/123/locations/us-central1/metadataStores/default/artifacts/456"
)
_TEST_EVAL_METRICS_ARTIFACT_URI = "gs://test-bucket/eval_pipeline_root/123/evaluation-default-pipeline-20220615135923/model-evaluation-2_-789/evaluation_metrics"


# executions: this is used in test_list_pipeline_based_service
_TEST_EXECUTION_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)

_TEST_RUN = "run-1"
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}"
_TEST_EXECUTION_NAME = f"{_TEST_EXECUTION_PARENT}/executions/{_TEST_EXECUTION_ID}"


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
                        schema_title=metadata_constants.SYSTEM_RUN,
                        schema_version=metadata_constants.SCHEMA_VERSIONS[
                            metadata_constants.SYSTEM_RUN
                        ],
                        metadata={"component_type": _TEST_COMPONENT_IDENTIFIER},
                    ),
                ),
            ],
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
def mock_successfully_completed_eval_job():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_model_eval_job:
        mock_get_model_eval_job.return_value = make_pipeline_job(
            gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED
        )
        yield mock_get_model_eval_job


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
def mock_load_yaml_and_json(job_spec_json):
    with patch.object(storage.Blob, "download_as_bytes") as mock_load_yaml_and_json:
        mock_load_yaml_and_json.return_value = job_spec_json.encode()
        yield mock_load_yaml_and_json


@pytest.fixture
def mock_request_urlopen(job_spec_json):
    with mock.patch.object(request, "urlopen") as mock_urlopen:
        mock_read_response = mock.MagicMock()
        mock_decode_response = mock.MagicMock()
        mock_decode_response.return_value = job_spec_json.encode()
        mock_read_response.return_value.decode = mock_decode_response
        mock_urlopen.return_value.read = mock_read_response
        yield mock_urlopen


@pytest.fixture
def preview_get_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client_v1beta1.DeploymentResourcePoolServiceClient,
        "get_deployment_resource_pool",
    ) as get_drp_mock:
        machine_spec = gca_machine_resources_v1beta1.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )

        autoscaling_metric_specs = [
            gca_machine_resources_v1beta1.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_CPU_UTILIZATION, target=70
            ),
            gca_machine_resources_v1beta1.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_GPU_UTILIZATION, target=70
            ),
        ]

        dedicated_resources = gca_machine_resources_v1beta1.DedicatedResources(
            machine_spec=machine_spec,
            min_replica_count=10,
            max_replica_count=20,
            autoscaling_metric_specs=autoscaling_metric_specs,
        )

        get_drp_mock.return_value = (
            gca_deployment_resource_pool_v1beta1.DeploymentResourcePool(
                name=_TEST_DRP_NAME,
                dedicated_resources=dedicated_resources,
            )
        )
        yield get_drp_mock


@pytest.fixture
def get_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client.DeploymentResourcePoolServiceClient,
        "get_deployment_resource_pool",
    ) as get_drp_mock:
        machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )

        autoscaling_metric_specs = [
            gca_machine_resources.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_CPU_UTILIZATION, target=70
            ),
            gca_machine_resources.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_GPU_UTILIZATION, target=70
            ),
        ]

        dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=machine_spec,
            min_replica_count=10,
            max_replica_count=20,
            autoscaling_metric_specs=autoscaling_metric_specs,
        )

        get_drp_mock.return_value = gca_deployment_resource_pool.DeploymentResourcePool(
            name=_TEST_DRP_NAME,
            dedicated_resources=dedicated_resources,
        )
        yield get_drp_mock


@pytest.fixture
def preview_deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client_v1beta1.EndpointServiceClient, "deploy_model"
    ) as preview_deploy_model_mock:
        deployed_model = gca_endpoint_v1beta1.DeployedModel(model=_TEST_MODEL_NAME)
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = (
            gca_endpoint_service_v1beta1.DeployModelResponse(
                deployed_model=deployed_model,
            )
        )
        preview_deploy_model_mock.return_value = deploy_model_lro_mock
        yield preview_deploy_model_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestModel:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor_creates_client(self, create_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        models.Model(_TEST_ID)
        create_client_mock.assert_any_call(
            client_class=utils.ModelClientWithOverride,
            credentials=initializer.global_config.credentials,
            location_override=_TEST_LOCATION,
            appended_user_agent=None,
        )

    def test_constructor_create_client_with_custom_location(self, create_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        models.Model(_TEST_ID, location=_TEST_LOCATION_2)
        create_client_mock.assert_any_call(
            client_class=utils.ModelClientWithOverride,
            credentials=initializer.global_config.credentials,
            location_override=_TEST_LOCATION_2,
            appended_user_agent=None,
        )

    def test_constructor_creates_client_with_custom_credentials(
        self, create_client_mock
    ):
        creds = auth_credentials.AnonymousCredentials()
        models.Model(_TEST_ID, credentials=creds)
        create_client_mock.assert_any_call(
            client_class=utils.ModelClientWithOverride,
            credentials=creds,
            location_override=_TEST_LOCATION,
            appended_user_agent=None,
        )

    def test_constructor_gets_model(self, get_model_mock):
        models.Model(_TEST_ID)
        get_model_mock.assert_called_once_with(
            name=_TEST_MODEL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_constructor_gets_model_with_custom_project(self, get_model_mock):
        models.Model(_TEST_ID, project=_TEST_PROJECT_2)
        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )
        get_model_mock.assert_called_once_with(
            name=test_model_resource_name, retry=base._DEFAULT_RETRY
        )

    def test_constructor_gets_model_with_custom_location(self, get_model_mock):
        models.Model(_TEST_ID, location=_TEST_LOCATION_2)
        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
        )
        get_model_mock.assert_called_once_with(
            name=test_model_resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model(
        self, upload_model_mock, get_model_mock, sync
    ):

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            sync=sync,
            upload_request_timeout=None,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

        get_model_mock.assert_called_once_with(
            name=_TEST_MODEL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_upload_without_serving_container_image_uri_throw_error(
        self, upload_model_mock, get_model_mock
    ):
        expected_message = (
            "The parameter `serving_container_image_uri` is required "
            "if no `local_model` is provided."
        )

        with pytest.raises(ValueError) as exception:
            _ = models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                artifact_uri=_TEST_ARTIFACT_URI,
            )

        assert str(exception.value) == expected_message

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_local_model(self, upload_model_mock, get_model_mock, sync):
        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=_TEST_LOCAL_MODEL.get_serving_container_spec(),
            version_aliases=["default"],
        )

        my_model = models.Model.upload(
            local_model=_TEST_LOCAL_MODEL,
            display_name=_TEST_MODEL_NAME,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_local_model_overwrite_all_serving_container_parameters(
        self, upload_model_mock, get_model_mock, sync
    ):
        container_spec = gca_model.ModelContainerSpec(
            image_uri="another-image-uri",
            predict_route="another-predict-route",
            health_route="another-health-route",
        )
        local_model = LocalModel(serving_container_spec=container_spec)
        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            version_aliases=["default"],
        )

        my_model = models.Model.upload(
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            local_model=local_model,
            display_name=_TEST_MODEL_NAME,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_timeout(self, upload_model_mock, get_model_mock, sync):
        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            sync=sync,
            upload_request_timeout=180.0,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=180.0,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_timeout_not_explicitly_set(
        self, upload_model_mock, get_model_mock, sync
    ):
        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_labels(
        self, upload_model_mock, get_model_mock, sync
    ):

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            labels=_TEST_LABEL,
            upload_request_timeout=None,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            labels=_TEST_LABEL,
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

        get_model_mock.assert_called_once_with(
            name=_TEST_MODEL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_upload_raises_with_impartial_explanation_spec(self):

        with pytest.raises(ValueError) as e:
            models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                explanation_metadata=_TEST_EXPLANATION_METADATA
                # Missing the required explanations_parameters field
            )

        assert e.match(
            regexp=r"To get model explanation, `explanation_parameters` "
            "must be specified."
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_parameters_without_metadata(
        self, upload_model_mock, get_model_mock, sync
    ):
        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            # No explanation_metadata provided
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            explanation_spec=gca_model.explanation.ExplanationSpec(
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_parameters_for_examples_presets(
        self, upload_model_mock, get_model_mock, sync
    ):
        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS_EXAMPLES_PRESETS,
            explanation_metadata=_TEST_EXPLANATION_METADATA_EXAMPLES,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA_EXAMPLES,
                parameters=_TEST_EXPLANATION_PARAMETERS_EXAMPLES_PRESETS,
            ),
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_with_parameters_for_examples_full_config(
        self, upload_model_mock, get_model_mock, sync
    ):
        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS_EXAMPLES_FULL_CONFIG,
            explanation_metadata=_TEST_EXPLANATION_METADATA_EXAMPLES,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA_EXAMPLES,
                parameters=_TEST_EXPLANATION_PARAMETERS_EXAMPLES_FULL_CONFIG,
            ),
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_all_args(
        self, upload_model_mock, get_model_mock, sync
    ):

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            instance_schema_uri=_TEST_INSTANCE_SCHEMA_URI,
            parameters_schema_uri=_TEST_PARAMETERS_SCHEMA_URI,
            prediction_schema_uri=_TEST_PREDICTION_SCHEMA_URI,
            description=_TEST_DESCRIPTION,
            serving_container_command=_TEST_SERVING_CONTAINER_COMMAND,
            serving_container_args=_TEST_SERVING_CONTAINER_ARGS,
            serving_container_environment_variables=_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            serving_container_ports=_TEST_SERVING_CONTAINER_PORTS,
            serving_container_grpc_ports=_TEST_SERVING_CONTAINER_GRPC_PORTS,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            labels=_TEST_LABEL,
            sync=sync,
            upload_request_timeout=None,
            serving_container_deployment_timeout=_TEST_SERVING_CONTAINER_DEPLOYMENT_TIMEOUT,
            serving_container_shared_memory_size_mb=_TEST_SERVING_CONTAINER_SHARED_MEMORY_SIZE_MB,
            serving_container_startup_probe_exec=_TEST_SERVING_CONTAINER_STARTUP_PROBE_EXEC,
            serving_container_startup_probe_period_seconds=_TEST_SERVING_CONTAINER_STARTUP_PROBE_PERIOD_SECONDS,
            serving_container_startup_probe_timeout_seconds=_TEST_SERVING_CONTAINER_STARTUP_PROBE_TIMEOUT_SECONDS,
            serving_container_health_probe_exec=_TEST_SERVING_CONTAINER_HEALTH_PROBE_EXEC,
            serving_container_health_probe_period_seconds=_TEST_SERVING_CONTAINER_HEALTH_PROBE_PERIOD_SECONDS,
            serving_container_health_probe_timeout_seconds=_TEST_SERVING_CONTAINER_HEALTH_PROBE_TIMEOUT_SECONDS,
        )

        if not sync:
            my_model.wait()

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_PORTS
        ]

        grpc_ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_GRPC_PORTS
        ]

        deployment_timeout = duration_pb2.Duration(
            seconds=_TEST_SERVING_CONTAINER_DEPLOYMENT_TIMEOUT
        )

        startup_probe = gca_model.Probe(
            exec=gca_model.Probe.ExecAction(
                command=_TEST_SERVING_CONTAINER_STARTUP_PROBE_EXEC
            ),
            period_seconds=_TEST_SERVING_CONTAINER_STARTUP_PROBE_PERIOD_SECONDS,
            timeout_seconds=_TEST_SERVING_CONTAINER_STARTUP_PROBE_TIMEOUT_SECONDS,
        )

        health_probe = gca_model.Probe(
            exec=gca_model.Probe.ExecAction(
                command=_TEST_SERVING_CONTAINER_HEALTH_PROBE_EXEC
            ),
            period_seconds=_TEST_SERVING_CONTAINER_HEALTH_PROBE_PERIOD_SECONDS,
            timeout_seconds=_TEST_SERVING_CONTAINER_HEALTH_PROBE_TIMEOUT_SECONDS,
        )

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_SERVING_CONTAINER_COMMAND,
            args=_TEST_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
            grpc_ports=grpc_ports,
            deployment_timeout=deployment_timeout,
            shared_memory_size_mb=_TEST_SERVING_CONTAINER_SHARED_MEMORY_SIZE_MB,
            startup_probe=startup_probe,
            health_probe=health_probe,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            description=_TEST_DESCRIPTION,
            artifact_uri=_TEST_ARTIFACT_URI,
            container_spec=container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_PREDICTION_SCHEMA_URI,
            ),
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
            version_aliases=["default"],
        )

        upload_model_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            ),
            timeout=None,
        )
        get_model_mock.assert_called_once_with(
            name=_TEST_MODEL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_model_with_custom_project_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_custom_project(
        self,
        upload_model_with_custom_project_mock,
        get_model_with_custom_project_mock,
        sync,
    ):

        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            project=_TEST_PROJECT_2,
            sync=sync,
            upload_request_timeout=None,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            container_spec=container_spec,
            version_aliases=["default"],
        )

        upload_model_with_custom_project_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=f"projects/{_TEST_PROJECT_2}/locations/{_TEST_LOCATION}",
                model=managed_model,
            ),
            timeout=None,
        )

        get_model_with_custom_project_mock.assert_called_once_with(
            name=test_model_resource_name, retry=base._DEFAULT_RETRY
        )

        assert my_model.uri == _TEST_ARTIFACT_URI
        assert my_model.supported_export_formats == {}
        assert my_model.supported_deployment_resources_types == []
        assert my_model.supported_input_storage_formats == []
        assert my_model.supported_output_storage_formats == []
        assert my_model.description == _TEST_DESCRIPTION

    @pytest.mark.usefixtures("get_model_with_custom_project_mock")
    def test_accessing_properties_with_no_resource_raises(
        self,
    ):

        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )

        my_model = models.Model(test_model_resource_name)
        my_model._gca_resource = None

        with pytest.raises(RuntimeError) as e:
            my_model.uri
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_export_formats
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_deployment_resources_types
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_input_storage_formats
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_output_storage_formats
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.description
        e.match(regexp=r"Model resource has not been created.")

    @pytest.mark.usefixtures("get_model_with_custom_location_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_custom_location(
        self,
        upload_model_with_custom_location_mock,
        get_model_with_custom_location_mock,
        sync,
    ):
        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
        )

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            location=_TEST_LOCATION_2,
            sync=sync,
            upload_request_timeout=None,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            container_spec=container_spec,
            version_aliases=["default"],
        )

        upload_model_with_custom_location_mock.assert_called_once_with(
            request=gca_model_service.UploadModelRequest(
                parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION_2}",
                model=managed_model,
            ),
            timeout=None,
        )

        get_model_with_custom_location_mock.assert_called_once_with(
            name=test_model_resource_name, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        test_endpoint = models.Endpoint(_TEST_ID)

        assert (
            test_model.deploy(
                test_endpoint,
                sync=sync,
            )
            == test_endpoint
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_timeout(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        test_endpoint = models.Endpoint(_TEST_ID)

        test_model.deploy(test_endpoint, sync=sync, deploy_request_timeout=180.0)

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=180.0,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_timeout_not_explicitly_set(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        test_endpoint = models.Endpoint(_TEST_ID)

        test_model.deploy(
            test_endpoint,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_with_version")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_version(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_MODEL_NAME)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        version = _TEST_MODEL_OBJ_WITH_VERSION.version_id

        test_endpoint = models.Endpoint(_TEST_ID)

        test_endpoint = test_model.deploy(
            test_endpoint,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=f"{test_model.resource_name}@{version}",
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint = test_model.deploy(sync=sync)

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_dedicated_resources(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint = test_model.deploy(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
            spot=False,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_with_tpu_topology(self, deploy_model_mock, sync):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint = test_model.deploy(
            machine_type=_TEST_TPU_MACHINE_TYPE,
            tpu_topology=_TEST_TPU_TOPOLOGY,
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_TPU_MACHINE_TYPE,
            tpu_topology=_TEST_TPU_TOPOLOGY,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
            spot=False,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_with_spot(self, deploy_model_mock, sync):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint = test_model.deploy(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
            spot=_TEST_SPOT,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
            spot=True,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_with_specific_reservation_affinity(
        self, deploy_model_mock, sync
    ):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint = test_model.deploy(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
            reservation_affinity_type=_TEST_RESERVATION_AFFINITY_TYPE,
            reservation_affinity_key=_TEST_RESERVATION_AFFINITY_KEY,
            reservation_affinity_values=_TEST_RESERVATION_AFFINITY_VALUES,
        )

        if not sync:
            test_endpoint.wait()

        expected_reservation_affinity = gca_reservation_affinity_v1.ReservationAffinity(
            reservation_affinity_type=_TEST_RESERVATION_AFFINITY_TYPE,
            key=_TEST_RESERVATION_AFFINITY_KEY,
            values=_TEST_RESERVATION_AFFINITY_VALUES,
        )
        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reservation_affinity=expected_reservation_affinity,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
            spot=False,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_with_any_reservation_affinity(
        self, deploy_model_mock, sync
    ):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint = test_model.deploy(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
            reservation_affinity_type="ANY_RESERVATION",
        )

        if not sync:
            test_endpoint.wait()

        expected_reservation_affinity = gca_reservation_affinity_v1.ReservationAffinity(
            reservation_affinity_type="ANY_RESERVATION",
        )
        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            reservation_affinity=expected_reservation_affinity,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
            spot=False,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_with_explanations(self, deploy_model_mock, sync):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint = test_model.deploy(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
            spot=False,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            explanation_spec=gca_endpoint.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    def test_deploy_raises_with_impartial_explanation_spec(self):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )

        with pytest.raises(ValueError) as e:
            test_model.deploy(
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                explanation_metadata=_TEST_EXPLANATION_METADATA,
                # Missing required `explanation_parameters` argument
            )

        assert e.match(
            regexp=r"To get model explanation, `explanation_parameters` "
            "must be specified."
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    def test_deploy_no_endpoint_with_network(self, deploy_model_mock):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        test_endpoint = test_model.deploy(network=_TEST_NETWORK)
        # Ensure endpoint created with `network` is a PrivateEndpoint
        assert isinstance(test_endpoint, models.PrivateEndpoint)

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )

        # Ensure traffic_split is set to `None` for PrivateEndpoint
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split=None,
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_disable_container_logging(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        test_endpoint = models.Endpoint(_TEST_ID)

        assert (
            test_model.deploy(
                test_endpoint,
                disable_container_logging=True,
                sync=sync,
            )
            == test_endpoint
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
            disable_container_logging=True,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_model_mock",
        "preview_get_drp_mock",
        "create_endpoint_mock",
        "get_endpoint_mock",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_preview_deploy_with_deployment_resource_pool(
        self, preview_deploy_model_mock, sync
    ):
        test_model = models.Model(_TEST_ID).preview
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.SHARED_RESOURCES,
        )
        test_drp = preview_models.DeploymentResourcePool(_TEST_DRP_NAME)

        test_endpoint = test_model.deploy(
            deployment_resource_pool=test_drp,
            sync=sync,
            deploy_request_timeout=None,
        )
        if not sync:
            test_endpoint.wait()

        deployed_model = gca_endpoint_v1beta1.DeployedModel(
            shared_resources=_TEST_DRP_NAME,
            model=test_model.resource_name,
            display_name=None,
            enable_container_logging=True,
        )
        preview_deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_model_mock", "get_drp_mock", "create_endpoint_mock", "get_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_deployment_resource_pool(self, deploy_model_mock, sync):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.SHARED_RESOURCES,
        )
        test_drp = models.DeploymentResourcePool(_TEST_DRP_NAME)

        test_endpoint = test_model.deploy(
            deployment_resource_pool=test_drp,
            sync=sync,
            deploy_request_timeout=None,
        )
        if not sync:
            test_endpoint.wait()

        deployed_model = gca_endpoint.DeployedModel(
            shared_resources=_TEST_DRP_NAME,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_init_aiplatform_with_encryption_key_name_and_batch_predict_gcs_source_and_dest(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )
        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = (
            gca_batch_prediction_job.BatchPredictionJob(
                display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                model=model_service_client.ModelServiceClient.model_path(
                    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
                ),
                input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                    instances_format="jsonl",
                    gcs_source=gca_io.GcsSource(
                        uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                    ),
                ),
                output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                    gcs_destination=gca_io.GcsDestination(
                        output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                    ),
                    predictions_format="jsonl",
                ),
                encryption_spec=_TEST_ENCRYPTION_SPEC,
                service_account=_TEST_SERVICE_ACCOUNT,
            )
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_init_aiplatform_with_service_account_and_batch_predict_gcs_source_and_dest(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = (
            gca_batch_prediction_job.BatchPredictionJob(
                display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                model=model_service_client.ModelServiceClient.model_path(
                    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
                ),
                input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                    instances_format="jsonl",
                    gcs_source=gca_io.GcsSource(
                        uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                    ),
                ),
                output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                    gcs_destination=gca_io.GcsDestination(
                        output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                    ),
                    predictions_format="jsonl",
                ),
                encryption_spec=_TEST_ENCRYPTION_SPEC,
                service_account=_TEST_SERVICE_ACCOUNT,
            )
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_and_dest(
        self, create_batch_prediction_job_mock, sync
    ):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        if not sync:
            batch_prediction_job.wait()

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_version", "get_batch_prediction_job_mock")
    def test_batch_predict_with_version(self, sync, create_batch_prediction_job_mock):

        test_model = models.Model(_TEST_MODEL_NAME, version=_TEST_VERSION_ALIAS_1)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = (
            gca_batch_prediction_job.BatchPredictionJob(
                display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                model=f"{_TEST_MODEL_PARENT}@{_TEST_VERSION_ID}",
                input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                    instances_format="jsonl",
                    gcs_source=gca_io.GcsSource(
                        uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                    ),
                ),
                output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                    gcs_destination=gca_io.GcsDestination(
                        output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                    ),
                    predictions_format="jsonl",
                ),
                service_account=_TEST_SERVICE_ACCOUNT,
            )
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_bq_dest(
        self, create_batch_prediction_job_mock, sync
    ):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            sync=sync,
            create_request_timeout=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = (
            gca_batch_prediction_job.BatchPredictionJob(
                display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                model=model_service_client.ModelServiceClient.model_path(
                    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
                ),
                input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                    instances_format="jsonl",
                    gcs_source=gca_io.GcsSource(
                        uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]
                    ),
                ),
                output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                    bigquery_destination=gca_io.BigQueryDestination(
                        output_uri=_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL
                    ),
                    predictions_format="bigquery",
                ),
                service_account=_TEST_SERVICE_ACCOUNT,
            )
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_with_all_args(self, create_batch_prediction_job_mock, sync):
        test_model = models.Model(_TEST_ID)
        creds = auth_credentials.AnonymousCredentials()

        # Make SDK batch_predict method call passing all arguments
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            predictions_format="csv",
            model_parameters={},
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
            max_replica_count=_TEST_MAX_REPLICA_COUNT,
            generate_explanation=True,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            labels=_TEST_LABEL,
            credentials=creds,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
            create_request_timeout=None,
            batch_size=_TEST_BATCH_SIZE,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            model=model_service_client.ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            ),
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="csv",
            ),
            dedicated_resources=gca_machine_resources.BatchDedicatedResources(
                machine_spec=gca_machine_resources.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                ),
                starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
                max_replica_count=_TEST_MAX_REPLICA_COUNT,
            ),
            manual_batch_tuning_parameters=gca_manual_batch_tuning_parameters_compat.ManualBatchTuningParameters(
                batch_size=_TEST_BATCH_SIZE
            ),
            generate_explanation=True,
            explanation_spec=gca_explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
            service_account=_TEST_SERVICE_ACCOUNT,
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            batch_prediction_job=expected_gapic_batch_prediction_job,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_no_source(self, create_batch_prediction_job_mock):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call without source
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"source")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_two_sources(self, create_batch_prediction_job_mock):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call with two sources
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                bigquery_source=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"source")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_no_destination(self):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call without destination
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            )

        assert e.match(regexp=r"destination")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_wrong_instance_format(self):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                instances_format="wrong",
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"accepted instances format")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_wrong_prediction_format(self):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                predictions_format="wrong",
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"accepted prediction format")

    @pytest.mark.usefixtures("get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_model(self, delete_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model.delete(sync=sync)

        if not sync:
            test_model.wait()

        delete_model_mock.assert_called_once_with(name=test_model.resource_name)

    @pytest.mark.usefixtures("get_model_mock")
    def test_print_model(self):
        test_model = models.Model(_TEST_ID)
        assert (
            repr(test_model)
            == f"{object.__repr__(test_model)} \nresource name: {test_model.resource_name}"
        )

    @pytest.mark.usefixtures("get_model_mock")
    def test_print_model_if_waiting(self):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource = None
        test_model._latest_future = futures.Future()
        assert (
            repr(test_model)
            == f"{object.__repr__(test_model)} is waiting for upstream dependencies to complete."
        )

    @pytest.mark.usefixtures("get_model_mock")
    def test_print_model_if_exception(self):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource = None
        mock_exception = Exception("mock exception")
        test_model._exception = mock_exception
        assert (
            repr(test_model)
            == f"{object.__repr__(test_model)} failed with {str(mock_exception)}"
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_artifact")
    def test_export_model_as_artifact(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        if not sync:
            test_model.wait()

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            artifact_destination=_TEST_OUTPUT_DIR,
        )

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            artifact_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_OUTPUT_DIR
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures(
        "get_model_with_supported_export_formats_artifact_and_version"
    )
    def test_export_model_with_version(self, export_model_mock, sync):
        test_model = models.Model(f"{_TEST_ID}@{_TEST_VERSION_ID}")

        if not sync:
            test_model.wait()

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            artifact_destination=_TEST_OUTPUT_DIR,
        )

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            artifact_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_OUTPUT_DIR
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}@{_TEST_VERSION_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_image")
    def test_export_model_as_image(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
            image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
        )

        if not sync:
            test_model.wait()

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
            image_destination=gca_io.ContainerRegistryDestination(
                output_uri=_TEST_CONTAINER_REGISTRY_DESTINATION
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_both_supported_export_formats")
    def test_export_model_as_both_formats(self, export_model_mock, sync):
        """Exports a 'tf-saved-model' as both an artifact and an image"""

        test_model = models.Model(_TEST_ID)

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
            artifact_destination=_TEST_OUTPUT_DIR,
        )

        if not sync:
            test_model.wait()

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            image_destination=gca_io.ContainerRegistryDestination(
                output_uri=_TEST_CONTAINER_REGISTRY_DESTINATION
            ),
            artifact_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_OUTPUT_DIR
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_unsupported_export_formats")
    def test_export_model_not_supported(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        with pytest.raises(ValueError) as e:
            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
                image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
            )

            if not sync:
                test_model.wait()

            assert e.match(
                regexp=f"The model `{_TEST_PARENT}/models/{_TEST_ID}` is not exportable."
            )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_image")
    def test_export_model_as_image_with_invalid_args(self, export_model_mock, sync):

        # Passing an artifact destination on an image-only Model
        with pytest.raises(ValueError) as dest_type_err:
            test_model = models.Model(_TEST_ID)

            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
                artifact_destination=_TEST_OUTPUT_DIR,
                sync=sync,
            )

            if not sync:
                test_model.wait()

        # Passing no destination type
        with pytest.raises(ValueError) as no_dest_err:
            test_model = models.Model(_TEST_ID)

            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
                sync=sync,
            )

            if not sync:
                test_model.wait()

        # Passing an invalid export format ID
        with pytest.raises(ValueError) as format_err:
            test_model = models.Model(_TEST_ID)
            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
                image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
                sync=sync,
            )

            if not sync:
                test_model.wait()

        assert dest_type_err.match(
            regexp=r"This model can not be exported as an artifact."
        )
        assert no_dest_err.match(regexp=r"Please provide an")
        assert format_err.match(
            regexp=f"'{_TEST_EXPORT_FORMAT_ID_ARTIFACT}' is not a supported export format"
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_artifact")
    def test_export_model_as_artifact_with_invalid_args(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        # Passing an image destination on an artifact-only Model
        with pytest.raises(ValueError) as e:
            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
                image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
                sync=sync,
            )

            if not sync:
                test_model.wait()

            assert e.match(
                regexp=r"This model can not be exported as a container image."
            )

    @pytest.mark.usefixtures(
        "get_training_job_non_existent_mock", "get_model_with_training_job"
    )
    def test_get_and_return_subclass_not_found(self):
        test_model = models.Model(_TEST_ID)

        # Attempt to access Model's training job that no longer exists
        with pytest.raises(api_exceptions.NotFound) as e:
            test_model.training_job

        assert e.match(
            regexp=(
                r"The training job used to create this model could not be found: "
                rf"{_TEST_PIPELINE_RESOURCE_NAME}"
            )
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "model_file_name",
        ["my_model.xgb", "my_model.pkl", "my_model.joblib", "my_model.bst"],
    )
    def test_upload_xgboost_model_file_uploads_and_gets_model(
        self,
        tmp_path: pathlib.Path,
        model_file_name: str,
        mock_storage_blob_upload_from_filename,
        upload_model_mock,
        get_model_mock,
        sync: bool,
    ):
        model_file_path = tmp_path / model_file_name
        model_file_path.touch()

        my_model = models.Model.upload_xgboost_model_file(
            model_file_path=str(model_file_path),
            xgboost_version="1.4",
            display_name=_TEST_MODEL_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            sync=sync,
            upload_request_timeout=None,
        )

        if not sync:
            my_model.wait()

        upload_model_mock.assert_called_once()
        upload_model_call_kwargs = upload_model_mock.call_args[1]
        upload_model_model = upload_model_call_kwargs["request"].model

        # Verifying the container image selection
        assert (
            upload_model_model.container_spec.image_uri
            == "us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-4:latest"
        )

        # Verifying the staging bucket name generation
        assert upload_model_model.artifact_uri.startswith(
            f"gs://{_TEST_PROJECT}-vertex-staging-{_TEST_LOCATION}"
        )
        assert "/vertex_ai_auto_staging/" in upload_model_model.artifact_uri

        # Verifying that the model was renamed to a file name that is acceptable for Model.upload
        staged_model_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        staged_model_file_name = staged_model_file_path.split("/")[-1]
        assert staged_model_file_name in ["model.bst", "model.pkl", "model.joblib"]

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "model_file_name",
        [
            "model.bst",
            "model.pkl",
            "model.joblib",
            "saved_model.pb",
            "saved_model.pbtxt",
        ],
    )
    def test_upload_stages_data_uploads_and_gets_model(
        self,
        tmp_path: pathlib.Path,
        model_file_name: str,
        mock_storage_blob_upload_from_filename,
        upload_model_mock,
        get_model_mock,
        sync: bool,
    ):
        model_file_path = tmp_path / model_file_name
        model_file_path.touch()

        my_model = models.Model.upload(
            artifact_uri=str(tmp_path),
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/xgboost-cpu.1-4:latest",
            display_name=_TEST_MODEL_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        upload_model_mock.assert_called_once()
        upload_model_call_kwargs = upload_model_mock.call_args[1]
        upload_model_model = upload_model_call_kwargs["request"].model

        # Verifying the staging bucket name generation
        assert upload_model_model.artifact_uri.startswith(
            f"gs://{_TEST_PROJECT}-vertex-staging-{_TEST_LOCATION}"
        )
        assert "/vertex_ai_auto_staging/" in upload_model_model.artifact_uri

        # Verifying that the model was renamed to a file name that is acceptable for Model.upload
        staged_model_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        staged_model_file_name = staged_model_file_path.split("/")[-1]
        assert staged_model_file_name in [
            "model.bst",
            "model.pkl",
            "model.joblib",
            "saved_model.pb",
            "saved_model.pbtxt",
        ]

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize(
        "model_file_name",
        ["my_model.pkl", "my_model.joblib"],
    )
    def test_upload_scikit_learn_model_file_uploads_and_gets_model(
        self,
        tmp_path: pathlib.Path,
        model_file_name: str,
        mock_storage_blob_upload_from_filename,
        upload_model_mock,
        get_model_mock,
        sync: bool,
    ):
        model_file_path = tmp_path / model_file_name
        model_file_path.touch()

        my_model = models.Model.upload_scikit_learn_model_file(
            model_file_path=str(model_file_path),
            sklearn_version="0.24",
            display_name=_TEST_MODEL_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            sync=sync,
            upload_request_timeout=None,
        )

        if not sync:
            my_model.wait()

        upload_model_mock.assert_called_once()
        upload_model_call_kwargs = upload_model_mock.call_args[1]
        upload_model_model = upload_model_call_kwargs["request"].model

        # Verifying the container image selection
        assert (
            upload_model_model.container_spec.image_uri
            == "us-docker.pkg.dev/vertex-ai/prediction/sklearn-cpu.0-24:latest"
        )

        # Verifying the staging bucket name generation
        assert upload_model_model.artifact_uri.startswith(
            f"gs://{_TEST_PROJECT}-vertex-staging-{_TEST_LOCATION}"
        )
        assert "/vertex_ai_auto_staging/" in upload_model_model.artifact_uri

        # Verifying that the model was renamed to a file name that is acceptable for Model.upload
        staged_model_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        staged_model_file_name = staged_model_file_path.split("/")[-1]
        assert staged_model_file_name in ["model.pkl", "model.joblib"]

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_tensorflow_saved_model_uploads_and_gets_model(
        self,
        tmp_path: pathlib.Path,
        mock_storage_blob_upload_from_filename,
        upload_model_mock,
        get_model_mock,
        sync: bool,
    ):
        saved_model_dir = tmp_path / "saved_model"
        saved_model_dir.mkdir()
        (saved_model_dir / "saved_model.pb").touch()

        my_model = models.Model.upload_tensorflow_saved_model(
            saved_model_dir=str(saved_model_dir),
            tensorflow_version="2.6",
            use_gpu=True,
            display_name=_TEST_MODEL_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            sync=sync,
            upload_request_timeout=None,
        )

        if not sync:
            my_model.wait()

        upload_model_mock.assert_called_once()
        upload_model_call_kwargs = upload_model_mock.call_args[1]
        upload_model_model = upload_model_call_kwargs["request"].model

        # Verifying the container image selection
        assert (
            upload_model_model.container_spec.image_uri
            == "us-docker.pkg.dev/vertex-ai/prediction/tf2-gpu.2-6:latest"
        )

        # Verifying the staging bucket name generation
        assert upload_model_model.artifact_uri.startswith(
            f"gs://{_TEST_PROJECT}-vertex-staging-{_TEST_LOCATION}"
        )
        assert "/vertex_ai_auto_staging/" in upload_model_model.artifact_uri

        # Verifying that the model files were uploaded
        staged_model_file_path = mock_storage_blob_upload_from_filename.call_args[1][
            "filename"
        ]
        staged_model_file_name = staged_model_file_path.split("/")[-1]
        assert staged_model_file_name in ["saved_model.pb", "saved_model.pbtxt"]

    def test_copy_as_new_model(self, copy_model_mock, get_model_mock):

        test_model = models.Model(_TEST_ID)
        test_model.copy(destination_location=_TEST_LOCATION_2)

        copy_model_mock.assert_called_once_with(
            request=gca_model_service.CopyModelRequest(
                parent=initializer.global_config.common_location_path(
                    location=_TEST_LOCATION_2
                ),
                source_model=_TEST_MODEL_RESOURCE_NAME,
            ),
            timeout=None,
        )

    def test_copy_as_new_version(self, copy_model_mock, get_model_mock):
        test_model = models.Model(_TEST_ID)
        test_model.copy(
            destination_location=_TEST_LOCATION_2,
            destination_parent_model=_TEST_MODEL_NAME_ALT,
        )

        copy_model_mock.assert_called_once_with(
            request=gca_model_service.CopyModelRequest(
                parent=initializer.global_config.common_location_path(
                    location=_TEST_LOCATION_2
                ),
                source_model=_TEST_MODEL_RESOURCE_NAME,
                parent_model=model_service_client.ModelServiceClient.model_path(
                    _TEST_PROJECT, _TEST_LOCATION_2, _TEST_MODEL_NAME_ALT
                ),
            ),
            timeout=None,
        )

    def test_copy_as_new_model_custom_id(self, copy_model_mock, get_model_mock):
        test_model = models.Model(_TEST_ID)
        test_model.copy(
            destination_location=_TEST_LOCATION_2, destination_model_id=_TEST_MODEL_ID
        )

        copy_model_mock.assert_called_once_with(
            request=gca_model_service.CopyModelRequest(
                parent=initializer.global_config.common_location_path(
                    location=_TEST_LOCATION_2
                ),
                source_model=_TEST_MODEL_RESOURCE_NAME,
                model_id=_TEST_MODEL_ID,
            ),
            timeout=None,
        )

    def test_copy_with_invalid_params(self, copy_model_mock, get_model_mock):
        with pytest.raises(ValueError) as e:
            test_model = models.Model(_TEST_ID)
            test_model.copy(
                destination_location=_TEST_LOCATION,
                destination_model_id=_TEST_MODEL_ID,
                destination_parent_model=_TEST_MODEL_RESOURCE_NAME,
            )

        assert e.match(
            regexp=r"`destination_model_id` and `destination_parent_model` can not be set together."
        )

    @pytest.mark.usefixtures("get_model_mock")
    def test_update(self, update_model_mock, get_model_mock):

        test_model = models.Model(_TEST_ID)

        test_model.update(
            display_name=_TEST_MODEL_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABEL,
        )

        current_model_proto = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABEL,
            name=_TEST_MODEL_RESOURCE_NAME,
        )

        update_mask = field_mask_pb2.FieldMask(
            paths=["display_name", "description", "labels"]
        )

        update_model_mock.assert_called_once_with(
            model=current_model_proto, update_mask=update_mask
        )

    def test_get_model_evaluation_with_evaluation_id(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        test_model.get_model_evaluation(evaluation_id=_TEST_ID)

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_model_evaluation_with_evaluation_and_instantiated_version(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        test_model = models.Model(
            model_name=f"{_TEST_MODEL_RESOURCE_NAME}@{_TEST_VERSION_ID}"
        )

        test_model.get_model_evaluation(evaluation_id=_TEST_ID)

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

        list_model_evaluations_mock.assert_called_once_with(
            request={"parent": test_model.versioned_resource_name}
        )

    def test_get_model_evaluation_without_id(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        test_model.get_model_evaluation()

        list_model_evaluations_mock.assert_called_once_with(
            request={"parent": _TEST_MODEL_RESOURCE_NAME}
        )

    def test_list_model_evaluations(
        self,
        get_model_mock,
        mock_model_eval_get,
        list_model_evaluations_mock,
    ):

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        eval_list = test_model.list_model_evaluations()

        list_model_evaluations_mock.assert_called_once_with(
            request={"parent": _TEST_MODEL_RESOURCE_NAME}
        )

        assert len(eval_list) == len(_TEST_MODEL_EVAL_LIST)

    def test_list_model_evaluations_with_version(
        self,
        get_model_mock,
        mock_model_eval_get,
        list_model_evaluations_mock,
    ):

        test_model = models.Model(
            model_name=f"{_TEST_MODEL_RESOURCE_NAME}@{_TEST_VERSION_ID}"
        )

        test_model.list_model_evaluations()

        list_model_evaluations_mock.assert_called_once_with(
            request={"parent": test_model.versioned_resource_name}
        )

    def test_init_with_version_in_resource_name(self, get_model_with_version):
        model = models.Model(
            model_name=models.ModelRegistry._get_versioned_name(
                _TEST_MODEL_NAME, _TEST_VERSION_ALIAS_1
            )
        )

        assert model.version_aliases == [_TEST_VERSION_ALIAS_1, _TEST_VERSION_ALIAS_2]
        assert model.display_name == _TEST_MODEL_NAME
        assert model.resource_name == _TEST_MODEL_PARENT
        assert model.version_id == _TEST_VERSION_ID
        assert model.version_description == _TEST_MODEL_VERSION_DESCRIPTION_2
        # The Model yielded from upload should not have a version in resource name
        assert "@" not in model.resource_name
        # The Model yielded from upload SHOULD have a version in the versioned resource name
        assert model.versioned_resource_name.endswith(f"@{_TEST_VERSION_ID}")

    def test_init_with_version_arg(self, get_model_with_version):
        model = models.Model(model_name=_TEST_MODEL_NAME, version=_TEST_VERSION_ID)

        assert model.version_aliases == [_TEST_VERSION_ALIAS_1, _TEST_VERSION_ALIAS_2]
        assert model.display_name == _TEST_MODEL_NAME
        assert model.resource_name == _TEST_MODEL_PARENT
        assert model.version_id == _TEST_VERSION_ID
        assert model.version_description == _TEST_MODEL_VERSION_DESCRIPTION_2
        # The Model yielded from upload should not have a version in resource name
        assert "@" not in model.resource_name
        # The Model yielded from upload SHOULD have a version in the versioned resource name
        assert model.versioned_resource_name.endswith(f"@{_TEST_VERSION_ID}")

    @pytest.mark.parametrize(
        "parent,location,project",
        [
            (_TEST_MODEL_NAME, _TEST_LOCATION, _TEST_PROJECT),
            (_TEST_MODEL_PARENT, None, None),
        ],
    )
    @pytest.mark.parametrize(
        "aliases,default,goal",
        [
            (["alias1", "alias2"], True, ["alias1", "alias2", "default"]),
            (None, True, ["default"]),
            (["alias1", "alias2", "default"], True, ["alias1", "alias2", "default"]),
            (["alias1", "alias2", "default"], False, ["alias1", "alias2", "default"]),
            (["alias1", "alias2"], False, ["alias1", "alias2"]),
            (None, False, []),
        ],
    )
    @pytest.mark.parametrize(
        "callable, model_file_path, saved_model",
        [
            (models.Model.upload, None, None),
            (models.Model.upload_scikit_learn_model_file, "my_model.pkl", None),
            (models.Model.upload_tensorflow_saved_model, None, "saved_model.pb"),
            (models.Model.upload_xgboost_model_file, "my_model.xgb", None),
        ],
    )
    def test_upload_new_version(
        self,
        upload_model_with_version_mock,
        get_model_with_version,
        mock_storage_blob_upload_from_filename,
        parent,
        location,
        project,
        aliases,
        default,
        goal,
        callable,
        model_file_path,
        saved_model,
        tmp_path: pathlib.Path,
    ):
        args = {
            "display_name": _TEST_MODEL_NAME,
            "location": location,
            "project": project,
            "sync": True,
            "upload_request_timeout": None,
            "model_id": _TEST_ID,
            "parent_model": parent,
            "version_description": _TEST_MODEL_VERSION_DESCRIPTION_2,
            "version_aliases": aliases,
            "is_default_version": default,
        }
        if model_file_path:
            model_file_path = tmp_path / model_file_path
            model_file_path.touch()
            args["model_file_path"] = str(model_file_path)
        elif saved_model:
            saved_model_dir = tmp_path / "saved_model"
            saved_model_dir.mkdir()
            (saved_model_dir / saved_model).touch()
            args["saved_model_dir"] = str(saved_model_dir)
        else:
            args["serving_container_image_uri"] = _TEST_SERVING_CONTAINER_IMAGE

        _ = callable(**args)

        upload_model_with_version_mock.assert_called_once()
        upload_model_call_kwargs = upload_model_with_version_mock.call_args[1]
        upload_model_request = upload_model_call_kwargs["request"]

        assert upload_model_request.model.display_name == _TEST_MODEL_NAME
        assert upload_model_request.model.version_aliases == goal
        assert (
            upload_model_request.model.version_description
            == _TEST_MODEL_VERSION_DESCRIPTION_2
        )
        assert upload_model_request.parent_model == _TEST_MODEL_PARENT
        assert upload_model_request.model_id == _TEST_ID

    def test_get_model_instance_from_registry(self, get_model_with_version):
        registry = models.ModelRegistry(_TEST_MODEL_PARENT)
        model = registry.get_model(_TEST_VERSION_ALIAS_1)
        assert model.version_aliases == [_TEST_VERSION_ALIAS_1, _TEST_VERSION_ALIAS_2]
        assert model.display_name == _TEST_MODEL_NAME
        assert model.resource_name == _TEST_MODEL_PARENT
        assert model.version_id == _TEST_VERSION_ID
        assert model.version_description == _TEST_MODEL_VERSION_DESCRIPTION_2

    def test_list_versions(self, list_model_versions_mock, get_model_with_version):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        versions = my_model.versioning_registry.list_versions()

        assert len(versions) == len(_TEST_MODEL_VERSIONS_LIST)

        for i in range(len(versions)):
            ver = versions[i]
            model = _TEST_MODEL_VERSIONS_LIST[i]
            assert ver.version_id == model.version_id
            assert ver.version_create_time == model.version_create_time
            assert ver.version_update_time == model.version_update_time
            assert ver.model_display_name == model.display_name
            assert ver.version_aliases == model.version_aliases
            assert ver.version_description == model.version_description

            assert model.name.startswith(ver.model_resource_name)
            assert model.name.endswith(ver.version_id)

    def test_list_versions_with_filter(
        self, list_model_versions_with_filter_mock, get_model_with_version
    ):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        versions = my_model.versioning_registry.list_versions(
            filter='labels.team="experimentation"'
        )

        assert len(versions) == len(_TEST_MODEL_VERSIONS_WITH_FILTER_LIST)

        ver = versions[0]
        model = _TEST_MODEL_VERSIONS_WITH_FILTER_LIST[0]
        assert ver.version_id == "3"
        assert ver.version_create_time == model.version_create_time
        assert ver.version_update_time == model.version_update_time
        assert ver.model_display_name == model.display_name
        assert ver.version_aliases == model.version_aliases
        assert ver.version_description == model.version_description

        assert model.name.startswith(ver.model_resource_name)
        assert model.name.endswith(ver.version_id)

    def test_get_version_info(self, get_model_with_version):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        ver = my_model.versioning_registry.get_version_info("2")
        model = _TEST_MODEL_OBJ_WITH_VERSION

        assert ver.version_id == model.version_id
        assert ver.version_create_time == model.version_create_time
        assert ver.version_update_time == model.version_update_time
        assert ver.model_display_name == model.display_name
        assert ver.version_aliases == model.version_aliases
        assert ver.version_description == model.version_description

        assert model.name.startswith(ver.model_resource_name)
        assert model.name.endswith(ver.version_id)

    def test_delete_version(self, delete_model_version_mock, get_model_with_version):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        my_model.versioning_registry.delete_version(_TEST_VERSION_ALIAS_1)

        delete_model_version_mock.assert_called_once_with(
            name=models.ModelRegistry._get_versioned_name(
                _TEST_MODEL_PARENT, _TEST_VERSION_ALIAS_1
            )
        )

    @pytest.mark.usefixtures("get_model_mock")
    def test_update_version(
        self, update_model_mock, get_model_mock, get_model_with_version
    ):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        my_model.versioning_registry.update_version(
            _TEST_VERSION_ALIAS_1,
            version_description="update version",
            labels=_TEST_LABEL,
        )

        model_to_update = _TEST_MODEL_OBJ_WITH_VERSION
        model_to_update.version_description = "update version"
        model_to_update.labels = _TEST_LABEL

        update_mask = field_mask_pb2.FieldMask(paths=["version_description", "labels"])

        update_model_mock.assert_called_once_with(
            model=model_to_update, update_mask=update_mask
        )

    def test_add_versions(self, merge_version_aliases_mock, get_model_with_version):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        my_model.versioning_registry.add_version_aliases(
            ["new-alias", "other-new-alias"], _TEST_VERSION_ALIAS_1
        )

        merge_version_aliases_mock.assert_called_once_with(
            name=models.ModelRegistry._get_versioned_name(
                _TEST_MODEL_PARENT, _TEST_VERSION_ALIAS_1
            ),
            version_aliases=["new-alias", "other-new-alias"],
        )

    def test_remove_versions(self, merge_version_aliases_mock, get_model_with_version):
        my_model = models.Model(_TEST_MODEL_NAME, _TEST_PROJECT, _TEST_LOCATION)
        my_model.versioning_registry.remove_version_aliases(
            ["old-alias", "other-old-alias"], _TEST_VERSION_ALIAS_1
        )

        merge_version_aliases_mock.assert_called_once_with(
            name=models.ModelRegistry._get_versioned_name(
                _TEST_MODEL_PARENT, _TEST_VERSION_ALIAS_1
            ),
            version_aliases=["-old-alias", "-other-old-alias"],
        )

    @pytest.mark.parametrize(
        "resource",
        [
            "abc",
            "abc@1",
            "abc@my-alias",
            pytest.param("@5", marks=pytest.mark.xfail),
            pytest.param("abc@", marks=pytest.mark.xfail),
            pytest.param("abc#alias", marks=pytest.mark.xfail),
        ],
    )
    def test_model_resource_id_validator(self, resource):
        models.Model._revisioned_resource_id_validator(resource)

    def test_list(self, list_models_mock):
        models_list = models.Model.list()

        assert len(models_list) == len(_TEST_MODELS_LIST)

        for i in range(len(models_list)):
            listed_model = models_list[i]
            ideal_model = _TEST_MODELS_LIST[i]
            assert listed_model.version_id == ideal_model.version_id
            assert listed_model.version_create_time == ideal_model.version_create_time
            assert listed_model.version_update_time == ideal_model.version_update_time
            assert listed_model.display_name == ideal_model.display_name
            assert listed_model.version_aliases == ideal_model.version_aliases
            assert listed_model.version_description == ideal_model.version_description

            assert ideal_model.name.startswith(listed_model.resource_name)
            if "@" in ideal_model.name:
                assert ideal_model.name.endswith(listed_model.version_id)

            assert listed_model.versioning_registry
            assert listed_model._revisioned_resource_id_validator

    @pytest.mark.usefixtures(
        "get_endpoint_mock",
        "get_model_mock",
        "create_endpoint_mock",
        "raw_predict_mock",
    )
    def test_raw_predict(self, raw_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_endpoint.raw_predict(_TEST_RAW_PREDICT_DATA, _TEST_RAW_PREDICT_HEADER)
        raw_predict_mock.assert_called_once_with(
            url=_TEST_RAW_PREDICT_URL,
            data=_TEST_RAW_PREDICT_DATA,
            headers=_TEST_RAW_PREDICT_HEADER,
        )

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_MODEL_EVAL_PIPELINE_JOB],
    )
    def test_model_evaluate_with_gcs_input_uris(
        self,
        get_model_mock,
        mock_model_eval_get,
        mock_get_model_evaluation,
        list_model_evaluations_mock,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_successfully_completed_eval_job,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
        job_spec_json,
        mock_request_urlopen,
    ):
        aiplatform.init(project=_TEST_PROJECT)

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        eval_job = test_model.evaluate(
            prediction_type="classification",
            target_field_name="class",
            class_labels=_TEST_MODEL_EVAL_CLASS_LABELS,
            staging_bucket="gs://my-eval-staging-path",
            gcs_source_uris=["gs://test-bucket/test-file.csv"],
        )

        assert isinstance(eval_job, model_evaluation_job._ModelEvaluationJob)

        assert mock_pipeline_service_create.called_once

        assert mock_pipeline_service_get.called_once

        eval_job.wait()

        eval_resource = eval_job.get_model_evaluation()

        assert isinstance(eval_resource, aiplatform.ModelEvaluation)

        assert eval_resource.metrics == _TEST_MODEL_EVAL_METRICS

        assert isinstance(eval_resource._backing_pipeline_job, aiplatform.PipelineJob)

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_MODEL_EVAL_PIPELINE_JOB_WITH_BQ_INPUT],
    )
    def test_model_evaluate_with_bigquery_input(
        self,
        get_model_mock,
        mock_model_eval_get,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_load_yaml_and_json,
        mock_pipeline_bucket_exists,
        job_spec_json,
        mock_request_urlopen,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket="gs://my-bucket")

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        eval_job = test_model.evaluate(
            prediction_type="classification",
            target_field_name="class",
            class_labels=_TEST_MODEL_EVAL_CLASS_LABELS,
            bigquery_source_uri=_TEST_BIGQUERY_EVAL_INPUT_URI,
            bigquery_destination_output_uri=_TEST_BIGQUERY_EVAL_DESTINATION_URI,
        )

        assert isinstance(eval_job, model_evaluation_job._ModelEvaluationJob)

        assert mock_pipeline_service_create.called_once

        assert mock_pipeline_service_get.called_once

    @pytest.mark.parametrize(
        "job_spec_json",
        [_TEST_MODEL_EVAL_PIPELINE_JOB],
    )
    def test_model_evaluate_using_initialized_staging_bucket(
        self,
        get_model_mock,
        mock_model_eval_get,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_pipeline_bucket_exists,
        mock_load_yaml_and_json,
        job_spec_json,
        mock_request_urlopen,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket="gs://my-bucket")

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        eval_job = test_model.evaluate(
            prediction_type="classification",
            target_field_name="class",
            class_labels=_TEST_MODEL_EVAL_CLASS_LABELS,
            gcs_source_uris=["gs://test-bucket/test-file.csv"],
        )

        assert isinstance(eval_job, model_evaluation_job._ModelEvaluationJob)

        assert mock_pipeline_service_create.called_once

        assert mock_pipeline_service_get.called_once

    def test_model_evaluate_with_no_staging_path_or_initialized_staging_bucket_raises(
        self,
        get_model_mock,
        mock_model_eval_get,
    ):

        aiplatform.init(project=_TEST_PROJECT)

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        with pytest.raises(ValueError):
            test_model.evaluate(
                prediction_type="classification",
                target_field_name="class",
                class_labels=_TEST_MODEL_EVAL_CLASS_LABELS,
                gcs_source_uris=["gs://test-bucket/test-file.csv"],
            )

    def test_model_evaluate_with_invalid_prediction_type_raises(
        self,
        get_model_mock,
        mock_model_eval_get,
    ):

        aiplatform.init(project=_TEST_PROJECT)

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        with pytest.raises(ValueError):
            test_model.evaluate(
                prediction_type="invalid_prediction_type",
                target_field_name="class",
                gcs_source_uris=["gs://test-bucket/test-file.csv"],
            )

    def test_model_evaluate_with_invalid_gcs_uri_raises(
        self,
        get_model_mock,
        mock_model_eval_get,
    ):

        aiplatform.init(project=_TEST_PROJECT)

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        with pytest.raises(ValueError):
            test_model.evaluate(
                prediction_type="classification",
                target_field_name="class",
                gcs_source_uris=["storage.googleapis.com/test-bucket/test-file.csv"],
            )

    def test_model_evaluate_with_invalid_bq_uri_raises(
        self,
        get_model_mock,
        mock_model_eval_get,
    ):

        aiplatform.init(project=_TEST_PROJECT)

        test_model = models.Model(model_name=_TEST_MODEL_RESOURCE_NAME)

        with pytest.raises(ValueError):
            test_model.evaluate(
                prediction_type="classification",
                target_field_name="class",
                bigquery_source_uri="my-project.my-dataset.my-table",
                bigquery_destination_output_uri="bq://my-project.my-dataset.my-table",
            )
