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

# Delete a featurestore.
# See https://cloud.google.com/vertex-ai/docs/featurestore/setup before running
# the code snippet

# [START aiplatform_delete_featurestore_sample]
from google.cloud import aiplatform


def delete_featurestore_sample(
    project: str,
    featurestore_id: str,
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
    name = client.featurestore_path(
        project=project, location=location, featurestore=featurestore_id
    )
    response = client.delete_featurestore(name=name)
    print("Long running operation:", response.operation.name)
    delete_featurestore_response = response.result(timeout=timeout)
    print("delete_featurestore_response:", delete_featurestore_response)


# [END aiplatform_delete_featurestore_sample]
