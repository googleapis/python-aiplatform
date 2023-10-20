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

import json
import pytest

from google.cloud import aiplatform

from tests.system.aiplatform import e2e_base

_PERMANENT_IRIS_ENDPOINT_ID = "4966625964059525120"
_PREDICTION_INSTANCE = {
    "petal_length": "3.0",
    "petal_width": "3.0",
    "sepal_length": "3.0",
    "sepal_width": "3.0",
}


class TestModelInteractions(e2e_base.TestEndToEnd):
    _temp_prefix = ""
    aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
    endpoint = aiplatform.Endpoint(_PERMANENT_IRIS_ENDPOINT_ID)

    def test_prediction(self):
        # test basic predict
        prediction_response = self.endpoint.predict(instances=[_PREDICTION_INSTANCE])
        assert len(prediction_response.predictions) == 1

        # test predict(use_raw_predict = True)
        prediction_with_raw_predict = self.endpoint.predict(
            instances=[_PREDICTION_INSTANCE], use_raw_predict=True
        )
        assert (
            prediction_with_raw_predict.deployed_model_id
            == prediction_response.deployed_model_id
        )
        assert (
            prediction_with_raw_predict.model_resource_name
            == prediction_response.model_resource_name
        )
        assert (
            prediction_with_raw_predict.model_version_id
            == prediction_response.model_version_id
        )

        # test raw_predict
        raw_prediction_response = self.endpoint.raw_predict(
            json.dumps({"instances": [_PREDICTION_INSTANCE]}),
            {"Content-Type": "application/json"},
        )
        assert raw_prediction_response.status_code == 200
        assert len(json.loads(raw_prediction_response.text)) == 1

    @pytest.mark.asyncio
    async def test_endpoint_predict_async(self):
        # Test the Endpoint.predict_async method.
        prediction_response = await self.endpoint.predict_async(
            instances=[_PREDICTION_INSTANCE]
        )
        assert len(prediction_response.predictions) == 1
