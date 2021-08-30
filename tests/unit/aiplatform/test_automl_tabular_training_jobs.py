import importlib
import pytest
from unittest import mock

from google.cloud import aiplatform

from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform_v1.services.pipeline_service import (
    client as pipeline_service_client,
)
from google.cloud.aiplatform_v1.types import (
    dataset as gca_dataset,
    encryption_spec as gca_encryption_spec,
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
_TEST_METADATA_SCHEMA_URI_TABULAR = schema.dataset.metadata.tabular
_TEST_METADATA_SCHEMA_URI_NONTABULAR = schema.dataset.metadata.image

_TEST_TRAINING_COLUMN_NAMES = [
    "sepal_width",
    "sepal_length",
    "petal_length",
    "petal_width",
    "target",
]

_TEST_TRAINING_COLUMN_NAMES_ALTERNATIVE = [
    "apple",
    "banana",
    "coconut",
    "target",
]

_TEST_TRAINING_COLUMN_TRANSFORMATIONS = [
    {"auto": {"column_name": "sepal_width"}},
    {"auto": {"column_name": "sepal_length"}},
    {"auto": {"column_name": "petal_length"}},
    {"auto": {"column_name": "petal_width"}},
]
_TEST_TRAINING_COLUMN_SPECS = {
    "apple": "auto",
    "banana": "auto",
    "coconut": "auto",
}
_TEST_TRAINING_COLUMN_TRANSFORMATIONS_ALTERNATIVE = [
    {"auto": {"column_name": "apple"}},
    {"auto": {"column_name": "banana"}},
    {"auto": {"column_name": "coconut"}},
]
_TEST_TRAINING_COLUMN_TRANSFORMATIONS_ALTERNATIVE_NOT_AUTO = [
    {"numeric": {"column_name": "apple"}},
    {"categorical": {"column_name": "banana"}},
    {"text": {"column_name": "coconut"}},
]
_TEST_TRAINING_TARGET_COLUMN = "target"
_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS = 1000
_TEST_TRAINING_WEIGHT_COLUMN = "weight"
_TEST_TRAINING_DISABLE_EARLY_STOPPING = True
_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME = "minimize-log-loss"
_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE = "classification"
_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS = True
_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI = (
    "bq://path.to.table"
)
_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION = False
_TEST_ADDITIONAL_EXPERIMENTS = ["exp1", "exp2"]
_TEST_TRAINING_TASK_INPUTS_DICT = {
    # required inputs
    "targetColumn": _TEST_TRAINING_TARGET_COLUMN,
    "transformations": _TEST_TRAINING_COLUMN_TRANSFORMATIONS,
    "trainBudgetMilliNodeHours": _TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
    # optional inputs
    "weightColumnName": _TEST_TRAINING_WEIGHT_COLUMN,
    "disableEarlyStopping": _TEST_TRAINING_DISABLE_EARLY_STOPPING,
    "predictionType": _TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
    "optimizationObjective": _TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
    "optimizationObjectiveRecallValue": None,
    "optimizationObjectivePrecisionValue": None,
}
_TEST_TRAINING_TASK_INPUTS = json_format.ParseDict(
    _TEST_TRAINING_TASK_INPUTS_DICT, struct_pb2.Value(),
)
_TEST_TRAINING_TASK_INPUTS_WITH_ADDITIONAL_EXPERIMENTS = json_format.ParseDict(
    {
        **_TEST_TRAINING_TASK_INPUTS_DICT,
        "additionalExperiments": _TEST_ADDITIONAL_EXPERIMENTS,
    },
    struct_pb2.Value(),
)
_TEST_TRAINING_TASK_INPUTS_ALTERNATIVE = json_format.ParseDict(
    {
        **_TEST_TRAINING_TASK_INPUTS_DICT,
        "transformations": _TEST_TRAINING_COLUMN_TRANSFORMATIONS_ALTERNATIVE,
    },
    struct_pb2.Value(),
)
_TEST_TRAINING_TASK_INPUTS_ALTERNATIVE_NOT_AUTO = json_format.ParseDict(
    {
        **_TEST_TRAINING_TASK_INPUTS_DICT,
        "transformations": _TEST_TRAINING_COLUMN_TRANSFORMATIONS_ALTERNATIVE_NOT_AUTO,
    },
    struct_pb2.Value(),
)
_TEST_TRAINING_TASK_INPUTS_WITH_EXPORT_EVAL_DATA_ITEMS = json_format.ParseDict(
    {
        **_TEST_TRAINING_TASK_INPUTS_DICT,
        "exportEvaluatedDataItemsConfig": {
            "destinationBigqueryUri": _TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            "overrideExistingTable": _TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
        },
    },
    struct_pb2.Value(),
)

_TEST_DATASET_NAME = "test-dataset-name"

_TEST_MODEL_DISPLAY_NAME = "model-display-name"

_TEST_LABELS = {"key": "value"}
_TEST_MODEL_LABELS = {"model_key": "model_value"}

_TEST_FRACTION_SPLIT_TRAINING = 0.6
_TEST_FRACTION_SPLIT_VALIDATION = 0.2
_TEST_FRACTION_SPLIT_TEST = 0.2

_TEST_SPLIT_PREDEFINED_COLUMN_NAME = "split"
_TEST_SPLIT_TIMESTAMP_COLUMN_NAME = "timestamp"

_TEST_OUTPUT_PYTHON_PACKAGE_PATH = "gs://test/ouput/python/trainer.tar.gz"

_TEST_MODEL_NAME = "projects/my-project/locations/us-central1/models/12345"

_TEST_PIPELINE_RESOURCE_NAME = (
    "projects/my-project/locations/us-central1/trainingPipelines/12345"
)

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_PIPELINE_ENCRYPTION_KEY_NAME = "key_pipeline"
_TEST_PIPELINE_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME
)

