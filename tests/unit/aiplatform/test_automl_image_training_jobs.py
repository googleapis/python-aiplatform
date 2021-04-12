import pytest
import importlib
from unittest import mock

from google.protobuf import json_format
from google.protobuf import struct_pb2

from google.cloud import aiplatform

from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
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

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_DATASET_DISPLAY_NAME = "test-dataset-display-name"
_TEST_DATASET_NAME = "test-dataset-name"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_METADATA_SCHEMA_URI_IMAGE = schema.dataset.metadata.image

_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS = 1000
_TEST_TRAINING_DISABLE_EARLY_STOPPING = True
_TEST_MODEL_TYPE_ICN = "CLOUD"  # Image Classification default
_TEST_MODEL_TYPE_IOD = "CLOUD_HIGH_ACCURACY_1"  # Image Object Detection default
_TEST_MODEL_TYPE_MOBILE = "MOBILE_TF_LOW_LATENCY_1"
_TEST_PREDICTION_TYPE_ICN = "classification"
_TEST_PREDICTION_TYPE_IOD = "object_detection"

_TEST_DATASET_NAME = "test-dataset-name"
_TEST_MODEL_DISPLAY_NAME = "model-display-name"
_TEST_MODEL_ID = "98777645321"

_TEST_TRAINING_TASK_INPUTS = json_format.ParseDict(
    {
        "modelType": "CLOUD",
        "budgetMilliNodeHours": _TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
        "multiLabel": False,
        "disableEarlyStopping": _TEST_TRAINING_DISABLE_EARLY_STOPPING,
    },
    struct_pb2.Value(),
)

_TEST_TRAINING_TASK_INPUTS_WITH_BASE_MODEL = json_format.ParseDict(
    {
        "modelType": "CLOUD",
        "budgetMilliNodeHours": _TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
        "multiLabel": False,
        "disableEarlyStopping": _TEST_TRAINING_DISABLE_EARLY_STOPPING,
        "baseModelId": _TEST_MODEL_ID,
    },
    struct_pb2.Value(),
)

_TEST_FRACTION_SPLIT_TRAINING = 0.6
_TEST_FRACTION_SPLIT_VALIDATION = 0.2
_TEST_FRACTION_SPLIT_TEST = 0.2

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_MODEL_ID}"
)

_TEST_PIPELINE_RESOURCE_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/trainingPipeline/12345"
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
def mock_dataset_image():
    ds = mock.MagicMock(datasets.ImageDataset)
    ds.name = _TEST_DATASET_NAME
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_IMAGE,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


@pytest.fixture
def mock_model_image():
    model = mock.MagicMock(models.Model)
    model.name = _TEST_MODEL_ID
    model._latest_future = None
    model._exception = None
    model._gca_resource = gca_model.Model(
        display_name=_TEST_MODEL_DISPLAY_NAME,
        description="This is the mock Model's description",
        name=_TEST_MODEL_NAME,
    )
    yield model


class TestAutoMLImageTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_all_parameters(self, mock_model_image):
        """Ensure all private members are set correctly at initalization"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLImageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_ICN,
            model_type=_TEST_MODEL_TYPE_MOBILE,
            base_model=mock_model_image,
            multi_label=True,
        )

        assert job._display_name == _TEST_DISPLAY_NAME
        assert job._model_type == _TEST_MODEL_TYPE_MOBILE
        assert job._prediction_type == _TEST_PREDICTION_TYPE_ICN
        assert job._multi_label is True
        assert job._base_model == mock_model_image

    def test_init_wrong_parameters(self, mock_model_image):
        """Ensure correct exceptions are raised when initializing with invalid args"""

        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(ValueError, match=r"not a supported prediction type"):
            training_jobs.AutoMLImageTrainingJob(
                display_name=_TEST_DISPLAY_NAME, prediction_type="abcdefg",
            )

        with pytest.raises(ValueError, match=r"not a supported model_type for"):
            training_jobs.AutoMLImageTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                prediction_type="classification",
                model_type=_TEST_MODEL_TYPE_IOD,
            )

        with pytest.raises(ValueError, match=r"`base_model` is only supported"):
            training_jobs.AutoMLImageTrainingJob(
                display_name=_TEST_DISPLAY_NAME,
                prediction_type=_TEST_PREDICTION_TYPE_IOD,
                base_model=mock_model_image,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_image,
        mock_model_service_get,
        mock_model_image,
        sync,
    ):
        """Create and run an AutoML ICN training job, verify calls and return value"""

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLImageTrainingJob(
            display_name=_TEST_DISPLAY_NAME, base_model=mock_model_image
        )

        model_from_job = job.run(
            dataset=mock_dataset_image,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
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
            description=mock_model_image._gca_resource.description,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split, dataset_id=mock_dataset_image.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_image_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_WITH_BASE_MODEL,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
        )

        mock_model_service_get.assert_called_once_with(name=_TEST_MODEL_NAME)
        assert job._gca_resource is mock_pipeline_service_get.return_value
        assert model_from_job._gca_resource is mock_model_service_get.return_value
        assert job.get_model()._gca_resource is mock_model_service_get.return_value
        assert not job.has_failed
        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_if_no_model_display_name(
        self,
        mock_pipeline_service_create,
        mock_dataset_image,
        mock_model_service_get,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLImageTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_dataset_image,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            budget_milli_node_hours=_TEST_TRAINING_BUDGET_MILLI_NODE_HOURS,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
        )

        if not sync:
            model_from_job.wait()

        true_fraction_split = gca_training_pipeline.FractionSplit(
            training_fraction=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction=_TEST_FRACTION_SPLIT_TEST,
        )

        # Test that if defaults to the job display name
        true_managed_model = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split, dataset_id=mock_dataset_image.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_image_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
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
    def test_run_called_twice_raises(self, mock_dataset_image, sync):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLImageTrainingJob(display_name=_TEST_DISPLAY_NAME,)

        job.run(
            dataset=mock_dataset_image,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            disable_early_stopping=_TEST_TRAINING_DISABLE_EARLY_STOPPING,
            sync=sync,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_dataset_image,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
                validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
                test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
                sync=sync,
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self, mock_pipeline_service_create_and_get_with_fail, mock_dataset_image, sync
    ):

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLImageTrainingJob(display_name=_TEST_DISPLAY_NAME,)

        with pytest.raises(RuntimeError):
            job.run(
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                dataset=mock_dataset_image,
                training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
                validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
                test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
                sync=sync,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    def test_raises_before_run_is_called(self, mock_pipeline_service_create):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLImageTrainingJob(display_name=_TEST_DISPLAY_NAME,)

        with pytest.raises(RuntimeError):
            job.get_model()

        with pytest.raises(RuntimeError):
            job.has_failed

        with pytest.raises(RuntimeError):
            job.state
