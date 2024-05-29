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
# Generated code. DO NOT EDIT!
#
# Snippet for UpdateReasoningEngine
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_ReasoningEngineService_UpdateReasoningEngine_async]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


async def sample_update_reasoning_engine():
    # Create a client
    client = aiplatform_v1beta1.ReasoningEngineServiceAsyncClient()

    # Initialize request argument(s)
    reasoning_engine = aiplatform_v1beta1.ReasoningEngine()
    reasoning_engine.display_name = "display_name_value"

    request = aiplatform_v1beta1.UpdateReasoningEngineRequest(
        reasoning_engine=reasoning_engine,
    )

    # Make the request
    operation = client.update_reasoning_engine(request=request)

    print("Waiting for operation to complete...")

    response = (await operation).result()

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_ReasoningEngineService_UpdateReasoningEngine_async]
