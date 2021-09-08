# Copyright 2020 Google LLC
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

# [START aiplatform_delete_dataset_sample]
from google.cloud import aiplatform


def delete_dataset_sample(
    project: str,
    dataset_id: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    timeout: int = 300,
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.DatasetServiceClient(client_options=client_options)
    name = client.dataset_path(project=project, location=location, dataset=dataset_id)
    response = client.delete_dataset(name=name)
    print("Long running operation:", response.operation.name)
    delete_dataset_response = response.result(timeout=timeout)
    print("delete_dataset_response:", delete_dataset_response)


# [END aiplatform_delete_dataset_sample]
