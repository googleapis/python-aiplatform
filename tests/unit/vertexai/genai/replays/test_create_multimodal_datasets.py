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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

import pytest

METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/multimodal_1.0.0.yaml"
)
BIGQUERY_TABLE_NAME = "vertex-sdk-dev.multimodal_dataset.test-table"


def test_create_dataset(client):
    create_dataset_operation = client.datasets._create_multimodal_dataset(
        name="projects/vertex-sdk-dev/locations/us-central1",
        display_name="test-display-name",
        metadata_schema_uri=METADATA_SCHEMA_URI,
        metadata={
            "inputConfig": {
                "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
            },
        },
    )
    assert isinstance(create_dataset_operation, types.MultimodalDatasetOperation)
    assert create_dataset_operation


def test_create_dataset_from_bigquery(client):
    dataset = client.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"


def test_create_dataset_from_bigquery_without_bq_prefix(client):
    dataset = client.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": BIGQUERY_TABLE_NAME},
                },
            },
        },
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_dataset_async(client):
    create_dataset_operation = await client.aio.datasets._create_multimodal_dataset(
        name="projects/vertex-sdk-dev/locations/us-central1",
        display_name="test-display-name",
        metadata_schema_uri=METADATA_SCHEMA_URI,
        metadata={
            "inputConfig": {
                "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
            },
        },
    )
    assert isinstance(create_dataset_operation, types.MultimodalDatasetOperation)
    assert create_dataset_operation


@pytest.mark.asyncio
async def test_create_dataset_from_bigquery_async(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"


@pytest.mark.asyncio
async def test_create_dataset_from_bigquery_async_with_timeout(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        config=types.CreateMultimodalDatasetConfig(timeout=120),
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        },
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"


@pytest.mark.asyncio
async def test_create_dataset_from_bigquery_async_without_bq_prefix(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "description": "test-description-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": BIGQUERY_TABLE_NAME},
                },
            },
        },
    )
    assert isinstance(dataset, types.MultimodalDataset)
    assert dataset.display_name == "test-from-bigquery"
