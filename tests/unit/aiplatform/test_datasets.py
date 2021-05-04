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
from google.cloud import bigquery
from google.cloud import storage

from google.cloud.aiplatform import datasets
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema

from google.cloud.aiplatform_v1.services.dataset_service import (
    client as dataset_service_client,
)

from google.cloud.aiplatform_v1.types import (
    dataset as gca_dataset,
    dataset_service as gca_dataset_service,
    encryption_spec as gca_encryption_spec,
    io as gca_io,
)

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_ALT_PROJECT = "test-project_alt"

_TEST_ALT_LOCATION = "europe-west4"
_TEST_INVALID_LOCATION = "us-central2"

# dataset
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "my_dataset_1234"
_TEST_DATA_LABEL_ITEMS = None

_TEST_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/{_TEST_ID}"
_TEST_ALT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_ALT_LOCATION}/datasets/{_TEST_ID}"
)
_TEST_INVALID_NAME = f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_ID}"

# metadata_schema_uri
_TEST_METADATA_SCHEMA_URI_TABULAR = schema.dataset.metadata.tabular
_TEST_METADATA_SCHEMA_URI_NONTABULAR = schema.dataset.metadata.image
_TEST_METADATA_SCHEMA_URI_IMAGE = schema.dataset.metadata.image
_TEST_METADATA_SCHEMA_URI_TEXT = schema.dataset.metadata.text
_TEST_METADATA_SCHEMA_URI_VIDEO = schema.dataset.metadata.video

# import_schema_uri
_TEST_IMPORT_SCHEMA_URI_IMAGE = (
    schema.dataset.ioformat.image.single_label_classification
)
_TEST_IMPORT_SCHEMA_URI_TEXT = schema.dataset.ioformat.text.single_label_classification
_TEST_IMPORT_SCHEMA_URI = schema.dataset.ioformat.image.single_label_classification
_TEST_IMPORT_SCHEMA_URI_VIDEO = schema.dataset.ioformat.video.classification

# datasources
_TEST_SOURCE_URI_GCS = "gs://my-bucket/my_index_file.jsonl"
_TEST_SOURCE_URIS_GCS = [
    "gs://my-bucket/index_file_1.jsonl",
    "gs://my-bucket/index_file_2.jsonl",
    "gs://my-bucket/index_file_3.jsonl",
]
_TEST_SOURCE_URI_BQ = "bq://my-project.my-dataset.table"
_TEST_INVALID_SOURCE_URIS = ["gs://my-bucket/index_file_1.jsonl", 123]

# request_metadata
_TEST_REQUEST_METADATA = ()

# dataset_metadata
_TEST_NONTABULAR_DATASET_METADATA = None
_TEST_METADATA_TABULAR_GCS = {
    "inputConfig": {"gcsSource": {"uri": [_TEST_SOURCE_URI_GCS]}}
}
_TEST_METADATA_TABULAR_BQ = {
    "inputConfig": {"bigquerySource": {"uri": _TEST_SOURCE_URI_BQ}}
}

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

# misc
_TEST_OUTPUT_DIR = "gs://my-output-bucket"

_TEST_DATASET_LIST = [
    gca_dataset.Dataset(
        display_name="a", metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR
    ),
    gca_dataset.Dataset(
        display_name="d", metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR
    ),
    gca_dataset.Dataset(
        display_name="b", metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR
    ),
    gca_dataset.Dataset(
        display_name="e", metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT
    ),
    gca_dataset.Dataset(
        display_name="c", metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR
    ),
]

_TEST_LIST_FILTER = 'display_name="abc"'
_TEST_LIST_ORDER_BY = "create_time desc"


@pytest.fixture
def get_dataset_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            name=_TEST_NAME,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_without_name_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_image_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_IMAGE,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_tabular_gcs_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata=_TEST_METADATA_TABULAR_GCS,
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_tabular_bq_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata=_TEST_METADATA_TABULAR_BQ,
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_tabular_missing_metadata_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata=None,
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_tabular_missing_input_config_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata={},
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_tabular_missing_datasource_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata={"inputConfig": {}},
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_text_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def get_dataset_video_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "get_dataset"
    ) as get_dataset_mock:
        get_dataset_mock.return_value = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_VIDEO,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            name=_TEST_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_dataset_mock


