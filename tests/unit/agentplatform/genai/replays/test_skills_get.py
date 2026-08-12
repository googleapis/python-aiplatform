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

"""Tests the skills.get() method against the prod endpoint."""

from google.api_core import exceptions
from tests.unit.agentplatform.genai.replays import pytest_helper
import pytest

PROJECT_ID = "demo-project"
REGION = "us-central1"
SKILL_ID = "7184367305562783744"


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_get_skill(client):  # client fixture is injected by pytest_helper.setup
    """Tests the skills.get() method against the prod endpoint."""

    skill_name = f"projects/{PROJECT_ID}/locations/{REGION}/skills/{SKILL_ID}"

    try:
        skill = client.skills.get(name=skill_name)
        assert skill.name == skill_name

    except exceptions.GoogleAPIError as e:
        pytest.fail(f"Error calling client.skills.get(): {e}")
