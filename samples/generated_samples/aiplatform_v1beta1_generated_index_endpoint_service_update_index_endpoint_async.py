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
# Generated code. DO NOT EDIT!
#
# Snippet for UpdateIndexEndpoint
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform

# [START aiplatform_v1beta1_generated_IndexEndpointService_UpdateIndexEndpoint_async]
from google.cloud import aiplatform_v1beta1


async def sample_update_index_endpoint():
  # Create a client
  client = aiplatform_v1beta1.IndexEndpointServiceAsyncClient()

  # Initialize request argument(s)
  index_endpoint = aiplatform_v1beta1.IndexEndpoint()
  index_endpoint.display_name = "display_name_value"

  request = aiplatform_v1beta1.UpdateIndexEndpointRequest(
      index_endpoint=index_endpoint,)

  # Make the request
  response = await client.update_index_endpoint(request=request)

  # Handle the response
  print(response)


# [END aiplatform_v1beta1_generated_IndexEndpointService_UpdateIndexEndpoint_async]
