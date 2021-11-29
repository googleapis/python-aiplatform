# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Bulk import values into a featurestore for existing features.
# See https://cloud.google.com/vertex-ai/docs/featurestore/setup before running
# the code snippet

# [START aiplatform_import_feature_values_sample]
from google.cloud import aiplatform


def import_feature_values_sample(
    project: str,
    featurestore_id: str,
    entity_type_id: str,
    avro_gcs_uri: str,
    entity_id_field: str,
    feature_time_field: str,
    worker_count: int = 2,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    timeout: int = 300,
):
    # The AI Platform services require regional API endpoints, which need to be
    # in the same region or multi-region overlap with the Feature Store location.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.FeaturestoreServiceClient(client_options=client_options)
    entity_type = f"projects/{project}/locations/{location}/featurestores/{featurestore_id}/entityTypes/{entity_type_id}"
    avro_source = aiplatform.gapic.AvroSource(
        gcs_source=aiplatform.gapic.GcsSource(uris=[avro_gcs_uri])
    )
    feature_specs = [
        aiplatform.gapic.ImportFeatureValuesRequest.FeatureSpec(id="age"),
        aiplatform.gapic.ImportFeatureValuesRequest.FeatureSpec(id="gender"),
        aiplatform.gapic.ImportFeatureValuesRequest.FeatureSpec(id="liked_genres"),
    ]
    import_feature_values_request = aiplatform.gapic.ImportFeatureValuesRequest(
        entity_type=entity_type,
        avro_source=avro_source,
        feature_specs=feature_specs,
        entity_id_field=entity_id_field,
        feature_time_field=feature_time_field,
        worker_count=worker_count,
    )
    lro_response = client.import_feature_values(request=import_feature_values_request)
    print("Long running operation:", lro_response.operation.name)
    import_feature_values_response = lro_response.result(timeout=timeout)
    print("import_feature_values_response:", import_feature_values_response)


# [END aiplatform_import_feature_values_sample]
