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

import asyncio
import importlib
import json
import multiprocessing
import os
import pytest
import requests
import textwrap
import time
from unittest import mock

from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from starlette.datastructures import Headers
from starlette.testclient import TestClient

from google.auth.exceptions import GoogleAuthError

from google.cloud import aiplatform
from google.cloud.aiplatform import helpers
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models

from google.cloud.aiplatform.compat.types import (
    model as gca_model_compat,
    env_var as gca_env_var,
)

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.docker_utils import errors
from google.cloud.aiplatform.docker_utils import local_util
from google.cloud.aiplatform.docker_utils import run
from google.cloud.aiplatform.docker_utils import utils
from google.cloud.aiplatform.prediction import DEFAULT_HEALTH_ROUTE
from google.cloud.aiplatform.prediction import DEFAULT_HTTP_PORT
from google.cloud.aiplatform.prediction import DEFAULT_PREDICT_ROUTE
from google.cloud.aiplatform.prediction import LocalModel
from google.cloud.aiplatform.prediction import LocalEndpoint
from google.cloud.aiplatform.prediction import handler_utils
from google.cloud.aiplatform.prediction import local_endpoint
from google.cloud.aiplatform.prediction import (
    model_server as model_server_module,
)
from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.model_server import CprModelServer
from google.cloud.aiplatform.prediction.local_model import (
    _DEFAULT_HANDLER_CLASS,
)
from google.cloud.aiplatform.prediction.local_model import (
    _DEFAULT_HANDLER_MODULE,
)
from google.cloud.aiplatform.prediction.local_model import (
    _DEFAULT_PYTHON_MODULE,
)
from google.cloud.aiplatform.prediction.local_model import (
    _DEFAULT_SDK_REQUIREMENTS,
)
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.prediction.serializer import DefaultSerializer
from google.cloud.aiplatform.utils import prediction_utils

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)


_TEST_INPUT = b'{"instances": [[1, 2, 3, 4]]}'
_TEST_DESERIALIZED_INPUT = {"instances": [[1, 2, 3, 4]]}
_TEST_PREDICTION_OUTPUT = {"predictions": [[1]]}
_TEST_SERIALIZED_OUTPUT = b'{"predictions": [[1]]}'
_APPLICATION_JSON = "application/json"
_TEST_GCS_ARTIFACTS_URI = ""

_TEST_AIP_HTTP_PORT = "8080"
_TEST_AIP_HEALTH_ROUTE = "/health"
_TEST_AIP_PREDICT_ROUTE = "/predict"
_TEST_AIP_STORAGE_URI = "gs://fake/storage/uri"

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_MODEL_NAME = "test-model"
_TEST_ARTIFACT_URI = "gs://test/artifact/uri"
_TEST_SERVING_CONTAINER_IMAGE = "gcr.io/test-serving/container:image"
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = "health"
_TEST_DESCRIPTION = "test description"
_TEST_SERVING_CONTAINER_COMMAND = ["python3", "run_my_model.py"]
_TEST_SERVING_CONTAINER_ARGS = ["--test", "arg"]
_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES = {
    "learning_rate": 0.01,
    "loss_fn": "mse",
}
_TEST_SERVING_CONTAINER_PORTS = [8888, 10000]
_TEST_SERVING_CONTAINER_GRPC_PORTS = [7777, 7000]
_TEST_ID = "1028944691210842416"
_TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}
_TEST_APPENDED_USER_AGENT = ["fake_user_agent"]

_TEST_INSTANCE_SCHEMA_URI = "gs://test/schema/instance.yaml"
_TEST_PARAMETERS_SCHEMA_URI = "gs://test/schema/parameters.yaml"
_TEST_PREDICTION_SCHEMA_URI = "gs://test/schema/predictions.yaml"

_TEST_EXPLANATION_METADATA = aiplatform.explain.ExplanationMetadata(
    inputs={
        "features": {
            "input_tensor_name": "dense_input",
            "encoding": "BAG_OF_FEATURES",
            "modality": "numeric",
            "index_feature_mapping": ["abc", "def", "ghj"],
        }
    },
    outputs={"medv": {"output_tensor_name": "dense_2"}},
)
_TEST_EXPLANATION_PARAMETERS = aiplatform.explain.ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 10}}
)

_TEST_MODEL_RESOURCE_NAME = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
)

_TEST_IMAGE_URI = "test_image:latest"

_DEFAULT_BASE_IMAGE = "python:3.10"
_MODEL_SERVER_FILE = "cpr_model_server.py"
_TEST_SRC_DIR = "user_code"
_TEST_PREDICTOR_FILE = "predictor.py"
_TEST_PREDICTOR_FILE_STEM = "predictor"
_TEST_PREDICTOR_CLASS = "MyPredictor"
_TEST_HANDLER_FILE = "hanlder.py"
_TEST_HANDLER_FILE_STEM = "hanlder"
_TEST_HANDLER_CLASS = "MyHandler"
_TEST_OUTPUT_IMAGE = "cpr_image:latest"

_TEST_PREDICT_RESPONSE_CONTENT = b'{"x": [[1]]}'
_TEST_HEALTH_CHECK_RESPONSE_CONTENT = b"{}"
_TEST_HTTP_ERROR_MESSAGE = "HTTP Error Occurred."
_TEST_CONTAINER_LOGS_LEN = 5
_CONTAINER_RUNNING_STATUS = "running"
_CONTAINER_EXITED_STATUS = "exited"

_TEST_GPU_COUNT = 1
_TEST_GPU_DEVICE_IDS = ["1"]
_TEST_GPU_CAPABILITIES = [["gpu"]]
_TEST_MULTIPROCESSING_CPU_COUNT = 16
_DEFAULT_WORKERS_PER_CORE = 1


@pytest.fixture
def deserialize_mock():
    with mock.patch.object(DefaultSerializer, "deserialize") as deserialize_mock:
        deserialize_mock.return_value = _TEST_DESERIALIZED_INPUT
        yield deserialize_mock


@pytest.fixture
def deserialize_exception_mock():
    with mock.patch.object(
        DefaultSerializer, "deserialize"
    ) as deserialize_exception_mock:
        deserialize_exception_mock.side_effect = HTTPException(
            status_code=400,
        )
        yield deserialize_exception_mock


@pytest.fixture
def serialize_mock():
    with mock.patch.object(DefaultSerializer, "serialize") as serialize_mock:
        serialize_mock.return_value = _TEST_SERIALIZED_OUTPUT
        yield serialize_mock


@pytest.fixture
def serialize_exception_mock():
    with mock.patch.object(DefaultSerializer, "serialize") as serialize_exception_mock:
        serialize_exception_mock.side_effect = HTTPException(
            status_code=400,
        )
        yield serialize_exception_mock


@pytest.fixture
def predictor_mock():
    with mock.patch(
        "google.cloud.aiplatform.prediction.predictor.Predictor"
    ) as MockPredictor:
        instance = MockPredictor.return_value
        instance().preprocess.return_value = _TEST_DESERIALIZED_INPUT
        instance().predict.return_value = _TEST_PREDICTION_OUTPUT
        instance().postprocess.return_value = _TEST_SERIALIZED_OUTPUT
        yield instance


@pytest.fixture
def model_server_env_mock():
    env_vars = {
        "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
        "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
        "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
        "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
        "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
        "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
        "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
        "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
    }
    with mock.patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def cpu_count_mock():
    with mock.patch.object(multiprocessing, "cpu_count") as cpu_count_mock:
        cpu_count_mock.return_value = _TEST_MULTIPROCESSING_CPU_COUNT
        yield cpu_count_mock


def get_test_headers():
    return Headers({"content-type": _APPLICATION_JSON, "accept": _APPLICATION_JSON})


def get_test_request():
    async def _create_request_receive():
        return {
            "type": "http.request",
            "body": _TEST_INPUT,
            "more_body": False,
        }

    return Request(
        scope={"type": "http", "headers": get_test_headers().raw},
        receive=_create_request_receive,
    )


@pytest.fixture
def get_content_type_from_headers_mock():
    with mock.patch.object(
        handler_utils, "get_content_type_from_headers"
    ) as get_content_type_from_headers_mock:
        get_content_type_from_headers_mock.return_value = _APPLICATION_JSON
        yield get_content_type_from_headers_mock


@pytest.fixture
def get_accept_from_headers_mock():
    with mock.patch.object(
        handler_utils, "get_accept_from_headers"
    ) as get_accept_from_headers_mock:
        get_accept_from_headers_mock.return_value = _APPLICATION_JSON
        yield get_accept_from_headers_mock


def get_test_predictor():
    class _TestPredictor(Predictor):
        def __init__(self):
            pass

        def load(self, artifacts_uri):
            pass

        def predict(self, instances):
            pass

    return _TestPredictor


@pytest.fixture
def populate_model_server_if_not_exists_mock():
    with mock.patch.object(
        prediction_utils, "populate_model_server_if_not_exists"
    ) as populate_model_server_if_not_exists_mock:
        yield populate_model_server_if_not_exists_mock


@pytest.fixture
def populate_entrypoint_if_not_exists_mock():
    with mock.patch.object(
        prediction_utils, "populate_entrypoint_if_not_exists"
    ) as populate_entrypoint_if_not_exists_mock:
        yield populate_entrypoint_if_not_exists_mock


