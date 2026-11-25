# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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
from google.api_core import gapic_v1
from google.api_core import retry as retries
from google.api_core import retry_async as retries_async
from typing import Any, AsyncIterator, Awaitable, Callable, Sequence, Tuple, Optional, Iterator, Union
try:
    OptionalRetry = Union[retries.Retry, gapic_v1.method._MethodDefault, None]
    OptionalAsyncRetry = Union[retries_async.AsyncRetry, gapic_v1.method._MethodDefault, None]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.Retry, object, None]  # type: ignore
    OptionalAsyncRetry = Union[retries_async.AsyncRetry, object, None]  # type: ignore

from google.cloud.aiplatform_v1.types import agent_anomaly_detection_service


class ListMonitoredAgentsPager:
    """A pager for iterating through ``list_monitored_agents`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListMonitoredAgentsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``monitored_agents`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListMonitoredAgents`` requests and continue to iterate
    through the ``monitored_agents`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListMonitoredAgentsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., agent_anomaly_detection_service.ListMonitoredAgentsResponse],
            request: agent_anomaly_detection_service.ListMonitoredAgentsRequest,
            response: agent_anomaly_detection_service.ListMonitoredAgentsResponse,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListMonitoredAgentsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListMonitoredAgentsResponse):
                The initial response object.
            retry (google.api_core.retry.Retry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListMonitoredAgentsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterator[agent_anomaly_detection_service.ListMonitoredAgentsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterator[agent_anomaly_detection_service.MonitoredAgent]:
        for page in self.pages:
            yield from page.monitored_agents

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListMonitoredAgentsAsyncPager:
    """A pager for iterating through ``list_monitored_agents`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListMonitoredAgentsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``monitored_agents`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListMonitoredAgents`` requests and continue to iterate
    through the ``monitored_agents`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListMonitoredAgentsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., Awaitable[agent_anomaly_detection_service.ListMonitoredAgentsResponse]],
            request: agent_anomaly_detection_service.ListMonitoredAgentsRequest,
            response: agent_anomaly_detection_service.ListMonitoredAgentsResponse,
            *,
            retry: OptionalAsyncRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListMonitoredAgentsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListMonitoredAgentsResponse):
                The initial response object.
            retry (google.api_core.retry.AsyncRetry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListMonitoredAgentsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterator[agent_anomaly_detection_service.ListMonitoredAgentsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response
    def __aiter__(self) -> AsyncIterator[agent_anomaly_detection_service.MonitoredAgent]:
        async def async_generator():
            async for page in self.pages:
                for response in page.monitored_agents:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListAgentAnomalyDetectionScopesPager:
    """A pager for iterating through ``list_agent_anomaly_detection_scopes`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``agent_anomaly_detection_scopes`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListAgentAnomalyDetectionScopes`` requests and continue to iterate
    through the ``agent_anomaly_detection_scopes`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse],
            request: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
            response: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesResponse):
                The initial response object.
            retry (google.api_core.retry.Retry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterator[agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterator[agent_anomaly_detection_service.AgentAnomalyDetectionScope]:
        for page in self.pages:
            yield from page.agent_anomaly_detection_scopes

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListAgentAnomalyDetectionScopesAsyncPager:
    """A pager for iterating through ``list_agent_anomaly_detection_scopes`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``agent_anomaly_detection_scopes`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListAgentAnomalyDetectionScopes`` requests and continue to iterate
    through the ``agent_anomaly_detection_scopes`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., Awaitable[agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse]],
            request: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
            response: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
            *,
            retry: OptionalAsyncRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAgentAnomalyDetectionScopesResponse):
                The initial response object.
            retry (google.api_core.retry.AsyncRetry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterator[agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response
    def __aiter__(self) -> AsyncIterator[agent_anomaly_detection_service.AgentAnomalyDetectionScope]:
        async def async_generator():
            async for page in self.pages:
                for response in page.agent_anomaly_detection_scopes:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListAnalyzedSessionsPager:
    """A pager for iterating through ``list_analyzed_sessions`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``analyzed_sessions`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListAnalyzedSessions`` requests and continue to iterate
    through the ``analyzed_sessions`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., agent_anomaly_detection_service.ListAnalyzedSessionsResponse],
            request: agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
            response: agent_anomaly_detection_service.ListAnalyzedSessionsResponse,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAnalyzedSessionsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse):
                The initial response object.
            retry (google.api_core.retry.Retry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterator[agent_anomaly_detection_service.ListAnalyzedSessionsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterator[agent_anomaly_detection_service.AnalyzedSession]:
        for page in self.pages:
            yield from page.analyzed_sessions

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListAnalyzedSessionsAsyncPager:
    """A pager for iterating through ``list_analyzed_sessions`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``analyzed_sessions`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListAnalyzedSessions`` requests and continue to iterate
    through the ``analyzed_sessions`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., Awaitable[agent_anomaly_detection_service.ListAnalyzedSessionsResponse]],
            request: agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
            response: agent_anomaly_detection_service.ListAnalyzedSessionsResponse,
            *,
            retry: OptionalAsyncRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAnalyzedSessionsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAnalyzedSessionsResponse):
                The initial response object.
            retry (google.api_core.retry.AsyncRetry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListAnalyzedSessionsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterator[agent_anomaly_detection_service.ListAnalyzedSessionsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response
    def __aiter__(self) -> AsyncIterator[agent_anomaly_detection_service.AnalyzedSession]:
        async def async_generator():
            async for page in self.pages:
                for response in page.analyzed_sessions:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListAnalyzedInvocationsPager:
    """A pager for iterating through ``list_analyzed_invocations`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``analyzed_invocations`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListAnalyzedInvocations`` requests and continue to iterate
    through the ``analyzed_invocations`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., agent_anomaly_detection_service.ListAnalyzedInvocationsResponse],
            request: agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
            response: agent_anomaly_detection_service.ListAnalyzedInvocationsResponse,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsResponse):
                The initial response object.
            retry (google.api_core.retry.Retry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterator[agent_anomaly_detection_service.ListAnalyzedInvocationsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterator[agent_anomaly_detection_service.AnalyzedInvocation]:
        for page in self.pages:
            yield from page.analyzed_invocations

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class ListAnalyzedInvocationsAsyncPager:
    """A pager for iterating through ``list_analyzed_invocations`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``analyzed_invocations`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListAnalyzedInvocations`` requests and continue to iterate
    through the ``analyzed_invocations`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., Awaitable[agent_anomaly_detection_service.ListAnalyzedInvocationsResponse]],
            request: agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
            response: agent_anomaly_detection_service.ListAnalyzedInvocationsResponse,
            *,
            retry: OptionalAsyncRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAnalyzedInvocationsResponse):
                The initial response object.
            retry (google.api_core.retry.AsyncRetry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.ListAnalyzedInvocationsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterator[agent_anomaly_detection_service.ListAnalyzedInvocationsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response
    def __aiter__(self) -> AsyncIterator[agent_anomaly_detection_service.AnalyzedInvocation]:
        async def async_generator():
            async for page in self.pages:
                for response in page.analyzed_invocations:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class AggregateAnalyzedSessionsPager:
    """A pager for iterating through ``aggregate_analyzed_sessions`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``agent_aggregates`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``AggregateAnalyzedSessions`` requests and continue to iterate
    through the ``agent_aggregates`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse],
            request: agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
            response: agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse):
                The initial response object.
            retry (google.api_core.retry.Retry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterator[agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterator[agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate]:
        for page in self.pages:
            yield from page.agent_aggregates

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)


class AggregateAnalyzedSessionsAsyncPager:
    """A pager for iterating through ``aggregate_analyzed_sessions`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``agent_aggregates`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``AggregateAnalyzedSessions`` requests and continue to iterate
    through the ``agent_aggregates`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[..., Awaitable[agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse]],
            request: agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
            response: agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
            *,
            retry: OptionalAsyncRetry = gapic_v1.method.DEFAULT,
            timeout: Union[float, object] = gapic_v1.method.DEFAULT,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = ()):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.AggregateAnalyzedSessionsResponse):
                The initial response object.
            retry (google.api_core.retry.AsyncRetry): Designation of what errors,
                if any, should be retried.
            timeout (float): The timeout for this request.
            metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                sent along with the request as metadata. Normally, each value must be of type `str`,
                but for metadata keys ending with the suffix `-bin`, the corresponding values must
                be of type `bytes`.
        """
        self._method = method
        self._request = agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest(request)
        self._response = response
        self._retry = retry
        self._timeout = timeout
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterator[agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, retry=self._retry, timeout=self._timeout, metadata=self._metadata)
            yield self._response
    def __aiter__(self) -> AsyncIterator[agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.AgentAggregate]:
        async def async_generator():
            async for page in self.pages:
                for response in page.agent_aggregates:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)
