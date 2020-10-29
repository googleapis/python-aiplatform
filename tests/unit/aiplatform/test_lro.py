# Copyright 2020, Google LLC
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

import mock

from google.api_core import operation
from google.cloud.aiplatform import base
from google.cloud.aiplatform import lro
from google.cloud.aiplatform_v1beta1.services.model_service.client import (
    ModelServiceClient,
)
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types.model_service import UploadModelResponse
from google.longrunning import operations_pb2
from google.protobuf import struct_pb2 as struct


TEST_OPERATION_NAME = "test/operation"


class AiPlatformResourceNounImpl(base.AiPlatformResourceNoun):
    client_class = ModelServiceClient
    _is_client_prediction_client = False


def make_operation_proto(name=TEST_OPERATION_NAME, response=None, **kwargs):
    operation_proto = operations_pb2.Operation(name=name, **kwargs)

    if response is not None:
        operation_proto.response.Pack(response)

    return operation_proto


def make_operation_future(client_operations_responses=None):
    if client_operations_responses is None:
        client_operations_responses = [make_operation_proto()]

    refresh = mock.Mock(spec=["__call__"], side_effect=client_operations_responses)
    refresh.responses = client_operations_responses
    cancel = mock.Mock(spec=["__call__"])
    operation_future = operation.Operation(
        client_operations_responses[0],
        refresh,
        cancel,
        result_type=gca_model.Model,
        metadata_type=struct.Struct,
    )

    return operation_future


def test_constructor():
    operation_future = make_operation_future()
    test_lro = lro.LRO(operation_future)

    assert test_lro.operation_future.operation.name == TEST_OPERATION_NAME
    assert test_lro.operation_future._result_type is gca_model.Model
    assert test_lro.operation_future.done() is False
    assert len(test_lro.operation_future._done_callbacks) == 0


def test_constructor_with_update():
    operation_future = make_operation_future()
    resource_noun_obj = AiPlatformResourceNounImpl()
    result_key = "name"
    api_get = mock.Mock(spec=["__call__"])
    test_lro = lro.LRO(operation_future, resource_noun_obj, result_key, api_get)

    assert len(test_lro.operation_future._done_callbacks) == 1


def test_update_resource():
    expected_result = UploadModelResponse(model="tardigrade")
    responses = [
        make_operation_proto(),
        # Second operation response includes the result.
        make_operation_proto(done=True, response=expected_result),
    ]
    operation_future = make_operation_future(responses)
    resource_noun_obj = AiPlatformResourceNounImpl()
    result_key = "model"

    def get_object(result_value):
        return gca_model.Model(display_name=result_value)

    api_get = mock.Mock(spec=["__call__"], side_effect=get_object)

    assert hasattr(resource_noun_obj, "_gca_resource") is False

    lro.LRO.update_resource(operation_future, resource_noun_obj, result_key, api_get)

    assert hasattr(resource_noun_obj, "_gca_resource")


def test_add_update_resource_callback():
    operation_future = make_operation_future()
    test_lro = lro.LRO(operation_future)
    resource_noun_obj = AiPlatformResourceNounImpl()
    result_key = "name"
    api_get = mock.Mock(spec=["__call__"])
    test_lro.add_update_resource_callback(resource_noun_obj, result_key, api_get)

    assert len(test_lro.operation_future._done_callbacks) == 1
