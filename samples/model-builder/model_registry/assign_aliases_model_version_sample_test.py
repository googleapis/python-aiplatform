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

from model_registry import assign_aliases_model_version_sample
import test_constants as constants


def test_assign_aliases_model_version_sample(
    mock_sdk_init, mock_init_model_registry, mock_add_version_aliases, mock_model
):

    # Assign aliases to a model version.
    assign_aliases_model_version_sample.assign_aliases_model_version_sample(
        model_id=constants.MODEL_NAME,
        version_id=constants.VERSION_ID,
        version_aliases=constants.VERSION_ALIASES,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Check client initialization.
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check model registry initialization.
    mock_init_model_registry.assert_called_with(model=constants.MODEL_NAME)

    # Check that the model version was assigned the aliases.
    mock_add_version_aliases.assert_called_with(
        new_aliases=constants.VERSION_ALIASES,
        version=constants.VERSION_ID,
    )
