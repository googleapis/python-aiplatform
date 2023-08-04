# Copyright 2023 Google LLC
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


import create_custom_job_with_experiment_sample
import test_constants as constants


def test_create_custom_job_with_experiment_sample(
    mock_sdk_init,
    mock_get_custom_job_from_local_script,
    mock_run_custom_job,
):
    create_custom_job_with_experiment_sample.create_custom_job_with_experiment_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
        display_name=constants.DISPLAY_NAME,
        script_path=constants.SCRIPT_PATH,
        container_uri=constants.CONTAINER_URI,
        service_account=constants.SERVICE_ACCOUNT,
        experiment=constants.EXPERIMENT_NAME,
        experiment_run=constants.EXPERIMENT_RUN_NAME,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
    )

    mock_get_custom_job_from_local_script.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        script_path=constants.SCRIPT_PATH,
        container_uri=constants.CONTAINER_URI,
    )

    mock_run_custom_job.assert_called_once_with(
        service_account=constants.SERVICE_ACCOUNT,
        experiment=constants.EXPERIMENT_NAME,
        experiment_run=constants.EXPERIMENT_RUN_NAME,
    )
