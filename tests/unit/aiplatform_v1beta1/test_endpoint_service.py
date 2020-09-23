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
from google.cloud.aiplatform_v1beta1.services.endpoint_service import (
    EndpointServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.endpoint_service import pagers
from google.cloud.aiplatform_v1beta1.services.endpoint_service import transports
from google.cloud.aiplatform_v1beta1.types import accelerator_type
from google.cloud.aiplatform_v1beta1.types import endpoint
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import endpoint_service
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import explanation_metadata
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


def test_endpoint_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = EndpointServiceClient.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = EndpointServiceClient.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "aiplatform.googleapis.com:443"


def test_endpoint_service_client_client_options():
    # Check the default options have their expected values.
    assert (
        EndpointServiceClient.DEFAULT_OPTIONS.api_endpoint
        == "aiplatform.googleapis.com"
    )

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.endpoint_service.EndpointServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = EndpointServiceClient(client_options=options)
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_endpoint_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.endpoint_service.EndpointServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = EndpointServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_create_endpoint(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.CreateEndpointRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.create_endpoint(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_endpoint_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_endpoint(
            parent="parent_value", endpoint=gca_endpoint.Endpoint(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].endpoint == gca_endpoint.Endpoint(name="name_value")


def test_create_endpoint_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_endpoint(
            endpoint_service.CreateEndpointRequest(),
            parent="parent_value",
            endpoint=gca_endpoint.Endpoint(name="name_value"),
        )


def test_get_endpoint(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.GetEndpointRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = endpoint.Endpoint(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
        )

        response = client.get_endpoint(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, endpoint.Endpoint)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_get_endpoint_field_headers():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = endpoint_service.GetEndpointRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_endpoint), "__call__") as call:
        call.return_value = endpoint.Endpoint()
        client.get_endpoint(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_endpoint_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = endpoint.Endpoint()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_endpoint(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_endpoint_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_endpoint(
            endpoint_service.GetEndpointRequest(), name="name_value",
        )


def test_list_endpoints(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.ListEndpointsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_endpoints), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = endpoint_service.ListEndpointsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_endpoints(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListEndpointsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_endpoints_field_headers():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = endpoint_service.ListEndpointsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_endpoints), "__call__") as call:
        call.return_value = endpoint_service.ListEndpointsResponse()
        client.list_endpoints(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_endpoints_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_endpoints), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = endpoint_service.ListEndpointsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_endpoints(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_endpoints_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_endpoints(
            endpoint_service.ListEndpointsRequest(), parent="parent_value",
        )


def test_list_endpoints_pager():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_endpoints), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            endpoint_service.ListEndpointsResponse(
                endpoints=[
                    endpoint.Endpoint(),
                    endpoint.Endpoint(),
                    endpoint.Endpoint(),
                ],
                next_page_token="abc",
            ),
            endpoint_service.ListEndpointsResponse(
                endpoints=[], next_page_token="def",
            ),
            endpoint_service.ListEndpointsResponse(
                endpoints=[endpoint.Endpoint(),], next_page_token="ghi",
            ),
            endpoint_service.ListEndpointsResponse(
                endpoints=[endpoint.Endpoint(), endpoint.Endpoint(),],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_endpoints(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, endpoint.Endpoint) for i in results)


def test_list_endpoints_pages():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_endpoints), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            endpoint_service.ListEndpointsResponse(
                endpoints=[
                    endpoint.Endpoint(),
                    endpoint.Endpoint(),
                    endpoint.Endpoint(),
                ],
                next_page_token="abc",
            ),
            endpoint_service.ListEndpointsResponse(
                endpoints=[], next_page_token="def",
            ),
            endpoint_service.ListEndpointsResponse(
                endpoints=[endpoint.Endpoint(),], next_page_token="ghi",
            ),
            endpoint_service.ListEndpointsResponse(
                endpoints=[endpoint.Endpoint(), endpoint.Endpoint(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_endpoints(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_update_endpoint(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.UpdateEndpointRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_endpoint.Endpoint(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            etag="etag_value",
        )

        response = client.update_endpoint(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_endpoint.Endpoint)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.etag == "etag_value"


def test_update_endpoint_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_endpoint.Endpoint()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.update_endpoint(
            endpoint=gca_endpoint.Endpoint(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].endpoint == gca_endpoint.Endpoint(name="name_value")
        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_endpoint_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_endpoint(
            endpoint_service.UpdateEndpointRequest(),
            endpoint=gca_endpoint.Endpoint(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_delete_endpoint(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.DeleteEndpointRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_endpoint(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_endpoint_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_endpoint), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_endpoint(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_endpoint_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_endpoint(
            endpoint_service.DeleteEndpointRequest(), name="name_value",
        )


def test_deploy_model(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.DeployModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.deploy_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.deploy_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_deploy_model_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.deploy_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.deploy_model(
            endpoint="endpoint_value",
            deployed_model=gca_endpoint.DeployedModel(
                dedicated_resources=machine_resources.DedicatedResources(
                    machine_spec=machine_resources.MachineSpec(
                        machine_type="machine_type_value"
                    )
                )
            ),
            traffic_split={"key_value": 541},
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].endpoint == "endpoint_value"
        assert args[0].deployed_model == gca_endpoint.DeployedModel(
            dedicated_resources=machine_resources.DedicatedResources(
                machine_spec=machine_resources.MachineSpec(
                    machine_type="machine_type_value"
                )
            )
        )
        assert args[0].traffic_split == {"key_value": 541}


def test_deploy_model_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.deploy_model(
            endpoint_service.DeployModelRequest(),
            endpoint="endpoint_value",
            deployed_model=gca_endpoint.DeployedModel(
                dedicated_resources=machine_resources.DedicatedResources(
                    machine_spec=machine_resources.MachineSpec(
                        machine_type="machine_type_value"
                    )
                )
            ),
            traffic_split={"key_value": 541},
        )


def test_undeploy_model(transport: str = "grpc"):
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = endpoint_service.UndeployModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.undeploy_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.undeploy_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_undeploy_model_flattened():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.undeploy_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.undeploy_model(
            endpoint="endpoint_value",
            deployed_model_id="deployed_model_id_value",
            traffic_split={"key_value": 541},
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].endpoint == "endpoint_value"
        assert args[0].deployed_model_id == "deployed_model_id_value"
        assert args[0].traffic_split == {"key_value": 541}


def test_undeploy_model_flattened_error():
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.undeploy_model(
            endpoint_service.UndeployModelRequest(),
            endpoint="endpoint_value",
            deployed_model_id="deployed_model_id_value",
            traffic_split={"key_value": 541},
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.EndpointServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = EndpointServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.EndpointServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = EndpointServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = EndpointServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.EndpointServiceGrpcTransport,)


def test_endpoint_service_base_transport():
    # Instantiate the base transport.
    transport = transports.EndpointServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_endpoint",
        "get_endpoint",
        "list_endpoints",
        "update_endpoint",
        "delete_endpoint",
        "deploy_model",
        "undeploy_model",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_endpoint_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        EndpointServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_endpoint_service_host_no_port():
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:443"


def test_endpoint_service_host_with_port():
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:8000"


def test_endpoint_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")
    transport = transports.EndpointServiceGrpcTransport(channel=channel,)
    assert transport.grpc_channel is channel


def test_endpoint_service_grpc_lro_client():
    client = EndpointServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_endpoint_path():
    project = "squid"
    location = "clam"
    endpoint = "whelk"

    expected = "projects/{project}/locations/{location}/endpoints/{endpoint}".format(
        project=project, location=location, endpoint=endpoint,
    )
    actual = EndpointServiceClient.endpoint_path(project, location, endpoint)
    assert expected == actual
