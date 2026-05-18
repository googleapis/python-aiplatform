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
"""Tests the skills.create() method against the Vertex AI endpoint using replays."""

import io
import zipfile

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types

# MANDATORY: Initialize the replay test framework for this module
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_create_skill(client, tmp_path):
  client._api_client._http_options.base_url = (
      "https://us-central1-aiplatform.googleapis.com"
  )

  # Create a dummy skill structure (SKILL.md is required by the spec)
  with open(tmp_path / "SKILL.md", "w") as f:
    f.write("# My Replay Skill\nThis is a test skill for replay tests.")

  skill = client.skills.create(
      skill_id="my-replay-skill-v2",
      display_name="My Replay Skill",
      description="My Replay Skill Description",
      config=types.CreateSkillConfig(
          local_path=str(tmp_path), wait_for_completion=True
      ),
  )

  assert skill.name is not None
  assert skill.display_name == "My Replay Skill"
  assert skill.description == "My Replay Skill Description"


def test_create_skill_with_prezipped_bytes(client):
  """Tests the creation of a skill with pre-zipped bytes."""
  client._api_client._http_options.base_url = (
      "https://us-central1-aiplatform.googleapis.com"
  )

  zip_buffer = io.BytesIO()
  zinfo = zipfile.ZipInfo("SKILL.md", date_time=(1980, 1, 1, 0, 0, 0))
  with zipfile.ZipFile(zip_buffer, "w") as zip_file:
    zip_file.writestr(zinfo, "# My Zipped Replay Skill\nThis is a test.")
  zipped_bytes = zip_buffer.getvalue()

  skill = client.skills.create(
      skill_id="my-zipped-replay-skill-v2",
      display_name="My Zipped Replay Skill",
      description="My Zipped Replay Skill Description",
      config=types.CreateSkillConfig(
          zipped_filesystem=zipped_bytes, wait_for_completion=True
      ),
  )

  assert skill.name is not None
  assert skill.display_name == "My Zipped Replay Skill"
  assert skill.description == "My Zipped Replay Skill Description"
