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

from model_registry import upload_new_aliased_model_version_sample
import test_constants as constants


def test_upload_new_model_version_sample(mock_sdk_init, mock_upload_model):
    # Upload a new version of the model.
    upload_new_aliased_model_version_sample.upload_new_aliased_model_version_sample(
        parent_name=constants.MODEL_NAME,
        artifact_uri=constants.MODEL_ARTIFACT_URI,
        serving_container_image=constants.SERVING_CONTAINER_IMAGE,
        is_default_version=constants.IS_DEFAULT_VERSION,
        version_aliases=constants.VERSION_ALIASES,
        version_description=constants.VERSION_DESCRIPTION,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    # Check client initialization.
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check that the model was uploaded.
    mock_upload_model.assert_called_with(
        artifact_uri=constants.MODEL_ARTIFACT_URI,
        serving_container_image=constants.SERVING_CONTAINER_IMAGE,
        is_default_version=constants.IS_DEFAULT_VERSION,
        version_aliases=constants.VERSION_ALIASES,
        version_description=constants.VERSION_DESCRIPTION,
        parent_name=constants.MODEL_NAME,
    )
