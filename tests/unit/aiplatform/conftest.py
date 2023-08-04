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

from google import auth
from google.api_core import operation
from google.auth import credentials as auth_credentials

from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform.utils import source_utils
import constants as test_constants
from google.cloud.aiplatform.metadata import constants as metadata_constants
from google.cloud.aiplatform.compat.services import (
    metadata_service_client_v1,
    model_service_client,
    tensorboard_service_client,
    pipeline_service_client,
)

from google.cloud.aiplatform.compat.types import (
    context,
    endpoint,
    metadata_store,
    endpoint_service,
    model,
    model_service,
    pipeline_job,
    pipeline_state,
    tensorboard,
    tensorboard_service,
    dataset,
    prediction_service,
    training_pipeline,
)


from google.cloud.aiplatform.compat.services import (
    dataset_service_client,
    endpoint_service_client,
    prediction_service_client,
)


# Module-scoped fixtures
@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            "test-project",
        )
        yield google_auth_mock


# Training job fixtures
@pytest.fixture
def mock_python_package_to_gcs():
    with mock.patch.object(
        source_utils._TrainingScriptPythonPackager, "package_and_copy_to_gcs"
    ) as mock_package_to_copy_gcs:
        mock_package_to_copy_gcs.return_value = (
            test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH
        )
        yield mock_package_to_copy_gcs


# Model fixtures
@pytest.fixture
def upload_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(operation.Operation)
        mock_lro.result.return_value = model_service.UploadModelResponse(
            model=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = model.Model(
            display_name=test_constants.ModelConstants._TEST_MODEL_NAME,
            name=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_version_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = (
            test_constants.ModelConstants._TEST_MODEL_OBJ_WITH_VERSION
        )
        yield get_model_mock


@pytest.fixture
def deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = endpoint.DeployedModel(
            model=test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME,
            display_name=test_constants.ModelConstants._TEST_MODEL_NAME,
        )
        deploy_model_lro_mock = mock.Mock(operation.Operation)
        deploy_model_lro_mock.result.return_value = (
            endpoint_service.DeployModelResponse(
                deployed_model=deployed_model,
            )
        )
        deploy_model_mock.return_value = deploy_model_lro_mock
        yield deploy_model_mock


# Tensorboard fixtures
@pytest.fixture
def get_tensorboard_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient, "get_tensorboard"
    ) as get_tensorboard_mock:
        get_tensorboard_mock.return_value = tensorboard.Tensorboard(
            name=test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME,
            display_name=test_constants.TensorboardConstants._TEST_DISPLAY_NAME,
            encryption_spec=test_constants.ProjectConstants._TEST_ENCRYPTION_SPEC,
        )
        yield get_tensorboard_mock


@pytest.fixture
def create_tensorboard_experiment_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "create_tensorboard_experiment",
    ) as create_tensorboard_experiment_mock:
        create_tensorboard_experiment_mock.return_value = (
            test_constants.TensorboardConstants._TEST_TENSORBOARD_EXPERIMENT
        )
        yield create_tensorboard_experiment_mock


@pytest.fixture
def create_tensorboard_run_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "create_tensorboard_run",
    ) as create_tensorboard_run_mock:
        create_tensorboard_run_mock.return_value = (
            test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN
        )
        yield create_tensorboard_run_mock


@pytest.fixture
def write_tensorboard_run_data_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "write_tensorboard_run_data",
    ) as write_tensorboard_run_data_mock:
        yield write_tensorboard_run_data_mock


@pytest.fixture
def create_tensorboard_time_series_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "create_tensorboard_time_series",
    ) as create_tensorboard_time_series_mock:
        create_tensorboard_time_series_mock.return_value = (
            test_constants.TensorboardConstants._TEST_TENSORBOARD_TIME_SERIES
        )
        yield create_tensorboard_time_series_mock


@pytest.fixture
def get_tensorboard_run_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "get_tensorboard_run",
    ) as get_tensorboard_run_mock:
        get_tensorboard_run_mock.return_value = (
            test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN
        )
        yield get_tensorboard_run_mock


@pytest.fixture
def list_tensorboard_time_series_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "list_tensorboard_time_series",
    ) as list_tensorboard_time_series_mock:
        list_tensorboard_time_series_mock.return_value = [
            test_constants.TensorboardConstants._TEST_TENSORBOARD_TIME_SERIES
        ]
        yield list_tensorboard_time_series_mock


