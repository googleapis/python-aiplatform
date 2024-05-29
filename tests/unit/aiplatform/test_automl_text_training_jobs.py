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

import pytest
import importlib
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import schema
from google.cloud.aiplatform import training_jobs

from google.cloud.aiplatform.compat.services import (
    model_service_client,
    pipeline_service_client,
)
from google.cloud.aiplatform.compat.types import (
    dataset as gca_dataset,
    encryption_spec as gca_encryption_spec,
    model as gca_model,
    pipeline_state as gca_pipeline_state,
    training_pipeline as gca_training_pipeline,
)
from google.cloud.aiplatform.v1.schema.trainingjob import (
    definition_v1 as training_job_inputs,
)
import constants as test_constants

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_DATASET_DISPLAY_NAME = (
    test_constants.TrainingJobConstants._TEST_DATASET_DISPLAY_NAME
)
_TEST_DATASET_NAME = test_constants.TrainingJobConstants._TEST_DATASET_NAME
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME
_TEST_METADATA_SCHEMA_URI_TEXT = schema.dataset.metadata.text

_TEST_PREDICTION_TYPE_CLASSIFICATION = "classification"
_TEST_CLASSIFICATION_MULTILABEL = True
_TEST_PREDICTION_TYPE_EXTRACTION = "extraction"
_TEST_PREDICTION_TYPE_SENTIMENT = "sentiment"
_TEST_SENTIMENT_MAX = 10

_TEST_DATASET_NAME = test_constants.TrainingJobConstants._TEST_DATASET_NAME
_TEST_MODEL_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_MODEL_DISPLAY_NAME

_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS
_TEST_MODEL_LABELS = test_constants.TrainingJobConstants._TEST_MODEL_LABELS

_TEST_MODEL_ID = "98777645321"

_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION = (
    training_job_inputs.AutoMlTextClassificationInputs(
        multi_label=_TEST_CLASSIFICATION_MULTILABEL
    )
)
_TEST_TRAINING_TASK_INPUTS_EXTRACTION = training_job_inputs.AutoMlTextExtractionInputs()
_TEST_TRAINING_TASK_INPUTS_SENTIMENT = training_job_inputs.AutoMlTextSentimentInputs(
    sentiment_max=_TEST_SENTIMENT_MAX
)

_TEST_FRACTION_SPLIT_TRAINING = 0.6
_TEST_FRACTION_SPLIT_VALIDATION = 0.2
_TEST_FRACTION_SPLIT_TEST = 0.2
_TEST_FILTER_SPLIT_TRAINING = "train"
_TEST_FILTER_SPLIT_VALIDATION = "validate"
_TEST_FILTER_SPLIT_TEST = "test"
_TEST_PREDEFINED_SPLIT_COLUMN_NAME = "predefined_column"

