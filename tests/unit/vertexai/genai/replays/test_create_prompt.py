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
TEST_PROMPT = types.Prompt(
    prompt_data=genai_types.Part(text="Hello, {name}! How are you?"),
    prompt_name="test_prompt",
    system_instruction="Please answer in a short sentence.",
    variables=[{"name": types.Part(text="Alice")}],
    generation_config=genai_types.GenerationConfig(
        temperature=0.1,
        response_schema={
        "type": "object",
        "properties": {
            "greeting": {
            "type": "string"
            },
        },
        "required": [
            "greeting",
        ]
        },
    ),
    safety_settings=genai_types.SafetySetting(
        category="HARM_CATEGORY_DANGEROUS_CONTENT",
        threshold="BLOCK_MEDIUM_AND_ABOVE",
        method="SEVERITY",
    ),
    model_name="gemini-2.0-flash-001",
)


def test_create_dataset(client):
    create_dataset_operation = client.prompt_management._create_dataset_resource(
        config=types.CreateDatasetConfig(should_return_http_response=True),
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
                        "model": "projects/vertex-sdk-dev/locations/us-central1/publishers/google/models/"
                        "gemini-2.0-flash-001",
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
    assert isinstance(create_dataset_operation, types.CreateDatasetOperationMetadata)
    assert create_dataset_operation.sdk_http_response.body is not None


def test_create_dataset_version(client):
    dataset_version_resource = (
        client.prompt_management._create_dataset_version_resource(
            dataset_name=TEST_PROMPT_DATASET_ID,
            display_name="my new version yay",
        )
    )
    assert isinstance(
        dataset_version_resource, types.CreateDatasetVersionOperationMetadata
    )


def test_create_version_e2e(client):
    prompt_resource = client.prompt_management.create_version(
        prompt=TEST_PROMPT,
        version_name="my_version",
    )
    assert isinstance(prompt_resource, types.Prompt)
    prompt_dataset = prompt_resource.dataset
    assert isinstance(prompt_dataset, types.Dataset)

    # Test local prompt resource is the same after calling get()
    retrieved_prompt = client.prompt_management.get(prompt_id=prompt_resource.prompt_id)
    assert retrieved_prompt.system_instruction == prompt_resource.system_instruction
    assert (
        retrieved_prompt.variables[0]["name"].text
        == prompt_resource.variables[0]["name"].text
    )
    assert (
        retrieved_prompt.generation_config.temperature
        == prompt_resource.generation_config.temperature
    )
    assert retrieved_prompt.safety_settings == prompt_resource.safety_settings
    assert retrieved_prompt.model_name == prompt_resource.model_name
    assert (
        retrieved_prompt.generation_config.response_schema
        == prompt_resource.generation_config.response_schema
    )

    # Test calling create_version again uses dataset from local Prompt resource.
    prompt_resource_2 = client.prompt_management.create_version(
        prompt=TEST_PROMPT, version_name="updated_version"
    )
    assert prompt_resource_2.dataset.name == prompt_dataset.name


def test_create_version_in_existing_dataset(client):
    prompt_resource = client.prompt_management.create_version(
        prompt=TEST_PROMPT,
        prompt_id=TEST_PROMPT_DATASET_ID,
        version_name="my_version_existing_dataset",
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.dataset.name.endswith(TEST_PROMPT_DATASET_ID)


def test_create_version_with_version_name(client):
    version_name = "a_new_version_yay"
    prompt_resource = client.prompt_management.create_version(
        prompt=types.Prompt(
            prompt_data=types.Part(text="Hello, {name}! How are you?"),
            prompt_name="test_prompt",
            system_instruction="Please answer in a short sentence.",
            variables=[{"name": types.Part(text="Alice")}],
            generation_config=types.GenerateContentConfig(temperature=0.1),
            safety_settings=types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE",
                method="SEVERITY",
            ),
            model_name="gemini-2.0-flash-001",
        ),
        version_name=version_name,
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.dataset_version.display_name == version_name


def test_create_version_with_inline_data(client):
    version_name = "prompt with inline data"

    pink_square_blob = types.Part(
        inline_data=(
            types.Blob(
                display_name="pink_square.ppm",
                data=b"P3\n1 1\n255\n255 192 203\n",
                mime_type="image/x-portable-pixmap",
            )
        )
    )

    prompt_resource = client.prompt_management.create_version(
        prompt=types.Prompt(
            prompt_data=[pink_square_blob, "What is this image?"],
            prompt_name="test_prompt",
            system_instruction="Answer in the style of Taylor Swift lyrics.",
            generation_config=types.GenerateContentConfig(temperature=0.1),
            safety_settings=types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE",
                method="SEVERITY",
            ),
            model_name="gemini-2.0-flash-001",
        ),
        version_name=version_name,
    )
    assert isinstance(prompt_resource, types.Prompt)
    assert isinstance(prompt_resource.dataset, types.Dataset)
    assert isinstance(prompt_resource.dataset_version, types.DatasetVersion)
    assert prompt_resource.dataset_version.display_name == version_name

    # Confirm inline data is preserved when we retrieve the prompt.
    retrieved_prompt = client.prompt_management.get(
        prompt_id=prompt_resource.prompt_id,
    )
    assert (
        retrieved_prompt.prompt_data[0].inline_data.data
        == pink_square_blob.inline_data.data
    )
    assert (
        retrieved_prompt.prompt_data[0].inline_data.display_name
        == pink_square_blob.inline_data.display_name
    )


def test_create_version_with_file_data(client):
    version_name = "prompt with file data"

    audio_file_part = types.Part(
        file_data=types.FileData(
            file_uri="https://generativelanguage.googleapis.com/v1beta/files/57w3vpfomj71",
            mime_type="video/mp4",
        ),
    )

    prompt_resource = client.prompt_management.create_version(
        prompt=types.Prompt(
            prompt_data=[audio_file_part, "What is this recording about?"],
            prompt_name="test_prompt",
            system_instruction="Answer in the style of Taylor Swift lyrics.",
            generation_config=types.GenerateContentConfig(temperature=0.1),
            safety_settings=types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE",
                method="SEVERITY",
            ),
            model_name="gemini-2.0-flash-001",
        ),
        version_name=version_name,
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
        retrieved_prompt.prompt_data[0].file_data.file_uri
        == audio_file_part.file_data.file_uri
    )
    assert (
        retrieved_prompt.prompt_data[0].file_data.display_name
        == audio_file_part.file_data.display_name
    )


def test_prompt_id_overrides_local_prompt(client):
    prompt_resource = client.prompt_management.create_version(
        prompt=types.Prompt(**TEST_PROMPT.model_dump()),
        prompt_id="2966871049100066816",
    )

    # Passing in prompt_id should override prompt_resource.prompt_id
    new_prompt_resource = client.prompt_management.create_version(
        prompt=types.Prompt(**TEST_PROMPT.model_dump()),
        prompt_id=TEST_PROMPT_DATASET_ID,
    )
    assert new_prompt_resource.prompt_id == TEST_PROMPT_DATASET_ID
    assert new_prompt_resource.prompt_id != prompt_resource.prompt_id

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompt_management.create_version",
)
