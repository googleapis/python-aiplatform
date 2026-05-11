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
"""Tests the skills.revisions methods against the autopush endpoint."""

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types


def test_get_skill_revision(client, tmp_path):
    # Target the autopush sandbox endpoint for the Skill Registry API
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com"
    )

    # 1. Create a fresh unique skill
    with open(tmp_path / "SKILL.md", "w") as f:
        f.write("# Replay Revision Test Skill\nThis is a test skill.")

    created_skill = client.skills.create(
        display_name="Replay Revision Test Skill",
        description="A temporary skill to test revisions E2E",
        config=types.CreateSkillConfig(
            local_path=str(tmp_path), wait_for_completion=True
        ),
    )

    try:
        assert created_skill.name is not None

        # 2. List revisions to dynamically discover the revision ID
        revisions_response = client.skills.revisions.list(name=created_skill.name)
        revisions_list = revisions_response.skill_revisions

        assert len(revisions_list) > 0
        first_revision = revisions_list[0]
        assert isinstance(first_revision, types.SkillRevision)
        assert first_revision.name is not None

        # 3. Explicitly GET the revision by its resource name
        revision = client.skills.revisions.get(name=first_revision.name)

        assert isinstance(revision, types.SkillRevision)
        assert revision.name == first_revision.name
        assert revision.state == types.SkillState.ACTIVE

    finally:
        # 4. Clean up the temporary skill
        client.skills.delete(
            name=created_skill.name,
            config=types.DeleteSkillConfig(wait_for_completion=True),
        )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="skills.revisions.get",
)
