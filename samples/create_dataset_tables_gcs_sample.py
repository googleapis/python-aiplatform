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

# [START aiplatform_create_dataset_tables_gcs_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def create_dataset_tables_gcs_sample(display_name: str, gcs_uri: str, project: str):
    client_options = dict(api_endpoint="us-central1-aiplatform.googleapis.com")
    client = aiplatform.DatasetServiceClient(client_options=client_options)
    location = "us-central1"
    parent = "projects/{project}/locations/{location}".format(
        project=project, location=location
    )
    metadata_dict = {"input_config": {"gcs_source": {"uri": [gcs_uri]}}}
    metadata = json_format.ParseDict(metadata_dict, Value())

    dataset = {
        "display_name": display_name,
        "metadata_schema_uri": "gs://google-cloud-aiplatform/schema/dataset/metadata/tables_1.0.0.yaml",
        "metadata": metadata,
    }
    response = client.create_dataset(parent=parent, dataset=dataset)
    print("Long running operation:", response.operation.name)
    create_dataset_response = response.result(timeout=300)
    print("create_dataset_response")
    print(" name:", create_dataset_response.name)
    print(" display_name:", create_dataset_response.display_name)
    print(" metadata_schema_uri:", create_dataset_response.metadata_schema_uri)
    print(" metadata:", json_format.MessageToDict(create_dataset_response._pb.metadata))


# [END aiplatform_create_dataset_tables_gcs_sample]
