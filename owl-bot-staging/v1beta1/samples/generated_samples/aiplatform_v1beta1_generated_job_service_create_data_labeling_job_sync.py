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
# Snippet for CreateDataLabelingJob
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_JobService_CreateDataLabelingJob_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


def sample_create_data_labeling_job():
    # Create a client
    client = aiplatform_v1beta1.JobServiceClient()

    # Initialize request argument(s)
    data_labeling_job = aiplatform_v1beta1.DataLabelingJob()
    data_labeling_job.display_name = "display_name_value"
    data_labeling_job.datasets = ['datasets_value1', 'datasets_value2']
    data_labeling_job.labeler_count = 1375
    data_labeling_job.instruction_uri = "instruction_uri_value"
    data_labeling_job.inputs_schema_uri = "inputs_schema_uri_value"
    data_labeling_job.inputs.null_value = "NULL_VALUE"

    request = aiplatform_v1beta1.CreateDataLabelingJobRequest(
        parent="parent_value",
        data_labeling_job=data_labeling_job,
    )

    # Make the request
    response = client.create_data_labeling_job(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_JobService_CreateDataLabelingJob_sync]
