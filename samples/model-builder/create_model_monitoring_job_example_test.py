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

import create_model_monitoring_job_example
import test_constants as constants

def test_create_model_monitoring_job_example(
    mock_sdk_init, mock_create_model_deployment_monitoring_job
):
    create_model_monitoring_job_example.create_model_monitoring_job_example(
        project = constants.PROJECT,
        location = constants.LOCATION,
        endpoint = constants.ENDPOINT_NAME,
        display_name = constants.DISPLAY_NAME,
        skew_thresholds = constants.SKEW_THRESHOLDS,
        target_field = constants.TARGET_FIELD,
        data_source = constants.BIGQUERY_SOURCE,
        emails = constants.ALERT_EMAILS,
        schedule = constants.MONITOR_INTERVAL
    )
    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT, location=constants.LOCATION
    )
    mock_create_model_deployment_monitoring_job.assert_called_once()