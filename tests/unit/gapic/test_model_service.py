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
from google.cloud.aiplatform_v1beta1.services.model_service import ModelServiceClient
from google.cloud.aiplatform_v1beta1.services.model_service import pagers
from google.cloud.aiplatform_v1beta1.services.model_service import transports
from google.cloud.aiplatform_v1beta1.types import deployed_model_ref
from google.cloud.aiplatform_v1beta1.types import env_var
from google.cloud.aiplatform_v1beta1.types import explanation
from google.cloud.aiplatform_v1beta1.types import explanation_metadata
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import model
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import model_evaluation
from google.cloud.aiplatform_v1beta1.types import model_evaluation_slice
from google.cloud.aiplatform_v1beta1.types import model_service
from google.cloud.aiplatform_v1beta1.types import operation as gca_operation
from google.longrunning import operations_pb2
from google.oauth2 import service_account
from google.protobuf import field_mask_pb2 as field_mask  # type: ignore
from google.protobuf import struct_pb2 as struct  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore


def test_model_service_client_from_service_account_file():
    creds = credentials.AnonymousCredentials()
    with mock.patch.object(
        service_account.Credentials, "from_service_account_file"
    ) as factory:
        factory.return_value = creds
        client = ModelServiceClient.from_service_account_file("dummy/file/path.json")
        assert client._transport._credentials == creds

        client = ModelServiceClient.from_service_account_json("dummy/file/path.json")
        assert client._transport._credentials == creds

        assert client._transport._host == "aiplatform.googleapis.com:443"


def test_model_service_client_client_options():
    # Check the default options have their expected values.
    assert (
        ModelServiceClient.DEFAULT_OPTIONS.api_endpoint == "aiplatform.googleapis.com"
    )

    # Check that options can be customized.
    options = client_options.ClientOptions(api_endpoint="squid.clam.whelk")
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.model_service.ModelServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = ModelServiceClient(client_options=options)
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_model_service_client_client_options_from_dict():
    with mock.patch(
        "google.cloud.aiplatform_v1beta1.services.model_service.ModelServiceClient.get_transport_class"
    ) as gtc:
        transport = gtc.return_value = mock.MagicMock()
        client = ModelServiceClient(client_options={"api_endpoint": "squid.clam.whelk"})
        transport.assert_called_once_with(credentials=None, host="squid.clam.whelk")


def test_upload_model(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.UploadModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.upload_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.upload_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_upload_model_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.upload_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.upload_model(
            parent="parent_value", model=gca_model.Model(name="name_value"),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"
        assert args[0].model == gca_model.Model(name="name_value")


def test_upload_model_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.upload_model(
            model_service.UploadModelRequest(),
            parent="parent_value",
            model=gca_model.Model(name="name_value"),
        )


def test_get_model(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.GetModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = model.Model(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            training_pipeline="training_pipeline_value",
            artifact_uri="artifact_uri_value",
            supported_deployment_resources_types=[
                model.Model.DeploymentResourcesType.DEDICATED_RESOURCES
            ],
            supported_input_storage_formats=["supported_input_storage_formats_value"],
            supported_output_storage_formats=["supported_output_storage_formats_value"],
            etag="etag_value",
        )

        response = client.get_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, model.Model)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.training_pipeline == "training_pipeline_value"
    assert response.artifact_uri == "artifact_uri_value"
    assert response.supported_deployment_resources_types == [
        model.Model.DeploymentResourcesType.DEDICATED_RESOURCES
    ]
    assert response.supported_input_storage_formats == [
        "supported_input_storage_formats_value"
    ]
    assert response.supported_output_storage_formats == [
        "supported_output_storage_formats_value"
    ]
    assert response.etag == "etag_value"


def test_get_model_field_headers():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = model_service.GetModelRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_model), "__call__") as call:
        call.return_value = model.Model()
        client.get_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_model_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.get_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = model.Model()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_model(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_model_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_model(
            model_service.GetModelRequest(), name="name_value",
        )


def test_list_models(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.ListModelsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_models), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_service.ListModelsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_models(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListModelsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_models_field_headers():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = model_service.ListModelsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_models), "__call__") as call:
        call.return_value = model_service.ListModelsResponse()
        client.list_models(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_models_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_models), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_service.ListModelsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_models(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_models_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_models(
            model_service.ListModelsRequest(), parent="parent_value",
        )


def test_list_models_pager():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_models), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            model_service.ListModelsResponse(
                models=[model.Model(), model.Model(), model.Model(),],
                next_page_token="abc",
            ),
            model_service.ListModelsResponse(models=[], next_page_token="def",),
            model_service.ListModelsResponse(
                models=[model.Model(),], next_page_token="ghi",
            ),
            model_service.ListModelsResponse(models=[model.Model(), model.Model(),],),
            RuntimeError,
        )
        results = [i for i in client.list_models(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, model.Model) for i in results)