@pytest.fixture
def inspect_source_from_class_mock_predictor_only():
    with mock.patch.object(
        prediction_utils, "inspect_source_from_class"
    ) as inspect_source_from_class_mock_predictor_only:
        inspect_source_from_class_mock_predictor_only.return_value = (
            f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
            _TEST_PREDICTOR_CLASS,
        )
        yield inspect_source_from_class_mock_predictor_only


@pytest.fixture
def inspect_source_from_class_mock_handler_only():
    with mock.patch.object(
        prediction_utils, "inspect_source_from_class"
    ) as inspect_source_from_class_mock_handler_only:
        inspect_source_from_class_mock_handler_only.return_value = (
            f"{_TEST_SRC_DIR}.{_TEST_HANDLER_FILE_STEM}",
            _TEST_HANDLER_CLASS,
        )
        yield inspect_source_from_class_mock_handler_only


@pytest.fixture
def inspect_source_from_class_mock_predictor_and_handler():
    with mock.patch.object(
        prediction_utils, "inspect_source_from_class"
    ) as inspect_source_from_class_mock_predictor_and_handler:
        inspect_source_from_class_mock_predictor_and_handler.side_effect = [
            (f"{_TEST_SRC_DIR}.{_TEST_HANDLER_FILE_STEM}", _TEST_HANDLER_CLASS),
            (f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}", _TEST_PREDICTOR_CLASS),
        ]
        yield inspect_source_from_class_mock_predictor_and_handler


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


@pytest.fixture
def local_endpoint_logger_mock():
    with mock.patch(
        "google.cloud.aiplatform.prediction.local_endpoint._logger"
    ) as local_endpoint_logger_mock:
        yield local_endpoint_logger_mock


@pytest.fixture
def local_endpoint_init_mock():
    with mock.patch.object(LocalEndpoint, "__init__") as local_endpoint_init_mock:
        local_endpoint_init_mock.return_value = None
        yield local_endpoint_init_mock


@pytest.fixture
def local_endpoint_enter_mock():
    with mock.patch.object(LocalEndpoint, "__enter__") as local_endpoint_enter_mock:
        yield local_endpoint_enter_mock


@pytest.fixture
def local_endpoint_exit_mock():
    with mock.patch.object(LocalEndpoint, "__exit__") as local_endpoint_exit_mock:
        yield local_endpoint_exit_mock


@pytest.fixture
def local_endpoint_del_mock():
    with mock.patch.object(LocalEndpoint, "__del__") as local_endpoint_del_mock:
        yield local_endpoint_del_mock


@pytest.fixture
def local_endpoint_run_health_check_mock():
    with mock.patch.object(
        LocalEndpoint, "run_health_check"
    ) as local_endpoint_run_health_check_mock:
        local_endpoint_run_health_check_mock.return_value.status_code = 200
        yield local_endpoint_run_health_check_mock


@pytest.fixture
def local_endpoint_run_health_check_raise_exception_mock():
    with mock.patch.object(
        LocalEndpoint, "run_health_check"
    ) as local_endpoint_run_health_check_raise_exception_mock:
        local_endpoint_run_health_check_raise_exception_mock.side_effect = (
            requests.exceptions.RequestException()
        )
        yield local_endpoint_run_health_check_raise_exception_mock


@pytest.fixture
def time_sleep_mock():
    with mock.patch.object(time, "sleep") as time_sleep_mock:
        yield time_sleep_mock


@pytest.fixture
def initializer_mock():
    global_config = initializer.global_config
    type(global_config).project = mock.PropertyMock(return_value=_TEST_PROJECT)


@pytest.fixture
def initializer_project_none_mock():
    global_config = initializer.global_config
    type(global_config).project = mock.PropertyMock(side_effect=GoogleAuthError)


def get_docker_container_mock():
    container = mock.MagicMock()
    return container


@pytest.fixture
def run_prediction_container_mock():
    with mock.patch.object(
        run, "run_prediction_container"
    ) as run_prediction_container_mock:
        run_prediction_container_mock.return_value = get_docker_container_mock()
        run_prediction_container_mock.return_value.status = run.CONTAINER_RUNNING_STATUS
        yield run_prediction_container_mock


@pytest.fixture
def run_prediction_container_container_not_running_mock():
    with mock.patch.object(
        run, "run_prediction_container"
    ) as run_prediction_container_container_not_running_mock:
        run_prediction_container_container_not_running_mock.return_value = (
            get_docker_container_mock()
        )
        run_prediction_container_container_not_running_mock.return_value.status = (
            "NOT_RUNNING"
        )
        yield run_prediction_container_container_not_running_mock


@pytest.fixture
def run_print_container_logs_mock():
    with mock.patch.object(
        run, "print_container_logs"
    ) as run_print_container_logs_mock:
        run_print_container_logs_mock.return_value = _TEST_CONTAINER_LOGS_LEN
        yield run_print_container_logs_mock


@pytest.fixture
def check_image_exists_locally_true_mock():
    with mock.patch.object(
        utils, "check_image_exists_locally"
    ) as check_image_exists_locally_true_mock:
        check_image_exists_locally_true_mock.return_value = True
        yield check_image_exists_locally_true_mock


@pytest.fixture
def check_image_exists_locally_false_mock():
    with mock.patch.object(
        utils, "check_image_exists_locally"
    ) as check_image_exists_locally_false_mock:
        check_image_exists_locally_false_mock.return_value = False
        yield check_image_exists_locally_false_mock


@pytest.fixture
def get_container_status_running_mock():
    with mock.patch.object(
        LocalEndpoint, "get_container_status"
    ) as get_container_status_running_mock:
        get_container_status_running_mock.return_value = _CONTAINER_RUNNING_STATUS
        yield get_container_status_running_mock


@pytest.fixture
def get_container_status_second_fail_mock():
    with mock.patch.object(
        LocalEndpoint, "get_container_status"
    ) as get_container_status_second_fail_mock:
        get_container_status_second_fail_mock.side_effect = [
            _CONTAINER_RUNNING_STATUS,
            _CONTAINER_EXITED_STATUS,
        ]
        yield get_container_status_second_fail_mock


@pytest.fixture
def local_endpoint_print_container_logs_mock():
    with mock.patch.object(
        LocalEndpoint, "print_container_logs"
    ) as local_endpoint_print_container_logs_mock:
        yield local_endpoint_print_container_logs_mock


@pytest.fixture
def pull_image_if_not_exists_mock():
    with mock.patch.object(
        LocalModel, "pull_image_if_not_exists"
    ) as pull_image_if_not_exists_mock:
        yield pull_image_if_not_exists_mock


def get_requests_post_response():
    response = requests.models.Response()
    response.status_code = 200
    response._content = _TEST_PREDICT_RESPONSE_CONTENT
    return response


@pytest.fixture
def requests_post_mock():
    with mock.patch.object(requests, "post") as requests_post_mock:
        requests_post_mock.return_value = get_requests_post_response()
        yield requests_post_mock


@pytest.fixture
def requests_post_raises_exception_mock():
    with mock.patch.object(requests, "post") as requests_post_raises_exception_mock:
        requests_post_raises_exception_mock.side_effect = requests.exceptions.HTTPError(
            _TEST_HTTP_ERROR_MESSAGE
        )
        yield requests_post_raises_exception_mock


@pytest.fixture
def open_file_mock():
    with mock.patch("builtins.open") as open_file_mock:
        yield open_file_mock().__enter__()


def get_requests_get_response():
    response = requests.models.Response()
    response.status_code = 200
    response._content = _TEST_HEALTH_CHECK_RESPONSE_CONTENT
    return response


@pytest.fixture
def requests_get_mock():
    with mock.patch.object(requests, "get") as requests_get_mock:
        requests_get_mock.return_value = get_requests_get_response()
        yield requests_get_mock


@pytest.fixture
def requests_get_second_raises_exception_mock():
    with mock.patch.object(
        requests, "get"
    ) as requests_get_second_raises_exception_mock:
        requests_get_second_raises_exception_mock.side_effect = [
            get_requests_get_response(),
            requests.exceptions.HTTPError(_TEST_HTTP_ERROR_MESSAGE),
        ]
        yield requests_get_second_raises_exception_mock


@pytest.fixture
def upload_model_mock():
    with mock.patch.object(models.Model, "upload") as upload_model_mock:
        yield upload_model_mock


@pytest.fixture
def execute_command_mock():
    with mock.patch.object(local_util, "execute_command") as execute_command_mock:
        execute_command_mock.return_value = 0
        yield execute_command_mock


@pytest.fixture
def execute_command_return_code_1_mock():
    with mock.patch.object(
        local_util, "execute_command"
    ) as execute_command_return_code_1_mock:
        execute_command_return_code_1_mock.return_value = 1
        yield execute_command_return_code_1_mock


@pytest.fixture
def raise_docker_error_with_command_mock():
    with mock.patch.object(
        errors, "raise_docker_error_with_command"
    ) as raise_docker_error_with_command:
        raise_docker_error_with_command.side_effect = errors.DockerError()


@pytest.fixture
def is_registry_uri_true_mock():
    with mock.patch.object(
        prediction_utils, "is_registry_uri"
    ) as is_registry_uri_true_mock:
        is_registry_uri_true_mock.return_value = True
        yield is_registry_uri_true_mock


@pytest.fixture
def is_registry_uri_false_mock():
    with mock.patch.object(
        prediction_utils, "is_registry_uri"
    ) as is_registry_uri_false_mock:
        is_registry_uri_false_mock.return_value = False
        yield is_registry_uri_false_mock


