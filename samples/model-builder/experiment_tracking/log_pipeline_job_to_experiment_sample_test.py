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

from experiment_tracking import log_pipeline_job_to_experiment_sample
import test_constants as constants


def test_log_pipeline_job_sample(
    mock_sdk_init, mock_pipeline_job_create, mock_pipeline_job_submit
):

    log_pipeline_job_to_experiment_sample.log_pipeline_job_to_experiment_sample(
        experiment_name=constants.EXPERIMENT_NAME,
        pipeline_job_display_name=constants.DISPLAY_NAME,
        template_path=constants.TEMPLATE_PATH,
        pipeline_root=constants.STAGING_BUCKET,
        parameter_values=constants.PARAMS,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_sdk_init.assert_called_with(
        project=constants.PROJECT, location=constants.LOCATION
    )

    mock_pipeline_job_create.assert_called_with(
        display_name=constants.DISPLAY_NAME,
        template_path=constants.TEMPLATE_PATH,
        pipeline_root=constants.STAGING_BUCKET,
        parameter_values=constants.PARAMS,
    )

    mock_pipeline_job_submit.assert_called_with(experiment=constants.EXPERIMENT_NAME)