def test_list_models_pages():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.list_models), "__call__") as call:
        # Set the response to a series of pages.
        call.side_effect = (
            model_service.ListModelsResponse(
                models=[model.Model(), model.Model(), model.Model(),],
                next_page_token="abc",
            ),
            model_service.ListModelsResponse(models=[], next_page_token="def",),
            model_service.ListModelsResponse(
                models=[model.Model(),], next_page_token="ghi",
            ),
            model_service.ListModelsResponse(models=[model.Model(), model.Model(),],),
            RuntimeError,
        )
        pages = list(client.list_models(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_update_model(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.UpdateModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_model.Model(
            name="name_value",
            display_name="display_name_value",
            description="description_value",
            metadata_schema_uri="metadata_schema_uri_value",
            training_pipeline="training_pipeline_value",
            artifact_uri="artifact_uri_value",
            supported_deployment_resources_types=[
                gca_model.Model.DeploymentResourcesType.DEDICATED_RESOURCES
            ],
            supported_input_storage_formats=["supported_input_storage_formats_value"],
            supported_output_storage_formats=["supported_output_storage_formats_value"],
            etag="etag_value",
        )

        response = client.update_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, gca_model.Model)
    assert response.name == "name_value"
    assert response.display_name == "display_name_value"
    assert response.description == "description_value"
    assert response.metadata_schema_uri == "metadata_schema_uri_value"
    assert response.training_pipeline == "training_pipeline_value"
    assert response.artifact_uri == "artifact_uri_value"
    assert response.supported_deployment_resources_types == [
        gca_model.Model.DeploymentResourcesType.DEDICATED_RESOURCES
    ]
    assert response.supported_input_storage_formats == [
        "supported_input_storage_formats_value"
    ]
    assert response.supported_output_storage_formats == [
        "supported_output_storage_formats_value"
    ]
    assert response.etag == "etag_value"


def test_update_model_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.update_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = gca_model.Model()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.update_model(
            model=gca_model.Model(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].model == gca_model.Model(name="name_value")
        assert args[0].update_mask == field_mask.FieldMask(paths=["paths_value"])


def test_update_model_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.update_model(
            model_service.UpdateModelRequest(),
            model=gca_model.Model(name="name_value"),
            update_mask=field_mask.FieldMask(paths=["paths_value"]),
        )


def test_delete_model(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.DeleteModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.delete_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_delete_model_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.delete_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.delete_model(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_delete_model_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.delete_model(
            model_service.DeleteModelRequest(), name="name_value",
        )


def test_export_model(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.ExportModelRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.export_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/spam")

        response = client.export_model(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, future.Future)


def test_export_model_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(type(client._transport.export_model), "__call__") as call:
        # Designate an appropriate return value for the call.
        call.return_value = operations_pb2.Operation(name="operations/op")

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.export_model(
            name="name_value",
            output_config=model_service.ExportModelRequest.OutputConfig(
                export_format_id="export_format_id_value"
            ),
        )

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"
        assert args[0].output_config == model_service.ExportModelRequest.OutputConfig(
            export_format_id="export_format_id_value"
        )


def test_export_model_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.export_model(
            model_service.ExportModelRequest(),
            name="name_value",
            output_config=model_service.ExportModelRequest.OutputConfig(
                export_format_id="export_format_id_value"
            ),
        )


def test_get_model_evaluation(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.GetModelEvaluationRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_model_evaluation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_evaluation.ModelEvaluation(
            name="name_value",
            metrics_schema_uri="metrics_schema_uri_value",
            slice_dimensions=["slice_dimensions_value"],
        )

        response = client.get_model_evaluation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, model_evaluation.ModelEvaluation)
    assert response.name == "name_value"
    assert response.metrics_schema_uri == "metrics_schema_uri_value"
    assert response.slice_dimensions == ["slice_dimensions_value"]


def test_get_model_evaluation_field_headers():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = model_service.GetModelEvaluationRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_model_evaluation), "__call__"
    ) as call:
        call.return_value = model_evaluation.ModelEvaluation()
        client.get_model_evaluation(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_model_evaluation_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_model_evaluation), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_evaluation.ModelEvaluation()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_model_evaluation(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_model_evaluation_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_model_evaluation(
            model_service.GetModelEvaluationRequest(), name="name_value",
        )


def test_list_model_evaluations(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.ListModelEvaluationsRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_service.ListModelEvaluationsResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_model_evaluations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListModelEvaluationsPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_model_evaluations_field_headers():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = model_service.ListModelEvaluationsRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluations), "__call__"
    ) as call:
        call.return_value = model_service.ListModelEvaluationsResponse()
        client.list_model_evaluations(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_model_evaluations_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluations), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_service.ListModelEvaluationsResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_model_evaluations(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_model_evaluations_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_model_evaluations(
            model_service.ListModelEvaluationsRequest(), parent="parent_value",
        )


def test_list_model_evaluations_pager():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluations), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[
                    model_evaluation.ModelEvaluation(),
                    model_evaluation.ModelEvaluation(),
                    model_evaluation.ModelEvaluation(),
                ],
                next_page_token="abc",
            ),
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[], next_page_token="def",
            ),
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[model_evaluation.ModelEvaluation(),],
                next_page_token="ghi",
            ),
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[
                    model_evaluation.ModelEvaluation(),
                    model_evaluation.ModelEvaluation(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_model_evaluations(request={},)]
        assert len(results) == 6
        assert all(isinstance(i, model_evaluation.ModelEvaluation) for i in results)


def test_list_model_evaluations_pages():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluations), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[
                    model_evaluation.ModelEvaluation(),
                    model_evaluation.ModelEvaluation(),
                    model_evaluation.ModelEvaluation(),
                ],
                next_page_token="abc",
            ),
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[], next_page_token="def",
            ),
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[model_evaluation.ModelEvaluation(),],
                next_page_token="ghi",
            ),
            model_service.ListModelEvaluationsResponse(
                model_evaluations=[
                    model_evaluation.ModelEvaluation(),
                    model_evaluation.ModelEvaluation(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_model_evaluations(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_get_model_evaluation_slice(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.GetModelEvaluationSliceRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_model_evaluation_slice), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_evaluation_slice.ModelEvaluationSlice(
            name="name_value", metrics_schema_uri="metrics_schema_uri_value",
        )

        response = client.get_model_evaluation_slice(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, model_evaluation_slice.ModelEvaluationSlice)
    assert response.name == "name_value"
    assert response.metrics_schema_uri == "metrics_schema_uri_value"


def test_get_model_evaluation_slice_field_headers():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = model_service.GetModelEvaluationSliceRequest(name="name/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_model_evaluation_slice), "__call__"
    ) as call:
        call.return_value = model_evaluation_slice.ModelEvaluationSlice()
        client.get_model_evaluation_slice(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "name=name/value",) in kw["metadata"]


def test_get_model_evaluation_slice_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.get_model_evaluation_slice), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_evaluation_slice.ModelEvaluationSlice()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.get_model_evaluation_slice(name="name_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].name == "name_value"


def test_get_model_evaluation_slice_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.get_model_evaluation_slice(
            model_service.GetModelEvaluationSliceRequest(), name="name_value",
        )


def test_list_model_evaluation_slices(transport: str = "grpc"):
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport=transport,
    )

    # Everything is optional in proto3 as far as the runtime is concerned,
    # and we are mocking out the actual API, so just send an empty request.
    request = model_service.ListModelEvaluationSlicesRequest()

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluation_slices), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_service.ListModelEvaluationSlicesResponse(
            next_page_token="next_page_token_value",
        )

        response = client.list_model_evaluation_slices(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]

        assert args[0] == request

    # Establish that the response is the type that we expect.
    assert isinstance(response, pagers.ListModelEvaluationSlicesPager)
    assert response.next_page_token == "next_page_token_value"


def test_list_model_evaluation_slices_field_headers():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Any value that is part of the HTTP/1.1 URI should be sent as
    # a field header. Set these to a non-empty value.
    request = model_service.ListModelEvaluationSlicesRequest(parent="parent/value",)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluation_slices), "__call__"
    ) as call:
        call.return_value = model_service.ListModelEvaluationSlicesResponse()
        client.list_model_evaluation_slices(request)

        # Establish that the underlying gRPC stub method was called.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0] == request

    # Establish that the field header was sent.
    _, _, kw = call.mock_calls[0]
    assert ("x-goog-request-params", "parent=parent/value",) in kw["metadata"]


