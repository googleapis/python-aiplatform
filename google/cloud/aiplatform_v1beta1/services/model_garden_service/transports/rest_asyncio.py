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

from google.auth.aio import credentials as ga_credentials_async  # type: ignore

from google.api_core import exceptions as core_exceptions
from google.api_core import gapic_v1
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore
from google.api_core import retry_async as retries
from google.api_core import rest_helpers
from google.api_core import rest_streaming_async  # type: ignore


from google.protobuf import json_format
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.cloud.location import locations_pb2  # type: ignore

import json  # type: ignore
import dataclasses
from typing import Any, Dict, List, Callable, Tuple, Optional, Sequence, Union


from google.cloud.aiplatform_v1beta1.types import model_garden_service
from google.cloud.aiplatform_v1beta1.types import publisher_model
from google.longrunning import operations_pb2  # type: ignore


from .rest_base import _BaseModelGardenServiceRestTransport

from .base import DEFAULT_CLIENT_INFO as BASE_DEFAULT_CLIENT_INFO

try:
    OptionalRetry = Union[retries.AsyncRetry, gapic_v1.method._MethodDefault, None]
except AttributeError:  # pragma: NO COVER
    OptionalRetry = Union[retries.AsyncRetry, object, None]  # type: ignore

DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
    gapic_version=BASE_DEFAULT_CLIENT_INFO.gapic_version,
    grpc_version=None,
    rest_version=f"google-auth@{google.auth.__version__}",
)


