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

import google.auth

try:
    import aiohttp  # type: ignore
    from google.auth.aio.transport.sessions import AsyncAuthorizedSession  # type: ignore
    from google.api_core import rest_streaming_async  # type: ignore
    from google.api_core.operations_v1 import AsyncOperationsRestClient  # type: ignore
except ImportError as e:  # pragma: NO COVER
    raise ImportError(
        "`rest_asyncio` transport requires the library to be installed with the `async_rest` extra. Install the library with the `async_rest` extra using `pip install google-cloud-aiplatform[async_rest]`"
    ) from e

from google.auth import credentials as ga_credentials  # type: ignore
from google.auth.aio import credentials as ga_credentials_async  # type: ignore

from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import operations_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore
from google.api_core import retry_async as retries
from google.api_core import rest_helpers
from google.api_core import rest_streaming_async  # type: ignore
from google.cloud.aiplatform_v1._compat import transcode_request

import google.protobuf

from google.protobuf import json_format
from google.api_core import operations_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore

import json  # type: ignore
import dataclasses
from typing import Any, Dict, List, Callable, Tuple, Optional, Sequence, Union


from google.cloud.aiplatform_v1.types import agent_anomaly_detection_service
from google.longrunning import operations_pb2  # type: ignore


from .rest_base import _BaseAgentAnomalyDetectionServiceRestTransport

from .base import DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO


import logging

try:
    from google.api_core import client_logging  # type: ignore

    CLIENT_LOGGING_SUPPORTED = True  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    CLIENT_LOGGING_SUPPORTED = False

_LOGGER = logging.getLogger(__name__)

try:
    OptionalRetry = Union[retries.AsyncRetry, gapic_v1.method._MethodDefault, None]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.AsyncRetry, object, None]  # type: ignore

DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=f"google-auth@{google.auth.__version__}",
)

DEFAULT_CLIENT_INFO.protobuf_runtime_version = google.protobuf.__version__


