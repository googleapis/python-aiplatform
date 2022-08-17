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

# [START aiplatform_sdk_create_hyperparameter_tuning_job_sample]
from google.cloud import aiplatform

from google.cloud.aiplatform import hyperparameter_tuning as hpt


def create_hyperparameter_tuning_job_sample(
    project: str,
    location: str,
    staging_bucket: str,
    display_name: str,
    container_uri: str,
):
    aiplatform.init(project=project, location=location, staging_bucket=staging_bucket)

    worker_pool_specs = [
        {
            "machine_spec": {
                "machine_type": "n1-standard-4",
                "accelerator_type": "NVIDIA_TESLA_K80",
                "accelerator_count": 1,
            },
            "replica_count": 1,
            "container_spec": {
                "image_uri": container_uri,
                "command": [],
                "args": [],
            },
        }
    ]

    custom_job = aiplatform.CustomJob(
        display_name='custom_job',
        worker_pool_specs=worker_pool_specs,
    )

    hpt_job = aiplatform.HyperparameterTuningJob(
        display_name=display_name,
        custom_job=custom_job,
        metric_spec={
            'loss': 'minimize',
        },
        parameter_spec={
            'lr': hpt.DoubleParameterSpec(min=0.001, max=0.1, scale='log'),
            'units': hpt.IntegerParameterSpec(min=4, max=128, scale='linear'),
            'activation': hpt.CategoricalParameterSpec(values=['relu', 'selu']),
            'batch_size': hpt.DiscreteParameterSpec(values=[128, 256], scale='linear')
        },
        max_trial_count=128,
        parallel_trial_count=8,
        labels={'my_key': 'my_value'},
    )

    hpt_job.run()

    print(hpt_job.resource_name)
    return hpt_job


# [END aiplatform_sdk_create_hyperparameter_tuning_job_sample]
