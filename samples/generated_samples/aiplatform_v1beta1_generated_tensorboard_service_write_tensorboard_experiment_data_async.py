# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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


# [START aiplatform_v1beta1_generated_TensorboardService_WriteTensorboardExperimentData_async]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


async def sample_write_tensorboard_experiment_data():
    # Create a client
    client = aiplatform_v1beta1.TensorboardServiceAsyncClient()

    # Initialize request argument(s)
    write_run_data_requests = aiplatform_v1beta1.WriteTensorboardRunDataRequest()
    write_run_data_requests.tensorboard_run = "tensorboard_run_value"
    write_run_data_requests.time_series_data.tensorboard_time_series_id = "tensorboard_time_series_id_value"
    write_run_data_requests.time_series_data.value_type = "BLOB_SEQUENCE"

    request = aiplatform_v1beta1.WriteTensorboardExperimentDataRequest(
        tensorboard_experiment="tensorboard_experiment_value",
        write_run_data_requests=write_run_data_requests,
    )

    # Make the request
    response = await client.write_tensorboard_experiment_data(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_TensorboardService_WriteTensorboardExperimentData_async]
