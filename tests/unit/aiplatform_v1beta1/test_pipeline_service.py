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
from google.api_core import future
from google.api_core import operations_v1
from google.auth import credentials
from google.cloud.aiplatform_v1beta1.services.pipeline_service import (
    PipelineServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.pipeline_service import pagers
from google.cloud.aiplatform_v1beta1.services.pipeline_service import transports
from google.cloud.aiplatform_v1beta1.types import deployed_model_ref
from google.cloud.aiplatform_v1beta1.types import env_var
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import explanation_metadata
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import model
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import pipeline_service
from google.cloud.aiplatform_v1beta1.types import pipeline_state
from google.cloud.aiplatform_v1beta1.types import training_pipeline
from google.cloud.aiplatform_v1beta1.types import (
    training_pipeline as gca_training_pipeline,
)
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import any_pb2 as any  # type: ignore
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.rpc import status_pb2 as status  # type: ignore


def test_pipeline_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = PipelineServiceClient.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = PipelineServiceClient.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "aiplatform.googleapis.com:443"


def test_pipeline_service_client_client_options():
    # Check the default options have their expected values.
    assert (
        PipelineServiceClient.DEFAULT_OPTIONS.api_endpoint
        == "aiplatform.googleapis.com"
    )

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.pipeline_service.PipelineServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = PipelineServiceClient(client_options=options)
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_pipeline_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.pipeline_service.PipelineServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = PipelineServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_create_training_pipeline(transport: str = "grpc"):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = pipeline_service.CreateTrainingPipelineRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_training_pipeline.TrainingPipeline(
            name="name_value",
            display_name="display_name_value",
            training_task_definition="training_task_definition_value",
            state=pipeline_state.PipelineState.PIPELINE_STATE_QUEUED,
        )

        response = client.create_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_training_pipeline.TrainingPipeline)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.training_task_definition == "training_task_definition_value"
    assert response.state == pipeline_state.PipelineState.PIPELINE_STATE_QUEUED


def test_create_training_pipeline_flattened():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.create_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_training_pipeline.TrainingPipeline()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_training_pipeline(
            parent="parent_value",
            training_pipeline=gca_training_pipeline.TrainingPipeline(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].training_pipeline == gca_training_pipeline.TrainingPipeline(
            name="name_value"
        )


def test_create_training_pipeline_flattened_error():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_training_pipeline(
            pipeline_service.CreateTrainingPipelineRequest(),
            parent="parent_value",
            training_pipeline=gca_training_pipeline.TrainingPipeline(name="name_value"),
        )


def test_get_training_pipeline(transport: str = "grpc"):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = pipeline_service.GetTrainingPipelineRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = training_pipeline.TrainingPipeline(
            name="name_value",
            display_name="display_name_value",
            training_task_definition="training_task_definition_value",
            state=pipeline_state.PipelineState.PIPELINE_STATE_QUEUED,
        )

        response = client.get_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, training_pipeline.TrainingPipeline)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.training_task_definition == "training_task_definition_value"
    assert response.state == pipeline_state.PipelineState.PIPELINE_STATE_QUEUED


def test_get_training_pipeline_field_headers():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.GetTrainingPipelineRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_training_pipeline), "__call__"
    ) as call:
        call.return_value = training_pipeline.TrainingPipeline()
        client.get_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_training_pipeline_flattened():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = training_pipeline.TrainingPipeline()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_training_pipeline(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_training_pipeline_flattened_error():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_training_pipeline(
            pipeline_service.GetTrainingPipelineRequest(), name="name_value",
        )


def test_list_training_pipelines(transport: str = "grpc"):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = pipeline_service.ListTrainingPipelinesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_training_pipelines), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = pipeline_service.ListTrainingPipelinesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_training_pipelines(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListTrainingPipelinesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_training_pipelines_field_headers():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = pipeline_service.ListTrainingPipelinesRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_training_pipelines), "__call__"
    ) as call:
        call.return_value = pipeline_service.ListTrainingPipelinesResponse()
        client.list_training_pipelines(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_training_pipelines_flattened():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_training_pipelines), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = pipeline_service.ListTrainingPipelinesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_training_pipelines(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_training_pipelines_flattened_error():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_training_pipelines(
            pipeline_service.ListTrainingPipelinesRequest(), parent="parent_value",
        )


def test_list_training_pipelines_pager():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_training_pipelines), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token="abc",
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[], next_page_token="def",
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[training_pipeline.TrainingPipeline(),],
                next_page_token="ghi",
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_training_pipelines(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, training_pipeline.TrainingPipeline) for i in results)


def test_list_training_pipelines_pages():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_training_pipelines), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
                next_page_token="abc",
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[], next_page_token="def",
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[training_pipeline.TrainingPipeline(),],
                next_page_token="ghi",
            ),
            pipeline_service.ListTrainingPipelinesResponse(
                training_pipelines=[
                    training_pipeline.TrainingPipeline(),
                    training_pipeline.TrainingPipeline(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_training_pipelines(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_delete_training_pipeline(transport: str = "grpc"):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = pipeline_service.DeleteTrainingPipelineRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_training_pipeline_flattened():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.delete_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_training_pipeline(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_training_pipeline_flattened_error():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_training_pipeline(
            pipeline_service.DeleteTrainingPipelineRequest(), name="name_value",
        )


def test_cancel_training_pipeline(transport: str = "grpc"):
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = pipeline_service.CancelTrainingPipelineRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        response = client.cancel_training_pipeline(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert response is None


def test_cancel_training_pipeline_flattened():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.cancel_training_pipeline), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = None

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.cancel_training_pipeline(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_cancel_training_pipeline_flattened_error():
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.cancel_training_pipeline(
            pipeline_service.CancelTrainingPipelineRequest(), name="name_value",
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = PipelineServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.PipelineServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = PipelineServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = PipelineServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.PipelineServiceGrpcTransport,)


def test_pipeline_service_base_transport():
    # Instantiate the base transport.
    transport = transports.PipelineServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_training_pipeline",
        "get_training_pipeline",
        "list_training_pipelines",
        "delete_training_pipeline",
        "cancel_training_pipeline",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_pipeline_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        PipelineServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_pipeline_service_host_no_port():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:443"


def test_pipeline_service_host_with_port():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:8000"


def test_pipeline_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")
    transport = transports.PipelineServiceGrpcTransport(channel=channel,)
    assert transport.grpc_channel is channel


def test_pipeline_service_grpc_lro_client():
    client = PipelineServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_training_pipeline_path():
    project = "squid"
    location = "clam"
    training_pipeline = "whelk"

    expected = "projects/{project}/locations/{location}/trainingPipelines/{training_pipeline}".format(
        project=project, location=location, training_pipeline=training_pipeline,
    )
    actual = PipelineServiceClient.training_pipeline_path(
        project, location, training_pipeline
    )
    assert expected == actual


def test_model_path():
    project = "squid"
    location = "clam"
    model = "whelk"

    expected = "projects/{project}/locations/{location}/models/{model}".format(
        project=project, location=location, model=model,
    )
    actual = PipelineServiceClient.model_path(project, location, model)
    assert expected == actual
