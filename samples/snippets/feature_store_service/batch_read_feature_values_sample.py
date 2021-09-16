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

# [START aiplatform_batch_read_feature_values_sample]
from google.cloud import aiplatform_v1beta1 as aiplatform


def batch_read_feature_values_sample(
    project: str,
    featurestore_id: str,
    input_csv_file: str,
    destination_table_uri: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    timeout: int = 300,
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.FeaturestoreServiceClient(client_options=client_options)
    featurestore = (
        f"projects/{project}/locations/{location}/featurestores/{featurestore_id}"
    )
    csv_read_instances = aiplatform.CsvSource(
        gcs_source=aiplatform.GcsSource(uris=[input_csv_file])
    )
    destination = aiplatform.FeatureValueDestination(
        bigquery_destination=aiplatform.BigQueryDestination(
            # Output to BigQuery table created earlier
            output_uri=destination_table_uri
        )
    )
    entity_type_specs = [
        aiplatform.BatchReadFeatureValuesRequest.EntityTypeSpec(
            # Read the 'age', 'gender' and 'liked_genres' features from the 'perm_users' entity
            entity_type_id="perm_users",
            feature_selector=aiplatform.FeatureSelector(
                id_matcher=aiplatform.IdMatcher(
                    ids=[
                        # features, use "*" if you want to select all features within this entity type
                        "age",
                        "gender",
                        "liked_genres",
                    ]
                )
            ),
        ),
        aiplatform.BatchReadFeatureValuesRequest.EntityTypeSpec(
            # Read the 'average_rating' and 'genres' features from the 'perm_movies' entity
            entity_type_id="perm_movies",
            feature_selector=aiplatform.FeatureSelector(
                id_matcher=aiplatform.IdMatcher(ids=["average_rating", "genres"])
            ),
        ),
    ]
    # Batch serving request from CSV
    batch_read_feature_values_request = aiplatform.BatchReadFeatureValuesRequest(
        featurestore=featurestore,
        csv_read_instances=csv_read_instances,
        destination=destination,
        entity_type_specs=entity_type_specs,
    )
    lro_response = client.batch_read_feature_values(
        request=batch_read_feature_values_request
    )
    print("Long running operation:", lro_response.operation.name)
    batch_read_feature_values_response = lro_response.result(timeout=timeout)
    print("batch_read_feature_values_response:", batch_read_feature_values_response)


# [END aiplatform_batch_read_feature_values_sample]
