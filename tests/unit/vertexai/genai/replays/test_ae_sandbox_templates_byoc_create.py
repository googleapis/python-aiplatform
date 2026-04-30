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

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_sandbox_templates_byoc_create(client):
    container_image_uri = "us-central1-docker.pkg.dev/agent-sandbox-fishfood-1564/agent-sandbox/custom-jupiter-sandbox:latest"
    cpu_request = "1"
    memory_request = "500Mi"
    cpu_limit = "1"
    memory_limit = "500Mi"
    config = {
        "custom_container_environment": {
            "custom_container_spec": {"image_uri": container_image_uri},
            "resources": {
                "requests": {
                    "cpu": cpu_request,
                    "memory": memory_request,
                },
                "limits": {
                    "cpu": cpu_limit,
                    "memory": memory_limit,
                },
            },
            "ports": [
                {
                    "port": 8080,
                    "protocol": "TCP",
                }
            ],
        },
        "egress_control_config": {
            "internet_access": True,
        },
    }
    sandbox_template_operation = client.agent_engines.sandboxes.templates.create(
        name=(
            "projects/254005681254/locations/us-central1/reasoningEngines/208148546254274560"
        ),
        display_name="Test Sandbox Template 1",
        config=config,
    )
    assert isinstance(
        sandbox_template_operation, types.SandboxEnvironmentTemplateOperation
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="agent_engines.sandboxes.templates.create",
)
