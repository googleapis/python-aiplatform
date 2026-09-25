"""Tests the serving_profiles.update() method against the Vertex AI endpoint using replays."""

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


def test_update_serving_profile(client):
    """Tests updating a serving profile."""
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
    test_updated_display_name = "Updated SDK Replay Test Profile"
    test_description = "Created by SDK Replay Test"
    test_updated_description = "Updated by SDK Replay Test"
    try:
        sp = client.serving_profiles.create(
            serving_profile_id="sp-sdk-replay-test",
            display_name=test_display_name,
            scope=types.ServingProfileScope.GEMINI_LIVE,
            cmek_config=cmek_config,
            config=types.CreateServingProfileConfig(description=test_description),
        )
        assert sp.display_name == test_display_name
        assert sp.description == test_description

        updated_sp = client.serving_profiles.update(
            name=sp.name,
            config=types.UpdateServingProfileConfig(
                display_name=test_updated_display_name,
                description=test_updated_description,
            ),
        )
        assert updated_sp.name == sp.name
        assert updated_sp.display_name == test_updated_display_name
        assert updated_sp.description == test_updated_description

    except exceptions.GoogleAPIError as e:
        pytest.fail(f"Error calling client.serving_profiles.update(): {e}")
    finally:
        if sp:
            try:
                client.serving_profiles.delete(name=sp.name)
            except Exception:
                pass


def test_update_serving_profile_explicit_mask(client):
    """Tests updating a serving profile using explicit mask."""
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
    test_updated_description = "Updated by SDK Replay Test"
    try:
        sp = client.serving_profiles.create(
            serving_profile_id="sp-sdk-replay-test",
            display_name=test_display_name,
            scope=types.ServingProfileScope.GEMINI_LIVE,
            cmek_config=cmek_config,
            config=types.CreateServingProfileConfig(description=test_description),
        )
        assert sp.display_name == test_display_name
        assert sp.description == test_description

        update_config = types.UpdateServingProfileConfig(
            display_name="Display name should not change to this",
            description=test_updated_description,
            update_mask="description",
        )
        updated_sp = client.serving_profiles.update(
            name=sp.name,
            config=update_config,
        )
        assert updated_sp.name == sp.name
        assert updated_sp.display_name == test_display_name
        assert updated_sp.description == test_updated_description

    except exceptions.GoogleAPIError as e:
        pytest.fail(f"Error calling client.serving_profiles.update(): {e}")
    finally:
        if sp:
            try:
                client.serving_profiles.delete(name=sp.name)
            except Exception:
                pass
