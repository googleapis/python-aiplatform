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

# [START aiplatform_get_model_evaluation_image_classification_sample]
from google.cloud import aiplatform
from google.protobuf import json_format


def get_model_evaluation_image_classification_sample(
    project: str, model_id: str, evaluation_id: str
):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.ModelServiceClient(client_options=client_options)
    location = "us-central1"
    name = "projects/{project}/locations/{location}/models/{model}/evaluations/{evaluation}".format(
        project=project, location=location, model=model_id, evaluation=evaluation_id
    )
    response = client.get_model_evaluation(name=name)
    print("response")
    print(" name:", response.name)
    print(" metrics_schema_uri:", response.metrics_schema_uri)
    print(" metrics:", json_format.MessageToDict(response._pb.metrics))
    print(" slice_dimensions:", response.slice_dimensions)
    model_explanation = response.model_explanation


# [END aiplatform_get_model_evaluation_image_classification_sample]
