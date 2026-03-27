# Copyright 2025 Google LLC
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
"""Tests for multimodal datasets."""

from vertexai._genai import types


class TestMultimodalDataset:

    def test_read_config(self):
        dataset = types.MultimodalDataset(
            metadata={
                "gemini_request_read_config": {
                    "assembled_request_column_name": "test_column",
                },
            },
        )

        assert isinstance(dataset.read_config, types.GeminiRequestReadConfig)
        assert dataset.read_config.assembled_request_column_name == "test_column"

    def test_read_config_empty(self):
        dataset = types.MultimodalDataset()
        assert dataset.read_config is None

    def test_set_read_config(self):
        dataset = types.MultimodalDataset()

        dataset.set_read_config(
            read_config={
                "assembled_request_column_name": "test_column",
            },
        )

        assert isinstance(dataset, types.MultimodalDataset)
        assert (
            dataset.metadata.gemini_request_read_config.assembled_request_column_name
            == "test_column"
        )

    def test_set_read_config_preserves_other_fields(self):
        dataset = types.MultimodalDataset(
            metadata={
                "inputConfig": {
                    "bigquerySource": {"uri": "bq://test_table"},
                },
            },
        )

        dataset.set_read_config(
            read_config={
                "assembled_request_column_name": "test_column",
            },
        )

        assert isinstance(dataset, types.MultimodalDataset)
        assert (
            dataset.metadata.gemini_request_read_config.assembled_request_column_name
            == "test_column"
        )
        assert dataset.metadata.input_config.bigquery_source.uri == "bq://test_table"

    def test_bigquery_uri(self):
        dataset = types.MultimodalDataset(
            metadata={
                "inputConfig": {
                    "bigquerySource": {"uri": "bq://project.dataset.table"},
                },
            },
        )

        assert dataset.bigquery_uri == "bq://project.dataset.table"

    def test_bigquery_uri_empty(self):
        dataset = types.MultimodalDataset()
        assert dataset.bigquery_uri is None

    def test_set_bigquery_uri(self):
        dataset = types.MultimodalDataset()

        dataset.set_bigquery_uri("bq://project.dataset.table")

        assert isinstance(dataset, types.MultimodalDataset)
        assert (
            dataset.metadata.input_config.bigquery_source.uri
            == "bq://project.dataset.table"
        )

    def test_set_bigquery_uri_without_prefix(self):
        dataset = types.MultimodalDataset()

        dataset.set_bigquery_uri("project.dataset.table")

        assert isinstance(dataset, types.MultimodalDataset)
        assert (
            dataset.metadata.input_config.bigquery_source.uri
            == "bq://project.dataset.table"
        )

    def test_set_bigquery_uri_preserves_other_fields(self):
        dataset = types.MultimodalDataset(
            metadata={
                "gemini_request_read_config": {
                    "assembled_request_column_name": "test_column",
                },
            },
        )

        dataset.set_bigquery_uri("bq://test_table")

        assert isinstance(dataset, types.MultimodalDataset)
        assert dataset.metadata.input_config.bigquery_source.uri == "bq://test_table"
        assert (
            dataset.metadata.gemini_request_read_config.assembled_request_column_name
            == "test_column"
        )
