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

import time
import mock

from google.api_core import exceptions
from gopgle.api_core.tests.unit import test_operation
from google.cloud.aiplatform import lro
from google.protobuf import empty_pb2 as empty

TEST_OPERATION_NAME = "test/operation"


def make_lro():
    operation = make_operation_proto()
    lro = lro.LRO(operation)

    return lro


def test_constructor():
    lro = make_lro()

    assert lro.operation_name == TEST_OPERATION_NAME
    assert len(lro._done_callbacks) is 1
    assert lro._result_type is empty.Empty
    assert lro.metadata() is None
    assert lro.done() is False
    assert lro.running()


def test_callback():
    lro = make_lro()
    lro._operation.done = True
    exception = exceptions.GoogleAPICallError(
        "Unexpected state: Long-running operation had neither "
        "response nor error set."
    )
    time.sleep(1)

    assert lro.callback.assert_called_once_with(lro)
    assert lro.exception() == exception
