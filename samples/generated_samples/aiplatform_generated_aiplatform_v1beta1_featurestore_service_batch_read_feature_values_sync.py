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
# Snippet for BatchReadFeatureValues
# NOTE: This snippet has been automatically generated for illustrative purposes only.
# It may require modifications to work in your environment.

# To install the latest published package dependency, execute the following:
#   python3 -m pip install google-cloud-aiplatform


# [START aiplatform_generated_aiplatform_v1beta1_FeaturestoreService_BatchReadFeatureValues_sync]
from google.cloud import aiplatform_v1beta1


def sample_batch_read_feature_values():
    # Create a client
    client = aiplatform_v1beta1.FeaturestoreServiceClient()

    # Initialize request argument(s)
    csv_read_instances = aiplatform_v1beta1.CsvSource()
    csv_read_instances.gcs_source.uris = ['uris_value_1', 'uris_value_2']

    destination = aiplatform_v1beta1.FeatureValueDestination()
    destination.bigquery_destination.output_uri = "output_uri_value"

    entity_type_specs = aiplatform_v1beta1.EntityTypeSpec()
    entity_type_specs.entity_type_id = "entity_type_id_value"
    entity_type_specs.feature_selector.id_matcher.ids = ['ids_value_1', 'ids_value_2']

    request = aiplatform_v1beta1.BatchReadFeatureValuesRequest(
        csv_read_instances=csv_read_instances,
        featurestore="featurestore_value",
        destination=destination,
        entity_type_specs=entity_type_specs,
    )

    # Make the request
    operation = client.batch_read_feature_values(request=request)

    print("Waiting for operation to complete...")

    response = operation.result()

    # Handle the response
    print(response)

# [END aiplatform_generated_aiplatform_v1beta1_FeaturestoreService_BatchReadFeatureValues_sync]
