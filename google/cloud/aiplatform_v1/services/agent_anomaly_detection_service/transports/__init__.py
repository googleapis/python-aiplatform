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
from collections import OrderedDict
from typing import Dict, Type, Tuple

from .base import AgentAnomalyDetectionServiceTransport
from .grpc import AgentAnomalyDetectionServiceGrpcTransport
from .grpc_asyncio import AgentAnomalyDetectionServiceGrpcAsyncIOTransport
from .rest import AgentAnomalyDetectionServiceRestTransport
from .rest import AgentAnomalyDetectionServiceRestInterceptor

ASYNC_REST_CLASSES: Tuple[str, ...]
try:
    from .rest_asyncio import AsyncAgentAnomalyDetectionServiceRestTransport
    from .rest_asyncio import (
        AsyncAgentAnomalyDetectionServiceRestInterceptor,
    )  # pragma: NO COVER

    ASYNC_REST_CLASSES = (
        "AsyncAgentAnomalyDetectionServiceRestTransport",
        "AsyncAgentAnomalyDetectionServiceRestInterceptor",
    )  # pragma: NO COVER
    HAS_REST_ASYNC = True  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    ASYNC_REST_CLASSES = ()
    HAS_REST_ASYNC = False


# Compile a registry of transports.
_transport_registry = (
    OrderedDict()
)  # type: Dict[str, Type[AgentAnomalyDetectionServiceTransport]]
_transport_registry["grpc"] = AgentAnomalyDetectionServiceGrpcTransport
_transport_registry["grpc_asyncio"] = AgentAnomalyDetectionServiceGrpcAsyncIOTransport
_transport_registry["rest"] = AgentAnomalyDetectionServiceRestTransport
if HAS_REST_ASYNC:  # pragma: NO COVER
    _transport_registry["rest_asyncio"] = AsyncAgentAnomalyDetectionServiceRestTransport

__all__ = (
    "AgentAnomalyDetectionServiceTransport",
    "AgentAnomalyDetectionServiceGrpcTransport",
    "AgentAnomalyDetectionServiceGrpcAsyncIOTransport",
    "AgentAnomalyDetectionServiceRestTransport",
    "AgentAnomalyDetectionServiceRestInterceptor",
) + ASYNC_REST_CLASSES
