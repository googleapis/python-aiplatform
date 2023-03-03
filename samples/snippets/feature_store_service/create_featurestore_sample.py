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

# Create a featurestore resource to contain entity types and features.
# See https://cloud.google.com/vertex-ai/docs/featurestore/setup before running
# the code snippet

# [START aiplatform_create_featurestore_sample]
from google.cloud import aiplatform


def create_featurestore_sample(
    project: str,
    featurestore_id: str,
    fixed_node_count: int = 1,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    timeout: int = 1200,
):
    # The AI Platform services require regional API endpoints, which need to be
    # in the same region or multi-region overlap with the Feature Store location.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.FeaturestoreServiceClient(client_options=client_options)
    parent = f"projects/{project}/locations/{location}"
    create_featurestore_request = aiplatform.gapic.CreateFeaturestoreRequest(
        parent=parent,
        featurestore_id=featurestore_id,
        featurestore=aiplatform.gapic.Featurestore(
            online_serving_config=aiplatform.gapic.Featurestore.OnlineServingConfig(
                fixed_node_count=fixed_node_count,
            ),
        ),
    )
    lro_response = client.create_featurestore(request=create_featurestore_request)
    print("Long running operation:", lro_response.operation.name)
    create_featurestore_response = lro_response.result(timeout=timeout)
    print("create_featurestore_response:", create_featurestore_response)


# [END aiplatform_create_featurestore_sample]
