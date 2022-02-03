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

import importlib
import pytest
import textwrap
from unittest import mock

from google.cloud.aiplatform import helpers
from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.prediction import DEFAULT_HEALTH_ROUTE
from google.cloud.aiplatform.prediction import DEFAULT_HTTP_PORT
from google.cloud.aiplatform.prediction import DEFAULT_PREDICT_ROUTE
from google.cloud.aiplatform.prediction import LocalModel
from google.cloud.aiplatform.utils import prediction_utils

_DEFAULT_BASE_IMAGE = "python:3.7"
_ENTRYPOINT_FILE = "entrypoint.py"
_TEST_SRC_DIR = "user_code"
_TEST_PREDICTOR_FILE = "predictor.py"
_TEST_OUTPUT_IMAGE = "cpr_image:latest"


@pytest.fixture
def populate_entrypoint_if_not_exists_mock():
    with mock.patch.object(
        prediction_utils, "populate_entrypoint_if_not_exists"
    ) as populate_entrypoint_if_not_exists_mock:
        yield populate_entrypoint_if_not_exists_mock


@pytest.fixture
def is_prebuilt_prediction_container_uri_is_true_mock():
    with mock.patch.object(
        helpers, "is_prebuilt_prediction_container_uri"
    ) as is_prebuilt_prediction_container_uri_is_true_mock:
        is_prebuilt_prediction_container_uri_is_false_mock.return_value = True
        yield is_prebuilt_prediction_container_uri_is_true_mock


@pytest.fixture
def is_prebuilt_prediction_container_uri_is_false_mock():
    with mock.patch.object(
        helpers, "is_prebuilt_prediction_container_uri"
    ) as is_prebuilt_prediction_container_uri_is_false_mock:
        is_prebuilt_prediction_container_uri_is_false_mock.return_value = False
        yield is_prebuilt_prediction_container_uri_is_false_mock


@pytest.fixture
def build_image_mock():
    with mock.patch.object(build, "build_image") as build_image_mock:
        build_image_mock.return_value = None
        yield build_image_mock


class TestLocalModel:
    def _load_module(self, name, location):
        spec = importlib.util.spec_from_file_location(name, location)
        return importlib.util.module_from_spec(spec)

    def test_create_cpr_model_creates_and_get_localmodel(
        self,
        tmp_path,
        populate_entrypoint_if_not_exists_mock,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor:
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))
        entrypoint = f"{_TEST_SRC_DIR}/{_ENTRYPOINT_FILE}"

        local_model = LocalModel.create_cpr_model(
            _TEST_SRC_DIR, _TEST_OUTPUT_IMAGE, predictor=my_predictor,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE

        populate_entrypoint_if_not_exists_mock.assert_called_once_with(
            _TEST_SRC_DIR, _ENTRYPOINT_FILE, predictor=my_predictor, handler=None
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            _TEST_SRC_DIR,
            entrypoint,
            _TEST_OUTPUT_IMAGE,
            requirements_path=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            pip_command="pip",
            python_command="python",
        )

    def test_create_cpr_model_creates_and_get_localmodel_base_is_prebuilt(
        self,
        tmp_path,
        populate_entrypoint_if_not_exists_mock,
        is_prebuilt_prediction_container_uri_is_true_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor:
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))
        entrypoint = f"{_TEST_SRC_DIR}/{_ENTRYPOINT_FILE}"

        local_model = LocalModel.create_cpr_model(
            _TEST_SRC_DIR, _TEST_OUTPUT_IMAGE, predictor=my_predictor,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE

        populate_entrypoint_if_not_exists_mock.assert_called_once_with(
            _TEST_SRC_DIR, _ENTRYPOINT_FILE, predictor=my_predictor, handler=None
        )
        is_prebuilt_prediction_container_uri_is_true_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            _TEST_SRC_DIR,
            entrypoint,
            _TEST_OUTPUT_IMAGE,
            requirements_path=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            pip_command="pip3",
            python_command="python3",
        )

    def test_create_cpr_model_creates_and_get_localmodel_with_requirements_path(
        self,
        tmp_path,
        populate_entrypoint_if_not_exists_mock,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class MyPredictor:
                pass
            """
            )
        )
        my_predictor = self._load_module("MyPredictor", str(predictor))
        entrypoint = f"{_TEST_SRC_DIR}/{_ENTRYPOINT_FILE}"
        requirements_path = f"{_TEST_SRC_DIR}/requirements.txt"

        local_model = LocalModel.create_cpr_model(
            _TEST_SRC_DIR,
            _TEST_OUTPUT_IMAGE,
            predictor=my_predictor,
            requirements_path=requirements_path,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE

        populate_entrypoint_if_not_exists_mock.assert_called_once_with(
            _TEST_SRC_DIR, _ENTRYPOINT_FILE, predictor=my_predictor, handler=None
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            _TEST_SRC_DIR,
            entrypoint,
            _TEST_OUTPUT_IMAGE,
            requirements_path=requirements_path,
            exposed_ports=[DEFAULT_HTTP_PORT],
            pip_command="pip",
            python_command="python",
        )
