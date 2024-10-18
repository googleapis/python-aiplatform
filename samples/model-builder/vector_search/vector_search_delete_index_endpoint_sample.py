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


#  [START aiplatform_sdk_vector_search_delete_index_endpoint_sample]
def vector_search_delete_index_endpoint(
    project: str, location: str, index_endpoint_name: str, force: bool = False
) -> None:
    """Delete a vector search index endpoint.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_endpoint_name (str): Required. Index endpoint to run the query
          against.
        force (bool): Required. If true, undeploy any deployed indexes on this
          endpoint before deletion.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index endpoint instance from an existing endpoint
    index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
        index_endpoint_name=index_endpoint_name
    )

    # Delete the index endpoint
    index_endpoint.delete(force=force)


#  [END aiplatform_sdk_vector_search_delete_index_endpoint_sample]
