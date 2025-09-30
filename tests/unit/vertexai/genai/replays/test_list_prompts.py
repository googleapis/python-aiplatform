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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

import pytest


def test_list_returns_prompts(client):
    prompt_refs = client.prompts.list()
    for prompt in prompt_refs:
        assert isinstance(prompt, types.PromptRef)
        assert prompt.prompt_id is not None
        assert prompt.model is not None
    prompts_list = list(client.prompts.list())
    assert isinstance(prompts_list[0], types.PromptRef)
    assert prompts_list[0].prompt_id is not None
    assert prompts_list[0].model is not None

    # Test calling get on returned PromptRef
    prompt = client.prompts.get(prompt_id=prompts_list[0].prompt_id)
    assert isinstance(prompt, types.Prompt)
    assert prompt.prompt_data is not None
    assert prompt.prompt_data.contents is not None
    assert prompt.prompt_data.model is not None


def test_list_versions(client):
    prompt_version_refs = client.prompts.list_versions(prompt_id="3331020504126455808")
    for prompt_version in prompt_version_refs:
        assert isinstance(prompt_version, types.PromptVersionRef)
        assert prompt_version.prompt_id is not None
        assert prompt_version.version_id is not None
        assert prompt_version.model is not None

    versions_list = list(client.prompts.list_versions(prompt_id="3331020504126455808"))
    assert isinstance(versions_list, list)
    assert isinstance(versions_list[0], types.PromptVersionRef)
    assert versions_list[0].prompt_id is not None
    assert versions_list[0].version_id is not None
    assert versions_list[0].model is not None

    # Test calling get on returned PromptVersionRef
    prompt_version = client.prompts.get_version(
        prompt_id=versions_list[0].prompt_id,
        version_id=versions_list[0].version_id,
    )
    assert isinstance(prompt_version, types.Prompt)
    assert prompt_version.prompt_data is not None
    assert prompt_version.prompt_data.contents is not None
    assert prompt_version.prompt_data.model is not None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompts.list_prompts",
)

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_list_returns_prompts_async(client):
    prompt_refs = client.aio.prompts.list()
    async for prompt in prompt_refs:
        assert isinstance(prompt, types.PromptRef)
        assert prompt.prompt_id is not None
        assert prompt.model is not None


@pytest.mark.asyncio
async def test_list_versions_async(client):
    prompt_version_refs = client.aio.prompts.list_versions(
        prompt_id="3331020504126455808"
    )
    async for prompt_version in prompt_version_refs:
        assert isinstance(prompt_version, types.PromptVersionRef)
        assert prompt_version.prompt_id is not None
        assert prompt_version.version_id is not None
        assert prompt_version.model is not None
