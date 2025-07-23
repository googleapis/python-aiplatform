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


def test_agent_engines_update(client):
    agent_engine = client.agent_engines.create()
    assert agent_engine.api_resource.display_name is None

    updated_agent_engine = client.agent_engines.update(
        name=agent_engine.api_resource.name,
        config=types.AgentEngineConfig(
            display_name="updated_display_name",
            description="updated description",
        ),
    )
    assert isinstance(updated_agent_engine, types.AgentEngine)
    assert updated_agent_engine.api_resource.name == agent_engine.api_resource.name

    assert updated_agent_engine.api_resource.display_name == "updated_display_name"
    assert updated_agent_engine.api_resource.description == "updated description"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.update",
)
