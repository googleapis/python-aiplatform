"""Tests the skills.get() method against the prod endpoint."""

from google.api_core import exceptions
from tests.unit.vertexai.genai.replays import pytest_helper
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
