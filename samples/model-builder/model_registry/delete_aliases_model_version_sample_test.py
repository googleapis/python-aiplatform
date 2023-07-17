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


from model_registry import delete_aliases_model_version_sample
import test_constants as constants


def test_delete_aliases_model_version_sample(
    mock_sdk_init, mock_init_model_registry, mock_remove_version_aliases
):
    # Delete aliases from a model version.
    delete_aliases_model_version_sample.delete_aliases_model_version_sample(
        model_id=constants.MODEL_NAME,
        version_aliases=constants.VERSION_ALIASES,
        version_id=constants.VERSION_ID,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Check client initialization.
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check model registry initialization.
    mock_init_model_registry.assert_called_with(model=constants.MODEL_NAME)

    # Check that the model version was removed the aliases.
    mock_remove_version_aliases.assert_called_once()
