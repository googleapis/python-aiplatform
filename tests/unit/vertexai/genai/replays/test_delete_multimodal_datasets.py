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

BIGQUERY_TABLE_NAME = "vertex-sdk-dev.multimodal_dataset.test-table"


def test_delete_dataset(client):
    dataset = client.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    name = dataset.name.split("/datasets/")[1]

    operation = client.datasets._delete_multimodal_dataset(
        name=name,
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)
    assert operation.done


def test_delete_dataset_with_public_method(client):
    dataset = client.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    name = dataset.name.split("/datasets/")[1]

    operation = client.datasets.delete_multimodal_dataset(
        name=name,
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)
    assert operation.done


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_delete_dataset_async(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    name = dataset.name.split("/datasets/")[1]

    operation = await client.aio.datasets._delete_multimodal_dataset(
        name=name,
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)
    assert operation


@pytest.mark.asyncio
async def test_delete_dataset_with_public_method_async(client):
    dataset = await client.aio.datasets.create_from_bigquery(
        multimodal_dataset={
            "display_name": "test-from-bigquery",
            "metadata": {
                "inputConfig": {
                    "bigquerySource": {"uri": f"bq://{BIGQUERY_TABLE_NAME}"},
                },
            },
        }
    )
    name = dataset.name.split("/datasets/")[1]

    operation = await client.aio.datasets.delete_multimodal_dataset(
        name=name,
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)
    assert operation.done
