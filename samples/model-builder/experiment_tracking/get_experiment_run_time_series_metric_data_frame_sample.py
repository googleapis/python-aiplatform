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

from typing import Union

from google.cloud import aiplatform


#  [START aiplatform_sdk_get_experiment_run_time_series_metric_data_frame_sample]
def get_experiment_run_time_series_metric_data_frame_sample(
    run_name: str,
    experiment: Union[str, aiplatform.Experiment],
    project: str,
    location: str,
) -> "pd.DataFrame":  # noqa: F821
    experiment_run = aiplatform.ExperimentRun(
        run_name=run_name, experiment=experiment, project=project, location=location
    )

    return experiment_run.get_time_series_data_frame()


#  [END aiplatform_sdk_get_experiment_run_time_series_metric_data_frame_sample]
