# Copyright 2020 Google LLC
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

import os

import get_hyperparameter_tuning_job_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
HYPERPARAMETER_TUNING_JOB_ID = "2216298782247616512"
KNOWN_HYPERPARAMETER_TUNING_JOB = (
    f"/locations/us-central1/hyperparameterTuningJobs/{HYPERPARAMETER_TUNING_JOB_ID}"
)


def test_ucaip_generated_get_hyperparameter_tuning_job_sample(capsys):
    get_hyperparameter_tuning_job_sample.get_hyperparameter_tuning_job_sample(
        project=PROJECT_ID, hyperparameter_tuning_job_id=HYPERPARAMETER_TUNING_JOB_ID
    )
    out, _ = capsys.readouterr()
    assert KNOWN_HYPERPARAMETER_TUNING_JOB in out
