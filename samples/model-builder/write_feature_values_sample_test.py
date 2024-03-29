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

import test_constants as constants
import write_feature_values_sample


def test_write_feature_values_sample(
    mock_sdk_init, mock_get_entity_type, mock_write_feature_values
):

    write_feature_values_sample.write_feature_values_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        entity_type_id=constants.ENTITY_TYPE_ID,
        featurestore_id=constants.FEATURESTORE_ID,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_get_entity_type.assert_called_once_with(
        entity_type_name=constants.ENTITY_TYPE_ID,
        featurestore_id=constants.FEATURESTORE_ID,
    )

    mock_write_feature_values.assert_called_once_with(
        instances=constants.ENTITY_INSTANCES
    )
