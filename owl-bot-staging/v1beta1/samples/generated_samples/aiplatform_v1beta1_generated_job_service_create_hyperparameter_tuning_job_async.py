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
# Snippet for CreateHyperparameterTuningJob
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_JobService_CreateHyperparameterTuningJob_async]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


async def sample_create_hyperparameter_tuning_job():
    # Create a client
    client = aiplatform_v1beta1.JobServiceAsyncClient()

    # Initialize request argument(s)
    hyperparameter_tuning_job = aiplatform_v1beta1.HyperparameterTuningJob()
    hyperparameter_tuning_job.display_name = "display_name_value"
    hyperparameter_tuning_job.study_spec.metrics.metric_id = "metric_id_value"
    hyperparameter_tuning_job.study_spec.metrics.goal = "MINIMIZE"
    hyperparameter_tuning_job.study_spec.parameters.double_value_spec.min_value = 0.96
    hyperparameter_tuning_job.study_spec.parameters.double_value_spec.max_value = 0.962
    hyperparameter_tuning_job.study_spec.parameters.parameter_id = "parameter_id_value"
    hyperparameter_tuning_job.max_trial_count = 1609
    hyperparameter_tuning_job.parallel_trial_count = 2128
    hyperparameter_tuning_job.trial_job_spec.worker_pool_specs.container_spec.image_uri = "image_uri_value"

    request = aiplatform_v1beta1.CreateHyperparameterTuningJobRequest(
        parent="parent_value",
        hyperparameter_tuning_job=hyperparameter_tuning_job,
    )

    # Make the request
    response = await client.create_hyperparameter_tuning_job(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_JobService_CreateHyperparameterTuningJob_async]
