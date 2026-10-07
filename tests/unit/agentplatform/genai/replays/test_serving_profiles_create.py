"""Tests the serving_profiles.create() method against the Vertex AI endpoint using replays."""

from agentplatform._genai import types
from tests.unit.agentplatform.genai.replays import pytest_helper
from google.genai import types as genai_types

# MANDATORY: Initialize the replay test framework for this module
pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
)


def test_create_serving_profile(client):
    """Tests synchronous serving profile creation with LRO polling."""
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
        sp = client.serving_profiles.create(
            serving_profile_id="sp-sdk-replay-test",
            display_name=test_display_name,
            scope=test_scope,
            cmek_config=cmek_config,
            config=types.CreateServingProfileConfig(description=test_description),
        )

        assert sp.name is not None
        assert sp.display_name == test_display_name
        assert sp.description == test_description
        assert sp.scope == test_scope
        assert sp.cmek_config is not None
        assert sp.cmek_config.encryption_spec.kms_key_name == kms_key_name
        assert sp.create_time is not None
    finally:
        if sp:
            try:
                client.serving_profiles.delete(name=sp.name)
            except Exception:
                pass
