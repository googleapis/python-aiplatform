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

import importlib
import pytest

import bigframes.pandas as bpd
import pandas as pd

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.preview import datasets
from vertexai.preview import prompts

from tests.system.aiplatform import e2e_base


_TEST_PROJECT = e2e_base._PROJECT
_TEST_LOCATION = e2e_base._LOCATION

_TEST_DATASET = [
    {
        "Question": "What is the leading cause of delays on the Forest Floor Transit system?",
        "Answer": "A family of snails attempting a group commute during rush hour.",
    },
    {
        "Question": "Which item is considered the height of fashion in Badger Burrow Boutiques?",
        "Answer": "Elaborately decorated digging claws (preferably mud-resistant).",
    },
    {
        "Question": "What is the official slogan of the Squirrel Savings & Hoard Bank?",
        "Answer": '"Your nuts are safe with us... probably."',
    },
    {
        "Question": "Why was the annual Berry Festival postponed this year by Mayor Bear?",
        "Answer": "He accidentally ate all the prize-winning blueberries during 'testing'.",
    },
    {
        "Question": "What subject do young foxes complain about most in school?",
        "Answer": "Advanced Napping Techniques (they find it too easy).",
    },
]

Content = datasets.GeminiExample.Content
Part = datasets.GeminiExample.Part

_TEST_BIGQUERY_DATASET = "bigquery-public-data.ml_datasets.penguins"
_TEST_TEMPLATE_CONFIG = datasets.GeminiTemplateConfig(
    gemini_example=datasets.GeminiExample(
        contents=[
            Content(role="user", parts=[Part.from_text("Species: {species}")]),
            Content(role="model", parts=[Part.from_text("Island: {island}")]),
        ]
    )
)


def _uri_to_table_id(bq_uri):
    if bq_uri.startswith("bq://"):
        return bq_uri[len("bq://") :]
    return bq_uri


