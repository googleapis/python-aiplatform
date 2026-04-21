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
from google.genai import types as genai_types
import pytest


TEST_PROMPT_DATASET_ID = "8005484238453342208"
TEST_VARIABLES = [
    {"name": genai_types.Part(text="Alice")},
    {"name": genai_types.Part(text="Bob")},
]
TEST_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {"response": {"type": "string"}},
}
TEST_PROMPT = types.Prompt(
    prompt_data=types.PromptData(
        contents=[
            genai_types.Content(
                role="user",
                parts=[genai_types.Part(text="Hello, {name}! How are you?")],
            )
        ],
        safety_settings=[
            genai_types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE",
                method="SEVERITY",
            ),
        ],
        generation_config=genai_types.GenerationConfig(
            temperature=0.1,
            candidate_count=1,
            top_p=0.95,
            top_k=40,
            response_modalities=["TEXT"],
            response_schema=TEST_RESPONSE_SCHEMA,
        ),
        system_instruction=genai_types.Content(
            parts=[genai_types.Part(text="Please answer in a short sentence.")]
        ),
        tools=[
            genai_types.Tool(
                google_search_retrieval=genai_types.GoogleSearchRetrieval(
                    dynamic_retrieval_config=genai_types.DynamicRetrievalConfig(
                        mode="MODE_DYNAMIC"
                    )
                )
            ),
        ],
        tool_config=genai_types.ToolConfig(
            retrieval_config=genai_types.RetrievalConfig(
                lat_lng=genai_types.LatLng(latitude=37.7749, longitude=-122.4194)
            )
        ),
        model="gemini-2.0-flash-001",
        variables=TEST_VARIABLES,
    ),
)
TEST_CREATE_PROMPT_CONFIG = types.CreatePromptConfig(
    prompt_display_name="my_prompt",
)

TEST_CREATE_PROMPT_VERSION_CONFIG = types.CreatePromptVersionConfig(
    version_display_name="my_version",
)


def test_update_creates_new_version(client):
    updated_prompt = TEST_PROMPT.model_copy(deep=True)
    updated_prompt.prompt_data.contents[0].parts[0].text = "Is this Alice?"

    prompt_resource = client.prompts.update(
        prompt_id=TEST_PROMPT_DATASET_ID,
        prompt=updated_prompt,
        config=types.UpdatePromptConfig(
            version_display_name="my_version",
        ),
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.prompt_data.contents[0].parts[0].text == "Is this Alice?"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompts.update",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_update_async(client):
    updated_prompt = TEST_PROMPT.model_copy(deep=True)
    updated_prompt.prompt_data.contents[0].parts[0].text = "Is this Alice?"

    prompt_resource = await client.aio.prompts.update(
        prompt_id=TEST_PROMPT_DATASET_ID,
        prompt=updated_prompt,
        config=types.UpdatePromptConfig(
            version_display_name="my_updated_version",
        ),
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.prompt_data.contents[0].parts[0].text == "Is this Alice?"
