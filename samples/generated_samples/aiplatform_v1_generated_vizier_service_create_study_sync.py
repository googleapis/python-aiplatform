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
# Snippet for CreateStudy
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1_generated_VizierService_CreateStudy_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1


def sample_create_study():
    # Create a client
    client = aiplatform_v1.VizierServiceClient()

    # Initialize request argument(s)
    study = aiplatform_v1.Study()
    study.display_name = "display_name_value"
    study.study_spec.metrics.metric_id = "metric_id_value"
    study.study_spec.metrics.goal = "MINIMIZE"
    study.study_spec.parameters.double_value_spec.min_value = 0.96
    study.study_spec.parameters.double_value_spec.max_value = 0.962
    study.study_spec.parameters.parameter_id = "parameter_id_value"

    request = aiplatform_v1.CreateStudyRequest(
        parent="parent_value",
        study=study,
    )

    # Make the request
    response = client.create_study(request=request)

    # Handle the response
    print(response)

# [END aiplatform_v1_generated_VizierService_CreateStudy_sync]
