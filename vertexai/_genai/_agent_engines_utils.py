# Copyright 2025 Google LLC
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
"""Utility functions for agent engines."""

from typing import Any, Callable, Coroutine, Iterator, AsyncIterator
from . import types


def _wrap_query_operation(*, method_name: str) -> Callable[..., Any]:
    """Wraps an Agent Engine method, creating a callable for `query` API.

    This function creates a callable object that executes the specified
    Agent Engine method using the `query` API.  It handles the creation of
    the API request and the processing of the API response.

    Args:
        method_name: The name of the Agent Engine method to call.
        doc: Documentation string for the method.

    Returns:
        A callable object that executes the method on the Agent Engine via
        the `query` API.
    """

    def _method(self: types.AgentEngine, **kwargs) -> Any:
        if not self.api_client:
            raise ValueError("api_client is not initialized.")
        if not self.api_resource:
            raise ValueError("api_resource is not initialized.")
        response = self.api_client._query(
            name=self.api_resource.name,
            config={
                "class_method": method_name,
                "input": kwargs,
                "include_all_fields": True,
            },
        )
        return response.output

    return _method


def _wrap_async_query_operation(
    *, method_name: str
) -> Callable[..., Coroutine[Any, Any, Any]]:
    """Wraps an Agent Engine method, creating an async callable for `query` API.

    This function creates a callable object that executes the specified
    Agent Engine method asynchronously using the `query` API. It handles the
    creation of the API request and the processing of the API response.

    Args:
        method_name: The name of the Agent Engine method to call.
        doc: Documentation string for the method.

    Returns:
        A callable object that executes the method on the Agent Engine via
        the `query` API.
    """

    async def _method(self: types.AgentEngine, **kwargs):
        if not self.api_async_client:
            raise ValueError("api_async_client is not initialized.")
        if not self.api_resource:
            raise ValueError("api_resource is not initialized.")
        response = await self.api_async_client._query(
            name=self.api_resource.name,
            config={
                "class_method": method_name,
                "input": kwargs,
                "include_all_fields": True,
            },
        )
        return response.output

    return _method


def _wrap_stream_query_operation(*, method_name: str) -> Callable[..., Iterator[Any]]:
    """Wraps an Agent Engine method, creating a callable for `stream_query` API.

    This function creates a callable object that executes the specified
    Agent Engine method using the `stream_query` API.  It handles the
    creation of the API request and the processing of the API response.

    Args:
        method_name: The name of the Agent Engine method to call.
        doc: Documentation string for the method.

    Returns:
        A callable object that executes the method on the Agent Engine via
        the `stream_query` API.
    """

    def _method(self: types.AgentEngine, **kwargs) -> Iterator[Any]:
        if not self.api_client:
            raise ValueError("api_client is not initialized.")
        if not self.api_resource:
            raise ValueError("api_resource is not initialized.")
        for response in self.api_client._stream_query(
            name=self.api_resource.name,
            config={
                "class_method": method_name,
                "input": kwargs,
                "include_all_fields": True,
            },
        ):
            yield response

    return _method


def _wrap_async_stream_query_operation(
    *, method_name: str
) -> Callable[..., AsyncIterator[Any]]:
    """Wraps an Agent Engine method, creating an async callable for `stream_query` API.

    This function creates a callable object that executes the specified
    Agent Engine method using the `stream_query` API.  It handles the
    creation of the API request and the processing of the API response.

    Args:
        method_name: The name of the Agent Engine method to call.
        doc: Documentation string for the method.

    Returns:
        A callable object that executes the method on the Agent Engine via
        the `stream_query` API.
    """

    async def _method(self: types.AgentEngine, **kwargs):
        if not self.api_client:
            raise ValueError("api_client is not initialized.")
        if not self.api_resource:
            raise ValueError("api_resource is not initialized.")
        for response in self.api_client._stream_query(
            name=self.api_resource.name,
            config={
                "class_method": method_name,
                "input": kwargs,
                "include_all_fields": True,
            },
        ):
            yield response

    return _method
