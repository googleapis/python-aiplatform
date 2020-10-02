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

# [START aiplatform_get_model_sample]
from google.cloud import aiplatform
from google.protobuf import json_format


def get_model_sample(project: str, model_id: str):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.ModelServiceClient(client_options=client_options)
    location = "us-central1"
    name = client.model_path(project=project, location=location, model=model_id)
    response = client.get_model(name=name)
    print("response")
    print(" name:", response.name)
    print(" display_name:", response.display_name)
    print(" description:", response.description)
    print(" metadata_schema_uri:", response.metadata_schema_uri)
    print(" metadata:", json_format.MessageToDict(response._pb.metadata))
    print(" training_pipeline:", response.training_pipeline)
    print(" artifact_uri:", response.artifact_uri)
    print(
        " supported_deployment_resources_types:",
        response.supported_deployment_resources_types,
    )
    print(" supported_input_storage_formats:", response.supported_input_storage_formats)
    print(
        " supported_output_storage_formats:", response.supported_output_storage_formats
    )
    print(" labels:", response.labels)
    predict_schemata = response.predict_schemata
    supported_export_formats = response.supported_export_formats
    container_spec = response.container_spec
    deployed_models = response.deployed_models


# [END aiplatform_get_model_sample]
