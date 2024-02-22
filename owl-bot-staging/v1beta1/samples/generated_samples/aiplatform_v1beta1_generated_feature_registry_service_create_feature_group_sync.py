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
# Snippet for CreateFeatureGroup
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_FeatureRegistryService_CreateFeatureGroup_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


def sample_create_feature_group():
    # Create a client
    client = aiplatform_v1beta1.FeatureRegistryServiceClient()

    # Initialize request argument(s)
    feature_group = aiplatform_v1beta1.FeatureGroup()
    feature_group.big_query.big_query_source.input_uri = "input_uri_value"

    request = aiplatform_v1beta1.CreateFeatureGroupRequest(
        parent="parent_value",
        feature_group=feature_group,
        feature_group_id="feature_group_id_value",
    )

    # Make the request
    operation = client.create_feature_group(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_FeatureRegistryService_CreateFeatureGroup_sync]
