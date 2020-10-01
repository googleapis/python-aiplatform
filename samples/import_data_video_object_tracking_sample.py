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

# [START aiplatform_import_data_video_object_tracking_sample]
from google.cloud import aiplatform


def import_data_video_object_tracking_sample(
    gcs_source_uri: str, project: str, dataset_id: str
):
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    # Initialize client that will be used to create and send requests.
    # This client only needs to be created once, and can be reused for multiple requests.
    client = aiplatform.DatasetServiceClient(client_options=client_options)
    location = "us-central1"
    name = client.dataset_path(project=project, location=location, dataset=dataset_id)
    import_configs = [
        {
            "gcs_source": {"uris": [gcs_source_uri]},
            "import_schema_uri": "gs://google-cloud-aiplatform/schema/dataset/ioformat/video_object_tracking_io_format_1.0.0.yaml",
        }
    ]
    response = client.import_data(name=name, import_configs=import_configs)
    print("Long running operation:", response.operation.name)
    import_data_response = response.result(timeout=1800)
    print("import_data_response:", import_data_response)


# [END aiplatform_import_data_video_object_tracking_sample]
