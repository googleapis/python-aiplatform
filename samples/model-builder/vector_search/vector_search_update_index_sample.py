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

from typing import Dict, Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_vector_search_update_index_embeddings_sample]
def vector_search_update_index_embeddings(
    project: str,
    location: str,
    index_name: str,
    gcs_uri: str,
    is_complete_overwrite: Optional[bool] = None,
) -> None:
    """Update a vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_name (str): Required. The index to update. A fully-qualified index
          resource name or a index ID.  Example:
          "projects/123/locations/us-central1/indexes/my_index_id" or
          "my_index_id".
        gcs_uri (str): Required. The Google Cloud Storage uri for index content
        is_complete_overwrite (bool): Optional. If true, the index content will
          be overwritten wth the contents at gcs_uri.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index instance from an existing index
    index = aiplatform.MatchingEngineIndex(index_name=index_name)

    index.update_embeddings(
        contents_delta_uri=gcs_uri, is_complete_overwrite=is_complete_overwrite
    )


#  [END aiplatform_sdk_vector_search_update_index_embeddings_sample]


#  [START aiplatform_sdk_vector_search_update_index_metadata_sample]
def vector_search_update_index_metadata(
    project: str,
    location: str,
    index_name: str,
    display_name: Optional[str] = None,
    description: Optional[str] = None,
    labels: Optional[Dict[str, str]] = None,
) -> None:
    """Update a vector search index.

    Args:
        project (str): Required. Project ID
        location (str): Required. The region name
        index_name (str): Required. The index to update. A fully-qualified index
          resource name or a index ID.  Example:
          "projects/123/locations/us-central1/indexes/my_index_id" or
          "my_index_id".
        display_name (str): Optional. The display name of the Index. The name
          can be up to 128 characters long and can be consist of any UTF-8
          characters.
        description (str): Optional. The description of the Index.
        labels (Dict[str, str]): Optional. The labels with user-defined
          metadata to organize your Indexs. Label keys and values can be no
          longer than 64 characters (Unicode codepoints), can only contain
          lowercase letters, numeric characters, underscores and dashes.
          International characters are allowed. See https://goo.gl/xmQnxf for
          more information on and examples of labels. No more than 64 user
          labels can be associated with one Index (System labels are excluded).
          System reserved label keys are prefixed with
          "aiplatform.googleapis.com/" and are immutable.
    """
    # Initialize the Vertex AI client
    aiplatform.init(project=project, location=location)

    # Create the index instance from an existing index
    index = aiplatform.MatchingEngineIndex(index_name=index_name)

    index.update_metadata(
        display_name=display_name,
        description=description,
        labels=labels,
    )


#  [END aiplatform_sdk_vector_search_update_index_metadata_sample]
