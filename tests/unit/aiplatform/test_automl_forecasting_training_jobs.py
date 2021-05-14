import importlib
import pytest
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform.training_jobs import AutoMLForecastingTrainingJob

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform_v1.services.pipeline_service import (
    client as pipeline_service_client,
)
from google.cloud.aiplatform_v1.types import (
    dataset as gca_dataset,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
)
from google.protobuf import json_format
from google.protobuf import struct_pb2

_TEST_BUCKET_NAME = "test-bucket"
_TEST_GCS_PATH_WITHOUT_BUCKET = "path/to/folder"
_TEST_GCS_PATH = f"{_TEST_BUCKET_NAME}/{_TEST_GCS_PATH_WITHOUT_BUCKET}"
_TEST_GCS_PATH_WITH_TRAILING_SLASH = f"{_TEST_GCS_PATH}/"
_TEST_PROJECT = "test-project"

_TEST_DATASET_DISPLAY_NAME = "test-dataset-display-name"
_TEST_DATASET_NAME = "test-dataset-name"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_TRAINING_CONTAINER_IMAGE = "gcr.io/test-training/container:image"
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
_TEST_TRAINING_TASK_INPUTS = json_format.ParseDict(
    {
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
    },
    struct_pb2.Value(),
)

_TEST_DATASET_NAME = "test-dataset-name"

_TEST_MODEL_DISPLAY_NAME = "model-display-name"
_TEST_TRAINING_FRACTION_SPLIT = 0.8
_TEST_VALIDATION_FRACTION_SPLIT = 0.1
_TEST_TEST_FRACTION_SPLIT = 0.1
_TEST_PREDEFINED_SPLIT_COLUMN_NAME = "split"

_TEST_OUTPUT_PYTHON_PACKAGE_PATH = "gs://test/ouput/python/trainer.tar.gz"

_TEST_MODEL_NAME = "projects/my-project/locations/us-central1/models/12345"

_TEST_PIPELINE_RESOURCE_NAME = (
    "projects/my-project/locations/us-central1/trainingPipeline/12345"
)


@pytest.fixture
def mock_pipeline_service_create():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
            name=_TEST_PIPELINE_RESOURCE_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
            model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
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
        )
        yield mock_get_training_pipeline


@pytest.fixture
def mock_pipeline_service_create_and_get_with_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
            name=_TEST_PIPELINE_RESOURCE_NAME,
            state=gca_pipeline_state.PipelineState.PIPELINE_STATE_RUNNING,
        )

        with mock.patch.object(
            pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
        ) as mock_get_training_pipeline:
            mock_get_training_pipeline.return_value = gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_FAILED,
            )

            yield mock_create_training_pipeline, mock_get_training_pipeline


@pytest.fixture
def mock_model_service_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as mock_get_model:
        mock_get_model.return_value = gca_model.Model()
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


class TestAutoMLForecastingTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = AutoMLForecastingTrainingJob(
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
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        true_managed_model = gca_model.Model(display_name=_TEST_MODEL_DISPLAY_NAME)

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            predefined_split=gca_training_pipeline.PredefinedSplit(
                key=_TEST_PREDEFINED_SPLIT_COLUMN_NAME
            ),
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_forecasting,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

        assert job._gca_resource is mock_pipeline_service_get.return_value

        mock_model_service_get.assert_called_once_with(name=_TEST_MODEL_NAME)

        assert model_from_job._gca_resource is mock_model_service_get.return_value

        assert job.get_model()._gca_resource is mock_model_service_get.return_value

        assert not job.has_failed

        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_if_no_model_display_name(
        self,
        mock_pipeline_service_create,
        mock_dataset_time_series,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = AutoMLForecastingTrainingJob(
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
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            time_series_attribute_columns=_TEST_TRAINING_TIME_SERIES_ATTRIBUTE_COLUMNS,
            context_window=_TEST_TRAINING_CONTEXT_WINDOW,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            quantiles=_TEST_TRAINING_QUANTILES,
            validation_options=_TEST_TRAINING_VALIDATION_OPTIONS,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_TRAINING_FRACTION_SPLIT,
            validation_fraction=_TEST_VALIDATION_FRACTION_SPLIT,
            test_fraction=_TEST_TEST_FRACTION_SPLIT,
        )

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(display_name=_TEST_DISPLAY_NAME)

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_dataset_time_series.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_forecasting,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_model_service_get",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_called_twice_raises(
        self, mock_dataset_time_series, sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = AutoMLForecastingTrainingJob(
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
            sync=sync,
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
                sync=sync,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self,
        mock_pipeline_service_create_and_get_with_fail,
        mock_dataset_time_series,
        sync,
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = AutoMLForecastingTrainingJob(
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
                sync=sync,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    def test_raises_before_run_is_called(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = AutoMLForecastingTrainingJob(
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
