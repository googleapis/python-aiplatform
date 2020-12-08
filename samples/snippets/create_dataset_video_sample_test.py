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
from uuid import uuid4

import pytest

import create_dataset_video_sample
import helpers

PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
VIDEO_METADATA_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/video_1.0.0.yaml"
)


@pytest.fixture(scope="function", autouse=True)
def teardown(teardown_dataset):
    yield


def test_ucaip_generated_create_dataset_video_sample_vision(capsys, shared_state):
    create_dataset_video_sample.create_dataset_video_sample(
        display_name=f"temp_create_dataset_test_{uuid4()}", project=PROJECT_ID
    )
    out, _ = capsys.readouterr()
    assert "create_dataset_response" in out

    shared_state["dataset_name"] = helpers.get_name(out)
