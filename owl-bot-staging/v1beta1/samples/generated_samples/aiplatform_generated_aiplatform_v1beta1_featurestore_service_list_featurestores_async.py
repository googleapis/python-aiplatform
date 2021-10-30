# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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
# Snippet for ListFeaturestores
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1beta1_FeaturestoreService_ListFeaturestores_async]
from google.cloud import aiplatform_v1beta1


async def sample_list_featurestores():
    """Snippet for list_featurestores"""

    # Create a client
    client = aiplatform_v1beta1.FeaturestoreServiceAsyncClient()

    # Initialize request argument(s)
    request = aiplatform_v1beta1.ListFeaturestoresRequest(
        parent="projects/{project}/locations/{location}/featurestores/{featurestore}",
    )

    # Make the request
    page_result = client.list_featurestores(request=request)
    async for response in page_result:
        print(response)

# [END aiplatform_generated_aiplatform_v1beta1_FeaturestoreService_ListFeaturestores_async]
