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

# Create features in bulk for an existing type.
# See https://cloud.google.com/vertex-ai/docs/featurestore/setup before running
# the code snippet

# [START aiplatform_batch_create_features_sample]
from google.cloud import aiplatform


def batch_create_features_sample(
    project: str,
    featurestore_id: str,
    entity_type_id: str,
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
    parent = f"projects/{project}/locations/{location}/featurestores/{featurestore_id}/entityTypes/{entity_type_id}"
    age_feature = aiplatform.gapic.Feature(
        value_type=aiplatform.gapic.Feature.ValueType.INT64, description="User age",
    )
    age_feature_request = aiplatform.gapic.CreateFeatureRequest(
        feature=age_feature, feature_id="age"
    )

    gender_feature = aiplatform.gapic.Feature(
        value_type=aiplatform.gapic.Feature.ValueType.STRING, description="User gender"
    )
    gender_feature_request = aiplatform.gapic.CreateFeatureRequest(
        feature=gender_feature, feature_id="gender"
    )

    liked_genres_feature = aiplatform.gapic.Feature(
        value_type=aiplatform.gapic.Feature.ValueType.STRING_ARRAY,
        description="An array of genres that this user liked",
    )
    liked_genres_feature_request = aiplatform.gapic.CreateFeatureRequest(
        feature=liked_genres_feature, feature_id="liked_genres"
    )

    requests = [
        age_feature_request,
        gender_feature_request,
        liked_genres_feature_request,
    ]
    batch_create_features_request = aiplatform.gapic.BatchCreateFeaturesRequest(
        parent=parent, requests=requests
    )
    lro_response = client.batch_create_features(request=batch_create_features_request)
    print("Long running operation:", lro_response.operation.name)
    batch_create_features_response = lro_response.result(timeout=timeout)
    print("batch_create_features_response:", batch_create_features_response)


# [END aiplatform_batch_create_features_sample]
