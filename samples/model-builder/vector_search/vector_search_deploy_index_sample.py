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

from typing import Sequence, Tuple

from google.cloud import aiplatform


#  [START aiplatform_sdk_vector_search_deploy_index_sample]
def vector_search_deploy_index(
    project: str,
    location: str,
    index_name: str,
    index_endpoint_name: str,
    deployed_index_id: str,
) -> None:
    """Deploy a vector search index to a vector search index endpoint.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_name (str): Required. The index to update. A fully-qualified index
          resource name or a index ID.  Example:
          "projects/123/locations/us-central1/indexes/my_index_id" or
          "my_index_id".
        index_endpoint_name (str): Required. Index endpoint to deploy the index
          to.
        deployed_index_id (str): Required. The user specified ID of the
          DeployedIndex.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index instance from an existing index
    index = aiplatform.MatchingEngineIndex(index_name=index_name)

    # Create the index endpoint instance from an existing endpoint.
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Deploy Index to Endpoint
    index_endpoint = index_endpoint.deploy_index(
        index=index, deployed_index_id=deployed_index_id
    )

    print(index_endpoint.deployed_indexes)


#  [END aiplatform_sdk_vector_search_deploy_index_sample]


#  [START aiplatform_sdk_vector_search_deploy_autoscaling_index_sample]
def vector_search_deploy_autoscaling_index(
    project: str,
    location: str,
    index_name: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    min_replica_count: int,
    max_replica_count: int,
) -> None:
    """Deploy a vector search index to a vector search index endpoint.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_name (str): Required. The index to update. A fully-qualified index
          resource name or a index ID.  Example:
          "projects/123/locations/us-central1/indexes/my_index_id" or
          "my_index_id".
        index_endpoint_name (str): Required. Index endpoint to deploy the index
          to.
        deployed_index_id (str): Required. The user specified ID of the
          DeployedIndex.
        min_replica_count (int): Required. The minimum number of replicas to
          deploy.
        max_replica_count (int): Required. The maximum number of replicas to
          deploy.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index instance from an existing index
    index = aiplatform.MatchingEngineIndex(index_name=index_name)

    # Create the index endpoint instance from an existing endpoint.
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Deploy Index to Endpoint. Specifying min and max replica counts will
    # enable autoscaling.
    index_endpoint.deploy_index(
        index=index,
        deployed_index_id=deployed_index_id,
        min_replica_count=min_replica_count,
        max_replica_count=max_replica_count,
    )


#  [END aiplatform_sdk_vector_search_deploy_autoscaling_index_sample]


#  [START aiplatform_sdk_vector_search_deploy_psc_automation_sample]
def vector_search_deploy_psc_automation_index(
    project: str,
    location: str,
    index_name: str,
    index_endpoint_name: str,
    deployed_index_id: str,
    psc_automation_configs: Sequence[Tuple[str, str]],
) -> None:
    """Deploy a vector search index to an index endpoint using PSC automation.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_name (str): Required. The index to update. A fully-qualified index
          resource name or a index ID.  Example:
          "projects/123/locations/us-central1/indexes/my_index_id" or
          "my_index_id".
        index_endpoint_name (str): Required. Index endpoint to deploy the index
          to.
        deployed_index_id (str): Required. The user specified ID of the
          DeployedIndex.
        psc_automation_config (Sequence[Tuple[str, str]]): Required. A list of
          (project_id, network) pairs where PSC endpoints will be setup for the
          deployed index. Example:
          [("123", "{projects/123/global/networks/my-network1"),
          ("123", "{projects/123/global/networks/my-network2")]
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index instance from an existing index
    index = aiplatform.MatchingEngineIndex(index_name=index_name)

    # Create the index endpoint instance from an existing endpoint.
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Deploy Index to Endpoint with PSC automation enabled.
    index_endpoint.deploy_index(
        index=index,
        deployed_index_id=deployed_index_id,
        psc_automation_configs=psc_automation_configs,
    )


#  [END aiplatform_sdk_vector_search_deploy_psc_automation_sample]