@pytest.fixture
def importlib_import_module_mock_once():
    with mock.patch.object(
        importlib, "import_module"
    ) as importlib_import_module_mock_once:
        yield importlib_import_module_mock_once


@pytest.fixture
def importlib_import_module_mock_twice():
    with mock.patch.object(
        importlib, "import_module"
    ) as importlib_import_module_mock_twice:
        return_values = {
            _DEFAULT_HANDLER_MODULE: mock.Mock(),
            f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}": mock.Mock(),
        }
        importlib_import_module_mock_twice.side_effect = return_values.get
        yield importlib_import_module_mock_twice


@pytest.fixture
def fastapi_mock():
    with mock.patch.object(model_server_module, "FastAPI") as fastapi_mock:
        yield fastapi_mock


class FakeHandler(Handler):
    def __init__(self, artifacts_uri, predictor=None):
        pass

    def handle(self, request):
        pass


class TestPredictor:
    def test_preprocess(self):
        prediction_input = {"x": [1]}
        predictor = get_test_predictor()

        result = predictor().preprocess(prediction_input)

        assert result == prediction_input

    def test_postprocess(self):
        prediction_results = {"x": [1]}
        predictor = get_test_predictor()

        result = predictor().postprocess(prediction_results)

        assert result == prediction_results


class TestDefaultSerializer:
    def test_deserialize_application_json(self):
        data = b'{"instances": [1, 2, 3]}'

        deserialized_data = DefaultSerializer.deserialize(
            data, content_type="application/json"
        )

        assert deserialized_data == {"instances": [1, 2, 3]}

    def test_deserialize_unsupported_content_type_throws_exception(self):
        content_type = "unsupported_type"
        expected_message = (
            f"Unsupported content type of the request: {content_type}.\n"
            f'Currently supported content-type in DefaultSerializer: "application/json".'
        )
        data = b'{"instances": [1, 2, 3]}'

        with pytest.raises(HTTPException) as exception:
            DefaultSerializer.deserialize(data, content_type=content_type)

        assert exception.value.status_code == 400
        assert exception.value.detail == expected_message

    def test_deserialize_invalid_json(self):
        data = b"instances"
        expected_message = "JSON deserialization failed for the request data"

        with pytest.raises(HTTPException) as exception:
            DefaultSerializer.deserialize(data, content_type="application/json")

        assert exception.value.status_code == 400
        assert expected_message in exception.value.detail

    def test_serialize_application_json(self):
        prediction = {}

        serialized_prediction = DefaultSerializer.serialize(
            prediction, accept="application/json"
        )

        assert serialized_prediction == "{}"

    @pytest.mark.parametrize(
        "accept",
        [
            ("application/json, text/html"),
            ("application/json, text/html;q=0.9"),
            ("text/html, application/json"),
            ("text/html, application/json;q=0.9"),
            (
                "text/html, application/xhtml+xml, application/xml;q=0.9, application/json;q=0.8"
            ),
            ("*/*"),
            ("text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8"),
            ("application/json, */*"),
            ("application/json, */*;q=0.9"),
            ("text/html, application/json, */*;q=0.9"),
            ("text/html, application/json;q=0.9, */*;q=0.8"),
        ],
    )
    def test_serialize_application_json_multiple_accept(self, accept):
        prediction = {}

        serialized_prediction = DefaultSerializer.serialize(prediction, accept=accept)

        assert serialized_prediction == "{}"

    def test_serialize_unsupported_accept_throws_exception(self):
        accept = "unsupported_type"
        expected_message = (
            f"Unsupported accept of the response: {accept}.\n"
            f'Currently supported accept in DefaultSerializer: "application/json".'
        )
        prediction = {}

        with pytest.raises(HTTPException) as exception:
            DefaultSerializer.serialize(prediction, accept=accept)

        assert exception.value.status_code == 400
        assert exception.value.detail == expected_message

    def test_serialize_invalid_json(self):
        data = b"instances"
        expected_message = "JSON serialization failed for the prediction result"

        with pytest.raises(HTTPException) as exception:
            DefaultSerializer.serialize(data, accept="application/json")

        assert exception.value.status_code == 400
        assert expected_message in exception.value.detail


class TestPredictionHandler:
    def test_init(self, predictor_mock):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        assert handler._predictor == predictor_mock()
        predictor_mock().load.assert_called_once_with(_TEST_GCS_ARTIFACTS_URI)

    def test_init_no_predictor_raises_exception(self):
        expected_message = (
            "PredictionHandler must have a predictor class passed to the init function."
        )

        with pytest.raises(ValueError) as exception:
            _ = PredictionHandler(_TEST_GCS_ARTIFACTS_URI)

        assert str(exception.value) == expected_message

    @pytest.mark.asyncio
    async def test_handle(
        self,
        deserialize_mock,
        get_content_type_from_headers_mock,
        predictor_mock,
        get_accept_from_headers_mock,
        serialize_mock,
    ):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        response = await handler.handle(get_test_request())

        assert response.status_code == 200
        assert response.body == _TEST_SERIALIZED_OUTPUT

        deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
        get_content_type_from_headers_mock.assert_called_once_with(get_test_headers())
        predictor_mock().preprocess.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().predict.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().postprocess.assert_called_once_with(_TEST_PREDICTION_OUTPUT)
        get_accept_from_headers_mock.assert_called_once_with(get_test_headers())
        serialize_mock.assert_called_once_with(
            _TEST_SERIALIZED_OUTPUT, _APPLICATION_JSON
        )

    @pytest.mark.asyncio
    async def test_handle_deserialize_raises_exception(
        self,
        deserialize_exception_mock,
        get_content_type_from_headers_mock,
        predictor_mock,
        get_accept_from_headers_mock,
        serialize_mock,
    ):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        with pytest.raises(HTTPException):
            await handler.handle(get_test_request())

        get_content_type_from_headers_mock.assert_called_once_with(get_test_headers())
        deserialize_exception_mock.assert_called_once_with(
            _TEST_INPUT, _APPLICATION_JSON
        )
        assert not predictor_mock().preprocess.called
        assert not predictor_mock().predict.called
        assert not predictor_mock().postprocess.called
        assert not get_accept_from_headers_mock.called
        assert not serialize_mock.called

    @pytest.mark.asyncio
    async def test_handle_predictor_raises_exception(
        self,
        deserialize_mock,
        get_content_type_from_headers_mock,
        get_accept_from_headers_mock,
        serialize_mock,
    ):
        preprocess_mock = mock.MagicMock(return_value=_TEST_DESERIALIZED_INPUT)
        predict_mock = mock.MagicMock(side_effect=Exception())
        postprocess_mock = mock.MagicMock(return_value=_TEST_SERIALIZED_OUTPUT)
        handler = PredictionHandler(
            _TEST_GCS_ARTIFACTS_URI, predictor=get_test_predictor()
        )
        expected_message = (
            "The following exception has occurred: Exception. Arguments: ()."
        )

        with mock.patch.multiple(
            handler._predictor,
            preprocess=preprocess_mock,
            predict=predict_mock,
            postprocess=postprocess_mock,
        ):
            with pytest.raises(HTTPException) as exception:
                await handler.handle(get_test_request())

        assert exception.value.status_code == 500
        assert exception.value.detail == expected_message
        get_content_type_from_headers_mock.assert_called_once_with(get_test_headers())
        deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
        preprocess_mock.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predict_mock.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        assert not postprocess_mock.called
        assert not get_accept_from_headers_mock.called
        assert not serialize_mock.called

    @pytest.mark.asyncio
    async def test_handle_predictor_raises_http_exception(
        self,
        get_content_type_from_headers_mock,
        deserialize_mock,
        get_accept_from_headers_mock,
        serialize_mock,
    ):
        status_code = 400
        expected_message = "This is an user error."
        preprocess_mock = mock.MagicMock(return_value=_TEST_DESERIALIZED_INPUT)
        predict_mock = mock.MagicMock(
            side_effect=HTTPException(status_code=status_code, detail=expected_message)
        )
        postprocess_mock = mock.MagicMock(return_value=_TEST_SERIALIZED_OUTPUT)
        handler = PredictionHandler(
            _TEST_GCS_ARTIFACTS_URI, predictor=get_test_predictor()
        )

        with mock.patch.multiple(
            handler._predictor,
            preprocess=preprocess_mock,
            predict=predict_mock,
            postprocess=postprocess_mock,
        ):
            with pytest.raises(HTTPException) as exception:
                await handler.handle(get_test_request())

        assert exception.value.status_code == status_code
        assert exception.value.detail == expected_message
        get_content_type_from_headers_mock.assert_called_once_with(get_test_headers())
        deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
        preprocess_mock.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predict_mock.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        assert not postprocess_mock.called
        assert not get_accept_from_headers_mock.called
        assert not serialize_mock.called

    @pytest.mark.asyncio
    async def test_handle_serialize_raises_exception(
        self,
        deserialize_mock,
        get_content_type_from_headers_mock,
        predictor_mock,
        get_accept_from_headers_mock,
        serialize_exception_mock,
    ):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        with pytest.raises(HTTPException):
            await handler.handle(get_test_request())

        deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
        get_content_type_from_headers_mock.assert_called_once_with(get_test_headers())
        predictor_mock().preprocess.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().predict.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().postprocess.assert_called_once_with(_TEST_PREDICTION_OUTPUT)
        get_accept_from_headers_mock.assert_called_once_with(get_test_headers())
        serialize_exception_mock.assert_called_once_with(
            _TEST_SERIALIZED_OUTPUT, _APPLICATION_JSON
        )


