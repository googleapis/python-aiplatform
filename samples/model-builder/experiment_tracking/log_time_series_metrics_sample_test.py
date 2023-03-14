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

from experiment_tracking import log_time_series_metrics_sample
import test_constants as constants


@pytest.mark.usefixtures("mock_sdk_init", "mock_start_run")
def test_log_time_series_metrics_sample(mock_log_time_series_metrics):

    log_time_series_metrics_sample.log_time_series_metrics_sample(
        experiment_name=constants.EXPERIMENT_NAME,
        run_name=constants.EXPERIMENT_RUN_NAME,
        metrics=constants.METRICS,
        step=constants.STEP,
        wall_time=constants.TIMESTAMP,
        project=constants.PROJECT,
        location=constants.LOCATION,
    )

    mock_log_time_series_metrics.assert_called_with(
        metrics=constants.METRICS,
        step=constants.STEP,
        wall_time=constants.TIMESTAMP,
    )
