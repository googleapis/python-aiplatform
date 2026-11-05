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
import base64
import datetime
import json
from unittest import mock

import google.auth.credentials
import agentplatform
from google.genai import types as genai_types
import pytest


@pytest.fixture
def client():
    creds = mock.create_autospec(google.auth.credentials.Credentials, instance=True)
    creds.token = "test_token"
    return agentplatform.Client(
        project="test-project", location="us-central1", credentials=creds
    )


class TestGenaiDetections:

    mock_detect_content_response = {
        "aiGeneratedLikelihood": "HIGH",
        "c2pa": [
            {
                "outcome": "VALID_MANIFEST",
                "manifest": {
                    "creationTypes": ["PARTLY_GENAI_CREATION"],
                    "actions": ["EDITED_USING_GENAI_TOOLS"],
                    "signerOrganization": "Example Org",
                    "signerCommonName": "Example Signer",
                    "claimGenerator": "ExampleGenerator/1.0",
                    "signTime": "2026-01-15T12:30:00Z",
                },
            }
        ],
        "responseId": "resp-123",
        "modelVersion": "ai-content-detection@001",
    }

    def test_detect_content(self, client):
        raw_bytes = b"fake-jpeg-bytes"
        with mock.patch.object(
            client.detections._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(self.mock_detect_content_response)
            )
            response = client.detections.detect_content(
                model="ai-content-detection",
                content=genai_types.Content(
                    role="user",
                    parts=[
                        genai_types.Part.from_bytes(
                            data=raw_bytes, mime_type="image/jpeg"
                        )
                    ],
                ),
                config=agentplatform.types.DetectContentConfig(),
            )
            request_mock.assert_called_once_with(
                "post",
                "publishers/google/models/ai-content-detection:detectContent",
                {
                    "_url": {"model": "publishers/google/models/ai-content-detection"},
                    "content": {
                        "parts": [
                            {
                                "inline_data": {
                                    "data": base64.b64encode(raw_bytes).decode("ascii"),
                                    "mime_type": "image/jpeg",
                                }
                            }
                        ],
                        "role": "user",
                    },
                },
                None,
            )
            assert isinstance(response, agentplatform.types.DetectContentResponse)
            assert (
                response.ai_generated_likelihood
                == agentplatform.types.AiGeneratedLikelihood.HIGH
            )
            assert response.c2pa is not None
            assert len(response.c2pa) == 1
            assert (
                response.c2pa[0].outcome
                == agentplatform.types.C2paResultOutcome.VALID_MANIFEST
            )
            assert response.c2pa[0].manifest is not None
            assert response.c2pa[0].manifest.creation_types == [
                agentplatform.types.C2paResultManifestCreationType.PARTLY_GENAI_CREATION
            ]
            assert response.c2pa[0].manifest.actions == [
                agentplatform.types.C2paResultManifestAction.EDITED_USING_GENAI_TOOLS
            ]
            assert response.c2pa[0].manifest.signer_organization == "Example Org"
            assert response.c2pa[0].manifest.signer_common_name == "Example Signer"
            assert response.c2pa[0].manifest.claim_generator == "ExampleGenerator/1.0"
            assert response.c2pa[0].manifest.sign_time == datetime.datetime(
                2026, 1, 15, 12, 30, 0, tzinfo=datetime.timezone.utc
            )
            assert response.response_id == "resp-123"
            assert response.model_version == "ai-content-detection@001"

    def test_detect_content_with_http_options(self, client):
        raw_bytes = b"fake-png-bytes"
        http_options = genai_types.HttpOptions(api_version="v1")
        with mock.patch.object(
            client.detections._api_client, "request", autospec=True
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps({"aiGeneratedLikelihood": "VERY_LOW"})
            )
            response = client.detections.detect_content(
                model="ai-content-detection@001",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part.from_bytes(
                            data=raw_bytes, mime_type="image/png"
                        )
                    ]
                ),
                config=agentplatform.types.DetectContentConfig(
                    http_options=http_options
                ),
            )
            request_mock.assert_called_once_with(
                "post",
                "publishers/google/models/ai-content-detection@001:detectContent",
                {
                    "_url": {
                        "model": "publishers/google/models/ai-content-detection@001"
                    },
                    "content": {
                        "parts": [
                            {
                                "inline_data": {
                                    "data": base64.b64encode(raw_bytes).decode("ascii"),
                                    "mime_type": "image/png",
                                }
                            }
                        ]
                    },
                },
                http_options,
            )
            assert (
                response.ai_generated_likelihood
                == agentplatform.types.AiGeneratedLikelihood.VERY_LOW
            )

    @pytest.mark.asyncio
    async def test_detect_content_async(self, client):
        raw_bytes = b"fake-webp-bytes"
        with mock.patch.object(
            client.aio.detections._api_client,
            "async_request",
            new_callable=mock.AsyncMock,
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(self.mock_detect_content_response)
            )
            response = await client.aio.detections.detect_content(
                model="ai-content-detection",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part.from_bytes(
                            data=raw_bytes, mime_type="image/webp"
                        )
                    ]
                ),
            )
            request_mock.assert_called_once_with(
                "post",
                "publishers/google/models/ai-content-detection:detectContent",
                {
                    "_url": {"model": "publishers/google/models/ai-content-detection"},
                    "content": {
                        "parts": [
                            {
                                "inline_data": {
                                    "data": base64.b64encode(raw_bytes).decode("ascii"),
                                    "mime_type": "image/webp",
                                }
                            }
                        ]
                    },
                },
                None,
            )
            assert (
                response.ai_generated_likelihood
                == agentplatform.types.AiGeneratedLikelihood.HIGH
            )
