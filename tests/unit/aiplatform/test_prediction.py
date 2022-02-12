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
import os
import pytest
import requests
import textwrap
from unittest import mock

from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from starlette.datastructures import Headers
from starlette.testclient import TestClient

from google.api_core import operation as ga_operation

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import helpers
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.compat.types import model as gca_model_compat
from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.docker_utils import build
from google.cloud.aiplatform.docker_utils import run
from google.cloud.aiplatform.prediction import DEFAULT_HEALTH_ROUTE
from google.cloud.aiplatform.prediction import DEFAULT_HTTP_PORT
from google.cloud.aiplatform.prediction import DEFAULT_PREDICT_ROUTE
from google.cloud.aiplatform.prediction import LocalEndpoint
from google.cloud.aiplatform.prediction import LocalModel
from google.cloud.aiplatform.prediction import handler_utils
from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.model_server import ModelServer
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.prediction.serializer import DefaultSerializer
from google.cloud.aiplatform.utils import prediction_utils

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform.compat.types import (
    model as gca_model,
    env_var as gca_env_var,
    model_service as gca_model_service,
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

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_MODEL_NAME = "test-model"
_TEST_ARTIFACT_URI = "gs://test/artifact/uri"
_TEST_SERVING_CONTAINER_IMAGE = "gcr.io/test-serving/container:image"
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = "metadata"
_TEST_DESCRIPTION = "test description"
_TEST_SERVING_CONTAINER_COMMAND = ["python3", "run_my_model.py"]
_TEST_SERVING_CONTAINER_ARGS = ["--test", "arg"]
_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES = {
    "learning_rate": 0.01,
    "loss_fn": "mse",
}
_TEST_SERVING_CONTAINER_PORTS = [8888, 10000]
_TEST_ID = "1028944691210842416"
_TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}

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

_DEFAULT_BASE_IMAGE = "python:3.7"
_ENTRYPOINT_FILE = "entrypoint.py"
_TEST_SRC_DIR = "user_code"
_TEST_PREDICTOR_FILE = "predictor.py"
_TEST_OUTPUT_IMAGE = "cpr_image:latest"

_TEST_IMAGE_URI = "test_image:latest"
_TEST_PREDICT_RESPONSE_CONTENT = b'{"x": [[1]]}'
_TEST_HEALTH_CHECK_RESPONSE_CONTENT = b"{}"
_TEST_HTTP_ERROR_MESSAGE = "HTTP Error Occurred."
_TEST_CONTAINER_LOGS_LEN = 5
_CONTAINER_RUNNING_STATUS = "running"
_CONTAINER_EXITED_STATUS = "exited"


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
        deserialize_exception_mock.side_effect = HTTPException(status_code=400,)
        yield deserialize_exception_mock


@pytest.fixture
def serialize_mock():
    with mock.patch.object(DefaultSerializer, "serialize") as serialize_mock:
        serialize_mock.return_value = _TEST_SERIALIZED_OUTPUT
        yield serialize_mock


@pytest.fixture
def serialize_exception_mock():
    with mock.patch.object(DefaultSerializer, "serialize") as serialize_exception_mock:
        serialize_exception_mock.side_effect = HTTPException(status_code=400,)
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
    }
    with mock.patch.dict(os.environ, env_vars):
        yield


def get_test_request():
    async def _create_request_receive():
        return {
            "type": "http.request",
            "body": _TEST_INPUT,
            "more_body": False,
        }

    return Request(
        scope={
            "type": "http",
            "headers": Headers(
                {"content-type": _APPLICATION_JSON, "accept": _APPLICATION_JSON}
            ).raw,
        },
        receive=_create_request_receive,
    )


def get_test_predictor():
    class _TestPredictor(Predictor):
        def __init__(self):
            pass

        def load(self, gcs_artifacts_uri):
            pass

        def predict(self, instances):
            pass

    return _TestPredictor


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
def upload_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


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


def get_docker_container_mock():
    container = mock.MagicMock()
    return container


