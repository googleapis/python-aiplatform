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

#  [START aiplatform_sdk_create_feature_view_from_bq_source_with_embedding_management]

from google.cloud import aiplatform
from vertexai.resources.preview import feature_store
from typing import List


def create_feature_view_from_bq_source_with_embedding_management(
    project: str,
    location: str,
    existing_feature_online_store_id: str,
    feature_view_id: str,
    bq_table_uri: str,
    entity_id_columns: List[str],
    embedding_column: str,
    embedding_dimensions: int,
):
    aiplatform.init(project=project, location=location)

    fos = feature_store.FeatureOnlineStore(existing_feature_online_store_id)

    bigquery_source = feature_store.utils.FeatureViewBigQuerySource(
        uri=bq_table_uri,
        entity_id_columns=entity_id_columns,
    )
    index_config = feature_store.utils.IndexConfig(
        embedding_column=embedding_column,
        dimensions=embedding_dimensions,
        algorithm_config=feature_store.utils.TreeAhConfig(),
    )
    fv = fos.create_feature_view(
        name=feature_view_id,
        source=bigquery_source,
        index_config=index_config,
    )
    return fv


#  [END aiplatform_sdk_create_feature_view_from_bq_source_with_embedding_management]
