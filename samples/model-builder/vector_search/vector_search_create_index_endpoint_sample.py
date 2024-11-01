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


#  [START aiplatform_sdk_vector_search_create_index_endpoint_vpc_sample]
def vector_search_create_index_endpoint_vpc(
    project: str, location: str, display_name: str, network: str
) -> aiplatform.MatchingEngineIndexEndpoint:
    """Create a vector search index endpoint within a VPC network.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        display_name (str): Required. The index endpoint display name
        network(str): Required. The VPC network name, in the format of
            projects/{project number}/global/networks/{network name}.

    Returns:
        aiplatform.MatchingEngineIndexEndpoint - The created index endpoint.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create Index Endpoint
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=display_name,
        network=network,
        description="Matching Engine VPC Index Endpoint",
    )

    return index_endpoint


#  [END aiplatform_sdk_vector_search_create_index_endpoint_vpc_sample]


#  [START aiplatform_sdk_vector_search_create_index_endpoint_psc_sample]
def vector_search_create_index_endpoint_private_service_connect(
    project: str, location: str, display_name: str, project_allowlist: list[str]
) -> aiplatform.MatchingEngineIndexEndpoint:
    """Create a vector search index endpoint with Private Service Connect enabled.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        display_name (str): Required. The index endpoint display name
        project_allowlist (list[str]): Required. A list of projects from which
            the forwarding rule will be able to target the service attachment.

    Returns:
        aiplatform.MatchingEngineIndexEndpoint - The created index endpoint.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create Index Endpoint
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint.create(
        display_name=display_name,
        description="Matching Engine VPC Index Endpoint",
        enable_private_service_connect=True,
        project_allowlist=project_allowlist,
    )

    return index_endpoint


#  [END aiplatform_sdk_vector_search_create_index_endpoint_psc_sample]
