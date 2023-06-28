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

from experiment_tracking import resume_experiment_run_sample
import test_constants as constants


def test_resume_experiment_run_sample(mock_sdk_init, mock_start_run):

    resume_experiment_run_sample.resume_experiment_run_sample(
        experiment_name=constants.EXPERIMENT_NAME,
        run_name=constants.EXPERIMENT_RUN_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_sdk_init.assert_called_with(
        experiment=constants.EXPERIMENT_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_start_run.assert_called_with(run=constants.EXPERIMENT_RUN_NAME, resume=True)
