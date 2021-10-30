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
# Snippet for CreateBatchPredictionJob
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1beta1_JobService_CreateBatchPredictionJob_async]
from google.cloud import aiplatform_v1beta1


async def sample_create_batch_prediction_job():
    """Snippet for create_batch_prediction_job"""

    # Create a client
    client = aiplatform_v1beta1.JobServiceAsyncClient()

    # Initialize request argument(s)
    batch_prediction_job = aiplatform_v1beta1.BatchPredictionJob()
    batch_prediction_job.display_name = "display_name_value"
    batch_prediction_job.model = "projects/{project}/locations/{location}/models/{model}"
    batch_prediction_job.input_config.gcs_source.uris = ['uris_value_1', 'uris_value_2']
    batch_prediction_job.input_config.instances_format = "instances_format_value"
    batch_prediction_job.output_config.gcs_destination.output_uri_prefix = "output_uri_prefix_value"
    batch_prediction_job.output_config.predictions_format = "predictions_format_value"

    request = aiplatform_v1beta1.CreateBatchPredictionJobRequest(
        parent="projects/{project}/locations/{location}",
        batch_prediction_job=batch_prediction_job,
    )

    # Make the request
    response = await client.create_batch_prediction_job(request=request)

    # Handle response
    print(response)

# [END aiplatform_generated_aiplatform_v1beta1_JobService_CreateBatchPredictionJob_async]
