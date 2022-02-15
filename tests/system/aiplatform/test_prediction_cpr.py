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

import datetime
import json
import os
import pytest

from test_resources.cpr_user_code.predictor import SklearnPredictor

from google import auth as google_auth
from google.cloud import aiplatform

from tests.system.aiplatform import e2e_base
from google.cloud.aiplatform.prediction import LocalModel

_, _TEST_PROJECT = google_auth.default()
_TEST_LOCATION = "us-central1"

_TIMESTAMP = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
_IMAGE_URI = f"gcr.io/ucaip-sample-tests/prediction-cpr/sklearn:{_TIMESTAMP}"
_DIR_NAME = os.path.dirname(os.path.abspath(__file__))
_USER_CODE_DIR = os.path.join(_DIR_NAME, "test_resources/cpr_user_code")
_REQUIREMENTS_FILE = "requirements.txt"
_ARTIFACT_URI = "gs://cloud-samples-data-us-central1/vertex-ai/prediction-cpr/sklearn"
_PREDICTION_INPUT = [[4.6, 3.1, 1.5, 0.2]]


@pytest.mark.usefixtures("teardown")
class TestPredictionCpr(e2e_base.TestEndToEnd):
    """End to end system test of the Vertex SDK with Prediction custom prediction routines."""

    _temp_prefix = "temp-vertex-sdk-e2e-prediction-cpr"

    def test_create_cpr_model_upload_and_deploy(self, shared_state):
        """Creates a CPR model from custom predictor, uploads it and deploys."""

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        local_model = LocalModel.create_cpr_model(
            _USER_CODE_DIR,
            _IMAGE_URI,
            predictor=SklearnPredictor,
            requirements_path=os.path.join(_USER_CODE_DIR, _REQUIREMENTS_FILE),
        )

        with local_model.deploy_to_local_endpoint(
            artifact_uri=_ARTIFACT_URI,
            credential_path=os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"),
        ) as local_endpoint:
            local_predict_response = local_endpoint.predict(
                request=f'{{"instances": {_PREDICTION_INPUT}}}',
                headers={"Content-Type": "application/json"},
            )
        assert len(json.loads(local_predict_response.content)["predictions"]) == 1

        local_model.push_image()

        model = local_model.upload(
            f"cpr_e2e_test_{_TIMESTAMP}", artifact_uri=_ARTIFACT_URI
        )
        shared_state["resources"] = [model]

        # Currently we need to explicitly specify machine type.
        # See https://github.com/googleapis/python-aiplatform/issues/773
        endpoint = model.deploy(machine_type="n1-standard-2")
        shared_state["resources"].append(endpoint)
        predict_response = endpoint.predict(instances=_PREDICTION_INPUT)
        assert len(predict_response.predictions) == 1
