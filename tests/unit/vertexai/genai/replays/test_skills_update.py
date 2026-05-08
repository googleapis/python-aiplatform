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
"""Tests the skills.update() method against the Vertex AI endpoint using replays."""

import io
import zipfile

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

# MANDATORY: Initialize the replay test framework for this module
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_update_skill(client, tmp_path):
    # Target the autopush sandbox endpoint for the Skill Registry API
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com"
    )

    # 1. Create a fresh unique skill first
    with open(tmp_path / "SKILL.md", "w") as f:
        f.write("# Test Skill\nInitial content.")

    created_skill = client.skills.create(
        display_name="Original Skill",
        description="Original Description",
        config=types.CreateSkillConfig(
            local_path=str(tmp_path), wait_for_completion=True
        ),
    )

    # 2. Perform the metadata-only update on the new skill
    updated_skill = client.skills.update(
        name=created_skill.name,
        config=types.UpdateSkillConfig(
            display_name="My Updated Replay Skill",
            description="My Updated Replay Skill Description",
            wait_for_completion=True,
        ),
    )

    assert updated_skill.name == created_skill.name
    assert updated_skill.display_name == "My Updated Replay Skill"
    assert updated_skill.description == "My Updated Replay Skill Description"


def test_update_skill_with_zipped_bytes(client, tmp_path):
    # Target the autopush sandbox endpoint for the Skill Registry API
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com"
    )

    # 1. Create a fresh unique skill first
    with open(tmp_path / "SKILL.md", "w") as f:
        f.write("# Test Skill\nInitial content.")

    created_skill = client.skills.create(
        display_name="Original Skill",
        description="Original Description",
        config=types.CreateSkillConfig(
            local_path=str(tmp_path), wait_for_completion=True
        ),
    )

    # 2. Prepare zipped bytes for update
    zip_buffer = io.BytesIO()
    zinfo = zipfile.ZipInfo("SKILL.md", date_time=(1980, 1, 1, 0, 0, 0))
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        zip_file.writestr(zinfo, "# My Updated Zipped Replay Skill\nThis is updated.")
    zipped_bytes = zip_buffer.getvalue()

    # 3. Update the skill with new zipped bytes
    updated_skill = client.skills.update(
        name=created_skill.name,
        config=types.UpdateSkillConfig(
            zipped_filesystem=zipped_bytes, wait_for_completion=True
        ),
    )

    assert updated_skill.name == created_skill.name
    assert (
        updated_skill.display_name == "Original Skill"
    )  # Display name remains unchanged