@pytest.mark.usefixtures(
    "prepare_bigquery_dataset", "delete_bigquery_dataset", "copy_sample_data"
)
class TestDataset(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-multimodal-dataset-test"

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @pytest.fixture(scope="class")
    def copy_sample_data(self, shared_state):
        assert shared_state["bigquery_client"]
        assert shared_state["bigquery_dataset_id"]

        bq_client = shared_state["bigquery_client"]
        bq_dataset = shared_state["bigquery_dataset_id"]
        bq_test_table = f"{bq_dataset}.test_data"
        copy_job = bq_client.copy_table(
            sources=_TEST_BIGQUERY_DATASET, destination=bq_test_table
        )
        copy_job.result()

        shared_state["bigquery_test_table"] = bq_test_table
        # The full dataset is deleted in `delete_bigquery_dataset`, so no need
        # to clean up the table.
        yield

    def test_create_new_dataset_from_bq_table_uri(self, shared_state):
        assert shared_state["bigquery_test_table"]
        bigquery_table = f"bq://{shared_state['bigquery_test_table']}"
        display_name = "test dataset"
        labels = {"label1": "value1", "label2": "value2"}
        try:
            ds = datasets.MultimodalDataset.from_bigquery(
                bigquery_source=bigquery_table, display_name=display_name, labels=labels
            )
            assert ds.display_name == display_name
            assert ds.bigquery_table == bigquery_table
            assert ds.labels == labels
            assert ds.location == _TEST_LOCATION
        finally:
            ds.delete()

    def test_create_new_dataset_from_bq_table_id(self, shared_state):
        assert shared_state["bigquery_test_table"]
        bigquery_table = f"{shared_state['bigquery_test_table']}"
        display_name = "test dataset"
        labels = {"label1": "value1", "label2": "value2"}
        try:
            ds = datasets.MultimodalDataset.from_bigquery(
                bigquery_source=bigquery_table, display_name=display_name, labels=labels
            )
            assert ds.display_name == display_name
            assert ds.bigquery_table == bigquery_table
            assert ds.labels == labels
            assert ds.location == _TEST_LOCATION
        finally:
            ds.delete()

    def test_create_from_pandas(self, shared_state):
        assert shared_state["bigquery_client"]
        bigquery_client = shared_state["bigquery_client"]

        try:
            df = pd.DataFrame(_TEST_DATASET)
            ds = datasets.MultimodalDataset.from_pandas(dataframe=df)

            # Set these options after the `from_pandas` call to ensure that it
            # works without global bpd configs.
            bpd.options.bigquery.project = _TEST_PROJECT
            bpd.options.bigquery.location = _TEST_LOCATION

            table_id = _uri_to_table_id(ds.bigquery_table)
            assert table_id.startswith(
                f"{_TEST_PROJECT}.vertex_datasets_{_TEST_LOCATION.replace('-', '_')}"
            )

            bf_dataframe = bpd.read_gbq(table_id)
            assert len(bf_dataframe) == len(_TEST_DATASET)
            assert set(bf_dataframe.columns) == {"Question", "Answer"}

        finally:
            bigquery_client.delete_table(table_id, not_found_ok=True)
            ds.delete()

    def test_create_from_bigframes(self, shared_state):
        assert shared_state["bigquery_client"]
        bigquery_client = shared_state["bigquery_client"]

        bpd.options.bigquery.project = _TEST_PROJECT
        bpd.options.bigquery.location = _TEST_LOCATION

        try:
            pd_df = pd.DataFrame(_TEST_DATASET)
            bf_df = bpd.read_pandas(pd_df)
            ds = datasets.MultimodalDataset.from_bigframes(dataframe=bf_df)

            table_id = _uri_to_table_id(ds.bigquery_table)
            assert table_id.startswith(
                f"{_TEST_PROJECT}.vertex_datasets_{_TEST_LOCATION.replace('-', '_')}"
            )

            imported_bf_dataframe = bpd.read_gbq(table_id)
            assert len(imported_bf_dataframe) == len(_TEST_DATASET)
            assert set(imported_bf_dataframe.columns) == {"Question", "Answer"}
        finally:
            bigquery_client.delete_table(table_id, not_found_ok=True)
            ds.delete()

    def test_export_to_bigframes(self, shared_state):
        assert shared_state["bigquery_client"]
        bigquery_client = shared_state["bigquery_client"]

        bpd.options.bigquery.project = _TEST_PROJECT
        bpd.options.bigquery.location = _TEST_LOCATION

        try:
            bf_df_source = bpd.DataFrame(_TEST_DATASET)
            ds = datasets.MultimodalDataset.from_bigframes(dataframe=bf_df_source)
            bf_df_exported = ds.to_bigframes()
            table_id = _uri_to_table_id(ds.bigquery_table)

            assert len(bf_df_exported) == len(_TEST_DATASET)
            assert set(bf_df_exported.columns) == {"Question", "Answer"}
        finally:
            bigquery_client.delete_table(table_id, not_found_ok=True)
            ds.delete()

    def test_assemble_dataset(self, shared_state):
        assert shared_state["bigquery_client"]
        assert shared_state["bigquery_test_table"]
        bigquery_client = shared_state["bigquery_client"]
        bigquery_table = f"bq://{shared_state['bigquery_test_table']}"

        try:
            ds = datasets.MultimodalDataset.from_bigquery(bigquery_uri=bigquery_table)
            ds.attach_template_config(template_config=_TEST_TEMPLATE_CONFIG)
            bf_uri, dataframe = ds.assemble()
            assert bf_uri
            assert len(dataframe) > 0
        finally:
            ds.delete()
            bigquery_client.delete_table(_uri_to_table_id(bf_uri), not_found_ok=True)

    def test_assess_tuning_validity(self, shared_state):
        assert shared_state["bigquery_test_table"]
        bigquery_table = f"bq://{shared_state['bigquery_test_table']}"

        try:
            ds = datasets.MultimodalDataset.from_bigquery(bigquery_uri=bigquery_table)
            ds.attach_template_config(template_config=_TEST_TEMPLATE_CONFIG)
            validation_result = ds.assess_tuning_validity(
                model_name="gemini-1.5-flash-002", dataset_usage="SFT_TRAINING"
            )
            assert not validation_result.errors
        finally:
            ds.delete()

    def test_assess_tuning_resources(self, shared_state):
        assert shared_state["bigquery_test_table"]
        bigquery_table = f"bq://{shared_state['bigquery_test_table']}"

        try:
            ds = datasets.MultimodalDataset.from_bigquery(bigquery_uri=bigquery_table)
            ds.attach_template_config(template_config=_TEST_TEMPLATE_CONFIG)
            tuning_resources = ds.assess_tuning_resources(
                model_name="gemini-1.5-flash-002"
            )
            assert tuning_resources.billable_character_count > 0
            assert tuning_resources.token_count > 0
        finally:
            ds.delete()

    def test_attach_prompt_as_template_config(self, shared_state):
        assert shared_state["bigquery_test_table"]
        bigquery_table = f"bq://{shared_state['bigquery_test_table']}"

        try:
            ds = datasets.MultimodalDataset.from_bigquery(bigquery_uri=bigquery_table)
            prompt = prompts.create_version(
                prompts.Prompt(prompt_data="Tell me about this species: {species}")
            )
            ds.attach_template_config(prompt=prompt)

            _, bf = ds.assemble()
            assert len(bf) > 0
            request = bf.iloc[0]["request"]
            assert "Tell me about this species: " in request
        finally:
            ds.delete()
            prompts.delete(prompt.prompt_id)
