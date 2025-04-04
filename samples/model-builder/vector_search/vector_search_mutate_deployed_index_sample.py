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


#  [START aiplatform_sdk_vector_search_mutate_deployed_index_sample]
def vector_search_mutate_deployed_index(
    project: str,
    location: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    min_replica_count: int,
    max_replica_count: int,
) -> None:
    """Mutate the deployment resources of an already deployed index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_endpoint_name (str): Required. Index endpoint to run the query
          against.
        deployed_index_id (str): Required. The ID of the DeployedIndex to run
          the queries against.
        min_replica_count (int): Required. The minimum number of replicas to
          deploy.
        max_replica_count (int): Required. The maximum number of replicas to
          deploy.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index endpoint instance from an existing endpoint
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Mutate the deployed index
    index_endpoint.mutate_deployed_index(
        deployed_index_id=deployed_index_id,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
    )


#  [END aiplatform_sdk_vector_search_mutate_deployed_index_sample]
