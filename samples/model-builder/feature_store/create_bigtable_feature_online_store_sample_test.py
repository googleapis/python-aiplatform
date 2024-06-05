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

from feature_store import create_bigtable_feature_online_store_sample

import test_constants as constants


def test_create_bigtable_feature_online_store_sample(
    mock_sdk_init, mock_create_feature_online_store
):
    create_bigtable_feature_online_store_sample.create_bigtable_feature_online_store_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        feature_online_store_id=constants.FEATURE_ONLINE_STORE_ID,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_create_feature_online_store.assert_called_once_with(
        constants.FEATURE_ONLINE_STORE_ID
    )
