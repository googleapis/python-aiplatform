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
import pytest


from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_agent_engine_delete(client, caplog):
    caplog.set_level(logging.INFO)
    agent_engine = client.agent_engines.create()
    operation = client.agent_engines.delete(name=agent_engine.api_resource.name)
    assert isinstance(operation, types.DeleteAgentEngineOperation)
    assert "Deleting AgentEngine resource" in caplog.text
    assert f"Started AgentEngine delete operation: {operation.name}" in caplog.text


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.delete",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_agent_engine_delete_async(client, caplog):
    caplog.set_level(logging.INFO)
    # TODO(b/431785750): use async methods for create() when available
    agent_engine = client.agent_engines.create()
    operation = await client.aio.agent_engines.delete(
        name=agent_engine.api_resource.name
    )
    assert isinstance(operation, types.DeleteAgentEngineOperation)
    assert "Deleting AgentEngine resource" in caplog.text
    assert f"Started AgentEngine delete operation: {operation.name}" in caplog.text
