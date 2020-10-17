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

import functools

from google.api_core import operation as ga_operation
from google.cloud.aiplatform_v1beta1.services.endpoint_service.transports.base import EndpointServiceTransport
from google.protobuf import empty_pb2 as empty

class LRO(ga_operation):
    """A handler for Operation futures.

    Args:
        operation (google.longrunning.operations_pb2.Operation): The
            initial operation.
        result_type (func:`type`): The protobuf type for the operation's
            result.
    """

    def __init__(self, operation, result_type=empty.Empty, **kwargs):
        operations_client = EndpointServiceTransport().operations_client
        refresh = functools.partial(operations_client.get_operation, operation.name)
        cancel = functools.partial(operations_client.cancel_operation, operation.name)
        super().__init__(operation, refresh, cancel, result_type, **kwargs)
        self.operation_name = operation.name
        self.add_done_callback(callback)

    def callback(operation_future):
        """Callback used to set results of operation future.

        Args:
            operation_future (ga_operation.Operation): operation to set result of
        """
        operation_future._set_result_from_operation()