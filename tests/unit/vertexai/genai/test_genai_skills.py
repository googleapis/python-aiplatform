# //third_party/py/google/cloud/aiplatform/tests/unit/vertexai/genai/test_genai_skills.py
import pytest
from unittest import mock
from vertexai import client as vertexai_client
from vertexai import _genai as genai
from google.genai import client as genai_client
from google.genai import deps

@pytest.fixture
def mock_genai_client():
    return mock.create_autospec(genai_client.Client)

@pytest.fixture
def skills_client(mock_genai_client):
    creds = mock.MagicMock()
    creds.token = "test_token"
    client = vertexai_client.Client(
        project="test-project", location="test-location", credentials=creds
    )
    client._genai_client = mock_genai_client
    return client.skills

class TestGenaiSkills:
    mock_get_skill_response = {
        "name": "projects/test-project/locations/test-location/skills/test-skill",
        "displayName": "My Test Skill",
        # Add other expected fields from the Skill proto
    }

    def test_get_skill(self, skills_client, mock_genai_client):
        """Tests the get_skill method."""
        mock_genai_client.post.return_value = deps.Response(
            result=self.mock_get_skill_response,
            request=mock.MagicMock(),
            response=mock.MagicMock(),
        )

        skill_name = "projects/test-project/locations/test-location/skills/test-skill"
        skill = skills_client.get(name=skill_name)

        mock_genai_client.post.assert_called_once()
        call_args = mock_genai_client.post.call_args
        assert call_args[0][0] == skill_name
        assert call_args[1]["method"] == "GET"

        assert isinstance(skill, genai.types.Skill)
        assert skill.name == skill_name
        assert skill.display_name == "My Test Skill"
