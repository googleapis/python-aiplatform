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
import importlib

from google import auth as google_auth
from google.cloud import aiplatform
from google.cloud import storage
from google.cloud.aiplatform import initializer

# TODO(vinnys): Replace with env var `BUILD_SPECIFIC_GCP_PROJECT` once supported
_, _TEST_PROJECT = google_auth.default()
_TEST_LOCATION = "us-central1"

_XGBOOST_MODEL_URI = "gs://ucaip-test-us-central1/models/iris_xgboost/model.bst"


class TestModel:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    def test_upload_and_deploy_xgboost_model(self):
        """Upload XGBoost model from local file and deploy it for prediction."""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        storage_client = storage.Client(project=_TEST_PROJECT)
        model_blob = storage.Blob.from_string(
            uri=_XGBOOST_MODEL_URI, client=storage_client
        )
        model_path = tempfile.mktemp() + ".my_model.xgb"
        model_blob.download_to_filename(filename=model_path)

        model = aiplatform.Model.upload_xgboost_model_file(model_file_path=model_path,)

        # Currently we need to explicitly specify machine type.
        # See https://github.com/googleapis/python-aiplatform/issues/773
        endpoint = model.deploy(machine_type="n1-standard-2")
        predict_response = endpoint.predict(instances=[[0, 0, 0]])
        assert len(predict_response.predictions) == 1

        endpoint.delete(force=True)
        model.delete()
