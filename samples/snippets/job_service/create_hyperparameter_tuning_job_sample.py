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

# [START aiplatform_create_hyperparameter_tuning_job_sample]
from google.cloud import aiplatform


def create_hyperparameter_tuning_job_sample(
    project: str,
    display_name: str,
    container_image_uri: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)
    hyperparameter_tuning_job = {
        "display_name": display_name,
        "max_trial_count": 2,
        "parallel_trial_count": 1,
        "max_failed_trial_count": 1,
        "study_spec": {
            "metrics": [
                {
                    "metric_id": "accuracy",
                    "goal": aiplatform.gapic.StudySpec.MetricSpec.GoalType.MAXIMIZE,
                }
            ],
            "parameters": [
                {
                    # Learning rate.
                    "parameter_id": "lr",
                    "double_value_spec": {"min_value": 0.001, "max_value": 0.1},
                },
            ],
        },
        "trial_job_spec": {
            "worker_pool_specs": [
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4",
                        "accelerator_type": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
                        "accelerator_count": 1,
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_image_uri,
                        "command": [],
                        "args": [],
                    },
                }
            ]
        },
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_hyperparameter_tuning_job(
        parent=parent, hyperparameter_tuning_job=hyperparameter_tuning_job
    )
    print("response:", response)


# [END aiplatform_create_hyperparameter_tuning_job_sample]