def test_list_model_evaluation_slices_flattened():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluation_slices), "__call__"
    ) as call:
        # Designate an appropriate return value for the call.
        call.return_value = model_service.ListModelEvaluationSlicesResponse()

        # Call the method with a truthy value for each flattened field,
        # using the keyword arguments to the method.
        response = client.list_model_evaluation_slices(parent="parent_value",)

        # Establish that the underlying call was made with the expected
        # request object values.
        assert len(call.mock_calls) == 1
        _, args, _ = call.mock_calls[0]
        assert args[0].parent == "parent_value"


def test_list_model_evaluation_slices_flattened_error():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)

    # Attempting to call a method with both a request object and flattened
    # fields is an error.
    with pytest.raises(ValueError):
        client.list_model_evaluation_slices(
            model_service.ListModelEvaluationSlicesRequest(), parent="parent_value",
        )


def test_list_model_evaluation_slices_pager():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluation_slices), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[
                    model_evaluation_slice.ModelEvaluationSlice(),
                    model_evaluation_slice.ModelEvaluationSlice(),
                    model_evaluation_slice.ModelEvaluationSlice(),
                ],
                next_page_token="abc",
            ),
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[], next_page_token="def",
            ),
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[
                    model_evaluation_slice.ModelEvaluationSlice(),
                ],
                next_page_token="ghi",
            ),
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[
                    model_evaluation_slice.ModelEvaluationSlice(),
                    model_evaluation_slice.ModelEvaluationSlice(),
                ],
            ),
            RuntimeError,
        )
        results = [i for i in client.list_model_evaluation_slices(request={},)]
        assert len(results) == 6
        assert all(
            isinstance(i, model_evaluation_slice.ModelEvaluationSlice) for i in results
        )


