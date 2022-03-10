# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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
# Snippet for UpdateTensorboard
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_TensorboardService_UpdateTensorboard_sync]
from google.cloud import aiplatform_v1beta1


def sample_update_tensorboard():
    # Create a client
    client = aiplatform_v1beta1.TensorboardServiceClient()

    # Initialize request argument(s)
    tensorboard = aiplatform_v1beta1.Tensorboard()
    tensorboard.display_name = "display_name_value"

    request = aiplatform_v1beta1.UpdateTensorboardRequest(
        tensorboard=tensorboard,
    )

    # Make the request
    operation = client.update_tensorboard(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_TensorboardService_UpdateTensorboard_sync]
