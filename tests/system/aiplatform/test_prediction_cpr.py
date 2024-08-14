# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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
import logging
import os
import pytest
import subprocess

from tests.system.aiplatform.test_resources.cpr_user_code.predictor import (
    SklearnPredictor,
)

from google.cloud import aiplatform
from google.cloud.aiplatform import models
from google.cloud.aiplatform.prediction import LocalModel

from tests.system.aiplatform import e2e_base

_TIMESTAMP = f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
_IMAGE_URI = f"gcr.io/ucaip-sample-tests/prediction-cpr/sklearn:{_TIMESTAMP}"
_DIR_NAME = os.path.dirname(os.path.abspath(__file__))
_USER_CODE_DIR = os.path.join(_DIR_NAME, "test_resources/cpr_user_code")
_REQUIREMENTS_FILE = "requirements.txt"
_DIR_NAME = os.path.dirname(os.path.abspath(__file__))
_LOCAL_MODEL_DIR = os.path.join(_DIR_NAME, "test_resources/cpr_model")
_ARTIFACT_URI = "gs://cloud-aiplatform-us-central1/vertex-ai/prediction-cpr/sklearn"
_PREDICTION_INPUT = [[4.6, 3.1, 1.5, 0.2]]


@pytest.mark.usefixtures("tear_down_resources")
class TestPredictionCpr(e2e_base.TestEndToEnd):
    """End to end system test of the Vertex SDK with Prediction custom prediction routines."""

    _temp_prefix = "temp-vertex-sdk-e2e-prediction-cpr"

    def test_build_cpr_model_upload_and_deploy(self, shared_state, caplog):
        """Creates a CPR model from custom predictor, uploads it and deploys."""

        caplog.set_level(logging.INFO)

        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        local_model = LocalModel.build_cpr_model(
            _USER_CODE_DIR,
            _IMAGE_URI,
            predictor=SklearnPredictor,
            requirements_path=os.path.join(_USER_CODE_DIR, _REQUIREMENTS_FILE),
        )

        with local_model.deploy_to_local_endpoint(
            artifact_uri=_LOCAL_MODEL_DIR,
        ) as local_endpoint:
            local_predict_response = local_endpoint.predict(
                request=f'{{"instances": {_PREDICTION_INPUT}}}',
                headers={"Content-Type": "application/json"},
            )
        assert len(json.loads(local_predict_response.content)["predictions"]) == 1

        interactive_local_endpoint = local_model.deploy_to_local_endpoint(
            artifact_uri=_LOCAL_MODEL_DIR,
        )
        interactive_local_endpoint.serve()
        interactive_local_predict_response = interactive_local_endpoint.predict(
            request=f'{{"instances": {_PREDICTION_INPUT}}}',
            headers={"Content-Type": "application/json"},
        )
        interactive_local_endpoint.stop()
        assert (
            len(json.loads(interactive_local_predict_response.content)["predictions"])
            == 1
        )

        # Configure docker.
        logging.info(
            subprocess.run(["gcloud", "auth", "configure-docker"], capture_output=True)
        )

        local_model.push_image()

        model = models.Model.upload(
            local_model=local_model,
            display_name=f"cpr_e2e_test_{_TIMESTAMP}",
            artifact_uri=_ARTIFACT_URI,
            serving_container_deployment_timeout=3600,
            serving_container_shared_memory_size_mb=20,
        )
        shared_state["resources"] = [model]

        # Currently we need to explicitly specify machine type.
        # See https://github.com/googleapis/python-aiplatform/issues/773
        endpoint = model.deploy(machine_type="n1-standard-2")
        shared_state["resources"].append(endpoint)
        predict_response = endpoint.predict(instances=_PREDICTION_INPUT)
        assert len(predict_response.predictions) == 1

        caplog.clear()
