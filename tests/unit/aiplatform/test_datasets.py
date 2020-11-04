# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

import os
import pytest

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.api_core import operation
from google.auth.exceptions import GoogleAuthError
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import Dataset
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform_v1beta1 import GcsSource
from google.cloud.aiplatform_v1beta1 import GcsDestination
from google.cloud.aiplatform_v1beta1 import ImportDataConfig
from google.cloud.aiplatform_v1beta1 import ExportDataConfig
from google.cloud.aiplatform_v1beta1 import DatasetServiceClient
from google.cloud.aiplatform_v1beta1 import Dataset as GapicDataset

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ALT_LOCATION = "europe-west4"
_TEST_ID = "1028944691210842416"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/{_TEST_ID}"
_TEST_ALT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_ALT_LOCATION}/datasets/{_TEST_ID}"
)

_TEST_INVALID_LOCATION = "us-central2"
_TEST_INVALID_NAME = f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_ID}"

_TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}
_TEST_DISPLAY_NAME = "my_dataset_1234"
_TEST_METADATA_SCHEMA_URI = "gs://my-bucket/schema-9876.yaml"

_TEST_IMPORT_SCHEMA_URI = "gs://google-cloud-aiplatform/schemas/1.0.0.yaml"
_TEST_SOURCE_URI = "gs://my-bucket/my_index_file.jsonl"
_TEST_SOURCE_URIS = [
    "gs://my-bucket/index_file_1.jsonl",
    "gs://my-bucket/index_file_2.jsonl",
    "gs://my-bucket/index_file_3.jsonl",
]
_TEST_INVALID_SOURCE_URIS = ["gs://my-bucket/index_file_1.jsonl", 123]
_TEST_DATA_LABEL_ITEMS = {}

_TEST_OUTPUT_DIR = "gs://my-output-bucket"


# TODO(b/171333554): Move reusable test fixtures to conftest.py file
class TestDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    @pytest.fixture
    def get_dataset_mock(self):
        with patch.object(DatasetServiceClient, "get_dataset") as get_dataset_mock:
            get_dataset_mock.return_value = GapicDataset(
                display_name=_TEST_DISPLAY_NAME,
                metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
                labels=_TEST_LABEL,
                name=_TEST_NAME,
            )
            yield get_dataset_mock

    @pytest.fixture
    def get_dataset_without_name_mock(self):
        with patch.object(DatasetServiceClient, "get_dataset") as get_dataset_mock:
            get_dataset_mock.return_value = GapicDataset(
                display_name=_TEST_DISPLAY_NAME,
                metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
                labels=_TEST_LABEL,
            )
            yield get_dataset_mock

    @pytest.fixture
    def create_dataset_mock(self):
        with patch.object(
            DatasetServiceClient, "create_dataset"
        ) as create_dataset_mock:
            create_dataset_lro_mock = mock.Mock(operation.Operation)
            create_dataset_lro_mock.result.return_value = GapicDataset(
                name=_TEST_NAME, display_name=_TEST_DISPLAY_NAME
            )
            create_dataset_mock.return_value = create_dataset_lro_mock
            yield create_dataset_mock

    @pytest.fixture
    def import_data_mock(self):
        with patch.object(DatasetServiceClient, "import_data") as import_data_mock:
            import_data_mock.return_value = mock.Mock(operation.Operation)
            yield import_data_mock

    @pytest.fixture
    def export_data_mock(self):
        with patch.object(DatasetServiceClient, "export_data") as export_data_mock:
            export_data_mock.return_value = mock.Mock(operation.Operation)
            yield export_data_mock

    def test_init_dataset(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        Dataset(dataset_name=_TEST_NAME)
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_dataset_with_id_only(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        Dataset(dataset_name=_TEST_ID)
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_without_name_mock")
    @patch.dict(
        os.environ, {"GOOGLE_CLOUD_PROJECT": "", "GOOGLE_APPLICATION_CREDENTIALS": ""}
    )
    def test_init_dataset_with_id_only_without_project_or_location(self):
        with pytest.raises(GoogleAuthError):
            Dataset(
                dataset_name=_TEST_ID,
                credentials=auth_credentials.AnonymousCredentials(),
            )

    def test_init_dataset_with_location_override(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        Dataset(dataset_name=_TEST_ID, location=_TEST_ALT_LOCATION)
        get_dataset_mock.assert_called_once_with(name=_TEST_ALT_NAME)

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_init_dataset_with_invalid_name(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            Dataset(dataset_name=_TEST_INVALID_NAME)

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_dataset(self, create_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)

        Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
            labels=_TEST_LABEL,
        )

        expected_dataset = GapicDataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
            labels=_TEST_LABEL,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT, dataset=expected_dataset, metadata=()
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_and_import_dataset(self, create_dataset_mock, import_data_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            source=_TEST_SOURCE_URI,
            labels=_TEST_LABEL,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_items_labels=_TEST_DATA_LABEL_ITEMS,
        )

        expected_dataset = GapicDataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
            labels=_TEST_LABEL,
        )

        expected_import_config = ImportDataConfig(
            gcs_source=GcsSource(uris=[_TEST_SOURCE_URI]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT, dataset=expected_dataset, metadata=()
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_and_import_dataset_without_import_schema_uri(
        self, create_dataset_mock
    ):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT)

            Dataset.create(
                display_name=_TEST_DISPLAY_NAME,
                metadata_schema_uri=_TEST_METADATA_SCHEMA_URI,
                labels=_TEST_LABEL,
                source=_TEST_SOURCE_URI,
            )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_import_data(self, import_data_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = Dataset(dataset_name=_TEST_NAME)

        my_dataset.import_data(
            gcs_source=_TEST_SOURCE_URI,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_items_labels=_TEST_DATA_LABEL_ITEMS,
        )

        expected_import_config = ImportDataConfig(
            gcs_source=GcsSource(uris=[_TEST_SOURCE_URI]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_export_data(self, export_data_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = Dataset(dataset_name=_TEST_NAME)

        my_dataset.export_data(output_dir=_TEST_OUTPUT_DIR)

        expected_export_config = ExportDataConfig(
            gcs_destination=GcsDestination(output_uri_prefix=_TEST_OUTPUT_DIR)
        )

        export_data_mock.assert_called_once_with(
            name=_TEST_NAME, export_config=expected_export_config
        )
