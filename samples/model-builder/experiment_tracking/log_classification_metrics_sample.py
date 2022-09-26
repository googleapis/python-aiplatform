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

from typing import List, Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_log_classification_metrics_sample]
def log_classification_metrics_sample(
    experiment_name: str,
    run_name: str,
    project: str,
    location: str,
    labels: Optional[List[str]] = None,
    matrix: Optional[List[List[int]]] = None,
    fpr: Optional[List[float]] = None,
    tpr: Optional[List[float]] = None,
    threshold: Optional[List[float]] = None,
    display_name: Optional[str] = None,
) -> None:
    aiplatform.init(experiment=experiment_name, project=project, location=location)

    aiplatform.start_run(run=run_name, resume=True)

    aiplatform.log_classification_metrics(
        labels=labels,
        matrix=matrix,
        fpr=fpr,
        tpr=tpr,
        threshold=threshold,
        display_name=display_name,
    )


#  [END aiplatform_sdk_log_classification_metrics_sample]
