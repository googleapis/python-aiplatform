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
import upload_new_model_version_using_custom_training_pipeline_sample


def test_upload_new_model_version_using_custom_training_pipeline_sample(
        mock_sdk_init,
        mock_tabular_dataset,
        mock_get_tabular_dataset,
        mock_get_custom_training_job,
        mock_run_custom_training_job,
        mock_upload_model):

    upload_new_model_version_using_custom_training_pipeline_sample.upload_new_model_version_using_custom_training_pipeline(
        display_name=constants.DISPLAY_NAME,
        script_path=constants.SCRIPT_PATH,
        container_uri=constants.CONTAINER_URI,
        model_serving_container_image_uri=constants.CONTAINER_URI,
        dataset_id=constants.RESOURCE_ID,
        replica_count=constants.REPLICA_COUNT,
        machine_type=constants.MACHINE_TYPE,
        accelerator_type=constants.ACCELERATOR_TYPE,
        accelerator_count=constants.ACCELERATOR_COUNT,
        model_id=constants.MODEL_NAME,
        args=constants.ARGS,
        model_version_aliases=constants.VERSION_ALIASES,
        model_version_description=constants.MODEL_DESCRIPTION,
        is_default_version=constants.IS_DEFAULT_VERSION,
        project=constants.PROJECT,
        location=constants.LOCATION
    )

    # Check if the client was initialized.
    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    # Check if the training job was created.
    mock_get_custom_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        script_path=constants.SCRIPT_PATH,
        container_uri=constants.CONTAINER_URI,
        model_serving_container_image_uri=constants.CONTAINER_URI
    )

    # Check if the training job was run.
    mock_run_custom_training_job.assert_called_once_with(
        dataset=mock_tabular_dataset,
        replica_count=constants.REPLICA_COUNT,
        machine_type=constants.MACHINE_TYPE,
        accelerator_type=constants.ACCELERATOR_TYPE,
        accelerator_count=constants.ACCELERATOR_COUNT,
        args=constants.ARGS,
        model_id=constants.MODEL_NAME,
        model_version_aliases=constants.VERSION_ALIASES,
        model_version_description=constants.MODEL_DESCRIPTION,
        is_default_version=constants.IS_DEFAULT_VERSION
    )

    # Check if the model was uploaded.
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


