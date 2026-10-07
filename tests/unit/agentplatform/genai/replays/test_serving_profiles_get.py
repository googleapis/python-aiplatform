"""Tests the serving_profiles.get() method against the Vertex AI endpoint using replays."""

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


def test_get_serving_profile(client):
    """Tests fetching a serving profile by name."""
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
    test_display_name = "SDK Replay Test Profile"
    test_description = "Created by SDK Replay Test"
    test_scope = types.ServingProfileScope.GEMINI_LIVE
    try:
        # Create a fresh profile for the get test
        sp = client.serving_profiles.create(
            serving_profile_id="sp-sdk-replay-test",
            display_name=test_display_name,
            scope=test_scope,
            cmek_config=cmek_config,
            config=types.CreateServingProfileConfig(description=test_description),
        )

        # Act: Get the profile
        fetched_sp = client.serving_profiles.get(name=sp.name)
        assert fetched_sp.name == sp.name
        assert fetched_sp.display_name == test_display_name
        assert fetched_sp.description == test_description
        assert fetched_sp.scope == test_scope
        assert fetched_sp.cmek_config is not None
        assert fetched_sp.cmek_config.encryption_spec.kms_key_name == kms_key_name
        assert fetched_sp.create_time is not None

    except exceptions.GoogleAPIError as e:
        pytest.fail(f"Error calling client.serving_profiles.get(): {e}")
    finally:
        if sp:
            try:
                client.serving_profiles.delete(name=sp.name)
            except Exception:
                pass