class AsyncAgentAnomalyDetectionServiceRestInterceptor:
    """Asynchronous Interceptor for AgentAnomalyDetectionService.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the AsyncAgentAnomalyDetectionServiceRestTransport.

    .. code-block:: python
        class MyCustomAgentAnomalyDetectionServiceInterceptor(AgentAnomalyDetectionServiceRestInterceptor):
            async def pre_aggregate_analyzed_sessions(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_aggregate_analyzed_sessions(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_clear_training_data(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_clear_training_data(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_create_agent_anomaly_detection_scope(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_create_agent_anomaly_detection_scope(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_delete_agent_anomaly_detection_scope(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_delete_agent_anomaly_detection_scope(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_disable_monitored_agent(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_disable_monitored_agent(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_enable_monitored_agent(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_enable_monitored_agent(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_agent_anomaly_detection_scope(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_agent_anomaly_detection_scope(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_analyzed_invocation(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_analyzed_invocation(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_analyzed_session(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_analyzed_session(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_get_monitored_agent(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_monitored_agent(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_agent_anomaly_detection_scopes(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_agent_anomaly_detection_scopes(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_analyzed_invocations(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_analyzed_invocations(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_analyzed_sessions(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_analyzed_sessions(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_monitored_agents(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_monitored_agents(self, response):
                logging.log(f"Received response: {response}")
                return response

        transport = AsyncAgentAnomalyDetectionServiceRestTransport(interceptor=MyCustomAgentAnomalyDetectionServiceInterceptor())
        client = async AgentAnomalyDetectionServiceClient(transport=transport)


    """

    async def pre_aggregate_analyzed_sessions(
        self,
        request: agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for aggregate_analyzed_sessions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_aggregate_analyzed_sessions(
        self,
        response: agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
    ) -> agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse:
        """Post-rpc interceptor for aggregate_analyzed_sessions

        DEPRECATED. Please use the `post_aggregate_analyzed_sessions_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_aggregate_analyzed_sessions` interceptor runs
        before the `post_aggregate_analyzed_sessions_with_metadata` interceptor.
        """
        return response

    async def post_aggregate_analyzed_sessions_with_metadata(
        self,
        response: agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for aggregate_analyzed_sessions

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_aggregate_analyzed_sessions_with_metadata`
        interceptor in new development instead of the `post_aggregate_analyzed_sessions` interceptor.
        When both interceptors are used, this `post_aggregate_analyzed_sessions_with_metadata` interceptor runs after the
        `post_aggregate_analyzed_sessions` interceptor. The (possibly modified) response returned by
        `post_aggregate_analyzed_sessions` will be passed to
        `post_aggregate_analyzed_sessions_with_metadata`.
        """
        return response, metadata

    async def pre_clear_training_data(
        self,
        request: agent_anomaly_detection_service.ClearTrainingDataRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ClearTrainingDataRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for clear_training_data

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_clear_training_data(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for clear_training_data

        DEPRECATED. Please use the `post_clear_training_data_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_clear_training_data` interceptor runs
        before the `post_clear_training_data_with_metadata` interceptor.
        """
        return response

    async def post_clear_training_data_with_metadata(
        self,
        response: operations_pb2.Operation,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[operations_pb2.Operation, Sequence[Tuple[str, Union[str, bytes]]]]:
        """Post-rpc interceptor for clear_training_data

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_clear_training_data_with_metadata`
        interceptor in new development instead of the `post_clear_training_data` interceptor.
        When both interceptors are used, this `post_clear_training_data_with_metadata` interceptor runs after the
        `post_clear_training_data` interceptor. The (possibly modified) response returned by
        `post_clear_training_data` will be passed to
        `post_clear_training_data_with_metadata`.
        """
        return response, metadata

    async def pre_create_agent_anomaly_detection_scope(
        self,
        request: agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for create_agent_anomaly_detection_scope

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_create_agent_anomaly_detection_scope(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for create_agent_anomaly_detection_scope

        DEPRECATED. Please use the `post_create_agent_anomaly_detection_scope_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_create_agent_anomaly_detection_scope` interceptor runs
        before the `post_create_agent_anomaly_detection_scope_with_metadata` interceptor.
        """
        return response

    async def post_create_agent_anomaly_detection_scope_with_metadata(
        self,
        response: operations_pb2.Operation,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[operations_pb2.Operation, Sequence[Tuple[str, Union[str, bytes]]]]:
        """Post-rpc interceptor for create_agent_anomaly_detection_scope

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_create_agent_anomaly_detection_scope_with_metadata`
        interceptor in new development instead of the `post_create_agent_anomaly_detection_scope` interceptor.
        When both interceptors are used, this `post_create_agent_anomaly_detection_scope_with_metadata` interceptor runs after the
        `post_create_agent_anomaly_detection_scope` interceptor. The (possibly modified) response returned by
        `post_create_agent_anomaly_detection_scope` will be passed to
        `post_create_agent_anomaly_detection_scope_with_metadata`.
        """
        return response, metadata

    async def pre_delete_agent_anomaly_detection_scope(
        self,
        request: agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for delete_agent_anomaly_detection_scope

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_delete_agent_anomaly_detection_scope(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for delete_agent_anomaly_detection_scope

        DEPRECATED. Please use the `post_delete_agent_anomaly_detection_scope_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_delete_agent_anomaly_detection_scope` interceptor runs
        before the `post_delete_agent_anomaly_detection_scope_with_metadata` interceptor.
        """
        return response

    async def post_delete_agent_anomaly_detection_scope_with_metadata(
        self,
        response: operations_pb2.Operation,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[operations_pb2.Operation, Sequence[Tuple[str, Union[str, bytes]]]]:
        """Post-rpc interceptor for delete_agent_anomaly_detection_scope

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_delete_agent_anomaly_detection_scope_with_metadata`
        interceptor in new development instead of the `post_delete_agent_anomaly_detection_scope` interceptor.
        When both interceptors are used, this `post_delete_agent_anomaly_detection_scope_with_metadata` interceptor runs after the
        `post_delete_agent_anomaly_detection_scope` interceptor. The (possibly modified) response returned by
        `post_delete_agent_anomaly_detection_scope` will be passed to
        `post_delete_agent_anomaly_detection_scope_with_metadata`.
        """
        return response, metadata

    async def pre_disable_monitored_agent(
        self,
        request: agent_anomaly_detection_service.DisableMonitoredAgentRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.DisableMonitoredAgentRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for disable_monitored_agent

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_disable_monitored_agent(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for disable_monitored_agent

        DEPRECATED. Please use the `post_disable_monitored_agent_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_disable_monitored_agent` interceptor runs
        before the `post_disable_monitored_agent_with_metadata` interceptor.
        """
        return response

    async def post_disable_monitored_agent_with_metadata(
        self,
        response: operations_pb2.Operation,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[operations_pb2.Operation, Sequence[Tuple[str, Union[str, bytes]]]]:
        """Post-rpc interceptor for disable_monitored_agent

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_disable_monitored_agent_with_metadata`
        interceptor in new development instead of the `post_disable_monitored_agent` interceptor.
        When both interceptors are used, this `post_disable_monitored_agent_with_metadata` interceptor runs after the
        `post_disable_monitored_agent` interceptor. The (possibly modified) response returned by
        `post_disable_monitored_agent` will be passed to
        `post_disable_monitored_agent_with_metadata`.
        """
        return response, metadata

    async def pre_enable_monitored_agent(
        self,
        request: agent_anomaly_detection_service.EnableMonitoredAgentRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.EnableMonitoredAgentRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for enable_monitored_agent

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_enable_monitored_agent(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for enable_monitored_agent

        DEPRECATED. Please use the `post_enable_monitored_agent_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_enable_monitored_agent` interceptor runs
        before the `post_enable_monitored_agent_with_metadata` interceptor.
        """
        return response

    async def post_enable_monitored_agent_with_metadata(
        self,
        response: operations_pb2.Operation,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[operations_pb2.Operation, Sequence[Tuple[str, Union[str, bytes]]]]:
        """Post-rpc interceptor for enable_monitored_agent

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_enable_monitored_agent_with_metadata`
        interceptor in new development instead of the `post_enable_monitored_agent` interceptor.
        When both interceptors are used, this `post_enable_monitored_agent_with_metadata` interceptor runs after the
        `post_enable_monitored_agent` interceptor. The (possibly modified) response returned by
        `post_enable_monitored_agent` will be passed to
        `post_enable_monitored_agent_with_metadata`.
        """
        return response, metadata

    async def pre_get_agent_anomaly_detection_scope(
        self,
        request: agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for get_agent_anomaly_detection_scope

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_agent_anomaly_detection_scope(
        self, response: agent_anomaly_detection_service.AgentAnomalyDetectionScope
    ) -> agent_anomaly_detection_service.AgentAnomalyDetectionScope:
        """Post-rpc interceptor for get_agent_anomaly_detection_scope

        DEPRECATED. Please use the `post_get_agent_anomaly_detection_scope_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_get_agent_anomaly_detection_scope` interceptor runs
        before the `post_get_agent_anomaly_detection_scope_with_metadata` interceptor.
        """
        return response

    async def post_get_agent_anomaly_detection_scope_with_metadata(
        self,
        response: agent_anomaly_detection_service.AgentAnomalyDetectionScope,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.AgentAnomalyDetectionScope,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for get_agent_anomaly_detection_scope

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_get_agent_anomaly_detection_scope_with_metadata`
        interceptor in new development instead of the `post_get_agent_anomaly_detection_scope` interceptor.
        When both interceptors are used, this `post_get_agent_anomaly_detection_scope_with_metadata` interceptor runs after the
        `post_get_agent_anomaly_detection_scope` interceptor. The (possibly modified) response returned by
        `post_get_agent_anomaly_detection_scope` will be passed to
        `post_get_agent_anomaly_detection_scope_with_metadata`.
        """
        return response, metadata

    async def pre_get_analyzed_invocation(
        self,
        request: agent_anomaly_detection_service.GetAnalyzedInvocationRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.GetAnalyzedInvocationRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for get_analyzed_invocation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_analyzed_invocation(
        self, response: agent_anomaly_detection_service.AnalyzedInvocation
    ) -> agent_anomaly_detection_service.AnalyzedInvocation:
        """Post-rpc interceptor for get_analyzed_invocation

        DEPRECATED. Please use the `post_get_analyzed_invocation_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_get_analyzed_invocation` interceptor runs
        before the `post_get_analyzed_invocation_with_metadata` interceptor.
        """
        return response

    async def post_get_analyzed_invocation_with_metadata(
        self,
        response: agent_anomaly_detection_service.AnalyzedInvocation,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.AnalyzedInvocation,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for get_analyzed_invocation

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_get_analyzed_invocation_with_metadata`
        interceptor in new development instead of the `post_get_analyzed_invocation` interceptor.
        When both interceptors are used, this `post_get_analyzed_invocation_with_metadata` interceptor runs after the
        `post_get_analyzed_invocation` interceptor. The (possibly modified) response returned by
        `post_get_analyzed_invocation` will be passed to
        `post_get_analyzed_invocation_with_metadata`.
        """
        return response, metadata

    async def pre_get_analyzed_session(
        self,
        request: agent_anomaly_detection_service.GetAnalyzedSessionRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.GetAnalyzedSessionRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for get_analyzed_session

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_analyzed_session(
        self, response: agent_anomaly_detection_service.AnalyzedSession
    ) -> agent_anomaly_detection_service.AnalyzedSession:
        """Post-rpc interceptor for get_analyzed_session

        DEPRECATED. Please use the `post_get_analyzed_session_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_get_analyzed_session` interceptor runs
        before the `post_get_analyzed_session_with_metadata` interceptor.
        """
        return response

    async def post_get_analyzed_session_with_metadata(
        self,
        response: agent_anomaly_detection_service.AnalyzedSession,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.AnalyzedSession,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for get_analyzed_session

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_get_analyzed_session_with_metadata`
        interceptor in new development instead of the `post_get_analyzed_session` interceptor.
        When both interceptors are used, this `post_get_analyzed_session_with_metadata` interceptor runs after the
        `post_get_analyzed_session` interceptor. The (possibly modified) response returned by
        `post_get_analyzed_session` will be passed to
        `post_get_analyzed_session_with_metadata`.
        """
        return response, metadata

    async def pre_get_monitored_agent(
        self,
        request: agent_anomaly_detection_service.GetMonitoredAgentRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.GetMonitoredAgentRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for get_monitored_agent

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_monitored_agent(
        self, response: agent_anomaly_detection_service.MonitoredAgent
    ) -> agent_anomaly_detection_service.MonitoredAgent:
        """Post-rpc interceptor for get_monitored_agent

        DEPRECATED. Please use the `post_get_monitored_agent_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_get_monitored_agent` interceptor runs
        before the `post_get_monitored_agent_with_metadata` interceptor.
        """
        return response

    async def post_get_monitored_agent_with_metadata(
        self,
        response: agent_anomaly_detection_service.MonitoredAgent,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.MonitoredAgent,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for get_monitored_agent

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_get_monitored_agent_with_metadata`
        interceptor in new development instead of the `post_get_monitored_agent` interceptor.
        When both interceptors are used, this `post_get_monitored_agent_with_metadata` interceptor runs after the
        `post_get_monitored_agent` interceptor. The (possibly modified) response returned by
        `post_get_monitored_agent` will be passed to
        `post_get_monitored_agent_with_metadata`.
        """
        return response, metadata

    async def pre_list_agent_anomaly_detection_scopes(
        self,
        request: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for list_agent_anomaly_detection_scopes

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_list_agent_anomaly_detection_scopes(
        self,
        response: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
    ) -> agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse:
        """Post-rpc interceptor for list_agent_anomaly_detection_scopes

        DEPRECATED. Please use the `post_list_agent_anomaly_detection_scopes_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_list_agent_anomaly_detection_scopes` interceptor runs
        before the `post_list_agent_anomaly_detection_scopes_with_metadata` interceptor.
        """
        return response

    async def post_list_agent_anomaly_detection_scopes_with_metadata(
        self,
        response: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for list_agent_anomaly_detection_scopes

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_list_agent_anomaly_detection_scopes_with_metadata`
        interceptor in new development instead of the `post_list_agent_anomaly_detection_scopes` interceptor.
        When both interceptors are used, this `post_list_agent_anomaly_detection_scopes_with_metadata` interceptor runs after the
        `post_list_agent_anomaly_detection_scopes` interceptor. The (possibly modified) response returned by
        `post_list_agent_anomaly_detection_scopes` will be passed to
        `post_list_agent_anomaly_detection_scopes_with_metadata`.
        """
        return response, metadata

    async def pre_list_analyzed_invocations(
        self,
        request: agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for list_analyzed_invocations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_list_analyzed_invocations(
        self, response: agent_anomaly_detection_service.ListAnalyzedInvocationsResponse
    ) -> agent_anomaly_detection_service.ListAnalyzedInvocationsResponse:
        """Post-rpc interceptor for list_analyzed_invocations

        DEPRECATED. Please use the `post_list_analyzed_invocations_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_list_analyzed_invocations` interceptor runs
        before the `post_list_analyzed_invocations_with_metadata` interceptor.
        """
        return response

    async def post_list_analyzed_invocations_with_metadata(
        self,
        response: agent_anomaly_detection_service.ListAnalyzedInvocationsResponse,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListAnalyzedInvocationsResponse,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for list_analyzed_invocations

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_list_analyzed_invocations_with_metadata`
        interceptor in new development instead of the `post_list_analyzed_invocations` interceptor.
        When both interceptors are used, this `post_list_analyzed_invocations_with_metadata` interceptor runs after the
        `post_list_analyzed_invocations` interceptor. The (possibly modified) response returned by
        `post_list_analyzed_invocations` will be passed to
        `post_list_analyzed_invocations_with_metadata`.
        """
        return response, metadata

    async def pre_list_analyzed_sessions(
        self,
        request: agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for list_analyzed_sessions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_list_analyzed_sessions(
        self, response: agent_anomaly_detection_service.ListAnalyzedSessionsResponse
    ) -> agent_anomaly_detection_service.ListAnalyzedSessionsResponse:
        """Post-rpc interceptor for list_analyzed_sessions

        DEPRECATED. Please use the `post_list_analyzed_sessions_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_list_analyzed_sessions` interceptor runs
        before the `post_list_analyzed_sessions_with_metadata` interceptor.
        """
        return response

    async def post_list_analyzed_sessions_with_metadata(
        self,
        response: agent_anomaly_detection_service.ListAnalyzedSessionsResponse,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListAnalyzedSessionsResponse,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for list_analyzed_sessions

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_list_analyzed_sessions_with_metadata`
        interceptor in new development instead of the `post_list_analyzed_sessions` interceptor.
        When both interceptors are used, this `post_list_analyzed_sessions_with_metadata` interceptor runs after the
        `post_list_analyzed_sessions` interceptor. The (possibly modified) response returned by
        `post_list_analyzed_sessions` will be passed to
        `post_list_analyzed_sessions_with_metadata`.
        """
        return response, metadata

    async def pre_list_monitored_agents(
        self,
        request: agent_anomaly_detection_service.ListMonitoredAgentsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListMonitoredAgentsRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for list_monitored_agents

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_list_monitored_agents(
        self, response: agent_anomaly_detection_service.ListMonitoredAgentsResponse
    ) -> agent_anomaly_detection_service.ListMonitoredAgentsResponse:
        """Post-rpc interceptor for list_monitored_agents

        DEPRECATED. Please use the `post_list_monitored_agents_with_metadata`
        interceptor instead.

        Override in a subclass to read or manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code. This `post_list_monitored_agents` interceptor runs
        before the `post_list_monitored_agents_with_metadata` interceptor.
        """
        return response

    async def post_list_monitored_agents_with_metadata(
        self,
        response: agent_anomaly_detection_service.ListMonitoredAgentsResponse,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        agent_anomaly_detection_service.ListMonitoredAgentsResponse,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Post-rpc interceptor for list_monitored_agents

        Override in a subclass to read or manipulate the response or metadata after it
        is returned by the AgentAnomalyDetectionService server but before it is returned to user code.

        We recommend only using this `post_list_monitored_agents_with_metadata`
        interceptor in new development instead of the `post_list_monitored_agents` interceptor.
        When both interceptors are used, this `post_list_monitored_agents_with_metadata` interceptor runs after the
        `post_list_monitored_agents` interceptor. The (possibly modified) response returned by
        `post_list_monitored_agents` will be passed to
        `post_list_monitored_agents_with_metadata`.
        """
        return response, metadata

    async def pre_get_location(
        self,
        request: locations_pb2.GetLocationRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        locations_pb2.GetLocationRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for get_location

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_location(
        self, response: locations_pb2.Location
    ) -> locations_pb2.Location:
        """Post-rpc interceptor for get_location

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_locations(
        self,
        request: locations_pb2.ListLocationsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        locations_pb2.ListLocationsRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for list_locations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_list_locations(
        self, response: locations_pb2.ListLocationsResponse
    ) -> locations_pb2.ListLocationsResponse:
        """Post-rpc interceptor for list_locations

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_iam_policy(
        self,
        request: iam_policy_pb2.GetIamPolicyRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        iam_policy_pb2.GetIamPolicyRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_set_iam_policy(
        self,
        request: iam_policy_pb2.SetIamPolicyRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        iam_policy_pb2.SetIamPolicyRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_set_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_test_iam_permissions(
        self,
        request: iam_policy_pb2.TestIamPermissionsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        iam_policy_pb2.TestIamPermissionsRequest,
        Sequence[Tuple[str, Union[str, bytes]]],
    ]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_test_iam_permissions(
        self, response: iam_policy_pb2.TestIamPermissionsResponse
    ) -> iam_policy_pb2.TestIamPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_cancel_operation(
        self,
        request: operations_pb2.CancelOperationRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        operations_pb2.CancelOperationRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_cancel_operation(self, response: None) -> None:
        """Post-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_operation(
        self,
        request: operations_pb2.DeleteOperationRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        operations_pb2.DeleteOperationRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for delete_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_delete_operation(self, response: None) -> None:
        """Post-rpc interceptor for delete_operation

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_operation(
        self,
        request: operations_pb2.GetOperationRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        operations_pb2.GetOperationRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for get_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_get_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for get_operation

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_operations(
        self,
        request: operations_pb2.ListOperationsRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        operations_pb2.ListOperationsRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for list_operations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_list_operations(
        self, response: operations_pb2.ListOperationsResponse
    ) -> operations_pb2.ListOperationsResponse:
        """Post-rpc interceptor for list_operations

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response

    async def pre_wait_operation(
        self,
        request: operations_pb2.WaitOperationRequest,
        metadata: Sequence[Tuple[str, Union[str, bytes]]],
    ) -> Tuple[
        operations_pb2.WaitOperationRequest, Sequence[Tuple[str, Union[str, bytes]]]
    ]:
        """Pre-rpc interceptor for wait_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the AgentAnomalyDetectionService server.
        """
        return request, metadata

    async def post_wait_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for wait_operation

        Override in a subclass to manipulate the response
        after it is returned by the AgentAnomalyDetectionService server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class AsyncAgentAnomalyDetectionServiceRestStub:
    _session: AsyncAuthorizedSession
    _host: str
    _interceptor: AsyncAgentAnomalyDetectionServiceRestInterceptor


class AsyncAgentAnomalyDetectionServiceRestTransport(
    _BaseAgentAnomalyDetectionServiceRestTransport
):
    """Asynchronous REST backend transport for AgentAnomalyDetectionService.

    A service for managing Agent Anomaly Detection for monitored
    agents.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: Optional[
            Union[ga_credentials.Credentials, ga_credentials_async.Credentials]
        ] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        url_scheme: str = "https",
        interceptor: Optional[AsyncAgentAnomalyDetectionServiceRestInterceptor] = None,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to (default: 'aiplatform.googleapis.com').
            credentials (Optional[Union[google.auth.credentials.Credentials, google.auth.aio.credentials.Credentials]]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you are developing
                your own client library.
            url_scheme (str): the protocol scheme for the API endpoint.  Normally
                "https", but for testing or local servers,
                "http" can be specified.
            interceptor (Optional[AsyncAgentAnomalyDetectionServiceRestInterceptor]): Interceptor used
                to manipulate requests, request metadata, and responses.
        """
        # Run the base constructor
        super().__init__(
            host=host,
            credentials=credentials,
            client_info=client_info,
            always_use_jwt_access=False,
            url_scheme=url_scheme,
            api_audience=None,
        )
        self._session = AsyncAuthorizedSession(self._credentials)  # type: ignore
        self._interceptor = (
            interceptor or AsyncAgentAnomalyDetectionServiceRestInterceptor()
        )
        self._wrap_with_kind = True
        self._prep_wrapped_messages(client_info)
        self._operations_client: Optional[operations_v1.AsyncOperationsRestClient] = (
            None
        )

    def _prep_wrapped_messages(self, client_info):
        """Precompute the wrapped methods, overriding the base class method to use async wrappers."""
        self._wrapped_methods = {
            self.get_agent_anomaly_detection_scope: self._wrap_method(
                self.get_agent_anomaly_detection_scope,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_monitored_agent: self._wrap_method(
                self.get_monitored_agent,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_monitored_agents: self._wrap_method(
                self.list_monitored_agents,
                default_timeout=None,
                client_info=client_info,
            ),
            self.enable_monitored_agent: self._wrap_method(
                self.enable_monitored_agent,
                default_timeout=None,
                client_info=client_info,
            ),
            self.disable_monitored_agent: self._wrap_method(
                self.disable_monitored_agent,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_agent_anomaly_detection_scope: self._wrap_method(
                self.delete_agent_anomaly_detection_scope,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_agent_anomaly_detection_scope: self._wrap_method(
                self.create_agent_anomaly_detection_scope,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_agent_anomaly_detection_scopes: self._wrap_method(
                self.list_agent_anomaly_detection_scopes,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_analyzed_sessions: self._wrap_method(
                self.list_analyzed_sessions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_analyzed_session: self._wrap_method(
                self.get_analyzed_session,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_analyzed_invocations: self._wrap_method(
                self.list_analyzed_invocations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_analyzed_invocation: self._wrap_method(
                self.get_analyzed_invocation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.aggregate_analyzed_sessions: self._wrap_method(
                self.aggregate_analyzed_sessions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.clear_training_data: self._wrap_method(
                self.clear_training_data,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_location: self._wrap_method(
                self.get_location,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_locations: self._wrap_method(
                self.list_locations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_iam_policy: self._wrap_method(
                self.get_iam_policy,
                default_timeout=None,
                client_info=client_info,
            ),
            self.set_iam_policy: self._wrap_method(
                self.set_iam_policy,
                default_timeout=None,
                client_info=client_info,
            ),
            self.test_iam_permissions: self._wrap_method(
                self.test_iam_permissions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_operation: self._wrap_method(
                self.cancel_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_operation: self._wrap_method(
                self.delete_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_operation: self._wrap_method(
                self.get_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_operations: self._wrap_method(
                self.list_operations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.wait_operation: self._wrap_method(
                self.wait_operation,
                default_timeout=None,
                client_info=client_info,
            ),
        }

    def _wrap_method(self, func, *args, **kwargs):
        if self._wrap_with_kind:  # pragma: NO COVER
            kwargs["kind"] = self.kind
        return gapic_v1.method_async.wrap_method(func, *args, **kwargs)

    class _AggregateAnalyzedSessions(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseAggregateAnalyzedSessions,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.AggregateAnalyzedSessions"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse:
            r"""Call the aggregate analyzed
            sessions method over HTTP.

                Args:
                    request (~.agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest):
                        The request object. Request to aggregate AnalyzedSessions across one or more
                    MonitoredAgents. Use the ``-`` wildcard in the
                    monitored_agent segment of the parent to aggregate
                    across all MonitoredAgents in the location.
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                        sent along with the request as metadata. Normally, each value must be of type `str`,
                        but for metadata keys ending with the suffix `-bin`, the corresponding values must
                        be of type `bytes`.

                Returns:
                    ~.agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse:
                        Contains aggregated AnalyzedSession
                    statistics, grouped by MonitoredAgent.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseAggregateAnalyzedSessions._get_http_options()
            )
            request, metadata = await self._interceptor.pre_aggregate_analyzed_sessions(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseAggregateAnalyzedSessions,
                    "_BaseAggregateAnalyzedSessions__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.AggregateAnalyzedSessions",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "AggregateAnalyzedSessions",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._AggregateAnalyzedSessions._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse()
            pb_resp = (
                agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.pb(
                    resp
                )
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_aggregate_analyzed_sessions(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_aggregate_analyzed_sessions_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse.to_json(
                        response
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.aggregate_analyzed_sessions",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "AggregateAnalyzedSessions",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _ClearTrainingData(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseClearTrainingData,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.ClearTrainingData"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.ClearTrainingDataRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the clear training data method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.ClearTrainingDataRequest):
                    The request object. Request message for
                [AgentAnomalyDetectionService.ClearTrainingData][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ClearTrainingData].
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseClearTrainingData._get_http_options()
            )
            request, metadata = await self._interceptor.pre_clear_training_data(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseClearTrainingData,
                    "_BaseClearTrainingData__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ClearTrainingData",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ClearTrainingData",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ClearTrainingData._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_clear_training_data(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = await self._interceptor.post_clear_training_data_with_metadata(
                resp, response_metadata
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.clear_training_data",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ClearTrainingData",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _CreateAgentAnomalyDetectionScope(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseCreateAgentAnomalyDetectionScope,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.CreateAgentAnomalyDetectionScope"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the create agent anomaly
            detection scope method over HTTP.

                Args:
                    request (~.agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest):
                        The request object. Request message for
                    [AgentAnomalyDetectionService.CreateAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.CreateAgentAnomalyDetectionScope].
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                        sent along with the request as metadata. Normally, each value must be of type `str`,
                        but for metadata keys ending with the suffix `-bin`, the corresponding values must
                        be of type `bytes`.

                Returns:
                    ~.operations_pb2.Operation:
                        This resource represents a
                    long-running operation that is the
                    result of a network API call.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseCreateAgentAnomalyDetectionScope._get_http_options()
            )
            request, metadata = (
                await self._interceptor.pre_create_agent_anomaly_detection_scope(
                    request, metadata
                )
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseCreateAgentAnomalyDetectionScope,
                    "_BaseCreateAgentAnomalyDetectionScope__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.CreateAgentAnomalyDetectionScope",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "CreateAgentAnomalyDetectionScope",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._CreateAgentAnomalyDetectionScope._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_create_agent_anomaly_detection_scope(
                resp
            )
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_create_agent_anomaly_detection_scope_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.create_agent_anomaly_detection_scope",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "CreateAgentAnomalyDetectionScope",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _DeleteAgentAnomalyDetectionScope(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseDeleteAgentAnomalyDetectionScope,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.DeleteAgentAnomalyDetectionScope"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the delete agent anomaly
            detection scope method over HTTP.

                Args:
                    request (~.agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest):
                        The request object. Request message for
                    [AgentAnomalyDetectionService.DeleteAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.DeleteAgentAnomalyDetectionScope].
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                        sent along with the request as metadata. Normally, each value must be of type `str`,
                        but for metadata keys ending with the suffix `-bin`, the corresponding values must
                        be of type `bytes`.

                Returns:
                    ~.operations_pb2.Operation:
                        This resource represents a
                    long-running operation that is the
                    result of a network API call.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseDeleteAgentAnomalyDetectionScope._get_http_options()
            )
            request, metadata = (
                await self._interceptor.pre_delete_agent_anomaly_detection_scope(
                    request, metadata
                )
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseDeleteAgentAnomalyDetectionScope,
                    "_BaseDeleteAgentAnomalyDetectionScope__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.DeleteAgentAnomalyDetectionScope",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "DeleteAgentAnomalyDetectionScope",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._DeleteAgentAnomalyDetectionScope._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_delete_agent_anomaly_detection_scope(
                resp
            )
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_delete_agent_anomaly_detection_scope_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.delete_agent_anomaly_detection_scope",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "DeleteAgentAnomalyDetectionScope",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _DisableMonitoredAgent(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseDisableMonitoredAgent,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.DisableMonitoredAgent"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.DisableMonitoredAgentRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the disable monitored agent method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.DisableMonitoredAgentRequest):
                    The request object. Request message for
                [AgentAnomalyDetectionService.DisableMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.DisableMonitoredAgent].
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseDisableMonitoredAgent._get_http_options()
            )
            request, metadata = await self._interceptor.pre_disable_monitored_agent(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseDisableMonitoredAgent,
                    "_BaseDisableMonitoredAgent__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.DisableMonitoredAgent",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "DisableMonitoredAgent",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._DisableMonitoredAgent._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_disable_monitored_agent(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_disable_monitored_agent_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.disable_monitored_agent",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "DisableMonitoredAgent",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _EnableMonitoredAgent(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseEnableMonitoredAgent,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.EnableMonitoredAgent"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.EnableMonitoredAgentRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the enable monitored agent method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.EnableMonitoredAgentRequest):
                    The request object. Request message for
                [AgentAnomalyDetectionService.EnableMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.EnableMonitoredAgent].
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseEnableMonitoredAgent._get_http_options()
            )
            request, metadata = await self._interceptor.pre_enable_monitored_agent(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseEnableMonitoredAgent,
                    "_BaseEnableMonitoredAgent__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.EnableMonitoredAgent",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "EnableMonitoredAgent",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._EnableMonitoredAgent._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = operations_pb2.Operation()
            pb_resp = resp
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_enable_monitored_agent(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = await self._interceptor.post_enable_monitored_agent_with_metadata(
                resp, response_metadata
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.enable_monitored_agent",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "EnableMonitoredAgent",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _GetAgentAnomalyDetectionScope(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAgentAnomalyDetectionScope,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.GetAgentAnomalyDetectionScope"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.AgentAnomalyDetectionScope:
            r"""Call the get agent anomaly
            detection scope method over HTTP.

                Args:
                    request (~.agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest):
                        The request object. Request message for
                    [AgentAnomalyDetectionService.GetAgentAnomalyDetectionScope][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.GetAgentAnomalyDetectionScope].
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                        sent along with the request as metadata. Normally, each value must be of type `str`,
                        but for metadata keys ending with the suffix `-bin`, the corresponding values must
                        be of type `bytes`.

                Returns:
                    ~.agent_anomaly_detection_service.AgentAnomalyDetectionScope:
                        Represents an Agent Anomaly Detection
                    Scope.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAgentAnomalyDetectionScope._get_http_options()
            )
            request, metadata = (
                await self._interceptor.pre_get_agent_anomaly_detection_scope(
                    request, metadata
                )
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAgentAnomalyDetectionScope,
                    "_BaseGetAgentAnomalyDetectionScope__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetAgentAnomalyDetectionScope",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetAgentAnomalyDetectionScope",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetAgentAnomalyDetectionScope._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.AgentAnomalyDetectionScope()
            pb_resp = agent_anomaly_detection_service.AgentAnomalyDetectionScope.pb(
                resp
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_agent_anomaly_detection_scope(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_get_agent_anomaly_detection_scope_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = agent_anomaly_detection_service.AgentAnomalyDetectionScope.to_json(
                        response
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.get_agent_anomaly_detection_scope",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetAgentAnomalyDetectionScope",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _GetAnalyzedInvocation(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAnalyzedInvocation,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.GetAnalyzedInvocation"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.GetAnalyzedInvocationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.AnalyzedInvocation:
            r"""Call the get analyzed invocation method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.GetAnalyzedInvocationRequest):
                    The request object. Request to get the details of a
                specific analyzed invocation.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.agent_anomaly_detection_service.AnalyzedInvocation:
                    Represents an analyzed invocation for
                a monitored agent's session.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAnalyzedInvocation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_analyzed_invocation(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAnalyzedInvocation,
                    "_BaseGetAnalyzedInvocation__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetAnalyzedInvocation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetAnalyzedInvocation",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetAnalyzedInvocation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.AnalyzedInvocation()
            pb_resp = agent_anomaly_detection_service.AnalyzedInvocation.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_analyzed_invocation(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_get_analyzed_invocation_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = (
                        agent_anomaly_detection_service.AnalyzedInvocation.to_json(
                            response
                        )
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.get_analyzed_invocation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetAnalyzedInvocation",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _GetAnalyzedSession(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAnalyzedSession,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.GetAnalyzedSession"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.GetAnalyzedSessionRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.AnalyzedSession:
            r"""Call the get analyzed session method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.GetAnalyzedSessionRequest):
                    The request object. Request to get the details of a
                specific analyzed session.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.agent_anomaly_detection_service.AnalyzedSession:
                    Represents an analyzed session for a
                monitored agent.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAnalyzedSession._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_analyzed_session(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetAnalyzedSession,
                    "_BaseGetAnalyzedSession__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetAnalyzedSession",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetAnalyzedSession",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetAnalyzedSession._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.AnalyzedSession()
            pb_resp = agent_anomaly_detection_service.AnalyzedSession.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_analyzed_session(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = await self._interceptor.post_get_analyzed_session_with_metadata(
                resp, response_metadata
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = (
                        agent_anomaly_detection_service.AnalyzedSession.to_json(
                            response
                        )
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.get_analyzed_session",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetAnalyzedSession",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _GetMonitoredAgent(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetMonitoredAgent,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.GetMonitoredAgent"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.GetMonitoredAgentRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.MonitoredAgent:
            r"""Call the get monitored agent method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.GetMonitoredAgentRequest):
                    The request object. Request message for
                [AgentAnomalyDetectionService.GetMonitoredAgent][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.GetMonitoredAgent].
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.agent_anomaly_detection_service.MonitoredAgent:
                    Represents a monitored agent in a
                specific Location.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetMonitoredAgent._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_monitored_agent(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetMonitoredAgent,
                    "_BaseGetMonitoredAgent__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetMonitoredAgent",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetMonitoredAgent",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetMonitoredAgent._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.MonitoredAgent()
            pb_resp = agent_anomaly_detection_service.MonitoredAgent.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_monitored_agent(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = await self._interceptor.post_get_monitored_agent_with_metadata(
                resp, response_metadata
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = (
                        agent_anomaly_detection_service.MonitoredAgent.to_json(response)
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.get_monitored_agent",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetMonitoredAgent",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _ListAgentAnomalyDetectionScopes(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAgentAnomalyDetectionScopes,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.ListAgentAnomalyDetectionScopes"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse:
            r"""Call the list agent anomaly
            detection scopes method over HTTP.

                Args:
                    request (~.agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest):
                        The request object. Request message for
                    [AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes].
                    retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                        should be retried.
                    timeout (float): The timeout for this request.
                    metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                        sent along with the request as metadata. Normally, each value must be of type `str`,
                        but for metadata keys ending with the suffix `-bin`, the corresponding values must
                        be of type `bytes`.

                Returns:
                    ~.agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse:
                        Response message for
                    [AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListAgentAnomalyDetectionScopes].

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAgentAnomalyDetectionScopes._get_http_options()
            )
            request, metadata = (
                await self._interceptor.pre_list_agent_anomaly_detection_scopes(
                    request, metadata
                )
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAgentAnomalyDetectionScopes,
                    "_BaseListAgentAnomalyDetectionScopes__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ListAgentAnomalyDetectionScopes",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListAgentAnomalyDetectionScopes",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ListAgentAnomalyDetectionScopes._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = (
                agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse()
            )
            pb_resp = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.pb(
                resp
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_agent_anomaly_detection_scopes(
                resp
            )
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_list_agent_anomaly_detection_scopes_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse.to_json(
                        response
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.list_agent_anomaly_detection_scopes",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListAgentAnomalyDetectionScopes",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _ListAnalyzedInvocations(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAnalyzedInvocations,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.ListAnalyzedInvocations"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.ListAnalyzedInvocationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.ListAnalyzedInvocationsResponse:
            r"""Call the list analyzed invocations method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.ListAnalyzedInvocationsRequest):
                    The request object. Request to list analyzed invocations.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.agent_anomaly_detection_service.ListAnalyzedInvocationsResponse:
                    Response to list analyzed
                invocations.

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAnalyzedInvocations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_analyzed_invocations(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAnalyzedInvocations,
                    "_BaseListAnalyzedInvocations__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ListAnalyzedInvocations",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListAnalyzedInvocations",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ListAnalyzedInvocations._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse()
            pb_resp = (
                agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.pb(resp)
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_analyzed_invocations(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = (
                await self._interceptor.post_list_analyzed_invocations_with_metadata(
                    resp, response_metadata
                )
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = agent_anomaly_detection_service.ListAnalyzedInvocationsResponse.to_json(
                        response
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.list_analyzed_invocations",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListAnalyzedInvocations",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _ListAnalyzedSessions(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAnalyzedSessions,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.ListAnalyzedSessions"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.ListAnalyzedSessionsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.ListAnalyzedSessionsResponse:
            r"""Call the list analyzed sessions method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.ListAnalyzedSessionsRequest):
                    The request object. Request to list analyzed sessions.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.agent_anomaly_detection_service.ListAnalyzedSessionsResponse:
                    Response to list analyzed sessions.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAnalyzedSessions._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_analyzed_sessions(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseListAnalyzedSessions,
                    "_BaseListAnalyzedSessions__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ListAnalyzedSessions",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListAnalyzedSessions",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ListAnalyzedSessions._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.ListAnalyzedSessionsResponse()
            pb_resp = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.pb(
                resp
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_analyzed_sessions(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = await self._interceptor.post_list_analyzed_sessions_with_metadata(
                resp, response_metadata
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = agent_anomaly_detection_service.ListAnalyzedSessionsResponse.to_json(
                        response
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.list_analyzed_sessions",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListAnalyzedSessions",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    class _ListMonitoredAgents(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseListMonitoredAgents,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.ListMonitoredAgents"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: agent_anomaly_detection_service.ListMonitoredAgentsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> agent_anomaly_detection_service.ListMonitoredAgentsResponse:
            r"""Call the list monitored agents method over HTTP.

            Args:
                request (~.agent_anomaly_detection_service.ListMonitoredAgentsRequest):
                    The request object. Request message for
                [AgentAnomalyDetectionService.ListMonitoredAgents][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListMonitoredAgents].
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                ~.agent_anomaly_detection_service.ListMonitoredAgentsResponse:
                    Response message for
                [AgentAnomalyDetectionService.ListMonitoredAgents][google.cloud.aiplatform.v1.AgentAnomalyDetectionService.ListMonitoredAgents].

            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseListMonitoredAgents._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_monitored_agents(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseListMonitoredAgents,
                    "_BaseListMonitoredAgents__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=True,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = type(request).to_json(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ListMonitoredAgents",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListMonitoredAgents",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ListMonitoredAgents._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            # Return the response
            resp = agent_anomaly_detection_service.ListMonitoredAgentsResponse()
            pb_resp = agent_anomaly_detection_service.ListMonitoredAgentsResponse.pb(
                resp
            )
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_monitored_agents(resp)
            response_metadata = [(k, str(v)) for k, v in response.headers.items()]
            resp, _ = await self._interceptor.post_list_monitored_agents_with_metadata(
                resp, response_metadata
            )
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = agent_anomaly_detection_service.ListMonitoredAgentsResponse.to_json(
                        response
                    )
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": "OK",  # need to obtain this properly
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.list_monitored_agents",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListMonitoredAgents",
                        "metadata": http_response["headers"],
                        "httpResponse": http_response,
                    },
                )

            return resp

    @property
    def operations_client(self) -> AsyncOperationsRestClient:
        """Create the async client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Only create a new client if we do not already have one.
        if self._operations_client is None:
            http_options: Dict[str, List[Dict[str, str]]] = {
                "google.longrunning.Operations.CancelOperation": [
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/ragEngineConfig/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=reasoningEngines/*/sessions/*/operations/*}:cancel",
                    },
                ],
                "google.longrunning.Operations.DeleteOperation": [
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "delete",
                        "uri": "/v1/{name=reasoningEngines/*/sessions/*/operations/*}",
                    },
                ],
                "google.longrunning.Operations.GetOperation": [
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDeploymentJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/ragEngineConfig/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=reasoningEngines/*/sessions/*/operations/*}",
                    },
                ],
                "google.longrunning.Operations.ListOperations": [
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/agents/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tuningJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/ragEngineConfig}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "get",
                        "uri": "/v1/{name=reasoningEngines/*/sessions/*}/operations",
                    },
                ],
                "google.longrunning.Operations.WaitOperation": [
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/agents/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/apps/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/extensions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/ragEngineConfig/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/ui/{name=projects/*/locations/*/featureGroups/*/featureMonitors/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/ragEngineConfig/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/ragCorpora/*/ragFiles/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/reasoningEngines/*/sessions/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/schedules/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait",
                    },
                    {
                        "method": "post",
                        "uri": "/v1/{name=reasoningEngines/*/sessions/*/operations/*}:wait",
                    },
                ],
            }

            rest_transport = operations_v1.AsyncOperationsRestTransport(  # type: ignore
                host=self._host,
                # use the credentials which are saved
                credentials=self._credentials,  # type: ignore
                http_options=http_options,
                path_prefix="v1",
            )

            self._operations_client = AsyncOperationsRestClient(
                transport=rest_transport
            )

        # Return the client from cache.
        return self._operations_client

    @property
    def aggregate_analyzed_sessions(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest],
        agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
    ]:
        return self._AggregateAnalyzedSessions(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def clear_training_data(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.ClearTrainingDataRequest],
        operations_pb2.Operation,
    ]:
        return self._ClearTrainingData(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def create_agent_anomaly_detection_scope(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest],
        operations_pb2.Operation,
    ]:
        return self._CreateAgentAnomalyDetectionScope(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def delete_agent_anomaly_detection_scope(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest],
        operations_pb2.Operation,
    ]:
        return self._DeleteAgentAnomalyDetectionScope(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def disable_monitored_agent(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.DisableMonitoredAgentRequest],
        operations_pb2.Operation,
    ]:
        return self._DisableMonitoredAgent(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def enable_monitored_agent(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.EnableMonitoredAgentRequest],
        operations_pb2.Operation,
    ]:
        return self._EnableMonitoredAgent(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_agent_anomaly_detection_scope(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest],
        agent_anomaly_detection_service.AgentAnomalyDetectionScope,
    ]:
        return self._GetAgentAnomalyDetectionScope(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_analyzed_invocation(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.GetAnalyzedInvocationRequest],
        agent_anomaly_detection_service.AnalyzedInvocation,
    ]:
        return self._GetAnalyzedInvocation(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_analyzed_session(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.GetAnalyzedSessionRequest],
        agent_anomaly_detection_service.AnalyzedSession,
    ]:
        return self._GetAnalyzedSession(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_monitored_agent(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.GetMonitoredAgentRequest],
        agent_anomaly_detection_service.MonitoredAgent,
    ]:
        return self._GetMonitoredAgent(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_agent_anomaly_detection_scopes(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest],
        agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
    ]:
        return self._ListAgentAnomalyDetectionScopes(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_analyzed_invocations(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.ListAnalyzedInvocationsRequest],
        agent_anomaly_detection_service.ListAnalyzedInvocationsResponse,
    ]:
        return self._ListAnalyzedInvocations(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_analyzed_sessions(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.ListAnalyzedSessionsRequest],
        agent_anomaly_detection_service.ListAnalyzedSessionsResponse,
    ]:
        return self._ListAnalyzedSessions(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_monitored_agents(
        self,
    ) -> Callable[
        [agent_anomaly_detection_service.ListMonitoredAgentsRequest],
        agent_anomaly_detection_service.ListMonitoredAgentsResponse,
    ]:
        return self._ListMonitoredAgents(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_location(self):
        return self._GetLocation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetLocation(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetLocation,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.GetLocation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: locations_pb2.GetLocationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> locations_pb2.Location:
            r"""Call the get location method over HTTP.

            Args:
                request (locations_pb2.GetLocationRequest):
                    The request object for GetLocation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                locations_pb2.Location: Response from GetLocation method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetLocation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_location(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetLocation,
                    "_BaseGetLocation__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetLocation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetLocation",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetLocation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = locations_pb2.Location()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_get_location(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.GetLocation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetLocation",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def list_locations(self):
        return self._ListLocations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListLocations(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseListLocations,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.ListLocations")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: locations_pb2.ListLocationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> locations_pb2.ListLocationsResponse:
            r"""Call the list locations method over HTTP.

            Args:
                request (locations_pb2.ListLocationsRequest):
                    The request object for ListLocations method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                locations_pb2.ListLocationsResponse: Response from ListLocations method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseListLocations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_locations(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseListLocations,
                    "_BaseListLocations__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ListLocations",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListLocations",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ListLocations._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = locations_pb2.ListLocationsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_list_locations(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.ListLocations",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListLocations",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def get_iam_policy(self):
        return self._GetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _GetIamPolicy(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetIamPolicy,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.GetIamPolicy")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: iam_policy_pb2.GetIamPolicyRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> policy_pb2.Policy:
            r"""Call the get iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.GetIamPolicyRequest):
                    The request object for GetIamPolicy method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                policy_pb2.Policy: Response from GetIamPolicy method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetIamPolicy._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_iam_policy(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetIamPolicy,
                    "_BaseGetIamPolicy__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetIamPolicy",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetIamPolicy",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetIamPolicy._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_get_iam_policy(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.GetIamPolicy",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetIamPolicy",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def set_iam_policy(self):
        return self._SetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _SetIamPolicy(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseSetIamPolicy,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.SetIamPolicy")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        async def __call__(
            self,
            request: iam_policy_pb2.SetIamPolicyRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> policy_pb2.Policy:
            r"""Call the set iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.SetIamPolicyRequest):
                    The request object for SetIamPolicy method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                policy_pb2.Policy: Response from SetIamPolicy method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseSetIamPolicy._get_http_options()
            )
            request, metadata = await self._interceptor.pre_set_iam_policy(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseSetIamPolicy,
                    "_BaseSetIamPolicy__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.SetIamPolicy",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "SetIamPolicy",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._SetIamPolicy._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
                body,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_set_iam_policy(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.SetIamPolicy",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "SetIamPolicy",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def test_iam_permissions(self):
        return self._TestIamPermissions(self._session, self._host, self._interceptor)  # type: ignore

    class _TestIamPermissions(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseTestIamPermissions,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.TestIamPermissions"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: iam_policy_pb2.TestIamPermissionsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> iam_policy_pb2.TestIamPermissionsResponse:
            r"""Call the test iam permissions method over HTTP.

            Args:
                request (iam_policy_pb2.TestIamPermissionsRequest):
                    The request object for TestIamPermissions method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                iam_policy_pb2.TestIamPermissionsResponse: Response from TestIamPermissions method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseTestIamPermissions._get_http_options()
            )
            request, metadata = await self._interceptor.pre_test_iam_permissions(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseTestIamPermissions,
                    "_BaseTestIamPermissions__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.TestIamPermissions",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "TestIamPermissions",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._TestIamPermissions._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = iam_policy_pb2.TestIamPermissionsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_test_iam_permissions(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.TestIamPermissions",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "TestIamPermissions",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def cancel_operation(self):
        return self._CancelOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _CancelOperation(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseCancelOperation,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.CancelOperation"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: operations_pb2.CancelOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> None:
            r"""Call the cancel operation method over HTTP.

            Args:
                request (operations_pb2.CancelOperationRequest):
                    The request object for CancelOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseCancelOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_operation(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseCancelOperation,
                    "_BaseCancelOperation__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.CancelOperation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "CancelOperation",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._CancelOperation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            return await self._interceptor.post_cancel_operation(None)

    @property
    def delete_operation(self):
        return self._DeleteOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _DeleteOperation(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseDeleteOperation,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash(
                "AsyncAgentAnomalyDetectionServiceRestTransport.DeleteOperation"
            )

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: operations_pb2.DeleteOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> None:
            r"""Call the delete operation method over HTTP.

            Args:
                request (operations_pb2.DeleteOperationRequest):
                    The request object for DeleteOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseDeleteOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_operation(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseDeleteOperation,
                    "_BaseDeleteOperation__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.DeleteOperation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "DeleteOperation",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._DeleteOperation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            return await self._interceptor.post_delete_operation(None)

    @property
    def get_operation(self):
        return self._GetOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetOperation(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetOperation,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.GetOperation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: operations_pb2.GetOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the get operation method over HTTP.

            Args:
                request (operations_pb2.GetOperationRequest):
                    The request object for GetOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                operations_pb2.Operation: Response from GetOperation method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_operation(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseGetOperation,
                    "_BaseGetOperation__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.GetOperation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetOperation",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._GetOperation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_get_operation(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.GetOperation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "GetOperation",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def list_operations(self):
        return self._ListOperations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListOperations(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseListOperations,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.ListOperations")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: operations_pb2.ListOperationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.ListOperationsResponse:
            r"""Call the list operations method over HTTP.

            Args:
                request (operations_pb2.ListOperationsRequest):
                    The request object for ListOperations method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                operations_pb2.ListOperationsResponse: Response from ListOperations method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseListOperations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_operations(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseListOperations,
                    "_BaseListOperations__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.ListOperations",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListOperations",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._ListOperations._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = operations_pb2.ListOperationsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_list_operations(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.ListOperations",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "ListOperations",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def wait_operation(self):
        return self._WaitOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _WaitOperation(
        _BaseAgentAnomalyDetectionServiceRestTransport._BaseWaitOperation,
        AsyncAgentAnomalyDetectionServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncAgentAnomalyDetectionServiceRestTransport.WaitOperation")

        @staticmethod
        async def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None,
        ):

            uri = transcoded_request["uri"]
            method = transcoded_request["method"]
            headers = dict(metadata)
            headers["Content-Type"] = "application/json"
            response = await getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        async def __call__(
            self,
            request: operations_pb2.WaitOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, Union[str, bytes]]] = (),
        ) -> operations_pb2.Operation:
            r"""Call the wait operation method over HTTP.

            Args:
                request (operations_pb2.WaitOperationRequest):
                    The request object for WaitOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, Union[str, bytes]]]): Key/value pairs which should be
                    sent along with the request as metadata. Normally, each value must be of type `str`,
                    but for metadata keys ending with the suffix `-bin`, the corresponding values must
                    be of type `bytes`.

            Returns:
                operations_pb2.Operation: Response from WaitOperation method.
            """

            http_options = (
                _BaseAgentAnomalyDetectionServiceRestTransport._BaseWaitOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_wait_operation(
                request, metadata
            )
            transcoded_request, body, query_params = transcode_request(
                http_options,
                request,
                required_fields_default_values=getattr(
                    _BaseAgentAnomalyDetectionServiceRestTransport._BaseWaitOperation,
                    "_BaseWaitOperation__REQUIRED_FIELDS_DEFAULT_VALUES",
                    None,
                ),
                rest_numeric_enums=False,
            )

            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                try:
                    request_payload = json_format.MessageToJson(request)
                except:
                    request_payload = None
                http_request = {
                    "payload": request_payload,
                    "requestMethod": method,
                    "requestUrl": request_url,
                    "headers": dict(metadata),
                }
                _LOGGER.debug(
                    f"Sending request for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceClient.WaitOperation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "WaitOperation",
                        "httpRequest": http_request,
                        "metadata": http_request["headers"],
                    },
                )

            # Send the request
            response = await AsyncAgentAnomalyDetectionServiceRestTransport._WaitOperation._get_response(
                self._host,
                metadata,
                query_params,
                self._session,
                timeout,
                transcoded_request,
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                content = await response.read()
                payload = json.loads(content.decode("utf-8"))
                request_url = "{host}{uri}".format(
                    host=self._host, uri=transcoded_request["uri"]
                )
                method = transcoded_request["method"]
                raise core_exceptions.format_http_response_error(response, method, request_url, payload)  # type: ignore

            content = await response.read()
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_wait_operation(resp)
            if CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(
                logging.DEBUG
            ):  # pragma: NO COVER
                try:
                    response_payload = json_format.MessageToJson(resp)
                except:
                    response_payload = None
                http_response = {
                    "payload": response_payload,
                    "headers": dict(response.headers),
                    "status": response.status_code,
                }
                _LOGGER.debug(
                    "Received response for google.cloud.aiplatform_v1.AgentAnomalyDetectionServiceAsyncClient.WaitOperation",
                    extra={
                        "serviceName": "google.cloud.aiplatform.v1.AgentAnomalyDetectionService",
                        "rpcName": "WaitOperation",
                        "httpResponse": http_response,
                        "metadata": http_response["headers"],
                    },
                )
            return resp

    @property
    def kind(self) -> str:
        return "rest_asyncio"

    async def close(self):
        await self._session.close()
