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


class LRO:
    """A handler for operation futures."""

    def __init__(self, operation: google.api_core.operation.Operation):
        """Initialises class with operation.

        Args:
            operation (google.api_core.operation.Operation): operation to handle
        """
        self._operation_future = operation

    def add_update_resource_callback(
        self, resource_noun_obj: google.cloud.aiplatform.base.AiPlatformResourceNoun
    ):
        """Updates resource with result of operation.

        Args:
            resource_noun_obj (google.cloud.aiplatform.base.AiPlatformResourceNoun):
                resource to be updated upon operation completion
        """
        def callback(operation_future):
            result_obj = operation_future.result()
            resource_noun_obj._gca_resource = result_obj

        self._operation_future.add_done_callback(callback)

    def operation_future(self):
        """google.api_core.operation.Operation: underlying operation future"""
        return self._operation_future
