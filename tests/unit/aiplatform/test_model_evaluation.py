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

import pytest

from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import models

from google.cloud.aiplatform.compat.services import (
    model_service_client,
)


from google.cloud.aiplatform.compat.types import model as gca_model

from google.cloud.aiplatform.compat.types import (
    model_evaluation as gca_model_evaluation,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_MODEL_NAME = "test-model"
_TEST_MODEL_ID = "1028944691210842416"
_TEST_EVAL_ID = "1028944691210842622"

_TEST_MODEL_RESOURCE_NAME = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT, _TEST_LOCATION, _TEST_MODEL_ID
)

_TEST_MODEL_EVAL_RESOURCE_NAME = (
    model_service_client.ModelServiceClient.model_evaluation_path(
        _TEST_PROJECT,
        _TEST_LOCATION,
        _TEST_MODEL_ID,
        _TEST_EVAL_ID,
    )
)

_TEST_MODEL_EVAL_METRICS = {
    "auPrc": 0.80592036,
    "auRoc": 0.8100363,
    "logLoss": 0.53061414,
    "confidenceMetrics": [
        {
            "confidenceThreshold": -0.01,
            "recall": 1.0,
            "precision": 0.5,
            "falsePositiveRate": 1.0,
            "f1Score": 0.6666667,
            "recallAt1": 1.0,
            "precisionAt1": 0.5,
            "falsePositiveRateAt1": 1.0,
            "f1ScoreAt1": 0.6666667,
            "truePositiveCount": "415",
            "falsePositiveCount": "415",
        },
        {
            "recall": 1.0,
            "precision": 0.5,
            "falsePositiveRate": 1.0,
            "f1Score": 0.6666667,
            "recallAt1": 0.74216866,
            "precisionAt1": 0.74216866,
            "falsePositiveRateAt1": 0.25783134,
            "f1ScoreAt1": 0.74216866,
            "truePositiveCount": "415",
            "falsePositiveCount": "415",
        },
    ],
}


@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
        )

        yield get_model_mock


@pytest.fixture
def mock_model():
    model = mock.MagicMock(models.Model)
    model.name = _TEST_MODEL_ID
    model._latest_future = None
    model._exception = None
    model._gca_resource = gca_model.Model(
        display_name="test-eval-model",
        description="This is the mock Model's description",
        name=_TEST_MODEL_NAME,
    )
    yield model


# ModelEvaluation mocks
@pytest.fixture
def mock_model_eval_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model_evaluation"
    ) as mock_get_model_eval:
        mock_get_model_eval.return_value = gca_model_evaluation.ModelEvaluation(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME,
            metrics=_TEST_MODEL_EVAL_METRICS,
        )
        yield mock_get_model_eval


@pytest.mark.usefixtures("google_auth_mock")
class TestModelEvaluation:
    def test_init_model_evaluation_with_only_resource_name(self, mock_model_eval_get):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.ModelEvaluation(evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME)

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_model_evaluation_with_eval_id_and_model_id(self, mock_model_eval_get):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.ModelEvaluation(
            evaluation_name=_TEST_EVAL_ID, model_id=_TEST_MODEL_ID
        )

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_model_evaluatin_with_id_project_and_location(
        self, mock_model_eval_get
    ):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        mock_model_eval_get.assert_called_once_with(
            name=_TEST_MODEL_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_model_evaluation_with_invalid_evaluation_resource_raises(
        self, mock_model_eval_get
    ):
        aiplatform.init(project=_TEST_PROJECT)

        with pytest.raises(ValueError):
            aiplatform.ModelEvaluation(evaluation_name=_TEST_MODEL_RESOURCE_NAME)

    def test_get_model_evaluation_metrics(self, mock_model_eval_get):
        aiplatform.init(project=_TEST_PROJECT)

        eval_metrics = aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME
        ).metrics
        assert eval_metrics == _TEST_MODEL_EVAL_METRICS

    def test_no_delete_model_evaluation_method(self, mock_model_eval_get):

        my_eval = aiplatform.ModelEvaluation(
            evaluation_name=_TEST_MODEL_EVAL_RESOURCE_NAME
        )

        with pytest.raises(NotImplementedError):
            my_eval.delete()
