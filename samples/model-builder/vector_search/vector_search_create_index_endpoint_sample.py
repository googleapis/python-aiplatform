# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import aiplatform


#  [START aiplatform_sdk_vector_search_create_index_endpoint_sample]
def vector_search_create_index_endpoint(
    project: str, location: str, display_name: str
) -> None:
    """Create a vector search index endpoint.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        display_name (str): Required. The index endpoint display name
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create Index Endpoint
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=display_name,
        public_endpoint_enabled=True,
        description="Matching Engine Index Endpoint",
    )

    print(index_endpoint.name)


#  [END aiplatform_sdk_vector_search_create_index_endpoint_sample]
