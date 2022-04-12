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

from multiprocessing.sharedctypes import Value
from google.cloud.aiplatform import model_evaluation
import yaml
import datetime
import os
from typing import Type
import pytest
import json

from unittest import mock
from unittest.mock import patch
from importlib import reload

from google.api_core import operation
from google.protobuf import json_format
from google.cloud import storage

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import models
from google.cloud.aiplatform import pipeline_jobs

from google.cloud.aiplatform.model_evaluation import ModelEvaluation

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)



from google.cloud.aiplatform.compat.types import model as gca_model

from google.cloud.aiplatform_v1.types import (
    model_evaluation as gca_model_evaluation,
)

# pipeline job
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PIPELINE_JOB_ID = "sample-test-pipeline-202111111"

_TEST_ID = "1028944691210842416"

_TEST_MODEL_RESOURCE_NAME = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
)

_TEST_MODEL_NAME = "test-model"

_TEST_EVAL_RESOURCE_NAME = f"projects/{_TEST_ID}/locations/{_TEST_LOCATION}/models/{_TEST_ID}/evaluations/{_TEST_ID}"


@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME, name=_TEST_MODEL_RESOURCE_NAME,
        )

        yield get_model_mock


@pytest.fixture
def mock_model():
    model = mock.MagicMock(models.Model)
    model.name = _TEST_ID
    # model.resource_name = _TEST_MODEL_RESOURCE_NAME,
    model._latest_future = None
    model._exception = None
    model._gca_resource = gca_model.Model(
        display_name="test-eval-model",
        description="This is the mock Model's description",
        name=_TEST_MODEL_NAME,
    )
    yield model


# Mocks specific to ModelEvaluation


@pytest.fixture
def mock_model_eval_get():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model_evaluation"
    ) as mock_get_model_eval:
        mock_get_model_eval.return_value = gca_model_evaluation.ModelEvaluation(
            name=_TEST_EVAL_RESOURCE_NAME
        )
        yield mock_get_model_eval


class TestModelEvaluation:
    def test_init_model_evaluation(self, mock_model_eval_get):
        aiplatform.init(project=_TEST_PROJECT)

        aiplatform.ModelEvaluation(
            evaluation_name=_TEST_EVAL_RESOURCE_NAME
        )

        mock_model_eval_get.assert_called_once_with(
            name=_TEST_EVAL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    # TODO: test_init_model_evaluation_with_invalid_evaluation_resource_raises
