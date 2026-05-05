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
# Snippet for CreateOnlineEvaluator
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_OnlineEvaluatorService_CreateOnlineEvaluator_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


def sample_create_online_evaluator():
    # Create a client
    client = aiplatform_v1beta1.OnlineEvaluatorServiceClient()

    # Initialize request argument(s)
    online_evaluator = aiplatform_v1beta1.OnlineEvaluator()
    online_evaluator.cloud_observability.open_telemetry.semconv_version = "semconv_version_value"
    online_evaluator.agent_resource = "agent_resource_value"
    online_evaluator.metric_sources.metric.predefined_metric_spec.metric_spec_name = "metric_spec_name_value"
    online_evaluator.config.random_sampling.percentage = 1054

    request = aiplatform_v1beta1.CreateOnlineEvaluatorRequest(
        parent="parent_value",
        online_evaluator=online_evaluator,
    )

    # Make the request
    operation = client.create_online_evaluator(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_OnlineEvaluatorService_CreateOnlineEvaluator_sync]
