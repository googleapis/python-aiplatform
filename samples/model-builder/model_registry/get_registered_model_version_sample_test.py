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


from model_registry import get_registered_model_version_sample
import test_constants as constants


def test_get_registered_model_version_sample(
    mock_sdk_init, mock_init_model_registry, mock_get_model
):
    # Get the registered model version.
    get_registered_model_version_sample.get_registered_model_version_sample(
        model_id=constants.MODEL_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
        version_id=constants.VERSION_ID,
    )

    # Check client initialization.
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check that the model registry was created.
    mock_init_model_registry.assert_called_with(model=constants.MODEL_NAME)

    # Check that the model version was retrieved.
    mock_get_model.assert_called_with(version=constants.VERSION_ID)
