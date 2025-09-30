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
from tests.unit.vertexai.genai.replays import test_create_prompt
from vertexai._genai import types
import pytest


TEST_PROMPT_DATASET_ID = "6550997480673116160"
TEST_PROMPT_VERSION_ID = "2"


prompt_contents_2 = test_create_prompt.TEST_PROMPT.model_copy(deep=True)
prompt_contents_2.prompt_data.variables = None
prompt_contents_2.prompt_data.contents[0].parts[0].text = "Is this Alice?"


def test_restore_version(client):
    my_prompt = client.prompts.create(
        prompt=test_create_prompt.TEST_PROMPT.model_dump(),
        config=test_create_prompt.TEST_CREATE_PROMPT_CONFIG,
    )

    # Create 2 versions on my_prompt
    prompt_v1 = client.prompts.create_version(
        prompt_id=my_prompt.prompt_id,
        prompt=test_create_prompt.TEST_PROMPT.model_copy(deep=True),
        config=types.CreatePromptVersionConfig(version_display_name="my_prompt_v1"),
    )
    prompt_v2 = client.prompts.create_version(
        prompt_id=my_prompt.prompt_id,
        prompt=prompt_contents_2,
        config=types.CreatePromptVersionConfig(version_display_name="my_prompt_v2"),
    )
    my_prompt_v1_id = prompt_v1.dataset_version.name.split("/")[-1]
    my_prompt_v2_id = prompt_v2.dataset_version.name.split("/")[-1]
    assert my_prompt_v2_id != my_prompt_v1_id
    assert (
        prompt_v1.prompt_data.contents[0].parts[0].text == "Hello, {name}! How are you?"
    )
    assert prompt_v1.prompt_data.variables is not None
    assert prompt_v2.prompt_data.contents[0].parts[0].text == "Is this Alice?"
    assert not prompt_v2.prompt_data.variables

    # Restore version to my_prompt_v1_id
    restored_prompt = client.prompts.restore_version(
        prompt_id=my_prompt.prompt_id,
        version_id=my_prompt_v1_id,
    )
    assert restored_prompt.dataset_version.name.split("/")[-1] == my_prompt_v1_id
    assert (
        restored_prompt.prompt_data.contents[0].parts[0].text
        == "Hello, {name}! How are you?"
    )
    assert restored_prompt.prompt_data.variables is not None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompts.restore_version",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_restore_version_async(client):
    my_prompt = await client.aio.prompts.create(
        prompt=test_create_prompt.TEST_PROMPT.model_dump(),
        config=test_create_prompt.TEST_CREATE_PROMPT_CONFIG,
    )

    # Create 2 versions on my_prompt
    prompt_v1 = client.prompts.create_version(
        prompt_id=my_prompt.prompt_id,
        prompt=test_create_prompt.TEST_PROMPT.model_copy(deep=True),
        config=types.CreatePromptVersionConfig(version_display_name="my_prompt_v1"),
    )
    prompt_v2 = client.prompts.create_version(
        prompt_id=my_prompt.prompt_id,
        prompt=prompt_contents_2,
        config=types.CreatePromptVersionConfig(version_display_name="my_prompt_v2"),
    )
    my_prompt_v1_id = prompt_v1.dataset_version.name.split("/")[-1]
    my_prompt_v2_id = prompt_v2.dataset_version.name.split("/")[-1]
    assert my_prompt_v2_id != my_prompt_v1_id

    # Restore version to my_prompt_v1_id
    restored_prompt = await client.aio.prompts.restore_version(
        prompt_id=my_prompt.prompt_id,
        version_id=my_prompt_v1_id,
    )
    assert restored_prompt.dataset_version.name.split("/")[-1] == my_prompt_v1_id
