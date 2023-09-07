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
# Snippet for BatchMigrateResources
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_v1beta1_generated_MigrationService_BatchMigrateResources_sync]
# This snippet has been automatically generated and should be regarded as a
# code template only.
# It will require modifications to work:
# - It may require correct/in-range values for request initialization.
# - It may require specifying regional endpoints when creating the service
#   client as shown in:
#   https://googleapis.dev/python/google-api-core/latest/client_options.html
from google.cloud import aiplatform_v1beta1


def sample_batch_migrate_resources():
    # Create a client
    client = aiplatform_v1beta1.MigrationServiceClient()

    # Initialize request argument(s)
    migrate_resource_requests = aiplatform_v1beta1.MigrateResourceRequest()
    migrate_resource_requests.migrate_ml_engine_model_version_config.endpoint = "endpoint_value"
    migrate_resource_requests.migrate_ml_engine_model_version_config.model_version = "model_version_value"
    migrate_resource_requests.migrate_ml_engine_model_version_config.model_display_name = "model_display_name_value"

    request = aiplatform_v1beta1.BatchMigrateResourcesRequest(
        parent="parent_value",
        migrate_resource_requests=migrate_resource_requests,
    )

    # Make the request
    operation = client.batch_migrate_resources(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)

# [END aiplatform_v1beta1_generated_MigrationService_BatchMigrateResources_sync]
