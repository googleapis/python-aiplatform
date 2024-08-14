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

import importlib
import pytest
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs

from google.cloud.aiplatform.compat.services import (
    model_service_client,
    pipeline_service_client,
)

from google.cloud.aiplatform.compat.types import (
    dataset as gca_dataset,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
    encryption_spec as gca_encryption_spec,
)
from google.protobuf import json_format
from google.protobuf import struct_pb2
import constants as test_constants

_TEST_BUCKET_NAME = test_constants.TrainingJobConstants._TEST_BUCKET_NAME
_TEST_GCS_PATH_WITHOUT_BUCKET = (
    test_constants.TrainingJobConstants._TEST_GCS_PATH_WITHOUT_BUCKET
)
_TEST_GCS_PATH = test_constants.TrainingJobConstants._TEST_GCS_PATH
_TEST_GCS_PATH_WITH_TRAILING_SLASH = (
    test_constants.TrainingJobConstants._TEST_GCS_PATH_WITH_TRAILING_SLASH
)
_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT

_TEST_DATASET_DISPLAY_NAME = (
    test_constants.TrainingJobConstants._TEST_DATASET_DISPLAY_NAME
)
_TEST_DATASET_NAME = test_constants.TrainingJobConstants._TEST_DATASET_NAME
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME
_TEST_TRAINING_CONTAINER_IMAGE = (
    test_constants.TrainingJobConstants._TEST_TRAINING_CONTAINER_IMAGE
)
_TEST_METADATA_SCHEMA_URI_TIMESERIES = schema.dataset.metadata.time_series
_TEST_METADATA_SCHEMA_URI_NONTIMESERIES = schema.dataset.metadata.image

_TEST_TRAINING_COLUMN_TRANSFORMATIONS = [
    {"auto": {"column_name": "time"}},
    {"auto": {"column_name": "time_series_identifier"}},
    {"auto": {"column_name": "target"}},
    {"auto": {"column_name": "weight"}},
]
_TEST_TRAINING_TARGET_COLUMN = "target"
_TEST_TRAINING_TIME_COLUMN = "time"
_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN = "time_series_identifier"
_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS = []
_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS = []
_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS = []
_TEST_TRAINING_FORECAST_HORIZON = 10
_TEST_TRAINING_DATA_GRANULARITY_UNIT = "day"
_TEST_TRAINING_DATA_GRANULARITY_COUNT = 1
_TEST_TRAINING_CONTEXT_WINDOW = None
_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS = True
_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI = (
    "bq://path.to.table"
)
_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION = False
_TEST_TRAINING_QUANTILES = None
_TEST_TRAINING_VALIDATION_OPTIONS = None
_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS = 1000
_TEST_TRAINING_WEIGHT_COLUMN = "weight"
_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME = "minimize-rmse"
_TEST_ADDITIONAL_EXPERIMENTS = ["exp1", "exp2"]
_TEST_HIERARCHY_GROUP_COLUMNS = []
_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT = 1
_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT = None
_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT = None
_TEST_WINDOW_COLUMN = None
_TEST_WINDOW_STRIDE_LENGTH = 1
_TEST_WINDOW_MAX_COUNT = None
_TEST_TRAINING_HOLIDAY_REGIONS = ["GLOBAL"]
_TEST_ENABLE_PROBABILISTIC_INFERENCE = True
_TEST_ADDITIONAL_EXPERIMENTS_PROBABILISTIC_INFERENCE = [
    "exp1",
    "exp2",
    "enable_probabilistic_inference",
]
_TEST_TRAINING_TASK_INPUTS_DICT = {
    # required inputs
    "targetColumn": _TEST_TRAINING_TARGET_COLUMN,
    "timeColumn": _TEST_TRAINING_TIME_COLUMN,
    "timeSeriesIdentifierColumn": _TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
    "timeSeriesAttributeColumns": _TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
    "unavailableAtForecastColumns": _TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
    "availableAtForecastColumns": _TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
    "forecastHorizon": _TEST_TRAINING_FORECAST_HORIZON,
    "dataGranularity": {
        "unit": _TEST_TRAINING_DATA_GRANULARITY_UNIT,
        "quantity": _TEST_TRAINING_DATA_GRANULARITY_COUNT,
    },
    "transformations": _TEST_TRAINING_COLUMN_TRANSFORMATIONS,
    "trainBudgetMilliNodeHours": _TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
    # optional inputs
    "weightColumn": _TEST_TRAINING_WEIGHT_COLUMN,
    "contextWindow": _TEST_TRAINING_CONTEXT_WINDOW,
    "exportEvaluatedDataItemsConfig": {
        "destinationBigqueryUri": _TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
        "overrideExistingTable": _TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
    },
    "quantiles": _TEST_TRAINING_QUANTILES,
    "validationOptions": _TEST_TRAINING_VALIDATION_OPTIONS,
    "optimizationObjective": _TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
    "hierarchyConfig": {
        "groupColumns": _TEST_HIERARCHY_GROUP_COLUMNS,
        "groupTotalWeight": _TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
        "temporalTotalWeight": _TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
        "groupTemporalTotalWeight": _TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
    },
    "windowConfig": {
        "strideLength": _TEST_WINDOW_STRIDE_LENGTH,
    },
    "holidayRegions": _TEST_TRAINING_HOLIDAY_REGIONS,
}

