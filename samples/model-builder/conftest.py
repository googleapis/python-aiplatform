# Copyright 2022 Google LLC
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
def mock_get_automl_forecasting_seq2seq_training_job(mock_forecasting_training_job):
    with patch.object(
        aiplatform, "SequenceToSequencePlusForecastingTrainingJob"
    ) as mock:
        mock.return_value = mock_forecasting_training_job
        yield mock


@pytest.fixture
def mock_run_automl_forecasting_seq2seq_training_job(mock_forecasting_training_job):
    with patch.object(mock_forecasting_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_get_automl_forecasting_tft_training_job(mock_forecasting_training_job):
    with patch.object(
        aiplatform, "TemporalFusionTransformerForecastingTrainingJob"
    ) as mock:
        mock.return_value = mock_forecasting_training_job
        yield mock


@pytest.fixture
def mock_run_automl_forecasting_tft_training_job(mock_forecasting_training_job):
    with patch.object(mock_forecasting_training_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_get_automl_forecasting_tide_training_job(mock_forecasting_training_job):
    with patch.object(
        aiplatform, "TimeSeriesDenseEncoderForecastingTrainingJob"
    ) as mock:
        mock.return_value = mock_forecasting_training_job
        yield mock


@pytest.fixture
def mock_run_automl_forecasting_tide_training_job(mock_forecasting_training_job):
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


@pytest.fixture
def mock_custom_job():
    mock = MagicMock(aiplatform.CustomJob)
    yield mock


@pytest.fixture
def mock_get_custom_job(mock_custom_job):
    with patch.object(aiplatform, "CustomJob") as mock:
        mock.return_value = mock_custom_job
        yield mock


@pytest.fixture
def mock_get_custom_job_from_local_script(mock_custom_job):
    with patch.object(aiplatform.CustomJob, "from_local_script") as mock:
        mock.return_value = mock_custom_job
        yield mock


@pytest.fixture
def mock_run_custom_job(mock_custom_job):
    with patch.object(mock_custom_job, "run") as mock:
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
Tensorboard Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_tensorboard():
    mock = MagicMock(aiplatform.Tensorboard)
    yield mock


@pytest.fixture
def mock_TensorBoard_uploaderTracker():
    mock = MagicMock(aiplatform.uploader_tracker)
    yield mock


@pytest.fixture
def mock_create_tensorboard(mock_tensorboard):
    with patch.object(aiplatform.Tensorboard, "create") as mock:
        mock.return_value = mock_tensorboard
        yield mock


@pytest.fixture
def mock_tensorboard_uploader_onetime():
    with patch.object(aiplatform, "upload_tb_log") as mock_tensorboard_uploader_onetime:
        mock_tensorboard_uploader_onetime.return_value = None
        yield mock_tensorboard_uploader_onetime


@pytest.fixture
def mock_tensorboard_uploader_start():
    with patch.object(
        aiplatform, "start_upload_tb_log"
    ) as mock_tensorboard_uploader_start:
        mock_tensorboard_uploader_start.return_value = None
        yield mock_tensorboard_uploader_start


@pytest.fixture
def mock_tensorboard_uploader_end():
    with patch.object(aiplatform, "end_upload_tb_log") as mock_tensorboard_uploader_end:
        mock_tensorboard_uploader_end.return_value = None
        yield mock_tensorboard_uploader_end


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


# ----------------------------------------------------------------------------
# Hyperparameter Tuning Job Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def mock_hyperparameter_tuning_job():
    mock = MagicMock(aiplatform.HyperparameterTuningJob)
    yield mock


@pytest.fixture
def mock_get_hyperparameter_tuning_job(mock_hyperparameter_tuning_job):
    with patch.object(aiplatform, "HyperparameterTuningJob") as mock:
        mock.return_value = mock_hyperparameter_tuning_job
        yield mock


@pytest.fixture
def mock_run_hyperparameter_tuning_job(mock_hyperparameter_tuning_job):
    with patch.object(mock_hyperparameter_tuning_job, "run") as mock:
        yield mock


@pytest.fixture
def mock_hyperparameter_tuning_job_get(mock_hyperparameter_tuning_job):
    with patch.object(
        aiplatform.HyperparameterTuningJob, "get"
    ) as mock_hyperparameter_tuning_job_get:
        mock_hyperparameter_tuning_job_get.return_value = mock_hyperparameter_tuning_job
        yield mock_hyperparameter_tuning_job_get


@pytest.fixture
def mock_hyperparameter_tuning_job_cancel(mock_hyperparameter_tuning_job):
    with patch.object(mock_hyperparameter_tuning_job, "cancel") as mock:
        yield mock


@pytest.fixture
def mock_hyperparameter_tuning_job_delete(mock_hyperparameter_tuning_job):
    with patch.object(mock_hyperparameter_tuning_job, "delete") as mock:
        yield mock


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


@pytest.fixture
def mock_write_feature_values(mock_entity_type):
    with patch.object(
        mock_entity_type, "write_feature_values"
    ) as mock_write_feature_values:
        yield mock_write_feature_values


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
    mock = MagicMock(aiplatform.Context)
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
def mock_classification_metrics():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_artifacts():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_experiment_models():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_model_info():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_ml_model():
    mock = MagicMock()
    yield mock


@pytest.fixture
def mock_experiment_model():
    mock = MagicMock(aiplatform.metadata.schema.google.artifact_schema.ExperimentModel)
    yield mock


@pytest.fixture
def mock_get_execution(mock_execution):
    with patch.object(aiplatform, "Execution") as mock_get_execution:
        mock_get_execution.return_value = mock_execution
        yield mock_get_execution


@pytest.fixture
def mock_execution_get(mock_execution):
    with patch.object(aiplatform.Execution, "get") as mock_execution_get:
        mock_execution_get.return_value = mock_execution
        yield mock_execution_get


@pytest.fixture
def mock_create_execution(mock_execution):
    with patch.object(aiplatform.Execution, "create") as mock_create_execution:
        mock_create_execution.return_value = mock_execution
        yield mock_create_execution


@pytest.fixture
def mock_list_execution(mock_execution):
    with patch.object(aiplatform.Execution, "list") as mock_list_execution:
        # Returning list of 2 executions to avoid confusion with get method
        # which returns one unique execution.
        mock_list_execution.return_value = [mock_execution, mock_execution]
        yield mock_list_execution


@pytest.fixture
def mock_get_artifact(mock_artifact):
    with patch.object(aiplatform, "Artifact") as mock_get_artifact:
        mock_get_artifact.return_value = mock_artifact
        yield mock_get_artifact


@pytest.fixture
def mock_context_get(mock_context):
    with patch.object(aiplatform.Context, "get") as mock_context_get:
        mock_context_get.return_value = mock_context
        yield mock_context_get


@pytest.fixture
def mock_context_list(mock_context):
    with patch.object(aiplatform.Context, "list") as mock_context_list:
        # Returning list of 2 contexts to avoid confusion with get method
        # which returns one unique context.
        mock_context_list.return_value = [mock_context, mock_context]
        yield mock_context_list


@pytest.fixture
def mock_create_schema_base_context(mock_context):
    with patch.object(
        aiplatform.metadata.schema.base_context.BaseContextSchema, "create"
    ) as mock_create_schema_base_context:
        mock_create_schema_base_context.return_value = mock_context
        yield mock_create_schema_base_context


@pytest.fixture
def mock_artifact_get(mock_artifact):
    with patch.object(aiplatform.Artifact, "get") as mock_artifact_get:
        mock_artifact_get.return_value = mock_artifact
        yield mock_artifact_get


@pytest.fixture
def mock_pipeline_job_create(mock_pipeline_job):
    with patch.object(aiplatform, "PipelineJob") as mock_pipeline_job_create:
        mock_pipeline_job_create.return_value = mock_pipeline_job
        yield mock_pipeline_job_create


@pytest.fixture
def mock_artifact_delete():
    with patch.object(aiplatform.Artifact, "delete") as mock_artifact_delete:
        mock_artifact_delete.return_value = None
        yield mock_artifact_delete


@pytest.fixture
def mock_execution_delete():
    with patch.object(aiplatform.Execution, "delete") as mock_execution_delete:
        mock_execution_delete.return_value = None
        yield mock_execution_delete


@pytest.fixture
def mock_context_delete():
    with patch.object(aiplatform.Context, "delete") as mock_context_delete:
        mock_context_delete.return_value = None
        yield mock_context_delete


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
def mock_create_schema_base_artifact(mock_artifact):
    with patch.object(
        aiplatform.metadata.schema.base_artifact.BaseArtifactSchema, "create"
    ) as mock_create_schema_base_artifact:
        mock_create_schema_base_artifact.return_value = mock_artifact
        yield mock_create_schema_base_artifact


@pytest.fixture
def mock_create_schema_base_execution(mock_execution):
    with patch.object(
        aiplatform.metadata.schema.base_execution.BaseExecutionSchema, "create"
    ) as mock_create_schema_base_execution:
        mock_create_schema_base_execution.return_value = mock_execution
        yield mock_create_schema_base_execution


@pytest.fixture
def mock_list_artifact(mock_artifact):
    with patch.object(aiplatform.Artifact, "list") as mock_list_artifact:
        # Returning list of 2 artifacts to avoid confusion with get method
        # which returns one unique artifact.
        mock_list_artifact.return_value = [mock_artifact, mock_artifact]
        yield mock_list_artifact


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
def mock_log_classification_metrics():
    with patch.object(aiplatform, "log_classification_metrics") as mock_log_metrics:
        mock_log_metrics.return_value = None
        yield mock_log_metrics


@pytest.fixture
def mock_log_model():
    with patch.object(aiplatform, "log_model") as mock_log_model:
        mock_log_model.return_value = None
        yield mock_log_model


@pytest.fixture
def mock_save_model():
    with patch.object(aiplatform, "save_model") as mock_save_model:
        mock_save_model.return_value = None
        yield mock_save_model


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


@pytest.fixture
def mock_get_classification_metrics(mock_classification_metrics, mock_experiment_run):
    with patch.object(
        mock_experiment_run, "get_classification_metrics"
    ) as mock_get_classification_metrics:
        mock_get_classification_metrics.return_value = mock_classification_metrics
        yield mock_get_classification_metrics


@pytest.fixture
def mock_get_artifacts(mock_artifacts, mock_experiment_run):
    with patch.object(mock_experiment_run, "get_artifacts") as mock_get_artifacts:
        mock_get_artifacts.return_value = mock_artifacts
        yield mock_get_artifacts


@pytest.fixture
def mock_get_experiment_models(mock_experiment_models, mock_experiment_run):
    with patch.object(
        mock_experiment_run, "get_experiment_models"
    ) as mock_get_experiment_models:
        mock_get_experiment_models.return_value = mock_experiment_models
        yield mock_get_experiment_models


@pytest.fixture
def mock_get_experiment_model(mock_experiment_model):
    with patch.object(aiplatform, "get_experiment_model") as mock_get_experiment_model:
        mock_get_experiment_model.return_value = mock_experiment_model
        yield mock_get_experiment_model


@pytest.fixture
def mock_get_model_info(mock_experiment_model, mock_model_info):
    with patch.object(mock_experiment_model, "get_model_info") as mock_get_model_info:
        mock_get_model_info.return_value = mock_model_info
        yield mock_get_model_info


@pytest.fixture
def mock_load_model(mock_experiment_model, mock_ml_model):
    with patch.object(mock_experiment_model, "load_model") as mock_load_model:
        mock_load_model.return_value = mock_ml_model
        yield mock_load_model


@pytest.fixture
def mock_register_model(mock_experiment_model, mock_model):
    with patch.object(mock_experiment_model, "register_model") as mock_register_model:
        mock_register_model.return_value = mock_model
        yield mock_register_model


@pytest.fixture
def mock_update_run_state(mock_experiment_run):
    with patch.object(mock_experiment_run, "update_state") as mock_update_run_state:
        mock_update_run_state.return_value = None
        yield mock_update_run_state


"""
----------------------------------------------------------------------------
Model Versioning Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_model_registry():
    mock = MagicMock(aiplatform.models.ModelRegistry)
    yield mock


@pytest.fixture
def mock_version_info():
    mock = MagicMock(aiplatform.models.VersionInfo)
    yield mock


@pytest.fixture
def mock_init_model_registry(mock_model_registry):
    with patch.object(aiplatform.models, "ModelRegistry") as mock:
        mock.return_value = mock_model_registry
        yield mock


@pytest.fixture
def mock_get_model(mock_model_registry):
    with patch.object(mock_model_registry, "get_model") as mock_get_model:
        mock_get_model.return_value = mock_model
        yield mock_get_model


@pytest.fixture
def mock_get_model_version_info(mock_model_registry):
    with patch.object(
        mock_model_registry, "get_version_info"
    ) as mock_get_model_version_info:
        mock_get_model_version_info.return_value = mock_version_info
        yield mock_get_model_version_info


@pytest.fixture
def mock_list_versions(mock_model_registry, mock_version_info):
    with patch.object(mock_model_registry, "list_versions") as mock_list_versions:
        mock_list_versions.return_value = [mock_version_info, mock_version_info]
        yield mock_list_versions


@pytest.fixture
def mock_delete_version(mock_model_registry):
    with patch.object(mock_model_registry, "delete_version") as mock_delete_version:
        mock_delete_version.return_value = None
        yield mock_delete_version


@pytest.fixture
def mock_add_version_aliases(mock_model_registry):
    with patch.object(
        mock_model_registry, "add_version_aliases"
    ) as mock_add_version_aliases:
        mock_add_version_aliases.return_value = None
        yield mock_add_version_aliases


@pytest.fixture
def mock_remove_version_aliases(mock_model_registry):
    with patch.object(
        mock_model_registry, "remove_version_aliases"
    ) as mock_remove_version_aliases:
        mock_remove_version_aliases.return_value = None
        yield mock_remove_version_aliases


"""
----------------------------------------------------------------------------
Autologging Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def mock_autolog():
    with patch.object(aiplatform, "autolog") as mock_autolog_method:
        mock_autolog_method.return_value = None
        yield mock_autolog_method