def test_list_model_evaluation_slices_pages():
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials,)

    # Mock the actual call within the gRPC stub, and fake the request.
    with mock.patch.object(
        type(client._transport.list_model_evaluation_slices), "__call__"
    ) as call:
        # Set the response to a series of pages.
        call.side_effect = (
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[
                    model_evaluation_slice.ModelEvaluationSlice(),
                    model_evaluation_slice.ModelEvaluationSlice(),
                    model_evaluation_slice.ModelEvaluationSlice(),
                ],
                next_page_token="abc",
            ),
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[], next_page_token="def",
            ),
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[
                    model_evaluation_slice.ModelEvaluationSlice(),
                ],
                next_page_token="ghi",
            ),
            model_service.ListModelEvaluationSlicesResponse(
                model_evaluation_slices=[
                    model_evaluation_slice.ModelEvaluationSlice(),
                    model_evaluation_slice.ModelEvaluationSlice(),
                ],
            ),
            RuntimeError,
        )
        pages = list(client.list_model_evaluation_slices(request={}).pages)
        for page, token in zip(pages, ["abc", "def", "ghi", ""]):
            assert page.raw_page.next_page_token == token


def test_credentials_transport_error():
    # It is an error to provide credentials and a transport instance.
    transport = transports.ModelServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    with pytest.raises(ValueError):
        client = ModelServiceClient(
            credentials=credentials.AnonymousCredentials(), transport=transport,
        )


