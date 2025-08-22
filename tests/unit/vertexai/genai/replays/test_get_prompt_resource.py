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

TEST_PROMPT_DATASET_ID = "6550997480673116160"
TEST_PROMPT_VERSION_ID = "2"


def test_get_dataset(client):
    dataset = client.prompt_management._get_dataset_resource(
        name=TEST_PROMPT_DATASET_ID
    )
    assert isinstance(dataset, types.Dataset)


def test_get_prompt(client):
    prompt = client.prompt_management.get(prompt_id=TEST_PROMPT_DATASET_ID)
    assert isinstance(prompt, types.Prompt)
    assert isinstance(prompt.dataset, types.Dataset)
    assert prompt.dataset.name.endswith(TEST_PROMPT_DATASET_ID)


def test_get_prompt_version(client):
    prompt = client.prompt_management.get(
        prompt_id=TEST_PROMPT_DATASET_ID,
        version_id=TEST_PROMPT_VERSION_ID,
    )
    assert isinstance(prompt, types.Prompt)
    assert isinstance(prompt.dataset, types.Dataset)
    assert isinstance(prompt.dataset_version, types.DatasetVersion)
    assert prompt.dataset.name.endswith(TEST_PROMPT_DATASET_ID)
    assert prompt.dataset_version.name.endswith(TEST_PROMPT_VERSION_ID)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="prompt_management._get_dataset_resource",
)