@pytest.fixture
def run_prediction_container_mock():
    with mock.patch.object(
        run, "run_prediction_container"
    ) as run_prediction_container_mock:
        run_prediction_container_mock.return_value = get_docker_container_mock()
        yield run_prediction_container_mock


@pytest.fixture
def run_prediction_container_with_running_status_mock():
    with mock.patch.object(
        run, "run_prediction_container"
    ) as run_prediction_container_with_running_status_mock:
        run_prediction_container_with_running_status_mock.return_value = (
            get_docker_container_mock()
        )
        run_prediction_container_with_running_status_mock().status = (
            _CONTAINER_RUNNING_STATUS
        )
        yield run_prediction_container_with_running_status_mock


@pytest.fixture
def run_print_container_logs_mock():
    with mock.patch.object(
        run, "print_container_logs"
    ) as run_print_container_logs_mock:
        run_print_container_logs_mock.return_value = _TEST_CONTAINER_LOGS_LEN
        yield run_print_container_logs_mock


@pytest.fixture
def get_container_status_running_mock():
    with mock.patch.object(
        LocalEndpoint, "get_container_status"
    ) as get_container_status_running_mock:
        get_container_status_running_mock.return_value = _CONTAINER_RUNNING_STATUS
        yield get_container_status_running_mock


@pytest.fixture
def get_container_status_exited_mock():
    with mock.patch.object(
        LocalEndpoint, "get_container_status"
    ) as get_container_status_exited_mock:
        get_container_status_exited_mock.return_value = _CONTAINER_EXITED_STATUS
        yield get_container_status_exited_mock


@pytest.fixture
def local_endpoint_print_container_logs_mock():
    with mock.patch.object(
        LocalEndpoint, "print_container_logs"
    ) as local_endpoint_print_container_logs_mock:
        yield local_endpoint_print_container_logs_mock


@pytest.fixture
def wait_until_container_runs_mock():
    with mock.patch.object(
        LocalEndpoint, "_wait_until_container_runs"
    ) as wait_until_container_runs_mock:
        yield wait_until_container_runs_mock


@pytest.fixture
def wait_until_health_check_succeeds_mock():
    with mock.patch.object(
        LocalEndpoint, "_wait_until_health_check_succeeds"
    ) as wait_until_health_check_succeeds_mock:
        yield wait_until_health_check_succeeds_mock


@pytest.fixture
def stop_container_if_exists_mock():
    with mock.patch.object(
        LocalEndpoint, "_stop_container_if_exists"
    ) as stop_container_if_exists_mock:
        yield stop_container_if_exists_mock


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
def requests_get_raises_exception_mock():
    with mock.patch.object(requests, "get") as requests_get_raises_exception_mock:
        requests_get_raises_exception_mock.side_effect = requests.exceptions.HTTPError(
            _TEST_HTTP_ERROR_MESSAGE
        )
        yield requests_get_raises_exception_mock


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
    async def test_handle(self, deserialize_mock, predictor_mock, serialize_mock):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        response = await handler.handle(get_test_request())

        assert response.status_code == 200
        assert response.body == _TEST_SERIALIZED_OUTPUT

        deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
        predictor_mock().preprocess.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().predict.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().postprocess.assert_called_once_with(_TEST_PREDICTION_OUTPUT)
        serialize_mock.assert_called_once_with(
            _TEST_SERIALIZED_OUTPUT, _APPLICATION_JSON
        )

    @pytest.mark.asyncio
    async def test_handle_deserialize_raises_exception(
        self, deserialize_exception_mock, predictor_mock, serialize_mock
    ):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        with pytest.raises(HTTPException):
            await handler.handle(get_test_request())

        deserialize_exception_mock.assert_called_once_with(
            _TEST_INPUT, _APPLICATION_JSON
        )
        assert not predictor_mock().preprocess.called
        assert not predictor_mock().predict.called
        assert not predictor_mock().postprocess.called
        assert not serialize_mock.called

    @pytest.mark.asyncio
    async def test_handle_predictor_raises_exception(
        self, deserialize_mock, serialize_mock
    ):
        preprocess_mock = mock.MagicMock(return_value=_TEST_DESERIALIZED_INPUT)
        predict_mock = mock.MagicMock(side_effect=Exception())
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
            with pytest.raises(Exception):
                await handler.handle(get_test_request())

            deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
            preprocess_mock.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
            predict_mock.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
            assert not postprocess_mock.called
            assert not serialize_mock.called

    @pytest.mark.asyncio
    async def test_handle_serialize_raises_exception(
        self, deserialize_mock, predictor_mock, serialize_exception_mock
    ):
        handler = PredictionHandler(_TEST_GCS_ARTIFACTS_URI, predictor=predictor_mock)

        with pytest.raises(HTTPException):
            await handler.handle(get_test_request())

        deserialize_mock.assert_called_once_with(_TEST_INPUT, _APPLICATION_JSON)
        predictor_mock().preprocess.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().predict.assert_called_once_with(_TEST_DESERIALIZED_INPUT)
        predictor_mock().postprocess.assert_called_once_with(_TEST_PREDICTION_OUTPUT)
        serialize_exception_mock.assert_called_once_with(
            _TEST_SERIALIZED_OUTPUT, _APPLICATION_JSON
        )


