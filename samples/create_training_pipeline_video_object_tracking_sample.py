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

# [START aiplatform_create_training_pipeline_video_object_tracking_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def create_training_pipeline_video_object_tracking_sample(
    display_name: str, dataset_id: str, model_display_name: str, project: str
):
    client_options = dict(api_endpoint="us-central1-aiplatform.googleapis.com")
    client = aiplatform.PipelineServiceClient(client_options=client_options)
    location = "us-central1"
    parent = "projects/{project}/locations/{location}".format(
        project=project, location=location
    )
    training_task_inputs_dict = {"modelType": "CLOUD"}
    training_task_inputs = json_format.ParseDict(training_task_inputs_dict, Value())

    training_pipeline = {
        "display_name": display_name,
        "training_task_definition": "gs://google-cloud-aiplatform/schema/trainingjob/definition/automl_video_object_tracking_1.0.0.yaml",
        "training_task_inputs": training_task_inputs,
        "input_data_config": {"dataset_id": dataset_id},
        "model_to_upload": {"display_name": model_display_name},
    }
    response = client.create_training_pipeline(
        parent=parent, training_pipeline=training_pipeline
    )
    print("response")
    print(" name:", response.name)
    print(" display_name:", response.display_name)
    print(" training_task_definition:", response.training_task_definition)
    print(
        " training_task_inputs:",
        json_format.MessageToDict(response._pb.training_task_inputs),
    )
    print(
        " training_task_metadata:",
        json_format.MessageToDict(response._pb.training_task_metadata),
    )
    print(" state:", response.state)
    print(" create_time:", response.create_time)
    print(" start_time:", response.start_time)
    print(" end_time:", response.end_time)
    print(" update_time:", response.update_time)
    print(" labels:", response.labels)
    input_data_config = response.input_data_config
    print(" input_data_config")
    print("  dataset_id:", input_data_config.dataset_id)
    print("  annotations_filter:", input_data_config.annotations_filter)
    fraction_split = input_data_config.fraction_split
    print("  fraction_split")
    print("   training_fraction:", fraction_split.training_fraction)
    print("   validation_fraction:", fraction_split.validation_fraction)
    print("   test_fraction:", fraction_split.test_fraction)
    filter_split = input_data_config.filter_split
    print("  filter_split")
    print("   training_filter:", filter_split.training_filter)
    print("   validation_filter:", filter_split.validation_filter)
    print("   test_filter:", filter_split.test_filter)
    predefined_split = input_data_config.predefined_split
    print("  predefined_split")
    print("   key:", predefined_split.key)
    timestamp_split = input_data_config.timestamp_split
    print("  timestamp_split")
    print("   training_fraction:", timestamp_split.training_fraction)
    print("   validation_fraction:", timestamp_split.validation_fraction)
    print("   test_fraction:", timestamp_split.test_fraction)
    print("   key:", timestamp_split.key)
    model_to_upload = response.model_to_upload
    print(" model_to_upload")
    print("  name:", model_to_upload.name)
    print("  display_name:", model_to_upload.display_name)
    print("  description:", model_to_upload.description)
    print("  metadata_schema_uri:", model_to_upload.metadata_schema_uri)
    print("  metadata:", json_format.MessageToDict(model_to_upload._pb.metadata))
    print("  training_pipeline:", model_to_upload.training_pipeline)
    print("  artifact_uri:", model_to_upload.artifact_uri)
    print(
        "  supported_deployment_resources_types:",
        model_to_upload.supported_deployment_resources_types,
    )
    print(
        "  supported_input_storage_formats:",
        model_to_upload.supported_input_storage_formats,
    )
    print(
        "  supported_output_storage_formats:",
        model_to_upload.supported_output_storage_formats,
    )
    print("  create_time:", model_to_upload.create_time)
    print("  update_time:", model_to_upload.update_time)
    print("  labels:", model_to_upload.labels)
    error = response.error
    print(" error")
    print("  code:", error.code)
    print("  message:", error.message)
    details = error.details


# [END aiplatform_create_training_pipeline_video_object_tracking_sample]
