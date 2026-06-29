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

from unittest import mock

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import _datasets_utils
from agentplatform._genai import types

import pandas as pd
import pytest

METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/multimodal_1.0.0.yaml"
)
BIGQUERY_TABLE_NAME = "vertex-sdk-dev.multimodal_dataset.test-table"
DATASET = "projects/vertex-sdk-dev/locations/us-central1/datasets/8810841321427173376"


@pytest.fixture
def mock_import_bigframes(is_replay_mode):
    if is_replay_mode:
        with mock.patch.object(
            _datasets_utils, "_try_import_bigframes"
        ) as mock_try_import:
            bigframes = mock.MagicMock()
            dataframe = (
                bigframes.connect.return_value.__enter__.return_value.read_gbq.return_value
            )
            dataframe.head.return_value.to_pandas.return_value = pd.DataFrame(
                {"request": ["What is the capital of France?"]}
            )
            mock_try_import.return_value = bigframes
            yield mock_try_import
    else:
        yield None


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


def test_assemble_dataset_public(client, mock_import_bigframes):
    table_id, dataframe = client.datasets.assemble(
        name=DATASET,
        gemini_request_read_config=types.GeminiRequestReadConfig(
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
            )
        ),
        load_dataframe=True,
    )
    assert table_id.startswith(BIGQUERY_TABLE_NAME)
    assert not table_id.startswith("bq://")
    assert dataframe is not None
    head_rows = dataframe.head().to_pandas()
    assert head_rows["request"].tolist() == ["What is the capital of France?"]


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
async def test_assemble_dataset_public_async(client, mock_import_bigframes):
    table_id, dataframe = await client.aio.datasets.assemble(
        name=DATASET,
        gemini_request_read_config=types.GeminiRequestReadConfig(
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
            )
        ),
        load_dataframe=True,
    )
    assert table_id.startswith(BIGQUERY_TABLE_NAME)
    assert not table_id.startswith("bq://")
    assert dataframe is not None
    head_rows = dataframe.head().to_pandas()
    assert head_rows["request"].tolist() == ["What is the capital of France?"]
