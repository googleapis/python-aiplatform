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

# [START aiplatform_create_hyperparameter_tuning_job_python_package_sample]
from google.cloud import aiplatform


def create_hyperparameter_tuning_job_python_package_sample(
    project: str,
    display_name: str,
    executor_image_uri: str,
    package_uri: str,
    python_module: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)

    # study_spec
    metric = {
        "metric_id": "val_rmse",
        "goal": aiplatform.gapic.StudySpec.MetricSpec.GoalType.MINIMIZE,
    }

    conditional_parameter_decay = {
        "parameter_spec": {
            "parameter_id": "decay",
            "double_value_spec": {"min_value": 1e-07, "max_value": 1},
            "scale_type": aiplatform.gapic.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
        },
        "parent_discrete_values": {"values": [32, 64]},
    }
    conditional_parameter_learning_rate = {
        "parameter_spec": {
            "parameter_id": "learning_rate",
            "double_value_spec": {"min_value": 1e-07, "max_value": 1},
            "scale_type": aiplatform.gapic.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
        },
        "parent_discrete_values": {"values": [4, 8, 16]},
    }
    parameter = {
        "parameter_id": "batch_size",
        "discrete_value_spec": {"values": [4, 8, 16, 32, 64, 128]},
        "scale_type": aiplatform.gapic.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
        "conditional_parameter_specs": [
            conditional_parameter_decay,
            conditional_parameter_learning_rate,
        ],
    }

    # trial_job_spec
    machine_spec = {
        "machine_type": "n1-standard-4",
        "accelerator_type": aiplatform.gapic.AcceleratorType.NVIDIA_TESLA_K80,
        "accelerator_count": 1,
    }
    worker_pool_spec = {
        "machine_spec": machine_spec,
        "replica_count": 1,
        "python_package_spec": {
            "executor_image_uri": executor_image_uri,
            "package_uris": [package_uri],
            "python_module": python_module,
            "args": [],
        },
    }

    # hyperparameter_tuning_job
    hyperparameter_tuning_job = {
        "display_name": display_name,
        "max_trial_count": 4,
        "parallel_trial_count": 2,
        "study_spec": {
            "metrics": [metric],
            "parameters": [parameter],
            "algorithm": aiplatform.gapic.StudySpec.Algorithm.RANDOM_SEARCH,
        },
        "trial_job_spec": {"worker_pool_specs": [worker_pool_spec]},
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_hyperparameter_tuning_job(
        parent=parent, hyperparameter_tuning_job=hyperparameter_tuning_job
    )
    print("response:", response)


# [END aiplatform_create_hyperparameter_tuning_job_python_package_sample]
