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
import uuid
import pytest
import importlib

import pandas as pd

from google import auth as google_auth
from google.api_core import exceptions
from google.api_core import client_options

from google.cloud import bigquery

from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1beta1.services import dataset_service

from test_utils.vpcsc_config import vpcsc_config

# TODO(vinnys): Replace with env var `BUILD_SPECIFIC_GCP_PROJECT` once supported
_, _TEST_PROJECT = google_auth.default()
TEST_BUCKET = os.environ.get(
    "GCLOUD_TEST_SAMPLES_BUCKET", "cloud-samples-data-us-central1"
)

_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_API_ENDPOINT = f"{_TEST_LOCATION}-aiplatform.googleapis.com"
_TEST_IMAGE_DATASET_ID = "1084241610289446912"  # permanent_50_flowers_dataset
_TEST_TEXT_DATASET_ID = (
    "6203215905493614592"  # permanent_text_entity_extraction_dataset
)
_TEST_DATASET_DISPLAY_NAME = "permanent_50_flowers_dataset"
_TEST_TABULAR_CLASSIFICATION_GCS_SOURCE = "gs://ucaip-sample-resources/iris_1000.csv"
_TEST_TEXT_ENTITY_EXTRACTION_GCS_SOURCE = f"gs://{TEST_BUCKET}/ai-platform-unified/sdk/datasets/text_entity_extraction_dataset.jsonl"
_TEST_IMAGE_OBJECT_DETECTION_GCS_SOURCE = (
    "gs://ucaip-test-us-central1/dataset/salads_oid_ml_use_public_unassigned.jsonl"
)
_TEST_TEXT_ENTITY_IMPORT_SCHEMA = "gs://google-cloud-aiplatform/schema/dataset/ioformat/text_extraction_io_format_1.0.0.yaml"
_TEST_IMAGE_OBJ_DET_IMPORT_SCHEMA = "gs://google-cloud-aiplatform/schema/dataset/ioformat/image_bounding_box_io_format_1.0.0.yaml"

# create_from_dataframe
_TEST_BOOL_COL = "bool_col"
_TEST_BOOL_ARR_COL = "bool_array_col"
_TEST_DOUBLE_COL = "double_col"
_TEST_DOUBLE_ARR_COL = "double_array_col"
_TEST_INT_COL = "int64_col"
_TEST_INT_ARR_COL = "int64_array_col"
_TEST_STR_COL = "string_col"
_TEST_STR_ARR_COL = "string_array_col"
_TEST_BYTES_COL = "bytes_col"
_TEST_DF_COLUMN_NAMES = [
    _TEST_BOOL_COL,
    _TEST_BOOL_ARR_COL,
    _TEST_DOUBLE_COL,
    _TEST_DOUBLE_ARR_COL,
    _TEST_INT_COL,
    _TEST_INT_ARR_COL,
    _TEST_STR_COL,
    _TEST_STR_ARR_COL,
    _TEST_BYTES_COL,
]
_TEST_DATAFRAME = pd.DataFrame(
    data=[
        [
            False,
            [True, False],
            1.2,
            [1.2, 3.4],
            1,
            [1, 2],
            "test",
            ["test1", "test2"],
            b"1",
        ],
        [
            True,
            [True, True],
            2.2,
            [2.2, 4.4],
            2,
            [2, 3],
            "test1",
            ["test2", "test3"],
            b"0",
        ],
    ],
    columns=_TEST_DF_COLUMN_NAMES,
)
_TEST_PARTIAL_BQ_SCHEMA = [
    bigquery.SchemaField("bytes_col", "STRING"),
    bigquery.SchemaField("int64_col", "FLOAT"),
]


