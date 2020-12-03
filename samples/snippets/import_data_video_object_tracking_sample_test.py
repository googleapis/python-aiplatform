# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import pytest
import os

from uuid import uuid4
from google.cloud import aiplatform

import import_data_video_object_tracking_sample
import delete_dataset_sample


PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
GCS_SOURCE = "gs://ucaip-sample-resources/video_object_tracking_train.jsonl"
METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/video_1.0.0.yaml"
)


@pytest.fixture(scope="function", autouse=True)
def dataset_name():
    client_options = {"api_endpoint": "us-central1-aiplatform.googleapis.com"}
    client = aiplatform.gapic.DatasetServiceClient(client_options=client_options)

    dataset = aiplatform.gapic.Dataset(
        display_name=f"temp_import_dataset_test_{uuid4()}",
        metadata_schema_uri=METADATA_SCHEMA_URI,
    )

    operation = client.create_dataset(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}", dataset=dataset
    )

    created_dataset = operation.result(timeout=120)

    yield created_dataset.name

    dataset_id = created_dataset.name.split("/")[-1]

    # Delete the created dataset
    delete_dataset_sample.delete_dataset_sample(
        project=PROJECT_ID, dataset_id=dataset_id
    )


def test_ucaip_generated_import_data_video_object_tracking_sample_single_label_image(
    capsys, dataset_name
):
    dataset_id = dataset_name.split("/")[-1]

    import_data_video_object_tracking_sample.import_data_video_object_tracking_sample(
        project=PROJECT_ID, dataset_id=dataset_id, gcs_source_uri=GCS_SOURCE,
    )
    out, _ = capsys.readouterr()
    assert "import_data_response" in out
