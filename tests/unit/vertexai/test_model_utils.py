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
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import utils
import vertexai
from vertexai.preview._workflow.serialization_engine import (
    any_serializer,
)
import pytest

from sklearn.linear_model import _logistic
import tensorflow
import torch


# project constants
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_BUCKET = "gs://test-bucket"
_TEST_UNIQUE_NAME = "test-unique-name"


# framework-specific constants
_SKLEARN_MODEL = _logistic.LogisticRegression()
_TF_MODEL = tensorflow.keras.models.Model()
_PYTORCH_MODEL = torch.nn.Module()
_TEST_MODEL_GCS_URI = "gs://test_model_dir"
_MODEL_RESOURCE_NAME = "projects/123/locations/us-central1/models/456"
_REWRAPPER = "rewrapper"


@pytest.fixture
def mock_serialize_model():
    with mock.patch.object(
        any_serializer.AnySerializer, "serialize"
    ) as mock_serialize_model:
        yield mock_serialize_model


@pytest.fixture
def mock_vertex_model():
    model = mock.MagicMock(aiplatform.Model)
    model.uri = _TEST_MODEL_GCS_URI
    model.container_spec.image_uri = "us-docker.xxx/sklearn-cpu.1-0:latest"
    model.labels = {"registered_by_vertex_ai": "true"}
    yield model


@pytest.fixture
def mock_vertex_model_invalid():
    model = mock.MagicMock(aiplatform.Model)
    model.uri = _TEST_MODEL_GCS_URI
    model.container_spec.image_uri = "us-docker.xxx/sklearn-cpu.1-0:latest"
    yield model


@pytest.fixture
def mock_timestamped_unique_name():
    with mock.patch.object(
        utils, "timestamped_unique_name"
    ) as mock_timestamped_unique_name:
        mock_timestamped_unique_name.return_value = _TEST_UNIQUE_NAME
        yield mock_timestamped_unique_name


@pytest.fixture
def mock_model_upload(mock_vertex_model):
    with mock.patch.object(aiplatform.Model, "upload") as mock_model_upload:
        mock_model_upload.return_value = mock_vertex_model
        yield mock_model_upload


@pytest.fixture
def mock_get_vertex_model(mock_vertex_model):
    with mock.patch.object(aiplatform, "Model") as mock_get_vertex_model:
        mock_get_vertex_model.return_value = mock_vertex_model
        yield mock_get_vertex_model


@pytest.fixture
def mock_get_vertex_model_invalid(mock_vertex_model_invalid):
    with mock.patch.object(aiplatform, "Model") as mock_get_vertex_model:
        mock_get_vertex_model.return_value = mock_vertex_model_invalid
        yield mock_get_vertex_model


@pytest.fixture
def mock_deserialize_model():
    with mock.patch.object(
        any_serializer.AnySerializer, "deserialize"
    ) as mock_deserialize_model:

        mock_deserialize_model.side_effect = [
            _SKLEARN_MODEL,
            mock.Mock(return_value=None),
        ]
        yield mock_deserialize_model


@pytest.fixture
def mock_deserialize_model_exception():
    with mock.patch.object(
        any_serializer.AnySerializer, "deserialize"
    ) as mock_deserialize_model_exception:
        mock_deserialize_model_exception.side_effect = Exception
        yield mock_deserialize_model_exception


