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
from uuid import uuid4

import export_model_tabular_classification_sample
import pytest


PROJECT_ID = os.getenv("BUILD_SPECIFIC_GCLOUD_PROJECT")
MODEL_ID = "6036688272397172736"  # iris 1000
GCS_BUCKET = "gs://ucaip-samples-test-output"
GCS_PREFIX = f"tmp/export_model_test_{uuid4()}"


@pytest.fixture(scope="function", autouse=True)
def teardown(storage_client):
    yield

    bucket = storage_client.get_bucket("ucaip-samples-test-output")
    blobs = bucket.list_blobs(prefix=GCS_PREFIX)
    for blob in blobs:
        blob.delete()


@pytest.mark.skip(reason="https://github.com/googleapis/java-aiplatform/issues/420")
def test_ucaip_generated_export_model_tabular_classification_sample(capsys):
    export_model_tabular_classification_sample.export_model_tabular_classification_sample(
        project=PROJECT_ID,
        model_id=MODEL_ID,
        gcs_destination_output_uri_prefix=f"{GCS_BUCKET}/{GCS_PREFIX}",
    )
    out, _ = capsys.readouterr()
    assert "output_info" in out
