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
from typing import (
    Any,
    AsyncIterable,
    Awaitable,
    Callable,
    Iterable,
    Sequence,
    Tuple,
    Optional,
)

from google.cloud.aiplatform_v1.types import annotation
from google.cloud.aiplatform_v1.types import data_item
from google.cloud.aiplatform_v1.types import dataset
from google.cloud.aiplatform_v1.types import dataset_service


class ListDatasetsPager:
    """A pager for iterating through ``list_datasets`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListDatasetsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``datasets`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListDatasets`` requests and continue to iterate
    through the ``datasets`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListDatasetsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., dataset_service.ListDatasetsResponse],
        request: dataset_service.ListDatasetsRequest,
        response: dataset_service.ListDatasetsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListDatasetsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListDatasetsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = dataset_service.ListDatasetsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[dataset_service.ListDatasetsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[dataset.Dataset]:
        for page in self.pages:
            yield from page.datasets

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListDatasetsAsyncPager:
    """A pager for iterating through ``list_datasets`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListDatasetsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``datasets`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListDatasets`` requests and continue to iterate
    through the ``datasets`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListDatasetsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[dataset_service.ListDatasetsResponse]],
        request: dataset_service.ListDatasetsRequest,
        response: dataset_service.ListDatasetsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListDatasetsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListDatasetsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = dataset_service.ListDatasetsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[dataset_service.ListDatasetsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[dataset.Dataset]:
        async def async_generator():
            async for page in self.pages:
                for response in page.datasets:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListDataItemsPager:
    """A pager for iterating through ``list_data_items`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListDataItemsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``data_items`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListDataItems`` requests and continue to iterate
    through the ``data_items`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListDataItemsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., dataset_service.ListDataItemsResponse],
        request: dataset_service.ListDataItemsRequest,
        response: dataset_service.ListDataItemsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListDataItemsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListDataItemsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = dataset_service.ListDataItemsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[dataset_service.ListDataItemsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[data_item.DataItem]:
        for page in self.pages:
            yield from page.data_items

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListDataItemsAsyncPager:
    """A pager for iterating through ``list_data_items`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListDataItemsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``data_items`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListDataItems`` requests and continue to iterate
    through the ``data_items`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListDataItemsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[dataset_service.ListDataItemsResponse]],
        request: dataset_service.ListDataItemsRequest,
        response: dataset_service.ListDataItemsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListDataItemsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListDataItemsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = dataset_service.ListDataItemsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[dataset_service.ListDataItemsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[data_item.DataItem]:
        async def async_generator():
            async for page in self.pages:
                for response in page.data_items:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListAnnotationsPager:
    """A pager for iterating through ``list_annotations`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAnnotationsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``annotations`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListAnnotations`` requests and continue to iterate
    through the ``annotations`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAnnotationsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., dataset_service.ListAnnotationsResponse],
        request: dataset_service.ListAnnotationsRequest,
        response: dataset_service.ListAnnotationsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAnnotationsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAnnotationsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = dataset_service.ListAnnotationsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[dataset_service.ListAnnotationsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[annotation.Annotation]:
        for page in self.pages:
            yield from page.annotations

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListAnnotationsAsyncPager:
    """A pager for iterating through ``list_annotations`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListAnnotationsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``annotations`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListAnnotations`` requests and continue to iterate
    through the ``annotations`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListAnnotationsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[dataset_service.ListAnnotationsResponse]],
        request: dataset_service.ListAnnotationsRequest,
        response: dataset_service.ListAnnotationsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListAnnotationsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListAnnotationsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = dataset_service.ListAnnotationsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[dataset_service.ListAnnotationsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[annotation.Annotation]:
        async def async_generator():
            async for page in self.pages:
                for response in page.annotations:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)
