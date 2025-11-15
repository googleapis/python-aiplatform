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
DATASET = "8810841321427173376"


def test_assemble_dataset(client):
    operation = client.datasets._assemble_multimodal_dataset(
        name=DATASET,
        gemini_request_read_config={
            "template_config": {
                "field_mapping": {"question": "questionColumn"},
            },
        },
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)


def test_assemble_dataset_public(client):
    bigquery_destination = client.datasets.assemble(
        name=DATASET,
        template_config=types.GeminiTemplateConfig(
            gemini_example=types.GeminiExample(
                model="gemini-1.5-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": "What is the capital of {name}?"}],
                    }
                ],
            ),
        ),
    )
    assert bigquery_destination.startswith(f"bq://{BIGQUERY_TABLE_NAME}")


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_assemble_dataset_async(client):
    operation = await client.aio.datasets._assemble_multimodal_dataset(
        name=DATASET,
        gemini_request_read_config={
            "template_config": {
                "field_mapping": {"question": "questionColumn"},
            },
        },
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)


@pytest.mark.asyncio
async def test_assemble_dataset_public_async(client):
    bigquery_destination = await client.aio.datasets.assemble(
        name=DATASET,
        template_config=types.GeminiTemplateConfig(
            gemini_example=types.GeminiExample(
                model="gemini-1.5-flash",
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": "What is the capital of {name}?"}],
                    }
                ],
            ),
        ),
    )
    assert bigquery_destination.startswith(f"bq://{BIGQUERY_TABLE_NAME}")
