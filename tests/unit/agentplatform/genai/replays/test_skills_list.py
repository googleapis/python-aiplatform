"""Tests the skills.list() method against the prod endpoint."""

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_list_skills(client):

    skills = client.skills.list()
    for skill in skills:
        assert isinstance(skill, types.Skill)
        assert skill.name is not None
