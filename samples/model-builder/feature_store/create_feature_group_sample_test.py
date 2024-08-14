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

from feature_store import create_feature_group_sample

import test_constants as constants


def test_create_feature_group_sample(
    mock_sdk_init, mock_create_feature_group
):
    create_feature_group_sample.create_feature_group_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        feature_group_id=constants.FEATURE_GROUP_ID,
        bq_table_uri=constants.FEATURE_GROUP_BQ_URI,
        entity_id_columns=constants.FEATURE_GROUP_BQ_ENTITY_ID_COLUMNS,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_create_feature_group.assert_called_once_with(
        name=constants.FEATURE_GROUP_ID, source=constants.FEATURE_GROUP_SOURCE
    )
