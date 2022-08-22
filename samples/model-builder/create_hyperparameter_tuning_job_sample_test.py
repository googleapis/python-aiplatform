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

from unittest.mock import ANY

import create_hyperparameter_tuning_job_sample

import test_constants as constants


def test_create_hyperparameter_tuning_job_sample(
    mock_sdk_init,
    mock_custom_job,
    mock_get_custom_job,
    mock_get_hyperparameter_tuning_job,
    mock_run_hyperparameter_tuning_job,
):

    create_hyperparameter_tuning_job_sample.create_hyperparameter_tuning_job_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
        display_name=constants.HYPERPARAMETER_TUNING_JOB_DISPLAY_NAME,
        container_uri=constants.CONTAINER_URI,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
        staging_bucket=constants.STAGING_BUCKET,
    )

    mock_get_custom_job.assert_called_once_with(
        display_name=constants.CUSTOM_JOB_DISPLAY_NAME,
        worker_pool_specs=constants.CUSTOM_JOB_WORKER_POOL_SPECS,
    )

    mock_get_hyperparameter_tuning_job.assert_called_once_with(
        display_name=constants.HYPERPARAMETER_TUNING_JOB_DISPLAY_NAME,
        custom_job=mock_custom_job,
        metric_spec=constants.HYPERPARAMETER_TUNING_JOB_METRIC_SPEC,
        parameter_spec=ANY,
        max_trial_count=constants.HYPERPARAMETER_TUNING_JOB_MAX_TRIAL_COUNT,
        parallel_trial_count=constants.HYPERPARAMETER_TUNING_JOB_PARALLEL_TRIAL_COUNT,
        labels=constants.HYPERPARAMETER_TUNING_JOB_LABELS,
    )

    mock_run_hyperparameter_tuning_job.assert_called_once()
