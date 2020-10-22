# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

from unittest import mock

import grpc
import math
import pytest

from google import auth
from google.api_core import client_options
from google.auth import credentials
from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    PredictionServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.prediction_service import transports
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import prediction_service
from google.oauth2 import service_account
from google.protobuf import struct_pb2 as struct  # type: ignore


def test_prediction_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = PredictionServiceClient.from_service_account_file(
            "dummy/file/path.json"
        )
        assert client._transport._credentials == creds

        client = PredictionServiceClient.from_service_account_json(
            "dummy/file/path.json"
        )
        assert client._transport._credentials == creds

        assert client._transport._host == "aiplatform.googleapis.com:443"


def test_prediction_service_client_client_options():
    # Check the default options have their expected values.
    assert (
        PredictionServiceClient.DEFAULT_OPTIONS.api_endpoint
        == "aiplatform.googleapis.com"
    )

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.prediction_service.PredictionServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = PredictionServiceClient(client_options=options)
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_prediction_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.prediction_service.PredictionServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = PredictionServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_predict(transport: str = "grpc"):
    client = PredictionServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = prediction_service.PredictRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.predict), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = prediction_service.PredictResponse(
            deployed_model_id="deployed_model_id_value",
        )

        response = client.predict(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, prediction_service.PredictResponse)
    assert response.deployed_model_id == "deployed_model_id_value"


def test_predict_flattened():
    client = PredictionServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.predict), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = prediction_service.PredictResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.predict(
            endpoint="endpoint_value",
            instances=[struct.Value(null_value=struct.NullValue.NULL_VALUE)],
            parameters=struct.Value(null_value=struct.NullValue.NULL_VALUE),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].endpoint == "endpoint_value"
        assert args[0].instances == [
            struct.Value(null_value=struct.NullValue.NULL_VALUE)
        ]
        # https://github.com/googleapis/gapic-generator-python/issues/414
        # assert args[0].parameters == struct.Value(
        #     null_value=struct.NullValue.NULL_VALUE
        # )


def test_predict_flattened_error():
    client = PredictionServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.predict(
            prediction_service.PredictRequest(),
            endpoint="endpoint_value",
            instances=[struct.Value(null_value=struct.NullValue.NULL_VALUE)],
            parameters=struct.Value(null_value=struct.NullValue.NULL_VALUE),
        )


def test_explain(transport: str = "grpc"):
    client = PredictionServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = prediction_service.ExplainRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.explain), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = prediction_service.ExplainResponse(
            deployed_model_id="deployed_model_id_value",
        )

        response = client.explain(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, prediction_service.ExplainResponse)
    assert response.deployed_model_id == "deployed_model_id_value"


def test_explain_flattened():
    client = PredictionServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.explain), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = prediction_service.ExplainResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.explain(
            endpoint="endpoint_value",
            instances=[struct.Value(null_value=struct.NullValue.NULL_VALUE)],
            parameters=struct.Value(null_value=struct.NullValue.NULL_VALUE),
            deployed_model_id="deployed_model_id_value",
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].endpoint == "endpoint_value"
        assert args[0].instances == [
            struct.Value(null_value=struct.NullValue.NULL_VALUE)
        ]
        # https://github.com/googleapis/gapic-generator-python/issues/414
        # assert args[0].parameters == struct.Value(
        #     null_value=struct.NullValue.NULL_VALUE
        # )
        assert args[0].deployed_model_id == "deployed_model_id_value"


def test_explain_flattened_error():
    client = PredictionServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.explain(
            prediction_service.ExplainRequest(),
            endpoint="endpoint_value",
            instances=[struct.Value(null_value=struct.NullValue.NULL_VALUE)],
            parameters=struct.Value(null_value=struct.NullValue.NULL_VALUE),
            deployed_model_id="deployed_model_id_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.PredictionServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = PredictionServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.PredictionServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = PredictionServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = PredictionServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.PredictionServiceGrpcTransport,)


def test_prediction_service_base_transport():
    # Instantiate the base transport.
    transport = transports.PredictionServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "predict",
        "explain",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())


def test_prediction_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        PredictionServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_prediction_service_host_no_port():
    client = PredictionServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:443"


def test_prediction_service_host_with_port():
    client = PredictionServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:8000"


def test_prediction_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")
    transport = transports.PredictionServiceGrpcTransport(channel=channel,)
    assert transport.grpc_channel is channel
