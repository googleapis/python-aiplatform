"""Tests the skills.list() method against the autopush endpoint."""

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_list_skills(client):
    # Target the autopush sandbox endpoint for the Skill Registry API
    client._api_client._http_options.base_url = (
        "https://us-central1-autopush-aiplatform.sandbox.googleapis.com"
    )

    skills = client.skills.list()
    for skill in skills:
        assert isinstance(skill, types.Skill)
        assert skill.name is not None
