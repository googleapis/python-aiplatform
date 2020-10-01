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

# [START aiplatform_upload_model_sample]
from google.cloud import aiplatform


def upload_model_sample(
    display_name: str,
    metadata_schema_uri: str,
    image_uri: str,
    artifact_uri: str,
    project: str,
):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.ModelServiceClient(client_options=client_options)
    location = "us-central1"
    parent = "projects/{project}/locations/{location}".format(
        project=project, location=location
    )
    model = {
        "display_name": display_name,
        "metadata_schema_uri": metadata_schema_uri,
        # The artifact_uri should be the path to a GCS directory containing
        # saved model artifacts.  The bucket must be accessible for the
        # project's AI Platform service account and in the same region as
        # the api endpoint.
        "artifact_uri": artifact_uri,
        "container_spec": {
            "image_uri": image_uri,
            "command": [],
            "args": [],
            "env": [],
            "ports": [],
            "predict_route": "",
            "health_route": "",
        },
    }
    response = client.upload_model(parent=parent, model=model)
    print("Long running operation:", response.operation.name)
    upload_model_response = response.result(timeout=180)
    print("upload_model_response")
    print(" model:", upload_model_response.model)


# [END aiplatform_upload_model_sample]
