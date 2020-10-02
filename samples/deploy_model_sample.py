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

# [START aiplatform_deploy_model_sample]
from google.cloud import aiplatform


def deploy_model_sample(
    model_name: str, deployed_model_display_name: str, project: str, endpoint_id: str
):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.EndpointServiceClient(client_options=client_options)
    location = "us-central1"
    name = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    # key '0' assigns traffic for the newly deployed model
    # Traffic percentage values must add up to 100
    # Leave dictionary empty if endpoint should not accept any traffic
    traffic_split = {"0": 100}
    deployed_model = {
        # format: 'projects/{project}/locations/{location}/models/{model}'
        "model": model_name,
        "display_name": deployed_model_display_name,
        # AutoML Vision models require `automatic_resources` field
        # Other model types may require `dedicated_resources` field instead
        "automatic_resources": {"min_replica_count": 1, "max_replica_count": 1},
    }
    response = client.deploy_model(
        endpoint=name, deployed_model=deployed_model, traffic_split=traffic_split
    )
    print("Long running operation:", response.operation.name)
    deploy_model_response = response.result(timeout=7200)
    print("deploy_model_response")
    deployed_model = deploy_model_response.deployed_model
    print(" deployed_model")
    print("  id:", deployed_model.id)
    print("  model:", deployed_model.model)
    print("  display_name:", deployed_model.display_name)
    dedicated_resources = deployed_model.dedicated_resources
    automatic_resources = deployed_model.automatic_resources


# [END aiplatform_deploy_model_sample]
