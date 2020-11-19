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

import time
import proto

from google.api_core import operation as ga_operation
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils
from typing import Optional, Callable


class LRO:
    """A handler for operation futures."""

    def __init__(
        self,
        operation_future: ga_operation.Operation,
        resource_noun_obj: Optional[base.AiPlatformResourceNoun] = None,
        result_key: Optional[str] = None,
        api_get: Optional[Callable[..., proto.Message]] = None,
    ):
        """Initialises class with operation and optional object to update.

        Args:
            operation_future (ga_operation.Operation):
                Required. Operation future to handle.
            resource_noun_obj (base.AiPlatformResourceNoun):
                Optional. Resource to be updated upon operation completion.
                result_key and api_get also need to be passed.
            result_key (str):
                Optional. Attribute to retrieve from result.
                resource_noun_obj and api_get also need to be passed.
            api_get (Callable[...,proto.Message]):
                Optional. Callable that takes resource name and returns object.
                resource_noun_obj and result_key also need to be passed.
        """
        self._operation_future = operation_future
        if all([resource_noun_obj, result_key, api_get]):
            self.add_update_resource_callback(resource_noun_obj, result_key, api_get)
        elif any([resource_noun_obj, result_key, api_get]):
            raise ValueError(
                """To update resource automatically upon operation completion,
                resource_noun_obj, result_key and api_get have to all be set."""
            )

    def update_resource(
        operation_future: ga_operation.Operation,
        resource_noun_obj: base.AiPlatformResourceNoun,
        result_key: str,
        api_get: Callable[..., proto.Message],
    ):
        """Updates resource with result of operation, blocking if necessary.

        Args:
            operation_future (ga_operation.Operation):
                Required. Operation future that contains result.
            resource_noun_obj (base.AiPlatformResourceNoun):
                Required. Resource to be updated upon operation completion.
            result_key (str):
                Required. Attribute to retrieve from result.
            api_get (Callable[...,proto.Message]):
                Required. Callable that takes resource name and returns object.
        """
        result_value = getattr(operation_future.result(), result_key)
        resource = api_get(name=result_value)
        resource_noun_obj._gca_resource = resource

    def add_update_resource_callback(
        self,
        resource_noun_obj: base.AiPlatformResourceNoun,
        result_key: str,
        api_get: Callable[..., proto.Message],
    ):
        """Updates resource with result of operation, when it completes.

        Args:
            resource_noun_obj (base.AiPlatformResourceNoun):
                Required. Resource to be updated upon operation completion.
            result_key (str):
                Required. Attribute to retrieve from result.
            api_get (Callable[...,proto.Message]):
                Required. Callable that takes resource name and returns object.
        """

        def callback(operation_future):
            self.update_resource(
                operation_future, resource_noun_obj, result_key, api_get
            )

        self._operation_future.add_done_callback(callback)
        # TODO(b/171631203) Add support for queuing operations

    def wait_with_sleep(self):
        """"""
        while not self._operation_future.done:
            time.sleep(utils.ASYNC_SLEEP_TIME)

    def result(self):
        return self._operation_future.result()

    @property
    def operation_future(self) -> ga_operation.Operation:
        """ga_operation.Operation: underlying operation future"""
        return self._operation_future
