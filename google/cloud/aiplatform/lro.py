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

import threading

from google.api_core import ga_operation


class LRO:
    """A handler for Operation futures"""

    def __init__(self, operation, operations_client, result_type, **kwargs):
        self._operation_future = ga_operation.from_gapic(
            operation, operations_client, result_type, **kwargs
        )
        self.result = None
        self.exception = None
        self._poll_until_finish()

    def callback(operation_future):
        self._operation_future._set_result_from_operation()
        self.result = operation_future.result()
        self.exception = operation_future.exception()

    def done(self):
        return self._operation_future.done()

    def _poll_until_finish(self):
        self._operation_future.add_done_callback(callback)

    def running(self):
        return self._operation_future.running()