_TEST_TRAINING_TASK_INPUTS_WITH_ADDITIONAL_EXPERIMENTS = json_format.ParseDict(
    {
        **_TEST_TRAINING_TASK_INPUTS_DICT,
        "additionalExperiments": _TEST_ADDITIONAL_EXPERIMENTS,
    },
    struct_pb2.Value(),
)

_TEST_TRAINING_TASK_INPUTS_WITH_PROBABILISTIC_INFERENCE = json_format.ParseDict(
    {
        **_TEST_TRAINING_TASK_INPUTS_DICT,
        "additionalExperiments": _TEST_ADDITIONAL_EXPERIMENTS,
        "enableProbabilisticInference": True,
    },
    struct_pb2.Value(),
)

_TEST_TRAINING_TASK_INPUTS = json_format.ParseDict(
    _TEST_TRAINING_TASK_INPUTS_DICT,
    struct_pb2.Value(),
)

_TEST_DATASET_NAME = test_constants.TrainingJobConstants._TEST_DATASET_NAME

_TEST_MODEL_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_MODEL_DISPLAY_NAME

_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS
_TEST_MODEL_LABELS = test_constants.TrainingJobConstants._TEST_MODEL_LABELS

_TEST_PREDEFINED_SPLIT_COLUMN_NAME = "split"

_TEST_MODEL_NAME = "projects/my-project/locations/us-central1/models/12345"

_TEST_PIPELINE_RESOURCE_NAME = (
    test_constants.TrainingJobConstants._TEST_PIPELINE_RESOURCE_NAME
)

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = (
    test_constants.TrainingJobConstants._TEST_DEFAULT_ENCRYPTION_KEY_NAME
)
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_FRACTION_SPLIT_TRAINING = 0.6
_TEST_FRACTION_SPLIT_VALIDATION = 0.2
_TEST_FRACTION_SPLIT_TEST = 0.2

_TEST_SPLIT_PREDEFINED_COLUMN_NAME = "split"
_TEST_SPLIT_TIMESTAMP_COLUMN_NAME = "timestamp"

_FORECASTING_JOB_MODEL_TYPES = [
    training_jobs.AutoMLForecastingTrainingJob,
    training_jobs.SequenceToSequencePlusForecastingTrainingJob,
    training_jobs.TemporalFusionTransformerForecastingTrainingJob,
    training_jobs.TimeSeriesDenseEncoderForecastingTrainingJob,
]


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
            )
        )
        yield mock_create_training_pipeline


