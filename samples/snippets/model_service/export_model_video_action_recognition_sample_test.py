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

import os

import export_model_video_action_recognition_sample
import pytest


PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
MODEL_ID = (
    "3422489426196955136"  # permanent_swim_run_videos_action_recognition_edge_model
)
GCS_URI = (
    "gs://ucaip-samples-test-output/tmp/export_model_video_action_recognition_sample"
)
EXPORT_FORMAT = "tf-saved-model"


@pytest.fixture(scope="function", autouse=True)
def teardown(storage_client):
    yield

    bucket = storage_client.get_bucket("ucaip-samples-test-output")
    blobs = bucket.list_blobs(prefix="tmp/export_model_video_action_recognition_sample")
    for blob in blobs:
        blob.delete()


@pytest.mark.skip(reason="https://github.com/googleapis/java-aiplatform/issues/420")
def test_export_model_video_action_recognition_sample(capsys):
    export_model_video_action_recognition_sample.export_model_video_action_recognition_sample(
        project=PROJECT_ID,
        model_id=MODEL_ID,
        gcs_destination_output_uri_prefix=GCS_URI,
        export_format=EXPORT_FORMAT,
    )
    out, _ = capsys.readouterr()
    assert "output_info" in out
