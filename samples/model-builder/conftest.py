# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from unittest.mock import MagicMock, patch

from google.cloud import aiplatform
import pytest


@pytest.fixture
def mock_sdk_init():
    with patch.object(aiplatform, "init") as mock:
        yield mock


"""
----------------------------------------------------------------------------
Dataset Fixtures
----------------------------------------------------------------------------
"""

"""Dataset objects returned by SomeDataset(), create(), import_data(), etc. """


@pytest.fixture
def mock_image_dataset():
    mock = MagicMock(aiplatform.datasets.ImageDataset)
    yield mock


@pytest.fixture
def mock_tabular_dataset():
    mock = MagicMock(aiplatform.datasets.TabularDataset)
    yield mock


@pytest.fixture
def mock_time_series_dataset():
    mock = MagicMock(aiplatform.datasets.TimeSeriesDataset)
    yield mock


@pytest.fixture
def mock_text_dataset():
    mock = MagicMock(aiplatform.datasets.TextDataset)
    yield mock


@pytest.fixture
def mock_video_dataset():
    mock = MagicMock(aiplatform.datasets.VideoDataset)
    yield mock


"""Mocks for getting an existing Dataset, i.e. ds = aiplatform.ImageDataset(...) """


@pytest.fixture
def mock_get_image_dataset(mock_image_dataset):
    with patch.object(aiplatform, "ImageDataset") as mock_get_image_dataset:
        mock_get_image_dataset.return_value = mock_image_dataset
        yield mock_get_image_dataset


@pytest.fixture
def mock_get_tabular_dataset(mock_tabular_dataset):
    with patch.object(aiplatform, "TabularDataset") as mock_get_tabular_dataset:
        mock_get_tabular_dataset.return_value = mock_tabular_dataset
        yield mock_get_tabular_dataset


@pytest.fixture
def mock_get_time_series_dataset(mock_time_series_dataset):
    with patch.object(aiplatform, "TimeSeriesDataset") as mock_get_time_series_dataset:
        mock_get_time_series_dataset.return_value = mock_time_series_dataset
        yield mock_get_time_series_dataset


@pytest.fixture
def mock_get_text_dataset(mock_text_dataset):
    with patch.object(aiplatform, "TextDataset") as mock_get_text_dataset:
        mock_get_text_dataset.return_value = mock_text_dataset
        yield mock_get_text_dataset


@pytest.fixture
def mock_get_video_dataset(mock_video_dataset):
    with patch.object(aiplatform, "VideoDataset") as mock_get_video_dataset:
        mock_get_video_dataset.return_value = mock_video_dataset
        yield mock_get_video_dataset


"""Mocks for creating a new Dataset, i.e. aiplatform.ImageDataset.create(...) """


@pytest.fixture
def mock_create_image_dataset(mock_image_dataset):
    with patch.object(aiplatform.ImageDataset, "create") as mock_create_image_dataset:
        mock_create_image_dataset.return_value = mock_image_dataset
        yield mock_create_image_dataset


@pytest.fixture
def mock_create_tabular_dataset(mock_tabular_dataset):
    with patch.object(
        aiplatform.TabularDataset, "create"
    ) as mock_create_tabular_dataset:
        mock_create_tabular_dataset.return_value = mock_tabular_dataset
        yield mock_create_tabular_dataset


@pytest.fixture
def mock_create_time_series_dataset(mock_time_series_dataset):
    with patch.object(
        aiplatform.TimeSeriesDataset, "create"
    ) as mock_create_time_series_dataset:
        mock_create_time_series_dataset.return_value = mock_time_series_dataset
        yield mock_create_time_series_dataset


@pytest.fixture
def mock_create_text_dataset(mock_text_dataset):
    with patch.object(aiplatform.TextDataset, "create") as mock_create_text_dataset:
        mock_create_text_dataset.return_value = mock_text_dataset
        yield mock_create_text_dataset


