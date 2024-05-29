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


import custom_training_job_sample
import test_constants as constants


def test_custom_training_job_sample(
    mock_sdk_init, mock_get_custom_training_job, mock_run_custom_training_job
):
    custom_training_job_sample.custom_training_job_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        bucket=constants.STAGING_BUCKET,
        display_name=constants.DISPLAY_NAME,
        script_path=constants.PYTHON_PACKAGE,
        script_args=constants.PYTHON_PACKAGE_CMDARGS,
        container_uri=constants.TRAIN_IMAGE,
        model_serving_container_image_uri=constants.DEPLOY_IMAGE,
        requirements=[],
        replica_count=1,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
    )

    mock_get_custom_training_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        container_uri=constants.TRAIN_IMAGE,
        model_serving_container_image_uri=constants.DEPLOY_IMAGE,
        requirements=[],
        script_path=constants.PYTHON_PACKAGE,
    )

    mock_run_custom_training_job.assert_called_once()