@pytest.fixture
def create_dataset_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "create_dataset"
    ) as create_dataset_mock:
        create_dataset_lro_mock = mock.Mock(operation.Operation)
        create_dataset_lro_mock.result.return_value = gca_dataset.Dataset(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_dataset_mock.return_value = create_dataset_lro_mock
        yield create_dataset_mock


@pytest.fixture
def delete_dataset_mock():
    with mock.patch.object(
        dataset_service_client.DatasetServiceClient, "delete_dataset"
    ) as delete_dataset_mock:
        delete_dataset_lro_mock = mock.Mock(operation.Operation)
        delete_dataset_lro_mock.result.return_value = (
            gca_dataset_service.DeleteDatasetRequest()
        )
        delete_dataset_mock.return_value = delete_dataset_lro_mock
        yield delete_dataset_mock


@pytest.fixture
def import_data_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "import_data"
    ) as import_data_mock:
        import_data_mock.return_value = mock.Mock(operation.Operation)
        yield import_data_mock


@pytest.fixture
def export_data_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "export_data"
    ) as export_data_mock:
        export_data_mock.return_value = mock.Mock(operation.Operation)
        yield export_data_mock


@pytest.fixture
def list_datasets_mock():
    with patch.object(
        dataset_service_client.DatasetServiceClient, "list_datasets"
    ) as list_datasets_mock:
        list_datasets_mock.return_value = _TEST_DATASET_LIST
        yield list_datasets_mock


@pytest.fixture
def gcs_client_download_as_bytes_mock():
    with patch.object(storage.Blob, "download_as_bytes") as bigquery_blob_mock:
        bigquery_blob_mock.return_value = b'"column_1","column_2"\n0, 1'
        yield bigquery_blob_mock


@pytest.fixture
def bigquery_client_mock():
    with patch.object(bigquery.Client, "get_table") as bigquery_client_mock:
        bigquery_client_mock.return_value = bigquery.Table("project.dataset.table")
        yield bigquery_client_mock


@pytest.fixture
def bigquery_table_schema_mock():
    with patch.object(
        bigquery.Table, "schema", new_callable=mock.PropertyMock
    ) as bigquery_table_schema_mock:
        bigquery_table_schema_mock.return_value = [
            bigquery.SchemaField("column_1", "FLOAT", "NULLABLE", "", (), None),
            bigquery.SchemaField("column_2", "FLOAT", "NULLABLE", "", (), None),
        ]
        yield bigquery_table_schema_mock


