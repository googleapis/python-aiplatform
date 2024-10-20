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

from .base import DatasetServiceTransport
from .grpc import DatasetServiceGrpcTransport
from .grpc_asyncio import DatasetServiceGrpcAsyncIOTransport
from .rest import DatasetServiceRestTransport
from .rest import DatasetServiceRestInterceptor

ASYNC_REST_CLASSES: Tuple[str, ...]
try:
    from .rest_asyncio import AsyncDatasetServiceRestTransport
    from .rest_asyncio import AsyncDatasetServiceRestInterceptor

    ASYNC_REST_CLASSES = (
        "AsyncDatasetServiceRestTransport",
        "AsyncDatasetServiceRestInterceptor",
    )
    HAS_REST_ASYNC = True
except ImportError:  # pragma: NO COVER
    ASYNC_REST_CLASSES = ()
    HAS_REST_ASYNC = False


# Compile a registry of transports.
_transport_registry = OrderedDict()  # type: Dict[str, Type[DatasetServiceTransport]]
_transport_registry["grpc"] = DatasetServiceGrpcTransport
_transport_registry["grpc_asyncio"] = DatasetServiceGrpcAsyncIOTransport
_transport_registry["rest"] = DatasetServiceRestTransport
if HAS_REST_ASYNC:  # pragma: NO COVER
    _transport_registry["rest_asyncio"] = AsyncDatasetServiceRestTransport

__all__ = (
    "DatasetServiceTransport",
    "DatasetServiceGrpcTransport",
    "DatasetServiceGrpcAsyncIOTransport",
    "DatasetServiceRestTransport",
    "DatasetServiceRestInterceptor",
) + ASYNC_REST_CLASSES
