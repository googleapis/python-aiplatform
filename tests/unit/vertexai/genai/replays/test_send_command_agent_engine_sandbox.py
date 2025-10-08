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


def test_send_command_sandbox(client):
    # agent_engine = client.agent_engines.create()
    # assert isinstance(agent_engine, types.AgentEngine)
    # assert isinstance(agent_engine.api_resource, types.ReasoningEngine)
    # agent_engine_name = "projects/254005681254/locations/us-central1/reasoningEngines/2112984271655272448"
    # operation = client.agent_engines.sandboxes.create(
    #     # name=agent_engine.api_resource.name,
    #     name=agent_engine_name,
    #     spec={
    #         "code_execution_environment": {
    #             "machineConfig": "MACHINE_CONFIG_VCPU4_RAM4GIB"
    #         }
    #     },
    #     config=types.CreateAgentEngineSandboxConfig(display_name="test_sandbox"),
    # )
    # assert isinstance(operation, types.AgentEngineSandboxOperation)

    client._api_client.project = None
    client._api_client.location = None
    client._api_client.api_version = None
    token = client.agent_engines.sandboxes.generate_access_token(
        service_account_email="sign-verify-jwt@mariner-proxy.iam.gserviceaccount.com",
        sandbox_id="tenghuil-manual-sandbox-new",
    )
    response = client.agent_engines.sandboxes.send_command(
        http_method="GET",
        path="/",
        query_params={},
        access_token=token,
        headers={},
        request_dict={},
        sandbox_environment=None,
    )
    # assert token == "xxx"
    assert response.body == "Hello World"
    # assert response.outputs[0].mime_type == "application/json"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sandboxes.send_command",
)
