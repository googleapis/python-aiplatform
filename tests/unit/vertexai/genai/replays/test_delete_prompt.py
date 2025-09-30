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

import logging

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
from google.genai import types as genai_types
import pytest


TEST_PROMPT_DATASET_ID = "6550997480673116160"
TEST_PROMPT_VERSION_ID = "2"


def test_delete_dataset(client, caplog):
    caplog.set_level(logging.INFO)
    prompt_list = list(client.prompts.list())
    client.prompts.delete(
        prompt_id=prompt_list[0].prompt_id,
    )
    assert "Deleted prompt with id: " in caplog.text


def test_delete_dataset_version(client, caplog):
    caplog.set_level(logging.INFO)
    prompt_list = list(client.prompts.list())
    prompt_version_list = list(
        client.prompts.list_versions(prompt_id=prompt_list[0].prompt_id)
    )
    client.prompts.delete_version(
        prompt_id=prompt_list[0].prompt_id,
        version_id=prompt_version_list[0].version_id,
    )
    assert "Deleted prompt version" in caplog.text


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompts.delete",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_delete_dataset_async(client, caplog):
    caplog.set_level(logging.INFO)
    prompt_list = list(client.prompts.list())
    await client.aio.prompts.delete(
        prompt_id=prompt_list[0].prompt_id,
    )
    assert "Deleted prompt with id: " in caplog.text


@pytest.mark.asyncio
async def test_delete_version_async(client, caplog):
    caplog.set_level(logging.INFO)
    prompt = client.prompts.create(
        prompt=types.Prompt(
            prompt_data=types.PromptData(
                model="gemini-2.5-flash",
                contents=[
                    genai_types.Content(
                        parts=[genai_types.Part(text="What is the capital of France?")],
                    )
                ],
            )
        ),
        config=types.CreatePromptConfig(
            prompt_display_name="test_delete_prompt_dataset",
        ),
    )
    prompt_version = client.prompts.create_version(
        prompt_id=prompt.prompt_id,
        prompt=prompt,
        config=types.CreatePromptVersionConfig(
            version_display_name="test_delete_prompt_dataset_version",
        ),
    )
    version_id = prompt_version.dataset_version.name.split("/")[-1]
    await client.aio.prompts.delete_version(
        prompt_id=prompt.prompt_id,
        version_id=version_id,
    )
    assert "Deleted prompt version" in caplog.text
