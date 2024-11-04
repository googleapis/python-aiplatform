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

from typing import Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_vector_search_create_index_sample]
def vector_search_create_index(
    project: str, location: str, display_name: str, gcs_uri: Optional[str] = None
) -> None:
    """Create a vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        display_name (str): Required. The index display name
        gcs_uri (str): Optional. The Google Cloud Storage uri for index content
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location, staging_bucket=gcs_uri)

    # Create Index
    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=display_name,
        description="Matching Engine Index",
        dimensions=100,
        approximate_neighbors_count=150,
        leaf_node_embedding_count=500,
        leaf_nodes_to_search_percent=7,
        index_update_method="BATCH_UPDATE",  # Options: STREAM_UPDATE, BATCH_UPDATE
        distance_measure_type=aiplatform.matching_engine.matching_engine_index_config.DistanceMeasureType.DOT_PRODUCT_DISTANCE,
    )

    print(index.name)


#  [END aiplatform_sdk_vector_search_create_index_sample]


#  [START aiplatform_sdk_vector_search_create_streaming_index_sample]
def vector_search_create_streaming_index(
    project: str, location: str, display_name: str, gcs_uri: Optional[str] = None
) -> None:
    """Create a vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        display_name (str): Required. The index display name
        gcs_uri (str): Optional. The Google Cloud Storage uri for index content
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location, staging_bucket=gcs_uri)

    # Create Index
    index = aiplatform.MatchingEngineIndex.create_tree_ah_index(
        display_name=display_name,
        description="Matching Engine Index",
        dimensions=100,
        approximate_neighbors_count=150,
        leaf_node_embedding_count=500,
        leaf_nodes_to_search_percent=7,
        index_update_method="STREAM_UPDATE",  # Options: STREAM_UPDATE, BATCH_UPDATE
        distance_measure_type=aiplatform.matching_engine.matching_engine_index_config.DistanceMeasureType.DOT_PRODUCT_DISTANCE,
    )

    print(index.name)


#  [END aiplatform_sdk_vector_search_create_streaming_index_sample]
