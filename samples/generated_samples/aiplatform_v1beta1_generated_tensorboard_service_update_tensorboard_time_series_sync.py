# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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
# Snippet for UpdateTensorboardTimeSeries
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_TensorboardService_UpdateTensorboardTimeSeries_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


def sample_update_tensorboard_time_series():
    # Create a client
    client = aiplatform_v1beta1.TensorboardServiceClient()

    # Initialize request argument(s)
    tensorboard_time_series = aiplatform_v1beta1.TensorboardTimeSeries()
    tensorboard_time_series.display_name = "display_name_value"
    tensorboard_time_series.value_type = "BLOB_SEQUENCE"

    request = aiplatform_v1beta1.UpdateTensorboardTimeSeriesRequest(
        tensorboard_time_series=tensorboard_time_series,
    )

    # Make the request
    response = client.update_tensorboard_time_series(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_TensorboardService_UpdateTensorboardTimeSeries_sync]
