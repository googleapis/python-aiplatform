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

import pytest

from experiment_tracking import get_experiment_run_artifacts_sample
import test_constants as constants


@pytest.mark.usefixtures("mock_get_run")
def test_get_experiment_run_artifact_sample(mock_get_artifacts, mock_artifacts):

    artifacts = get_experiment_run_artifacts_sample.get_experiment_run_artifacts_sample(
        run_name=constants.EXPERIMENT_RUN_NAME,
        experiment=constants.EXPERIMENT_NAME,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_get_artifacts.assert_called_with()

    assert artifacts is mock_artifacts
