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

from typing import Sequence

from google.cloud import aiplatform


#  [START aiplatform_sdk_vector_search_stream_update_sample]
def stream_update_vector_search_index(
    project: str, location: str, index_name: str, datapoints: Sequence[dict]
) -> None:
    """Stream update an existing vector search index

    Args:
      project (str): Required. The Project ID
      location (str): Required. The region name, e.g. "us-central1"
      index_name (str): Required. The index to update. A fully-qualified index
        resource name or a index ID.  Example:
        "projects/123/locations/us-central1/indexes/my_index_id" or
        "my_index_id".
      datapoints: Sequence[dict]: Required. The datapoints to be updated. The dict
        element should be of the IndexDatapoint type.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index instance from an existing index with stream_update
    # enabled
    my_index = aiplatform.MatchingEngineIndex(index_name=index_name)

    # Upsert the datapoints to the index
    my_index.upsert_datapoints(datapoints=datapoints)


#  [END aiplatform_sdk_vector_search_stream_update_sample]
