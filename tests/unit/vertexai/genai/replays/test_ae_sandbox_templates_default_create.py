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


def test_sandbox_templates_default_create(client):
    config = {
        "default_container_environment": {
            "default_container_category": "DEFAULT_CONTAINER_CATEGORY_COMPUTER_USE",
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
