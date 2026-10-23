# Copyright 2026 Google LLC
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
from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from agentplatform.frameworks.a2a import default_a2a_agent
import pytest


pytest.importorskip(
    "a2a.types", reason="a2a-sdk not installed, skipping A2A Agent tests"
)
from a2a.types import AgentInterface
from a2a.utils.constants import TransportProtocol


def test_create_a2a_agent(client):
    my_agent = default_a2a_agent()

    my_agent.agent_card.supported_interfaces.append(
        AgentInterface(
            url="http://localhost:8888/",
            protocol_binding=TransportProtocol.HTTP_JSON,
            protocol_version="1.0",
        )
    )


    staging_bucket = os.environ["GCS_BUCKET"]

    runtime = client.runtimes.create(
        agent=my_agent,
        config={
            "staging_bucket": staging_bucket,
            "display_name": "test-a2a-agent",
            "http_options": {"api_version": "v1beta1"},
            "requirements": [
                "google-cloud-aiplatform[agent_engines]",
                "a2a-sdk",
                "sse-starlette",
            ],
        },
    )


    assert isinstance(runtime, types.Runtime)
    assert runtime.api_resource.display_name == "test-a2a-agent"

    # Clean up resources.
    client.runtimes.delete(name=runtime.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)

pytest_plugins = ("pytest_asyncio",)



