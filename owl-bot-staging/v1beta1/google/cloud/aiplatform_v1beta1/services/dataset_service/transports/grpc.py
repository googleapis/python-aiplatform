# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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
import json
import logging as std_logging
import pickle
import warnings
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

from google.api_core import grpc_helpers
from google.api_core import operations_v1
from google.api_core import gapic_v1
import google.auth                         # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore
from google.protobuf.json_format import MessageToJson
import google.protobuf.message

import grpc  # type: ignore
import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import annotation_spec
from google.cloud.aiplatform_v1beta1.types import dataset
from google.cloud.aiplatform_v1beta1.types import dataset as gca_dataset
from google.cloud.aiplatform_v1beta1.types import dataset_service
from google.cloud.aiplatform_v1beta1.types import dataset_version
from google.cloud.aiplatform_v1beta1.types import dataset_version as gca_dataset_version
from google.cloud.location import locations_pb2 # type: ignore
from google.iam.v1 import iam_policy_pb2  # type: ignore
from google.iam.v1 import policy_pb2  # type: ignore
from google.longrunning import operations_pb2 # type: ignore
from .base import DatasetServiceTransport, DEFAULT_CLIENT_INFO

try:
    from google.api_core import client_logging  # type: ignore
    CLIENT_LOGGING_SUPPORTED = True  # pragma: NO COVER
except ImportError:  # pragma: NO COVER
    CLIENT_LOGGING_SUPPORTED = False

_LOGGER = std_logging.getLogger(__name__)


class _LoggingClientInterceptor(grpc.UnaryUnaryClientInterceptor):  # pragma: NO COVER
    def intercept_unary_unary(self, continuation, client_call_details, request):
        logging_enabled = CLIENT_LOGGING_SUPPORTED and _LOGGER.isEnabledFor(std_logging.DEBUG)
        if logging_enabled:  # pragma: NO COVER
            request_metadata = client_call_details.metadata
            if isinstance(request, proto.Message):
                request_payload = type(request).to_json(request)
            elif isinstance(request, google.protobuf.message.Message):
                request_payload = MessageToJson(request)
            else:
                request_payload = f"{type(request).__name__}: {pickle.dumps(request)}"

            request_metadata = {
                key: value.decode("utf-8") if isinstance(value, bytes) else value
                for key, value in request_metadata
            }
            grpc_request = {
                "payload": request_payload,
                "requestMethod": "grpc",
                "metadata": dict(request_metadata),
            }
            _LOGGER.debug(
                f"Sending request for {client_call_details.method}",
                extra = {
                    "serviceName": "google.cloud.aiplatform.v1beta1.DatasetService",
                    "rpcName": client_call_details.method,
                    "request": grpc_request,
                    "metadata": grpc_request["metadata"],
                },
            )

        response = continuation(client_call_details, request)
        if logging_enabled:  # pragma: NO COVER
            response_metadata = response.trailing_metadata()
            # Convert gRPC metadata `<class 'grpc.aio._metadata.Metadata'>` to list of tuples
            metadata = dict([(k, str(v)) for k, v in response_metadata]) if response_metadata else None
            result = response.result()
            if isinstance(result, proto.Message):
                response_payload = type(result).to_json(result)
            elif isinstance(result, google.protobuf.message.Message):
                response_payload = MessageToJson(result)
            else:
                response_payload = f"{type(result).__name__}: {pickle.dumps(result)}"
            grpc_response = {
                "payload": response_payload,
                "metadata": metadata,
                "status": "OK",
            }
            _LOGGER.debug(
                f"Received response for {client_call_details.method}.",
                extra = {
                    "serviceName": "google.cloud.aiplatform.v1beta1.DatasetService",
                    "rpcName": client_call_details.method,
                    "response": grpc_response,
                    "metadata": grpc_response["metadata"],
                },
            )
        return response


