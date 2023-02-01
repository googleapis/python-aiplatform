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

from google.cloud.aiplatform.utils import source_utils
import constants as test_constants
from google.cloud.aiplatform.compat.services import (
    model_service_client,
    tensorboard_service_client,
    pipeline_service_client,
)

from google.cloud.aiplatform.compat.types import (
    context,
    endpoint,
    model,
    model_service,
    pipeline_job,
    pipeline_state,
    tensorboard,
    tensorboard_service,
)


from google.cloud.aiplatform.compat.services import endpoint_service_client


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
