# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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
from collections import OrderedDict
from typing import Dict, Type, Tuple

from .base import EndpointServiceTransport
from .grpc import EndpointServiceGrpcTransport
from .grpc_asyncio import EndpointServiceGrpcAsyncIOTransport
from .rest import EndpointServiceRestTransport
from .rest import EndpointServiceRestInterceptor
ASYNC_REST_CLASSES: Tuple[str, ...]
try:
    from .rest_asyncio import AsyncEndpointServiceRestTransport
    from .rest_asyncio import AsyncEndpointServiceRestInterceptor
    ASYNC_REST_CLASSES = ('AsyncEndpointServiceRestTransport', 'AsyncEndpointServiceRestInterceptor')
    HAS_REST_ASYNC = True
except ImportError:  # pragma: NO COVER
    ASYNC_REST_CLASSES = ()
    HAS_REST_ASYNC = False


# Compile a registry of transports.
_transport_registry = OrderedDict()  # type: Dict[str, Type[EndpointServiceTransport]]
_transport_registry['grpc'] = EndpointServiceGrpcTransport
_transport_registry['grpc_asyncio'] = EndpointServiceGrpcAsyncIOTransport
_transport_registry['rest'] = EndpointServiceRestTransport
if HAS_REST_ASYNC:  # pragma: NO COVER
    _transport_registry['rest_asyncio'] = AsyncEndpointServiceRestTransport

__all__ = (
    'EndpointServiceTransport',
    'EndpointServiceGrpcTransport',
    'EndpointServiceGrpcAsyncIOTransport',
    'EndpointServiceRestTransport',
    'EndpointServiceRestInterceptor',
) + ASYNC_REST_CLASSES