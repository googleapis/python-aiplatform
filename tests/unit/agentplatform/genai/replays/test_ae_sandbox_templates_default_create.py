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

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types


def test_sandbox_templates_default_create(client):
    config = {
        "default_container_environment": {
            "default_container_category": "DEFAULT_CONTAINER_CATEGORY_COMPUTER_USE",
        },
        "egress_control_config": {
            "internet_access": True,
        },
    }
    sandbox_template_operation = client.sandboxes.templates._create(
        name=(
            "projects/802583348448/locations/us-central1/reasoningEngines/6130241318758121472"
        ),
        display_name="Test Sandbox Template 1",
        config=config,
    )
    assert isinstance(
        sandbox_template_operation, types.SandboxEnvironmentTemplateOperation
    )

    # Verify display_name is sent in the create request body. The replay client
    # asserts the SDK's actual request matches this recorded request, so checking
    # the recorded body confirms display_name is included rather than dropped
    # (the behavior this CL fixes).
    client._api_client._initialize_replay_session_if_not_loaded()
    if client._api_client.replay_session:
        create_request_body = client._api_client.replay_session.interactions[
            0
        ].request.body_segments[0]
        assert create_request_body["displayName"] == "Test Sandbox Template 1"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="sandboxes.templates._create",
)
