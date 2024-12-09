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


#  [START aiplatform_sdk_vector_search_match_hybrid_queries_sample]
def vector_search_match_hybrid_queries(
    project: str,
    location: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    num_neighbors: int,
) -> List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]]:
    """Query the vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_endpoint_name (str): Required. Index endpoint to run the query
        against. The endpoint must be a private endpoint.
        deployed_index_id (str): Required. The ID of the DeployedIndex to run
        the queries against.
        num_neighbors (int): Required. The number of neighbors to return.

    Returns:
        List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]] - A list of nearest neighbors for each query.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index endpoint instance from an existing endpoint.
    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Example queries containing hybrid datapoints, sparse-only datapoints, and
    # dense-only datapoints.
    hybrid_queries = [
        aiplatform.matching_engine.matching_engine_index_endpoint.HybridQuery(
            dense_embedding=[1, 2, 3],
            sparse_embedding_dimensions=[10, 20, 30],
            sparse_embedding_values=[1.0, 1.0, 1.0],
            rrf_ranking_alpha=0.5,
        ),
        aiplatform.matching_engine.matching_engine_index_endpoint.HybridQuery(
            dense_embedding=[1, 2, 3],
            sparse_embedding_dimensions=[10, 20, 30],
            sparse_embedding_values=[0.1, 0.2, 0.3],
        ),
        aiplatform.matching_engine.matching_engine_index_endpoint.HybridQuery(
            sparse_embedding_dimensions=[10, 20, 30],
            sparse_embedding_values=[0.1, 0.2, 0.3],
        ),
        aiplatform.matching_engine.matching_engine_index_endpoint.HybridQuery(
            dense_embedding=[1, 2, 3]
        ),
    ]

    # Query the index endpoint for matches.
    resp = my_index_endpoint.match(
        deployed_index_id=deployed_index_id,
        queries=hybrid_queries,
        num_neighbors=num_neighbors,
    )
    return resp

#  [END aiplatform_sdk_vector_search_match_hybrid_queries_sample]


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


#  [START aiplatform_sdk_vector_search_match_psc_manual_sample]
def vector_search_match_psc_manual(
    project: str,
    location: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    queries: List[List[float]],
    num_neighbors: int,
    ip_address: str,
) -> List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]]:
    """Query the vector search index deployed with PSC manual configuration.

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
        ip_address (str): Required. The IP address of the PSC endpoint. Obtained
        from the created compute address used in the forwarding rule to the
        endpoint's service attachment.

    Returns:
        List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]] - A list of nearest neighbors for each query.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index endpoint instance from an existing endpoint.
    my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Set the IP address of the PSC endpoint.
    my_index_endpoint.private_service_connect_ip_address = ip_address

    # Query the index endpoint for matches.
    resp = my_index_endpoint.match(
        deployed_index_id=deployed_index_id,
        queries=queries,
        num_neighbors=num_neighbors
    )
    return resp

#  [END aiplatform_sdk_vector_search_match_psc_manual_sample]


#  [START aiplatform_sdk_vector_search_match_psc_automation_sample]
def vector_search_match_psc_automation(
    project: str,
    location: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    queries: List[List[float]],
    num_neighbors: int,
    psc_network: str,
) -> List[List[aiplatform.matching_engine.matching_engine_index_endpoint.MatchNeighbor]]:
    """Query the vector search index deployed with PSC automation.

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
        ip_address (str): Required. The IP address of the PSC endpoint. Obtained
        from the created compute address used in the fordwarding rule to the
        endpoint's service attachment.
        psc_network (str): The network the endpoint was deployed to via PSC
        automation configuration. The format is
        projects/{project_id}/global/networks/{network_name}.

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
        psc_network=psc_network
    )
    return resp

#  [END aiplatform_sdk_vector_search_match_psc_automation_sample]
