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

# [START aiplatform_list_model_evaluation_slices_sample]
from google.cloud import aiplatform
from google.protobuf import json_format


def list_model_evaluation_slices_sample(
    project: str, model_id: str, evaluation_id: str
):
    client_options = dict(api_endpoint="us-central1-aiplatform.googleapis.com")
    client = aiplatform.ModelServiceClient(client_options=client_options)
    location = "us-central1"
    parent = "projects/{project}/locations/{location}/models/{model}/evaluations/{evaluation}".format(
        project=project, location=location, model=model_id, evaluation=evaluation_id
    )
    response = client.list_model_evaluation_slices(parent=parent)
    for model_evaluation_slice in response:
        print("model_evaluation_slice")
        print(" name:", model_evaluation_slice.name)
        print(" metrics_schema_uri:", model_evaluation_slice.metrics_schema_uri)
        print(
            " metrics:", json_format.MessageToDict(model_evaluation_slice._pb.metrics)
        )
        print(" create_time:", model_evaluation_slice.create_time)
        slice = model_evaluation_slice.slice
        print(" slice")
        print("  dimension:", slice.dimension)
        print("  value:", slice.value)


# [END aiplatform_list_model_evaluation_slices_sample]
