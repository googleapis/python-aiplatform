"""Tests the skills.retrieve() method against the autopush endpoint."""

from tests.unit.agentplatform.genai.replays import pytest_helper
from agentplatform._genai import types

pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_retrieve_skills(client):
    # Target the prod endpoint for the Skill Registry API
    client._api_client._http_options.base_url = (
        "https://us-central1-aiplatform.googleapis.com"
    )

    response = client.skills.retrieve(query="stubby", config={"top_k": 2})

    assert isinstance(response, types.RetrieveSkillsResponse)
    assert response.retrieved_skills is not None

    for retrieved in response.retrieved_skills:
        assert isinstance(retrieved, types.RetrievedSkill)
        assert retrieved.skill_name is not None
        assert retrieved.description is not None
