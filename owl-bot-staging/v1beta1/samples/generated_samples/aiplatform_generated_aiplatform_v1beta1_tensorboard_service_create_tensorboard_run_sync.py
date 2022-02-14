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
# Snippet for CreateTensorboardRun
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1beta1_TensorboardService_CreateTensorboardRun_sync]
from google.cloud import aiplatform_v1beta1


def sample_create_tensorboard_run():
    # Create a client
    client = aiplatform_v1beta1.TensorboardServiceClient()

    # Initialize request argument(s)
    tensorboard_run = aiplatform_v1beta1.TensorboardRun()
    tensorboard_run.display_name = "display_name_value"

    request = aiplatform_v1beta1.CreateTensorboardRunRequest(
        parent="parent_value",
        tensorboard_run=tensorboard_run,
        tensorboard_run_id="tensorboard_run_id_value",
    )

    # Make the request
    response = client.create_tensorboard_run(request=request)

    # Handle the response
    print(response)

# [END aiplatform_generated_aiplatform_v1beta1_TensorboardService_CreateTensorboardRun_sync]
