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

from feature_store import create_feature_view_from_bq_source_with_embedding_management
import test_constants as constants


def test_create_feature_view_from_bq_source_with_embedding_management(
    mock_sdk_init,
    mock_get_feature_online_store,
):
    create_feature_view_from_bq_source_with_embedding_management.create_feature_view_from_bq_source_with_embedding_management(
        project=constants.PROJECT,
        location=constants.LOCATION,
        existing_feature_online_store_id=constants.FEATURE_ONLINE_STORE_ID,
        feature_view_id=constants.FEATURE_VIEW_ID,
        bq_table_uri=constants.FEATURE_VIEW_BQ_URI,
        entity_id_columns=constants.FEATURE_VIEW_BQ_ENTITY_ID_COLUMNS,
        embedding_column=constants.FEATURE_VIEW_BQ_EMBEDDING_COLUMN,
        embedding_dimensions=constants.FEATURE_VIEW_BQ_EMBEDDING_DIMENSIONS,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_feature_online_store.assert_called_once()
    mock_get_feature_online_store.return_value.create_feature_view.assert_called_once_with(
        name=constants.FEATURE_VIEW_ID,
        source=constants.FEATURE_VIEW_BQ_SOURCE,
        index_config=constants.FEATURE_VIEW_BQ_INDEX_CONFIG,
    )