class TestHandlerUtils:
    @pytest.mark.parametrize(
        "header_keys",
        [
            "Content-Type",
            "content-Type",
            "content-type",
            "Content-type",
            "ContentType",
            "contentType",
            "contenttype",
            "Contenttype",
        ],
    )
    def test_get_content_type_from_headers(self, header_keys):
        expected_content_type = "content_type"
        headers = Headers({header_keys: expected_content_type})

        content_type = handler_utils.get_content_type_from_headers(headers)

        assert content_type == expected_content_type

    def test_get_content_type_from_headers_no_headers(self):
        headers = Headers({})

        content_type = handler_utils.get_content_type_from_headers(headers)

        assert content_type is None

    def test_get_content_type_from_headers_none(self):
        content_type = handler_utils.get_content_type_from_headers(None)

        assert content_type is None

    @pytest.mark.parametrize("header_keys", ["Accept", "accept"])
    def test_get_accept_from_headers(self, header_keys):
        expected_accept = "accept"
        headers = Headers({header_keys: expected_accept})

        accept = handler_utils.get_accept_from_headers(headers)

        assert accept == expected_accept

    def test_get_accept_from_headers_no_headers(self):
        headers = Headers({})

        accept = handler_utils.get_accept_from_headers(headers)

        assert accept == handler_utils.DEFAULT_ACCEPT

    def test_get_accept_from_headers_accept_is_any(self):
        headers = Headers({"Accept": handler_utils.ANY})

        accept = handler_utils.get_accept_from_headers(headers)

        assert accept == handler_utils.DEFAULT_ACCEPT

    def test_get_accept_from_headers_none(self):
        accept = handler_utils.get_accept_from_headers(None)

        assert accept == handler_utils.DEFAULT_ACCEPT


