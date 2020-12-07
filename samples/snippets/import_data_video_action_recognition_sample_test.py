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


import os
import uuid

from google.cloud import aiplatform
import pytest

import import_data_video_action_recognition_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
GCS_SOURCE = "gs://automl-video-demo-data/ucaip-var/swimrun.jsonl"
METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/video_1.0.0.yaml"
)

DISPLAY_NAME = f"temp_import_data_video_action_recognition_test_{uuid.uuid4()}"


@pytest.fixture(scope="function", autouse=True)
def setup(shared_state, dataset_client):
    dataset = aiplatform.gapic.Dataset(
        display_name=f"temp_import_dataset_test_{uuid4()}",
        metadata_schema_uri=METADATA_SCHEMA_URI,
    )

    operation = dataset_client.create_dataset(
        parent=f"projects/{PROJECT_ID}/locations/{LOCATION}", dataset=dataset
    )

    dataset = operation.result(timeout=300)
    shared_state["dataset_name"] = dataset.name

    yield


@pytest.fixture(scope="function", autouse=True)
def teardown(shared_state, dataset_client):
    yield

    # Delete the created dataset
    dataset_client.delete_dataset(name=shared_state["dataset_name"])


def test_import_data_video_action_recognition_sample(
    capsys, shared_state, dataset_client
):
    dataset_id = shared_state["dataset_name"].split("/")[-1]

    import_data_video_action_recognition_sample.import_data_video_action_recognition_sample(
        project=PROJECT_ID, dataset_id=dataset_id, gcs_source_uri=GCS_SOURCE,
    )
    out, _ = capsys.readouterr()

    assert "import_data_response" in out