@pytest.fixture
def batch_read_tensorboard_time_series_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "batch_read_tensorboard_time_series_data",
    ) as batch_read_tensorboard_time_series_data_mock:
        batch_read_tensorboard_time_series_data_mock.return_value = tensorboard_service.BatchReadTensorboardTimeSeriesDataResponse(
            time_series_data=[
                test_constants.TensorboardConstants._TEST_TENSORBOARD_TIME_SERIES_DATA
            ]
        )
        yield batch_read_tensorboard_time_series_data_mock


# Endpoint mocks
@pytest.fixture
def create_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "create_endpoint"
    ) as create_endpoint_mock:
        create_endpoint_lro_mock = mock.Mock(operation.Operation)
        create_endpoint_lro_mock.result.return_value = endpoint.Endpoint(
            name=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
            display_name=test_constants.EndpointConstants._TEST_DISPLAY_NAME,
            encryption_spec=test_constants.ProjectConstants._TEST_ENCRYPTION_SPEC,
        )
        create_endpoint_mock.return_value = create_endpoint_lro_mock
        yield create_endpoint_mock


@pytest.fixture
def get_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = endpoint.Endpoint(
            display_name=test_constants.EndpointConstants._TEST_DISPLAY_NAME,
            name=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
            encryption_spec=test_constants.ProjectConstants._TEST_ENCRYPTION_SPEC,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_endpoint_with_models_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = endpoint.Endpoint(
            display_name=test_constants.EndpointConstants._TEST_DISPLAY_NAME,
            name=test_constants.EndpointConstants._TEST_ENDPOINT_NAME,
            deployed_models=test_constants.EndpointConstants._TEST_DEPLOYED_MODELS,
            traffic_split=test_constants.EndpointConstants._TEST_TRAFFIC_SPLIT,
        )
        yield get_endpoint_mock


@pytest.fixture
def predict_client_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "predict"
    ) as predict_mock:
        predict_mock.return_value = prediction_service.PredictResponse(
            deployed_model_id=test_constants.EndpointConstants._TEST_MODEL_ID,
            model_version_id=test_constants.EndpointConstants._TEST_VERSION_ID,
            model=test_constants.EndpointConstants._TEST_MODEL_NAME,
        )
        predict_mock.return_value.predictions.extend(
            test_constants.EndpointConstants._TEST_PREDICTION
        )
        yield predict_mock


# PipelineJob fixtures
def make_pipeline_job(state):
    return pipeline_job.PipelineJob(
        name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_NAME,
        state=state,
        create_time=test_constants.PipelineJobConstants._TEST_PIPELINE_CREATE_TIME,
        service_account=test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT,
        network=test_constants.TrainingJobConstants._TEST_NETWORK,
        job_detail=pipeline_job.PipelineJobDetail(
            pipeline_run_context=context.Context(
                name=test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_NAME,
            )
        ),
    )


@pytest.fixture
def get_pipeline_job_mock():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_pipeline_job"
    ) as mock_get_pipeline_job:
        mock_get_pipeline_job.side_effect = [
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_RUNNING),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_pipeline_job(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
        ]

        yield mock_get_pipeline_job


# Dataset mocks
@pytest.fixture
def create_dataset_mock():
    with mock.patch.object(
        dataset_service_client.DatasetServiceClient, "create_dataset"
    ) as create_dataset_mock:
        create_dataset_lro_mock = mock.Mock(operation.Operation)
        create_dataset_lro_mock.result.return_value = dataset.Dataset(
            name=test_constants.DatasetConstants._TEST_NAME,
            display_name=test_constants.DatasetConstants._TEST_DISPLAY_NAME,
            metadata_schema_uri=test_constants.DatasetConstants._TEST_METADATA_SCHEMA_URI_TEXT,
            encryption_spec=test_constants.DatasetConstants._TEST_ENCRYPTION_SPEC,
        )
        create_dataset_mock.return_value = create_dataset_lro_mock
        yield create_dataset_mock


