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

# [START aiplatform_create_data_labeling_job_images_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def create_data_labeling_job_images_sample(
    display_name: str,
    dataset: str,
    instruction_uri: str,
    annotation_spec: str,
    project: str,
):
    client_options = {
        "api_endpoint": "us-central1-autopush-aiplatform.sandbox.googleapis.com"
    }
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.JobServiceClient(client_options=client_options)
    location = "us-central1"
    parent = "projects/{project}/locations/{location}".format(
        project=project, location=location
    )
    inputs_dict = {"annotation_specs": [annotation_spec]}
    inputs = json_format.ParseDict(inputs_dict, Value())

    data_labeling_job = {
        "display_name": display_name,
        # Full resource name: projects/{project_id}/locations/{location}/datasets/{dataset_id}
        "datasets": [dataset],
        # labeler_count must be 1, 3, or 5
        "labeler_count": 1,
        "instruction_uri": instruction_uri,
        "inputs_schema_uri": "gs://google-cloud-aiplatform/schema/datalabelingjob/inputs/image_classification.yaml",
        "inputs": inputs,
        "annotation_labels": {
            "aiplatform.googleapis.com/annotation_set_name": "my_test_saved_query"
        },
    }
    response = client.create_data_labeling_job(
        parent=parent, data_labeling_job=data_labeling_job
    )
    print("response")
    print(" name:", response.name)
    print(" display_name:", response.display_name)
    print(" datasets:", response.datasets)
    print(" labeler_count:", response.labeler_count)
    print(" instruction_uri:", response.instruction_uri)
    print(" inputs_schema_uri:", response.inputs_schema_uri)
    print(" inputs:", json_format.MessageToDict(response._pb.inputs))
    print(" state:", response.state)
    print(" labeling_progress:", response.labeling_progress)
    print(" labels:", response.labels)
    print(" specialist_pools:", response.specialist_pools)
    annotation_labels = response.annotation_labels
    current_spend = response.current_spend


# [END aiplatform_create_data_labeling_job_images_sample]
