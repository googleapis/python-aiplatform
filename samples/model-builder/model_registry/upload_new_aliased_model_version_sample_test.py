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
import upload_new_aliased_model_version_sample


def test_upload_new_model_version_sample(mock_sdk_init, mock_upload_model):
    # Upload a new version of the model.
    upload_new_aliased_model_version_sample.upload_new_aliased_model_version_sample(
        model_id=constants.MODEL_NAME,
        artifact_uri=constants.MODEL_ARTIFACT_URI,
        serving_container_image=constants.SERVING_CONTAINER_IMAGE,
        is_default_version=constants.IS_DEFAULT_VERSION,
        version_aliases=constants.VERSION_ALIASES,
        version_description=constants.VERSION_DESCRIPTION,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Initialize the client.
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check that the model was uploaded.
    mock_upload_model.return_value.display_name = constants.MODEL_NAME
    mock_upload_model.return_value.resource_name = constants.MODEL_RESOURCE_NAME
    mock_upload_model.return_value.version_id = constants.VERSION_ID
    mock_upload_model.return_value.version_aliases = constants.VERSION_ALIASES
    mock_upload_model.return_value.version_description = constants.VERSION_DESCRIPTION

    # Print results.
    print(mock_upload_model.return_value.display_name)
    print(mock_upload_model.return_value.resource_name)
    print(mock_upload_model.return_value.version_id)
    print(mock_upload_model.return_value.version_aliases)
    print(mock_upload_model.return_value.version_description)
