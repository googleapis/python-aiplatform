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

# [START aiplatform_create_batch_prediction_job_tabular_forecasting_sample]
from google.cloud import aiplatform_v1beta1


def create_batch_prediction_job_tabular_forecasting_sample(
    project: str,
    display_name: str,
    model_name: str,
    gcs_source_uri: str,
    gcs_destination_output_uri_prefix: str,
    predictions_format: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform_v1beta1.JobServiceClient(client_options=client_options)
    batch_prediction_job = {
        "display_name": display_name,
        # Format: 'projects/{project}/locations/{location}/models/{model_id}'
        "model": model_name,
        "input_config": {
            "instances_format": predictions_format,
            "gcs_source": {"uris": [gcs_source_uri]},
        },
        "output_config": {
            "predictions_format": predictions_format,
            "gcs_destination": {"output_uri_prefix": gcs_destination_output_uri_prefix},
        },
    }
    parent = f"projects/{project}/locations/{location}"
    response = client.create_batch_prediction_job(
        parent=parent, batch_prediction_job=batch_prediction_job
    )
    print("response:", response)


# [END aiplatform_create_batch_prediction_job_tabular_forecasting_sample]
