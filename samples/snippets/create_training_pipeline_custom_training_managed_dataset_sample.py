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

# [START aiplatform_create_training_pipeline_custom_training_managed_dataset_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def create_training_pipeline_custom_training_managed_dataset_sample(
    project: str,
    display_name: str,
    model_display_name: str,
    dataset_id: str,
    annotation_schema_uri: str,
    training_container_spec_image_uri: str,
    model_container_spec_image_uri: str,
    base_output_uri_prefix: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PipelineServiceClient(client_options=client_options)

    # input_data_config
    input_data_config = {
        "dataset_id": dataset_id,
        "annotation_schema_uri": annotation_schema_uri,
        "gcs_destination": {"output_uri_prefix": base_output_uri_prefix},
    }

    # training_task_definition
    custom_task_definition = "gs://google-cloud-aiplatform/schema/trainingjob/definition/custom_task_1.0.0.yaml"

    # training_task_inputs
    training_container_spec = {
        "imageUri": training_container_spec_image_uri,
        # AIP_MODEL_DIR is set by the service according to baseOutputDirectory.
        "args": ["--model-dir=$(AIP_MODEL_DIR)"],
    }

    training_worker_pool_spec = {
        "replicaCount": 1,
        "machineSpec": {"machineType": "n1-standard-8"},
        "containerSpec": training_container_spec,
    }

    training_task_inputs_dict = {
        "workerPoolSpecs": [training_worker_pool_spec],
        "baseOutputDirectory": {"outputUriPrefix": base_output_uri_prefix},
    }

    training_task_inputs = json_format.ParseDict(training_task_inputs_dict, Value())

    # model_to_upload
    model_container_spec = {
        "image_uri": model_container_spec_image_uri,
        "command": [],
        "args": [],
    }

    model = {"display_name": model_display_name, "container_spec": model_container_spec}

    training_pipeline = {
        "display_name": display_name,
        "input_data_config": input_data_config,
        "training_task_definition": custom_task_definition,
        "training_task_inputs": training_task_inputs,
        "model_to_upload": model,
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_training_pipeline(
        parent=parent, training_pipeline=training_pipeline
    )
    print("response:", response)


# [END aiplatform_create_training_pipeline_custom_training_managed_dataset_sample]
