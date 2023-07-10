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
# Snippet for CreateNasJob
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1_generated_JobService_CreateNasJob_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1


def sample_create_nas_job():
    # Create a client
    client = aiplatform_v1.JobServiceClient()

    # Initialize request argument(s)
    nas_job = aiplatform_v1.NasJob()
    nas_job.display_name = "display_name_value"
    nas_job.nas_job_spec.multi_trial_algorithm_spec.search_trial_spec.search_trial_job_spec.worker_pool_specs.container_spec.image_uri = "image_uri_value"
    nas_job.nas_job_spec.multi_trial_algorithm_spec.search_trial_spec.max_trial_count = 1609
    nas_job.nas_job_spec.multi_trial_algorithm_spec.search_trial_spec.max_parallel_trial_count = 2549

    request = aiplatform_v1.CreateNasJobRequest(
        parent="parent_value",
        nas_job=nas_job,
    )

    # Make the request
    response = client.create_nas_job(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1_generated_JobService_CreateNasJob_sync]
