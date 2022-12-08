# Copyright 2022 Google LLC
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

# Serve feature values from a single entity for a particular entity type.
# See https://cloud.google.com/vertex-ai/docs/featurestore/setup before running
# the code snippet

# [START aiplatform_write_feature_values_sample]
from google.cloud import aiplatform_v1beta1 as aiplatform


def write_feature_values_sample(
        project: str,
        featurestore_id: str,
        entity_type_id: str,
        entity_id: str,
        location: str = "us-central1",
        api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.FeaturestoreOnlineServingServiceClient(
        client_options=client_options
    )
    entity_type = f"projects/{project}/locations/{location}/featurestores/{featurestore_id}/entityTypes/{entity_type_id}"

    write_feature_values_request = aiplatform.WriteFeatureValuesRequest(
        entity_type=entity_type,
        payloads=[
            aiplatform.WriteFeatureValuesPayload(
                entity_id=entity_id,
                feature_values={
                    "age": aiplatform.FeatureValue(int64_value=60),
                    "gender": aiplatform.FeatureValue(string_value='female'),
                    "liked_genres": aiplatform.FeatureValue(
                        string_array_value=aiplatform.StringArray(
                            values=["action"])),
                }
            )
        ]
    )
    write_feature_values_response = client.write_feature_values(
        request=write_feature_values_request
    )
    # Response is empty. write_feature_values will raise an exception if the call failed.
    print("write_feature_values_response:", write_feature_values_response)

# [END aiplatform_write_feature_values_sample]