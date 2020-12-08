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

import pytest

import import_data_video_classification_sample

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
LOCATION = "us-central1"
GCS_SOURCE = "gs://ucaip-sample-resources/video_classification_train.jsonl"
METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/video_1.0.0.yaml"
)


@pytest.fixture(scope="function", autouse=True)
def setup(create_dataset):
    create_dataset(PROJECT_ID, LOCATION, METADATA_SCHEMA_URI)
    yield


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_dataset):
    yield


def test_ucaip_generated_import_data_video_classification_sample_single_label_image(
    capsys, shared_state
):
    dataset_id = shared_state["dataset_name"].split("/")[-1]

    import_data_video_classification_sample.import_data_video_classification_sample(
        project=PROJECT_ID, dataset_id=dataset_id, gcs_source_uri=GCS_SOURCE,
    )
    out, _ = capsys.readouterr()
    assert "import_data_response" in out
