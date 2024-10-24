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
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore

from requests import __version__ as requests_version
import dataclasses
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union
import warnings


from google.api import httpbody_pb2  # type: ignore
from google.cloud.aiplatform_v1.types import prediction_service
from google.longrunning import operations_pb2  # type: ignore


from .rest_base import _BasePredictionServiceRestTransport
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


class PredictionServiceRestInterceptor:
    """Interceptor for PredictionService.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the PredictionServiceRestTransport.

    .. code-block:: python
        class MyCustomPredictionServiceInterceptor(PredictionServiceRestInterceptor):
            def pre_direct_predict(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_direct_predict(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_direct_raw_predict(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_direct_raw_predict(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_explain(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_explain(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_generate_content(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_generate_content(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_predict(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_predict(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_raw_predict(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_raw_predict(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_server_streaming_predict(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_server_streaming_predict(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_stream_generate_content(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_stream_generate_content(self, response):
                logging.log(f"Received response: {response}")
                return response

            def pre_stream_raw_predict(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            def post_stream_raw_predict(self, response):
                logging.log(f"Received response: {response}")
                return response

        transport = PredictionServiceRestTransport(interceptor=MyCustomPredictionServiceInterceptor())
        client = PredictionServiceClient(transport=transport)


    """

    def pre_direct_predict(
        self,
        request: prediction_service.DirectPredictRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.DirectPredictRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for direct_predict

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_direct_predict(
        self, response: prediction_service.DirectPredictResponse
    ) -> prediction_service.DirectPredictResponse:
        """Post-rpc interceptor for direct_predict

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_direct_raw_predict(
        self,
        request: prediction_service.DirectRawPredictRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.DirectRawPredictRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for direct_raw_predict

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_direct_raw_predict(
        self, response: prediction_service.DirectRawPredictResponse
    ) -> prediction_service.DirectRawPredictResponse:
        """Post-rpc interceptor for direct_raw_predict

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_explain(
        self,
        request: prediction_service.ExplainRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.ExplainRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for explain

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_explain(
        self, response: prediction_service.ExplainResponse
    ) -> prediction_service.ExplainResponse:
        """Post-rpc interceptor for explain

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_generate_content(
        self,
        request: prediction_service.GenerateContentRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.GenerateContentRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for generate_content

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_generate_content(
        self, response: prediction_service.GenerateContentResponse
    ) -> prediction_service.GenerateContentResponse:
        """Post-rpc interceptor for generate_content

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_predict(
        self,
        request: prediction_service.PredictRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.PredictRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for predict

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_predict(
        self, response: prediction_service.PredictResponse
    ) -> prediction_service.PredictResponse:
        """Post-rpc interceptor for predict

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_raw_predict(
        self,
        request: prediction_service.RawPredictRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.RawPredictRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for raw_predict

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_raw_predict(
        self, response: httpbody_pb2.HttpBody
    ) -> httpbody_pb2.HttpBody:
        """Post-rpc interceptor for raw_predict

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_server_streaming_predict(
        self,
        request: prediction_service.StreamingPredictRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.StreamingPredictRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for server_streaming_predict

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_server_streaming_predict(
        self, response: rest_streaming.ResponseIterator
    ) -> rest_streaming.ResponseIterator:
        """Post-rpc interceptor for server_streaming_predict

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_stream_generate_content(
        self,
        request: prediction_service.GenerateContentRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.GenerateContentRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for stream_generate_content

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_stream_generate_content(
        self, response: rest_streaming.ResponseIterator
    ) -> rest_streaming.ResponseIterator:
        """Post-rpc interceptor for stream_generate_content

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_stream_raw_predict(
        self,
        request: prediction_service.StreamRawPredictRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[prediction_service.StreamRawPredictRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for stream_raw_predict

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_stream_raw_predict(
        self, response: rest_streaming.ResponseIterator
    ) -> rest_streaming.ResponseIterator:
        """Post-rpc interceptor for stream_raw_predict

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_get_location(
        self,
        request: locations_pb2.GetLocationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.GetLocationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_location

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_get_location(
        self, response: locations_pb2.Location
    ) -> locations_pb2.Location:
        """Post-rpc interceptor for get_location

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_list_locations(
        self,
        request: locations_pb2.ListLocationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.ListLocationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_locations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_list_locations(
        self, response: locations_pb2.ListLocationsResponse
    ) -> locations_pb2.ListLocationsResponse:
        """Post-rpc interceptor for list_locations

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_get_iam_policy(
        self,
        request: iam_policy_pb2.GetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.GetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_get_iam_policy(self, response: policy_pb2.Policy) -> policy_pb2.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_set_iam_policy(
        self,
        request: iam_policy_pb2.SetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.SetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_set_iam_policy(self, response: policy_pb2.Policy) -> policy_pb2.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_test_iam_permissions(
        self,
        request: iam_policy_pb2.TestIamPermissionsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.TestIamPermissionsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_test_iam_permissions(
        self, response: iam_policy_pb2.TestIamPermissionsResponse
    ) -> iam_policy_pb2.TestIamPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_cancel_operation(
        self,
        request: operations_pb2.CancelOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.CancelOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_cancel_operation(self, response: None) -> None:
        """Post-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_delete_operation(
        self,
        request: operations_pb2.DeleteOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.DeleteOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_delete_operation(self, response: None) -> None:
        """Post-rpc interceptor for delete_operation

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_get_operation(
        self,
        request: operations_pb2.GetOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.GetOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_get_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for get_operation

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_list_operations(
        self,
        request: operations_pb2.ListOperationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.ListOperationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_operations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_list_operations(
        self, response: operations_pb2.ListOperationsResponse
    ) -> operations_pb2.ListOperationsResponse:
        """Post-rpc interceptor for list_operations

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response

    def pre_wait_operation(
        self,
        request: operations_pb2.WaitOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.WaitOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for wait_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the PredictionService server.
        """
        return request, metadata

    def post_wait_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for wait_operation

        Override in a subclass to manipulate the response
        after it is returned by the PredictionService server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class PredictionServiceRestStub:
    _session: AuthorizedSession
    _host: str
    _interceptor: PredictionServiceRestInterceptor


class PredictionServiceRestTransport(_BasePredictionServiceRestTransport):
    """REST backend synchronous transport for PredictionService.

    A service for online predictions and explanations.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: Optional[ga_credentials.Credentials] = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        client_cert_source_for_mtls: Optional[Callable[[], Tuple[bytes, bytes]]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        always_use_jwt_access: Optional[bool] = False,
        url_scheme: str = "https",
        interceptor: Optional[PredictionServiceRestInterceptor] = None,
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
            api_audience=api_audience,
        )
        self._session = AuthorizedSession(
            self._credentials, default_host=self.DEFAULT_HOST
        )
        if client_cert_source_for_mtls:
            self._session.configure_mtls_channel(client_cert_source_for_mtls)
        self._interceptor = interceptor or PredictionServiceRestInterceptor()
        self._prep_wrapped_messages(client_info)

    class _DirectPredict(
        _BasePredictionServiceRestTransport._BaseDirectPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.DirectPredict")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: prediction_service.DirectPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> prediction_service.DirectPredictResponse:
            r"""Call the direct predict method over HTTP.

            Args:
                request (~.prediction_service.DirectPredictRequest):
                    The request object. Request message for
                [PredictionService.DirectPredict][google.cloud.aiplatform.v1.PredictionService.DirectPredict].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.DirectPredictResponse:
                    Response message for
                [PredictionService.DirectPredict][google.cloud.aiplatform.v1.PredictionService.DirectPredict].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseDirectPredict._get_http_options()
            )
            request, metadata = self._interceptor.pre_direct_predict(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseDirectPredict._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseDirectPredict._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseDirectPredict._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._DirectPredict._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = prediction_service.DirectPredictResponse()
            pb_resp = prediction_service.DirectPredictResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_direct_predict(resp)
            return resp

    class _DirectRawPredict(
        _BasePredictionServiceRestTransport._BaseDirectRawPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.DirectRawPredict")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: prediction_service.DirectRawPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> prediction_service.DirectRawPredictResponse:
            r"""Call the direct raw predict method over HTTP.

            Args:
                request (~.prediction_service.DirectRawPredictRequest):
                    The request object. Request message for
                [PredictionService.DirectRawPredict][google.cloud.aiplatform.v1.PredictionService.DirectRawPredict].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.DirectRawPredictResponse:
                    Response message for
                [PredictionService.DirectRawPredict][google.cloud.aiplatform.v1.PredictionService.DirectRawPredict].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseDirectRawPredict._get_http_options()
            )
            request, metadata = self._interceptor.pre_direct_raw_predict(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseDirectRawPredict._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseDirectRawPredict._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseDirectRawPredict._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._DirectRawPredict._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = prediction_service.DirectRawPredictResponse()
            pb_resp = prediction_service.DirectRawPredictResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_direct_raw_predict(resp)
            return resp

    class _Explain(
        _BasePredictionServiceRestTransport._BaseExplain, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.Explain")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: prediction_service.ExplainRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> prediction_service.ExplainResponse:
            r"""Call the explain method over HTTP.

            Args:
                request (~.prediction_service.ExplainRequest):
                    The request object. Request message for
                [PredictionService.Explain][google.cloud.aiplatform.v1.PredictionService.Explain].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.ExplainResponse:
                    Response message for
                [PredictionService.Explain][google.cloud.aiplatform.v1.PredictionService.Explain].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseExplain._get_http_options()
            )
            request, metadata = self._interceptor.pre_explain(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseExplain._get_transcoded_request(
                http_options, request
            )

            body = (
                _BasePredictionServiceRestTransport._BaseExplain._get_request_body_json(
                    transcoded_request
                )
            )

            # Jsonify the query params
            query_params = (
                _BasePredictionServiceRestTransport._BaseExplain._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = PredictionServiceRestTransport._Explain._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = prediction_service.ExplainResponse()
            pb_resp = prediction_service.ExplainResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_explain(resp)
            return resp

    class _GenerateContent(
        _BasePredictionServiceRestTransport._BaseGenerateContent,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.GenerateContent")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: prediction_service.GenerateContentRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> prediction_service.GenerateContentResponse:
            r"""Call the generate content method over HTTP.

            Args:
                request (~.prediction_service.GenerateContentRequest):
                    The request object. Request message for [PredictionService.GenerateContent].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.GenerateContentResponse:
                    Response message for
                [PredictionService.GenerateContent].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseGenerateContent._get_http_options()
            )
            request, metadata = self._interceptor.pre_generate_content(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseGenerateContent._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseGenerateContent._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseGenerateContent._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._GenerateContent._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = prediction_service.GenerateContentResponse()
            pb_resp = prediction_service.GenerateContentResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_generate_content(resp)
            return resp

    class _Predict(
        _BasePredictionServiceRestTransport._BasePredict, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.Predict")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: prediction_service.PredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> prediction_service.PredictResponse:
            r"""Call the predict method over HTTP.

            Args:
                request (~.prediction_service.PredictRequest):
                    The request object. Request message for
                [PredictionService.Predict][google.cloud.aiplatform.v1.PredictionService.Predict].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.PredictResponse:
                    Response message for
                [PredictionService.Predict][google.cloud.aiplatform.v1.PredictionService.Predict].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BasePredict._get_http_options()
            )
            request, metadata = self._interceptor.pre_predict(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BasePredict._get_transcoded_request(
                http_options, request
            )

            body = (
                _BasePredictionServiceRestTransport._BasePredict._get_request_body_json(
                    transcoded_request
                )
            )

            # Jsonify the query params
            query_params = (
                _BasePredictionServiceRestTransport._BasePredict._get_query_params_json(
                    transcoded_request
                )
            )

            # Send the request
            response = PredictionServiceRestTransport._Predict._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = prediction_service.PredictResponse()
            pb_resp = prediction_service.PredictResponse.pb(resp)

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_predict(resp)
            return resp

    class _RawPredict(
        _BasePredictionServiceRestTransport._BaseRawPredict, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.RawPredict")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: prediction_service.RawPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> httpbody_pb2.HttpBody:
            r"""Call the raw predict method over HTTP.

            Args:
                request (~.prediction_service.RawPredictRequest):
                    The request object. Request message for
                [PredictionService.RawPredict][google.cloud.aiplatform.v1.PredictionService.RawPredict].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.httpbody_pb2.HttpBody:
                    Message that represents an arbitrary HTTP body. It
                should only be used for payload formats that can't be
                represented as JSON, such as raw binary or an HTML page.

                This message can be used both in streaming and
                non-streaming API methods in the request as well as the
                response.

                It can be used as a top-level request field, which is
                convenient if one wants to extract parameters from
                either the URL or HTTP template into the request fields
                and also want access to the raw HTTP body.

                Example:

                ::

                    message GetResourceRequest {
                      // A unique request id.
                      string request_id = 1;

                      // The raw HTTP body is bound to this field.
                      google.api.HttpBody http_body = 2;

                    }

                    service ResourceService {
                      rpc GetResource(GetResourceRequest)
                        returns (google.api.HttpBody);
                      rpc UpdateResource(google.api.HttpBody)
                        returns (google.protobuf.Empty);

                    }

                Example with streaming methods:

                ::

                    service CaldavService {
                      rpc GetCalendar(stream google.api.HttpBody)
                        returns (stream google.api.HttpBody);
                      rpc UpdateCalendar(stream google.api.HttpBody)
                        returns (stream google.api.HttpBody);

                    }

                Use of this type only changes how the request and
                response bodies are handled, all other features will
                continue to work unchanged.

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseRawPredict._get_http_options()
            )
            request, metadata = self._interceptor.pre_raw_predict(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseRawPredict._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseRawPredict._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseRawPredict._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._RawPredict._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = httpbody_pb2.HttpBody()
            pb_resp = resp

            json_format.Parse(response.content, pb_resp, ignore_unknown_fields=True)
            resp = self._interceptor.post_raw_predict(resp)
            return resp

    class _ServerStreamingPredict(
        _BasePredictionServiceRestTransport._BaseServerStreamingPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.ServerStreamingPredict")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                stream=True,
            )
            return response

        def __call__(
            self,
            request: prediction_service.StreamingPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            r"""Call the server streaming predict method over HTTP.

            Args:
                request (~.prediction_service.StreamingPredictRequest):
                    The request object. Request message for
                [PredictionService.StreamingPredict][google.cloud.aiplatform.v1.PredictionService.StreamingPredict].

                The first message must contain
                [endpoint][google.cloud.aiplatform.v1.StreamingPredictRequest.endpoint]
                field and optionally [input][]. The subsequent messages
                must contain [input][].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.StreamingPredictResponse:
                    Response message for
                [PredictionService.StreamingPredict][google.cloud.aiplatform.v1.PredictionService.StreamingPredict].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseServerStreamingPredict._get_http_options()
            )
            request, metadata = self._interceptor.pre_server_streaming_predict(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseServerStreamingPredict._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseServerStreamingPredict._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseServerStreamingPredict._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                PredictionServiceRestTransport._ServerStreamingPredict._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                    body,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = rest_streaming.ResponseIterator(
                response, prediction_service.StreamingPredictResponse
            )
            resp = self._interceptor.post_server_streaming_predict(resp)
            return resp

    class _StreamDirectPredict(
        _BasePredictionServiceRestTransport._BaseStreamDirectPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.StreamDirectPredict")

        def __call__(
            self,
            request: prediction_service.StreamDirectPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            raise NotImplementedError(
                "Method StreamDirectPredict is not available over REST transport"
            )

    class _StreamDirectRawPredict(
        _BasePredictionServiceRestTransport._BaseStreamDirectRawPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.StreamDirectRawPredict")

        def __call__(
            self,
            request: prediction_service.StreamDirectRawPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            raise NotImplementedError(
                "Method StreamDirectRawPredict is not available over REST transport"
            )

    class _StreamGenerateContent(
        _BasePredictionServiceRestTransport._BaseStreamGenerateContent,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.StreamGenerateContent")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                stream=True,
            )
            return response

        def __call__(
            self,
            request: prediction_service.GenerateContentRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            r"""Call the stream generate content method over HTTP.

            Args:
                request (~.prediction_service.GenerateContentRequest):
                    The request object. Request message for [PredictionService.GenerateContent].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.prediction_service.GenerateContentResponse:
                    Response message for
                [PredictionService.GenerateContent].

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseStreamGenerateContent._get_http_options()
            )
            request, metadata = self._interceptor.pre_stream_generate_content(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseStreamGenerateContent._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseStreamGenerateContent._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseStreamGenerateContent._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                PredictionServiceRestTransport._StreamGenerateContent._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                    body,
                )
            )

            # In case of error, raise the appropriate core_exceptions.GoogleAPICallError exception
            # subclass.
            if response.status_code >= 400:
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = rest_streaming.ResponseIterator(
                response, prediction_service.GenerateContentResponse
            )
            resp = self._interceptor.post_stream_generate_content(resp)
            return resp

    class _StreamingPredict(
        _BasePredictionServiceRestTransport._BaseStreamingPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.StreamingPredict")

        def __call__(
            self,
            request: prediction_service.StreamingPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            raise NotImplementedError(
                "Method StreamingPredict is not available over REST transport"
            )

    class _StreamingRawPredict(
        _BasePredictionServiceRestTransport._BaseStreamingRawPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.StreamingRawPredict")

        def __call__(
            self,
            request: prediction_service.StreamingRawPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            raise NotImplementedError(
                "Method StreamingRawPredict is not available over REST transport"
            )

    class _StreamRawPredict(
        _BasePredictionServiceRestTransport._BaseStreamRawPredict,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.StreamRawPredict")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
                stream=True,
            )
            return response

        def __call__(
            self,
            request: prediction_service.StreamRawPredictRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> rest_streaming.ResponseIterator:
            r"""Call the stream raw predict method over HTTP.

            Args:
                request (~.prediction_service.StreamRawPredictRequest):
                    The request object. Request message for
                [PredictionService.StreamRawPredict][google.cloud.aiplatform.v1.PredictionService.StreamRawPredict].
                retry (google.api_core.retry.Retry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.httpbody_pb2.HttpBody:
                    Message that represents an arbitrary HTTP body. It
                should only be used for payload formats that can't be
                represented as JSON, such as raw binary or an HTML page.

                This message can be used both in streaming and
                non-streaming API methods in the request as well as the
                response.

                It can be used as a top-level request field, which is
                convenient if one wants to extract parameters from
                either the URL or HTTP template into the request fields
                and also want access to the raw HTTP body.

                Example:

                ::

                    message GetResourceRequest {
                      // A unique request id.
                      string request_id = 1;

                      // The raw HTTP body is bound to this field.
                      google.api.HttpBody http_body = 2;

                    }

                    service ResourceService {
                      rpc GetResource(GetResourceRequest)
                        returns (google.api.HttpBody);
                      rpc UpdateResource(google.api.HttpBody)
                        returns (google.protobuf.Empty);

                    }

                Example with streaming methods:

                ::

                    service CaldavService {
                      rpc GetCalendar(stream google.api.HttpBody)
                        returns (stream google.api.HttpBody);
                      rpc UpdateCalendar(stream google.api.HttpBody)
                        returns (stream google.api.HttpBody);

                    }

                Use of this type only changes how the request and
                response bodies are handled, all other features will
                continue to work unchanged.

            """

            http_options = (
                _BasePredictionServiceRestTransport._BaseStreamRawPredict._get_http_options()
            )
            request, metadata = self._interceptor.pre_stream_raw_predict(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseStreamRawPredict._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseStreamRawPredict._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseStreamRawPredict._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._StreamRawPredict._get_response(
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
                raise core_exceptions.from_http_response(response)

            # Return the response
            resp = rest_streaming.ResponseIterator(response, httpbody_pb2.HttpBody)
            resp = self._interceptor.post_stream_raw_predict(resp)
            return resp

    @property
    def direct_predict(
        self,
    ) -> Callable[
        [prediction_service.DirectPredictRequest],
        prediction_service.DirectPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DirectPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def direct_raw_predict(
        self,
    ) -> Callable[
        [prediction_service.DirectRawPredictRequest],
        prediction_service.DirectRawPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._DirectRawPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def explain(
        self,
    ) -> Callable[
        [prediction_service.ExplainRequest], prediction_service.ExplainResponse
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._Explain(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def generate_content(
        self,
    ) -> Callable[
        [prediction_service.GenerateContentRequest],
        prediction_service.GenerateContentResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._GenerateContent(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def predict(
        self,
    ) -> Callable[
        [prediction_service.PredictRequest], prediction_service.PredictResponse
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._Predict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def raw_predict(
        self,
    ) -> Callable[[prediction_service.RawPredictRequest], httpbody_pb2.HttpBody]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._RawPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def server_streaming_predict(
        self,
    ) -> Callable[
        [prediction_service.StreamingPredictRequest],
        prediction_service.StreamingPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._ServerStreamingPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def stream_direct_predict(
        self,
    ) -> Callable[
        [prediction_service.StreamDirectPredictRequest],
        prediction_service.StreamDirectPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._StreamDirectPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def stream_direct_raw_predict(
        self,
    ) -> Callable[
        [prediction_service.StreamDirectRawPredictRequest],
        prediction_service.StreamDirectRawPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._StreamDirectRawPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def stream_generate_content(
        self,
    ) -> Callable[
        [prediction_service.GenerateContentRequest],
        prediction_service.GenerateContentResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._StreamGenerateContent(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def streaming_predict(
        self,
    ) -> Callable[
        [prediction_service.StreamingPredictRequest],
        prediction_service.StreamingPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._StreamingPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def streaming_raw_predict(
        self,
    ) -> Callable[
        [prediction_service.StreamingRawPredictRequest],
        prediction_service.StreamingRawPredictResponse,
    ]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._StreamingRawPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def stream_raw_predict(
        self,
    ) -> Callable[[prediction_service.StreamRawPredictRequest], httpbody_pb2.HttpBody]:
        # The return type is fine, but mypy isn't sophisticated enough to determine what's going on here.
        # In C++ this would require a dynamic_cast
        return self._StreamRawPredict(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_location(self):
        return self._GetLocation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetLocation(
        _BasePredictionServiceRestTransport._BaseGetLocation, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.GetLocation")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: locations_pb2.GetLocationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseGetLocation._get_http_options()
            )
            request, metadata = self._interceptor.pre_get_location(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseGetLocation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseGetLocation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._GetLocation._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = locations_pb2.Location()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_get_location(resp)
            return resp

    @property
    def list_locations(self):
        return self._ListLocations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListLocations(
        _BasePredictionServiceRestTransport._BaseListLocations,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.ListLocations")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: locations_pb2.ListLocationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseListLocations._get_http_options()
            )
            request, metadata = self._interceptor.pre_list_locations(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseListLocations._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseListLocations._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._ListLocations._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = locations_pb2.ListLocationsResponse()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_list_locations(resp)
            return resp

    @property
    def get_iam_policy(self):
        return self._GetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _GetIamPolicy(
        _BasePredictionServiceRestTransport._BaseGetIamPolicy, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.GetIamPolicy")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: iam_policy_pb2.GetIamPolicyRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseGetIamPolicy._get_http_options()
            )
            request, metadata = self._interceptor.pre_get_iam_policy(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseGetIamPolicy._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseGetIamPolicy._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._GetIamPolicy._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_get_iam_policy(resp)
            return resp

    @property
    def set_iam_policy(self):
        return self._SetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _SetIamPolicy(
        _BasePredictionServiceRestTransport._BaseSetIamPolicy, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.SetIamPolicy")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
                data=body,
            )
            return response

        def __call__(
            self,
            request: iam_policy_pb2.SetIamPolicyRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseSetIamPolicy._get_http_options()
            )
            request, metadata = self._interceptor.pre_set_iam_policy(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseSetIamPolicy._get_transcoded_request(
                http_options, request
            )

            body = _BasePredictionServiceRestTransport._BaseSetIamPolicy._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseSetIamPolicy._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._SetIamPolicy._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = policy_pb2.Policy()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_set_iam_policy(resp)
            return resp

    @property
    def test_iam_permissions(self):
        return self._TestIamPermissions(self._session, self._host, self._interceptor)  # type: ignore

    class _TestIamPermissions(
        _BasePredictionServiceRestTransport._BaseTestIamPermissions,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.TestIamPermissions")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: iam_policy_pb2.TestIamPermissionsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseTestIamPermissions._get_http_options()
            )
            request, metadata = self._interceptor.pre_test_iam_permissions(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseTestIamPermissions._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseTestIamPermissions._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._TestIamPermissions._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = iam_policy_pb2.TestIamPermissionsResponse()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_test_iam_permissions(resp)
            return resp

    @property
    def cancel_operation(self):
        return self._CancelOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _CancelOperation(
        _BasePredictionServiceRestTransport._BaseCancelOperation,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.CancelOperation")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: operations_pb2.CancelOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseCancelOperation._get_http_options()
            )
            request, metadata = self._interceptor.pre_cancel_operation(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseCancelOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseCancelOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._CancelOperation._get_response(
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
                raise core_exceptions.from_http_response(response)

            return self._interceptor.post_cancel_operation(None)

    @property
    def delete_operation(self):
        return self._DeleteOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _DeleteOperation(
        _BasePredictionServiceRestTransport._BaseDeleteOperation,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.DeleteOperation")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: operations_pb2.DeleteOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseDeleteOperation._get_http_options()
            )
            request, metadata = self._interceptor.pre_delete_operation(
                request, metadata
            )
            transcoded_request = _BasePredictionServiceRestTransport._BaseDeleteOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseDeleteOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._DeleteOperation._get_response(
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
                raise core_exceptions.from_http_response(response)

            return self._interceptor.post_delete_operation(None)

    @property
    def get_operation(self):
        return self._GetOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetOperation(
        _BasePredictionServiceRestTransport._BaseGetOperation, PredictionServiceRestStub
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.GetOperation")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: operations_pb2.GetOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseGetOperation._get_http_options()
            )
            request, metadata = self._interceptor.pre_get_operation(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseGetOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseGetOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._GetOperation._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = operations_pb2.Operation()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_get_operation(resp)
            return resp

    @property
    def list_operations(self):
        return self._ListOperations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListOperations(
        _BasePredictionServiceRestTransport._BaseListOperations,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.ListOperations")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: operations_pb2.ListOperationsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseListOperations._get_http_options()
            )
            request, metadata = self._interceptor.pre_list_operations(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseListOperations._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseListOperations._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._ListOperations._get_response(
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
                raise core_exceptions.from_http_response(response)

            content = response.content.decode("utf-8")
            resp = operations_pb2.ListOperationsResponse()
            resp = json_format.Parse(content, resp)
            resp = self._interceptor.post_list_operations(resp)
            return resp

    @property
    def wait_operation(self):
        return self._WaitOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _WaitOperation(
        _BasePredictionServiceRestTransport._BaseWaitOperation,
        PredictionServiceRestStub,
    ):
        def __hash__(self):
            return hash("PredictionServiceRestTransport.WaitOperation")

        @staticmethod
        def _get_response(
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
            response = getattr(session, method)(
                "{host}{uri}".format(host=host, uri=uri),
                timeout=timeout,
                headers=headers,
                params=rest_helpers.flatten_query_params(query_params, strict=True),
            )
            return response

        def __call__(
            self,
            request: operations_pb2.WaitOperationRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
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

            http_options = (
                _BasePredictionServiceRestTransport._BaseWaitOperation._get_http_options()
            )
            request, metadata = self._interceptor.pre_wait_operation(request, metadata)
            transcoded_request = _BasePredictionServiceRestTransport._BaseWaitOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BasePredictionServiceRestTransport._BaseWaitOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = PredictionServiceRestTransport._WaitOperation._get_response(
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


__all__ = ("PredictionServiceRestTransport",)