@pytest.mark.usefixtures("google_auth_mock")
class TestModelUtils:
    def setup_method(self):
        reload(aiplatform)
        reload(vertexai)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("mock_timestamped_unique_name")
    def test_register_sklearn_model(self, mock_model_upload, mock_serialize_model):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )
        vertex_model = vertexai.preview.register(_SKLEARN_MODEL)

        expected_display_name = (
            f"vertex-ai-registered-sklearn-model-{_TEST_UNIQUE_NAME}"
        )
        expected_uri = f"{_TEST_BUCKET}/{expected_display_name}"
        expected_container_uri = (
            aiplatform.helpers.get_prebuilt_prediction_container_uri(
                framework="sklearn",
                framework_version="1.0",
            )
        )

        assert vertex_model.uri == _TEST_MODEL_GCS_URI
        mock_model_upload.assert_called_once_with(
            display_name=expected_display_name,
            artifact_uri=expected_uri,
            serving_container_image_uri=expected_container_uri,
            labels={"registered_by_vertex_ai": "true"},
            sync=True,
        )
        assert 2 == mock_serialize_model.call_count
        mock_serialize_model.assert_has_calls(
            calls=[
                mock.call(
                    _SKLEARN_MODEL,
                    f"{expected_uri}/model.pkl",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.parametrize("use_gpu", [True, False])
    @pytest.mark.usefixtures("mock_timestamped_unique_name")
    def test_register_tf_model(self, mock_model_upload, mock_serialize_model, use_gpu):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )
        vertex_model = vertexai.preview.register(_TF_MODEL, use_gpu=use_gpu)

        expected_display_name = (
            f"vertex-ai-registered-tensorflow-model-{_TEST_UNIQUE_NAME}"
        )
        expected_uri = f"{_TEST_BUCKET}/{expected_display_name}/saved_model"
        expected_container_uri = (
            aiplatform.helpers.get_prebuilt_prediction_container_uri(
                framework="tensorflow",
                framework_version="2.11",
                accelerator="gpu" if use_gpu else "cpu",
            )
        )

        assert vertex_model.uri == _TEST_MODEL_GCS_URI
        mock_model_upload.assert_called_once_with(
            display_name=expected_display_name,
            artifact_uri=expected_uri,
            serving_container_image_uri=expected_container_uri,
            labels={"registered_by_vertex_ai": "true"},
            sync=True,
        )
        assert 2 == mock_serialize_model.call_count
        mock_serialize_model.assert_has_calls(
            calls=[
                mock.call(
                    _TF_MODEL,
                    f"{expected_uri}",
                    save_format="tf",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.parametrize("use_gpu", [True, False])
    @pytest.mark.usefixtures("mock_timestamped_unique_name")
    def test_register_pytorch_model(
        self, mock_model_upload, mock_serialize_model, use_gpu
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )
        vertex_model = vertexai.preview.register(_PYTORCH_MODEL, use_gpu=use_gpu)

        expected_display_name = (
            f"vertex-ai-registered-pytorch-model-{_TEST_UNIQUE_NAME}"
        )
        expected_uri = f"{_TEST_BUCKET}/{expected_display_name}"
        expected_container_uri = (
            aiplatform.helpers.get_prebuilt_prediction_container_uri(
                framework="pytorch",
                framework_version="1.12",
                accelerator="gpu" if use_gpu else "cpu",
            )
        )

        assert vertex_model.uri == _TEST_MODEL_GCS_URI
        mock_model_upload.assert_called_once_with(
            display_name=expected_display_name,
            artifact_uri=expected_uri,
            serving_container_image_uri=expected_container_uri,
            labels={"registered_by_vertex_ai": "true"},
            sync=True,
        )

        assert 2 == mock_serialize_model.call_count
        mock_serialize_model.assert_has_calls(
            calls=[
                mock.call(
                    _PYTORCH_MODEL,
                    f"{expected_uri}/model.mar",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("mock_get_vertex_model")
    def test_local_model_from_pretrained_succeed(self, mock_deserialize_model):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        local_model = vertexai.preview.from_pretrained(model_name=_MODEL_RESOURCE_NAME)
        assert local_model == _SKLEARN_MODEL
        assert 2 == mock_deserialize_model.call_count
        mock_deserialize_model.assert_has_calls(
            calls=[
                mock.call(
                    f"{_TEST_MODEL_GCS_URI}/model.pkl",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures(
        "mock_get_vertex_model_invalid",
    )
    def test_local_model_from_pretrained_fail(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        with pytest.raises(ValueError):
            vertexai.preview.from_pretrained(model_name=_MODEL_RESOURCE_NAME)
