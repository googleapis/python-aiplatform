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

import create_featurestore_sample
import test_constants as constants


def test_create_featurestore_sample(mock_sdk_init, mock_create_featurestore):

    create_featurestore_sample.create_featurestore_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        featurestore_id=constants.FEATURESTORE_ID,
        online_store_fixed_node_count=constants.ONLINE_STORE_FIXED_NODE_COUNT,
        sync=constants.SYNC,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_create_featurestore.assert_called_once_with(
        featurestore_id=constants.FEATURESTORE_ID,
        online_store_fixed_node_count=constants.ONLINE_STORE_FIXED_NODE_COUNT,
        sync=constants.SYNC,
    )
