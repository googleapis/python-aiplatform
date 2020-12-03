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

import pytest

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.api_core import operation

from google.cloud import aiplatform
from google.cloud.aiplatform import TabularDataset
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import schema

from google.cloud.aiplatform_v1beta1 import DatasetServiceClient
from google.cloud.aiplatform_v1beta1 import Dataset as GapicDataset

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/datasets/{_TEST_ID}"

_TEST_METADATA_SCHEMA_URI_TABULAR = schema.dataset.metadata.tabular
_TEST_METADATA_SCHEMA_URI_NONTABULAR = schema.dataset.metadata.image

_TEST_SOURCE_URI_GCS = "gs://my-bucket/my_index_file.jsonl"

_TEST_SOURCE_URI_BQ = "bigquery://my-project/my-dataset"

_TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}
_TEST_DISPLAY_NAME = "my_dataset_1234"
_TEST_METADATA_TABULAR_GCS = {
    "input_config": {"gcs_source": {"uri": [_TEST_SOURCE_URI_GCS]}}
}
_TEST_METADATA_TABULAR_BQ = {
    "input_config": {"bigquery_source": {"uri": _TEST_SOURCE_URI_BQ}}
}


class TestTabularDataset:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    @pytest.fixture
    def get_tabular_dataset_mock(self):
        with patch.object(DatasetServiceClient, "get_dataset") as get_dataset_mock:
            get_dataset_mock.return_value = GapicDataset(
                display_name=_TEST_DISPLAY_NAME,
                metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
                labels=_TEST_LABEL,
                name=_TEST_NAME,
            )
            yield get_dataset_mock

    @pytest.fixture
    def get_nontabular_dataset_mock(self):
        with patch.object(DatasetServiceClient, "get_dataset") as get_dataset_mock:
            get_dataset_mock.return_value = GapicDataset(
                display_name=_TEST_DISPLAY_NAME,
                metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_NONTABULAR,
                labels=_TEST_LABEL,
                name=_TEST_NAME,
            )
            yield get_dataset_mock

    @pytest.fixture
    def create_dataset_mock(self):
        with patch.object(
            DatasetServiceClient, "create_dataset"
        ) as create_dataset_mock:
            create_dataset_lro_mock = mock.Mock(operation.Operation)
            create_dataset_lro_mock.result.return_value = GapicDataset(
                display_name=_TEST_DISPLAY_NAME, name=_TEST_NAME,
            )
            create_dataset_mock.return_value = create_dataset_lro_mock
            yield create_dataset_mock

    def test_init_tabular_dataset(self, get_tabular_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)
        TabularDataset(dataset_name=_TEST_NAME)
        get_tabular_dataset_mock.assert_called_once_with(name=_TEST_NAME)

    @pytest.mark.usefixtures("get_nontabular_dataset_mock")
    def test_init_nontabular_dataset(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(Exception):
            TabularDataset(dataset_name=_TEST_NAME)

    @pytest.mark.usefixtures("get_tabular_dataset_mock")
    def test_create_dataset_tabular(self, create_dataset_mock):
        aiplatform.init(project=_TEST_PROJECT)

        TabularDataset.create(
            display_name=_TEST_DISPLAY_NAME,
            bq_source=_TEST_SOURCE_URI_BQ,
            labels=_TEST_LABEL,
        )

        expected_dataset = GapicDataset(
            display_name=_TEST_DISPLAY_NAME,
            metadata_schema_uri=_TEST_METADATA_SCHEMA_URI_TABULAR,
            labels=_TEST_LABEL,
            metadata=_TEST_METADATA_TABULAR_BQ,
        )

        create_dataset_mock.assert_called_once_with(
            parent=_TEST_PARENT, dataset=expected_dataset
        )

    def test_create_tabular_dataset_with_both_source(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(Exception):
            TabularDataset.create(
                display_name=_TEST_DISPLAY_NAME,
                gcs_source=_TEST_SOURCE_URI_GCS,
                bq_source=_TEST_SOURCE_URI_BQ,
            )

    def test_create_tabular_dataset_with_no_source(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(Exception):
            TabularDataset.create(display_name=_TEST_DISPLAY_NAME,)

    @pytest.mark.usefixtures("get_tabular_dataset_mock")
    def test_no_import_data_method(self):
        aiplatform.init(project=_TEST_PROJECT)
        my_dataset = TabularDataset(dataset_name=_TEST_NAME)
        with pytest.raises(Exception):
            my_dataset.import_data
