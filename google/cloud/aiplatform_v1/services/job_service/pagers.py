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

from google.cloud.aiplatform_v1.types import batch_prediction_job
from google.cloud.aiplatform_v1.types import custom_job
from google.cloud.aiplatform_v1.types import data_labeling_job
from google.cloud.aiplatform_v1.types import hyperparameter_tuning_job
from google.cloud.aiplatform_v1.types import job_service


class ListCustomJobsPager:
    """A pager for iterating through ``list_custom_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListCustomJobsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``custom_jobs`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListCustomJobs`` requests and continue to iterate
    through the ``custom_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListCustomJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., job_service.ListCustomJobsResponse],
        request: job_service.ListCustomJobsRequest,
        response: job_service.ListCustomJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListCustomJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListCustomJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListCustomJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[job_service.ListCustomJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[custom_job.CustomJob]:
        for page in self.pages:
            yield from page.custom_jobs

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListCustomJobsAsyncPager:
    """A pager for iterating through ``list_custom_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListCustomJobsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``custom_jobs`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListCustomJobs`` requests and continue to iterate
    through the ``custom_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListCustomJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[job_service.ListCustomJobsResponse]],
        request: job_service.ListCustomJobsRequest,
        response: job_service.ListCustomJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListCustomJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListCustomJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListCustomJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[job_service.ListCustomJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[custom_job.CustomJob]:
        async def async_generator():
            async for page in self.pages:
                for response in page.custom_jobs:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListDataLabelingJobsPager:
    """A pager for iterating through ``list_data_labeling_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListDataLabelingJobsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``data_labeling_jobs`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListDataLabelingJobs`` requests and continue to iterate
    through the ``data_labeling_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListDataLabelingJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., job_service.ListDataLabelingJobsResponse],
        request: job_service.ListDataLabelingJobsRequest,
        response: job_service.ListDataLabelingJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListDataLabelingJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListDataLabelingJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListDataLabelingJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[job_service.ListDataLabelingJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[data_labeling_job.DataLabelingJob]:
        for page in self.pages:
            yield from page.data_labeling_jobs

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListDataLabelingJobsAsyncPager:
    """A pager for iterating through ``list_data_labeling_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListDataLabelingJobsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``data_labeling_jobs`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListDataLabelingJobs`` requests and continue to iterate
    through the ``data_labeling_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListDataLabelingJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[job_service.ListDataLabelingJobsResponse]],
        request: job_service.ListDataLabelingJobsRequest,
        response: job_service.ListDataLabelingJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListDataLabelingJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListDataLabelingJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListDataLabelingJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[job_service.ListDataLabelingJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[data_labeling_job.DataLabelingJob]:
        async def async_generator():
            async for page in self.pages:
                for response in page.data_labeling_jobs:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListHyperparameterTuningJobsPager:
    """A pager for iterating through ``list_hyperparameter_tuning_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``hyperparameter_tuning_jobs`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListHyperparameterTuningJobs`` requests and continue to iterate
    through the ``hyperparameter_tuning_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., job_service.ListHyperparameterTuningJobsResponse],
        request: job_service.ListHyperparameterTuningJobsRequest,
        response: job_service.ListHyperparameterTuningJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListHyperparameterTuningJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[job_service.ListHyperparameterTuningJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[hyperparameter_tuning_job.HyperparameterTuningJob]:
        for page in self.pages:
            yield from page.hyperparameter_tuning_jobs

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListHyperparameterTuningJobsAsyncPager:
    """A pager for iterating through ``list_hyperparameter_tuning_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``hyperparameter_tuning_jobs`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListHyperparameterTuningJobs`` requests and continue to iterate
    through the ``hyperparameter_tuning_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[
            ..., Awaitable[job_service.ListHyperparameterTuningJobsResponse]
        ],
        request: job_service.ListHyperparameterTuningJobsRequest,
        response: job_service.ListHyperparameterTuningJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListHyperparameterTuningJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListHyperparameterTuningJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(
        self,
    ) -> AsyncIterable[job_service.ListHyperparameterTuningJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(
        self,
    ) -> AsyncIterable[hyperparameter_tuning_job.HyperparameterTuningJob]:
        async def async_generator():
            async for page in self.pages:
                for response in page.hyperparameter_tuning_jobs:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListBatchPredictionJobsPager:
    """A pager for iterating through ``list_batch_prediction_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListBatchPredictionJobsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``batch_prediction_jobs`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListBatchPredictionJobs`` requests and continue to iterate
    through the ``batch_prediction_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListBatchPredictionJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., job_service.ListBatchPredictionJobsResponse],
        request: job_service.ListBatchPredictionJobsRequest,
        response: job_service.ListBatchPredictionJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListBatchPredictionJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListBatchPredictionJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListBatchPredictionJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[job_service.ListBatchPredictionJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request, metadata=self._metadata)
            yield self._response

    def __iter__(self) -> Iterable[batch_prediction_job.BatchPredictionJob]:
        for page in self.pages:
            yield from page.batch_prediction_jobs

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)


class ListBatchPredictionJobsAsyncPager:
    """A pager for iterating through ``list_batch_prediction_jobs`` requests.

    This class thinly wraps an initial
    :class:`google.cloud.aiplatform_v1.types.ListBatchPredictionJobsResponse` object, and
    provides an ``__aiter__`` method to iterate through its
    ``batch_prediction_jobs`` field.

    If there are more pages, the ``__aiter__`` method will make additional
    ``ListBatchPredictionJobs`` requests and continue to iterate
    through the ``batch_prediction_jobs`` field on the
    corresponding responses.

    All the usual :class:`google.cloud.aiplatform_v1.types.ListBatchPredictionJobsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """

    def __init__(
        self,
        method: Callable[..., Awaitable[job_service.ListBatchPredictionJobsResponse]],
        request: job_service.ListBatchPredictionJobsRequest,
        response: job_service.ListBatchPredictionJobsResponse,
        *,
        metadata: Sequence[Tuple[str, str]] = ()
    ):
        """Instantiates the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (google.cloud.aiplatform_v1.types.ListBatchPredictionJobsRequest):
                The initial request object.
            response (google.cloud.aiplatform_v1.types.ListBatchPredictionJobsResponse):
                The initial response object.
            metadata (Sequence[Tuple[str, str]]): Strings which should be
                sent along with the request as metadata.
        """
        self._method = method
        self._request = job_service.ListBatchPredictionJobsRequest(request)
        self._response = response
        self._metadata = metadata

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    async def pages(self) -> AsyncIterable[job_service.ListBatchPredictionJobsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = await self._method(self._request, metadata=self._metadata)
            yield self._response

    def __aiter__(self) -> AsyncIterable[batch_prediction_job.BatchPredictionJob]:
        async def async_generator():
            async for page in self.pages:
                for response in page.batch_prediction_jobs:
                    yield response

        return async_generator()

    def __repr__(self) -> str:
        return "{0}<{1!r}>".format(self.__class__.__name__, self._response)
