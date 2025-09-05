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
from google.genai import types as genai_types


def test_list_returns_prompts(client):
    prompts = client.prompt_management.list_prompts()
    for prompt in prompts:
        assert isinstance(prompt, types.Prompt)
        assert prompt.prompt_id is not None
        assert prompt.dataset is not None
        assert prompt.prompt_data.model is not None
    prompts_list = list(client.prompt_management.list_prompts())
    assert isinstance(prompts_list[0], types.Prompt)
    assert prompts_list[0].prompt_id is not None
    assert prompts_list[0].dataset is not None
    assert prompts_list[0].prompt_data.model is not None


def test_list_returns_prompts_with_full_resources(client):
    # First create a prompt with a display name to filter on.
    client.prompt_management.create_version(
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
            prompt_display_name="test_list_prompt",
        ),
    )
    prompts = list(
        client.prompt_management.list_prompts(
            config=types.ListPromptsConfig(
                return_full_prompt_resources=True,
                filter='displayName="test_list_prompt"',
            )
        )
    )
    assert isinstance(prompts, list)
    assert isinstance(prompts[0], types.Prompt)
    assert prompts[0].prompt_data.contents is not None
    assert prompts[0].dataset is not None


def test_list_versions(client):
    versions = list(
        client.prompt_management.list_versions(prompt_id="3331020504126455808")
    )
    assert isinstance(versions, list)
    assert isinstance(versions[0], types.Prompt)
    assert versions[0].prompt_data.model is not None


def test_list_versions_with_full_resources(client):
    versions = client.prompt_management.list_versions(
        prompt_id="3331020504126455808",
        config=types.ListPromptsConfig(
            return_full_prompt_resources=True,
        ),
    )
    for version in versions:
        assert isinstance(version, types.Prompt)
        assert version.prompt_data.contents is not None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompt_management.list_prompts",
)