_TEST_MODEL_ENCRYPTION_KEY_NAME = "key_model"
_TEST_MODEL_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME
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
def mock_pipeline_service_create_fail():
    with mock.patch.object(
        pipeline_service_client.PipelineServiceClient, "create_training_pipeline"
    ) as mock_create_training_pipeline:
        mock_create_training_pipeline.side_effect = RuntimeError("Mock fail")
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
def mock_dataset_tabular():
    ds = mock.MagicMock(datasets.TabularDataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    ds.column_names = _TEST_TRAINING_COLUMN_NAMES

    yield ds


@pytest.fixture
def mock_dataset_tabular_alternative():
    ds = mock.MagicMock(datasets.TabularDataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    ds.column_names = _TEST_TRAINING_COLUMN_NAMES_ALTERNATIVE

    yield ds


@pytest.fixture
def mock_dataset_nontabular():
    ds = mock.MagicMock(datasets.ImageDataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


class TestAutoMLTabularTrainingJob:
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
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
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

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_export_eval_data_items(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            export_evaluated_data_items=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS,
            export_evaluated_data_items_bigquery_destination_uri=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_BIGQUERY_DESTINATION_URI,
            export_evaluated_data_items_override_destination=_TEST_TRAINING_EXPORT_EVALUATED_DATA_ITEMS_OVERRIDE_DESTINATION,
            sync=sync,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_EXPORT_EVAL_DATA_ITEMS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
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
    def test_run_call_pipeline_if_no_model_display_name_nor_model_labels(
        self,
        mock_pipeline_service_create,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        if not sync:
            model_from_job.wait()

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    # This test checks that default transformations are used if no columns transformations are provided
    def test_run_call_pipeline_service_create_if_no_column_transformations(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_transformations=None,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    # This test checks that default transformations are used if no columns transformations are provided
    def test_run_call_pipeline_service_create_if_set_additional_experiments(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            staging_bucket=_TEST_BUCKET_NAME,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_transformations=None,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        job._add_additional_experiments(_TEST_ADDITIONAL_EXPERIMENTS)

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_ADDITIONAL_EXPERIMENTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_column_specs(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular_alternative,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        column_specs = training_jobs.AutoMLTabularTrainingJob.get_auto_column_specs(
            dataset=mock_dataset_tabular_alternative,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
        )

        assert column_specs == _TEST_TRAINING_COLUMN_SPECS

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_specs=column_specs,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular_alternative,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(display_name=_TEST_MODEL_DISPLAY_NAME)

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular_alternative.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_ALTERNATIVE,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_call_pipeline_service_create_with_column_specs_and_transformations_raises(
        self, mock_dataset_tabular_alternative, sync,
    ):
        aiplatform.init()

        column_specs = training_jobs.AutoMLTabularTrainingJob.get_auto_column_specs(
            dataset=mock_dataset_tabular_alternative,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
        )

        assert column_specs == _TEST_TRAINING_COLUMN_SPECS

        with pytest.raises(ValueError):
            training_jobs.AutoMLTabularTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
                column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
                column_specs=column_specs,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_get_column_specs_no_target_raises(
        self, mock_dataset_tabular_alternative, sync,
    ):
        aiplatform.init()

        with pytest.raises(TypeError):
            training_jobs.AutoMLTabularTrainingJob.get_auto_column_specs(
                dataset=mock_dataset_tabular_alternative
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_with_column_specs_not_auto(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular_alternative,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        column_specs = training_jobs.AutoMLTabularTrainingJob.get_auto_column_specs(
            dataset=mock_dataset_tabular_alternative,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
        )
        column_specs[
            _TEST_TRAINING_COLUMN_NAMES_ALTERNATIVE[0]
        ] = training_jobs.AutoMLTabularTrainingJob.column_data_types.NUMERIC
        column_specs[
            _TEST_TRAINING_COLUMN_NAMES_ALTERNATIVE[1]
        ] = training_jobs.AutoMLTabularTrainingJob.column_data_types.CATEGORICAL
        column_specs[
            _TEST_TRAINING_COLUMN_NAMES_ALTERNATIVE[2]
        ] = training_jobs.AutoMLTabularTrainingJob.column_data_types.TEXT

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            column_specs=column_specs,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular_alternative,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(display_name=_TEST_MODEL_DISPLAY_NAME)

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular_alternative.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_ALTERNATIVE_NOT_AUTO,
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
    # Also acts as a custom column_transformations test as it should not error during first call
    def test_run_called_twice_raises(self, mock_dataset_tabular, sync):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            sync=sync,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_dataset_tabular,
                target_column=_TEST_TRAINING_TARGET_COLUMN,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                sync=sync,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self, mock_pipeline_service_create_and_get_with_fail, mock_dataset_tabular, sync
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        with pytest.raises(RuntimeError):
            job.run(
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                dataset=mock_dataset_tabular,
                target_column=_TEST_TRAINING_TARGET_COLUMN,
                sync=sync,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    def test_wait_for_resource_creation_does_not_fail_if_creation_does_not_fail(
        self, mock_pipeline_service_create_and_get_with_fail, mock_dataset_tabular
    ):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        job.run(
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            sync=False,
        )

        job.wait_for_resource_creation()

        assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME

        with pytest.raises(RuntimeError):
            job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    @pytest.mark.usefixtures("mock_pipeline_service_create_fail")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_fails(self, mock_dataset_tabular, sync):

        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        if sync:
            with pytest.raises(RuntimeError) as e:
                job.run(
                    model_display_name=_TEST_MODEL_DISPLAY_NAME,
                    dataset=mock_dataset_tabular,
                    target_column=_TEST_TRAINING_TARGET_COLUMN,
                    sync=sync,
                )
            assert e.match("Mock fail")

            with pytest.raises(RuntimeError) as e:
                job.wait_for_resource_creation()
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource is not scheduled to be created."
            )

            with pytest.raises(RuntimeError) as e:
                assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created."
            )

            job.wait()

            with pytest.raises(RuntimeError) as e:
                job.get_model()
                e.match(
                    regexp="TrainingPipeline has not been launched. You must run this TrainingPipeline using TrainingPipeline.run."
                )

        else:
            job.run(
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                dataset=mock_dataset_tabular,
                target_column=_TEST_TRAINING_TARGET_COLUMN,
                sync=sync,
            )

            with pytest.raises(RuntimeError) as e:
                job.wait_for_resource_creation()
            assert e.match(regexp=r"Mock fail")

            with pytest.raises(RuntimeError) as e:
                assert job.resource_name == _TEST_PIPELINE_RESOURCE_NAME
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created. Resource failed with: Mock fail"
            )

            with pytest.raises(RuntimeError):
                job.wait()

            with pytest.raises(RuntimeError):
                job.get_model()

    def test_raises_before_run_is_called(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT, staging_bucket=_TEST_BUCKET_NAME)

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        with pytest.raises(RuntimeError):
            job.get_model()

        with pytest.raises(RuntimeError):
            job.has_failed

        with pytest.raises(RuntimeError):
            job.state

        with pytest.raises(RuntimeError) as e:
            job.wait_for_resource_creation()
        assert e.match(
            regexp=r"AutoMLTabularTrainingJob resource is not scheduled to be created."
        )

    def test_properties_throw_if_not_available(self):

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
        )

        with pytest.raises(RuntimeError) as e:
            job.name
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

        with pytest.raises(RuntimeError) as e:
            job.resource_name
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

        with pytest.raises(RuntimeError) as e:
            job.display_name
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

        with pytest.raises(RuntimeError) as e:
            job.create_time
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

        with pytest.raises(RuntimeError) as e:
            job.encryption_spec
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

        with pytest.raises(RuntimeError) as e:
            job.labels
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

        with pytest.raises(RuntimeError) as e:
            job.gca_resource
            assert e.match(
                regexp=r"AutoMLTabularTrainingJob resource has not been created"
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_splits_fraction(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an AutoML Video Classification training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
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
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split, dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_splits_timestamp(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an AutoML Video Classification training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            timestamp_split_column_name=_TEST_SPLIT_TIMESTAMP_COLUMN_NAME,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
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
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            timestamp_split=true_split, dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_splits_predefined(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an AutoML Video Classification training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            predefined_split_column_name=_TEST_SPLIT_PREDEFINED_COLUMN_NAME,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_split = gca_training_pipeline.PredefinedSplit(
            key=_TEST_SPLIT_PREDEFINED_COLUMN_NAME
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            predefined_split=true_split, dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_splits_default(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_tabular,
        mock_model_service_get,
        sync,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an AutoML Video Classification training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTabularTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            optimization_prediction_type=_TEST_TRAINING_OPTIMIZATION_PREDICTION_TYPE,
            optimization_objective=_TEST_TRAINING_OPTIMIZATION_OBJECTIVE_NAME,
            column_transformations=_TEST_TRAINING_COLUMN_TRANSFORMATIONS,
            optimization_objective_recall_value=None,
            optimization_objective_precision_value=None,
        )

        model_from_job = job.run(
            dataset=mock_dataset_tabular,
            target_column=_TEST_TRAINING_TARGET_COLUMN,
            weight_column=_TEST_TRAINING_WEIGHT_COLUMN,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_tabular.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_tabular,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )
