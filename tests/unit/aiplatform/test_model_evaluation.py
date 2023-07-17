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
import pytest

from unittest import mock

from google.api_core import datetime_helpers

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

import constants as test_constants

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_MODEL_NAME = "test-model"
_TEST_MODEL_ID = test_constants.ModelConstants._TEST_ID
_TEST_EVAL_ID = "1028944691210842622"

_TEST_MODEL_RESOURCE_NAME = test_constants.ModelConstants._TEST_MODEL_RESOURCE_NAME

_TEST_MODEL_EVAL_RESOURCE_NAME = (
    model_service_client.ModelServiceClient.model_evaluation_path(
        _TEST_PROJECT,
        _TEST_LOCATION,
        _TEST_MODEL_ID,
        _TEST_EVAL_ID,
    )
)

_TEST_MODEL_EVAL_METRICS = test_constants.ModelConstants._TEST_MODEL_EVAL_METRICS


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


_TEST_MODEL_EVAL_LIST = [
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
        create_time=datetime_helpers.DatetimeWithNanoseconds(
            2023, 5, 14, 16, 24, 3, 299558, tzinfo=datetime.timezone.utc
        ),
    ),
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
        create_time=datetime_helpers.DatetimeWithNanoseconds(
            2023, 6, 14, 16, 24, 3, 299558, tzinfo=datetime.timezone.utc
        ),
    ),
    gca_model_evaluation.ModelEvaluation(
        name=_TEST_MODEL_EVAL_RESOURCE_NAME,
        create_time=datetime_helpers.DatetimeWithNanoseconds(
            2023, 7, 14, 16, 24, 3, 299558, tzinfo=datetime.timezone.utc
        ),
    ),
]


@pytest.fixture
def list_model_evaluations_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "list_model_evaluations"
    ) as list_model_evaluations_mock:
        list_model_evaluations_mock.return_value = _TEST_MODEL_EVAL_LIST
        yield list_model_evaluations_mock


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

    def test_list_model_evaluations(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        aiplatform.init(project=_TEST_PROJECT)

        metrics_list = aiplatform.ModelEvaluation.list(model=_TEST_MODEL_RESOURCE_NAME)

        assert isinstance(metrics_list[0], aiplatform.ModelEvaluation)

    def test_list_model_evaluations_with_order_by(
        self,
        mock_model_eval_get,
        get_model_mock,
        list_model_evaluations_mock,
    ):
        aiplatform.init(project=_TEST_PROJECT)

        metrics_list = aiplatform.ModelEvaluation.list(
            model=_TEST_MODEL_RESOURCE_NAME, order_by="create_time desc"
        )

        assert metrics_list[0].create_time > metrics_list[1].create_time