@pytest.fixture
def get_dataset_mock():
    with mock.patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = dataset.Dataset(
            display_name=test_constants.DatasetConstants._TEST_DISPLAY_NAME,
            metadata_schema_uri=test_constants.DatasetConstants._TEST_METADATA_SCHEMA_URI_NONTABULAR,
            name=test_constants.DatasetConstants._TEST_NAME,
            metadata=test_constants.DatasetConstants._TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=test_constants.DatasetConstants._TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def import_data_mock():
    with mock.patch.object(
        dataset_service_client.DatasetServiceClient, "import_data"
    ) as import_data_mock:
        import_data_mock.return_value = mock.Mock(operation.Operation)
        yield import_data_mock


# TrainingJob mocks
@pytest.fixture
def mock_model_service_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as mock_get_model:
        mock_get_model.return_value = model.Model(
            name=test_constants.TrainingJobConstants._TEST_MODEL_NAME
        )
        mock_get_model.return_value.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        mock_get_model.return_value.version_id = "1"
        yield mock_get_model


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = training_pipeline.TrainingPipeline(
            name=test_constants.TrainingJobConstants._TEST_PIPELINE_RESOURCE_NAME,
            state=pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            model_to_upload=model.Model(
                name=test_constants.TrainingJobConstants._TEST_MODEL_NAME
            ),
        )
        yield mock_create_training_pipeline


def make_training_pipeline(state, add_training_task_metadata=True):
    return training_pipeline.TrainingPipeline(
        name=test_constants.TrainingJobConstants._TEST_PIPELINE_RESOURCE_NAME,
        state=state,
        model_to_upload=model.Model(
            name=test_constants.TrainingJobConstants._TEST_MODEL_NAME
        ),
        training_task_inputs={
            "tensorboard": test_constants.TrainingJobConstants._TEST_TENSORBOARD_RESOURCE_NAME
        },
        training_task_metadata={
            "backingCustomJob": test_constants.TrainingJobConstants._TEST_CUSTOM_JOB_RESOURCE_NAME
        }
        if add_training_task_metadata
        else None,
    )


@pytest.fixture
def mock_pipeline_service_get(make_call=make_training_pipeline):
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.side_effect = [
            make_call(
                pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
                add_training_task_metadata=False,
            ),
            make_call(
                pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            ),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
            make_call(pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED),
        ]

        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_and_get_with_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = training_pipeline.TrainingPipeline(
            name=test_constants.TrainingJobConstants._TEST_PIPELINE_RESOURCE_NAME,
            state=pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
        )

        with mock.patch.object(
            pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
        ) as mock_get_training_pipeline:
            mock_get_training_pipeline.return_value = training_pipeline.TrainingPipeline(
                name=test_constants.TrainingJobConstants._TEST_PIPELINE_RESOURCE_NAME,
                state=pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
            )

            yield mock_create_training_pipeline, mock_get_training_pipeline


# Experiment fixtures
@pytest.fixture
def get_experiment_mock():
    with mock.patch.object(
        metadata_service_client_v1.MetadataServiceClient, "get_context"
    ) as get_context_mock:
        get_context_mock.return_value = (
            test_constants.ExperimentConstants._EXPERIMENT_MOCK
        )
        yield get_context_mock


@pytest.fixture
def get_metadata_store_mock():
    with mock.patch.object(
        metadata_service_client_v1.MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = metadata_store.MetadataStore(
            name=test_constants.ExperimentConstants._TEST_METADATASTORE,
        )
        yield get_metadata_store_mock


@pytest.fixture
def get_context_mock():
    with mock.patch.object(
        metadata_service_client_v1.MetadataServiceClient, "get_context"
    ) as get_context_mock:
        get_context_mock.return_value = context.Context(
            name=test_constants.ExperimentConstants._TEST_CONTEXT_NAME,
            display_name=test_constants.ExperimentConstants._TEST_EXPERIMENT,
            description=test_constants.ExperimentConstants._TEST_EXPERIMENT_DESCRIPTION,
            schema_title=metadata_constants.SYSTEM_EXPERIMENT,
            schema_version=metadata_constants.SCHEMA_VERSIONS[
                metadata_constants.SYSTEM_EXPERIMENT
            ],
            metadata=metadata_constants.EXPERIMENT_METADATA,
        )
        yield get_context_mock


@pytest.fixture
def add_context_children_mock():
    with mock.patch.object(
        metadata_service_client_v1.MetadataServiceClient, "add_context_children"
    ) as add_context_children_mock:
        yield add_context_children_mock
