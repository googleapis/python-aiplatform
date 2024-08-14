# Copyright 2024 Google LLC
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


import create_custom_job_on_persistent_resource_sample
import test_constants as constants


_PRESISTENT_RESOURCE_ID = "test_persistent_resource_id"


def test_create_custom_job_on_persistent_resource_sample(
    mock_sdk_init,
    mock_get_custom_job,
    mock_run_custom_job,
):
    create_custom_job_on_persistent_resource_sample.create_custom_job_on_persistent_resource_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
        display_name=constants.DISPLAY_NAME,
        container_uri=constants.CONTAINER_URI,
        persistent_resource_id=_PRESISTENT_RESOURCE_ID,
        service_account=constants.SERVICE_ACCOUNT,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
    )

    mock_get_custom_job.assert_called_once_with(
        display_name=constants.DISPLAY_NAME,
        worker_pool_specs=constants.CUSTOM_JOB_WORKER_POOL_SPECS,
        persistent_resource_id=_PRESISTENT_RESOURCE_ID,
    )

    mock_run_custom_job.assert_called_once_with(
        service_account=constants.SERVICE_ACCOUNT,
    )
