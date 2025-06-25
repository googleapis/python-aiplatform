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

import os

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_create_config_lightweight(client):
    agent_display_name = "test-display-name"
    agent_description = "my agent"

    if not os.environ.get("GCS_BUCKET"):
        raise ValueError("GCS_BUCKET environment variable is not set.")

    config = client.agent_engines._create_config(
        mode="create",
        staging_bucket=os.environ["GCS_BUCKET"],
        display_name=agent_display_name,
        description=agent_description,
    )
    assert config == {
        "display_name": agent_display_name,
        "description": agent_description,
    }


def test_create_operation(client):
    operation = client.agent_engines.create(
        config=types.AgentEngineConfig(return_agent=False)
    )
    assert "reasoningEngines" in operation.name


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create",
)
