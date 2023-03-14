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

from experiment_tracking import delete_experiment_run_sample
import test_constants


def test_delete_experiment_run_sample(
    mock_experiment_run,
    mock_get_run,
):
    delete_experiment_run_sample.delete_experiment_run_sample(
        run_name=test_constants.EXPERIMENT_RUN_NAME,
        experiment=test_constants.EXPERIMENT_NAME,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
        delete_backing_tensorboard_run=True,
    )

    mock_get_run.assert_called_with(
        run_name=test_constants.EXPERIMENT_RUN_NAME,
        experiment=test_constants.EXPERIMENT_NAME,
        project=test_constants.PROJECT,
        location=test_constants.LOCATION,
    )

    mock_experiment_run.delete.assert_called_with(delete_backing_tensorboard_run=True)
