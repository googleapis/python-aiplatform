# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json
from unittest import mock

import google.auth.credentials
from agentplatform._genai import client as agentplatform_client
from agentplatform._genai import types as agentplatform_types
from google.genai import types as genai_types
import pytest


@pytest.fixture
def serving_profiles_client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    client = agentplatform_client.Client(
        project="test-project", location="us", credentials=creds
    )
    return client.serving_profiles


@pytest.fixture
def async_serving_profiles_client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    client = agentplatform_client.Client(
        project="test-project", location="us", credentials=creds
    )
    return client.aio.serving_profiles


class TestGenaiServingProfiles:

    mock_get_serving_profile_response = {
        "name": ("projects/test-project/locations/us/servingProfiles/test-profile"),
        "displayName": "My Test Profile",
        "scope": "INTERACTIONS_API",
    }

    mock_operation_response = {
        "name": "projects/test-project/locations/us/operations/123",
        "done": True,
        "response": mock_get_serving_profile_response,
    }

    def test_get_serving_profile(self, serving_profiles_client):
        with mock.patch.object(
            serving_profiles_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(self.mock_get_serving_profile_response)
            )
            profile_name = (
                "projects/test-project/locations/us/servingProfiles/test-profile"
            )
            profile = serving_profiles_client.get(name=profile_name)
            request_mock.assert_called_once_with(
                "get",
                profile_name,
                {"_url": {"name": profile_name}},
                None,
            )
            assert isinstance(profile, agentplatform_types.ServingProfile)
            assert profile.name == profile_name
            assert profile.display_name == "My Test Profile"

    def test_create_serving_profile_wait(self, serving_profiles_client):
        with mock.patch.object(
            serving_profiles_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.side_effect = [
                # 1. return operation from _create
                genai_types.HttpResponse(
                    body=json.dumps(
                        {
                            "name": (
                                "projects/test-project/locations/us/operations/123"
                            ),
                            "done": False,
                        }
                    )
                ),
                # 2. return operation from get_operation
                genai_types.HttpResponse(body=json.dumps(self.mock_operation_response)),
                # 3. return the actual profile from get
                genai_types.HttpResponse(
                    body=json.dumps(self.mock_get_serving_profile_response)
                ),
            ]
            cmek_config = agentplatform_types.ServingProfileCmekConfig(
                encryption_spec=genai_types.EncryptionSpec(
                    kms_key_name="projects/test-project/locations/us/keyRings/my-ring/cryptoKeys/my-key"
                )
            )
            profile = serving_profiles_client.create(
                display_name="My Test Profile",
                scope="INTERACTIONS_API",
                serving_profile_id="test-profile",
                cmek_config=cmek_config,
            )
            assert isinstance(profile, agentplatform_types.ServingProfile)
            assert (
                profile.name
                == "projects/test-project/locations/us/servingProfiles/test-profile"
            )

    def test_update_serving_profile(self, serving_profiles_client):
        with mock.patch.object(
            serving_profiles_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(self.mock_get_serving_profile_response)
            )
            profile_name = (
                "projects/test-project/locations/us/servingProfiles/test-profile"
            )
            profile = serving_profiles_client.update(
                name=profile_name,
                config=agentplatform_types.UpdateServingProfileConfig(
                    display_name="Updated Profile",
                    description="New description",
                ),
            )
            request_mock.assert_called_once()
            assert isinstance(profile, agentplatform_types.ServingProfile)

    def test_delete_serving_profile(self, serving_profiles_client):
        with mock.patch.object(
            serving_profiles_client._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="{}")
            profile_name = (
                "projects/test-project/locations/us/servingProfiles/test-profile"
            )
            serving_profiles_client.delete(name=profile_name)
            request_mock.assert_called_once()


class TestAsyncGenaiServingProfiles:

    mock_get_serving_profile_response = {
        "name": ("projects/test-project/locations/us/servingProfiles/test-profile"),
        "displayName": "My Test Profile",
        "scope": "INTERACTIONS_API",
    }

    mock_operation_response = {
        "name": "projects/test-project/locations/us/operations/123",
        "done": True,
        "response": mock_get_serving_profile_response,
    }

    @pytest.mark.asyncio
    async def test_get_serving_profile(self, async_serving_profiles_client):
        with mock.patch.object(
            async_serving_profiles_client._api_client,
            "async_request",
            new_callable=mock.AsyncMock,
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(self.mock_get_serving_profile_response)
            )
            profile_name = (
                "projects/test-project/locations/us/servingProfiles/test-profile"
            )
            profile = await async_serving_profiles_client.get(name=profile_name)
            request_mock.assert_called_once_with(
                "get",
                profile_name,
                {"_url": {"name": profile_name}},
                None,
            )
            assert isinstance(profile, agentplatform_types.ServingProfile)
            assert profile.name == profile_name
            assert profile.display_name == "My Test Profile"

    @pytest.mark.asyncio
    async def test_create_serving_profile_wait(self, async_serving_profiles_client):
        with mock.patch.object(
            async_serving_profiles_client._api_client,
            "async_request",
            new_callable=mock.AsyncMock,
        ) as request_mock:
            request_mock.side_effect = [
                # 1. return operation from _create
                genai_types.HttpResponse(
                    body=json.dumps(
                        {
                            "name": (
                                "projects/test-project/locations/us/operations/123"
                            ),
                            "done": False,
                        }
                    )
                ),
                # 2. return operation from get_operation
                genai_types.HttpResponse(body=json.dumps(self.mock_operation_response)),
                # 3. return the actual profile from get
                genai_types.HttpResponse(
                    body=json.dumps(self.mock_get_serving_profile_response)
                ),
            ]
            cmek_config = agentplatform_types.ServingProfileCmekConfig(
                encryption_spec=genai_types.EncryptionSpec(
                    kms_key_name="projects/test-project/locations/us/keyRings/my-ring/cryptoKeys/my-key"
                )
            )

            with mock.patch("asyncio.sleep", new_callable=mock.AsyncMock):
                profile = await async_serving_profiles_client.create(
                    display_name="My Test Profile",
                    scope="INTERACTIONS_API",
                    serving_profile_id="test-profile",
                    cmek_config=cmek_config,
                )
            assert isinstance(profile, agentplatform_types.ServingProfile)
            assert (
                profile.name
                == "projects/test-project/locations/us/servingProfiles/test-profile"
            )
