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

# [START aiplatform_get_training_pipeline_sample]
from google.cloud import aiplatform
from google.protobuf import json_format


def get_training_pipeline_sample(project: str, training_pipeline_id: str):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.PipelineServiceClient(client_options=client_options)
    location = "us-central1"
    name = client.training_pipeline_path(
        project=project, location=location, training_pipeline=training_pipeline_id
    )
    response = client.get_training_pipeline(name=name)
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
    print(" start_time:", response.start_time)
    print(" end_time:", response.end_time)
    print(" labels:", response.labels)
    input_data_config = response.input_data_config
    model_to_upload = response.model_to_upload
    error = response.error


# [END aiplatform_get_training_pipeline_sample]
