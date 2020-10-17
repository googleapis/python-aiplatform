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

from google.api_core import operation as ga_operation
from google.cloud.aiplatform_v1beta1.services.endpoint_service.transports.base import EndpointServiceTransport
from google.protobuf import empty_pb2 as empty

class LRO:
    """A handler for Operation futures"""

    def __init__(self, operation, result_type=empty.Empty, **kwargs):
        """
        Retrieves the operation resource
        """
        transport = DatasetServiceTransport()
        self.result = None
        self.exception = None
        self.operation_name = operation.name
        self._operation_future = ga_operation.from_gapic(
            operation, transport.operations_client, result_type, **kwargs
        )
        self._operation_future.add_done_callback(callback)

    def callback(operation_future):
        """Callback used to set results of operation future.

        Args:
            operation_future (ga_operation.Operation): operation to set result of
        """
        operation_future._set_result_from_operation()

    def cancel(self):
        """Attempt to cancel the operation.
        Returns:
            bool: True if the cancel was made, False if the operation is
                already complete.
        """
        return self._operation_future.cancel()

    def cancelled(self):
        """True if the operation was cancelled."""
        return self._operation_future.cancelled()

    def done(self):
        """True if operation is complete, False otherwise. Will always be opposite of running().
        """
        done = self._operation_future.done()
        if done:
            self.result =  operation_future.result()
            self.exception =  operation_future.exception()

        return done

    def running(self):
        """True if operation is running, False otherwise. Will always be opposite of done().
        """
        return self._operation_future.running()
