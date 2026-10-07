"""Tests the serving_profiles.list() method against the Vertex AI endpoint using replays."""

from google.api_core import exceptions
from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
from google.genai import types as genai_types
import pytest

# MANDATORY: Initialize the replay test framework for this module
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_list_serving_profiles(client):
    """Tests listing serving profiles via the unified pagination mechanism."""
    location = "us"
    client._api_client.location = location
    client._api_client._http_options.base_url = (
        f"https://aiplatform.{location}.rep.googleapis.com/"
    )
    kms_key_name = (
        f"projects/ucaip-e2e-test-kms-key-host/locations/{location}/"
        f"keyRings/{location}-keys/cryptoKeys/e2e-test-key"
    )
    cmek_config = types.ServingProfileCmekConfig(
        encryption_spec=genai_types.EncryptionSpec(kms_key_name=kms_key_name)
    )

    sp = None
    try:
        # Guarantee there is at least one profile to list
        sp = client.serving_profiles.create(
            serving_profile_id="sp-sdk-replay-test",
            display_name="SDK Replay Test Profile",
            scope=types.ServingProfileScope.GEMINI_LIVE,
            cmek_config=cmek_config,
            config=types.CreateServingProfileConfig(
                description="Created by SDK Replay Test"
            ),
        )

        pager = client.serving_profiles.list()

        # Verify list items parse successfully
        for profile in pager:
            assert profile.name is not None
            assert hasattr(profile, "display_name")
            assert hasattr(profile, "description")
            assert hasattr(profile, "scope")
            assert hasattr(profile, "cmek_config")
            assert hasattr(profile, "create_time")
            assert hasattr(profile, "update_time")

    except exceptions.GoogleAPIError as e:
        pytest.fail(f"Error calling client.serving_profiles.list(): {e}")
    finally:
        if sp:
            try:
                client.serving_profiles.delete(name=sp.name)
            except Exception:
                pass
