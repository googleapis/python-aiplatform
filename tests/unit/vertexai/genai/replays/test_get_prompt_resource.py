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


TEST_PROMPT_DATASET_ID = "6550997480673116160"
TEST_PROMPT_VERSION_ID = "2"


def test_get_dataset(client):
    dataset = client.prompts._get_dataset_resource(name=TEST_PROMPT_DATASET_ID)
    assert isinstance(dataset, types.Dataset)


def test_get_prompt(client):
    prompt = client.prompts.get(prompt_id=TEST_PROMPT_DATASET_ID)
    assert isinstance(prompt, types.Prompt)
    assert isinstance(prompt.dataset, types.Dataset)
    assert prompt.dataset.name.endswith(TEST_PROMPT_DATASET_ID)
    assert (
        prompt.prompt_data
        == prompt.dataset.metadata.prompt_api_schema.multimodal_prompt.prompt_message
    )
    assert isinstance(prompt.prompt_data, types.SchemaPromptSpecPromptMessage)

    contents = prompt.assemble_contents()
    assert isinstance(contents[0], genai_types.Content)


def test_get_prompt_version(client):
    prompt = client.prompts.get_version(
        prompt_id=TEST_PROMPT_DATASET_ID,
        version_id=TEST_PROMPT_VERSION_ID,
    )
    assert isinstance(prompt, types.Prompt)
    assert isinstance(prompt.dataset, types.Dataset)
    assert isinstance(prompt.dataset_version, types.DatasetVersion)
    assert prompt.dataset.name.endswith(TEST_PROMPT_DATASET_ID)
    assert prompt.dataset_version.name.endswith(TEST_PROMPT_VERSION_ID)


def test_get_prompt_with_variables_and_assemble_contents(client):
    prompt = client.prompts.get(
        prompt_id="4505721135056289792",
    )
    assert isinstance(prompt.prompt_data, types.SchemaPromptSpecPromptMessage)
    assembled_contents = prompt.assemble_contents()
    assert isinstance(assembled_contents, list)
    assert len(assembled_contents) == 1
    assert isinstance(assembled_contents[0], genai_types.Content)
    assert assembled_contents[0].parts[0].text == "Hello, Alice! How are you?"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompts._get_dataset_resource",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_prompt_async(client):
    prompt = await client.aio.prompts.get(prompt_id=TEST_PROMPT_DATASET_ID)
    assert isinstance(prompt, types.Prompt)
    assert isinstance(prompt.dataset, types.Dataset)
    assert prompt.dataset.name.endswith(TEST_PROMPT_DATASET_ID)
    assert (
        prompt.prompt_data
        == prompt.dataset.metadata.prompt_api_schema.multimodal_prompt.prompt_message
    )
    assert isinstance(prompt.prompt_data, types.SchemaPromptSpecPromptMessage)

    contents = prompt.assemble_contents()
    assert isinstance(contents[0], genai_types.Content)


@pytest.mark.asyncio
async def test_get_prompt_version_async(client):
    prompt = await client.aio.prompts.get_version(
        prompt_id=TEST_PROMPT_DATASET_ID, version_id=TEST_PROMPT_VERSION_ID
    )
    assert isinstance(prompt, types.Prompt)
    assert isinstance(prompt.dataset, types.Dataset)
    assert prompt.dataset.name.endswith(TEST_PROMPT_DATASET_ID)
    assert (
        prompt.prompt_data
        == prompt.dataset.metadata.prompt_api_schema.multimodal_prompt.prompt_message
    )
    assert isinstance(prompt.prompt_data, types.SchemaPromptSpecPromptMessage)
