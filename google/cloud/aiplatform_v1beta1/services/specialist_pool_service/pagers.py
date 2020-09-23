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

from typing import Any, Callable, Iterable

from google.cloud.aiplatform_v1beta1.types import specialist_pool
from google.cloud.aiplatform_v1beta1.types import specialist_pool_service


class ListSpecialistPoolsPager:
    """A pager for iterating through ``list_specialist_pools`` requests.

    This class thinly wraps an initial
    :class:`~.specialist_pool_service.ListSpecialistPoolsResponse` object, and
    provides an ``__iter__`` method to iterate through its
    ``specialist_pools`` field.

    If there are more pages, the ``__iter__`` method will make additional
    ``ListSpecialistPools`` requests and continue to iterate
    through the ``specialist_pools`` field on the
    corresponding responses.

    All the usual :class:`~.specialist_pool_service.ListSpecialistPoolsResponse`
    attributes are available on the pager. If multiple requests are made, only
    the most recent response is retained, and thus used for attribute lookup.
    """
    def __init__(self,
            method: Callable[[specialist_pool_service.ListSpecialistPoolsRequest],
                specialist_pool_service.ListSpecialistPoolsResponse],
            request: specialist_pool_service.ListSpecialistPoolsRequest,
            response: specialist_pool_service.ListSpecialistPoolsResponse):
        """Instantiate the pager.

        Args:
            method (Callable): The method that was originally called, and
                which instantiated this pager.
            request (:class:`~.specialist_pool_service.ListSpecialistPoolsRequest`):
                The initial request object.
            response (:class:`~.specialist_pool_service.ListSpecialistPoolsResponse`):
                The initial response object.
        """
        self._method = method
        self._request = specialist_pool_service.ListSpecialistPoolsRequest(request)
        self._response = response

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)

    @property
    def pages(self) -> Iterable[specialist_pool_service.ListSpecialistPoolsResponse]:
        yield self._response
        while self._response.next_page_token:
            self._request.page_token = self._response.next_page_token
            self._response = self._method(self._request)
            yield self._response

    def __iter__(self) -> Iterable[specialist_pool.SpecialistPool]:
        for page in self.pages:
            yield from page.specialist_pools

    def __repr__(self) -> str:
        return '{0}<{1!r}>'.format(self.__class__.__name__, self._response)
