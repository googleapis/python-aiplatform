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


import pytest
from unittest.mock import MagicMock, patch

from google.cloud import aiplatform


FAKE_DATASET_NAME = "projects/fake_project/locations/fake_location/datasets/123456"


@pytest.fixture
def mock_create_dataset_response():
    mock = MagicMock()
    mock.result().name = FAKE_DATASET_NAME
    mock.resut().metadata_schema_uri = "gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml"

    yield mock


@pytest.fixture
def mock_create_dataset(mock_create_dataset_response):
    mock = MagicMock(return_value=mock_create_dataset_response)

    with patch.object(aiplatform.gapic.DatasetServiceClient, "create_dataset", mock):
        yield mock


@pytest.fixture
def mock_get_dataset():
    mock = MagicMock()
    mock.metadata_schema_uri = "gs://google-cloud-aiplatform/schema/dataset/metadata/text_1.0.0.yaml" 

    mock_method = MagicMock()
    mock_method.return_value = mock
    with patch.object(aiplatform.gapic.DatasetServiceClient, "get_dataset", mock_method):
        yield mock_method


@pytest.fixture
def mock_import_data():
    mock = MagicMock()

    with patch.object(aiplatform.gapic.DatasetServiceClient, "import_data", mock):
        yield mock