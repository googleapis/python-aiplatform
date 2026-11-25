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
import abc
from typing import Awaitable, Callable, Dict, Optional, Sequence, Union

from google.cloud.aiplatform_v1 import gapic_version as package_version

import google.auth  # type: ignore
import google.api_core
from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.api_core import retry as retries
from google.api_core import operations_v1
from google.auth import credentials as ga_credentials  # type: ignore
from google.oauth2 import service_account # type: ignore
import google.protobuf

from google.cloud.aiplatform_v1.types import agent_anomaly_detection_service
from google.cloud.location import locations_pb2 # type: ignore
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2 # type: ignore

DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(gapic_version=package_version.__version__)
DEFAULT_CLIENT_INFO.protobuf_runtime_version = google.protobuf.__version__


class AgentAnomalyDetectionServiceTransport(abc.ABC):
    """Abstract transport class for AgentAnomalyDetectionService."""

    AUTH_SCOPES = (
        'https://www.googleapis.com/auth/cloud-platform',
    )

    DEFAULT_HOST: str = 'aiplatform.googleapis.com'

    def __init__(
            self, *,
            host: str = DEFAULT_HOST,
            credentials: Optional[ga_credentials.Credentials] = None,
            credentials_file: Optional[str] = None,
            scopes: Optional[Sequence[str]] = None,
            quota_project_id: Optional[str] = None,
            client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
            always_use_jwt_access: Optional[bool] = False,
            api_audience: Optional[str] = None,
            **kwargs,
            ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to (default: 'aiplatform.googleapis.com').
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            credentials_file (Optional[str]): Deprecated. A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials. This argument will be
                removed in the next major version of this library.
            scopes (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
            api_audience (Optional[str]): The intended audience for the API calls
                to the service that will be set when using certain 3rd party
                authentication flows. Audience is typically a resource identifier.
                If not set, the host value will be used as a default.
        """

        # Save the scopes.
        self._scopes = scopes
        if not hasattr(self, "_ignore_credentials"):
            self._ignore_credentials: bool = False

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise core_exceptions.DuplicateCredentialArgs("'credentials_file' and 'credentials' are mutually exclusive")

        if credentials_file is not None:
            credentials, _ = google.auth.load_credentials_from_file(
                                credentials_file,
                                scopes=scopes,
                                quota_project_id=quota_project_id,
                                default_scopes=self.AUTH_SCOPES,
                            )
        elif credentials is None and not self._ignore_credentials:
            credentials, _ = google.auth.default(scopes=scopes, quota_project_id=quota_project_id, default_scopes=self.AUTH_SCOPES)
            # Don't apply audience if the credentials file passed from user.
            if hasattr(credentials, "with_gdch_audience"):
                credentials = credentials.with_gdch_audience(api_audience if api_audience else host)

        # If the credentials are service account credentials, then always try to use self signed JWT.
        if always_use_jwt_access and isinstance(credentials, service_account.Credentials) and hasattr(service_account.Credentials, "with_always_use_jwt_access"):
            credentials = credentials.with_always_use_jwt_access(True)

        # Save the credentials.
        self._credentials = credentials

        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ':' not in host:
            host += ':443'
        self._host = host

        self._wrapped_methods: Dict[Callable, Callable] = {}

    @property
    def host(self):
        return self._host

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.get_agent_anomaly_detection_scope: gapic_v1.method.wrap_method(
                self.get_agent_anomaly_detection_scope,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_monitored_agent: gapic_v1.method.wrap_method(
                self.get_monitored_agent,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_monitored_agents: gapic_v1.method.wrap_method(
                self.list_monitored_agents,
                default_timeout=None,
                client_info=client_info,
            ),
            self.enable_monitored_agent: gapic_v1.method.wrap_method(
                self.enable_monitored_agent,
                default_timeout=None,
                client_info=client_info,
            ),
            self.disable_monitored_agent: gapic_v1.method.wrap_method(
                self.disable_monitored_agent,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_agent_anomaly_detection_scope: gapic_v1.method.wrap_method(
                self.delete_agent_anomaly_detection_scope,
                default_timeout=None,
                client_info=client_info,
            ),
            self.create_agent_anomaly_detection_scope: gapic_v1.method.wrap_method(
                self.create_agent_anomaly_detection_scope,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_agent_anomaly_detection_scopes: gapic_v1.method.wrap_method(
                self.list_agent_anomaly_detection_scopes,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_analyzed_sessions: gapic_v1.method.wrap_method(
                self.list_analyzed_sessions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_analyzed_session: gapic_v1.method.wrap_method(
                self.get_analyzed_session,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_analyzed_invocations: gapic_v1.method.wrap_method(
                self.list_analyzed_invocations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_analyzed_invocation: gapic_v1.method.wrap_method(
                self.get_analyzed_invocation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.aggregate_analyzed_sessions: gapic_v1.method.wrap_method(
                self.aggregate_analyzed_sessions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.clear_training_data: gapic_v1.method.wrap_method(
                self.clear_training_data,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_location: gapic_v1.method.wrap_method(
                self.get_location,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_locations: gapic_v1.method.wrap_method(
                self.list_locations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_iam_policy: gapic_v1.method.wrap_method(
                self.get_iam_policy,
                default_timeout=None,
                client_info=client_info,
            ),
            self.set_iam_policy: gapic_v1.method.wrap_method(
                self.set_iam_policy,
                default_timeout=None,
                client_info=client_info,
            ),
            self.test_iam_permissions: gapic_v1.method.wrap_method(
                self.test_iam_permissions,
                default_timeout=None,
                client_info=client_info,
            ),
            self.cancel_operation: gapic_v1.method.wrap_method(
                self.cancel_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.delete_operation: gapic_v1.method.wrap_method(
                self.delete_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.get_operation: gapic_v1.method.wrap_method(
                self.get_operation,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_operations: gapic_v1.method.wrap_method(
                self.list_operations,
                default_timeout=None,
                client_info=client_info,
            ),
            self.wait_operation: gapic_v1.method.wrap_method(
                self.wait_operation,
                default_timeout=None,
                client_info=client_info,
            ),
         }

    def close(self):
        """Closes resources associated with the transport.

       .. warning::
            Only call this method if the transport is NOT shared
            with other clients - this may cause errors in other clients!
        """
        raise NotImplementedError()

    @property
    def operations_client(self):
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def get_agent_anomaly_detection_scope(self) -> Callable[
            [agent_anomaly_detection_service.GetAgentAnomalyDetectionScopeRequest],
            Union[
                agent_anomaly_detection_service.AgentAnomalyDetectionScope,
                Awaitable[agent_anomaly_detection_service.AgentAnomalyDetectionScope]
            ]]:
        raise NotImplementedError()

    @property
    def get_monitored_agent(self) -> Callable[
            [agent_anomaly_detection_service.GetMonitoredAgentRequest],
            Union[
                agent_anomaly_detection_service.MonitoredAgent,
                Awaitable[agent_anomaly_detection_service.MonitoredAgent]
            ]]:
        raise NotImplementedError()

    @property
    def list_monitored_agents(self) -> Callable[
            [agent_anomaly_detection_service.ListMonitoredAgentsRequest],
            Union[
                agent_anomaly_detection_service.ListMonitoredAgentsResponse,
                Awaitable[agent_anomaly_detection_service.ListMonitoredAgentsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def enable_monitored_agent(self) -> Callable[
            [agent_anomaly_detection_service.EnableMonitoredAgentRequest],
            Union[
                operations_pb2.Operation,
                Awaitable[operations_pb2.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def disable_monitored_agent(self) -> Callable[
            [agent_anomaly_detection_service.DisableMonitoredAgentRequest],
            Union[
                operations_pb2.Operation,
                Awaitable[operations_pb2.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def delete_agent_anomaly_detection_scope(self) -> Callable[
            [agent_anomaly_detection_service.DeleteAgentAnomalyDetectionScopeRequest],
            Union[
                operations_pb2.Operation,
                Awaitable[operations_pb2.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_agent_anomaly_detection_scope(self) -> Callable[
            [agent_anomaly_detection_service.CreateAgentAnomalyDetectionScopeRequest],
            Union[
                operations_pb2.Operation,
                Awaitable[operations_pb2.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def list_agent_anomaly_detection_scopes(self) -> Callable[
            [agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesRequest],
            Union[
                agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse,
                Awaitable[agent_anomaly_detection_service.ListAgentAnomalyDetectionScopesResponse]
            ]]:
        raise NotImplementedError()

    @property
    def list_analyzed_sessions(self) -> Callable[
            [agent_anomaly_detection_service.ListAnalyzedSessionsRequest],
            Union[
                agent_anomaly_detection_service.ListAnalyzedSessionsResponse,
                Awaitable[agent_anomaly_detection_service.ListAnalyzedSessionsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def get_analyzed_session(self) -> Callable[
            [agent_anomaly_detection_service.GetAnalyzedSessionRequest],
            Union[
                agent_anomaly_detection_service.AnalyzedSession,
                Awaitable[agent_anomaly_detection_service.AnalyzedSession]
            ]]:
        raise NotImplementedError()

    @property
    def list_analyzed_invocations(self) -> Callable[
            [agent_anomaly_detection_service.ListAnalyzedInvocationsRequest],
            Union[
                agent_anomaly_detection_service.ListAnalyzedInvocationsResponse,
                Awaitable[agent_anomaly_detection_service.ListAnalyzedInvocationsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def get_analyzed_invocation(self) -> Callable[
            [agent_anomaly_detection_service.GetAnalyzedInvocationRequest],
            Union[
                agent_anomaly_detection_service.AnalyzedInvocation,
                Awaitable[agent_anomaly_detection_service.AnalyzedInvocation]
            ]]:
        raise NotImplementedError()

    @property
    def aggregate_analyzed_sessions(self) -> Callable[
            [agent_anomaly_detection_service.AggregateAnalyzedSessionsRequest],
            Union[
                agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse,
                Awaitable[agent_anomaly_detection_service.AggregateAnalyzedSessionsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def clear_training_data(self) -> Callable[
            [agent_anomaly_detection_service.ClearTrainingDataRequest],
            Union[
                operations_pb2.Operation,
                Awaitable[operations_pb2.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def list_operations(
        self,
    ) -> Callable[
        [operations_pb2.ListOperationsRequest],
        Union[operations_pb2.ListOperationsResponse, Awaitable[operations_pb2.ListOperationsResponse]],
    ]:
        raise NotImplementedError()

    @property
    def get_operation(
        self,
    ) -> Callable[
        [operations_pb2.GetOperationRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def cancel_operation(
        self,
    ) -> Callable[
        [operations_pb2.CancelOperationRequest],
        None,
    ]:
        raise NotImplementedError()

    @property
    def delete_operation(
        self,
    ) -> Callable[
        [operations_pb2.DeleteOperationRequest],
        None,
    ]:
        raise NotImplementedError()

    @property
    def wait_operation(
        self,
    ) -> Callable[
        [operations_pb2.WaitOperationRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def set_iam_policy(
        self,
    ) -> Callable[
        [iam_policy_pb2.SetIamPolicyRequest],
        Union[policy_pb2.Policy, Awaitable[policy_pb2.Policy]],
    ]:
        raise NotImplementedError()

    @property
    def get_iam_policy(
        self,
    ) -> Callable[
        [iam_policy_pb2.GetIamPolicyRequest],
        Union[policy_pb2.Policy, Awaitable[policy_pb2.Policy]],
    ]:
        raise NotImplementedError()

    @property
    def test_iam_permissions(
        self,
    ) -> Callable[
        [iam_policy_pb2.TestIamPermissionsRequest],
        Union[
            iam_policy_pb2.TestIamPermissionsResponse,
            Awaitable[iam_policy_pb2.TestIamPermissionsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_location(self,
    ) -> Callable[
        [locations_pb2.GetLocationRequest],
        Union[locations_pb2.Location, Awaitable[locations_pb2.Location]],
    ]:
        raise NotImplementedError()

    @property
    def list_locations(self,
    ) -> Callable[
        [locations_pb2.ListLocationsRequest],
        Union[locations_pb2.ListLocationsResponse, Awaitable[locations_pb2.ListLocationsResponse]],
    ]:
        raise NotImplementedError()

    @property
    def kind(self) -> str:
        raise NotImplementedError()


__all__ = (
    'AgentAnomalyDetectionServiceTransport',
)
