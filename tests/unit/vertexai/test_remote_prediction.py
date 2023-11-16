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
import inspect
from unittest.mock import patch

from google.cloud import aiplatform
import vertexai
from vertexai.preview._workflow.executor import prediction
from vertexai.preview._workflow.executor import training
from vertexai.preview._workflow.shared import configs

import pytest
from sklearn.datasets import load_iris
from sklearn.linear_model import _logistic
from sklearn.model_selection import train_test_split


# vertexai constants
_TEST_PROJECT = "test-project"
_TEST_PROJECT_NUMBER = 123
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_BUCKET_NAME = "gs://test-bucket"

# dataset constants
dataset = load_iris()
_X_TRAIN, _X_TEST, _Y_TRAIN, _Y_TEST = train_test_split(
    dataset.data, dataset.target, test_size=0.2, random_state=42
)

# config constants
_TEST_CONTAINER_URI = "gcr.io/custom-image"
_TEST_DISPLAY_NAME = "test-display-name"


@pytest.fixture
def mock_remote_training():
    with patch.object(training, "remote_training") as mock_remote_training:
        mock_remote_training.return_value = _Y_TEST
        yield mock_remote_training


@pytest.mark.usefixtures("google_auth_mock")
class TestRemotePrediction:
    def setup_method(self):
        reload(vertexai)
        reload(vertexai.preview.initializer)
        reload(_logistic)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    def test_remote_prediction_sklearn(self, mock_remote_training):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.predict.vertex.remote = True
        model.predict.vertex.remote_config.staging_bucket = _TEST_BUCKET_NAME

        model.predict(_X_TEST)

        invokable = mock_remote_training.call_args[1]["invokable"]
        assert invokable.method == model.predict._method
        assert invokable.bound_arguments == (
            inspect.signature(model.predict._method).bind(_X_TEST)
        )

        assert invokable.vertex_config.remote is True

        assert invokable.vertex_config.remote_config.display_name is None
        assert invokable.vertex_config.remote_config.staging_bucket == _TEST_BUCKET_NAME
        assert invokable.vertex_config.remote_config.container_uri is None
        assert invokable.vertex_config.remote_config.machine_type is None
        assert invokable.vertex_config.remote_config.service_account is None

        assert invokable.remote_executor == prediction.remote_prediction
        assert invokable.remote_executor_kwargs == {}
        assert invokable.instance == model

    def test_remote_prediction_with_set_config(self, mock_remote_training):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.predict.vertex.remote = True

        model.predict.vertex.set_config(
            staging_bucket=_TEST_BUCKET_NAME, display_name=_TEST_DISPLAY_NAME
        )

        model.predict(_X_TEST)

        invokable = mock_remote_training.call_args[1]["invokable"]

        assert invokable.method == model.predict._method
        assert invokable.bound_arguments == (
            inspect.signature(model.predict._method).bind(_X_TEST)
        )

        assert invokable.vertex_config.remote is True
        assert isinstance(invokable.vertex_config.remote_config, configs.RemoteConfig)

        assert invokable.vertex_config.remote_config.display_name == _TEST_DISPLAY_NAME
        assert invokable.vertex_config.remote_config.staging_bucket == _TEST_BUCKET_NAME
        assert invokable.vertex_config.remote_config.container_uri is None
        assert invokable.vertex_config.remote_config.machine_type is None
        assert invokable.vertex_config.remote_config.service_account is None

        assert invokable.remote_executor == prediction.remote_prediction
        assert invokable.remote_executor_kwargs == {}
        assert invokable.instance == model
