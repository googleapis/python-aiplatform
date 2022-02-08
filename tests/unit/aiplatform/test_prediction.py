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
import json
import os
import pytest
from unittest import mock

from fastapi import HTTPException
from fastapi import Request
from fastapi import Response
from starlette.datastructures import Headers
from starlette.testclient import TestClient

from google.cloud.aiplatform.prediction.handler import Handler
from google.cloud.aiplatform.prediction.handler import PredictionHandler
from google.cloud.aiplatform.prediction.model_server import ModelServer
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.prediction.serializer import DefaultSerializer


_TEST_INPUT = b'{"instances": [[1, 2, 3, 4]]}'
_TEST_DESERIALIZED_INPUT = {"instances": [[1, 2, 3, 4]]}
_TEST_PREDICTION_OUTPUT = {"predictions": [[1]]}
_TEST_SERIALIZED_OUTPUT = b'{"predictions": [[1]]}'
_APPLICATION_JSON = "application/json"
_TEST_GCS_ARTIFACTS_URI = ""

_TEST_AIP_HTTP_PORT = "8080"
_TEST_AIP_HEALTH_ROUTE = "/health"
_TEST_AIP_PREDICT_ROUTE = "/predict"


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