_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_MODEL_ID}"
)

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
        mock_get_training_pipeline.return_value = (
            gca_training_pipeline.TrainingPipeline(
                name=_TEST_PIPELINE_RESOURCE_NAME,
                state=gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED,
                model_to_upload=gca_model.Model(name=_TEST_MODEL_NAME),
            )
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
def mock_dataset_text():
    ds = mock.MagicMock(datasets.TextDataset)
    ds.name = _TEST_DATASET_NAME
    ds.metadata_schema_uri = _TEST_METADATA_SCHEMA_URI_TEXT
    ds._latest_future = None
    ds._exception = None
    ds._gca_resource = gca_dataset.Dataset(
        display_name=_TEST_DATASET_DISPLAY_NAME,
        metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT,
        labels={},
        name=_TEST_DATASET_NAME,
        metadata={},
    )
    return ds


@pytest.fixture
def mock_model():
    model = mock.MagicMock(models.Model)
    model.name = _TEST_MODEL_ID
    model._latest_future = None
    model._gca_resource = gca_model.Model(
        display_name=_TEST_MODEL_DISPLAY_NAME,
        name=_TEST_MODEL_NAME,
    )
    yield model


@pytest.mark.usefixtures("google_auth_mock")
class TestAutoMLTextTrainingJob:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_all_parameters_classification(self):
        """Ensure all private members are set correctly at initialization"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
        )

        assert job._display_name == _TEST_DISPLAY_NAME
        assert (
            job._training_task_definition
            == schema.training_job.definition.automl_text_classification
        )
        assert (
            job._training_task_inputs_dict
            == training_job_inputs.AutoMlTextClassificationInputs(
                multi_label=_TEST_CLASSIFICATION_MULTILABEL
            )
        )

    def test_init_all_parameters_extraction(self):
        """Ensure all private members are set correctly at initialization"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_EXTRACTION,
        )

        assert job._display_name == _TEST_DISPLAY_NAME
        assert (
            job._training_task_definition
            == schema.training_job.definition.automl_text_extraction
        )
        assert (
            job._training_task_inputs_dict
            == training_job_inputs.AutoMlTextExtractionInputs()
        )

    def test_init_all_parameters_sentiment(self):
        """Ensure all private members are set correctly at initialization"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_SENTIMENT,
            sentiment_max=_TEST_SENTIMENT_MAX,
        )

        assert job._display_name == _TEST_DISPLAY_NAME
        assert (
            job._training_task_definition
            == schema.training_job.definition.automl_text_sentiment
        )
        assert (
            job._training_task_inputs_dict
            == training_job_inputs.AutoMlTextSentimentInputs(
                sentiment_max=_TEST_SENTIMENT_MAX
            )
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    def test_init_aiplatform_with_encryption_key_name_and_create_training_job(
        self,
        mock_pipeline_service_create,
        mock_dataset_text,
        mock_model_service_get,
        sync,
    ):
        """
        Initiate aiplatform with encryption key name.
        Create and run an AutoML Text Classification training job, verify calls and return value
        """

        aiplatform.init(
            project=_TEST_PROJECT,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
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
    def test_run_call_pipeline_service_create_classification(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        sync,
    ):
        """Create and run an AutoML Text Classification training job, verify calls and return value"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_filter_split=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter_split=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter_split=_TEST_FILTER_SPLIT_TEST,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter=_TEST_FILTER_SPLIT_TEST,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )
        assert job._gca_resource is mock_pipeline_service_get.return_value
        assert model_from_job._gca_resource is mock_model_service_get.return_value
        assert job.get_model()._gca_resource is mock_model_service_get.return_value
        assert not job.has_failed
        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_classification_with_timeout(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        sync,
    ):
        """Create and run an AutoML Text Classification training job, verify calls and return value"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
            training_encryption_spec_key_name=_TEST_PIPELINE_ENCRYPTION_KEY_NAME,
            model_encryption_spec_key_name=_TEST_MODEL_ENCRYPTION_KEY_NAME,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_filter_split=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter_split=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter_split=_TEST_FILTER_SPLIT_TEST,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            model_from_job.wait()

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter=_TEST_FILTER_SPLIT_TEST,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            encryption_spec=_TEST_MODEL_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_PIPELINE_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=180.0,
        )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_extraction(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        sync,
    ):
        """Create and run an AutoML Text Extraction training job, verify calls and return value"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            prediction_type=_TEST_PREDICTION_TYPE_EXTRACTION,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            sync=sync,
            create_request_timeout=None,
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
            labels=_TEST_MODEL_LABELS,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_text_extraction,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_EXTRACTION,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )
        assert job._gca_resource is mock_pipeline_service_get.return_value
        assert model_from_job._gca_resource is mock_model_service_get.return_value
        assert job.get_model()._gca_resource is mock_model_service_get.return_value
        assert not job.has_failed
        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_service_create_sentiment(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        sync,
    ):
        """Create and run an AutoML Text Sentiment training job, verify calls and return value"""

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            prediction_type=_TEST_PREDICTION_TYPE_SENTIMENT,
            sentiment_max=10,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            model_labels=_TEST_MODEL_LABELS,
            training_filter_split=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter_split=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter_split=_TEST_FILTER_SPLIT_TEST,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter=_TEST_FILTER_SPLIT_TEST,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            labels=_TEST_MODEL_LABELS,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_text_sentiment,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_SENTIMENT,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )

        mock_model_service_get.assert_called_once_with(
            name=_TEST_MODEL_NAME, retry=base._DEFAULT_RETRY
        )
        assert job._gca_resource is mock_pipeline_service_get.return_value
        assert model_from_job._gca_resource is mock_model_service_get.return_value
        assert job.get_model()._gca_resource is mock_model_service_get.return_value
        assert not job.has_failed
        assert job.state == gca_pipeline_state.PipelineState.PIPELINE_STATE_SUCCEEDED

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures("mock_pipeline_service_get")
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_call_pipeline_if_no_model_display_name_nor_model_labels(
        self,
        mock_pipeline_service_create,
        mock_dataset_text,
        mock_model_service_get,
        mock_model,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type="classification",
            multi_label=True,
            labels=_TEST_LABELS,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=None,  # Omit model_display_name
            sync=sync,
            create_request_timeout=None,
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
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
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
    def test_run_called_twice_raises(self, mock_dataset_text, sync):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type="classification",
            multi_label=True,
        )

        job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            sync=sync,
        )

        with pytest.raises(RuntimeError):
            job.run(
                dataset=mock_dataset_text,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                sync=sync,
            )

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.usefixtures(
        "mock_pipeline_service_create",
        "mock_pipeline_service_get",
        "mock_model_service_get",
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_with_two_split_raises(
        self,
        mock_dataset_text,
        sync,
    ):
        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type="classification",
            multi_label=True,
        )

        with pytest.raises(ValueError):
            model_from_job = job.run(
                dataset=mock_dataset_text,
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
                validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
                test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
                training_filter_split=_TEST_FILTER_SPLIT_TRAINING,
                validation_filter_split=_TEST_FILTER_SPLIT_VALIDATION,
                test_filter_split=_TEST_FILTER_SPLIT_TEST,
                sync=sync,
            )
            if not sync:
                model_from_job.wait()

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_run_raises_if_pipeline_fails(
        self, mock_pipeline_service_create_and_get_with_fail, mock_dataset_text, sync
    ):

        aiplatform.init(project=_TEST_PROJECT)

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
        )

        with pytest.raises(RuntimeError):
            job.run(
                model_display_name=_TEST_MODEL_DISPLAY_NAME,
                dataset=mock_dataset_text,
                training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
                validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
                test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
                sync=sync,
            )

            if not sync:
                job.wait()

        with pytest.raises(RuntimeError):
            job.get_model()

    @mock.patch.object(training_jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(training_jobs, "_LOG_WAIT_TIME", 1)
    @pytest.mark.parametrize("sync", [True, False])
    def test_splits_fraction(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        mock_model,
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

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_fraction_split=_TEST_FRACTION_SPLIT_TRAINING,
            validation_fraction_split=_TEST_FRACTION_SPLIT_VALIDATION,
            test_fraction_split=_TEST_FRACTION_SPLIT_TEST,
            sync=sync,
            create_request_timeout=None,
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
            description=mock_model._gca_resource.description,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            fraction_split=true_fraction_split,
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
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
    def test_splits_filter(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        mock_model,
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

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            training_filter_split=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter_split=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter_split=_TEST_FILTER_SPLIT_TEST,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_filter_split = gca_training_pipeline.FilterSplit(
            training_filter=_TEST_FILTER_SPLIT_TRAINING,
            validation_filter=_TEST_FILTER_SPLIT_VALIDATION,
            test_filter=_TEST_FILTER_SPLIT_TEST,
        )

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            description=mock_model._gca_resource.description,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            filter_split=true_filter_split,
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
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
    def test_splits_default(
        self,
        mock_pipeline_service_create,
        mock_pipeline_service_get,
        mock_dataset_text,
        mock_model_service_get,
        mock_model,
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

        job = training_jobs.AutoMLTextTrainingJob(
            display_name=_TEST_DISPLAY_NAME,
            prediction_type=_TEST_PREDICTION_TYPE_CLASSIFICATION,
            multi_label=_TEST_CLASSIFICATION_MULTILABEL,
        )

        model_from_job = job.run(
            dataset=mock_dataset_text,
            model_display_name=_TEST_MODEL_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            model_from_job.wait()

        true_managed_model = gca_model.Model(
            display_name=_TEST_MODEL_DISPLAY_NAME,
            description=mock_model._gca_resource.description,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
            version_aliases=["default"],
        )

        true_input_data_config = gca_training_pipeline.InputDataConfig(
            dataset_id=mock_dataset_text.name,
        )

        true_training_pipeline = gca_training_pipeline.TrainingPipeline(
            display_name=_TEST_DISPLAY_NAME,
            training_task_definition=schema.training_job.definition.automl_text_classification,
            training_task_inputs=_TEST_TRAINING_TASK_INPUTS_CLASSIFICATION,
            model_to_upload=true_managed_model,
            input_data_config=true_input_data_config,
            encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
        )

        mock_pipeline_service_create.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            training_pipeline=true_training_pipeline,
            timeout=None,
        )
