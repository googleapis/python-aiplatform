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

# [START aiplatform_sdk_get_hyperparameter_tuning_job_sample]
from google.cloud import aiplatform


def get_hyperparameter_tuning_job_sample(
    project: str,
    hyperparameter_tuning_job_id: str,
    location: str = "us-central1",
):

    aiplatform.init(project=project, location=location)

    hpt_job = aiplatform.HyperparameterTuningJob.get(
        resource_name=hyperparameter_tuning_job_id,
    )

    return hpt_job


# [END aiplatform_sdk_get_hyperparameter_tuning_job_sample]