class AsyncModelGardenServiceRestInterceptor:
    """Asynchronous Interceptor for ModelGardenService.

    Interceptors are used to manipulate requests, request metadata, and responses
    in arbitrary ways.
    Example use cases include:
    * Logging
    * Verifying requests according to service or custom semantics
    * Stripping extraneous information from responses

    These use cases and more can be enabled by injecting an
    instance of a custom subclass when constructing the AsyncModelGardenServiceRestTransport.

    .. code-block:: python
        class MyCustomModelGardenServiceInterceptor(ModelGardenServiceRestInterceptor):
            async def pre_get_publisher_model(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_get_publisher_model(self, response):
                logging.log(f"Received response: {response}")
                return response

            async def pre_list_publisher_models(self, request, metadata):
                logging.log(f"Received request: {request}")
                return request, metadata

            async def post_list_publisher_models(self, response):
                logging.log(f"Received response: {response}")
                return response

        transport = AsyncModelGardenServiceRestTransport(interceptor=MyCustomModelGardenServiceInterceptor())
        client = async ModelGardenServiceClient(transport=transport)


    """

    async def pre_get_publisher_model(
        self,
        request: model_garden_service.GetPublisherModelRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        model_garden_service.GetPublisherModelRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for get_publisher_model

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_get_publisher_model(
        self, response: publisher_model.PublisherModel
    ) -> publisher_model.PublisherModel:
        """Post-rpc interceptor for get_publisher_model

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_publisher_models(
        self,
        request: model_garden_service.ListPublisherModelsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[
        model_garden_service.ListPublisherModelsRequest, Sequence[Tuple[str, str]]
    ]:
        """Pre-rpc interceptor for list_publisher_models

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_list_publisher_models(
        self, response: model_garden_service.ListPublisherModelsResponse
    ) -> model_garden_service.ListPublisherModelsResponse:
        """Post-rpc interceptor for list_publisher_models

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_location(
        self,
        request: locations_pb2.GetLocationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.GetLocationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_location

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_get_location(
        self, response: locations_pb2.Location
    ) -> locations_pb2.Location:
        """Post-rpc interceptor for get_location

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_locations(
        self,
        request: locations_pb2.ListLocationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[locations_pb2.ListLocationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_locations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_list_locations(
        self, response: locations_pb2.ListLocationsResponse
    ) -> locations_pb2.ListLocationsResponse:
        """Post-rpc interceptor for list_locations

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_iam_policy(
        self,
        request: iam_policy_pb2.GetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.GetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_get_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for get_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_set_iam_policy(
        self,
        request: iam_policy_pb2.SetIamPolicyRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.SetIamPolicyRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_set_iam_policy(
        self, response: policy_pb2.Policy
    ) -> policy_pb2.Policy:
        """Post-rpc interceptor for set_iam_policy

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_test_iam_permissions(
        self,
        request: iam_policy_pb2.TestIamPermissionsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[iam_policy_pb2.TestIamPermissionsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_test_iam_permissions(
        self, response: iam_policy_pb2.TestIamPermissionsResponse
    ) -> iam_policy_pb2.TestIamPermissionsResponse:
        """Post-rpc interceptor for test_iam_permissions

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_cancel_operation(
        self,
        request: operations_pb2.CancelOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.CancelOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_cancel_operation(self, response: None) -> None:
        """Post-rpc interceptor for cancel_operation

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_delete_operation(
        self,
        request: operations_pb2.DeleteOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.DeleteOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for delete_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_delete_operation(self, response: None) -> None:
        """Post-rpc interceptor for delete_operation

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_get_operation(
        self,
        request: operations_pb2.GetOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.GetOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for get_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_get_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for get_operation

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_list_operations(
        self,
        request: operations_pb2.ListOperationsRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.ListOperationsRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for list_operations

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_list_operations(
        self, response: operations_pb2.ListOperationsResponse
    ) -> operations_pb2.ListOperationsResponse:
        """Post-rpc interceptor for list_operations

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response

    async def pre_wait_operation(
        self,
        request: operations_pb2.WaitOperationRequest,
        metadata: Sequence[Tuple[str, str]],
    ) -> Tuple[operations_pb2.WaitOperationRequest, Sequence[Tuple[str, str]]]:
        """Pre-rpc interceptor for wait_operation

        Override in a subclass to manipulate the request or metadata
        before they are sent to the ModelGardenService server.
        """
        return request, metadata

    async def post_wait_operation(
        self, response: operations_pb2.Operation
    ) -> operations_pb2.Operation:
        """Post-rpc interceptor for wait_operation

        Override in a subclass to manipulate the response
        after it is returned by the ModelGardenService server but before
        it is returned to user code.
        """
        return response


@dataclasses.dataclass
class AsyncModelGardenServiceRestStub:
    _session: AsyncAuthorizedSession
    _host: str
    _interceptor: AsyncModelGardenServiceRestInterceptor


class AsyncModelGardenServiceRestTransport(_BaseModelGardenServiceRestTransport):
    """Asynchronous REST backend transport for ModelGardenService.

    The interface of Model Garden Service.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends JSON representations of protocol buffers over HTTP/1.1
    """

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: Optional[ga_credentials_async.Credentials] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        url_scheme: str = "https",
        interceptor: Optional[AsyncModelGardenServiceRestInterceptor] = None,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to (default: 'aiplatform.googleapis.com').
            credentials (Optional[google.auth.aio.credentials.Credentials]): The
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
        self._interceptor = interceptor or AsyncModelGardenServiceRestInterceptor()
        self._wrap_with_kind = True
        self._prep_wrapped_messages(client_info)

    def _prep_wrapped_messages(self, client_info):
        """Precompute the wrapped methods, overriding the base class method to use async wrappers."""
        self._wrapped_methods = {
            self.get_publisher_model: self._wrap_method(
                self.get_publisher_model,
                default_timeout=None,
                client_info=client_info,
            ),
            self.list_publisher_models: self._wrap_method(
                self.list_publisher_models,
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

    class _GetPublisherModel(
        _BaseModelGardenServiceRestTransport._BaseGetPublisherModel,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.GetPublisherModel")

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
            request: model_garden_service.GetPublisherModelRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> publisher_model.PublisherModel:
            r"""Call the get publisher model method over HTTP.

            Args:
                request (~.model_garden_service.GetPublisherModelRequest):
                    The request object. Request message for
                [ModelGardenService.GetPublisherModel][google.cloud.aiplatform.v1beta1.ModelGardenService.GetPublisherModel]
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.publisher_model.PublisherModel:
                    A Model Garden Publisher Model.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseGetPublisherModel._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_publisher_model(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseGetPublisherModel._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseGetPublisherModel._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncModelGardenServiceRestTransport._GetPublisherModel._get_response(
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
            resp = publisher_model.PublisherModel()
            pb_resp = publisher_model.PublisherModel.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_get_publisher_model(resp)
            return resp

    class _ListPublisherModels(
        _BaseModelGardenServiceRestTransport._BaseListPublisherModels,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.ListPublisherModels")

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
            request: model_garden_service.ListPublisherModelsRequest,
            *,
            retry: OptionalRetry = gapic_v1.method.DEFAULT,
            timeout: Optional[float] = None,
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> model_garden_service.ListPublisherModelsResponse:
            r"""Call the list publisher models method over HTTP.

            Args:
                request (~.model_garden_service.ListPublisherModelsRequest):
                    The request object. Request message for
                [ModelGardenService.ListPublisherModels][google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels].
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                ~.model_garden_service.ListPublisherModelsResponse:
                    Response message for
                [ModelGardenService.ListPublisherModels][google.cloud.aiplatform.v1beta1.ModelGardenService.ListPublisherModels].

            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseListPublisherModels._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_publisher_models(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseListPublisherModels._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseListPublisherModels._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncModelGardenServiceRestTransport._ListPublisherModels._get_response(
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
            resp = model_garden_service.ListPublisherModelsResponse()
            pb_resp = model_garden_service.ListPublisherModelsResponse.pb(resp)
            content = await response.read()
            json_format.Parse(content, pb_resp, ignore_unknown_fields=True)
            resp = await self._interceptor.post_list_publisher_models(resp)
            return resp

    @property
    def get_publisher_model(
        self,
    ) -> Callable[
        [model_garden_service.GetPublisherModelRequest], publisher_model.PublisherModel
    ]:
        return self._GetPublisherModel(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def list_publisher_models(
        self,
    ) -> Callable[
        [model_garden_service.ListPublisherModelsRequest],
        model_garden_service.ListPublisherModelsResponse,
    ]:
        return self._ListPublisherModels(self._session, self._host, self._interceptor)  # type: ignore

    @property
    def get_location(self):
        return self._GetLocation(self._session, self._host, self._interceptor)  # type: ignore

    class _GetLocation(
        _BaseModelGardenServiceRestTransport._BaseGetLocation,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.GetLocation")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> locations_pb2.Location:

            r"""Call the get location method over HTTP.

            Args:
                request (locations_pb2.GetLocationRequest):
                    The request object for GetLocation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.Location: Response from GetLocation method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseGetLocation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_location(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseGetLocation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseGetLocation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncModelGardenServiceRestTransport._GetLocation._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
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
            return resp

    @property
    def list_locations(self):
        return self._ListLocations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListLocations(
        _BaseModelGardenServiceRestTransport._BaseListLocations,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.ListLocations")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> locations_pb2.ListLocationsResponse:

            r"""Call the list locations method over HTTP.

            Args:
                request (locations_pb2.ListLocationsRequest):
                    The request object for ListLocations method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                locations_pb2.ListLocationsResponse: Response from ListLocations method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseListLocations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_locations(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseListLocations._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseListLocations._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncModelGardenServiceRestTransport._ListLocations._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
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
            return resp

    @property
    def get_iam_policy(self):
        return self._GetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _GetIamPolicy(
        _BaseModelGardenServiceRestTransport._BaseGetIamPolicy,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.GetIamPolicy")

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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from GetIamPolicy method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseGetIamPolicy._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_iam_policy(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseGetIamPolicy._get_transcoded_request(
                http_options, request
            )

            body = _BaseModelGardenServiceRestTransport._BaseGetIamPolicy._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseGetIamPolicy._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncModelGardenServiceRestTransport._GetIamPolicy._get_response(
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
            return resp

    @property
    def set_iam_policy(self):
        return self._SetIamPolicy(self._session, self._host, self._interceptor)  # type: ignore

    class _SetIamPolicy(
        _BaseModelGardenServiceRestTransport._BaseSetIamPolicy,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.SetIamPolicy")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> policy_pb2.Policy:

            r"""Call the set iam policy method over HTTP.

            Args:
                request (iam_policy_pb2.SetIamPolicyRequest):
                    The request object for SetIamPolicy method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                policy_pb2.Policy: Response from SetIamPolicy method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseSetIamPolicy._get_http_options()
            )
            request, metadata = await self._interceptor.pre_set_iam_policy(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseSetIamPolicy._get_transcoded_request(
                http_options, request
            )

            body = _BaseModelGardenServiceRestTransport._BaseSetIamPolicy._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseSetIamPolicy._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncModelGardenServiceRestTransport._SetIamPolicy._get_response(
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
            return resp

    @property
    def test_iam_permissions(self):
        return self._TestIamPermissions(self._session, self._host, self._interceptor)  # type: ignore

    class _TestIamPermissions(
        _BaseModelGardenServiceRestTransport._BaseTestIamPermissions,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.TestIamPermissions")

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
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                iam_policy_pb2.TestIamPermissionsResponse: Response from TestIamPermissions method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseTestIamPermissions._get_http_options()
            )
            request, metadata = await self._interceptor.pre_test_iam_permissions(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseTestIamPermissions._get_transcoded_request(
                http_options, request
            )

            body = _BaseModelGardenServiceRestTransport._BaseTestIamPermissions._get_request_body_json(
                transcoded_request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseTestIamPermissions._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncModelGardenServiceRestTransport._TestIamPermissions._get_response(
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
            resp = iam_policy_pb2.TestIamPermissionsResponse()
            resp = json_format.Parse(content, resp)
            resp = await self._interceptor.post_test_iam_permissions(resp)
            return resp

    @property
    def cancel_operation(self):
        return self._CancelOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _CancelOperation(
        _BaseModelGardenServiceRestTransport._BaseCancelOperation,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.CancelOperation")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> None:

            r"""Call the cancel operation method over HTTP.

            Args:
                request (operations_pb2.CancelOperationRequest):
                    The request object for CancelOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseCancelOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_cancel_operation(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseCancelOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseCancelOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncModelGardenServiceRestTransport._CancelOperation._get_response(
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
        _BaseModelGardenServiceRestTransport._BaseDeleteOperation,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.DeleteOperation")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> None:

            r"""Call the delete operation method over HTTP.

            Args:
                request (operations_pb2.DeleteOperationRequest):
                    The request object for DeleteOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseDeleteOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_delete_operation(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseDeleteOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseDeleteOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncModelGardenServiceRestTransport._DeleteOperation._get_response(
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
        _BaseModelGardenServiceRestTransport._BaseGetOperation,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.GetOperation")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:

            r"""Call the get operation method over HTTP.

            Args:
                request (operations_pb2.GetOperationRequest):
                    The request object for GetOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from GetOperation method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseGetOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_get_operation(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseGetOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseGetOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncModelGardenServiceRestTransport._GetOperation._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
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
            return resp

    @property
    def list_operations(self):
        return self._ListOperations(self._session, self._host, self._interceptor)  # type: ignore

    class _ListOperations(
        _BaseModelGardenServiceRestTransport._BaseListOperations,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.ListOperations")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.ListOperationsResponse:

            r"""Call the list operations method over HTTP.

            Args:
                request (operations_pb2.ListOperationsRequest):
                    The request object for ListOperations method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.ListOperationsResponse: Response from ListOperations method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseListOperations._get_http_options()
            )
            request, metadata = await self._interceptor.pre_list_operations(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseListOperations._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseListOperations._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = await AsyncModelGardenServiceRestTransport._ListOperations._get_response(
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
            return resp

    @property
    def wait_operation(self):
        return self._WaitOperation(self._session, self._host, self._interceptor)  # type: ignore

    class _WaitOperation(
        _BaseModelGardenServiceRestTransport._BaseWaitOperation,
        AsyncModelGardenServiceRestStub,
    ):
        def __hash__(self):
            return hash("AsyncModelGardenServiceRestTransport.WaitOperation")

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
            metadata: Sequence[Tuple[str, str]] = (),
        ) -> operations_pb2.Operation:

            r"""Call the wait operation method over HTTP.

            Args:
                request (operations_pb2.WaitOperationRequest):
                    The request object for WaitOperation method.
                retry (google.api_core.retry_async.AsyncRetry): Designation of what errors, if any,
                    should be retried.
                timeout (float): The timeout for this request.
                metadata (Sequence[Tuple[str, str]]): Strings which should be
                    sent along with the request as metadata.

            Returns:
                operations_pb2.Operation: Response from WaitOperation method.
            """

            http_options = (
                _BaseModelGardenServiceRestTransport._BaseWaitOperation._get_http_options()
            )
            request, metadata = await self._interceptor.pre_wait_operation(
                request, metadata
            )
            transcoded_request = _BaseModelGardenServiceRestTransport._BaseWaitOperation._get_transcoded_request(
                http_options, request
            )

            # Jsonify the query params
            query_params = _BaseModelGardenServiceRestTransport._BaseWaitOperation._get_query_params_json(
                transcoded_request
            )

            # Send the request
            response = (
                await AsyncModelGardenServiceRestTransport._WaitOperation._get_response(
                    self._host,
                    metadata,
                    query_params,
                    self._session,
                    timeout,
                    transcoded_request,
                )
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
            return resp

    @property
    def kind(self) -> str:
        return "rest_asyncio"

    async def close(self):
        await self._session.close()
