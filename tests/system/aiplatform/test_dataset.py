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

from google.api_core import exceptions
from google.api_core import client_options

from google.cloud import bigquery

from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform import utils
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.services import dataset_service

from test_utils.vpcsc_config import vpcsc_config

from tests.system.aiplatform import e2e_base

_TEST_PROJECT = e2e_base._PROJECT
_TEST_LOCATION = e2e_base._LOCATION
TEST_BUCKET = os.environ.get(
    "GCLOUD_TEST_SAMPLES_BUCKET", "cloud-samples-data-us-central1"
)

_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_API_ENDPOINT = f"{_TEST_LOCATION}-aiplatform.googleapis.com"
_TEST_IMAGE_DATASET_ID = "1084241610289446912"  # permanent_50_flowers_dataset
_TEST_TEXT_DATASET_ID = (
    "6203215905493614592"  # permanent_text_entity_extraction_dataset
)
_TEST_DATASET_DISPLAY_NAME = "permanent_50_flowers_dataset"
_TEST_TABULAR_CLASSIFICATION_GCS_SOURCE = "gs://ucaip-sample-resources/iris_1000.csv"
_TEST_FORECASTING_BQ_SOURCE = (
    "bq://ucaip-sample-tests:ucaip_test_us_central1.2020_sales_train"
)
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
_TEST_DATAFRAME_BQ_SCHEMA = [
    bigquery.SchemaField(name="bool_col", field_type="BOOL"),
    bigquery.SchemaField(name="bool_array_col", field_type="BOOL", mode="REPEATED"),
    bigquery.SchemaField(name="double_col", field_type="FLOAT"),
    bigquery.SchemaField(name="double_array_col", field_type="FLOAT", mode="REPEATED"),
    bigquery.SchemaField(name="int64_col", field_type="INTEGER"),
    bigquery.SchemaField(name="int64_array_col", field_type="INTEGER", mode="REPEATED"),
    bigquery.SchemaField(name="string_col", field_type="STRING"),
    bigquery.SchemaField(name="string_array_col", field_type="STRING", mode="REPEATED"),
    bigquery.SchemaField(name="bytes_col", field_type="STRING"),
]


