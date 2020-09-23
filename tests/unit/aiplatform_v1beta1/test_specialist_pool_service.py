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
from google.cloud.aiplatform_v1beta1.services.specialist_pool_service import SpecialistPoolServiceClient
from google.cloud.aiplatform_v1beta1.services.specialist_pool_service import pagers
from google.cloud.aiplatform_v1beta1.services.specialist_pool_service import transports
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.cloud.aiplatform_v1beta1.types import specialist_pool
from google.cloud.aiplatform_v1beta1.types import specialist_pool as gca_specialist_pool
from google.cloud.aiplatform_v1beta1.types import specialist_pool_service
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore


def test_specialist_pool_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(service_account.Credentials, 'from_service_account_file') as factory:
        factory.return_value = creds
        client = SpecialistPoolServiceClient.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = SpecialistPoolServiceClient.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == 'aiplatform.googleapis.com:443'


def test_specialist_pool_service_client_client_options():
    # Check the default options have their expected values.
    assert SpecialistPoolServiceClient.DEFAULT_OPTIONS.api_endpoint == 'aiplatform.googleapis.com'

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch('google.cloud.aiplatform_v1beta1.services.specialist_pool_service.SpecialistPoolServiceClient.get_transport_class') as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = SpecialistPoolServiceClient(
            client_options=options
        )
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_specialist_pool_service_client_client_options_from_dict():
    with mock.patch('google.cloud.aiplatform_v1beta1.services.specialist_pool_service.SpecialistPoolServiceClient.get_transport_class') as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = SpecialistPoolServiceClient(
            client_options={'api_endpoint': 'squid.clam.whelk'}
        )
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_create_specialist_pool(transport: str = 'grpc'):
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = specialist_pool_service.CreateSpecialistPoolRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.create_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')

        response = client.create_specialist_pool(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_specialist_pool_flattened():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.create_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_specialist_pool(
            parent='parent_value',
            specialist_pool=gca_specialist_pool.SpecialistPool(name='name_value'),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == 'parent_value'
        assert args[0].specialist_pool == gca_specialist_pool.SpecialistPool(name='name_value')


def test_create_specialist_pool_flattened_error():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_specialist_pool(
            specialist_pool_service.CreateSpecialistPoolRequest(),
            parent='parent_value',
            specialist_pool=gca_specialist_pool.SpecialistPool(name='name_value'),
        )


def test_get_specialist_pool(transport: str = 'grpc'):
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = specialist_pool_service.GetSpecialistPoolRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.get_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = specialist_pool.SpecialistPool(
            name='name_value',
            display_name='display_name_value',
            specialist_managers_count=2662,
            specialist_manager_emails=['specialist_manager_emails_value'],
            pending_data_labeling_jobs=['pending_data_labeling_jobs_value'],
        )

        response = client.get_specialist_pool(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, specialist_pool.SpecialistPool)
    assert response.name == 'name_value'
    assert response.display_name == 'display_name_value'
    assert response.specialist_managers_count == 2662
    assert response.specialist_manager_emails == ['specialist_manager_emails_value']
    assert response.pending_data_labeling_jobs == ['pending_data_labeling_jobs_value']


def test_get_specialist_pool_field_headers():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
  )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = specialist_pool_service.GetSpecialistPoolRequest(
        name='name/value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.get_specialist_pool),
            '__call__') as call:
        call.return_value = specialist_pool.SpecialistPool()
        client.get_specialist_pool(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'name=name/value',
    ) in kw['metadata']


def test_get_specialist_pool_flattened():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.get_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = specialist_pool.SpecialistPool()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_specialist_pool(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == 'name_value'


def test_get_specialist_pool_flattened_error():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_specialist_pool(
            specialist_pool_service.GetSpecialistPoolRequest(),
            name='name_value',
        )


def test_list_specialist_pools(transport: str = 'grpc'):
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = specialist_pool_service.ListSpecialistPoolsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.list_specialist_pools),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = specialist_pool_service.ListSpecialistPoolsResponse(
            next_page_token='next_page_token_value',
        )

        response = client.list_specialist_pools(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListSpecialistPoolsPager)
    assert response.next_page_token == 'next_page_token_value'


def test_list_specialist_pools_field_headers():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
  )

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = specialist_pool_service.ListSpecialistPoolsRequest(
        parent='parent/value',
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.list_specialist_pools),
            '__call__') as call:
        call.return_value = specialist_pool_service.ListSpecialistPoolsResponse()
        client.list_specialist_pools(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert (
        'x-goog-request-params',
        'parent=parent/value',
    ) in kw['metadata']


def test_list_specialist_pools_flattened():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.list_specialist_pools),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = specialist_pool_service.ListSpecialistPoolsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_specialist_pools(
            parent='parent_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == 'parent_value'


def test_list_specialist_pools_flattened_error():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_specialist_pools(
            specialist_pool_service.ListSpecialistPoolsRequest(),
            parent='parent_value',
        )


def test_list_specialist_pools_pager():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.list_specialist_pools),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[
                    specialist_pool.SpecialistPool(),
                    specialist_pool.SpecialistPool(),
                    specialist_pool.SpecialistPool(),
                ],
                next_page_token='abc',
            ),
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[],
                next_page_token='def',
            ),
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[
                    specialist_pool.SpecialistPool(),
                ],
                next_page_token='ghi',
            ),
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[
                    specialist_pool.SpecialistPool(),
                    specialist_pool.SpecialistPool(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_specialist_pools(
            request={},
        )]
        assert len(results) == 6
        assert all(isinstance(i, specialist_pool.SpecialistPool)
                   for i in results)

def test_list_specialist_pools_pages():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials,
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.list_specialist_pools),
            '__call__') as call:
        # Set the response to a series of pages.
        call.side_effect = (
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[
                    specialist_pool.SpecialistPool(),
                    specialist_pool.SpecialistPool(),
                    specialist_pool.SpecialistPool(),
                ],
                next_page_token='abc',
            ),
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[],
                next_page_token='def',
            ),
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[
                    specialist_pool.SpecialistPool(),
                ],
                next_page_token='ghi',
            ),
            specialist_pool_service.ListSpecialistPoolsResponse(
                specialist_pools=[
                    specialist_pool.SpecialistPool(),
                    specialist_pool.SpecialistPool(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_specialist_pools(request={}).pages)
        for page, token in zip(pages, ['abc','def','ghi', '']):
            assert page.raw_page.next_page_token == token


def test_delete_specialist_pool(transport: str = 'grpc'):
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = specialist_pool_service.DeleteSpecialistPoolRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.delete_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')

        response = client.delete_specialist_pool(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_specialist_pool_flattened():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.delete_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_specialist_pool(
            name='name_value',
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == 'name_value'


def test_delete_specialist_pool_flattened_error():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_specialist_pool(
            specialist_pool_service.DeleteSpecialistPoolRequest(),
            name='name_value',
        )


def test_update_specialist_pool(transport: str = 'grpc'):
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = specialist_pool_service.UpdateSpecialistPoolRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.update_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/spam')

        response = client.update_specialist_pool(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_update_specialist_pool_flattened():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
            type(client._transport.update_specialist_pool),
            '__call__') as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name='operations/op')

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.update_specialist_pool(
            specialist_pool=gca_specialist_pool.SpecialistPool(name='name_value'),
            update_mask=field_mask.FieldMask(paths=['paths_value']),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].specialist_pool == gca_specialist_pool.SpecialistPool(name='name_value')
        assert args[0].update_mask == field_mask.FieldMask(paths=['paths_value'])


def test_update_specialist_pool_flattened_error():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_specialist_pool(
            specialist_pool_service.UpdateSpecialistPoolRequest(),
            specialist_pool=gca_specialist_pool.SpecialistPool(name='name_value'),
            update_mask=field_mask.FieldMask(paths=['paths_value']),
        )


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.SpecialistPoolServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = SpecialistPoolServiceClient(
            credentials=credentials.AnonymousCredentials(),
            transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.SpecialistPoolServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = SpecialistPoolServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
    )
    assert isinstance(
        client._transport,
        transports.SpecialistPoolServiceGrpcTransport,
    )


def test_specialist_pool_service_base_transport():
    # Instantiate the base transport.
    transport = transports.SpecialistPoolServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        'create_specialist_pool',
        'get_specialist_pool',
        'list_specialist_pools',
        'delete_specialist_pool',
        'update_specialist_pool',
        )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_specialist_pool_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, 'default') as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        SpecialistPoolServiceClient()
        adc.assert_called_once_with(scopes=(
            'https://www.googleapis.com/auth/cloud-platform',
        ))


def test_specialist_pool_service_host_no_port():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='aiplatform.googleapis.com'),
        transport='grpc',
    )
    assert client._transport._host == 'aiplatform.googleapis.com:443'


def test_specialist_pool_service_host_with_port():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(api_endpoint='aiplatform.googleapis.com:8000'),
        transport='grpc',
    )
    assert client._transport._host == 'aiplatform.googleapis.com:8000'


def test_specialist_pool_service_grpc_transport_channel():
    channel = grpc.insecure_channel('http://localhost/')
    transport = transports.SpecialistPoolServiceGrpcTransport(
        channel=channel,
    )
    assert transport.grpc_channel is channel


def test_specialist_pool_service_grpc_lro_client():
    client = SpecialistPoolServiceClient(
        credentials=credentials.AnonymousCredentials(),
        transport='grpc',
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(
        transport.operations_client,
        operations_v1.OperationsClient,
    )

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client

def test_specialist_pool_path():
  project = "squid"
  location = "clam"
  specialist_pool = "whelk"

  expected = "projects/{project}/locations/{location}/specialistPools/{specialist_pool}".format(project=project, location=location, specialist_pool=specialist_pool, )
  actual = SpecialistPoolServiceClient.specialist_pool_path(project, location, specialist_pool)
  assert expected == actual