class TestDataset:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    @pytest.fixture()
    def shared_state(self):
        shared_state = {}
        yield shared_state

    @pytest.fixture()
    def prepare_bigquery_dataset(self, shared_state):
        """Create a bigquery dataset and store bigquery resource object in shared state."""

        bigquery_client = bigquery.Client(project=_TEST_PROJECT)
        shared_state["bigquery_client"] = bigquery_client

        dataset_name = f"tabulardatasettest_{uuid.uuid4()}".replace("-", "_")
        shared_state["dataset_name"] = dataset_name

        dataset_id = f"{_TEST_PROJECT}.{dataset_name}"
        shared_state["bigquery_dataset_id"] = dataset_id

        dataset = bigquery.Dataset(dataset_id)
        dataset.location = _TEST_LOCATION
        shared_state["bigquery_dataset"] = bigquery_client.create_dataset(dataset)

        yield

    @pytest.fixture()
    def create_staging_bucket(self, shared_state):
        new_staging_bucket = f"temp-sdk-integration-{uuid.uuid4()}"

        storage_client = storage.Client()
        storage_client.create_bucket(new_staging_bucket)
        shared_state["storage_client"] = storage_client
        shared_state["staging_bucket"] = new_staging_bucket
        yield

    @pytest.fixture()
    def delete_staging_bucket(self, shared_state):
        yield
        storage_client = shared_state["storage_client"]

        # Delete temp staging bucket
        bucket_to_delete = storage_client.get_bucket(shared_state["staging_bucket"])
        bucket_to_delete.delete(force=True)

        # Close Storage Client
        storage_client._http._auth_request.session.close()
        storage_client._http.close()

    @pytest.fixture()
    def dataset_gapic_client(self):
        gapic_client = dataset_service.DatasetServiceClient(
            client_options=client_options.ClientOptions(api_endpoint=_TEST_API_ENDPOINT)
        )

        yield gapic_client

    @pytest.fixture()
    def create_text_dataset(self, dataset_gapic_client, shared_state):

        gapic_dataset = gca_dataset.Dataset(
            display_name=f"temp_sdk_integration_test_create_text_dataset_{uuid.uuid4()}",
            metadata_schema_uri=aiplatform.schema.dataset.metadata.text,
        )

        create_lro = dataset_gapic_client.create_dataset(
            parent=_TEST_PARENT, dataset=gapic_dataset
        )
        new_dataset = create_lro.result()
        shared_state["dataset_name"] = new_dataset.name
        yield

    @pytest.fixture()
    def create_tabular_dataset(self, dataset_gapic_client, shared_state):

        gapic_dataset = gca_dataset.Dataset(
            display_name=f"temp_sdk_integration_test_create_tabular_dataset_{uuid.uuid4()}",
            metadata_schema_uri=aiplatform.schema.dataset.metadata.tabular,
        )

        create_lro = dataset_gapic_client.create_dataset(
            parent=_TEST_PARENT, dataset=gapic_dataset
        )
        new_dataset = create_lro.result()
        shared_state["dataset_name"] = new_dataset.name
        yield

    @pytest.fixture()
    def create_image_dataset(self, dataset_gapic_client, shared_state):

        gapic_dataset = gca_dataset.Dataset(
            display_name=f"temp_sdk_integration_test_create_image_dataset_{uuid.uuid4()}",
            metadata_schema_uri=aiplatform.schema.dataset.metadata.image,
        )

        create_lro = dataset_gapic_client.create_dataset(
            parent=_TEST_PARENT, dataset=gapic_dataset
        )
        new_dataset = create_lro.result()
        shared_state["dataset_name"] = new_dataset.name
        yield

    @pytest.fixture()
    def delete_new_dataset(self, dataset_gapic_client, shared_state):
        yield
        assert shared_state["dataset_name"]

        deletion_lro = dataset_gapic_client.delete_dataset(
            name=shared_state["dataset_name"]
        )
        deletion_lro.result()

        shared_state["dataset_name"] = None

    # TODO(vinnys): Remove pytest skip once persistent resources are accessible
    @pytest.mark.skip(reason="System tests cannot access persistent test resources")
    def test_get_existing_dataset(self):
        """Retrieve a known existing dataset, ensure SDK successfully gets the
        dataset resource."""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        flowers_dataset = aiplatform.ImageDataset(dataset_name=_TEST_IMAGE_DATASET_ID)
        assert flowers_dataset.name == _TEST_IMAGE_DATASET_ID
        assert flowers_dataset.display_name == _TEST_DATASET_DISPLAY_NAME

    def test_get_nonexistent_dataset(self):
        """Ensure attempting to retrieve a dataset that doesn't exist raises
        a Google API core 404 exception."""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        # AI Platform service returns 404
        with pytest.raises(exceptions.NotFound):
            aiplatform.ImageDataset(dataset_name="0")

    @pytest.mark.usefixtures("create_text_dataset", "delete_new_dataset")
    def test_get_new_dataset_and_import(self, dataset_gapic_client, shared_state):
        """Retrieve new, empty dataset and import a text dataset using import().
        Then verify data items were successfully imported."""

        assert shared_state["dataset_name"]
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        my_dataset = aiplatform.TextDataset(dataset_name=shared_state["dataset_name"])

        data_items_pre_import = dataset_gapic_client.list_data_items(
            parent=my_dataset.resource_name
        )

        assert len(list(data_items_pre_import)) == 0

        # Blocking call to import
        my_dataset.import_data(
            gcs_source=_TEST_TEXT_ENTITY_EXTRACTION_GCS_SOURCE,
            import_schema_uri=_TEST_TEXT_ENTITY_IMPORT_SCHEMA,
            import_request_timeout=None,
        )

        data_items_post_import = dataset_gapic_client.list_data_items(
            parent=my_dataset.resource_name
        )

        assert len(list(data_items_post_import)) == 469

    @vpcsc_config.skip_if_inside_vpcsc
    @pytest.mark.usefixtures("delete_new_dataset")
    def test_create_and_import_image_dataset(self, dataset_gapic_client, shared_state):
        """Use the Dataset.create() method to create a new image obj detection
        dataset and import images. Then confirm images were successfully imported."""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        img_dataset = aiplatform.ImageDataset.create(
            display_name=f"temp_sdk_integration_create_and_import_dataset_{uuid.uuid4()}",
            gcs_source=_TEST_IMAGE_OBJECT_DETECTION_GCS_SOURCE,
            import_schema_uri=_TEST_IMAGE_OBJ_DET_IMPORT_SCHEMA,
            create_request_timeout=None,
        )

        shared_state["dataset_name"] = img_dataset.resource_name

        data_items_iterator = dataset_gapic_client.list_data_items(
            parent=img_dataset.resource_name
        )

        assert len(list(data_items_iterator)) == 14

    @pytest.mark.usefixtures("delete_new_dataset")
    def test_create_tabular_dataset(self, dataset_gapic_client, shared_state):
        """Use the Dataset.create() method to create a new tabular dataset.
        Then confirm the dataset was successfully created and references GCS source."""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        tabular_dataset = aiplatform.TabularDataset.create(
            display_name=f"temp_sdk_integration_create_and_import_dataset_{uuid.uuid4()}",
            gcs_source=[_TEST_TABULAR_CLASSIFICATION_GCS_SOURCE],
            create_request_timeout=None,
        )

        shared_state["dataset_name"] = tabular_dataset.resource_name

        gapic_metadata = tabular_dataset.to_dict()["metadata"]
        gcs_source_uris = gapic_metadata["inputConfig"]["gcsSource"]["uri"]

        assert len(gcs_source_uris) == 1
        assert _TEST_TABULAR_CLASSIFICATION_GCS_SOURCE == gcs_source_uris[0]
        assert (
            tabular_dataset.metadata_schema_uri
            == aiplatform.schema.dataset.metadata.tabular
        )

    @pytest.mark.usefixtures("delete_new_dataset", "prepare_bigquery_dataset")
    def test_create_tabular_dataset_from_dataframe(
        self, dataset_gapic_client, shared_state
    ):
        """Use the Dataset.create_from_dataframe() method to create a new tabular dataset.
        Then confirm the dataset was successfully created and references GCS source."""

        assert shared_state["dataset_name"]
        assert shared_state["bigquery_dataset"]

        bigquery_dataset_id = shared_state["bigquery_dataset_id"]
        bq_staging_table = f"bq://{bigquery_dataset_id}.test_table{uuid.uuid4()}"

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        tabular_dataset = aiplatform.TabularDataset.create_from_dataframe(
            df_source=_TEST_DATAFRAME,
            staging_path=bq_staging_table,
            display_name=f"temp_sdk_integration_create_and_import_dataset_from_dataframe{uuid.uuid4()}",
        )

        shared_state["dataset_name"] = tabular_dataset.resource_name

        gapic_metadata = tabular_dataset.to_dict()["metadata"]
        bq_source = gapic_metadata["inputConfig"]["bigquerySource"]["uri"]

        assert bq_staging_table == bq_source
        assert (
            tabular_dataset.metadata_schema_uri
            == aiplatform.schema.dataset.metadata.tabular
        )

    @pytest.mark.usefixtures("delete_new_dataset", "prepare_bigquery_dataset")
    def test_create_tabular_dataset_from_dataframe_with_provided_schema(
        self, dataset_gapic_client, shared_state
    ):
        """Use the Dataset.create_from_dataframe() method to create a new tabular dataset.
        Then confirm the dataset was successfully created and references GCS source."""

        assert shared_state["dataset_name"]
        assert shared_state["bigquery_dataset"]

        bigquery_dataset_id = shared_state["bigquery_dataset_id"]
        bq_staging_table = f"bq://{bigquery_dataset_id}.test_table{uuid.uuid4()}"

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        tabular_dataset = aiplatform.TabularDataset.create_from_dataframe(
            df_source=_TEST_DATAFRAME,
            staging_path=bq_staging_table,
            display_name=f"temp_sdk_integration_create_and_import_dataset_from_dataframe{uuid.uuid4()}",
            bq_schema=_TEST_PARTIAL_BQ_SCHEMA,
        )

        shared_state["dataset_name"] = tabular_dataset.resource_name

        gapic_metadata = tabular_dataset.to_dict()["metadata"]
        bq_source = gapic_metadata["inputConfig"]["bigquerySource"]["uri"]

        assert bq_staging_table == bq_source
        assert (
            tabular_dataset.metadata_schema_uri
            == aiplatform.schema.dataset.metadata.tabular
        )

    # TODO(vinnys): Remove pytest skip once persistent resources are accessible
    @pytest.mark.skip(reason="System tests cannot access persistent test resources")
    @pytest.mark.usefixtures("create_staging_bucket", "delete_staging_bucket")
    def test_export_data(self, shared_state):
        """Get an existing dataset, export data to a newly created folder in
        Google Cloud Storage, then verify data was successfully exported."""

        assert shared_state["staging_bucket"]
        assert shared_state["storage_client"]

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket']}",
        )

        text_dataset = aiplatform.TextDataset(dataset_name=_TEST_TEXT_DATASET_ID)

        exported_files = text_dataset.export_data(
            output_dir=f"gs://{shared_state['staging_bucket']}"
        )

        assert len(exported_files)  # Ensure at least one GCS path was returned

        exported_file = exported_files[0]
        bucket, prefix = utils.extract_bucket_and_prefix_from_gcs_path(exported_file)

        storage_client = shared_state["storage_client"]

        bucket = storage_client.get_bucket(bucket)
        blob = bucket.get_blob(prefix)

        assert blob  # Verify the returned GCS export path exists
