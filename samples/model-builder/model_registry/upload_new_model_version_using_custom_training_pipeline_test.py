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

from model_registry import (
    upload_new_model_version_using_custom_training_pipeline_sample,
)
import test_constants as constants


def test_upload_new_model_version_using_custom_training_pipeline_sample(
    mock_sdk_init,
    mock_tabular_dataset,
    mock_get_tabular_dataset,
    mock_get_custom_training_job,
    mock_run_custom_training_job,
    mock_upload_model,
):
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
        parent_model=constants.MODEL_NAME,
        args=constants.ARGS,
        model_version_aliases=constants.VERSION_ALIASES,
        model_version_description=constants.MODEL_DESCRIPTION,
        is_default_version=constants.IS_DEFAULT_VERSION,
        project=constants.PROJECT,
        location=constants.LOCATION,
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
        model_serving_container_image_uri=constants.CONTAINER_URI,
    )

    # Check if the training job was run.
    mock_run_custom_training_job.assert_called_once_with(
        dataset=mock_tabular_dataset,
        args=constants.ARGS,
        replica_count=constants.REPLICA_COUNT,
        machine_type=constants.MACHINE_TYPE,
        accelerator_type=constants.ACCELERATOR_TYPE,
        accelerator_count=constants.ACCELERATOR_COUNT,
        parent_model=constants.MODEL_NAME,
        model_version_aliases=constants.VERSION_ALIASES,
        model_version_description=constants.MODEL_DESCRIPTION,
        is_default_version=constants.IS_DEFAULT_VERSION,
    )
