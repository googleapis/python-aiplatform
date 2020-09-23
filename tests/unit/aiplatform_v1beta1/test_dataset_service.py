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
from google.cloud.aiplatform_v1beta1.services.dataset_service import (
    DatasetServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.dataset_service import pagers
from google.cloud.aiplatform_v1beta1.services.dataset_service import transports
from google.cloud.aiplatform_v1beta1.types import annotation
from google.cloud.aiplatform_v1beta1.types import annotation_spec
from google.cloud.aiplatform_v1beta1.types import data_item
from google.cloud.aiplatform_v1beta1.types import dataset
from google.cloud.aiplatform_v1beta1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1beta1.types import dataset_service
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


def test_dataset_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = DatasetServiceClient.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = DatasetServiceClient.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "aiplatform.googleapis.com:443"


def test_dataset_service_client_client_options():
    # Check the default options have their expected values.
    assert (
        DatasetServiceClient.DEFAULT_OPTIONS.api_endpoint == "aiplatform.googleapis.com"
    )

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.dataset_service.DatasetServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = DatasetServiceClient(client_options=options)
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_dataset_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.dataset_service.DatasetServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = DatasetServiceClient(
            client_options={"api_endpoint": "squid.clam.whelk"}
        )
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_create_dataset(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.CreateDatasetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.create_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_create_dataset_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.create_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.create_dataset(
            parent="parent_value", dataset=gca_dataset.Dataset(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].dataset == gca_dataset.Dataset(name="name_value")


def test_create_dataset_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.create_dataset(
            dataset_service.CreateDatasetRequest(),
            parent="parent_value",
            dataset=gca_dataset.Dataset(name="name_value"),
        )


def test_get_dataset(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.GetDatasetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            metadata_schema_uri="metadata_schema_uri_value",
            etag="etag_value",
        )

        response = client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.etag == "etag_value"


def test_get_dataset_field_headers():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetDatasetRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_dataset), "__call__") as call:
        call.return_value = dataset.Dataset()
        client.get_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_dataset_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset.Dataset()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_dataset(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_dataset_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_dataset(
            dataset_service.GetDatasetRequest(), name="name_value",
        )


def test_update_dataset(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.UpdateDatasetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset.Dataset(
            name="name_value",
            display_name="display_name_value",
            metadata_schema_uri="metadata_schema_uri_value",
            etag="etag_value",
        )

        response = client.update_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_dataset.Dataset)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.etag == "etag_value"


def test_update_dataset_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_dataset.Dataset()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.update_dataset(
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].dataset == gca_dataset.Dataset(name="name_value")
        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_dataset_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_dataset(
            dataset_service.UpdateDatasetRequest(),
            dataset=gca_dataset.Dataset(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_list_datasets(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.ListDatasetsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDatasetsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_datasets_field_headers():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDatasetsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_datasets), "__call__") as call:
        call.return_value = dataset_service.ListDatasetsResponse()
        client.list_datasets(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_datasets_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_datasets), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDatasetsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_datasets(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_datasets_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_datasets(
            dataset_service.ListDatasetsRequest(), parent="parent_value",
        )


def test_list_datasets_pager():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_datasets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetsResponse(
                datasets=[dataset.Dataset(), dataset.Dataset(), dataset.Dataset(),],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(datasets=[], next_page_token="def",),
            dataset_service.ListDatasetsResponse(
                datasets=[dataset.Dataset(),], next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[dataset.Dataset(), dataset.Dataset(),],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_datasets(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, dataset.Dataset) for i in results)


def test_list_datasets_pages():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_datasets), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDatasetsResponse(
                datasets=[dataset.Dataset(), dataset.Dataset(), dataset.Dataset(),],
                next_page_token="abc",
            ),
            dataset_service.ListDatasetsResponse(datasets=[], next_page_token="def",),
            dataset_service.ListDatasetsResponse(
                datasets=[dataset.Dataset(),], next_page_token="ghi",
            ),
            dataset_service.ListDatasetsResponse(
                datasets=[dataset.Dataset(), dataset.Dataset(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_datasets(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_delete_dataset(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.DeleteDatasetRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_dataset(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_dataset_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_dataset), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_dataset(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_dataset_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_dataset(
            dataset_service.DeleteDatasetRequest(), name="name_value",
        )


def test_import_data(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.ImportDataRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.import_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_import_data_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.import_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.import_data(
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"
        assert args[0].import_configs == [
            dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
        ]


def test_import_data_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.import_data(
            dataset_service.ImportDataRequest(),
            name="name_value",
            import_configs=[
                dataset.ImportDataConfig(gcs_source=io.GcsSource(uris=["uris_value"]))
            ],
        )


def test_export_data(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.ExportDataRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.export_data(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_export_data_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.export_data), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.export_data(
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"
        assert args[0].export_config == dataset.ExportDataConfig(
            gcs_destination=io.GcsDestination(
                output_uri_prefix="output_uri_prefix_value"
            )
        )


def test_export_data_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_data(
            dataset_service.ExportDataRequest(),
            name="name_value",
            export_config=dataset.ExportDataConfig(
                gcs_destination=io.GcsDestination(
                    output_uri_prefix="output_uri_prefix_value"
                )
            ),
        )


def test_list_data_items(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.ListDataItemsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDataItemsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListDataItemsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_data_items_field_headers():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListDataItemsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_data_items), "__call__") as call:
        call.return_value = dataset_service.ListDataItemsResponse()
        client.list_data_items(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_data_items_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_data_items), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListDataItemsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_data_items(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_data_items_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_data_items(
            dataset_service.ListDataItemsRequest(), parent="parent_value",
        )


def test_list_data_items_pager():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_data_items), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[], next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[data_item.DataItem(),], next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[data_item.DataItem(), data_item.DataItem(),],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_data_items(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, data_item.DataItem) for i in results)


def test_list_data_items_pages():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_data_items), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListDataItemsResponse(
                data_items=[
                    data_item.DataItem(),
                    data_item.DataItem(),
                    data_item.DataItem(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[], next_page_token="def",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[data_item.DataItem(),], next_page_token="ghi",
            ),
            dataset_service.ListDataItemsResponse(
                data_items=[data_item.DataItem(), data_item.DataItem(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_data_items(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_get_annotation_spec(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.GetAnnotationSpecRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = annotation_spec.AnnotationSpec(
            name="name_value", display_name="display_name_value", etag="etag_value",
        )

        response = client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, annotation_spec.AnnotationSpec)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.etag == "etag_value"


def test_get_annotation_spec_field_headers():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.GetAnnotationSpecRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_annotation_spec), "__call__"
    ) as call:
        call.return_value = annotation_spec.AnnotationSpec()
        client.get_annotation_spec(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_annotation_spec_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_annotation_spec), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = annotation_spec.AnnotationSpec()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_annotation_spec(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_annotation_spec_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_annotation_spec(
            dataset_service.GetAnnotationSpecRequest(), name="name_value",
        )


def test_list_annotations(transport: str = "grpc"):
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = dataset_service.ListAnnotationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_annotations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListAnnotationsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListAnnotationsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_annotations_field_headers():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = dataset_service.ListAnnotationsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_annotations), "__call__"
    ) as call:
        call.return_value = dataset_service.ListAnnotationsResponse()
        client.list_annotations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_annotations_flattened():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_annotations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = dataset_service.ListAnnotationsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_annotations(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_annotations_flattened_error():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_annotations(
            dataset_service.ListAnnotationsRequest(), parent="parent_value",
        )


def test_list_annotations_pager():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_annotations), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[], next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[annotation.Annotation(),], next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[annotation.Annotation(), annotation.Annotation(),],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_annotations(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, annotation.Annotation) for i in results)


def test_list_annotations_pages():
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_annotations), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            dataset_service.ListAnnotationsResponse(
                annotations=[
                    annotation.Annotation(),
                    annotation.Annotation(),
                    annotation.Annotation(),
                ],
                next_page_token="abc",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[], next_page_token="def",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[annotation.Annotation(),], next_page_token="ghi",
            ),
            dataset_service.ListAnnotationsResponse(
                annotations=[annotation.Annotation(), annotation.Annotation(),],
            ),
            RuntimeError,
        )
        pages = list(client.list_annotations(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = DatasetServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.DatasetServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = DatasetServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = DatasetServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.DatasetServiceGrpcTransport,)


def test_dataset_service_base_transport():
    # Instantiate the base transport.
    transport = transports.DatasetServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "create_dataset",
        "get_dataset",
        "update_dataset",
        "list_datasets",
        "delete_dataset",
        "import_data",
        "export_data",
        "list_data_items",
        "get_annotation_spec",
        "list_annotations",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_dataset_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        DatasetServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_dataset_service_host_no_port():
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:443"


def test_dataset_service_host_with_port():
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:8000"


def test_dataset_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")
    transport = transports.DatasetServiceGrpcTransport(channel=channel,)
    assert transport.grpc_channel is channel


def test_dataset_service_grpc_lro_client():
    client = DatasetServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_dataset_path():
    project = "squid"
    location = "clam"
    dataset = "whelk"

    expected = "projects/{project}/locations/{location}/datasets/{dataset}".format(
        project=project, location=location, dataset=dataset,
    )
    actual = DatasetServiceClient.dataset_path(project, location, dataset)
    assert expected == actual
