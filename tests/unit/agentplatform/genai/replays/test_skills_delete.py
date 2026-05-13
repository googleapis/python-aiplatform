"""Tests the skills.delete() method against the prod endpoint."""

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types
from google.genai import errors
import pytest

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_delete_skill(client, tmp_path):

    # 1. Create a fresh unique skill first
    with open(tmp_path / "SKILL.md", "w") as f:
        f.write("# Test Skill\nTo be deleted.")

    created_skill = client.skills.create(
        display_name="To Be Deleted Skill",
        description="Skill to be deleted",
        config=types.CreateSkillConfig(
            local_path=str(tmp_path), wait_for_completion=True
        ),
    )

    assert created_skill.name is not None

    # 2. Delete the skill and wait for LRO completion
    client.skills.delete(
        name=created_skill.name,
        config=types.DeleteSkillConfig(wait_for_completion=True),
    )

    # 3. Verify the skill is successfully deleted (Getting it should raise NotFound)
    with pytest.raises(errors.ClientError) as exc_info:
        client.skills.get(name=created_skill.name)

    assert exc_info.value.code == 404
