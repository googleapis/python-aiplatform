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


def test_assess_dataset(client):
    operation = client.datasets._assess_multimodal_dataset(
        name=DATASET,
        tuning_resource_usage_assessment_config=types.TuningResourceUsageAssessmentConfig(
            model_name="gemini-2.5-flash-001"
        ),
        gemini_request_read_config=types.GeminiRequestReadConfig(
            template_config=types.GeminiTemplateConfig(
                gemini_example=types.GeminiExample(
                    contents=[
                        {
                            "role": "user",
                            "parts": [{"text": "What is the capital of {name}?"}],
                        }
                    ],
                ),
            ),
        ),
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)


def test_assess_tuning_resources(client):
    response = client.datasets.assess_tuning_resources(
        dataset_name=DATASET,
        model_name="gemini-2.5-flash-001",
        template_config=types.GeminiTemplateConfig(
            gemini_example=types.GeminiExample(
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": "What is the capital of {name}?"}],
                    }
                ],
            ),
        ),
    )
    assert isinstance(response, types.TuningResourceUsageAssessmentResult)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_assess_dataset_async(client):
    operation = await client.aio.datasets._assess_multimodal_dataset(
        name=DATASET,
        tuning_resource_usage_assessment_config=types.TuningResourceUsageAssessmentConfig(
            model_name="gemini-2.5-flash-001"
        ),
        gemini_request_read_config=types.GeminiRequestReadConfig(
            template_config=types.GeminiTemplateConfig(
                gemini_example=types.GeminiExample(
                    contents=[
                        {
                            "role": "user",
                            "parts": [{"text": "What is the capital of {name}?"}],
                        }
                    ],
                ),
            ),
        ),
    )
    assert isinstance(operation, types.MultimodalDatasetOperation)


@pytest.mark.asyncio
async def test_assess_tuning_resources_async(client):
    response = await client.aio.datasets.assess_tuning_resources(
        dataset_name=DATASET,
        model_name="gemini-2.5-flash-001",
        template_config=types.GeminiTemplateConfig(
            gemini_example=types.GeminiExample(
                contents=[
                    {
                        "role": "user",
                        "parts": [{"text": "What is the capital of {name}?"}],
                    }
                ],
            ),
        ),
    )
    assert isinstance(response, types.TuningResourceUsageAssessmentResult)
