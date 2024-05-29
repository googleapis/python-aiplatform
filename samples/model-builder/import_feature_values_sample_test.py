# Copyright 2022 Google LLC
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

import import_feature_values_sample
import test_constants as constants


def test_import_feature_values_sample(
    mock_sdk_init, mock_get_entity_type, mock_import_feature_values
):

    import_feature_values_sample.import_feature_values_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        entity_type_id=constants.ENTITY_TYPE_ID,
        featurestore_id=constants.FEATURESTORE_ID,
        feature_ids=constants.FEATURE_IDS,
        feature_time=constants.USERS_FEATURE_TIME,
        gcs_source_uris=constants.USERS_GCS_SOURCE_URI,
        gcs_source_type=constants.GCS_SOURCE_TYPE,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_entity_type.assert_called_once_with(
        entity_type_name=constants.ENTITY_TYPE_ID,
        featurestore_id=constants.FEATURESTORE_ID,
    )

    mock_import_feature_values.assert_called_once_with(
        feature_ids=constants.FEATURE_IDS,
        feature_time=constants.USERS_FEATURE_TIME,
        gcs_source_uris=constants.USERS_GCS_SOURCE_URI,
        gcs_source_type=constants.GCS_SOURCE_TYPE,
    )
