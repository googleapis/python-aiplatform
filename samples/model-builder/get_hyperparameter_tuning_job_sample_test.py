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

import get_hyperparameter_tuning_job_sample
import test_constants as constants


def test_get_hyperparameter_tuning_job_sample(
    mock_sdk_init,
    mock_hyperparameter_tuning_job_get,
):

    get_hyperparameter_tuning_job_sample.get_hyperparameter_tuning_job_sample(
        project=constants.PROJECT,
        location=constants.LOCATION,
        hyperparameter_tuning_job_id=constants.HYPERPARAMETER_TUNING_JOB_ID,
    )

    mock_sdk_init.assert_called_once_with(
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_hyperparameter_tuning_job_get.assert_called_once_with(
        resource_name=constants.HYPERPARAMETER_TUNING_JOB_ID,
    )
