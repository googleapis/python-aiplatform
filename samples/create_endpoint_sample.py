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

# [START aiplatform_create_endpoint_sample]
from google.cloud import aiplatform


def create_endpoint_sample(display_name: str, project: str):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.EndpointServiceClient(client_options=client_options)
    location = "us-central1"
    parent = "projects/{project}/locations/{location}".format(
        project=project, location=location
    )
    endpoint = {"display_name": display_name}
    response = client.create_endpoint(parent=parent, endpoint=endpoint)
    print("Long running operation:", response.operation.name)
    create_endpoint_response = response.result(timeout=300)
    print("create_endpoint_response")
    print(" name:", create_endpoint_response.name)
    print(" display_name:", create_endpoint_response.display_name)
    print(" description:", create_endpoint_response.description)
    print(" labels:", create_endpoint_response.labels)


# [END aiplatform_create_endpoint_sample]
