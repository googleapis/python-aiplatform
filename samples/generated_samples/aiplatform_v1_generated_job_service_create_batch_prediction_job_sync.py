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
# Snippet for CreateBatchPredictionJob
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1_generated_JobService_CreateBatchPredictionJob_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1


def sample_create_batch_prediction_job():
    # Create a client
    client = aiplatform_v1.JobServiceClient()

    # Initialize request argument(s)
    batch_prediction_job = aiplatform_v1.BatchPredictionJob()
    batch_prediction_job.display_name = "display_name_value"
    batch_prediction_job.input_config.gcs_source.uris = ['uris_value1', 'uris_value2']
    batch_prediction_job.input_config.instances_format = "instances_format_value"
    batch_prediction_job.output_config.gcs_destination.output_uri_prefix = "output_uri_prefix_value"
    batch_prediction_job.output_config.predictions_format = "predictions_format_value"

    request = aiplatform_v1.CreateBatchPredictionJobRequest(
        parent="parent_value",
        batch_prediction_job=batch_prediction_job,
    )

    # Make the request
    response = client.create_batch_prediction_job(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1_generated_JobService_CreateBatchPredictionJob_sync]