class DatasetServiceGrpcTransport(DatasetServiceTransport):
    """gRPC backend transport for DatasetService.

    The service that manages Vertex AI Dataset and its child
    resources.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """
    _stubs: Dict[str, Callable]

    def __init__(self, *,
            host: str = 'aiplatform.googleapis.com',
            credentials: Optional[ga_credentials.Credentials] = None,
            credentials_file: Optional[str] = None,
            scopes: Optional[Sequence[str]] = None,
            channel: Optional[Union[grpc.Channel, Callable[..., grpc.Channel]]] = None,
            api_mtls_endpoint: Optional[str] = None,
            client_cert_source: Optional[Callable[[], Tuple[bytes, bytes]]] = None,
            ssl_channel_credentials: Optional[grpc.ChannelCredentials] = None,
            client_cert_source_for_mtls: Optional[Callable[[], Tuple[bytes, bytes]]] = None,
            quota_project_id: Optional[str] = None,
            client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
            always_use_jwt_access: Optional[bool] = False,
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
                This argument is ignored if a ``channel`` instance is provided.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if a ``channel`` instance is provided.
            scopes (Optional(Sequence[str])): A list of scopes. This argument is
                ignored if a ``channel`` instance is provided.
            channel (Optional[Union[grpc.Channel, Callable[..., grpc.Channel]]]):
                A ``Channel`` instance through which to make calls, or a Callable
                that constructs and returns one. If set to None, ``self.create_channel``
                is used to create the channel. If a Callable is given, it will be called
                with the same arguments as used in ``self.create_channel``.
            api_mtls_endpoint (Optional[str]): Deprecated. The mutual TLS endpoint.
                If provided, it overrides the ``host`` argument and tries to create
                a mutual TLS channel with client SSL credentials from
                ``client_cert_source`` or application default SSL credentials.
            client_cert_source (Optional[Callable[[], Tuple[bytes, bytes]]]):
                Deprecated. A callback to provide client SSL certificate bytes and
                private key bytes, both in PEM format. It is ignored if
                ``api_mtls_endpoint`` is None.
            ssl_channel_credentials (grpc.ChannelCredentials): SSL credentials
                for the grpc channel. It is ignored if a ``channel`` instance is provided.
            client_cert_source_for_mtls (Optional[Callable[[], Tuple[bytes, bytes]]]):
                A callback to provide client certificate bytes and private key bytes,
                both in PEM format. It is used to configure a mutual TLS channel. It is
                ignored if a ``channel`` instance or ``ssl_channel_credentials`` is provided.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.

        Raises:
          google.auth.exceptions.MutualTLSChannelError: If mutual TLS transport
              creation failed for any reason.
          google.api_core.exceptions.DuplicateCredentialArgs: If both ``credentials``
              and ``credentials_file`` are passed.
        """
        self._grpc_channel = None
        self._ssl_channel_credentials = ssl_channel_credentials
        self._stubs: Dict[str, Callable] = {}
        self._operations_client: Optional[operations_v1.OperationsClient] = None

        if api_mtls_endpoint:
            warnings.warn("api_mtls_endpoint is deprecated", DeprecationWarning)
        if client_cert_source:
            warnings.warn("client_cert_source is deprecated", DeprecationWarning)

        if isinstance(channel, grpc.Channel):
            # Ignore credentials if a channel was passed.
            credentials = None
            self._ignore_credentials = True
            # If a channel was explicitly provided, set it.
            self._grpc_channel = channel
            self._ssl_channel_credentials = None

        else:
            if api_mtls_endpoint:
                host = api_mtls_endpoint

                # Create SSL credentials with client_cert_source or application
                # default SSL credentials.
                if client_cert_source:
                    cert, key = client_cert_source()
                    self._ssl_channel_credentials = grpc.ssl_channel_credentials(
                        certificate_chain=cert, private_key=key
                    )
                else:
                    self._ssl_channel_credentials = SslCredentials().ssl_credentials

            else:
                if client_cert_source_for_mtls and not ssl_channel_credentials:
                    cert, key = client_cert_source_for_mtls()
                    self._ssl_channel_credentials = grpc.ssl_channel_credentials(
                        certificate_chain=cert, private_key=key
                    )

        # The base transport sets the host, credentials and scopes
        super().__init__(
            host=host,
            credentials=credentials,
            credentials_file=credentials_file,
            scopes=scopes,
            quota_project_id=quota_project_id,
            client_info=client_info,
            always_use_jwt_access=always_use_jwt_access,
            api_audience=api_audience,
        )

        if not self._grpc_channel:
            # initialize with the provided callable or the default channel
            channel_init = channel or type(self).create_channel
            self._grpc_channel = channel_init(
                self._host,
                # use the credentials which are saved
                credentials=self._credentials,
                # Set ``credentials_file`` to ``None`` here as
                # the credentials that we saved earlier should be used.
                credentials_file=None,
                scopes=self._scopes,
                ssl_credentials=self._ssl_channel_credentials,
                quota_project_id=quota_project_id,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )

        self._interceptor = _LoggingClientInterceptor()
        self._logged_channel =  grpc.intercept_channel(self._grpc_channel, self._interceptor)

        # Wrap messages. This must be done after self._logged_channel exists
        self._prep_wrapped_messages(client_info)

    @classmethod
    def create_channel(cls,
                       host: str = 'aiplatform.googleapis.com',
                       credentials: Optional[ga_credentials.Credentials] = None,
                       credentials_file: Optional[str] = None,
                       scopes: Optional[Sequence[str]] = None,
                       quota_project_id: Optional[str] = None,
                       **kwargs) -> grpc.Channel:
        """Create and return a gRPC channel object.
        Args:
            host (Optional[str]): The host for the channel to use.
            credentials (Optional[~.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify this application to the service. If
                none are specified, the client will attempt to ascertain
                the credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scopes (Optional[Sequence[str]]): A optional list of scopes needed for this
                service. These are only used when credentials are not specified and
                are passed to :func:`google.auth.default`.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            kwargs (Optional[dict]): Keyword arguments, which are passed to the
                channel creation.
        Returns:
            grpc.Channel: A gRPC channel object.

        Raises:
            google.api_core.exceptions.DuplicateCredentialArgs: If both ``credentials``
              and ``credentials_file`` are passed.
        """

        return grpc_helpers.create_channel(
            host,
            credentials=credentials,
            credentials_file=credentials_file,
            quota_project_id=quota_project_id,
            default_scopes=cls.AUTH_SCOPES,
            scopes=scopes,
            default_host=cls.DEFAULT_HOST,
            **kwargs
        )

    @property
    def grpc_channel(self) -> grpc.Channel:
        """Return the channel designed to connect to this service.
        """
        return self._grpc_channel

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Create the client designed to process long-running operations.

        This property caches on the instance; repeated calls return the same
        client.
        """
        # Quick check: Only create a new client if we do not already have one.
        if self._operations_client is None:
            self._operations_client = operations_v1.OperationsClient(
                self._logged_channel
            )

        # Return the client from cache.
        return self._operations_client

    @property
    def create_dataset(self) -> Callable[
            [dataset_service.CreateDatasetRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the create dataset method over gRPC.

        Creates a Dataset.

        Returns:
            Callable[[~.CreateDatasetRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'create_dataset' not in self._stubs:
            self._stubs['create_dataset'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/CreateDataset',
                request_serializer=dataset_service.CreateDatasetRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['create_dataset']

    @property
    def get_dataset(self) -> Callable[
            [dataset_service.GetDatasetRequest],
            dataset.Dataset]:
        r"""Return a callable for the get dataset method over gRPC.

        Gets a Dataset.

        Returns:
            Callable[[~.GetDatasetRequest],
                    ~.Dataset]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'get_dataset' not in self._stubs:
            self._stubs['get_dataset'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/GetDataset',
                request_serializer=dataset_service.GetDatasetRequest.serialize,
                response_deserializer=dataset.Dataset.deserialize,
            )
        return self._stubs['get_dataset']

    @property
    def update_dataset(self) -> Callable[
            [dataset_service.UpdateDatasetRequest],
            gca_dataset.Dataset]:
        r"""Return a callable for the update dataset method over gRPC.

        Updates a Dataset.

        Returns:
            Callable[[~.UpdateDatasetRequest],
                    ~.Dataset]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'update_dataset' not in self._stubs:
            self._stubs['update_dataset'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/UpdateDataset',
                request_serializer=dataset_service.UpdateDatasetRequest.serialize,
                response_deserializer=gca_dataset.Dataset.deserialize,
            )
        return self._stubs['update_dataset']

    @property
    def list_datasets(self) -> Callable[
            [dataset_service.ListDatasetsRequest],
            dataset_service.ListDatasetsResponse]:
        r"""Return a callable for the list datasets method over gRPC.

        Lists Datasets in a Location.

        Returns:
            Callable[[~.ListDatasetsRequest],
                    ~.ListDatasetsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'list_datasets' not in self._stubs:
            self._stubs['list_datasets'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ListDatasets',
                request_serializer=dataset_service.ListDatasetsRequest.serialize,
                response_deserializer=dataset_service.ListDatasetsResponse.deserialize,
            )
        return self._stubs['list_datasets']

    @property
    def delete_dataset(self) -> Callable[
            [dataset_service.DeleteDatasetRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the delete dataset method over gRPC.

        Deletes a Dataset.

        Returns:
            Callable[[~.DeleteDatasetRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'delete_dataset' not in self._stubs:
            self._stubs['delete_dataset'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/DeleteDataset',
                request_serializer=dataset_service.DeleteDatasetRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['delete_dataset']

    @property
    def import_data(self) -> Callable[
            [dataset_service.ImportDataRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the import data method over gRPC.

        Imports data into a Dataset.

        Returns:
            Callable[[~.ImportDataRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'import_data' not in self._stubs:
            self._stubs['import_data'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ImportData',
                request_serializer=dataset_service.ImportDataRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['import_data']

    @property
    def export_data(self) -> Callable[
            [dataset_service.ExportDataRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the export data method over gRPC.

        Exports data from a Dataset.

        Returns:
            Callable[[~.ExportDataRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'export_data' not in self._stubs:
            self._stubs['export_data'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ExportData',
                request_serializer=dataset_service.ExportDataRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['export_data']

    @property
    def create_dataset_version(self) -> Callable[
            [dataset_service.CreateDatasetVersionRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the create dataset version method over gRPC.

        Create a version from a Dataset.

        Returns:
            Callable[[~.CreateDatasetVersionRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'create_dataset_version' not in self._stubs:
            self._stubs['create_dataset_version'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/CreateDatasetVersion',
                request_serializer=dataset_service.CreateDatasetVersionRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['create_dataset_version']

    @property
    def update_dataset_version(self) -> Callable[
            [dataset_service.UpdateDatasetVersionRequest],
            gca_dataset_version.DatasetVersion]:
        r"""Return a callable for the update dataset version method over gRPC.

        Updates a DatasetVersion.

        Returns:
            Callable[[~.UpdateDatasetVersionRequest],
                    ~.DatasetVersion]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'update_dataset_version' not in self._stubs:
            self._stubs['update_dataset_version'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/UpdateDatasetVersion',
                request_serializer=dataset_service.UpdateDatasetVersionRequest.serialize,
                response_deserializer=gca_dataset_version.DatasetVersion.deserialize,
            )
        return self._stubs['update_dataset_version']

    @property
    def delete_dataset_version(self) -> Callable[
            [dataset_service.DeleteDatasetVersionRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the delete dataset version method over gRPC.

        Deletes a Dataset version.

        Returns:
            Callable[[~.DeleteDatasetVersionRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'delete_dataset_version' not in self._stubs:
            self._stubs['delete_dataset_version'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/DeleteDatasetVersion',
                request_serializer=dataset_service.DeleteDatasetVersionRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['delete_dataset_version']

    @property
    def get_dataset_version(self) -> Callable[
            [dataset_service.GetDatasetVersionRequest],
            dataset_version.DatasetVersion]:
        r"""Return a callable for the get dataset version method over gRPC.

        Gets a Dataset version.

        Returns:
            Callable[[~.GetDatasetVersionRequest],
                    ~.DatasetVersion]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'get_dataset_version' not in self._stubs:
            self._stubs['get_dataset_version'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/GetDatasetVersion',
                request_serializer=dataset_service.GetDatasetVersionRequest.serialize,
                response_deserializer=dataset_version.DatasetVersion.deserialize,
            )
        return self._stubs['get_dataset_version']

    @property
    def list_dataset_versions(self) -> Callable[
            [dataset_service.ListDatasetVersionsRequest],
            dataset_service.ListDatasetVersionsResponse]:
        r"""Return a callable for the list dataset versions method over gRPC.

        Lists DatasetVersions in a Dataset.

        Returns:
            Callable[[~.ListDatasetVersionsRequest],
                    ~.ListDatasetVersionsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'list_dataset_versions' not in self._stubs:
            self._stubs['list_dataset_versions'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ListDatasetVersions',
                request_serializer=dataset_service.ListDatasetVersionsRequest.serialize,
                response_deserializer=dataset_service.ListDatasetVersionsResponse.deserialize,
            )
        return self._stubs['list_dataset_versions']

    @property
    def restore_dataset_version(self) -> Callable[
            [dataset_service.RestoreDatasetVersionRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the restore dataset version method over gRPC.

        Restores a dataset version.

        Returns:
            Callable[[~.RestoreDatasetVersionRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'restore_dataset_version' not in self._stubs:
            self._stubs['restore_dataset_version'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/RestoreDatasetVersion',
                request_serializer=dataset_service.RestoreDatasetVersionRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['restore_dataset_version']

    @property
    def list_data_items(self) -> Callable[
            [dataset_service.ListDataItemsRequest],
            dataset_service.ListDataItemsResponse]:
        r"""Return a callable for the list data items method over gRPC.

        Lists DataItems in a Dataset.

        Returns:
            Callable[[~.ListDataItemsRequest],
                    ~.ListDataItemsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'list_data_items' not in self._stubs:
            self._stubs['list_data_items'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ListDataItems',
                request_serializer=dataset_service.ListDataItemsRequest.serialize,
                response_deserializer=dataset_service.ListDataItemsResponse.deserialize,
            )
        return self._stubs['list_data_items']

    @property
    def search_data_items(self) -> Callable[
            [dataset_service.SearchDataItemsRequest],
            dataset_service.SearchDataItemsResponse]:
        r"""Return a callable for the search data items method over gRPC.

        Searches DataItems in a Dataset.

        Returns:
            Callable[[~.SearchDataItemsRequest],
                    ~.SearchDataItemsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'search_data_items' not in self._stubs:
            self._stubs['search_data_items'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/SearchDataItems',
                request_serializer=dataset_service.SearchDataItemsRequest.serialize,
                response_deserializer=dataset_service.SearchDataItemsResponse.deserialize,
            )
        return self._stubs['search_data_items']

    @property
    def list_saved_queries(self) -> Callable[
            [dataset_service.ListSavedQueriesRequest],
            dataset_service.ListSavedQueriesResponse]:
        r"""Return a callable for the list saved queries method over gRPC.

        Lists SavedQueries in a Dataset.

        Returns:
            Callable[[~.ListSavedQueriesRequest],
                    ~.ListSavedQueriesResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'list_saved_queries' not in self._stubs:
            self._stubs['list_saved_queries'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ListSavedQueries',
                request_serializer=dataset_service.ListSavedQueriesRequest.serialize,
                response_deserializer=dataset_service.ListSavedQueriesResponse.deserialize,
            )
        return self._stubs['list_saved_queries']

    @property
    def delete_saved_query(self) -> Callable[
            [dataset_service.DeleteSavedQueryRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the delete saved query method over gRPC.

        Deletes a SavedQuery.

        Returns:
            Callable[[~.DeleteSavedQueryRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'delete_saved_query' not in self._stubs:
            self._stubs['delete_saved_query'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/DeleteSavedQuery',
                request_serializer=dataset_service.DeleteSavedQueryRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['delete_saved_query']

    @property
    def get_annotation_spec(self) -> Callable[
            [dataset_service.GetAnnotationSpecRequest],
            annotation_spec.AnnotationSpec]:
        r"""Return a callable for the get annotation spec method over gRPC.

        Gets an AnnotationSpec.

        Returns:
            Callable[[~.GetAnnotationSpecRequest],
                    ~.AnnotationSpec]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'get_annotation_spec' not in self._stubs:
            self._stubs['get_annotation_spec'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/GetAnnotationSpec',
                request_serializer=dataset_service.GetAnnotationSpecRequest.serialize,
                response_deserializer=annotation_spec.AnnotationSpec.deserialize,
            )
        return self._stubs['get_annotation_spec']

    @property
    def list_annotations(self) -> Callable[
            [dataset_service.ListAnnotationsRequest],
            dataset_service.ListAnnotationsResponse]:
        r"""Return a callable for the list annotations method over gRPC.

        Lists Annotations belongs to a dataitem.

        Returns:
            Callable[[~.ListAnnotationsRequest],
                    ~.ListAnnotationsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'list_annotations' not in self._stubs:
            self._stubs['list_annotations'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/ListAnnotations',
                request_serializer=dataset_service.ListAnnotationsRequest.serialize,
                response_deserializer=dataset_service.ListAnnotationsResponse.deserialize,
            )
        return self._stubs['list_annotations']

    @property
    def assess_data(self) -> Callable[
            [dataset_service.AssessDataRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the assess data method over gRPC.

        Assesses the state or validity of the dataset with
        respect to a given use case.

        Returns:
            Callable[[~.AssessDataRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'assess_data' not in self._stubs:
            self._stubs['assess_data'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/AssessData',
                request_serializer=dataset_service.AssessDataRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['assess_data']

    @property
    def assemble_data(self) -> Callable[
            [dataset_service.AssembleDataRequest],
            operations_pb2.Operation]:
        r"""Return a callable for the assemble data method over gRPC.

        Assembles each row of a multimodal dataset and writes
        the result into a BigQuery table.

        Returns:
            Callable[[~.AssembleDataRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if 'assemble_data' not in self._stubs:
            self._stubs['assemble_data'] = self._logged_channel.unary_unary(
                '/google.cloud.aiplatform.v1beta1.DatasetService/AssembleData',
                request_serializer=dataset_service.AssembleDataRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs['assemble_data']

    def close(self):
        self._logged_channel.close()

    @property
    def delete_operation(
        self,
    ) -> Callable[[operations_pb2.DeleteOperationRequest], None]:
        r"""Return a callable for the delete_operation method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_operation" not in self._stubs:
            self._stubs["delete_operation"] = self._logged_channel.unary_unary(
                "/google.longrunning.Operations/DeleteOperation",
                request_serializer=operations_pb2.DeleteOperationRequest.SerializeToString,
                response_deserializer=None,
            )
        return self._stubs["delete_operation"]

    @property
    def cancel_operation(
        self,
    ) -> Callable[[operations_pb2.CancelOperationRequest], None]:
        r"""Return a callable for the cancel_operation method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "cancel_operation" not in self._stubs:
            self._stubs["cancel_operation"] = self._logged_channel.unary_unary(
                "/google.longrunning.Operations/CancelOperation",
                request_serializer=operations_pb2.CancelOperationRequest.SerializeToString,
                response_deserializer=None,
            )
        return self._stubs["cancel_operation"]

    @property
    def wait_operation(
        self,
    ) -> Callable[[operations_pb2.WaitOperationRequest], None]:
        r"""Return a callable for the wait_operation method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "wait_operation" not in self._stubs:
            self._stubs["wait_operation"] = self._logged_channel.unary_unary(
                "/google.longrunning.Operations/WaitOperation",
                request_serializer=operations_pb2.WaitOperationRequest.SerializeToString,
                response_deserializer=None,
            )
        return self._stubs["wait_operation"]

    @property
    def get_operation(
        self,
    ) -> Callable[[operations_pb2.GetOperationRequest], operations_pb2.Operation]:
        r"""Return a callable for the get_operation method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_operation" not in self._stubs:
            self._stubs["get_operation"] = self._logged_channel.unary_unary(
                "/google.longrunning.Operations/GetOperation",
                request_serializer=operations_pb2.GetOperationRequest.SerializeToString,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["get_operation"]

    @property
    def list_operations(
        self,
    ) -> Callable[[operations_pb2.ListOperationsRequest], operations_pb2.ListOperationsResponse]:
        r"""Return a callable for the list_operations method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_operations" not in self._stubs:
            self._stubs["list_operations"] = self._logged_channel.unary_unary(
                "/google.longrunning.Operations/ListOperations",
                request_serializer=operations_pb2.ListOperationsRequest.SerializeToString,
                response_deserializer=operations_pb2.ListOperationsResponse.FromString,
            )
        return self._stubs["list_operations"]

    @property
    def list_locations(
        self,
    ) -> Callable[[locations_pb2.ListLocationsRequest], locations_pb2.ListLocationsResponse]:
        r"""Return a callable for the list locations method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_locations" not in self._stubs:
            self._stubs["list_locations"] = self._logged_channel.unary_unary(
                "/google.cloud.location.Locations/ListLocations",
                request_serializer=locations_pb2.ListLocationsRequest.SerializeToString,
                response_deserializer=locations_pb2.ListLocationsResponse.FromString,
            )
        return self._stubs["list_locations"]

    @property
    def get_location(
        self,
    ) -> Callable[[locations_pb2.GetLocationRequest], locations_pb2.Location]:
        r"""Return a callable for the list locations method over gRPC.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_location" not in self._stubs:
            self._stubs["get_location"] = self._logged_channel.unary_unary(
                "/google.cloud.location.Locations/GetLocation",
                request_serializer=locations_pb2.GetLocationRequest.SerializeToString,
                response_deserializer=locations_pb2.Location.FromString,
            )
        return self._stubs["get_location"]

    @property
    def set_iam_policy(
        self,
    ) -> Callable[[iam_policy_pb2.SetIamPolicyRequest], policy_pb2.Policy]:
        r"""Return a callable for the set iam policy method over gRPC.
        Sets the IAM access control policy on the specified
        function. Replaces any existing policy.
        Returns:
            Callable[[~.SetIamPolicyRequest],
                    ~.Policy]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "set_iam_policy" not in self._stubs:
            self._stubs["set_iam_policy"] = self._logged_channel.unary_unary(
                "/google.iam.v1.IAMPolicy/SetIamPolicy",
                request_serializer=iam_policy_pb2.SetIamPolicyRequest.SerializeToString,
                response_deserializer=policy_pb2.Policy.FromString,
            )
        return self._stubs["set_iam_policy"]

    @property
    def get_iam_policy(
        self,
    ) -> Callable[[iam_policy_pb2.GetIamPolicyRequest], policy_pb2.Policy]:
        r"""Return a callable for the get iam policy method over gRPC.
        Gets the IAM access control policy for a function.
        Returns an empty policy if the function exists and does
        not have a policy set.
        Returns:
            Callable[[~.GetIamPolicyRequest],
                    ~.Policy]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_iam_policy" not in self._stubs:
            self._stubs["get_iam_policy"] = self._logged_channel.unary_unary(
                "/google.iam.v1.IAMPolicy/GetIamPolicy",
                request_serializer=iam_policy_pb2.GetIamPolicyRequest.SerializeToString,
                response_deserializer=policy_pb2.Policy.FromString,
            )
        return self._stubs["get_iam_policy"]

    @property
    def test_iam_permissions(
        self,
    ) -> Callable[
        [iam_policy_pb2.TestIamPermissionsRequest], iam_policy_pb2.TestIamPermissionsResponse
    ]:
        r"""Return a callable for the test iam permissions method over gRPC.
        Tests the specified permissions against the IAM access control
        policy for a function. If the function does not exist, this will
        return an empty set of permissions, not a NOT_FOUND error.
        Returns:
            Callable[[~.TestIamPermissionsRequest],
                    ~.TestIamPermissionsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "test_iam_permissions" not in self._stubs:
            self._stubs["test_iam_permissions"] = self._logged_channel.unary_unary(
                "/google.iam.v1.IAMPolicy/TestIamPermissions",
                request_serializer=iam_policy_pb2.TestIamPermissionsRequest.SerializeToString,
                response_deserializer=iam_policy_pb2.TestIamPermissionsResponse.FromString,
            )
        return self._stubs["test_iam_permissions"]

    @property
    def kind(self) -> str:
        return "grpc"


__all__ = (
    'DatasetServiceGrpcTransport',
)