class TestHandlerUtils:
    @pytest.mark.parametrize(
        "header_key, content_type_value, expected_content_type",
        [
            ("Content-Type", "fake_content_type", "fake_content_type"),
            ("content-Type", "fake_content_type", "fake_content_type"),
            ("content-type", "fake_content_type", "fake_content_type"),
            ("Content-type", "fake_content_type", "fake_content_type"),
            ("ContentType", "fake_content_type", "fake_content_type"),
            ("contentType", "fake_content_type", "fake_content_type"),
            ("contenttype", "fake_content_type", "fake_content_type"),
            ("Contenttype", "fake_content_type", "fake_content_type"),
            ("Content-Type-", "fake_content_type", None),
            ("cContent-Type", "fake_content_type", None),
        ],
    )
    def test_get_content_type_from_headers(
        self, header_key, content_type_value, expected_content_type
    ):
        headers = Headers({header_key: content_type_value})

        content_type = handler_utils.get_content_type_from_headers(headers)

        assert content_type == expected_content_type

    @pytest.mark.parametrize(
        "header_key, content_type_value, expected_content_type",
        [
            ("Content-Type", "fake_content_type; charset", "fake_content_type"),
            ("content-Type", "fake_content_type; charset", "fake_content_type"),
            ("content-type", "fake_content_type; charset", "fake_content_type"),
            ("Content-type", "fake_content_type; charset", "fake_content_type"),
            ("ContentType", "fake_content_type; charset", "fake_content_type"),
            ("contentType", "fake_content_type; charset", "fake_content_type"),
            ("contenttype", "fake_content_type; charset", "fake_content_type"),
            ("Contenttype", "fake_content_type; charset", "fake_content_type"),
            ("Content-Type-", "fake_content_type; charset", None),
            ("cContent-Type", "fake_content_type; charset", None),
        ],
    )
    def test_get_content_type_from_headers_with_parameter(
        self, header_key, content_type_value, expected_content_type
    ):
        headers = Headers({header_key: content_type_value})

        content_type = handler_utils.get_content_type_from_headers(headers)

        assert content_type == expected_content_type

    def test_get_content_type_from_headers_no_headers(self):
        headers = Headers({})

        content_type = handler_utils.get_content_type_from_headers(headers)

        assert content_type is None

    def test_get_content_type_from_headers_none(self):
        content_type = handler_utils.get_content_type_from_headers(None)

        assert content_type is None

    @pytest.mark.parametrize(
        "header_key, accept_value, expected_accept",
        [
            ("Accept", "fake_accept", "fake_accept"),
            ("accept", "fake_accept", "fake_accept"),
            ("Accept", prediction.ANY_ACCEPT_TYPE, prediction.ANY_ACCEPT_TYPE),
            ("Accept", "fake_accept;q=0.9", "fake_accept;q=0.9"),
            ("accept", "fake_accept;q=0.9", "fake_accept;q=0.9"),
            ("aaccept", "fake_accept; charset", prediction.DEFAULT_ACCEPT_VALUE),
            ("accept-", "fake_accept; charset", prediction.DEFAULT_ACCEPT_VALUE),
        ],
    )
    def test_get_accept_from_headers(self, header_key, accept_value, expected_accept):
        headers = Headers({header_key: accept_value})

        accept = handler_utils.get_accept_from_headers(headers)

        assert accept == expected_accept

    def test_get_accept_from_headers_no_headers(self):
        headers = Headers({})

        accept = handler_utils.get_accept_from_headers(headers)

        assert accept == prediction.DEFAULT_ACCEPT_VALUE

    def test_get_accept_from_headers_none(self):
        accept = handler_utils.get_accept_from_headers(None)

        assert accept == prediction.DEFAULT_ACCEPT_VALUE

    @pytest.mark.parametrize(
        "accept, expected",
        [
            (
                "application/json, text/html",
                {"application/json": 1.0, "text/html": 1.0},
            ),
            (
                "application/json, text/html;q=0.9",
                {"application/json": 1.0, "text/html": 0.9},
            ),
            (
                "text/html, application/json",
                {"text/html": 1.0, "application/json": 1.0},
            ),
            (
                "text/html, application/json;q=0.9",
                {"text/html": 1.0, "application/json": 0.9},
            ),
            (
                "text/html, application/xhtml+xml, application/xml;q=0.9, application/json;q=0.8",
                {
                    "text/html": 1.0,
                    "application/xhtml+xml": 1.0,
                    "application/xml": 0.9,
                    "application/json": 0.8,
                },
            ),
            ("*/*", {"*/*": 1.0}),
            (
                "text/html, application/xhtml+xml, application/xml;q=0.9, */*;q=0.8",
                {
                    "text/html": 1.0,
                    "application/xhtml+xml": 1.0,
                    "application/xml": 0.9,
                    "*/*": 0.8,
                },
            ),
            ("application/json, */*", {"application/json": 1.0, "*/*": 1.0}),
            ("application/json, */*;q=0.9", {"application/json": 1.0, "*/*": 0.9}),
            (
                "text/html, application/json, */*;q=0.9",
                {"text/html": 1.0, "application/json": 1.0, "*/*": 0.9},
            ),
            (
                "text/html, application/json;q=0.9, */*;q=0.8",
                {"text/html": 1.0, "application/json": 0.9, "*/*": 0.8},
            ),
            (None, {}),
        ],
    )
    def test_parse_accept_header(self, accept, expected):
        result = handler_utils.parse_accept_header(accept)

        assert result == expected


