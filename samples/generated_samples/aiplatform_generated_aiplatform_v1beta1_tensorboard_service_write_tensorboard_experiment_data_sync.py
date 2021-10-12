# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Generated code. DO NOT EDIT!
#
# Snippet for WriteTensorboardExperimentData
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1beta1_TensorboardService_WriteTensorboardExperimentData_sync]
from google.cloud import aiplatform_v1beta1


def sample_write_tensorboard_experiment_data():
    """Snippet for write_tensorboard_experiment_data"""

    # Create a client
    client = aiplatform_v1beta1.TensorboardServiceClient()

    # Initialize request argument(s)
    write_run_data_requests = aiplatform_v1beta1.WriteTensorboardRunDataRequest()
    write_run_data_requests.tensorboard_run = "projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}"
    write_run_data_requests.time_series_data.tensorboard_time_series_id = "tensorboard_time_series_id_value"
    write_run_data_requests.time_series_data.value_type = "BLOB_SEQUENCE"

    request = aiplatform_v1beta1.WriteTensorboardExperimentDataRequest(
        tensorboard_experiment="projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}",
        write_run_data_requests=write_run_data_requests,
    )

    # Make the request
    response = client.write_tensorboard_experiment_data(request=request)

    # Handle response
    print(response)

# [END aiplatform_generated_aiplatform_v1beta1_TensorboardService_WriteTensorboardExperimentData_sync]
