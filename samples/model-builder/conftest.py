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

import pytest

from google.cloud import aiplatform


@pytest.fixture
def mock_sdk_init():
    with patch.object(aiplatform, "init") as mock:
        yield mock


# ----------------------------------------------------------------------------
# Dataset Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def mock_dataset():
    mock = MagicMock(aiplatform.datasets._Dataset)
    yield mock


@pytest.fixture
def mock_new_dataset(mock_dataset):
    with patch.object(aiplatform.datasets._Dataset, "__new__") as mock_new_dataset:
        mock_new_dataset.return_value = mock_dataset
        yield mock_new_dataset


@pytest.fixture
def mock_init_dataset(mock_new_dataset):
    with patch.object(aiplatform.datasets._Dataset, "__init__") as mock_init_dataset:
        mock_init_dataset.return_value = None
        yield mock_init_dataset


@pytest.fixture
def mock_create_dataset():
    with patch.object(aiplatform.datasets._Dataset, "create") as mock:
        mock.return_value = MagicMock(aiplatform._Dataset)
        yield mock


@pytest.fixture
def mock_create_image_dataset():
    with patch.object(aiplatform.datasets.ImageDataset, "create") as mock:
        mock.return_value = MagicMock(aiplatform.ImageDataset)
        yield mock


# ----------------------------------------------------------------------------
# TrainingJob Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def mock_init_automl_image_training_job():
    with patch.object(
        aiplatform.training_jobs.AutoMLImageTrainingJob, "__init__"
    ) as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def mock_run_automl_image_training_job():
    with patch.object(aiplatform.training_jobs.AutoMLImageTrainingJob, "run") as mock:
        yield mock


# ----------------------------------------------------------------------------
# Model Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def mock_init_model():
    with patch.object(aiplatform.models.Model, "__init__") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def mock_batch_predict_model():
    with patch.object(aiplatform.models.Model, "batch_predict") as mock:
        yield mock


# ----------------------------------------------------------------------------
# Job Fixtures
# ----------------------------------------------------------------------------


@pytest.fixture
def mock_create_batch_prediction_job():
    with patch.object(aiplatform.jobs.BatchPredictionJob, "create") as mock:
        yield mock
