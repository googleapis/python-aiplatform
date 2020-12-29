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

# [START aiplatform_import_data_video_classification_sample]
from google.cloud import aiplatform


def import_data_video_classification_sample(
    project: str,
    dataset_id: str,
    gcs_source_uri: str,
    location: str = "us-central1",
    api_endpoint: str = "us-central1-aiplatform.googleapis.com",
    timeout: int = 1800,
):
    # The AI Platform services require regional API endpoints.
    client_options = {"api_endpoint": api_endpoint}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.gapic.DatasetServiceClient(client_options=client_options)
    import_configs = [
        {
            "gcs_source": {"uris": [gcs_source_uri]},
            "import_schema_uri": "gs://google-cloud-aiplatform/schema/dataset/ioformat/video_classification_io_format_1.0.0.yaml",
        }
    ]
    name = client.dataset_path(project=project, location=location, dataset=dataset_id)
    response = client.import_data(name=name, import_configs=import_configs)
    print("Long running operation:", response.operation.name)
    import_data_response = response.result(timeout=timeout)
    print("import_data_response:", import_data_response)


# [END aiplatform_import_data_video_classification_sample]
