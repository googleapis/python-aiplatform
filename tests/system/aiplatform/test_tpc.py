# -*- coding: utf-8 -*-

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

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base

_TEST_PROJECT = "test-project"
_TEST_LOCATION_TPC = "u-us-prp1"
_TEST_ENDPOINT_TPC = "u-us-prp1-aiplatform.apis-tpczero.goog"
_TEST_UNIVERSE_TPC = "apis-tpczero.goog"


class TestTpcInitializer(e2e_base.TestEndToEnd):
    """Tests TPC support in the initializer without monkeypatching."""

    _temp_prefix = "test_tpc_initializer_"

    def test_init_tpc_sets_global_config(self):
        # This verifies that our changes to validate_region allow u-us-prp1
        # and that universe_domain is correctly stored.
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION_TPC,
            universe_domain=_TEST_UNIVERSE_TPC,
        )

        assert aiplatform.initializer.global_config.location == _TEST_LOCATION_TPC
        assert aiplatform.initializer.global_config.universe_domain == _TEST_UNIVERSE_TPC

    def test_tpc_client_creation_plumbing(self):
        """Verifies that clients created after TPC init have correct TPC endpoints."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION_TPC,
            universe_domain=_TEST_UNIVERSE_TPC,
        )

        # Instantiate a client (e.g., Endpoint)
        # We don't call any methods that trigger real RPCs.
        ds = aiplatform.Endpoint.list()

        # Check the underlying client's endpoint
        # The SDK should have constructed the endpoint using the TPC location and universe domain.
        client = aiplatform.initializer.global_config.create_client(
            client_class=aiplatform.utils.EndpointClientWithOverride
        )

        expected_host = f"{_TEST_LOCATION_TPC}-aiplatform.{_TEST_UNIVERSE_TPC}:443"
        assert client._transport._host == expected_host
