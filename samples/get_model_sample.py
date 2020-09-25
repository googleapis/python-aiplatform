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
    client_options = dict(api_endpoint="us-central1-aiplatform.googleapis.com")
    client = aiplatform.ModelServiceClient(client_options=client_options)
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
    print(" create_time:", response.create_time)
    print(" update_time:", response.update_time)
    print(" labels:", response.labels)
    predict_schemata = response.predict_schemata
    print(" predict_schemata")
    print("  instance_schema_uri:", predict_schemata.instance_schema_uri)
    print("  parameters_schema_uri:", predict_schemata.parameters_schema_uri)
    print("  prediction_schema_uri:", predict_schemata.prediction_schema_uri)
    supported_export_formats = response.supported_export_formats
    for supported_export_format in supported_export_formats:
        print(" supported_export_format")
        print("  id:", supported_export_format.id)
    container_spec = response.container_spec
    print(" container_spec")
    print("  image_uri:", container_spec.image_uri)
    print("  command:", container_spec.command)
    print("  args:", container_spec.args)
    print("  predict_route:", container_spec.predict_route)
    print("  health_route:", container_spec.health_route)
    env = container_spec.env
    for env in env:
        print("  env")
        print("   name:", env.name)
        print("   value:", env.value)
    ports = container_spec.ports
    for port in ports:
        print("  port")
        print("   container_port:", port.container_port)
    deployed_models = response.deployed_models
    for deployed_model in deployed_models:
        print(" deployed_model")
        print("  endpoint:", deployed_model.endpoint)
        print("  deployed_model_id:", deployed_model.deployed_model_id)


# [END aiplatform_get_model_sample]
