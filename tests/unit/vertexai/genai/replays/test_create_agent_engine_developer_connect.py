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

_TEST_CLASS_METHODS = [
    {"name": "query", "api_mode": ""},
]


def test_create_with_developer_connect_source(client):
    """Tests creating an agent engine with developer connect source."""
    developer_connect_source_config = types.ReasoningEngineSpecSourceCodeSpecDeveloperConnectConfig(
        git_repository_link="projects/reasoning-engine-test-1/locations/europe-west3/connections/shawn-develop-connect/gitRepositoryLinks/shawn-yang-google-adk-samples",
        revision="main",
        dir="test",
    )
    agent_engine = client.agent_engines.create(
        config={
            "display_name": "test-agent-engine-dev-connect",
            "developer_connect_source": developer_connect_source_config,
            "entrypoint_module": "my_agent",
            "entrypoint_object": "agent",
            "class_methods": _TEST_CLASS_METHODS,
            "http_options": {
                "base_url": "https://europe-west3-aiplatform.googleapis.com",
                "api_version": "v1beta1",
            },
        },
    )
    assert agent_engine.api_resource.display_name == "test-agent-engine-dev-connect"
    assert (
        agent_engine.api_resource.spec.source_code_spec.developer_connect_source.config.git_repository_link
        == developer_connect_source_config.git_repository_link
    )
    assert (
        agent_engine.api_resource.spec.source_code_spec.developer_connect_source.config.revision
        == developer_connect_source_config.revision
    )
    assert (
        agent_engine.api_resource.spec.source_code_spec.developer_connect_source.config.dir
        == developer_connect_source_config.dir
    )
    # Clean up resources.
    client.agent_engines.delete(name=agent_engine.api_resource.name, force=True)


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.create",
)
