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


def test_execute_code_sandbox(client):
    agent_engine = client.agent_engines.create()
    assert isinstance(agent_engine, types.AgentEngine)
    assert isinstance(agent_engine.api_resource, types.ReasoningEngine)

    operation = client.agent_engines.sandboxes.create(
        name=agent_engine.api_resource.name,
        spec={
            "code_execution_environment": {
                "machineConfig": "MACHINE_CONFIG_VCPU4_RAM4GIB"
            }
        },
        config=types.CreateAgentEngineSandboxConfig(display_name="test_sandbox"),
    )
    assert isinstance(operation, types.AgentEngineSandboxOperation)

    code = """
with open("test.txt", "r") as input:
    with open("output.txt", "w") as output_txt:
        for line in input:
            output_txt.write(line)
"""
    input_data = {
        "code": code,
        "files": [
            {
                "name": "test.txt",
                "mimeType": "text/plain",
                "content": b"Hello, world!",
            }
        ],
    }
    response = client.agent_engines.sandboxes.execute_code(
        name=operation.response.name,
        input_data=input_data,
    )
    assert response.outputs[0].mime_type == "application/json"
    assert response.outputs[1].data == b"Hello, world!"
    assert response.outputs[1].metadata.attributes.get("file_name") == b"output.txt"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sandboxes.execute_code",
)
