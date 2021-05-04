# Copyright 2021 Google LLC
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


import create_training_pipeline_custom_package_job_sample
import test_constants as constants


def test_create_training_pipeline_custom_package_job_sample(
    mock_sdk_init,
    mock_image_dataset,
    mock_get_image_dataset,
    mock_get_custom_package_training_job,
    mock_run_custom_package_training_job,
):

    create_training_pipeline_custom_package_job_sample.create_training_pipeline_custom_package_job_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
        display_name=constants.DISPLAY_NAME,
        python_package_gcs_uri=constants.PYTHON_PACKAGE_GCS_URI,
        python_module_name=constants.PYTHON_MODULE_NAME,
        container_uri=constants.CONTAINER_URI,
        args=constants.ARGS,
        model_serving_container_image_uri=constants.CONTAINER_URI,
        dataset_id=constants.RESOURCE_ID,
        model_display_name=constants.DISPLAY_NAME_2,
        replica_count=constants.REPLICA_COUNT,
        machine_type=constants.MACHINE_TYPE,
        accelerator_type=constants.ACCELERATOR_TYPE,
        accelerator_count=constants.ACCELERATOR_COUNT,
        training_fraction_split=constants.TRAINING_FRACTION_SPLIT,
        validation_fraction_split=constants.VALIDATION_FRACTION_SPLIT,
        test_fraction_split=constants.TEST_FRACTION_SPLIT,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
    )

    mock_get_custom_package_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        python_package_gcs_uri=constants.PYTHON_PACKAGE_GCS_URI,
        python_module_name=constants.PYTHON_MODULE_NAME,
        container_uri=constants.CONTAINER_URI,
        model_serving_container_image_uri=constants.CONTAINER_URI,
    )

    mock_run_custom_package_training_job.assert_called_once_with(
        dataset=mock_image_dataset,
        model_display_name=constants.DISPLAY_NAME_2,
        replica_count=constants.REPLICA_COUNT,
        machine_type=constants.MACHINE_TYPE,
        accelerator_type=constants.ACCELERATOR_TYPE,
        accelerator_count=constants.ACCELERATOR_COUNT,
        args=constants.ARGS,
        training_fraction_split=constants.TRAINING_FRACTION_SPLIT,
        validation_fraction_split=constants.VALIDATION_FRACTION_SPLIT,
        test_fraction_split=constants.TEST_FRACTION_SPLIT,
        sync=True,
    )
