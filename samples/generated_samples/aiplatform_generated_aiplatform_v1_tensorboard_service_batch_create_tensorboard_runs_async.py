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
# Snippet for BatchCreateTensorboardRuns
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1_TensorboardService_BatchCreateTensorboardRuns_async]
from google.cloud import aiplatform_v1


async def sample_batch_create_tensorboard_runs():
    # Create a client
    client = aiplatform_v1.TensorboardServiceAsyncClient()

    # Initialize request argument(s)
    requests = aiplatform_v1.CreateTensorboardRunRequest()
    requests.parent = "parent_value"
    requests.tensorboard_run.display_name = "display_name_value"
    requests.tensorboard_run_id = "tensorboard_run_id_value"

    request = aiplatform_v1.BatchCreateTensorboardRunsRequest(
        parent="parent_value",
        requests=requests,
    )

    # Make the request
    response = await client.batch_create_tensorboard_runs(request=request)

    # Handle the response
    print(response)

# [END aiplatform_generated_aiplatform_v1_TensorboardService_BatchCreateTensorboardRuns_async]
