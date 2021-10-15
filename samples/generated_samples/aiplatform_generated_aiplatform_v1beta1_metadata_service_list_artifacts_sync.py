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
# Snippet for ListArtifacts
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1beta1_MetadataService_ListArtifacts_sync]
from google.cloud import aiplatform_v1beta1


def sample_list_artifacts():
    """Snippet for list_artifacts"""

    # Create a client
    client = aiplatform_v1beta1.MetadataServiceClient()

    # Initialize request argument(s)
    request = aiplatform_v1beta1.ListArtifactsRequest(
        parent="projects/{project}/locations/{location}/metadataStores/{metadata_store}/artifacts/{artifact}",
    )

    # Make the request
    page_result = client.list_artifacts(request=request)
    for response in page_result:
        print(response)

# [END aiplatform_generated_aiplatform_v1beta1_MetadataService_ListArtifacts_sync]