class TestModelServer:
    def test_init(self, model_server_env_mock):
        model_server = ModelServer(Handler(_TEST_GCS_ARTIFACTS_URI))

        assert model_server.http_port == int(_TEST_AIP_HTTP_PORT)
        assert model_server.health_route == _TEST_AIP_HEALTH_ROUTE
        assert model_server.predict_route == _TEST_AIP_PREDICT_ROUTE

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
        },
    )
    def test_init_raises_exception_without_port(self):
        expected_message = (
            "The environment variable AIP_HTTP_PORT needs to be specified."
        )

        with pytest.raises(ValueError) as exception:
            ModelServer(Handler(_TEST_GCS_ARTIFACTS_URI))

        assert str(exception.value) == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_PREDICT_ROUTE": _TEST_AIP_PREDICT_ROUTE,
        },
    )
    def test_init_raises_exception_without_health_route(self):
        expected_message = (
            "Both of the environment variables AIP_HEALTH_ROUTE and "
            "AIP_PREDICT_ROUTE need to be specified."
        )

        with pytest.raises(ValueError) as exception:
            ModelServer(Handler(_TEST_GCS_ARTIFACTS_URI))

        assert str(exception.value) == expected_message

    @mock.patch.dict(
        os.environ,
        {
            "AIP_HTTP_PORT": _TEST_AIP_HTTP_PORT,
            "AIP_HEALTH_ROUTE": _TEST_AIP_HEALTH_ROUTE,
        },
    )
    def test_init_raises_exception_without_predict_route(self):
        expected_message = (
            "Both of the environment variables AIP_HEALTH_ROUTE and "
            "AIP_PREDICT_ROUTE need to be specified."
        )

        with pytest.raises(ValueError) as exception:
            ModelServer(Handler(_TEST_GCS_ARTIFACTS_URI))

        assert str(exception.value) == expected_message

    def test_health(self, model_server_env_mock):
        model_server = ModelServer(Handler(_TEST_GCS_ARTIFACTS_URI))
        client = TestClient(model_server.app)

        response = client.get(_TEST_AIP_HEALTH_ROUTE)

        assert response.status_code == 200

    def test_predict(self, model_server_env_mock):
        handler = PredictionHandler(
            _TEST_GCS_ARTIFACTS_URI, predictor=get_test_predictor()
        )
        model_server = ModelServer(handler)

        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            future = asyncio.Future()
            future.set_result(Response())

            handle_mock.return_value = future

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert response.status_code == 200

    def test_predict_handler_throws_http_exception(self, model_server_env_mock):
        expected_message = "A test HTTP exception."
        handler = PredictionHandler(
            _TEST_GCS_ARTIFACTS_URI, predictor=get_test_predictor()
        )
        model_server = ModelServer(handler)

        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            handle_mock.side_effect = HTTPException(
                status_code=400, detail=expected_message
            )

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert response.status_code == 400
        assert json.loads(response.content)["detail"] == expected_message

    def test_predict_handler_throws_exception_other_than_http_exception(
        self, model_server_env_mock
    ):
        expected_message = (
            "An exception ValueError occurred. Arguments: ('Not a correct value.',)."
        )
        handler = PredictionHandler(
            _TEST_GCS_ARTIFACTS_URI, predictor=get_test_predictor()
        )
        model_server = ModelServer(handler)

        client = TestClient(model_server.app)

        with mock.patch.object(model_server.handler, "handle") as handle_mock:
            handle_mock.side_effect = ValueError("Not a correct value.")

            response = client.post(_TEST_AIP_PREDICT_ROUTE, json={"x": [1]})

        assert response.status_code == 500
        assert json.loads(response.content)["detail"] == expected_message


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

    def test_create_creates_and_gets_localmodel(self):
        local_model = LocalModel.create(
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
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

    def test_create_creates_and_gets_localmodel_with_all_args(self):
        local_model = LocalModel.create(
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            serving_container_command=_TEST_SERVING_CONTAINER_COMMAND,
            serving_container_args=_TEST_SERVING_CONTAINER_ARGS,
            serving_container_environment_variables=_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            serving_container_ports=_TEST_SERVING_CONTAINER_PORTS,
        )

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_PORTS
        ]

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_SERVING_CONTAINER_COMMAND,
            args=_TEST_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
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

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model(
        self, upload_model_mock, get_model_mock, sync
    ):

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        local_model = LocalModel(container_spec)

        my_model = local_model.upload(display_name=_TEST_MODEL_NAME, sync=sync,)

        if not sync:
            my_model.wait()

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME, container_spec=container_spec,
        )

        upload_model_mock.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            model=managed_model,
        )

        get_model_mock.assert_called_once_with(
            name=_TEST_MODEL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_all_args(
        self, upload_model_mock, get_model_mock, sync
    ):

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
            for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
        ]

        ports = [
            gca_model.Port(container_port=port)
            for port in _TEST_SERVING_CONTAINER_PORTS
        ]

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            command=_TEST_SERVING_CONTAINER_COMMAND,
            args=_TEST_SERVING_CONTAINER_ARGS,
            env=env,
            ports=ports,
        )

        local_model = LocalModel(container_spec)

        my_model = local_model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            instance_schema_uri=_TEST_INSTANCE_SCHEMA_URI,
            parameters_schema_uri=_TEST_PARAMETERS_SCHEMA_URI,
            prediction_schema_uri=_TEST_PREDICTION_SCHEMA_URI,
            description=_TEST_DESCRIPTION,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            labels=_TEST_LABEL,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            description=_TEST_DESCRIPTION,
            artifact_uri=_TEST_ARTIFACT_URI,
            container_spec=container_spec,
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_PREDICTION_SCHEMA_URI,
            ),
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
        )

        upload_model_mock.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            model=managed_model,
        )
        get_model_mock.assert_called_once_with(
            name=_TEST_MODEL_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

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
            _TEST_SRC_DIR,
            _ENTRYPOINT_FILE,
            predictor=my_predictor,
            handler=PredictionHandler,
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
            _TEST_SRC_DIR,
            _ENTRYPOINT_FILE,
            predictor=my_predictor,
            handler=PredictionHandler,
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
            _TEST_SRC_DIR,
            _ENTRYPOINT_FILE,
            predictor=my_predictor,
            handler=PredictionHandler,
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

    def test_deploy_to_local_endpoint(
        self,
        local_endpoint_init_mock,
        local_endpoint_enter_mock,
        local_endpoint_exit_mock,
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
            container_ready_timeout=container_ready_timeout,
            container_ready_check_interval=container_ready_check_interval,
        )
        assert local_endpoint_enter_mock.called
        assert local_endpoint_exit_mock.called


class TestLocalEndpoint:
    def test_init(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
            serving_container_environment_variables=None,
            serving_container_ports=None,
            credential_path=None,
            host_port=None,
        )
        wait_until_container_runs_mock.assert_called_once_with()
        wait_until_health_check_succeeds_mock.assert_called_once_with()
        stop_container_if_exists_mock.assert_called_once_with()

    def test_init_with_all_parameters(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        )
        wait_until_container_runs_mock.assert_called_once_with()
        wait_until_health_check_succeeds_mock.assert_called_once_with()
        stop_container_if_exists_mock.assert_called_once_with()

    def test_predict_request(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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

    def test_predict_both_request_and_request_file_specified_raises_exception(
        self,
        tmp_path,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_run_health_check(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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

        requests_get_mock.assert_called_once_with(url)
        assert response.status_code == get_requests_get_response().status_code
        assert response._content == get_requests_get_response()._content

    def test_run_health_check_raises_exception(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        requests_get_raises_exception_mock,
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

        requests_get_raises_exception_mock.assert_called_once_with(url)
        assert str(exception.value) == _TEST_HTTP_ERROR_MESSAGE

    def test_print_container_logs(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        run_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs()

        run_print_container_logs_mock.assert_called_once_with(
            run_prediction_container_mock(), start_index=0
        )

    def test_print_container_logs_show_all(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        run_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs(show_all=True)

        run_print_container_logs_mock.assert_called_once_with(
            run_prediction_container_mock(), start_index=None
        )

    def test_print_container_logs_if_container_is_not_running_container_running(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
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
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        get_container_status_exited_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running()

        assert get_container_status_exited_mock.called
        local_endpoint_print_container_logs_mock.assert_called_once_with(show_all=False)

    def test_print_container_logs_if_container_is_not_running_container_exited_show_all(
        self,
        run_prediction_container_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
        get_container_status_exited_mock,
        local_endpoint_print_container_logs_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            endpoint.print_container_logs_if_container_is_not_running(show_all=True)

        assert get_container_status_exited_mock.called
        local_endpoint_print_container_logs_mock.assert_called_once_with(show_all=True)

    def test_get_container_status(
        self,
        run_prediction_container_with_running_status_mock,
        wait_until_container_runs_mock,
        wait_until_health_check_succeeds_mock,
        stop_container_if_exists_mock,
    ):
        with LocalEndpoint(_TEST_IMAGE_URI) as endpoint:
            status = endpoint.get_container_status()

        assert run_prediction_container_with_running_status_mock().reload.called
        assert status == _CONTAINER_RUNNING_STATUS
