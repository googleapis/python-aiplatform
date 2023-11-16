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

from typing import Dict, Optional

from google.cloud import aiplatform
from google.protobuf import timestamp_pb2


#  [START aiplatform_sdk_log_time_series_metrics_sample]
def log_time_series_metrics_sample(
    experiment_name: str,
    run_name: str,
    metrics: Dict[str, float],
    step: Optional[int],
    wall_time: Optional[timestamp_pb2.Timestamp],
    project: str,
    location: str,
):
    aiplatform.init(experiment=experiment_name, project=project, location=location)

    aiplatform.start_run(run_name=run_name, resume=True)

    aiplatform.log_time_series_metrics(metrics=metrics, step=step, wall_time=wall_time)


#  [END aiplatform_sdk_log_time_series_metrics_sample]
