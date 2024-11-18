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

from google.auth.transport.requests import AuthorizedSession  # type: ignore
import json  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.api_core import exceptions as core_exceptions
from google.api_core import retry as retries
from google.api_core import rest_helpers
from google.api_core import rest_streaming
from google.api_core import gapic_v1

from google.protobuf import json_format
from google.api_core import operations_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2 # type: ignore

from requests import __version__ as requests_version
import dataclasses
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
import warnings


from google.cloud.aiplatform_v1.types import genai_tuning_service
from google.cloud.aiplatform_v1.types import tuning_job
from google.cloud.aiplatform_v1.types import tuning_job as gca_tuning_job
from google.protobuf import empty_pb2  # type: ignore
from google.longrunning import operations_pb2  # type: ignore


from .rest_base import _BaseGenAiTuningServiceRestTransport
from .base import DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO

try:
    OptionalRetry = Union[retries.Retry, gapic_v1.method._MethodDefault, None]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.Retry, object, None]  # type: ignore


DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=f"requests@{requests_version}",
)


class GenAiTuningServiceRestInterceptor:
    """Interceptor for GenAiTuningService.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the GenAiTuningServiceRestTransport.

    .. code-block:: python
        class MyCustomGenAiTuningServiceInterceptor(GenAiTuningServiceRestInterceptor):
            def pre_cancel_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def pre_create_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_create_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_get_tuning_job(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_get_tuning_job(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_list_tuning_jobs(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_list_tuning_jobs(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_rebase_tuned_model(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_rebase_tuned_model(self, response):
                logging.log(f"Received response: {response}")
                return response

        transport = GenAiTuningServiceRestTransport(interceptor=MyCustomGenAiTuningServiceInterceptor())
        client = GenAiTuningServiceClient(transport=transport)


    """
    def pre_cancel_tuning_job(self, request: genai_tuning_service.CancelTuningJobRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[genai_tuning_service.CancelTuningJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def pre_create_tuning_job(self, request: genai_tuning_service.CreateTuningJobRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[genai_tuning_service.CreateTuningJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for create_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_create_tuning_job(self, response: gca_tuning_job.TuningJob) -> gca_tuning_job.TuningJob:
        """Post-rpc interceptor for create_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_get_tuning_job(self, request: genai_tuning_service.GetTuningJobRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[genai_tuning_service.GetTuningJobRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_tuning_job

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_get_tuning_job(self, response: tuning_job.TuningJob) -> tuning_job.TuningJob:
        """Post-rpc interceptor for get_tuning_job

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_list_tuning_jobs(self, request: genai_tuning_service.ListTuningJobsRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[genai_tuning_service.ListTuningJobsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_tuning_jobs

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_list_tuning_jobs(self, response: genai_tuning_service.ListTuningJobsResponse) -> genai_tuning_service.ListTuningJobsResponse:
        """Post-rpc interceptor for list_tuning_jobs

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_rebase_tuned_model(self, request: genai_tuning_service.RebaseTunedModelRequest, metadata: Sequence[Tuple[str, str]]) -> Tuple[genai_tuning_service.RebaseTunedModelRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for rebase_tuned_model

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_rebase_tuned_model(self, response: operations_pb2.Operation) -> operations_pb2.Operation:
        """Post-rpc interceptor for rebase_tuned_model

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_get_location(
        self, request: locations_pb2.GetLocationRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[locations_pb2.GetLocationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_location

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_get_location(
        self, response: locations_pb2.Location
    ) -> locations_pb2.Location:
        """Post-rpc interceptor for get_location

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_list_locations(
        self, request: locations_pb2.ListLocationsRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[locations_pb2.ListLocationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_locations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_list_locations(
        self, response: locations_pb2.ListLocationsResponse
    ) -> locations_pb2.ListLocationsResponse:
        """Post-rpc interceptor for list_locations

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_get_iam_policy(
        self, request: iam_policy_pb2.GetIamPolicyRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[iam_policy_pb2.GetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_get_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_set_iam_policy(
        self, request: iam_policy_pb2.SetIamPolicyRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[iam_policy_pb2.SetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_set_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_test_iam_permissions(
        self, request: iam_policy_pb2.TestIamPermissionsRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[iam_policy_pb2.TestIamPermissionsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_test_iam_permissions(
        self, response: iam_policy_pb2.TestIamPermissionsResponse
    ) -> iam_policy_pb2.TestIamPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_cancel_operation(
        self, request: operations_pb2.CancelOperationRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[operations_pb2.CancelOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_cancel_operation(
        self, response: None
    ) -> None:
        """Post-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_operation(
        self, request: operations_pb2.DeleteOperationRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[operations_pb2.DeleteOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_delete_operation(
        self, response: None
    ) -> None:
        """Post-rpc interceptor for delete_operation

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_get_operation(
        self, request: operations_pb2.GetOperationRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[operations_pb2.GetOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_get_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for get_operation

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_list_operations(
        self, request: operations_pb2.ListOperationsRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[operations_pb2.ListOperationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_operations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_list_operations(
        self, response: operations_pb2.ListOperationsResponse
    ) -> operations_pb2.ListOperationsResponse:
        """Post-rpc interceptor for list_operations

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response

    def pre_wait_operation(
        self, request: operations_pb2.WaitOperationRequest, metadata: Sequence[Tuple[str, str]]
    ) -> Tuple[operations_pb2.WaitOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for wait_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the GenAiTuningService server.
        """
        return request, metadata

    def post_wait_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for wait_operation

        Override in a subclass to manipulate the response
        after it is returned by the GenAiTuningService server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class GenAiTuningServiceRestStub:
    _session: AuthorizedSession
    _host: str
    _interceptor: GenAiTuningServiceRestInterceptor


class GenAiTuningServiceRestTransport(_BaseGenAiTuningServiceRestTransport):
    """REST backend synchronous transport for GenAiTuningService.

    A service for creating and managing GenAI Tuning Jobs.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """

    def __init__(self, *,
            host: str = 'aiplatform.googleapis.com',
            credentials: Optional[ga_credentials.Credentials] = None,
            credentials_file: Optional[str] = None,
            scopes: Optional[Sequence[str]] = None,
            client_cert_source_for_mtls: Optional[Callable[[
                ], Tuple[bytes, bytes]]] = None,
            quota_project_id: Optional[str] = None,
            client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
            always_use_jwt_access: Optional[bool] = False,
            url_scheme: str = 'https',
            interceptor: Optional[GenAiTuningServiceRestInterceptor] = None,
            api_audience: Optional[str] = None,
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

            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if ``channel`` is provided.
            scopes (Optional(Sequence[str])): A list of scopes. This argument is
                ignored if ``channel`` is provided.
            client_cert_source_for_mtls (Callable[[], Tuple[bytes, bytes]]): Client
                certificate to configure mutual TLS HTTP channel. It is ignored
                if ``channel`` is provided.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you are developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
            url_scheme: the protocol scheme for the API endpoint.  Normally
                "https", but for testing or local servers,
                "http" can be specified.
        """
        # Run the base constructor
        # TODO(yon-mg): resolve other ctor params i.e. scopes, quota, etc.
        # TODO: When custom host (api_endpoint) is set, `scopes` must *also* be set on the
        # credentials object
        super().__init__(
            host=host,
            credentials=credentials,
            client_info=client_info,
            always_use_jwt_access=always_use_jwt_access,
            url_scheme=url_scheme,
            api_audience=api_audience
        )
        self._session = AuthorizedSession(
            self._credentials, default_host=self.DEFAULT_HOST)
        self._operations_client: Optional[operations_v1.AbstractOperationsClient] = None
        if client_cert_source_for_mtls:
            self._session.configure_mtls_channel(client_cert_source_for_mtls)
        self._interceptor = interceptor or GenAiTuningServiceRestInterceptor()
        self._prep_wrapped_messages(client_info)

    @property
    def operations_client(self) -> operations_v1.AbstractOperationsClient:
        """Create the client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Only create a new client if we do not already have one.
        if self._operations_client is None:
            http_options: Dict[str, List[Dict[str, str]]] = {
                'google.longrunning.Operations.CancelOperation': [
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/agents/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/apps/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/extensions/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/indexes/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/schedules/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/indexes/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/schedules/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:cancel',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:cancel',
                    },
                ],
                'google.longrunning.Operations.DeleteOperation': [
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/agents/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/apps/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/endpoints/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/extensionControllers/*}/operations',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/extensions/*}/operations',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/customJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/indexes/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/schedules/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/endpoints/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/customJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/indexes/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/schedules/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}',
                    },
                    {
                        'method': 'delete',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}',
                    },
                ],
                'google.longrunning.Operations.GetOperation': [
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/agents/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/apps/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/edgeDeploymentJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/endpoints/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/extensions/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/customJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/indexes/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/schedules/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/endpoints/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/customJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tuningJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/indexes/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/schedules/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}',
                    },
                ],
                'google.longrunning.Operations.ListOperations': [
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/agents/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/apps/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/deploymentResourcePools/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/edgeDevices/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/endpoints/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/extensionControllers/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/extensions/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/customJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/dataLabelingJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tuningJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/indexes/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/indexEndpoints/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/modelMonitors/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/migratableResources/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/models/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/evaluations/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimes/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/trials/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/trainingPipelines/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/persistentResources/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/pipelineJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/schedules/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/specialistPools/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/deploymentResourcePools/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/endpoints/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/customJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/dataLabelingJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tuningJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/indexes/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/indexEndpoints/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/executions/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/migratableResources/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/models/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/evaluations/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/notebookExecutionJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimes/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/trials/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/trainingPipelines/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/persistentResources/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/pipelineJobs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/schedules/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/specialistPools/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*}/operations',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait',
                    },
                    {
                        'method': 'get',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait',
                    },
                ],
                'google.longrunning.Operations.WaitOperation': [
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/agents/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/apps/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/edgeDevices/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/endpoints/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/extensionControllers/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/extensions/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/customJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tuningJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/indexes/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/modelMonitors/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/schedules/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/ui/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/savedQueries/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/annotationSpecs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/datasets/*/dataItems/*/annotations/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/deploymentResourcePools/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/endpoints/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featurestores/*/entityTypes/*/features/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/customJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/dataLabelingJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/hyperparameterTuningJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/indexes/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/indexEndpoints/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/artifacts/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/contexts/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/metadataStores/*/executions/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/modelDeploymentMonitoringJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/migratableResources/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/models/*/evaluations/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/notebookExecutionJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimes/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/notebookRuntimeTemplates/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/studies/*/trials/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/trainingPipelines/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/persistentResources/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/pipelineJobs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/schedules/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/specialistPools/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/tensorboards/*/experiments/*/runs/*/timeSeries/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featureOnlineStores/*/featureViews/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/operations/*}:wait',
                    },
                    {
                        'method': 'post',
                        'uri': '/v1/{name=projects/*/locations/*/featureGroups/*/features/*/operations/*}:wait',
                    },
                ],
            }

            rest_transport = operations_v1.OperationsRestTransport(
                    host=self._host,
                    # use the credentials which are saved
                    credentials=self._credentials,
                    scopes=self._scopes,
                    http_options=http_options,
                    path_prefix="v1")

            self._operations_client = operations_v1.AbstractOperationsClient(transport=rest_transport)

        # Return the client from cache.
        return self._operations_client

    class _CancelTuningJob(_BaseGenAiTuningServiceRestTransport._BaseCancelTuningJob, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.CancelTuningJob")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                )
            return response

        def __call__(self,
                request: genai_tuning_service.CancelTuningJobRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: Optional[float]=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ):
            r"""Call the cancel tuning job method over HTTP.

            Args:
                request (~.genai_tuning_service.CancelTuningJobRequest):
                    The request object. Request message for
                [GenAiTuningService.CancelTuningJob][google.cloud.aiplatform.v1.GenAiTuningService.CancelTuningJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseCancelTuningJob._get_http_options()
            request, metadata = self._interceptor.pre_cancel_tuning_job(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseCancelTuningJob._get_transcoded_request(http_options, request)

            body = _BaseGenAiTuningServiceRestTransport._BaseCancelTuningJob._get_request_body_json(transcoded_request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseCancelTuningJob._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._CancelTuningJob._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request, body)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

    class _CreateTuningJob(_BaseGenAiTuningServiceRestTransport._BaseCreateTuningJob, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.CreateTuningJob")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                )
            return response

        def __call__(self,
                request: genai_tuning_service.CreateTuningJobRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: Optional[float]=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> gca_tuning_job.TuningJob:
            r"""Call the create tuning job method over HTTP.

            Args:
                request (~.genai_tuning_service.CreateTuningJobRequest):
                    The request object. Request message for
                [GenAiTuningService.CreateTuningJob][google.cloud.aiplatform.v1.GenAiTuningService.CreateTuningJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.gca_tuning_job.TuningJob:
                    Represents a TuningJob that runs with
                Google owned models.

            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseCreateTuningJob._get_http_options()
            request, metadata = self._interceptor.pre_create_tuning_job(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseCreateTuningJob._get_transcoded_request(http_options, request)

            body = _BaseGenAiTuningServiceRestTransport._BaseCreateTuningJob._get_request_body_json(transcoded_request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseCreateTuningJob._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._CreateTuningJob._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request, body)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = gca_tuning_job.TuningJob()
            pb_resp = gca_tuning_job.TuningJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_create_tuning_job(resp)
            return resp

    class _GetTuningJob(_BaseGenAiTuningServiceRestTransport._BaseGetTuningJob, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.GetTuningJob")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
                request: genai_tuning_service.GetTuningJobRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: Optional[float]=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> tuning_job.TuningJob:
            r"""Call the get tuning job method over HTTP.

            Args:
                request (~.genai_tuning_service.GetTuningJobRequest):
                    The request object. Request message for
                [GenAiTuningService.GetTuningJob][google.cloud.aiplatform.v1.GenAiTuningService.GetTuningJob].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.tuning_job.TuningJob:
                    Represents a TuningJob that runs with
                Google owned models.

            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseGetTuningJob._get_http_options()
            request, metadata = self._interceptor.pre_get_tuning_job(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseGetTuningJob._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseGetTuningJob._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._GetTuningJob._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = tuning_job.TuningJob()
            pb_resp = tuning_job.TuningJob.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_get_tuning_job(resp)
            return resp

    class _ListTuningJobs(_BaseGenAiTuningServiceRestTransport._BaseListTuningJobs, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.ListTuningJobs")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
                request: genai_tuning_service.ListTuningJobsRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: Optional[float]=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> genai_tuning_service.ListTuningJobsResponse:
            r"""Call the list tuning jobs method over HTTP.

            Args:
                request (~.genai_tuning_service.ListTuningJobsRequest):
                    The request object. Request message for
                [GenAiTuningService.ListTuningJobs][google.cloud.aiplatform.v1.GenAiTuningService.ListTuningJobs].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.genai_tuning_service.ListTuningJobsResponse:
                    Response message for
                [GenAiTuningService.ListTuningJobs][google.cloud.aiplatform.v1.GenAiTuningService.ListTuningJobs]

            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseListTuningJobs._get_http_options()
            request, metadata = self._interceptor.pre_list_tuning_jobs(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseListTuningJobs._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseListTuningJobs._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._ListTuningJobs._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = genai_tuning_service.ListTuningJobsResponse()
            pb_resp = genai_tuning_service.ListTuningJobsResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_list_tuning_jobs(resp)
            return resp

    class _RebaseTunedModel(_BaseGenAiTuningServiceRestTransport._BaseRebaseTunedModel, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.RebaseTunedModel")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                )
            return response

        def __call__(self,
                request: genai_tuning_service.RebaseTunedModelRequest, *,
                retry: OptionalRetry=gapic_v1.method.DEFAULT,
                timeout: Optional[float]=None,
                metadata: Sequence[Tuple[str, str]]=(),
                ) -> operations_pb2.Operation:
            r"""Call the rebase tuned model method over HTTP.

            Args:
                request (~.genai_tuning_service.RebaseTunedModelRequest):
                    The request object. Request message for
                [GenAiTuningService.RebaseTunedModel][google.cloud.aiplatform.v1.GenAiTuningService.RebaseTunedModel].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.operations_pb2.Operation:
                    This resource represents a
                long-running operation that is the
                result of a network API call.

            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseRebaseTunedModel._get_http_options()
            request, metadata = self._interceptor.pre_rebase_tuned_model(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseRebaseTunedModel._get_transcoded_request(http_options, request)

            body = _BaseGenAiTuningServiceRestTransport._BaseRebaseTunedModel._get_request_body_json(transcoded_request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseRebaseTunedModel._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._RebaseTunedModel._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request, body)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = operations_pb2.Operation()
            json_format.Parse(response.content, resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_rebase_tuned_model(resp)
            return resp

    @property
    def cancel_tuning_job(self) -> Callable[
            [genai_tuning_service.CancelTuningJobRequest],
            empty_pb2.Empty]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CancelTuningJob(self._session, self._host, self._interceptor) # type: ignore

    @property
    def create_tuning_job(self) -> Callable[
            [genai_tuning_service.CreateTuningJobRequest],
            gca_tuning_job.TuningJob]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._CreateTuningJob(self._session, self._host, self._interceptor) # type: ignore

    @property
    def get_tuning_job(self) -> Callable[
            [genai_tuning_service.GetTuningJobRequest],
            tuning_job.TuningJob]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GetTuningJob(self._session, self._host, self._interceptor) # type: ignore

    @property
    def list_tuning_jobs(self) -> Callable[
            [genai_tuning_service.ListTuningJobsRequest],
            genai_tuning_service.ListTuningJobsResponse]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ListTuningJobs(self._session, self._host, self._interceptor) # type: ignore

    @property
    def rebase_tuned_model(self) -> Callable[
            [genai_tuning_service.RebaseTunedModelRequest],
            operations_pb2.Operation]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._RebaseTunedModel(self._session, self._host, self._interceptor) # type: ignore

    @property
    def get_location(self):
        return self._GetLocation(self._session, self._host, self._interceptor) # type: ignore

    class _GetLocation(_BaseGenAiTuningServiceRestTransport._BaseGetLocation, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.GetLocation")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: locations_pb2.GetLocationRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> locations_pb2.Location:

            r"""Call the get location method over HTTP.

            Args:
                request (locations_pb2.GetLocationRequest):
                    The request object for GetLocation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.Location: Response from GetLocation method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseGetLocation._get_http_options()
            request, metadata = self._interceptor.pre_get_location(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseGetLocation._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseGetLocation._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._GetLocation._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = locations_pb2.Location()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_get_location(resp)
            return resp

    @property
    def list_locations(self):
        return self._ListLocations(self._session, self._host, self._interceptor) # type: ignore

    class _ListLocations(_BaseGenAiTuningServiceRestTransport._BaseListLocations, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.ListLocations")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: locations_pb2.ListLocationsRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> locations_pb2.ListLocationsResponse:

            r"""Call the list locations method over HTTP.

            Args:
                request (locations_pb2.ListLocationsRequest):
                    The request object for ListLocations method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.ListLocationsResponse: Response from ListLocations method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseListLocations._get_http_options()
            request, metadata = self._interceptor.pre_list_locations(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseListLocations._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseListLocations._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._ListLocations._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = locations_pb2.ListLocationsResponse()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_list_locations(resp)
            return resp

    @property
    def get_iam_policy(self):
        return self._GetIamPolicy(self._session, self._host, self._interceptor) # type: ignore

    class _GetIamPolicy(_BaseGenAiTuningServiceRestTransport._BaseGetIamPolicy, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.GetIamPolicy")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: iam_policy_pb2.GetIamPolicyRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> policy_pb2.Policy:

            r"""Call the get iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.GetIamPolicyRequest):
                    The request object for GetIamPolicy method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from GetIamPolicy method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseGetIamPolicy._get_http_options()
            request, metadata = self._interceptor.pre_get_iam_policy(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseGetIamPolicy._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseGetIamPolicy._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._GetIamPolicy._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_get_iam_policy(resp)
            return resp

    @property
    def set_iam_policy(self):
        return self._SetIamPolicy(self._session, self._host, self._interceptor) # type: ignore

    class _SetIamPolicy(_BaseGenAiTuningServiceRestTransport._BaseSetIamPolicy, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.SetIamPolicy")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                )
            return response

        def __call__(self,
            request: iam_policy_pb2.SetIamPolicyRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> policy_pb2.Policy:

            r"""Call the set iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.SetIamPolicyRequest):
                    The request object for SetIamPolicy method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from SetIamPolicy method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseSetIamPolicy._get_http_options()
            request, metadata = self._interceptor.pre_set_iam_policy(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseSetIamPolicy._get_transcoded_request(http_options, request)

            body = _BaseGenAiTuningServiceRestTransport._BaseSetIamPolicy._get_request_body_json(transcoded_request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseSetIamPolicy._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._SetIamPolicy._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request, body)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_set_iam_policy(resp)
            return resp

    @property
    def test_iam_permissions(self):
        return self._TestIamPermissions(self._session, self._host, self._interceptor) # type: ignore

    class _TestIamPermissions(_BaseGenAiTuningServiceRestTransport._BaseTestIamPermissions, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.TestIamPermissions")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: iam_policy_pb2.TestIamPermissionsRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> iam_policy_pb2.TestIamPermissionsResponse:

            r"""Call the test iam permissions method over HTTP.

            Args:
                request (iam_policy_pb2.TestIamPermissionsRequest):
                    The request object for TestIamPermissions method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                iam_policy_pb2.TestIamPermissionsResponse: Response from TestIamPermissions method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseTestIamPermissions._get_http_options()
            request, metadata = self._interceptor.pre_test_iam_permissions(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseTestIamPermissions._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseTestIamPermissions._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._TestIamPermissions._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = iam_policy_pb2.TestIamPermissionsResponse()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_test_iam_permissions(resp)
            return resp

    @property
    def cancel_operation(self):
        return self._CancelOperation(self._session, self._host, self._interceptor) # type: ignore

    class _CancelOperation(_BaseGenAiTuningServiceRestTransport._BaseCancelOperation, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.CancelOperation")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: operations_pb2.CancelOperationRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> None:

            r"""Call the cancel operation method over HTTP.

            Args:
                request (operations_pb2.CancelOperationRequest):
                    The request object for CancelOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseCancelOperation._get_http_options()
            request, metadata = self._interceptor.pre_cancel_operation(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseCancelOperation._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseCancelOperation._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._CancelOperation._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            return self._interceptor.post_cancel_operation(None)

    @property
    def delete_operation(self):
        return self._DeleteOperation(self._session, self._host, self._interceptor) # type: ignore

    class _DeleteOperation(_BaseGenAiTuningServiceRestTransport._BaseDeleteOperation, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.DeleteOperation")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: operations_pb2.DeleteOperationRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> None:

            r"""Call the delete operation method over HTTP.

            Args:
                request (operations_pb2.DeleteOperationRequest):
                    The request object for DeleteOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseDeleteOperation._get_http_options()
            request, metadata = self._interceptor.pre_delete_operation(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseDeleteOperation._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseDeleteOperation._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._DeleteOperation._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            return self._interceptor.post_delete_operation(None)

    @property
    def get_operation(self):
        return self._GetOperation(self._session, self._host, self._interceptor) # type: ignore

    class _GetOperation(_BaseGenAiTuningServiceRestTransport._BaseGetOperation, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.GetOperation")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: operations_pb2.GetOperationRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> operations_pb2.Operation:

            r"""Call the get operation method over HTTP.

            Args:
                request (operations_pb2.GetOperationRequest):
                    The request object for GetOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from GetOperation method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseGetOperation._get_http_options()
            request, metadata = self._interceptor.pre_get_operation(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseGetOperation._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseGetOperation._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._GetOperation._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_get_operation(resp)
            return resp

    @property
    def list_operations(self):
        return self._ListOperations(self._session, self._host, self._interceptor) # type: ignore

    class _ListOperations(_BaseGenAiTuningServiceRestTransport._BaseListOperations, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.ListOperations")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: operations_pb2.ListOperationsRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> operations_pb2.ListOperationsResponse:

            r"""Call the list operations method over HTTP.

            Args:
                request (operations_pb2.ListOperationsRequest):
                    The request object for ListOperations method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.ListOperationsResponse: Response from ListOperations method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseListOperations._get_http_options()
            request, metadata = self._interceptor.pre_list_operations(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseListOperations._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseListOperations._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._ListOperations._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = operations_pb2.ListOperationsResponse()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_list_operations(resp)
            return resp

    @property
    def wait_operation(self):
        return self._WaitOperation(self._session, self._host, self._interceptor) # type: ignore

    class _WaitOperation(_BaseGenAiTuningServiceRestTransport._BaseWaitOperation, GenAiTuningServiceRestStub):
        def __hash__(self):
            return hash("GenAiTuningServiceRestTransport.WaitOperation")

        @staticmethod
        def _get_response(
            host,
            metadata,
            query_params,
            session,
            timeout,
            transcoded_request,
            body=None):

            uri = transcoded_request['uri']
            method = transcoded_request['method']
            headers = dict(metadata)
            headers['Content-Type'] = 'application/json'
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                )
            return response

        def __call__(self,
            request: operations_pb2.WaitOperationRequest, *,
            retry: OptionalRetry=gapic_v1.method.DEFAULT,
            timeout: Optional[float]=None,
            metadata: Sequence[Tuple[str, str]]=(),
            ) -> operations_pb2.Operation:

            r"""Call the wait operation method over HTTP.

            Args:
                request (operations_pb2.WaitOperationRequest):
                    The request object for WaitOperation method.
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from WaitOperation method.
            """

            http_options = _BaseGenAiTuningServiceRestTransport._BaseWaitOperation._get_http_options()
            request, metadata = self._interceptor.pre_wait_operation(request, metadata)
            transcoded_request = _BaseGenAiTuningServiceRestTransport._BaseWaitOperation._get_transcoded_request(http_options, request)

            # Jsonify the query params
            query_params = _BaseGenAiTuningServiceRestTransport._BaseWaitOperation._get_query_params_json(transcoded_request)

            # Send the request
            response = GenAiTuningServiceRestTransport._WaitOperation._get_response(self._host, metadata, query_params, self._session, timeout, transcoded_request)

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_wait_operation(resp)
            return resp

    @property
    def kind(self) -> str:
        return "rest"

    def close(self):
        self._session.close()


__all__=(
    'GenAiTuningServiceRestTransport',
)