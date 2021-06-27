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
