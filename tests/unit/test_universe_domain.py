# -*- coding: utf-8 -*-
"""Unit tests for universe domain functionality in ClientOptions."""

# Copyright 2024 Google LLC
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

from unittest import mock

from google.api_core import client_options
from google.auth import credentials as ga_credentials
from google.cloud.aiplatform.compat.services import job_service_client
import pytest


@pytest.mark.parametrize(
    "location, universe_domain, expected_host",
    [
        # Default case
        (
            "us-central1",
            "googleapis.com",
            "us-central1-aiplatform.googleapis.com:443",
        ),
        # TPC case
        (
            "u-us-prp1",
            "apis-tpclp.goog",
            "u-us-prp1-aiplatform.apis-tpclp.goog:443",
        ),
        (
            "u-france-east1",
            "apis-s3ns.fr",
            "u-france-east1-aiplatform.apis-s3ns.fr:443",
        ),
    ],
)
@mock.patch("google.auth.default", autospec=True)
def test_client_options_api_endpoint_with_universe(
    mock_auth_default, location, universe_domain, expected_host
):
    """Verifies that ClientOptions correctly sets the endpoint for different universes."""

    # Mock credentials to avoid actual authentication attempt
    mock_auth_default.return_value = (
        ga_credentials.AnonymousCredentials(),
        "test-project",
    )

    api_endpoint = f"{location}-aiplatform.{universe_domain}"
    opts = client_options.ClientOptions(api_endpoint=api_endpoint)

    # Instantiate the client with the configured options
    client = job_service_client.JobServiceClient(client_options=opts)

    # Check the host that the client's transport is using
    assert client.transport.host == expected_host