@pytest.fixture
def mock_create_video_dataset(mock_video_dataset):
    with patch.object(aiplatform.VideoDataset, "create") as mock_create_video_dataset:
        mock_create_video_dataset.return_value = mock_video_dataset
        yield mock_create_video_dataset


"""Mocks for SomeDataset.import_data() """


@pytest.fixture
def mock_import_image_dataset(mock_image_dataset):
    with patch.object(mock_image_dataset, "import_data") as mock:
        yield mock


@pytest.fixture
def mock_import_tabular_dataset(mock_tabular_dataset):
    with patch.object(mock_tabular_dataset, "import_data") as mock:
        yield mock


@pytest.fixture
def mock_import_text_dataset(mock_text_dataset):
    with patch.object(mock_text_dataset, "import_data") as mock:
        yield mock


@pytest.fixture
def mock_import_video_data(mock_video_dataset):
    with patch.object(mock_video_dataset, "import_data") as mock:
        yield mock


# ----------------------------------------------------------------------------
# TrainingJob Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def mock_custom_training_job():
    mock = MagicMock(aiplatform.training_jobs.CustomTrainingJob)
    yield mock


@pytest.fixture
def mock_custom_container_training_job():
    mock = MagicMock(aiplatform.training_jobs.CustomContainerTrainingJob)
    yield mock


@pytest.fixture
def mock_custom_package_training_job():
    mock = MagicMock(aiplatform.training_jobs.CustomPythonPackageTrainingJob)
    yield mock


@pytest.fixture
def mock_image_training_job():
    mock = MagicMock(aiplatform.training_jobs.AutoMLImageTrainingJob)
    yield mock


@pytest.fixture
def mock_tabular_training_job():
    mock = MagicMock(aiplatform.training_jobs.AutoMLTabularTrainingJob)
    yield mock


@pytest.fixture
def mock_forecasting_training_job():
    mock = MagicMock(aiplatform.training_jobs.AutoMLForecastingTrainingJob)
    yield mock


@pytest.fixture
def mock_text_training_job():
    mock = MagicMock(aiplatform.training_jobs.AutoMLTextTrainingJob)
    yield mock


@pytest.fixture
def mock_video_training_job():
    mock = MagicMock(aiplatform.training_jobs.AutoMLVideoTrainingJob)
    yield mock


@pytest.fixture
def mock_get_automl_tabular_training_job(mock_tabular_training_job):
    with patch.object(aiplatform, "AutoMLTabularTrainingJob") as mock:
        mock.return_value = mock_tabular_training_job
        yield mock


