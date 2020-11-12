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

# [START aiplatform_create_batch_prediction_job_video_object_tracking_sample]
from google.cloud import aiplatform
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value


def run_sample():
    # TODO(dev): replace these variables to run the code
    project = "YOUR-PROJECT"
    display_name = "YOUR-DISPLAY-NAME"
    model_name = "YOUR-MODEL-NAME"
    gcs_source_uri = "YOUR-GCS-SOURCE-URI"
    gcs_destination_output_uri_prefix = "YOUR-GCS-DESTINATION-OUTPUT-URI-PREFIX"
    create_batch_prediction_job_video_object_tracking_sample(
        project,
        display_name,
        model_name,
        gcs_source_uri,
        gcs_destination_output_uri_prefix,
    )


def create_batch_prediction_job_video_object_tracking_sample(
    project: str,
    display_name: str,
    model_name: str,
    gcs_source_uri: str,
    gcs_destination_output_uri_prefix: str,
    location: str = "us-central1",
):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.JobServiceClient(client_options=client_options)
    model_parameters_dict = {"confidenceThreshold": 0.0}
    model_parameters = json_format.ParseDict(model_parameters_dict, Value())

    batch_prediction_job = {
        "display_name": display_name,
        # Format: 'projects/{project}/locations/{location}/models/{model_id}'
        "model": model_name,
        "model_parameters": model_parameters,
        "input_config": {
            "instances_format": "jsonl",
            "gcs_source": {"uris": [gcs_source_uri]},
        },
        "output_config": {
            "predictions_format": "jsonl",
            "gcs_destination": {"output_uri_prefix": gcs_destination_output_uri_prefix},
        },
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_batch_prediction_job(
        parent=parent, batch_prediction_job=batch_prediction_job
    )
    print("response:", response)


# [END aiplatform_create_batch_prediction_job_video_object_tracking_sample]
