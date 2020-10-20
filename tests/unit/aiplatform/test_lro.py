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

from gopgle.api_core.tests.unit import test_operation
from google.cloud.aiplatform import base
from google.cloud.aiplatform import lro
from google.protobuf import empty_pb2 as empty

TEST_OPERATION_NAME = "test/operation"


def make_lro():
    operation = test_operation.make_operation_future()
    lro = lro.LRO(operation)

    return lro

def test_constructor():
    lro = make_lro()
    operation_future = lro._operation_future

    assert operation_future.name == TEST_OPERATION_NAME
    assert operation_future._result_type is empty.Empty
    assert operation_future.metadata() is None
    assert operation_future.done() is False
    assert operation_future.running()

def test_add_update_resource_callback():
    lro = make_lro()
    resource_noun_obj = base.AiPlatformResourceNoun()
    lro.add_update_resource_callback(resource_noun_obj)

    operation_future = lro._operation_future

    assert len(operation_future._done_callbacks) is 1

def test_operation():
    lro = make_lro()
    operation_future = lro.operation_future()

    assert operation_future.name == TEST_OPERATION_NAME
    assert operation_future._result_type is empty.Empty
    assert operation_future.metadata() is None
    assert operation_future.done() is False
    assert operation_future.running()
