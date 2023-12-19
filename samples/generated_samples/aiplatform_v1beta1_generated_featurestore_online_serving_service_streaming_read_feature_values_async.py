# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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
# Snippet for StreamingReadFeatureValues
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_FeaturestoreOnlineServingService_StreamingReadFeatureValues_async]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


async def sample_streaming_read_feature_values():
    # Create a client
    client = aiplatform_v1beta1.FeaturestoreOnlineServingServiceAsyncClient()

    # Initialize request argument(s)
    feature_selector = aiplatform_v1beta1.FeatureSelector()
    feature_selector.id_matcher.ids = ['ids_value1', 'ids_value2']

    request = aiplatform_v1beta1.StreamingReadFeatureValuesRequest(
        entity_type="entity_type_value",
        entity_ids=['entity_ids_value1', 'entity_ids_value2'],
        feature_selector=feature_selector,
    )

    # Make the request
    stream = await client.streaming_read_feature_values(request=request)

    # Handle the response
    async for response in stream:
        print(response)

# [END aiplatform_v1beta1_generated_FeaturestoreOnlineServingService_StreamingReadFeatureValues_async]
