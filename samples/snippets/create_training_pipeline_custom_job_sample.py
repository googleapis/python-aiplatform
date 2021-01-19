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

# [START aiplatform_create_training_pipeline_custom_job_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def create_training_pipeline_custom_job_sample(
    project: str,
    display_name: str,
    model_display_name: str,
    container_image_uri: str,
    base_output_directory_prefix: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.PipelineServiceClient(client_options=client_options)

    training_task_inputs_dict = {
        "workerPoolSpecs": [
            {
                "replicaCount": 1,
                "machineSpec": {"machineType": "n1-standard-4"},
                "containerSpec": {
                    # A working docker image can be found at gs://cloud-samples-data/ai-platform/mnist_tfrecord/custom_job
                    "imageUri": container_image_uri,
                    "args": [
                        # AIP_MODEL_DIR is set by the service according to baseOutputDirectory.
                        "--model_dir=$(AIP_MODEL_DIR)",
                    ],
                },
            }
        ],
        "baseOutputDirectory": {
            # The GCS location for outputs must be accessible by the project's AI Platform service account.
            "output_uri_prefix": base_output_directory_prefix
        },
    }
    training_task_inputs = json_format.ParseDict(training_task_inputs_dict, Value())

    training_task_definition = "gs://google-cloud-aiplatform/schema/trainingjob/definition/custom_task_1.0.0.yaml"
    image_uri = "gcr.io/cloud-aiplatform/prediction/tf-cpu.1-15:latest"

    training_pipeline = {
        "display_name": display_name,
        "training_task_definition": training_task_definition,
        "training_task_inputs": training_task_inputs,
        "model_to_upload": {
            "display_name": model_display_name,
            "container_spec": {"image_uri": image_uri},
        },
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_training_pipeline(
        parent=parent, training_pipeline=training_pipeline
    )
    print("response:", response)


# [END aiplatform_create_training_pipeline_custom_job_sample]