class TestDataset(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-dataset-test"

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @pytest.fixture()
    def storage_client(self):
        yield storage.Client(project=_TEST_PROJECT)

    @pytest.fixture()
    def staging_bucket(self, storage_client):
        new_staging_bucket = f"temp-sdk-integration-{uuid.uuid4()}"
        bucket = storage_client.create_bucket(new_staging_bucket)

        yield bucket

        bucket.delete(force=True)

    @pytest.fixture()
    def dataset_gapic_client(self):
        gapic_client = dataset_service.DatasetServiceClient(
            client_options=client_options.ClientOptions(api_endpoint=_TEST_API_ENDPOINT)
        )

        yield gapic_client

    # TODO(vinnys): Remove pytest skip once persistent resources are accessible
    @pytest.mark.skip(reason="System tests cannot access persistent test resources")
    def test_get_existing_dataset(self):
        """Retrieve a known existing dataset, ensure SDK successfully gets the
        dataset resource."""

        flowers_dataset = aiplatform.ImageDataset(dataset_name=_TEST_IMAGE_DATASET_ID)
        assert flowers_dataset.name == _TEST_IMAGE_DATASET_ID
        assert flowers_dataset.display_name == _TEST_DATASET_DISPLAY_NAME

    def test_get_nonexistent_dataset(self):
        """Ensure attempting to retrieve a dataset that doesn't exist raises
        a Google API core 404 exception."""

        # AI Platform service returns 404
        with pytest.raises(exceptions.NotFound):
            aiplatform.ImageDataset(dataset_name="0")

    def test_get_new_dataset_and_import(self, dataset_gapic_client):
        """Retrieve new, empty dataset and import a text dataset using import().
        Then verify data items were successfully imported."""

        try:
            text_dataset = aiplatform.TextDataset.create(
                display_name=self._make_display_name(key="get_new_dataset_and_import"),
            )

            my_dataset = aiplatform.TextDataset(dataset_name=text_dataset.name)

            data_items_pre_import = dataset_gapic_client.list_data_items(
                parent=my_dataset.resource_name
            )

            assert len(list(data_items_pre_import)) == 0

            # Blocking call to import
            my_dataset.import_data(
                gcs_source=_TEST_TEXT_ENTITY_EXTRACTION_GCS_SOURCE,
                import_schema_uri=_TEST_TEXT_ENTITY_IMPORT_SCHEMA,
                import_request_timeout=500,
            )

            data_items_post_import = dataset_gapic_client.list_data_items(
                parent=my_dataset.resource_name
            )

            assert len(list(data_items_post_import)) == 469
        finally:
            text_dataset.delete()

    @vpcsc_config.skip_if_inside_vpcsc
    def test_create_and_import_image_dataset(self, dataset_gapic_client):
        """Use the Dataset.create() method to create a new image obj detection
        dataset and import images. Then confirm images were successfully imported."""

        try:
            img_dataset = aiplatform.ImageDataset.create(
                display_name=self._make_display_name(
                    key="create_and_import_image_dataset"
                ),
                gcs_source=_TEST_IMAGE_OBJECT_DETECTION_GCS_SOURCE,
                import_schema_uri=_TEST_IMAGE_OBJ_DET_IMPORT_SCHEMA,
                create_request_timeout=None,
            )

            data_items_iterator = dataset_gapic_client.list_data_items(
                parent=img_dataset.resource_name
            )

            assert len(list(data_items_iterator)) == 14

        finally:
            if img_dataset is not None:
                img_dataset.delete()

    def test_create_tabular_dataset(self):
        """Use the Dataset.create() method to create a new tabular dataset.
        Then confirm the dataset was successfully created and references GCS source."""

        try:
            tabular_dataset = aiplatform.TabularDataset.create(
                display_name=self._make_display_name(key="create_tabular_dataset"),
                gcs_source=[_TEST_TABULAR_CLASSIFICATION_GCS_SOURCE],
                create_request_timeout=None,
            )

            gapic_metadata = tabular_dataset.to_dict()["metadata"]
            gcs_source_uris = gapic_metadata["inputConfig"]["gcsSource"]["uri"]

            assert len(gcs_source_uris) == 1
            assert _TEST_TABULAR_CLASSIFICATION_GCS_SOURCE == gcs_source_uris[0]
            assert (
                tabular_dataset.metadata_schema_uri
                == aiplatform.schema.dataset.metadata.tabular
            )

        finally:
            if tabular_dataset is not None:
                tabular_dataset.delete()

    def test_create_tabular_dataset_from_dataframe(self, bigquery_dataset):
        bq_staging_table = f"bq://{_TEST_PROJECT}.{bigquery_dataset.dataset_id}.test_table{uuid.uuid4()}"

        try:
            tabular_dataset = aiplatform.TabularDataset.create_from_dataframe(
                df_source=_TEST_DATAFRAME,
                staging_path=bq_staging_table,
                display_name=self._make_display_name(
                    key="create_and_import_dataset_from_dataframe"
                ),
            )

            """Use the Dataset.create_from_dataframe() method to create a new tabular dataset.
            Then confirm the dataset was successfully created and references the BQ source."""
            gapic_metadata = tabular_dataset.to_dict()["metadata"]
            bq_source = gapic_metadata["inputConfig"]["bigquerySource"]["uri"]

            assert bq_staging_table == bq_source
            assert (
                tabular_dataset.metadata_schema_uri
                == aiplatform.schema.dataset.metadata.tabular
            )
        finally:
            if tabular_dataset is not None:
                tabular_dataset.delete()

    def test_create_tabular_dataset_from_dataframe_with_provided_schema(
        self, bigquery_dataset
    ):
        """Use the Dataset.create_from_dataframe() method to create a new tabular dataset,
        passing in the optional `bq_schema` argument. Then confirm the dataset was successfully
        created and references the BQ source."""

        try:
            bq_staging_table = f"bq://{_TEST_PROJECT}.{bigquery_dataset.dataset_id}.test_table{uuid.uuid4()}"

            tabular_dataset = aiplatform.TabularDataset.create_from_dataframe(
                df_source=_TEST_DATAFRAME,
                staging_path=bq_staging_table,
                display_name=self._make_display_name(
                    key="create_and_import_dataset_from_dataframe"
                ),
                bq_schema=_TEST_DATAFRAME_BQ_SCHEMA,
            )

            gapic_metadata = tabular_dataset.to_dict()["metadata"]
            bq_source = gapic_metadata["inputConfig"]["bigquerySource"]["uri"]

            assert bq_staging_table == bq_source
            assert (
                tabular_dataset.metadata_schema_uri
                == aiplatform.schema.dataset.metadata.tabular
            )
        finally:
            tabular_dataset.delete()

    def test_create_time_series_dataset(self):
        """Use the Dataset.create() method to create a new time series dataset.
        Then confirm the dataset was successfully created and references GCS source."""

        try:
            time_series_dataset = aiplatform.TimeSeriesDataset.create(
                display_name=self._make_display_name(key="create_time_series_dataset"),
                bq_source=[_TEST_FORECASTING_BQ_SOURCE],
                create_request_timeout=None,
            )

            gapic_metadata = time_series_dataset.to_dict()["metadata"]
            bq_source_uri = gapic_metadata["inputConfig"]["bigquerySource"]["uri"]

            assert _TEST_FORECASTING_BQ_SOURCE == bq_source_uri
            assert (
                time_series_dataset.metadata_schema_uri
                == aiplatform.schema.dataset.metadata.time_series
            )

        finally:
            if time_series_dataset is not None:
                time_series_dataset.delete()

    def test_export_data(self, storage_client, staging_bucket):
        """Get an existing dataset, export data to a newly created folder in
        Google Cloud Storage, then verify data was successfully exported."""

        dataset = aiplatform.TextDataset(dataset_name=_TEST_TEXT_DATASET_ID)

        exported_files = dataset.export_data(output_dir=f"gs://{staging_bucket.name}")

        assert len(exported_files)  # Ensure at least one GCS path was returned

        exported_file = exported_files[0]
        bucket, prefix = utils.extract_bucket_and_prefix_from_gcs_path(exported_file)

        bucket = storage_client.get_bucket(bucket)
        blob = bucket.get_blob(prefix)

        assert blob  # Verify the returned GCS export path exists