@pytest.fixture
def mock_run_automl_tabular_training_job(mock_tabular_training_job):
    with patch.object(mock_tabular_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_get_automl_forecasting_training_job(mock_forecasting_training_job):
    with patch.object(aiplatform, "AutoMLForecastingTrainingJob") as mock:
        mock.return_value = mock_forecasting_training_job
        yield mock


@pytest.fixture
def mock_run_automl_forecasting_training_job(mock_forecasting_training_job):
    with patch.object(mock_forecasting_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_get_automl_image_training_job(mock_image_training_job):
    with patch.object(aiplatform, "AutoMLImageTrainingJob") as mock:
        mock.return_value = mock_image_training_job
        yield mock


@pytest.fixture
def mock_run_automl_image_training_job(mock_image_training_job):
    with patch.object(mock_image_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_get_automl_text_training_job(mock_text_training_job):
    with patch.object(aiplatform, "AutoMLTextTrainingJob") as mock:
        mock.return_value = mock_text_training_job
        yield mock


@pytest.fixture
def mock_run_automl_text_training_job(mock_text_training_job):
    with patch.object(mock_text_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_get_custom_training_job(mock_custom_training_job):
    with patch.object(aiplatform, "CustomTrainingJob") as mock:
        mock.return_value = mock_custom_training_job
        yield mock


@pytest.fixture
def mock_get_custom_container_training_job(mock_custom_container_training_job):
    with patch.object(aiplatform, "CustomContainerTrainingJob") as mock:
        mock.return_value = mock_custom_container_training_job
        yield mock


@pytest.fixture
def mock_get_custom_package_training_job(mock_custom_package_training_job):
    with patch.object(aiplatform, "CustomPythonPackageTrainingJob") as mock:
        mock.return_value = mock_custom_package_training_job
        yield mock


@pytest.fixture
def mock_run_custom_training_job(mock_custom_training_job):
    with patch.object(mock_custom_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_run_custom_container_training_job(mock_custom_container_training_job):
    with patch.object(mock_custom_container_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_run_custom_package_training_job(mock_custom_package_training_job):
    with patch.object(mock_custom_package_training_job, "run") as mock:
        yield mock


"""
----------------------------------------------------------------------------
Model Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_model():
    mock = MagicMock(aiplatform.models.Model)
    yield mock


@pytest.fixture
def mock_init_model(mock_model):
    with patch.object(aiplatform, "Model") as mock:
        mock.return_value = mock_model
        yield mock


@pytest.fixture
def mock_batch_predict_model(mock_model):
    with patch.object(mock_model, "batch_predict") as mock:
        yield mock


@pytest.fixture
def mock_upload_model(mock_model):
    with patch.object(aiplatform.Model, "upload") as mock:
        mock.return_value = mock_model
        yield mock


@pytest.fixture
def mock_deploy_model(mock_model, mock_endpoint):
    with patch.object(mock_model, "deploy") as mock:
        mock.return_value = mock_endpoint
        yield mock


"""
----------------------------------------------------------------------------
Job Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_create_batch_prediction_job():
    with patch.object(aiplatform.jobs.BatchPredictionJob, "create") as mock:
        yield mock


"""
----------------------------------------------------------------------------
Endpoint Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_endpoint():
    mock = MagicMock(aiplatform.models.Endpoint)
    yield mock


@pytest.fixture
def mock_create_endpoint():
    with patch.object(aiplatform.models.Endpoint, "create") as mock:
        yield mock


@pytest.fixture
def mock_get_endpoint(mock_endpoint):
    with patch.object(aiplatform, "Endpoint") as mock_get_endpoint:
        mock_get_endpoint.return_value = mock_endpoint
        yield mock_get_endpoint


@pytest.fixture
def mock_endpoint_predict(mock_endpoint):
    with patch.object(mock_endpoint, "predict") as mock:
        mock.return_value = []
        yield mock


@pytest.fixture
def mock_endpoint_explain(mock_endpoint):
    with patch.object(mock_endpoint, "explain") as mock_endpoint_explain:
        mock_get_endpoint.return_value = mock_endpoint
        yield mock_endpoint_explain


"""
----------------------------------------------------------------------------
Feature Store Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_featurestore():
    mock = MagicMock(aiplatform.featurestore.Featurestore)
    yield mock


@pytest.fixture
def mock_entity_type():
    mock = MagicMock(aiplatform.featurestore.EntityType)
    yield mock


@pytest.fixture
def mock_feature():
    mock = MagicMock(aiplatform.featurestore.Feature)
    yield mock


@pytest.fixture
def mock_get_featurestore(mock_featurestore):
    with patch.object(aiplatform.featurestore, "Featurestore") as mock_get_featurestore:
        mock_get_featurestore.return_value = mock_featurestore
        yield mock_get_featurestore


@pytest.fixture
def mock_get_entity_type(mock_entity_type):
    with patch.object(aiplatform.featurestore, "EntityType") as mock_get_entity_type:
        mock_get_entity_type.return_value = mock_entity_type
        yield mock_get_entity_type


@pytest.fixture
def mock_create_featurestore(mock_featurestore):
    with patch.object(
        aiplatform.featurestore.Featurestore, "create"
    ) as mock_create_featurestore:
        mock_create_featurestore.return_value = mock_featurestore
        yield mock_create_featurestore


@pytest.fixture
def mock_create_entity_type(mock_entity_type):
    with patch.object(
        aiplatform.featurestore.EntityType, "create"
    ) as mock_create_entity_type:
        mock_create_entity_type.return_value = mock_entity_type
        yield mock_create_entity_type


@pytest.fixture
def mock_create_feature(mock_feature):
    with patch.object(aiplatform.featurestore.Feature, "create") as mock_create_feature:
        mock_create_feature.return_value = mock_feature
        yield mock_create_feature


@pytest.fixture
def mock_delete_featurestore(mock_featurestore):
    with patch.object(mock_featurestore, "delete") as mock_delete_featurestore:
        yield mock_delete_featurestore


@pytest.fixture
def mock_batch_serve_to_bq(mock_featurestore):
    with patch.object(mock_featurestore, "batch_serve_to_bq") as mock_batch_serve_to_bq:
        yield mock_batch_serve_to_bq


@pytest.fixture
def mock_batch_create_features(mock_entity_type):
    with patch.object(
        mock_entity_type, "batch_create_features"
    ) as mock_batch_create_features:
        yield mock_batch_create_features


@pytest.fixture
def mock_read_feature_values(mock_entity_type):
    with patch.object(mock_entity_type, "read") as mock_read_feature_values:
        yield mock_read_feature_values


@pytest.fixture
def mock_import_feature_values(mock_entity_type):
    with patch.object(
        mock_entity_type, "ingest_from_gcs"
    ) as mock_import_feature_values:
        yield mock_import_feature_values


"""
----------------------------------------------------------------------------
Experiment Tracking Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_execution():
    mock = MagicMock(aiplatform.Execution)
    mock.assign_input_artifacts.return_value = None
    mock.assign_output_artifacts.return_value = None
    mock.__enter__.return_value = mock
    yield mock


@pytest.fixture
def mock_artifact():
    mock = MagicMock(aiplatform.Artifact)
    yield mock


@pytest.fixture
def mock_context():
    mock = MagicMock(aiplatform.metadata.context.Context)
    yield mock


@pytest.fixture
def mock_experiment():
    mock = MagicMock(aiplatform.Experiment)
    yield mock


@pytest.fixture
def mock_experiment_run():
    mock = MagicMock(aiplatform.ExperimentRun)
    yield mock


@pytest.fixture
def mock_pipeline_job():
    mock = MagicMock(aiplatform.PipelineJob)
    yield mock


@pytest.fixture
def mock_df():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_metrics():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_params():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_time_series_metrics():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_get_execution(mock_execution):
    with patch.object(aiplatform, "Execution") as mock_get_execution:
        mock_get_execution.return_value = mock_execution
        yield mock_get_execution


@pytest.fixture
def mock_create_execution(mock_execution):
    with patch.object(aiplatform.Execution, "create") as mock_create_execution:
        mock_create_execution.return_value = mock_execution
        yield mock_create_execution


@pytest.fixture
def mock_get_artifact(mock_artifact):
    with patch.object(aiplatform, "Artifact") as mock_get_artifact:
        mock_get_artifact.return_value = mock_artifact
        yield mock_get_artifact


@pytest.fixture
def mock_context_get(mock_context):
    with patch.object(aiplatform.metadata.context.Context, "get") as mock_context_get:
        mock_context_get.return_value = mock_context
        yield mock_context_get


@pytest.fixture
def mock_context_list(mock_context):
    with patch.object(aiplatform.metadata.context.Context, "list") as mock_context_list:
        # Returning list of 2 contexts to avoid confusion with get method
        # which returns one unique context.
        mock_context_list.return_value = [mock_context, mock_context]
        yield mock_context_list


@pytest.fixture
def mock_create_context(mock_context):
    with patch.object(
        aiplatform.metadata.context.Context, "create"
    ) as mock_create_context:
        mock_create_context.return_value = mock_context
        yield mock_create_context


@pytest.fixture
def mock_pipeline_job_create(mock_pipeline_job):
    with patch.object(aiplatform, "PipelineJob") as mock_pipeline_job_create:
        mock_pipeline_job_create.return_value = mock_pipeline_job
        yield mock_pipeline_job_create


@pytest.fixture
def mock_pipeline_job_submit(mock_pipeline_job):
    with patch.object(mock_pipeline_job, "submit") as mock_pipeline_job_submit:
        mock_pipeline_job_submit.return_value = None
        yield mock_pipeline_job_submit


@pytest.fixture
def mock_create_artifact(mock_artifact):
    with patch.object(aiplatform.Artifact, "create") as mock_create_artifact:
        mock_create_artifact.return_value = mock_artifact
        yield mock_create_artifact


@pytest.fixture
def mock_start_run(mock_experiment_run):
    with patch.object(aiplatform, "start_run") as mock_start_run:
        mock_start_run.return_value = mock_experiment_run
        yield mock_start_run


@pytest.fixture
def mock_start_execution(mock_execution):
    with patch.object(aiplatform, "start_execution") as mock_start_execution:
        mock_start_execution.return_value = mock_execution
        yield mock_start_execution


@pytest.fixture
def mock_end_run():
    with patch.object(aiplatform, "end_run") as mock_end_run:
        mock_end_run.return_value = None
        yield mock_end_run


@pytest.fixture
def mock_log_metrics():
    with patch.object(aiplatform, "log_metrics") as mock_log_metrics:
        mock_log_metrics.return_value = None
        yield mock_log_metrics


@pytest.fixture
def mock_log_time_series_metrics():
    with patch.object(
        aiplatform, "log_time_series_metrics"
    ) as mock_log_time_series_metrics:
        mock_log_time_series_metrics.return_value = None
        yield mock_log_time_series_metrics


@pytest.fixture
def mock_log_params():
    with patch.object(aiplatform, "log_params") as mock_log_params:
        mock_log_params.return_value = None
        yield mock_log_params


@pytest.fixture
def mock_log_pipeline_job():
    with patch.object(aiplatform, "log") as mock_log_pipeline_job:
        mock_log_pipeline_job.return_value = None
        yield mock_log_pipeline_job


@pytest.fixture
def mock_get_run(mock_experiment_run):
    with patch.object(aiplatform, "ExperimentRun") as mock_get_run:
        mock_get_run.return_value = mock_experiment_run
        yield mock_get_run


@pytest.fixture
def mock_get_experiment(mock_experiment):
    with patch.object(aiplatform, "Experiment") as mock_get_experiment:
        mock_get_experiment.return_value = mock_experiment
        yield mock_get_experiment


@pytest.fixture
def mock_get_with_uri(mock_artifact):
    with patch.object(aiplatform.Artifact, "get_with_uri") as mock_get_with_uri:
        mock_get_with_uri.return_value = mock_artifact
        yield mock_get_with_uri


@pytest.fixture
def mock_get_experiment_df(mock_df):
    with patch.object(aiplatform, "get_experiment_df") as mock_get_experiment_df:
        mock_get_experiment_df.return_value = mock_df
        yield mock_get_experiment_df


@pytest.fixture
def mock_get_metrics(mock_metrics, mock_experiment_run):
    with patch.object(mock_experiment_run, "get_metrics") as mock_get_metrics:
        mock_get_metrics.return_value = mock_metrics
        yield mock_get_metrics


@pytest.fixture
def mock_get_params(mock_params, mock_experiment_run):
    with patch.object(mock_experiment_run, "get_params") as mock_get_params:
        mock_get_params.return_value = mock_params
        yield mock_get_params


@pytest.fixture
def mock_get_time_series_metrics(mock_time_series_metrics, mock_experiment_run):
    with patch.object(
        mock_experiment_run, "get_time_series_data_frame"
    ) as mock_get_time_series_metrics:
        mock_get_time_series_metrics.return_value = mock_time_series_metrics
        yield mock_get_time_series_metrics
