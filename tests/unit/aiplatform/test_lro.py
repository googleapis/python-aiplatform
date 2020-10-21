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
from google.longrunning import operations_pb2
from google.protobuf import empty_pb2 as empty
from google.protobuf import struct_pb2

TEST_OPERATION_NAME = "test/operation"


def make_operation_proto(
    name=TEST_OPERATION_NAME, metadata=None, response=None, error=None, **kwargs
):
    operation_proto = operations_pb2.Operation(name=name, **kwargs)

    if metadata is not None:
        operation_proto.metadata.Pack(metadata)

    if response is not None:
        operation_proto.response.Pack(response)

    if error is not None:
        operation_proto.error.CopyFrom(error)

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
        result_type=struct_pb2.Struct,
        metadata_type=struct_pb2.Struct,
    )

    return operation_future


def test_constructor():
    operation_future = make_operation_future()
    lro = lro.LRO(operation_future)

    assert lro._operation_future.name == TEST_OPERATION_NAME
    assert lro._operation_future._result_type is empty.Empty
    assert lro._operation_future.metadata() is None
    assert lro._operation_future.done() is False
    assert lro._operation_future.running()
    assert len(lro._operation_future._done_callbacks) is 0


def test_constructor_with_update():
    operation_future = make_operation_future()
    resource_noun_obj = base.AiPlatformResourceNoun()
    result_key = "name"
    api_get = mock.Mock(spec=["__call__"])
    lro = lro.LRO(operation_future, resource_noun_obj, result_key, api_get)

    assert len(lro._operation_future._done_callbacks) is 1


def test_add_update_resource_callback():
    operation_future = make_operation_future()
    lro = lro.LRO(operation_future)
    resource_noun_obj = base.AiPlatformResourceNoun()
    result_key = "name"
    api_get = mock.Mock(spec=["__call__"])
    lro.add_update_resource_callback(resource_noun_obj, result_key, api_get)

    assert len(lro._operation_future._done_callbacks) is 1


def test_operation_future():
    operation_future = make_operation_future()
    lro = lro.LRO(operation_future)

    assert lro.operation_future.name == TEST_OPERATION_NAME
    assert lro.operation_future._result_type is empty.Empty
    assert lro.operation_future.metadata() is None
    assert lro.operation_future.done() is False
    assert lro.operation_future.running()
