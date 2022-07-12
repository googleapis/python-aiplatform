# -*- coding: utf-8 -*-
# Copyright 2022 Google LLC
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
# Snippet for ExportData
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform

# [START aiplatform_v1beta1_generated_DatasetService_ExportData_sync]
from google.cloud import aiplatform_v1beta1


def sample_export_data():
  # Create a client
  client = aiplatform_v1beta1.DatasetServiceClient()

  # Initialize request argument(s)
  export_config = aiplatform_v1beta1.ExportDataConfig()
  export_config.gcs_destination.output_uri_prefix = "output_uri_prefix_value"

  request = aiplatform_v1beta1.ExportDataRequest(
      name="name_value",
      export_config=export_config,
  )

  # Make the request
  operation = client.export_data(request=request)

  print("Waiting for operation to complete...")

  response = operation.result()

  # Handle the response
  print(response)


# [END aiplatform_v1beta1_generated_DatasetService_ExportData_sync]
