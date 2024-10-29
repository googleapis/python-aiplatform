# Copyright 2023 Google LLC
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

from typing import List

from google.cloud import aiplatform


#  [START aiplatform_sdk_vector_search_match_jwt_sample]
def vector_search_match_jwt(
    project: str,
    location: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    queries: List[List[float]],
    num_neighbors: int,
    signed_jwt: str,
) -> List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]]:
    """Query the vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_endpoint_name (str): Required. Index endpoint to run the query
        against. The endpoint must be a private endpoint.
        deployed_index_id (str): Required. The ID of the DeployedIndex to run
        the queries against.
        queries (List[List[float]]): Required. A list of queries. Each query is
        a list of floats, representing a single embedding.
        num_neighbors (int): Required. The number of neighbors to return.
        signed_jwt (str): Required. The signed JWT token for the private
        endpoint. The endpoint must be configured to accept tokens from JWT's
        issuer and encoded audience.

    Returns:
        List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]] - A list of nearest neighbors for each query.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index endpoint instance from an existing endpoint.
    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Query the index endpoint for matches.
    resp = my_index_endpoint.match(
        deployed_index_id=deployed_index_id,
        queries=queries,
        num_neighbors=num_neighbors,
        signed_jwt=signed_jwt,
    )
    return resp

#  [END aiplatform_sdk_vector_search_match_jwt_sample]