class TestLocalModel:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def _load_module(self, name, location):
        spec = importlib.util.spec_from_file_location(name, location)
        return importlib.util.module_from_spec(spec)

    def test_init_with_serving_container_spec(self):
        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]
        ports = [
            gca_model_compat.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_PORTS
        ]
        grpc_ports = [
            gca_model_compat.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_GRPC_PORTS
        ]
        container_spec = gca_model_compat.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_SERVING_CONTAINER_COMMAND,
            args=_TEST_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
            grpc_ports=grpc_ports,
        )

        local_model = LocalModel(
            serving_container_spec=container_spec,
        )

        assert local_model.serving_container_spec.image_uri == container_spec.image_uri
        assert (
            local_model.serving_container_spec.predict_route
            == container_spec.predict_route
        )
        assert (
            local_model.serving_container_spec.health_route
            == container_spec.health_route
        )
        assert local_model.serving_container_spec.command == container_spec.command
        assert local_model.serving_container_spec.args == container_spec.args
        assert local_model.serving_container_spec.env == container_spec.env
        assert local_model.serving_container_spec.ports == container_spec.ports
        assert (
            local_model.serving_container_spec.grpc_ports == container_spec.grpc_ports
        )

    def test_init_with_serving_container_spec_but_not_image_uri_throws_exception(self):
        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]
        ports = [
            gca_model_compat.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_PORTS
        ]
        grpc_ports = [
            gca_model_compat.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_GRPC_PORTS
        ]
        container_spec = gca_model_compat.ModelContainerSpec(
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_SERVING_CONTAINER_COMMAND,
            args=_TEST_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
            grpc_ports=grpc_ports,
        )
        expected_message = "Image uri is required for the serving container spec to initialize a LocalModel instance."

        with pytest.raises(ValueError) as exception:
            _ = LocalModel(
                serving_container_spec=container_spec,
            )

        assert str(exception.value) == expected_message

    def test_init_with_separate_args(self):
        local_model = LocalModel(
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            serving_container_command=_TEST_SERVING_CONTAINER_COMMAND,
            serving_container_args=_TEST_SERVING_CONTAINER_ARGS,
            serving_container_environment_variables=_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            serving_container_ports=_TEST_SERVING_CONTAINER_PORTS,
            serving_container_grpc_ports=_TEST_SERVING_CONTAINER_GRPC_PORTS,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model_compat.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_PORTS
        ]

        grpc_ports = [
            gca_model_compat.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_GRPC_PORTS
        ]

        container_spec = gca_model_compat.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_SERVING_CONTAINER_COMMAND,
            args=_TEST_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
            grpc_ports=grpc_ports,
        )

        assert local_model.serving_container_spec.image_uri == container_spec.image_uri
        assert (
            local_model.serving_container_spec.predict_route
            == container_spec.predict_route
        )
        assert (
            local_model.serving_container_spec.health_route
            == container_spec.health_route
        )
        assert local_model.serving_container_spec.command == container_spec.command
        assert local_model.serving_container_spec.args == container_spec.args
        assert local_model.serving_container_spec.env == container_spec.env
        assert local_model.serving_container_spec.ports == container_spec.ports
        assert (
            local_model.serving_container_spec.grpc_ports == container_spec.grpc_ports
        )

    def test_init_with_separate_args_but_not_image_uri_throws_exception(self):
        expected_message = "Serving container image uri is required to initialize a LocalModel instance."

        with pytest.raises(ValueError) as exception:
            _ = LocalModel(
                serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                serving_container_command=_TEST_SERVING_CONTAINER_COMMAND,
                serving_container_args=_TEST_SERVING_CONTAINER_ARGS,
                serving_container_environment_variables=_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
                serving_container_ports=_TEST_SERVING_CONTAINER_PORTS,
                serving_container_grpc_ports=_TEST_SERVING_CONTAINER_GRPC_PORTS,
            )

        assert str(exception.value) == expected_message

    def test_build_cpr_model_creates_and_get_localmodel(
        self,
        tmp_path,
        inspect_source_from_class_mock_predictor_only,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class {predictor_class}:
                pass
            """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))

        local_model = LocalModel.build_cpr_model(
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            predictor=my_predictor,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_predictor_only.assert_called_once_with(
            my_predictor, str(src_dir)
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=None,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
                "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
                "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
                "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
            },
            pip_command="pip",
            python_command="python",
            no_cache=False,
        )

    def test_build_cpr_model_fails_handler_is_none(
        self,
        tmp_path,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class {predictor_class}:
                pass
            """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))
        expected_message = "A handler must be provided but handler is None."

        with pytest.raises(ValueError) as exception:
            _ = LocalModel.build_cpr_model(
                str(src_dir),
                _TEST_OUTPUT_IMAGE,
                predictor=my_predictor,
                handler=None,
            )

        assert str(exception.value) == expected_message

    def test_build_cpr_model_fails_prediction_handler_but_predictor_is_none(
        self,
        tmp_path,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        expected_message = (
            "PredictionHandler must have a predictor class but predictor is None."
        )

        with pytest.raises(ValueError) as exception:
            _ = LocalModel.build_cpr_model(
                str(src_dir),
                _TEST_OUTPUT_IMAGE,
                predictor=None,
            )

        assert str(exception.value) == expected_message

    def test_build_cpr_model_with_custom_handler(
        self,
        tmp_path,
        inspect_source_from_class_mock_predictor_and_handler,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class {predictor_class}:
                pass
            """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))
        handler = src_dir / _TEST_HANDLER_FILE
        handler.write_text(
            textwrap.dedent(
                """
            class {handler_class}:
                pass
            """
            ).format(handler_class=_TEST_HANDLER_CLASS)
        )
        my_handler = self._load_module(_TEST_HANDLER_CLASS, str(handler))

        local_model = LocalModel.build_cpr_model(
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            predictor=my_predictor,
            handler=my_handler,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_predictor_and_handler.assert_has_calls(
            [mock.call(my_handler, str(src_dir)), mock.call(my_predictor, str(src_dir))]
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=None,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": f"{_TEST_SRC_DIR}.{_TEST_HANDLER_FILE_STEM}",
                "HANDLER_CLASS": _TEST_HANDLER_CLASS,
                "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
                "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
            },
            pip_command="pip",
            python_command="python",
            no_cache=False,
        )

    def test_build_cpr_model_with_custom_handler_and_predictor_is_none(
        self,
        tmp_path,
        inspect_source_from_class_mock_handler_only,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        handler = src_dir / _TEST_HANDLER_FILE
        handler.write_text(
            textwrap.dedent(
                """
            class {handler_class}:
                pass
            """
            ).format(handler_class=_TEST_HANDLER_CLASS)
        )
        my_handler = self._load_module(_TEST_HANDLER_CLASS, str(handler))

        local_model = LocalModel.build_cpr_model(
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            predictor=None,
            handler=my_handler,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_handler_only.assert_called_once_with(
            my_handler, str(src_dir)
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=None,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": f"{_TEST_SRC_DIR}.{_TEST_HANDLER_FILE_STEM}",
                "HANDLER_CLASS": _TEST_HANDLER_CLASS,
            },
            pip_command="pip",
            python_command="python",
            no_cache=False,
        )

    def test_build_cpr_model_creates_and_get_localmodel_base_is_prebuilt(
        self,
        tmp_path,
        inspect_source_from_class_mock_predictor_only,
        is_prebuilt_prediction_container_uri_is_true_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class {predictor_class}:
                pass
            """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))

        local_model = LocalModel.build_cpr_model(
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            predictor=my_predictor,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_predictor_only.assert_called_once_with(
            my_predictor, str(src_dir)
        )
        is_prebuilt_prediction_container_uri_is_true_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=None,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
                "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
                "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
                "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
            },
            pip_command="pip3",
            python_command="python3",
            no_cache=False,
        )

    def test_build_cpr_model_creates_and_get_localmodel_with_requirements_path(
        self,
        tmp_path,
        inspect_source_from_class_mock_predictor_only,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class {predictor_class}:
                pass
            """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))
        requirements_path = f"{_TEST_SRC_DIR}/requirements.txt"

        local_model = LocalModel.build_cpr_model(
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            predictor=my_predictor,
            requirements_path=requirements_path,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_predictor_only.assert_called_once_with(
            my_predictor, str(src_dir)
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=requirements_path,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
                "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
                "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
                "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
            },
            pip_command="pip",
            python_command="python",
            no_cache=False,
        )

    def test_build_cpr_model_creates_and_get_localmodel_with_extra_packages(
        self,
        tmp_path,
        inspect_source_from_class_mock_predictor_only,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
            class {predictor_class}:
                pass
            """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))
        extra_packages = [f"{_TEST_SRC_DIR}/custom_package.tar.gz"]

        local_model = LocalModel.build_cpr_model(
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            predictor=my_predictor,
            extra_packages=extra_packages,
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_predictor_only.assert_called_once_with(
            my_predictor, str(src_dir)
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=None,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=extra_packages,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
                "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
                "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
                "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
            },
            pip_command="pip",
            python_command="python",
            no_cache=False,
        )

    def test_build_cpr_model_creates_and_get_localmodel_no_cache(
        self,
        tmp_path,
        inspect_source_from_class_mock_predictor_only,
        is_prebuilt_prediction_container_uri_is_false_mock,
        build_image_mock,
    ):
        src_dir = tmp_path / _TEST_SRC_DIR
        src_dir.mkdir()
        predictor = src_dir / _TEST_PREDICTOR_FILE
        predictor.write_text(
            textwrap.dedent(
                """
                class {predictor_class}:
                    pass
                """
            ).format(predictor_class=_TEST_PREDICTOR_CLASS)
        )
        my_predictor = self._load_module(_TEST_PREDICTOR_CLASS, str(predictor))
        no_cache = True

        local_model = LocalModel.build_cpr_model(
            str(src_dir), _TEST_OUTPUT_IMAGE, predictor=my_predictor, no_cache=no_cache
        )

        assert local_model.serving_container_spec.image_uri == _TEST_OUTPUT_IMAGE
        assert local_model.serving_container_spec.predict_route == DEFAULT_PREDICT_ROUTE
        assert local_model.serving_container_spec.health_route == DEFAULT_HEALTH_ROUTE
        inspect_source_from_class_mock_predictor_only.assert_called_once_with(
            my_predictor, str(src_dir)
        )
        is_prebuilt_prediction_container_uri_is_false_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE
        )
        build_image_mock.assert_called_once_with(
            _DEFAULT_BASE_IMAGE,
            str(src_dir),
            _TEST_OUTPUT_IMAGE,
            python_module=_DEFAULT_PYTHON_MODULE,
            requirements_path=None,
            extra_requirements=_DEFAULT_SDK_REQUIREMENTS,
            extra_packages=None,
            exposed_ports=[DEFAULT_HTTP_PORT],
            environment_variables={
                "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
                "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
                "PREDICTOR_MODULE": f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}",
                "PREDICTOR_CLASS": _TEST_PREDICTOR_CLASS,
            },
            pip_command="pip",
            python_command="python",
            no_cache=no_cache,
        )

    def test_deploy_to_local_endpoint(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
        local_endpoint_del_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)

        with local_model.deploy_to_local_endpoint():
            pass

        local_endpoint_init_mock.assert_called_once_with(
            serving_container_image_uri=_TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route="",
            serving_container_health_route="",
            serving_container_command=[],
            serving_container_args=[],
            serving_container_environment_variables={},
            serving_container_ports=[],
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
            container_ready_timeout=None,
            container_ready_check_interval=None,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called

    def test_deploy_to_local_endpoint_with_all_parameters(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
        local_endpoint_del_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        artifact_uri = "gs://myproject/mymodel"
        credential_path = "key.json"
        host_port = 6666
        container_ready_timeout = 60
        container_ready_check_interval = 5

        with local_model.deploy_to_local_endpoint(
            artifact_uri=artifact_uri,
            credential_path=credential_path,
            host_port=host_port,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        ):
            pass

        local_endpoint_init_mock.assert_called_once_with(
            serving_container_image_uri=_TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route="",
            serving_container_health_route="",
            serving_container_command=[],
            serving_container_args=[],
            serving_container_environment_variables={},
            serving_container_ports=[],
            credential_path=credential_path,
            host_port=host_port,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called

    def test_deploy_to_local_endpoint_with_gpu_count(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
        local_endpoint_del_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)

        with local_model.deploy_to_local_endpoint(
            gpu_count=_TEST_GPU_COUNT, gpu_capabilities=_TEST_GPU_CAPABILITIES
        ):
            pass

        local_endpoint_init_mock.assert_called_once_with(
            serving_container_image_uri=_TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route="",
            serving_container_health_route="",
            serving_container_command=[],
            serving_container_args=[],
            serving_container_environment_variables={},
            serving_container_ports=[],
            credential_path=None,
            host_port=None,
            gpu_count=_TEST_GPU_COUNT,
            gpu_device_ids=None,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
            container_ready_timeout=None,
            container_ready_check_interval=None,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called

    def test_deploy_to_local_endpoint_with_gpu_device_ids(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
        local_endpoint_del_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)

        with local_model.deploy_to_local_endpoint(
            gpu_device_ids=_TEST_GPU_DEVICE_IDS, gpu_capabilities=_TEST_GPU_CAPABILITIES
        ):
            pass

        local_endpoint_init_mock.assert_called_once_with(
            serving_container_image_uri=_TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route="",
            serving_container_health_route="",
            serving_container_command=[],
            serving_container_args=[],
            serving_container_environment_variables={},
            serving_container_ports=[],
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=_TEST_GPU_DEVICE_IDS,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
            container_ready_timeout=None,
            container_ready_check_interval=None,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called

    def test_copy_image(
        self,
        pull_image_if_not_exists_mock,
        execute_command_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        dst_image_uri = "new_image:latest"
        expected_command = ["docker", "tag", f"{_TEST_IMAGE_URI}", f"{dst_image_uri}"]

        new_local_model = local_model.copy_image(dst_image_uri)

        pull_image_if_not_exists_mock.assert_called_once_with()
        execute_command_mock.assert_called_once_with(expected_command)
        assert new_local_model.serving_container_spec.image_uri == dst_image_uri

    def test_copy_image_raises_exception(
        self,
        pull_image_if_not_exists_mock,
        execute_command_return_code_1_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        dst_image_uri = "new_image:latest"
        expected_command = ["docker", "tag", f"{_TEST_IMAGE_URI}", f"{dst_image_uri}"]
        expected_message = "Docker failed with error code"
        expected_return_code = 1

        with mock.patch.object(
            errors, "raise_docker_error_with_command"
        ) as raise_docker_error_with_command:
            raise_docker_error_with_command.side_effect = errors.DockerError(
                expected_message, expected_command, expected_return_code
            )

            with pytest.raises(errors.DockerError) as exception:
                local_model.copy_image(dst_image_uri)

        pull_image_if_not_exists_mock.assert_called_once_with()
        execute_command_return_code_1_mock.assert_called_once_with(expected_command)
        assert exception.value.message == expected_message
        assert exception.value.cmd == expected_command
        assert exception.value.exit_code == expected_return_code

    def test_push_image(
        self,
        execute_command_mock,
        is_registry_uri_true_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        expected_command = ["docker", "push", f"{_TEST_IMAGE_URI}"]

        local_model.push_image()

        execute_command_mock.assert_called_once_with(expected_command)

    def test_push_image_image_uri_is_not_registry_uri(
        self,
        execute_command_mock,
        is_registry_uri_false_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        expected_message = (
            "The image uri must be a container registry or artifact registry uri "
            f"but it is: {_TEST_IMAGE_URI}."
        )

        with pytest.raises(ValueError) as exception:
            local_model.push_image()

        assert str(exception.value) == expected_message

    def test_push_image_raises_exception(
        self,
        execute_command_return_code_1_mock,
        is_registry_uri_true_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        expected_command = ["docker", "push", f"{_TEST_IMAGE_URI}"]
        expected_message = "Docker failed with error code"
        expected_return_code = 1

        with mock.patch.object(
            errors, "raise_docker_error_with_command"
        ) as raise_docker_error_with_command:
            raise_docker_error_with_command.side_effect = errors.DockerError(
                expected_message, expected_command, expected_return_code
            )

            with pytest.raises(errors.DockerError) as exception:
                local_model.push_image()

        execute_command_return_code_1_mock.assert_called_once_with(expected_command)
        assert exception.value.message == expected_message
        assert exception.value.cmd == expected_command
        assert exception.value.exit_code == expected_return_code

    def test_pull_image_if_not_exists_image_exists(
        self,
        check_image_exists_locally_true_mock,
        execute_command_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)

        local_model.pull_image_if_not_exists()

        assert not execute_command_mock.called

    def test_pull_image_if_not_exists_image_not_exists(
        self,
        check_image_exists_locally_false_mock,
        execute_command_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        expected_command = ["docker", "pull", f"{_TEST_IMAGE_URI}"]

        local_model.pull_image_if_not_exists()

        execute_command_mock.assert_called_once_with(expected_command)

    def test_pull_image_if_not_exists_docker_command_fail(
        self,
        check_image_exists_locally_false_mock,
        execute_command_return_code_1_mock,
    ):
        container_spec = gca_model_compat.ModelContainerSpec(image_uri=_TEST_IMAGE_URI)
        local_model = LocalModel(container_spec)
        expected_command = ["docker", "pull", f"{_TEST_IMAGE_URI}"]
        return_code = 1
        expected_message = textwrap.dedent(
            """
            Docker failed with error code {return_code}.
            Command: {command}
            """.format(
                return_code=return_code, command=" ".join(expected_command)
            )
        )

        with pytest.raises(errors.DockerError) as exception:
            local_model.pull_image_if_not_exists()

        execute_command_return_code_1_mock.assert_called_once_with(expected_command)
        assert exception.value.message == expected_message
        assert exception.value.cmd == expected_command
        assert exception.value.exit_code == return_code


class TestLocalEndpoint:
    def test_init(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_all_parameters(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        artifact_uri = "gs://myproject/mymodel"
        serving_container_predict_route = "/custom_predict"
        serving_container_health_route = "/custom_health"
        serving_container_command = ["echo", "hello"]
        serving_container_args = [">", "tmp.log"]
        serving_container_environment_variables = {"custom_key": "custom_value"}
        serving_container_ports = [5555]
        credential_path = "key.json"
        host_port = 6666
        container_ready_timeout = 60
        container_ready_check_interval = 5

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        ):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_initializer_project(
        self,
        initializer_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={
                local_endpoint._GCLOUD_PROJECT_ENV: _TEST_PROJECT
            },
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_gpu_count(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(
            _TEST_IMAGE_URI,
            gpu_count=_TEST_GPU_COUNT,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        ):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=_TEST_GPU_COUNT,
            gpu_device_ids=None,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_gpu_device_ids(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(
            _TEST_IMAGE_URI,
            gpu_device_ids=_TEST_GPU_DEVICE_IDS,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        ):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=_TEST_GPU_DEVICE_IDS,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_gpu_count_and_device_ids_throw_error(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
    ):
        expected_message = (
            "At most one gpu_count or gpu_device_ids can be set but both are set."
        )

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                gpu_count=_TEST_GPU_COUNT,
                gpu_device_ids=_TEST_GPU_DEVICE_IDS,
                gpu_capabilities=_TEST_GPU_CAPABILITIES,
            ):
                pass

        assert str(exception.value) == expected_message

    def test_init_with_gpu_count_but_capabilities_unset(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI, gpu_count=_TEST_GPU_COUNT):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=_TEST_GPU_COUNT,
            gpu_device_ids=None,
            gpu_capabilities=prediction.DEFAULT_LOCAL_RUN_GPU_CAPABILITIES,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_gpu_device_ids_but_capabilities_unset(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI, gpu_device_ids=_TEST_GPU_DEVICE_IDS):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=_TEST_GPU_DEVICE_IDS,
            gpu_capabilities=prediction.DEFAULT_LOCAL_RUN_GPU_CAPABILITIES,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_with_gpu_capabilities_but_count_and_device_ids_unset(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI, gpu_capabilities=_TEST_GPU_CAPABILITIES):
            pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=prediction.DEFAULT_LOCAL_RUN_GPU_COUNT,
            gpu_device_ids=None,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )
        assert run_prediction_container_mock.return_value.stop.called

    def test_init_fail_with_container_not_running(
        self,
        initializer_project_none_mock,
        run_prediction_container_container_not_running_mock,
        time_sleep_mock,
        local_endpoint_run_health_check_mock,
    ):
        expected_message = "The container never starts running."
        expected_command = ""
        expected_return_code = 1
        with pytest.raises(errors.DockerError) as exception:
            with LocalEndpoint(_TEST_IMAGE_URI):
                pass

        run_prediction_container_container_not_running_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )
        assert (
            run_prediction_container_container_not_running_mock.return_value.stop.called
        )
        assert exception.value.message == expected_message
        assert exception.value.cmd == expected_command
        assert exception.value.exit_code == expected_return_code

    def test_init_fail_with_health_check_fail_container_not_running(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        time_sleep_mock,
        local_endpoint_run_health_check_raise_exception_mock,
        local_endpoint_print_container_logs_mock,
        get_container_status_second_fail_mock,
    ):
        expected_command = ""
        expected_message = "Container exited before the first health check succeeded."
        expected_return_code = 1

        with pytest.raises(errors.DockerError) as exception:
            with LocalEndpoint(_TEST_IMAGE_URI):
                pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )
        local_endpoint_print_container_logs_mock.assert_called_once_with(
            show_all=True,
            message="Container already exited, all container logs:",
        )
        assert run_prediction_container_mock.return_value.stop.called
        assert exception.value.message == expected_message
        assert exception.value.cmd == expected_command
        assert exception.value.exit_code == expected_return_code

    def test_init_fail_with_health_check_fail_timeout(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        time_sleep_mock,
        local_endpoint_run_health_check_raise_exception_mock,
        local_endpoint_print_container_logs_mock,
        get_container_status_running_mock,
    ):
        expected_command = ""
        expected_message = "The health check never succeeded."
        expected_return_code = 1

        with pytest.raises(errors.DockerError) as exception:
            with LocalEndpoint(_TEST_IMAGE_URI):
                pass

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )
        local_endpoint_print_container_logs_mock.assert_called_once_with(
            show_all=True,
            message="Health check never succeeds, all container logs:",
        )
        assert run_prediction_container_mock.return_value.stop.called
        assert exception.value.message == expected_message
        assert exception.value.cmd == expected_command
        assert exception.value.exit_code == expected_return_code

    def test_serve(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        local_endpoint = LocalEndpoint(_TEST_IMAGE_URI)

        local_endpoint.serve()

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )

    def test_serve_with_all_parameters(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        artifact_uri = "gs://myproject/mymodel"
        serving_container_predict_route = "/custom_predict"
        serving_container_health_route = "/custom_health"
        serving_container_command = ["echo", "hello"]
        serving_container_args = [">", "tmp.log"]
        serving_container_environment_variables = {"custom_key": "custom_value"}
        serving_container_ports = [5555]
        credential_path = "key.json"
        host_port = 6666
        container_ready_timeout = 60
        container_ready_check_interval = 5
        local_endpoint = LocalEndpoint(
            _TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        )

        local_endpoint.serve()

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=artifact_uri,
            serving_container_predict_route=serving_container_predict_route,
            serving_container_health_route=serving_container_health_route,
            serving_container_command=serving_container_command,
            serving_container_args=serving_container_args,
            serving_container_environment_variables=serving_container_environment_variables,
            serving_container_ports=serving_container_ports,
            credential_path=credential_path,
            host_port=host_port,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )

    def test_serve_with_initializer_project(
        self,
        initializer_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        local_endpoint_object = LocalEndpoint(_TEST_IMAGE_URI)

        local_endpoint_object.serve()

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={
                local_endpoint._GCLOUD_PROJECT_ENV: _TEST_PROJECT
            },
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )

    def test_serve_with_gpu_count(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        local_endpoint = LocalEndpoint(
            _TEST_IMAGE_URI,
            gpu_count=_TEST_GPU_COUNT,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )

        local_endpoint.serve()

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=_TEST_GPU_COUNT,
            gpu_device_ids=None,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )

    def test_serve_with_gpu_device_ids(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        local_endpoint = LocalEndpoint(
            _TEST_IMAGE_URI,
            gpu_device_ids=_TEST_GPU_DEVICE_IDS,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )

        local_endpoint.serve()

        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=_TEST_GPU_DEVICE_IDS,
            gpu_capabilities=_TEST_GPU_CAPABILITIES,
        )

    def test_serve_serve_twice(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        local_endpoint = LocalEndpoint(_TEST_IMAGE_URI)
        local_endpoint.serve()

        # Call serve again.
        local_endpoint.serve()

        # This is only called once.
        run_prediction_container_mock.assert_called_once_with(
            _TEST_IMAGE_URI,
            artifact_uri=None,
            serving_container_predict_route=prediction.DEFAULT_LOCAL_PREDICT_ROUTE,
            serving_container_health_route=prediction.DEFAULT_LOCAL_HEALTH_ROUTE,
            serving_container_command=None,
            serving_container_args=None,
            serving_container_environment_variables={},
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
            gpu_count=None,
            gpu_device_ids=None,
            gpu_capabilities=None,
        )

    def test_stop(
        self,
        initializer_project_none_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        endpoint = LocalEndpoint(_TEST_IMAGE_URI)
        endpoint.serve()

        endpoint.stop()

        assert run_prediction_container_mock.return_value.stop.called

    def test_predict_request(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        requests_post_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request=request)

        requests_post_mock.assert_called_once_with(url, data=request, headers=None)
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_request_with_headers(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        requests_post_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        headers = {"Custom-header": "Custom-value"}

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request=request, headers=headers)

        requests_post_mock.assert_called_once_with(url, data=request, headers=headers)
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_request_file(
        self,
        tmp_path,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        requests_post_mock,
        open_file_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        request_file = tmp_path / "input.json"
        request_file.write_text(request)

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request_file=request_file)

        requests_post_mock.assert_called_once_with(
            url, data=open_file_mock, headers=None
        )
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_request_file_with_headers(
        self,
        tmp_path,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        requests_post_mock,
        open_file_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        request_file = tmp_path / "input.json"
        request_file.write_text(request)
        headers = {"Custom-header": "Custom-value"}

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_predict_route=serving_container_predict_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.predict(request_file=request_file, headers=headers)

        requests_post_mock.assert_called_once_with(
            url, data=open_file_mock, headers=headers
        )
        assert response.status_code == get_requests_post_response().status_code
        assert response._content == get_requests_post_response()._content

    def test_predict_container_exited_raises_exception(
        self,
        run_prediction_container_mock,
        requests_post_mock,
    ):
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        endpoint = LocalEndpoint(
            _TEST_IMAGE_URI,
        )
        endpoint.container_exited = True
        expected_message = (
            "The local endpoint is not serving traffic. Please call `serve()`."
        )

        with pytest.raises(RuntimeError) as exception:
            endpoint.predict(request=request)

        assert str(exception.value) == expected_message

    def test_predict_both_request_and_request_file_specified_raises_exception(
        self,
        tmp_path,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'
        request_file = tmp_path / "input.json"
        request_file.write_text(request)
        expected_message = (
            "request and request_file can not be specified at the same time."
        )

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request=request, request_file=request_file)

        assert str(exception.value) == expected_message

    def test_predict_none_of_request_and_request_file_specified_raises_exception(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        expected_message = "One of request and request_file needs to be specified."

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict()

        assert str(exception.value) == expected_message

    def test_predict_request_file_not_exists_raises_exception(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        request_file = "non_existing_input.json"
        expected_message = f"request_file does not exist: {request_file}."

        with pytest.raises(ValueError) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request_file=request_file)

        assert str(exception.value) == expected_message

    def test_predict_raises_exception(
        self,
        local_endpoint_logger_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        requests_post_raises_exception_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'

        with pytest.raises(requests.exceptions.RequestException) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request=request)

        requests_post_raises_exception_mock.assert_called_once_with(
            url, data=request, headers=None
        )
        assert local_endpoint_logger_mock.warning.called
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_predict_raises_exception_not_verbose(
        self,
        local_endpoint_logger_mock,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        requests_post_raises_exception_mock,
    ):
        serving_container_predict_route = "/custom_predict"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_predict_route}"
        request = '{"instances": [{"x": [[1.1, 2.2, 3.3, 5.5]]}]}'

        with pytest.raises(requests.exceptions.RequestException) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_predict_route=serving_container_predict_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.predict(request=request, verbose=False)

        requests_post_raises_exception_mock.assert_called_once_with(
            url, data=request, headers=None
        )
        assert not local_endpoint_logger_mock.warning.called
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_run_health_check(
        self,
        run_prediction_container_mock,
        requests_get_mock,
    ):
        serving_container_health_route = "/custom_health"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_health_route}"

        with LocalEndpoint(
            _TEST_IMAGE_URI,
            serving_container_health_route=serving_container_health_route,
            host_port=host_port,
        ) as endpoint:
            response = endpoint.run_health_check()

        requests_get_mock.assert_called_with(url)
        assert response.status_code == get_requests_get_response().status_code
        assert response._content == get_requests_get_response()._content

    def test_run_health_check_container_exited_raises_exception(
        self,
        run_prediction_container_mock,
        requests_get_mock,
    ):
        endpoint = LocalEndpoint(
            _TEST_IMAGE_URI,
        )
        endpoint.container_exited = True
        expected_message = (
            "The local endpoint is not serving traffic. Please call `serve()`."
        )

        with pytest.raises(RuntimeError) as exception:
            endpoint.run_health_check()

        assert str(exception.value) == expected_message

    def test_run_health_check_raises_exception(
        self,
        local_endpoint_logger_mock,
        run_prediction_container_mock,
        requests_get_second_raises_exception_mock,
    ):
        serving_container_health_route = "/custom_health"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_health_route}"

        with pytest.raises(requests.exceptions.RequestException) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_health_route=serving_container_health_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.run_health_check()

        requests_get_second_raises_exception_mock.assert_called_with(url)
        assert local_endpoint_logger_mock.warning.called
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_run_health_check_raises_exception_not_verbose(
        self,
        local_endpoint_logger_mock,
        run_prediction_container_mock,
        requests_get_second_raises_exception_mock,
    ):
        serving_container_health_route = "/custom_health"
        host_port = 8080
        url = f"http://localhost:{host_port}{serving_container_health_route}"

        with pytest.raises(requests.exceptions.RequestException) as exception:
            with LocalEndpoint(
                _TEST_IMAGE_URI,
                serving_container_health_route=serving_container_health_route,
                host_port=host_port,
            ) as endpoint:
                endpoint.run_health_check(verbose=False)

        requests_get_second_raises_exception_mock.assert_called_with(url)
        assert not local_endpoint_logger_mock.warning.called
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_print_container_logs(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        run_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs()

        run_print_container_logs_mock.assert_called_once_with(
            run_prediction_container_mock(), start_index=0, message=None
        )

    def test_print_container_logs_show_all(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        run_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs(show_all=True)

        run_print_container_logs_mock.assert_called_once_with(
            run_prediction_container_mock(), start_index=None, message=None
        )

    def test_print_container_logs_if_container_is_not_running_container_running(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        get_container_status_running_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running()

        assert get_container_status_running_mock.called
        assert not local_endpoint_print_container_logs_mock.called

    def test_print_container_logs_if_container_is_not_running_container_exited(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        get_container_status_second_fail_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running()

        local_endpoint_print_container_logs_mock.assert_called_once_with(
            show_all=False, message=None
        )

    def test_print_container_logs_if_container_is_not_running_container_exited_show_all(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
        get_container_status_second_fail_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running(show_all=True)

        local_endpoint_print_container_logs_mock.assert_called_once_with(
            show_all=True, message=None
        )

    def test_get_container_status(
        self,
        run_prediction_container_mock,
        local_endpoint_run_health_check_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            status = endpoint.get_container_status()

        assert run_prediction_container_mock().reload.called
        assert status == _CONTAINER_RUNNING_STATUS


class TestModelServer:
    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
            "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
            "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
            "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
        },
        clear=True,
    )
    def test_init(
        self,
        importlib_import_module_mock_once,
        fastapi_mock,
    ):
        model_server = CprModelServer()

        importlib_import_module_mock_once.assert_called_once_with(
            _DEFAULT_HANDLER_MODULE
        )
        getattr(
            importlib_import_module_mock_once.return_value, _DEFAULT_HANDLER_CLASS
        ).assert_called_once_with(_TEST_AIP_STORAGE_URI, predictor=None)
        assert (
            model_server.handler
            == getattr(
                importlib_import_module_mock_once.return_value, _DEFAULT_HANDLER_CLASS
            ).return_value
        )
        assert model_server.http_port == int(_TEST_AIP_HTTP_PORT)
        assert model_server.health_route == _TEST_AIP_HEALTH_ROUTE
        assert model_server.predict_route == _TEST_AIP_PREDICT_ROUTE
        fastapi_mock.return_value.add_api_route.assert_has_calls(
            [
                mock.call(
                    path=_TEST_AIP_HEALTH_ROUTE,
                    endpoint=model_server.health,
                    methods=["GET"],
                )
            ],
            [
                mock.call(
                    path=_TEST_AIP_PREDICT_ROUTE,
                    endpoint=model_server.predict,
                    methods=["POST"],
                )
            ],
        )

    def test_init_with_predictor(
        self,
        model_server_env_mock,
        importlib_import_module_mock_twice,
        fastapi_mock,
    ):
        model_server = CprModelServer()

        importlib_import_module_mock_twice.assert_has_calls(
            [
                mock.call(_DEFAULT_HANDLER_MODULE),
                mock.call(f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}"),
            ]
        )
        getattr(
            importlib_import_module_mock_twice(_DEFAULT_HANDLER_MODULE),
            _DEFAULT_HANDLER_CLASS,
        ).assert_called_once_with(
            _TEST_AIP_STORAGE_URI,
            predictor=getattr(
                importlib_import_module_mock_twice(
                    f"{_TEST_SRC_DIR}.{_TEST_PREDICTOR_FILE_STEM}"
                ),
                _TEST_PREDICTOR_CLASS,
            ),
        )
        assert (
            model_server.handler
            == getattr(
                importlib_import_module_mock_twice(_DEFAULT_HANDLER_MODULE),
                _DEFAULT_HANDLER_CLASS,
            ).return_value
        )
        assert model_server.http_port == int(_TEST_AIP_HTTP_PORT)
        assert model_server.health_route == _TEST_AIP_HEALTH_ROUTE
        assert model_server.predict_route == _TEST_AIP_PREDICT_ROUTE
        fastapi_mock.return_value.add_api_route.assert_has_calls(
            [
                mock.call(
                    path=_TEST_AIP_HEALTH_ROUTE,
                    endpoint=model_server.health,
                    methods=["GET"],
                )
            ],
            [
                mock.call(
                    path=_TEST_AIP_PREDICT_ROUTE,
                    endpoint=model_server.predict,
                    methods=["POST"],
                )
            ],
        )

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
            "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
            "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
        },
        clear=True,
    )
    def test_init_fails_no_handler_module(
        self,
    ):
        expected_message = (
            "Both of the environment variables, HANDLER_MODULE and HANDLER_CLASS "
            "need to be specified."
        )

        with pytest.raises(ValueError) as exception:
            _ = CprModelServer()

        assert str(exception.value) == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
            "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
            "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
        },
        clear=True,
    )
    def test_init_fails_no_handler_class(
        self,
    ):
        expected_message = (
            "Both of the environment variables, HANDLER_MODULE and HANDLER_CLASS "
            "need to be specified."
        )

        with pytest.raises(ValueError) as exception:
            _ = CprModelServer()

        assert str(exception.value) == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
            "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
            "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
            "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
        },
        clear=True,
    )
    def test_init_no_aip_http_port(
        self,
        importlib_import_module_mock_once,
    ):
        expected_message = (
            "The environment variable AIP_HTTP_PORT needs to be specified."
        )

        with pytest.raises(ValueError) as exception:
            _ = CprModelServer()

        assert str(exception.value) == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
            "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
            "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
            "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
        },
        clear=True,
    )
    def test_init_no_aip_health_route(
        self,
        importlib_import_module_mock_once,
    ):
        expected_message = (
            "Both of the environment variables AIP_HEALTH_ROUTE and "
            "AIP_PREDICT_ROUTE need to be specified."
        )

        with pytest.raises(ValueError) as exception:
            _ = CprModelServer()

        assert str(exception.value) == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
            "AIP_STORAGE_URI": _TEST_AIP_STORAGE_URI,
            "HANDLER_MODULE": _DEFAULT_HANDLER_MODULE,
            "HANDLER_CLASS": _DEFAULT_HANDLER_CLASS,
        },
        clear=True,
    )
    def test_init_no_aip_predict_route(
        self,
        importlib_import_module_mock_once,
    ):
        expected_message = (
            "Both of the environment variables AIP_HEALTH_ROUTE and "
            "AIP_PREDICT_ROUTE need to be specified."
        )

        with pytest.raises(ValueError) as exception:
            _ = CprModelServer()

        assert str(exception.value) == expected_message

    def test_health(self, model_server_env_mock, importlib_import_module_mock_twice):
        model_server = CprModelServer()
        client = TestClient(model_server.app)

        response = client.get(_TEST_AIP_HEALTH_ROUTE)

        assert response.status_code == 200

    def test_predict(self, model_server_env_mock, importlib_import_module_mock_twice):
        model_server = CprModelServer()
        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            future = asyncio.Future()
            future.set_result(Response())

            handle_mock.return_value = future

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert response.status_code == 200

    def test_predict_thorws_http_exception(
        self, model_server_env_mock, importlib_import_module_mock_twice
    ):
        expected_message = "A fake HTTP exception."
        model_server = CprModelServer()
        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            handle_mock.side_effect = HTTPException(
                status_code=400,
                detail=expected_message,
            )

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert response.status_code == 400
        assert json.loads(response.content)["detail"] == expected_message

    def test_predict_thorws_exceptions_not_http_exception_default_handler(
        self, model_server_env_mock, importlib_import_module_mock_twice
    ):
        expected_message = (
            "An exception ValueError occurred. Arguments: ('Not a correct value.',)."
        )
        model_server = CprModelServer()
        model_server.is_default_handler = True
        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            handle_mock.side_effect = ValueError("Not a correct value.")

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert (
            prediction.CUSTOM_PREDICTION_ROUTINES_SERVER_ERROR_HEADER_KEY
            in response.headers
        )
        assert response.status_code == 500
        assert json.loads(response.content)["detail"] == expected_message

    def test_predict_thorws_exceptions_not_http_exception_not_default_handler(
        self, model_server_env_mock, importlib_import_module_mock_twice
    ):
        expected_message = (
            "An exception ValueError occurred. Arguments: ('Not a correct value.',)."
        )
        model_server = CprModelServer()
        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            handle_mock.side_effect = ValueError("Not a correct value.")

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert (
            prediction.CUSTOM_PREDICTION_ROUTINES_SERVER_ERROR_HEADER_KEY
            not in response.headers
        )
        assert response.status_code == 500
        assert json.loads(response.content)["detail"] == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "VERTEX_CPR_WEB_CONCURRENCY": "8",
        },
        clear=True,
    )
    def test_set_number_of_workers_from_env_web_concurrency(self):
        model_server_module.set_number_of_workers_from_env()

        assert os.getenv("WEB_CONCURRENCY") == "8"

    @mock.patch.dict(
        os.environ,
        {},
        clear=True,
    )
    def test_set_number_of_workers_from_env_default_workers_per_core(
        self, cpu_count_mock
    ):
        model_server_module.set_number_of_workers_from_env()

        assert os.getenv("WEB_CONCURRENCY") == str(
            cpu_count_mock.return_value * _DEFAULT_WORKERS_PER_CORE
        )

    @mock.patch.dict(
        os.environ,
        {"VERTEX_CPR_WORKERS_PER_CORE": "2"},
        clear=True,
    )
    def test_set_number_of_workers_from_env_with_workers_per_core(self, cpu_count_mock):
        model_server_module.set_number_of_workers_from_env()

        assert os.getenv("WEB_CONCURRENCY") == str(cpu_count_mock.return_value * 2)

    @mock.patch.dict(
        os.environ,
        {"VERTEX_CPR_MAX_WORKERS": "4"},
        clear=True,
    )
    def test_set_number_of_workers_from_env_max_workers(self, cpu_count_mock):
        number_of_workers = min(
            4, cpu_count_mock.return_value * _DEFAULT_WORKERS_PER_CORE
        )

        model_server_module.set_number_of_workers_from_env()

        assert os.getenv("WEB_CONCURRENCY") == str(number_of_workers)
