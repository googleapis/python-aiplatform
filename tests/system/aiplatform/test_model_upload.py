# -*- coding: utf-8 -*-

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
#

import tempfile

import pytest

from google import auth as google_auth
from google.cloud import aiplatform
from google.cloud import storage

from tests.system.aiplatform import e2e_base

# TODO(vinnys): Replace with env var `BUILD_SPECIFIC_GCP_PROJECT` once supported
_, _TEST_PROJECT = google_auth.default()
_TEST_LOCATION = "us-central1"

_XGBOOST_MODEL_URI = "gs://cloud-samples-data-us-central1/vertex-ai/google-cloud-aiplatform-ci-artifacts/models/iris_xgboost/model.bst"


@pytest.mark.usefixtures("delete_staging_bucket")
class TestModel(e2e_base.TestEndToEnd):
    _temp_prefix = f"{_TEST_PROJECT}-vertex-staging-{_TEST_LOCATION}"

    def test_upload_and_deploy_xgboost_model(self, shared_state):
        """Upload XGBoost model from local file and deploy it for prediction. Additionally, update model name, description and labels"""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        storage_client = storage.Client(project=_TEST_PROJECT)
        model_blob = storage.Blob.from_string(
            uri=_XGBOOST_MODEL_URI, client=storage_client
        )
        model_path = tempfile.mktemp() + ".my_model.xgb"
        model_blob.download_to_filename(filename=model_path)

        model = aiplatform.Model.upload_xgboost_model_file(model_file_path=model_path,)
        shared_state["resources"] = [model]

        staging_bucket = storage.Blob.from_string(
            uri=model.uri, client=storage_client
        ).bucket
        # Checking that the bucket is auto-generated
        assert "-vertex-staging-" in staging_bucket.name

        shared_state["bucket"] = staging_bucket

        # Currently we need to explicitly specify machine type.
        # See https://github.com/googleapis/python-aiplatform/issues/773
        endpoint = model.deploy(machine_type="n1-standard-2")
        shared_state["resources"].append(endpoint)
        predict_response = endpoint.predict(instances=[[0, 0, 0]])
        assert len(predict_response.predictions) == 1

        model = model.update(
            display_name="new_name",
            description="new_description",
            labels={"my_label": "updated"},
        )
        assert model.display_name == "new_name"
        assert model.description == "new_description"
        assert model.labels == {"my_label": "updated"}
