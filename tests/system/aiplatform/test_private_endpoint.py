# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import uuid

from google.cloud import aiplatform

from tests.system.aiplatform import e2e_base

# project
_TEST_ENDPOINT_DISPLAY_NAME = "endpoint_display_name"


class TestPrivateEndpoint(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_private_endpoint_test"

    def test_create_delete_private_endpoint(self):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        private_endpoint = aiplatform.PrivateEndpoint.create(
            display_name=_TEST_ENDPOINT_DISPLAY_NAME, network=e2e_base._VPC_NETWORK_URI
        )

        try:
            # Verify that the retrieved private Endpoint is the same
            my_private_endpoint = aiplatform.PrivateEndpoint(
                endpoint_name=private_endpoint.resource_name
            )
            assert private_endpoint.resource_name == my_private_endpoint.resource_name
            assert private_endpoint.display_name == my_private_endpoint.display_name

            # Verify the endpoint is in the private Endpoint list
            list_private_endpoint = aiplatform.PrivateEndpoint.list()
            assert private_endpoint.resource_name in [
                private_endpoint.resource_name
                for private_endpoint in list_private_endpoint
            ]
        finally:
            if private_endpoint is not None:
                private_endpoint.delete()

    def test_create_deploy_delete_private_endpoint(self):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        private_endpoint = aiplatform.PrivateEndpoint.create(
            display_name=_TEST_ENDPOINT_DISPLAY_NAME, network=e2e_base._VPC_NETWORK_URI
        )

        try:
            # Verify that the retrieved private Endpoint is the same
            my_private_endpoint = aiplatform.PrivateEndpoint(
                endpoint_name=private_endpoint.resource_name
            )
            assert private_endpoint.resource_name == my_private_endpoint.resource_name
            assert private_endpoint.display_name == my_private_endpoint.display_name

            # Verify the endpoint is in the private Endpoint list
            list_private_endpoint = aiplatform.PrivateEndpoint.list()
            assert private_endpoint.resource_name in [
                private_endpoint.resource_name
                for private_endpoint in list_private_endpoint
            ]
        finally:
            if private_endpoint is not None:
                private_endpoint.delete()
