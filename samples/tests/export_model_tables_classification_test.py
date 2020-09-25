# Generated code sample for google.cloud.aiplatform.DatasetServiceClient.get_dataset
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

import pytest

from samples import export_model_tables_classification_sample
from google.cloud import storage

PROJECT_ID = "ucaip-sample-tests"
MODEL_ID = "5359002081594179584" # iris 1000
GCS_URI = "gs://ucaip-samples-test-output/tmp/export_model_test"

@pytest.fixture(scope="function", autouse=True)
def teardown():
    yield

    storage_client = storage.Client()
    bucket = storage_client.get_bucket("ucaip-samples-test-output")
    blobs = bucket.list_blobs(prefix='tmp/export_model_test')
    for blob in blobs:
        blob.delete()

def test_ucaip_generated_export_model_tables_classification_sample(capsys):
    export_model_tables_classification_sample.export_model_tables_classification_sample(
        project = PROJECT_ID,
        model_id = MODEL_ID,
        gcs_destination_output_uri_prefix = GCS_URI
    )
    out, _ = capsys.readouterr()
    assert "export_model_response" in out
