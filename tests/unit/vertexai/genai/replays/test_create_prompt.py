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
TEST_CONFIG = types.CreatePromptConfig(
    prompt_display_name="my_prompt",
    version_display_name="my_version",
)


def test_create_dataset(client):
    create_dataset_operation = client.prompt_management._create_dataset_resource(
        name="projects/vertex-sdk-dev/locations/us-central1",
        display_name="test display name",
        metadata_schema_uri="gs://google-cloud-aiplatform/schema/dataset/metadata/text_prompt_1.0.0.yaml",
        metadata={
            "promptType": "freeform",
            "promptApiSchema": {
                "multimodalPrompt": {
                    "promptMessage": {
                        "contents": [
                            {
                                "role": "user",
                                "parts": [{"text": "Hello, {name}! How are you?"}],
                            }
                        ],
                        "safety_settings": [
                            {
                                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                                "threshold": "BLOCK_MEDIUM_AND_ABOVE",
                                "method": "SEVERITY",
                            }
                        ],
                        "generation_config": {"temperature": 0.1},
                        "model": "projects/vertex-sdk-dev/locations/us-central1/publishers/google/models/gemini-2.0-flash-001",
                        "system_instruction": {
                            "role": "user",
                            "parts": [{"text": "Please answer in a short sentence."}],
                        },
                    }
                },
                "apiSchemaVersion": "1.0.0",
                "executions": [
                    {
                        "arguments": {
                            "name": {"partList": {"parts": [{"text": "Alice"}]}}
                        }
                    },
                    {"arguments": {"name": {"partList": {"parts": [{"text": "Bob"}]}}}},
                ],
            },
        },
        model_reference="gemini-2.0-flash-001",
    )
    assert isinstance(create_dataset_operation, types.DatasetOperation)
    assert create_dataset_operation


def test_create_dataset_version(client):
    dataset_version_resource = (
        client.prompt_management._create_dataset_version_resource(
            dataset_name=TEST_PROMPT_DATASET_ID,
            display_name="my new version yay",
        )
    )
    assert isinstance(dataset_version_resource, types.DatasetOperation)


def test_create_version_e2e(client):
    prompt_resource = client.prompt_management.create_version(
        prompt=TEST_PROMPT,
        config=TEST_CONFIG,
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)

    # Test local prompt resource is the same after calling get()
    retrieved_prompt = client.prompt_management.get(prompt_id=prompt_resource.prompt_id)
    assert (
        retrieved_prompt.prompt_data.system_instruction
        == prompt_resource.prompt_data.system_instruction
    )
    assert (
        retrieved_prompt.prompt_data.variables[0]["name"].text
        == TEST_VARIABLES[0]["name"].text
    )
    assert (
        retrieved_prompt.prompt_data.generation_config.temperature
        == prompt_resource.prompt_data.generation_config.temperature
    )
    assert (
        retrieved_prompt.prompt_data.safety_settings
        == prompt_resource.prompt_data.safety_settings
    )
    assert retrieved_prompt.prompt_data.model == prompt_resource.prompt_data.model
    assert (
        retrieved_prompt.prompt_data.tool_config
        == prompt_resource.prompt_data.tool_config
    )
    assert (
        retrieved_prompt.prompt_data.generation_config
        == prompt_resource.prompt_data.generation_config
    )

    # Test calling create_version again uses dataset from local Prompt resource.
    prompt_resource_2 = client.prompt_management.create_version(
        prompt=TEST_PROMPT,
        config=types.CreatePromptConfig(
            version_display_name="my_version",
        ),
    )
    assert prompt_resource_2.dataset.name == prompt_resource.dataset.name


def test_create_version_in_existing_dataset(client):
    prompt_resource = client.prompt_management.create_version(
        prompt=TEST_PROMPT,
        config=types.CreatePromptConfig(
            prompt_id=TEST_PROMPT_DATASET_ID,
            prompt_display_name=TEST_CONFIG.prompt_display_name,
            version_display_name="my_version_existing_dataset",
        ),
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.dataset.name.endswith(TEST_PROMPT_DATASET_ID)


def test_create_version_with_version_name(client):
    version_name = "a_new_version_yay"
    prompt_resource = client.prompt_management.create_version(
        prompt=TEST_PROMPT,
        config=types.CreatePromptConfig(
            version_display_name=version_name,
        ),
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.dataset_version.display_name == version_name


def test_create_version_with_file_data(client):
    version_name = "prompt with file data"

    audio_file_part = genai_types.Part(
        file_data=genai_types.FileData(
            file_uri="https://generativelanguage.googleapis.com/v1beta/files/57w3vpfomj71",
            mime_type="video/mp4",
        ),
    )

    prompt_resource = client.prompt_management.create_version(
        prompt=types.Prompt(
            prompt_data=types.PromptData(
                contents=[
                    genai_types.Content(
                        parts=[
                            audio_file_part,
                            genai_types.Part(text="What is this recording about?"),
                        ]
                    )
                ],
                system_instruction=genai_types.Content(
                    parts=[genai_types.Part(text="Answer in three sentences.")]
                ),
                generation_config=genai_types.GenerationConfig(temperature=0.1),
                safety_settings=[
                    genai_types.SafetySetting(
                        category="HARM_CATEGORY_DANGEROUS_CONTENT",
                        threshold="BLOCK_MEDIUM_AND_ABOVE",
                        method="SEVERITY",
                    )
                ],
                model="gemini-2.0-flash-001",
            ),
        ),
        config=types.CreatePromptConfig(
            version_display_name=version_name,
            prompt_display_name="my prompt with file data",
        ),
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.dataset_version.display_name == version_name

    # Confirm file data is preserved when we retrieve the prompt.
    retrieved_prompt = client.prompt_management.get(
        prompt_id=prompt_resource.prompt_id,
    )
    assert (
        retrieved_prompt.prompt_data.contents[0].parts[0].file_data.file_uri
        == audio_file_part.file_data.file_uri
    )
    assert (
        retrieved_prompt.prompt_data.contents[0].parts[0].file_data.display_name
        == audio_file_part.file_data.display_name
    )

    # Test assemble_contents on the prompt works.
    contents = retrieved_prompt.assemble_contents()
    assert contents[0] == prompt_resource.prompt_data.contents[0]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompt_management.create_version",
)
