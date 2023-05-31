# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

from importlib import reload
import pytest
from unittest import mock

from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.compat.services import (
    prediction_service_client,
)

from google.cloud.aiplatform.compat.types import (
    prediction_service as gca_prediction_service,
)

import constants as test_constants

from google.cloud.aiplatform import prediction_service


_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION

_TEST_ID = test_constants.EndpointConstants._TEST_ID

_TEST_ENDPOINT_NAME = test_constants.EndpointConstants._TEST_ENDPOINT_NAME
_TEST_MODEL_NAME = test_constants.EndpointConstants._TEST_MODEL_NAME
_TEST_VERSION_ID = test_constants.EndpointConstants._TEST_VERSION_ID
_TEST_MODEL_ID = test_constants.EndpointConstants._TEST_MODEL_ID
_TEST_PREDICTION = test_constants.EndpointConstants._TEST_PREDICTION
_TEST_INSTANCES = [[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]]
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())


_TEST_EXPLANATIONS = [gca_prediction_service.explanation.Explanation(attributions=[])]

_TEST_ATTRIBUTIONS = [
    gca_prediction_service.explanation.Attribution(
        baseline_output_value=1.0,
        instance_output_value=2.0,
        feature_attributions=3.0,
        output_index=[1, 2, 3],
        output_display_name="abc",
        approximation_error=6.0,
        output_name="xyz",
    )
]


@pytest.fixture
def predict_client_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "predict"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.PredictResponse(
            deployed_model_id=_TEST_MODEL_ID,
            model_version_id=_TEST_VERSION_ID,
            model=_TEST_MODEL_NAME,
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        yield predict_mock


@pytest.fixture
def predict_client_explain_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "explain"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.ExplainResponse(
            deployed_model_id=_TEST_MODEL_ID,
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        predict_mock.return_value.explanations.extend(_TEST_EXPLANATIONS)
        predict_mock.return_value.explanations[0].attributions.extend(
            _TEST_ATTRIBUTIONS
        )
        yield predict_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestPredictor:
    """Tests for the prediction_service.Predictor class."""

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor(self):
        """Tests the Predictor constructor."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        predictor = prediction_service.Predictor(endpoint_name=_TEST_ENDPOINT_NAME)
        assert predictor.credentials == _TEST_CREDENTIALS

    def test_constructor_with_conflicting_project(self):
        """Tests the error when resource project conflicts with project."""
        with pytest.raises(ValueError) as err:
            prediction_service.Predictor(
                endpoint_name=_TEST_ENDPOINT_NAME, project="test-project-2"
            )

        assert err.match(regexp=r"is different from the resource project")

    def test_constructor_with_conflicting_location(self):
        """Tests the error when resource location conflicts with location."""
        with pytest.raises(ValueError) as err:
            prediction_service.Predictor(
                endpoint_name=_TEST_ENDPOINT_NAME, location="europe-west4"
            )

        assert err.match(regexp=r"is different from the resource location")

    def test_predict(self, predict_client_predict_mock):
        """Tests the Predictor.predict method."""
        test_endpoint = prediction_service.Predictor(_TEST_ENDPOINT_NAME)
        test_prediction = test_endpoint.predict(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            timeout=10.0,
        )

        true_prediction = prediction_service.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_ID,
            model_version_id=_TEST_VERSION_ID,
            model_resource_name=_TEST_MODEL_NAME,
        )

        assert true_prediction == test_prediction
        predict_client_predict_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            timeout=10.0,
        )

    def test_explain(self, predict_client_explain_mock):
        """Tests the Predictor.explain method."""

        test_endpoint = prediction_service.Predictor(_TEST_ENDPOINT_NAME)
        test_prediction = test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            timeout=10.0,
        )
        expected_explanations = _TEST_EXPLANATIONS
        expected_explanations[0].attributions.extend(_TEST_ATTRIBUTIONS)

        expected_prediction = prediction_service.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_ID,
            explanations=expected_explanations,
        )

        assert expected_prediction == test_prediction
        predict_client_explain_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            timeout=10.0,
        )