# TODO(b/171333554): Move reusable test fixtures to conftest.py file
class TestDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_dataset(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        datasets._Dataset(dataset_name=_TEST_NAME)
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_dataset_with_id_only_with_project_and_location(
        self, get_dataset_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        datasets._Dataset(
            dataset_name=_TEST_ID, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_dataset_with_project_and_location(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        datasets._Dataset(
            dataset_name=_TEST_NAME, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_dataset_with_alt_project_and_location(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        datasets._Dataset(
            dataset_name=_TEST_NAME, project=_TEST_ALT_PROJECT, location=_TEST_LOCATION
        )
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_dataset_with_project_and_alt_location(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(RuntimeError):
            datasets._Dataset(
                dataset_name=_TEST_NAME,
                project=_TEST_PROJECT,
                location=_TEST_ALT_LOCATION,
            )

    def test_init_dataset_with_id_only(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        datasets._Dataset(dataset_name=_TEST_ID)
        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_without_name_mock")
    @patch.dict(
        os.environ, {"GOOGLE_CLOUD_PROJECT": "", "GOOGLE_APPLICATION_CREDENTIALS": ""}
    )
    def test_init_dataset_with_id_only_without_project_or_location(self):
        with pytest.raises(GoogleAuthError):
            datasets._Dataset(
                dataset_name=_TEST_ID,
                credentials=auth_credentials.AnonymousCredentials(),
            )

    def test_init_dataset_with_location_override(self, get_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        datasets._Dataset(dataset_name=_TEST_ID, location=_TEST_ALT_LOCATION)
        get_dataset_mock.assert_called_once_with(name=_TEST_ALT_NAME)

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_init_dataset_with_invalid_name(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            datasets._Dataset(dataset_name=_TEST_INVALID_NAME)

    @pytest.mark.usefixtures("get_dataset_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_init_aiplatform_with_encryption_key_name_and_create_dataset(
        self, create_dataset_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_dataset = datasets._Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset_nontabular(self, create_dataset_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets._Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_create_dataset_tabular(self, create_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)

        datasets._Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            bq_source=_TEST_SOURCE_URI_BQ,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata=_TEST_METADATA_TABULAR_BQ,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_import_dataset(
        self, create_dataset_mock, import_data_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets._Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            gcs_source=_TEST_SOURCE_URI_GCS,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

    @pytest.mark.usefixtures("get_dataset_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_import_data(self, import_data_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets._Dataset(dataset_name=_TEST_NAME)

        my_dataset.import_data(
            gcs_source=_TEST_SOURCE_URI_GCS,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

    @pytest.mark.usefixtures("get_dataset_mock")
    def test_export_data(self, export_data_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets._Dataset(dataset_name=_TEST_NAME)

        my_dataset.export_data(output_dir=_TEST_OUTPUT_DIR)

        expected_export_config = gca_dataset.ExportDataConfig(
            gcs_destination=gca_io.GcsDestination(output_uri_prefix=_TEST_OUTPUT_DIR)
        )

        export_data_mock.assert_called_once_with(
            name=_TEST_NAME, export_config=expected_export_config
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_then_import(
        self, create_dataset_mock, import_data_mock, get_dataset_mock, sync
    ):

        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets._Dataset.create(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        my_dataset.import_data(
            gcs_source=_TEST_SOURCE_URI_GCS,
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI,
            data_item_labels=_TEST_DATA_LABEL_ITEMS,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        get_dataset_mock.assert_called_once_with(name=_TEST_NAME)

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

    @pytest.mark.usefixtures("get_dataset_tabular_bq_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_dataset(self, delete_dataset_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)
        my_dataset.delete(sync=sync)

        if not sync:
            my_dataset.wait()

        delete_dataset_mock.assert_called_once_with(name=my_dataset.resource_name)


class TestImageDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_dataset_image(self, get_dataset_image_mock):
        aiplatform.init(project=_TEST_PROJECT)
        datasets.ImageDataset(dataset_name=_TEST_NAME)
        get_dataset_image_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_tabular_bq_mock")
    def test_init_dataset_non_image(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(ValueError):
            datasets.ImageDataset(dataset_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_image_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset(self, create_dataset_mock, sync):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_dataset = datasets.ImageDataset.create(
            display_name=_TEST_DISPLAY_NAME, sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_IMAGE,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_image_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_import_dataset(
        self, create_dataset_mock, import_data_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.ImageDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_IMAGE,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_IMAGE,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_IMAGE,
        )
        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

    @pytest.mark.usefixtures("get_dataset_image_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_import_data(self, import_data_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.ImageDataset(dataset_name=_TEST_NAME)

        my_dataset.import_data(
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_IMAGE,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_IMAGE,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_then_import(
        self, create_dataset_mock, import_data_mock, get_dataset_image_mock, sync
    ):

        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.ImageDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        my_dataset.import_data(
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_IMAGE,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_IMAGE,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        get_dataset_image_mock.assert_called_once_with(name=_TEST_NAME)

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_IMAGE,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset


class TestTabularDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_dataset_tabular(self, get_dataset_tabular_bq_mock):

        datasets.TabularDataset(dataset_name=_TEST_NAME)
        get_dataset_tabular_bq_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_image_mock")
    def test_init_dataset_non_tabular(self):

        with pytest.raises(ValueError):
            datasets.TabularDataset(dataset_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_tabular_bq_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset_with_default_encryption_key(
        self, create_dataset_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_dataset = datasets.TabularDataset.create(
            display_name=_TEST_DISPLAY_NAME, bq_source=_TEST_SOURCE_URI_BQ, sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata=_TEST_METADATA_TABULAR_BQ,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_tabular_bq_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset(self, create_dataset_mock, sync):

        my_dataset = datasets.TabularDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            bq_source=_TEST_SOURCE_URI_BQ,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            metadata=_TEST_METADATA_TABULAR_BQ,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_tabular_bq_mock")
    def test_no_import_data_method(self):

        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)

        with pytest.raises(NotImplementedError):
            my_dataset.import_data()

    def test_list_dataset(self, list_datasets_mock):

        ds_list = aiplatform.TabularDataset.list(
            filter=_TEST_LIST_FILTER, order_by=_TEST_LIST_ORDER_BY
        )

        list_datasets_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": _TEST_LIST_FILTER}
        )

        # Ensure returned list is smaller since it filtered out non-tabular datasets
        assert len(ds_list) < len(_TEST_DATASET_LIST)

        for ds in ds_list:
            assert type(ds) == aiplatform.TabularDataset

    def test_list_dataset_no_order_or_filter(self, list_datasets_mock):

        ds_list = aiplatform.TabularDataset.list()

        list_datasets_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": None}
        )

        # Ensure returned list is smaller since it filtered out non-tabular datasets
        assert len(ds_list) < len(_TEST_DATASET_LIST)

        for ds in ds_list:
            assert type(ds) == aiplatform.TabularDataset

    @pytest.mark.usefixtures("get_dataset_tabular_missing_metadata_mock")
    def test_tabular_dataset_column_name_missing_metadata(self):
        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)

        with pytest.raises(RuntimeError):
            my_dataset.column_names

    @pytest.mark.usefixtures("get_dataset_tabular_missing_input_config_mock")
    def test_tabular_dataset_column_name_missing_input_config(self):
        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)

        with pytest.raises(RuntimeError):
            my_dataset.column_names

    @pytest.mark.usefixtures("get_dataset_tabular_missing_datasource_mock")
    def test_tabular_dataset_column_name_missing_datasource(self):
        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)

        with pytest.raises(RuntimeError):
            my_dataset.column_names

    @pytest.mark.usefixtures(
        "get_dataset_tabular_gcs_mock", "gcs_client_download_as_bytes_mock"
    )
    def test_tabular_dataset_column_name_gcs(self):
        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)

        assert my_dataset.column_names == ["column_1", "column_2"]

    @pytest.mark.usefixtures(
        "get_dataset_tabular_bq_mock",
        "bigquery_client_mock",
        "bigquery_table_schema_mock",
    )
    def test_tabular_dataset_column_name_bigquery(self):
        my_dataset = datasets.TabularDataset(dataset_name=_TEST_NAME)

        assert my_dataset.column_names == ["column_1", "column_2"]


class TestTextDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_dataset_text(self, get_dataset_text_mock):
        aiplatform.init(project=_TEST_PROJECT)
        datasets.TextDataset(dataset_name=_TEST_NAME)
        get_dataset_text_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_image_mock")
    def test_init_dataset_non_text(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(ValueError):
            datasets.TextDataset(dataset_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_text_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset(self, create_dataset_mock, sync):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_dataset = datasets.TextDataset.create(
            display_name=_TEST_DISPLAY_NAME, sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_text_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_import_dataset(
        self, create_dataset_mock, import_data_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.TextDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_TEXT,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_TEXT,
        )
        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

    @pytest.mark.usefixtures("get_dataset_text_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_import_data(self, import_data_mock, sync):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME
        )

        my_dataset = datasets.TextDataset(dataset_name=_TEST_NAME)

        my_dataset.import_data(
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_TEXT,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_TEXT,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_then_import(
        self, create_dataset_mock, import_data_mock, get_dataset_text_mock, sync
    ):

        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.TextDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        my_dataset.import_data(
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_TEXT,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TEXT,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        get_dataset_text_mock.assert_called_once_with(name=_TEST_NAME)

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_TEXT,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset


class TestVideoDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_dataset_video(self, get_dataset_video_mock):
        aiplatform.init(project=_TEST_PROJECT)
        datasets.VideoDataset(dataset_name=_TEST_NAME)
        get_dataset_video_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_tabular_bq_mock")
    def test_init_dataset_non_video(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(ValueError):
            datasets.VideoDataset(dataset_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_dataset_video_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_dataset(self, create_dataset_mock, sync):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME
        )

        my_dataset = datasets.VideoDataset.create(
            display_name=_TEST_DISPLAY_NAME, sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_VIDEO,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_dataset_video_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_and_import_dataset(
        self, create_dataset_mock, import_data_mock, sync
    ):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.VideoDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_VIDEO,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_VIDEO,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_VIDEO,
        )
        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset

    @pytest.mark.usefixtures("get_dataset_video_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_import_data(self, import_data_mock, sync):
        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.VideoDataset(dataset_name=_TEST_NAME)

        my_dataset.import_data(
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_VIDEO,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_VIDEO,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_then_import(
        self, create_dataset_mock, import_data_mock, get_dataset_video_mock, sync
    ):

        aiplatform.init(project=_TEST_PROJECT)

        my_dataset = datasets.VideoDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        my_dataset.import_data(
            gcs_source=[_TEST_SOURCE_URI_GCS],
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_VIDEO,
            sync=sync,
        )

        if not sync:
            my_dataset.wait()

        expected_dataset = gca_dataset.Dataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_VIDEO,
            metadata=_TEST_NONTABULAR_DATASET_METADATA,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            dataset=expected_dataset,
            metadata=_TEST_REQUEST_METADATA,
        )

        get_dataset_video_mock.assert_called_once_with(name=_TEST_NAME)

        expected_import_config = gca_dataset.ImportDataConfig(
            gcs_source=gca_io.GcsSource(uris=[_TEST_SOURCE_URI_GCS]),
            import_schema_uri=_TEST_IMPORT_SCHEMA_URI_VIDEO,
        )

        import_data_mock.assert_called_once_with(
            name=_TEST_NAME, import_configs=[expected_import_config]
        )

        expected_dataset.name = _TEST_NAME
        assert my_dataset._gca_resource == expected_dataset