def test_transport_instance():
    # A client may be instantiated with a custom transport instance.
    transport = transports.ModelServiceGrpcTransport(
        credentials=credentials.AnonymousCredentials(),
    )
    client = ModelServiceClient(transport=transport)
    assert client._transport is transport


def test_transport_grpc_default():
    # A client should use the gRPC transport by default.
    client = ModelServiceClient(credentials=credentials.AnonymousCredentials(),)
    assert isinstance(client._transport, transports.ModelServiceGrpcTransport,)


def test_model_service_base_transport():
    # Instantiate the base transport.
    transport = transports.ModelServiceTransport(
        credentials=credentials.AnonymousCredentials(),
    )

    # Every method on the transport should just blindly
    # raise NotImplementedError.
    methods = (
        "upload_model",
        "get_model",
        "list_models",
        "update_model",
        "delete_model",
        "export_model",
        "get_model_evaluation",
        "list_model_evaluations",
        "get_model_evaluation_slice",
        "list_model_evaluation_slices",
    )
    for method in methods:
        with pytest.raises(NotImplementedError):
            getattr(transport, method)(request=object())

    # Additionally, the LRO client (a property) should
    # also raise NotImplementedError
    with pytest.raises(NotImplementedError):
        transport.operations_client


def test_model_service_auth_adc():
    # If no credentials are provided, we should use ADC credentials.
    with mock.patch.object(auth, "default") as adc:
        adc.return_value = (credentials.AnonymousCredentials(), None)
        ModelServiceClient()
        adc.assert_called_once_with(
            scopes=("https://www.googleapis.com/auth/cloud-platform",)
        )


def test_model_service_host_no_port():
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:443"


def test_model_service_host_with_port():
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(),
        client_options=client_options.ClientOptions(
            api_endpoint="aiplatform.googleapis.com:8000"
        ),
        transport="grpc",
    )
    assert client._transport._host == "aiplatform.googleapis.com:8000"


def test_model_service_grpc_transport_channel():
    channel = grpc.insecure_channel("http://localhost/")
    transport = transports.ModelServiceGrpcTransport(channel=channel,)
    assert transport.grpc_channel is channel


def test_model_service_grpc_lro_client():
    client = ModelServiceClient(
        credentials=credentials.AnonymousCredentials(), transport="grpc",
    )
    transport = client._transport

    # Ensure that we have a api-core operations client.
    assert isinstance(transport.operations_client, operations_v1.OperationsClient,)

    # Ensure that subsequent calls to the property send the exact same object.
    assert transport.operations_client is transport.operations_client


def test_model_path():
    project = "squid"
    location = "clam"
    model = "whelk"

    expected = "projects/{project}/locations/{location}/models/{model}".format(
        project=project, location=location, model=model,
    )
    actual = ModelServiceClient.model_path(project, location, model)
    assert expected == actual