@pytest.fixture
def mock_pipeline_service_get():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as mock_get_training_pipeline:
        mock_get_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
            name=_TEST_PIPELINE_RESOURCE_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
            training_task_metadata={
                "evaluatedDataItemsBigqueryUri": _TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI
            },
        )
        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_and_get_with_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
            )
        )

        with mock.patch.object(
            pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
        ) as mock_get_training_pipeline:
            mock_get_training_pipeline.return_value = (
                gca_training_pipeline.TrainingPipeline(
                    name=_TEST_PIPELINE_RESOURCE_NAME,
                    state=gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
                )
            )

            yield mock_create_training_pipeline, mock_get_training_pipeline


@pytest.fixture
def mock_model_service_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as mock_get_model:
        mock_get_model.return_value = gca_model.Model(name=_TEST_MODEL_NAME)
        yield mock_get_model


@pytest.fixture
def mock_dataset_time_series():
    ds = mock.MagicMock(datasets.TimeSeriesDataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TIMESERIES,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


@pytest.fixture
def mock_dataset_nontimeseries():
    ds = mock.MagicMock(datasets.ImageDataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTIMESERIES,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


@pytest.mark.usefixtures("google_auth_mock")
class TestForecastingTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            labels=_TEST_LABELS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            additional_experiments=_TEST_ADDITIONAL_EXPERIMENTS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_ADDITIONAL_EXPERIMENTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        assert job._gca_resource is mock_pipeline_service_get.return_value

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_call_pipeline_service_create_with_timeout(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            labels=_TEST_LABELS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            additional_experiments=_TEST_ADDITIONAL_EXPERIMENTS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=180.0,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_ADDITIONAL_EXPERIMENTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=180.0,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_call_pipeline_if_no_model_display_name_nor_model_labels(
        self,
        mock_pipeline_service_create,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            labels=_TEST_LABELS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_call_pipeline_if_set_additional_experiments(
        self,
        mock_pipeline_service_create,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        job._add_additional_experiments(_TEST_ADDITIONAL_EXPERIMENTS)

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_ADDITIONAL_EXPERIMENTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_model_service_get",
    )
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_called_twice_raises(
        self,
        mock_dataset_time_series,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_dataset_time_series,
                target_column=_TEST_TRAINING_TARGET_COLUMN,
                time_column=_TEST_TRAINING_TIME_COLUMN,
                time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
                unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
                available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
                forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
                data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
                data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
                time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
                context_window=_TEST_TRAINING_CONTEXT_WINDOW,
                budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
                export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
                export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
                export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
                quantiles=_TEST_TRAINING_QUANTILES,
                validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
                hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
                hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
                hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
                hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
                window_column=_TEST_WINDOW_COLUMN,
                window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
                window_max_count=_TEST_WINDOW_MAX_COUNT,
                sync=sync,
                holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_raises_if_pipeline_fails(
        self,
        mock_pipeline_service_create_and_get_with_fail,
        mock_dataset_time_series,
        sync,
        training_job,
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_dataset_time_series,
                target_column=_TEST_TRAINING_TARGET_COLUMN,
                time_column=_TEST_TRAINING_TIME_COLUMN,
                time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
                unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
                available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
                forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
                data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
                data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
                time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
                context_window=_TEST_TRAINING_CONTEXT_WINDOW,
                budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
                export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
                export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
                export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
                quantiles=_TEST_TRAINING_QUANTILES,
                validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
                hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
                hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
                hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
                hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
                window_column=_TEST_WINDOW_COLUMN,
                window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
                window_max_count=_TEST_WINDOW_MAX_COUNT,
                sync=sync,
                holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_raises_before_run_is_called(
        self,
        mock_pipeline_service_create,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        with pytest.raises(RuntimeError):
            job.get_model()

        with pytest.raises(RuntimeError):
            job.has_failed

        with pytest.raises(RuntimeError):
            job.state

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_splits_fraction(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an Forecasting training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction=_TEST_FRACTION_SPLIT_TEST,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_splits_timestamp(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        """Initiate aiplatform with encryption key name.

        Create and run an Forecasting training job, verify calls and
        return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            timestamp_split_column_name=_TEST_SPLIT_TIMESTAMP_COLUMN_NAME,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        true_split = gca_training_pipeline.TimestampSplit(
            training_fraction=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction=_TEST_FRACTION_SPLIT_TEST,
            key=_TEST_SPLIT_TIMESTAMP_COLUMN_NAME,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_split, dataset_id=mock_dataset_time_series.name
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_splits_predefined(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an Forecasting training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        true_split = gca_training_pipeline.PredefinedSplit(
            key=_TEST_SPLIT_PREDEFINED_COLUMN_NAME
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=true_split,
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_splits_default(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an Forecasting training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_call_pipeline_if_set_additional_experiments_probabilistic_inference(
        self,
        mock_pipeline_service_create,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        job._add_additional_experiments(
            _TEST_ADDITIONAL_EXPERIMENTS_PROBABILISTIC_INFERENCE
        )

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
        )

        if not sync:
            model_from_job.wait()

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_PROBABILISTIC_INFERENCE,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.parametrize("training_job", _FORECASTING_JOB_MODEL_TYPES)
    def test_run_call_pipeline_if_set_enable_probabilistic_inference(
        self,
        mock_pipeline_service_create,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
        training_job,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_job(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
        )

        job._add_additional_experiments(_TEST_ADDITIONAL_EXPERIMENTS)

        model_from_job = job.run(
            dataset=mock_dataset_time_series,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            hierarchy_group_columns=_TEST_HIERARCHY_GROUP_COLUMNS,
            hierarchy_group_total_weight=_TEST_HIERARCHY_GROUP_TOTAL_WEIGHT,
            hierarchy_temporal_total_weight=_TEST_HIERARCHY_TEMPORAL_TOTAL_WEIGHT,
            hierarchy_group_temporal_total_weight=_TEST_HIERARCHY_GROUP_TEMPORAL_TOTAL_WEIGHT,
            window_column=_TEST_WINDOW_COLUMN,
            window_stride_length=_TEST_WINDOW_STRIDE_LENGTH,
            window_max_count=_TEST_WINDOW_MAX_COUNT,
            sync=sync,
            create_request_timeout=None,
            holiday_regions=_TEST_TRAINING_HOLIDAY_REGIONS,
            enable_probabilistic_inference=_TEST_ENABLE_PROBABILISTIC_INFERENCE,
        )

        if not sync:
            model_from_job.wait()

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=training_job._training_task_definition,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_PROBABILISTIC_INFERENCE,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

    def test_automl_forecasting_with_no_transformations(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
    ):
        aiplatform.init(project=_TEST_PROJECT)
        job = training_jobs.AutoMLForecastingTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
        )
        mock_dataset_time_series.column_names = [
            "a",
            "b",
            _TEST_TRAINING_TARGET_COLUMN,
        ]
        job.run(
            dataset=mock_dataset_time_series,
            predefined_split_column_name=_TEST_PREDEFINED_SPLIT_COLUMN_NAME,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            time_column=_TEST_TRAINING_TIME_COLUMN,
            time_series_identifier_column=_TEST_TRAINING_TIME_SERIES_IDENTIFIER_COLUMN,
            unavailable_at_forecast_columns=_TEST_TRAINING_UNAVAILABLE_AT_FORECAST_COLUMNS,
            available_at_forecast_columns=_TEST_TRAINING_AVAILABLE_AT_FORECAST_COLUMNS,
            forecast_horizon=_TEST_TRAINING_FORECAST_HORIZON,
            data_granularity_unit=_TEST_TRAINING_DATA_GRANULARITY_UNIT,
            data_granularity_count=_TEST_TRAINING_DATA_GRANULARITY_COUNT,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
        )
        assert job._column_transformations == [
            {"auto": {"column_name": "a"}},
            {"auto": {"column_name": "b"}},
        ]
