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
import warnings
from typing import Callable, Dict, Optional, Sequence, Tuple, Union

from google.api_core import grpc_helpers  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.api_core import gapic_v1  # type: ignore
import google.auth  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore
from google.auth.transport.grpc import SslCredentials  # type: ignore

import grpc  # type: ignore

from google.cloud.aiplatform_v1beta1.types import artifact
from google.cloud.aiplatform_v1beta1.types import artifact as gca_artifact
from google.cloud.aiplatform_v1beta1.types import context
from google.cloud.aiplatform_v1beta1.types import context as gca_context
from google.cloud.aiplatform_v1beta1.types import execution
from google.cloud.aiplatform_v1beta1.types import execution as gca_execution
from google.cloud.aiplatform_v1beta1.types import lineage_subgraph
from google.cloud.aiplatform_v1beta1.types import metadata_schema
from google.cloud.aiplatform_v1beta1.types import metadata_schema as gca_metadata_schema
from google.cloud.aiplatform_v1beta1.types import metadata_service
from google.cloud.aiplatform_v1beta1.types import metadata_store
from google.longrunning import operations_pb2  # type: ignore
from .base import MetadataServiceTransport, DEFAULT_CLIENT_INFO


class MetadataServiceGrpcTransport(MetadataServiceTransport):
    """gRPC backend transport for MetadataService.

    Service for reading and writing metadata entries.

    This class defines the same methods as the primary client, so the
    primary client can load the underlying transport implementation
    and call it.

    It sends protocol buffers over the wire using gRPC (which is built on
    top of HTTP/2); the ``grpcio`` package must be installed.
    """

    _stubs: Dict[str, Callable]

    def __init__(
        self,
        *,
        host: str = "aiplatform.googleapis.com",
        credentials: ga_credentials.Credentials = None,
        credentials_file: str = None,
        scopes: Sequence[str] = None,
        channel: grpc.Channel = None,
        api_mtls_endpoint: str = None,
        client_cert_source: Callable[[], Tuple[bytes, bytes]] = None,
        ssl_channel_credentials: grpc.ChannelCredentials = None,
        client_cert_source_for_mtls: Callable[[], Tuple[bytes, bytes]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
    ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]):
                 The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
                This argument is ignored if ``channel`` is provided.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is ignored if ``channel`` is provided.
            scopes (Optional(Sequence[str])): A list of scopes. This argument is
                ignored if ``channel`` is provided.
            channel (Optional[grpc.Channel]): A ``Channel`` instance through
                which to make calls.
            api_mtls_endpoint (Optional[str]): Deprecated. The mutual TLS endpoint.
                If provided, it overrides the ``host`` argument and tries to create
                a mutual TLS channel with client SSL credentials from
                ``client_cert_source`` or applicatin default SSL credentials.
            client_cert_source (Optional[Callable[[], Tuple[bytes, bytes]]]):
                Deprecated. A callback to provide client SSL certificate bytes and
                private key bytes, both in PEM format. It is ignored if
                ``api_mtls_endpoint`` is None.
            ssl_channel_credentials (grpc.ChannelCredentials): SSL credentials
                for grpc channel. It is ignored if ``channel`` is provided.
            client_cert_source_for_mtls (Optional[Callable[[], Tuple[bytes, bytes]]]):
                A callback to provide client certificate bytes and private key bytes,
                both in PEM format. It is used to configure mutual TLS channel. It is
                ignored if ``channel`` or ``ssl_channel_credentials`` is provided.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.

        Raises:
          google.auth.exceptions.MutualTLSChannelError: If mutual TLS transport
              creation failed for any reason.
          google.api_core.exceptions.DuplicateCredentialArgs: If both ``credentials``
              and ``credentials_file`` are passed.
        """
        self._grpc_channel = None
        self._ssl_channel_credentials = ssl_channel_credentials
        self._stubs: Dict[str, Callable] = {}
        self._operations_client = None

        if api_mtls_endpoint:
            warnings.warn("api_mtls_endpoint is deprecated", DeprecationWarning)
        if client_cert_source:
            warnings.warn("client_cert_source is deprecated", DeprecationWarning)

        if channel:
            # Ignore credentials if a channel was passed.
            credentials = False
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
        )

        if not self._grpc_channel:
            self._grpc_channel = type(self).create_channel(
                self._host,
                credentials=self._credentials,
                credentials_file=credentials_file,
                scopes=self._scopes,
                ssl_credentials=self._ssl_channel_credentials,
                quota_project_id=quota_project_id,
                options=[
                    ("grpc.max_send_message_length", -1),
                    ("grpc.max_receive_message_length", -1),
                ],
            )

        # Wrap messages. This must be done after self._grpc_channel exists
        self._prep_wrapped_messages(client_info)

    @classmethod
    def create_channel(
        cls,
        host: str = "aiplatform.googleapis.com",
        credentials: ga_credentials.Credentials = None,
        credentials_file: str = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        **kwargs,
    ) -> grpc.Channel:
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

        self_signed_jwt_kwargs = cls._get_self_signed_jwt_kwargs(host, scopes)

        return grpc_helpers.create_channel(
            host,
            credentials=credentials,
            credentials_file=credentials_file,
            quota_project_id=quota_project_id,
            **self_signed_jwt_kwargs,
            **kwargs,
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
        # Sanity check: Only create a new client if we do not already have one.
        if self._operations_client is None:
            self._operations_client = operations_v1.OperationsClient(self.grpc_channel)

        # Return the client from cache.
        return self._operations_client

    @property
    def create_metadata_store(
        self,
    ) -> Callable[
        [metadata_service.CreateMetadataStoreRequest], operations_pb2.Operation
    ]:
        r"""Return a callable for the create metadata store method over gRPC.

        Initializes a MetadataStore, including allocation of
        resources.

        Returns:
            Callable[[~.CreateMetadataStoreRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_metadata_store" not in self._stubs:
            self._stubs["create_metadata_store"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/CreateMetadataStore",
                request_serializer=metadata_service.CreateMetadataStoreRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["create_metadata_store"]

    @property
    def get_metadata_store(
        self,
    ) -> Callable[
        [metadata_service.GetMetadataStoreRequest], metadata_store.MetadataStore
    ]:
        r"""Return a callable for the get metadata store method over gRPC.

        Retrieves a specific MetadataStore.

        Returns:
            Callable[[~.GetMetadataStoreRequest],
                    ~.MetadataStore]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_metadata_store" not in self._stubs:
            self._stubs["get_metadata_store"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/GetMetadataStore",
                request_serializer=metadata_service.GetMetadataStoreRequest.serialize,
                response_deserializer=metadata_store.MetadataStore.deserialize,
            )
        return self._stubs["get_metadata_store"]

    @property
    def list_metadata_stores(
        self,
    ) -> Callable[
        [metadata_service.ListMetadataStoresRequest],
        metadata_service.ListMetadataStoresResponse,
    ]:
        r"""Return a callable for the list metadata stores method over gRPC.

        Lists MetadataStores for a Location.

        Returns:
            Callable[[~.ListMetadataStoresRequest],
                    ~.ListMetadataStoresResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_metadata_stores" not in self._stubs:
            self._stubs["list_metadata_stores"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/ListMetadataStores",
                request_serializer=metadata_service.ListMetadataStoresRequest.serialize,
                response_deserializer=metadata_service.ListMetadataStoresResponse.deserialize,
            )
        return self._stubs["list_metadata_stores"]

    @property
    def delete_metadata_store(
        self,
    ) -> Callable[
        [metadata_service.DeleteMetadataStoreRequest], operations_pb2.Operation
    ]:
        r"""Return a callable for the delete metadata store method over gRPC.

        Deletes a single MetadataStore.

        Returns:
            Callable[[~.DeleteMetadataStoreRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_metadata_store" not in self._stubs:
            self._stubs["delete_metadata_store"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/DeleteMetadataStore",
                request_serializer=metadata_service.DeleteMetadataStoreRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["delete_metadata_store"]

    @property
    def create_artifact(
        self,
    ) -> Callable[[metadata_service.CreateArtifactRequest], gca_artifact.Artifact]:
        r"""Return a callable for the create artifact method over gRPC.

        Creates an Artifact associated with a MetadataStore.

        Returns:
            Callable[[~.CreateArtifactRequest],
                    ~.Artifact]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_artifact" not in self._stubs:
            self._stubs["create_artifact"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/CreateArtifact",
                request_serializer=metadata_service.CreateArtifactRequest.serialize,
                response_deserializer=gca_artifact.Artifact.deserialize,
            )
        return self._stubs["create_artifact"]

    @property
    def get_artifact(
        self,
    ) -> Callable[[metadata_service.GetArtifactRequest], artifact.Artifact]:
        r"""Return a callable for the get artifact method over gRPC.

        Retrieves a specific Artifact.

        Returns:
            Callable[[~.GetArtifactRequest],
                    ~.Artifact]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_artifact" not in self._stubs:
            self._stubs["get_artifact"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/GetArtifact",
                request_serializer=metadata_service.GetArtifactRequest.serialize,
                response_deserializer=artifact.Artifact.deserialize,
            )
        return self._stubs["get_artifact"]

    @property
    def list_artifacts(
        self,
    ) -> Callable[
        [metadata_service.ListArtifactsRequest], metadata_service.ListArtifactsResponse
    ]:
        r"""Return a callable for the list artifacts method over gRPC.

        Lists Artifacts in the MetadataStore.

        Returns:
            Callable[[~.ListArtifactsRequest],
                    ~.ListArtifactsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_artifacts" not in self._stubs:
            self._stubs["list_artifacts"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/ListArtifacts",
                request_serializer=metadata_service.ListArtifactsRequest.serialize,
                response_deserializer=metadata_service.ListArtifactsResponse.deserialize,
            )
        return self._stubs["list_artifacts"]

    @property
    def update_artifact(
        self,
    ) -> Callable[[metadata_service.UpdateArtifactRequest], gca_artifact.Artifact]:
        r"""Return a callable for the update artifact method over gRPC.

        Updates a stored Artifact.

        Returns:
            Callable[[~.UpdateArtifactRequest],
                    ~.Artifact]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_artifact" not in self._stubs:
            self._stubs["update_artifact"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/UpdateArtifact",
                request_serializer=metadata_service.UpdateArtifactRequest.serialize,
                response_deserializer=gca_artifact.Artifact.deserialize,
            )
        return self._stubs["update_artifact"]

    @property
    def create_context(
        self,
    ) -> Callable[[metadata_service.CreateContextRequest], gca_context.Context]:
        r"""Return a callable for the create context method over gRPC.

        Creates a Context associated with a MetadataStore.

        Returns:
            Callable[[~.CreateContextRequest],
                    ~.Context]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_context" not in self._stubs:
            self._stubs["create_context"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/CreateContext",
                request_serializer=metadata_service.CreateContextRequest.serialize,
                response_deserializer=gca_context.Context.deserialize,
            )
        return self._stubs["create_context"]

    @property
    def get_context(
        self,
    ) -> Callable[[metadata_service.GetContextRequest], context.Context]:
        r"""Return a callable for the get context method over gRPC.

        Retrieves a specific Context.

        Returns:
            Callable[[~.GetContextRequest],
                    ~.Context]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_context" not in self._stubs:
            self._stubs["get_context"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/GetContext",
                request_serializer=metadata_service.GetContextRequest.serialize,
                response_deserializer=context.Context.deserialize,
            )
        return self._stubs["get_context"]

    @property
    def list_contexts(
        self,
    ) -> Callable[
        [metadata_service.ListContextsRequest], metadata_service.ListContextsResponse
    ]:
        r"""Return a callable for the list contexts method over gRPC.

        Lists Contexts on the MetadataStore.

        Returns:
            Callable[[~.ListContextsRequest],
                    ~.ListContextsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_contexts" not in self._stubs:
            self._stubs["list_contexts"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/ListContexts",
                request_serializer=metadata_service.ListContextsRequest.serialize,
                response_deserializer=metadata_service.ListContextsResponse.deserialize,
            )
        return self._stubs["list_contexts"]

    @property
    def update_context(
        self,
    ) -> Callable[[metadata_service.UpdateContextRequest], gca_context.Context]:
        r"""Return a callable for the update context method over gRPC.

        Updates a stored Context.

        Returns:
            Callable[[~.UpdateContextRequest],
                    ~.Context]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_context" not in self._stubs:
            self._stubs["update_context"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/UpdateContext",
                request_serializer=metadata_service.UpdateContextRequest.serialize,
                response_deserializer=gca_context.Context.deserialize,
            )
        return self._stubs["update_context"]

    @property
    def delete_context(
        self,
    ) -> Callable[[metadata_service.DeleteContextRequest], operations_pb2.Operation]:
        r"""Return a callable for the delete context method over gRPC.

        Deletes a stored Context.

        Returns:
            Callable[[~.DeleteContextRequest],
                    ~.Operation]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "delete_context" not in self._stubs:
            self._stubs["delete_context"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/DeleteContext",
                request_serializer=metadata_service.DeleteContextRequest.serialize,
                response_deserializer=operations_pb2.Operation.FromString,
            )
        return self._stubs["delete_context"]

    @property
    def add_context_artifacts_and_executions(
        self,
    ) -> Callable[
        [metadata_service.AddContextArtifactsAndExecutionsRequest],
        metadata_service.AddContextArtifactsAndExecutionsResponse,
    ]:
        r"""Return a callable for the add context artifacts and
        executions method over gRPC.

        Adds a set of Artifacts and Executions to a Context.
        If any of the Artifacts or Executions have already been
        added to a Context, they are simply skipped.

        Returns:
            Callable[[~.AddContextArtifactsAndExecutionsRequest],
                    ~.AddContextArtifactsAndExecutionsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "add_context_artifacts_and_executions" not in self._stubs:
            self._stubs[
                "add_context_artifacts_and_executions"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/AddContextArtifactsAndExecutions",
                request_serializer=metadata_service.AddContextArtifactsAndExecutionsRequest.serialize,
                response_deserializer=metadata_service.AddContextArtifactsAndExecutionsResponse.deserialize,
            )
        return self._stubs["add_context_artifacts_and_executions"]

    @property
    def add_context_children(
        self,
    ) -> Callable[
        [metadata_service.AddContextChildrenRequest],
        metadata_service.AddContextChildrenResponse,
    ]:
        r"""Return a callable for the add context children method over gRPC.

        Adds a set of Contexts as children to a parent Context. If any
        of the child Contexts have already been added to the parent
        Context, they are simply skipped. If this call would create a
        cycle or cause any Context to have more than 10 parents, the
        request will fail with INVALID_ARGUMENT error.

        Returns:
            Callable[[~.AddContextChildrenRequest],
                    ~.AddContextChildrenResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "add_context_children" not in self._stubs:
            self._stubs["add_context_children"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/AddContextChildren",
                request_serializer=metadata_service.AddContextChildrenRequest.serialize,
                response_deserializer=metadata_service.AddContextChildrenResponse.deserialize,
            )
        return self._stubs["add_context_children"]

    @property
    def query_context_lineage_subgraph(
        self,
    ) -> Callable[
        [metadata_service.QueryContextLineageSubgraphRequest],
        lineage_subgraph.LineageSubgraph,
    ]:
        r"""Return a callable for the query context lineage subgraph method over gRPC.

        Retrieves Artifacts and Executions within the
        specified Context, connected by Event edges and returned
        as a LineageSubgraph.

        Returns:
            Callable[[~.QueryContextLineageSubgraphRequest],
                    ~.LineageSubgraph]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "query_context_lineage_subgraph" not in self._stubs:
            self._stubs[
                "query_context_lineage_subgraph"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/QueryContextLineageSubgraph",
                request_serializer=metadata_service.QueryContextLineageSubgraphRequest.serialize,
                response_deserializer=lineage_subgraph.LineageSubgraph.deserialize,
            )
        return self._stubs["query_context_lineage_subgraph"]

    @property
    def create_execution(
        self,
    ) -> Callable[[metadata_service.CreateExecutionRequest], gca_execution.Execution]:
        r"""Return a callable for the create execution method over gRPC.

        Creates an Execution associated with a MetadataStore.

        Returns:
            Callable[[~.CreateExecutionRequest],
                    ~.Execution]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_execution" not in self._stubs:
            self._stubs["create_execution"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/CreateExecution",
                request_serializer=metadata_service.CreateExecutionRequest.serialize,
                response_deserializer=gca_execution.Execution.deserialize,
            )
        return self._stubs["create_execution"]

    @property
    def get_execution(
        self,
    ) -> Callable[[metadata_service.GetExecutionRequest], execution.Execution]:
        r"""Return a callable for the get execution method over gRPC.

        Retrieves a specific Execution.

        Returns:
            Callable[[~.GetExecutionRequest],
                    ~.Execution]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_execution" not in self._stubs:
            self._stubs["get_execution"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/GetExecution",
                request_serializer=metadata_service.GetExecutionRequest.serialize,
                response_deserializer=execution.Execution.deserialize,
            )
        return self._stubs["get_execution"]

    @property
    def list_executions(
        self,
    ) -> Callable[
        [metadata_service.ListExecutionsRequest],
        metadata_service.ListExecutionsResponse,
    ]:
        r"""Return a callable for the list executions method over gRPC.

        Lists Executions in the MetadataStore.

        Returns:
            Callable[[~.ListExecutionsRequest],
                    ~.ListExecutionsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_executions" not in self._stubs:
            self._stubs["list_executions"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/ListExecutions",
                request_serializer=metadata_service.ListExecutionsRequest.serialize,
                response_deserializer=metadata_service.ListExecutionsResponse.deserialize,
            )
        return self._stubs["list_executions"]

    @property
    def update_execution(
        self,
    ) -> Callable[[metadata_service.UpdateExecutionRequest], gca_execution.Execution]:
        r"""Return a callable for the update execution method over gRPC.

        Updates a stored Execution.

        Returns:
            Callable[[~.UpdateExecutionRequest],
                    ~.Execution]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "update_execution" not in self._stubs:
            self._stubs["update_execution"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/UpdateExecution",
                request_serializer=metadata_service.UpdateExecutionRequest.serialize,
                response_deserializer=gca_execution.Execution.deserialize,
            )
        return self._stubs["update_execution"]

    @property
    def add_execution_events(
        self,
    ) -> Callable[
        [metadata_service.AddExecutionEventsRequest],
        metadata_service.AddExecutionEventsResponse,
    ]:
        r"""Return a callable for the add execution events method over gRPC.

        Adds Events for denoting whether each Artifact was an
        input or output for a given Execution. If any Events
        already exist between the Execution and any of the
        specified Artifacts they are simply skipped.

        Returns:
            Callable[[~.AddExecutionEventsRequest],
                    ~.AddExecutionEventsResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "add_execution_events" not in self._stubs:
            self._stubs["add_execution_events"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/AddExecutionEvents",
                request_serializer=metadata_service.AddExecutionEventsRequest.serialize,
                response_deserializer=metadata_service.AddExecutionEventsResponse.deserialize,
            )
        return self._stubs["add_execution_events"]

    @property
    def query_execution_inputs_and_outputs(
        self,
    ) -> Callable[
        [metadata_service.QueryExecutionInputsAndOutputsRequest],
        lineage_subgraph.LineageSubgraph,
    ]:
        r"""Return a callable for the query execution inputs and
        outputs method over gRPC.

        Obtains the set of input and output Artifacts for
        this Execution, in the form of LineageSubgraph that also
        contains the Execution and connecting Events.

        Returns:
            Callable[[~.QueryExecutionInputsAndOutputsRequest],
                    ~.LineageSubgraph]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "query_execution_inputs_and_outputs" not in self._stubs:
            self._stubs[
                "query_execution_inputs_and_outputs"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/QueryExecutionInputsAndOutputs",
                request_serializer=metadata_service.QueryExecutionInputsAndOutputsRequest.serialize,
                response_deserializer=lineage_subgraph.LineageSubgraph.deserialize,
            )
        return self._stubs["query_execution_inputs_and_outputs"]

    @property
    def create_metadata_schema(
        self,
    ) -> Callable[
        [metadata_service.CreateMetadataSchemaRequest],
        gca_metadata_schema.MetadataSchema,
    ]:
        r"""Return a callable for the create metadata schema method over gRPC.

        Creates an MetadataSchema.

        Returns:
            Callable[[~.CreateMetadataSchemaRequest],
                    ~.MetadataSchema]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "create_metadata_schema" not in self._stubs:
            self._stubs["create_metadata_schema"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/CreateMetadataSchema",
                request_serializer=metadata_service.CreateMetadataSchemaRequest.serialize,
                response_deserializer=gca_metadata_schema.MetadataSchema.deserialize,
            )
        return self._stubs["create_metadata_schema"]

    @property
    def get_metadata_schema(
        self,
    ) -> Callable[
        [metadata_service.GetMetadataSchemaRequest], metadata_schema.MetadataSchema
    ]:
        r"""Return a callable for the get metadata schema method over gRPC.

        Retrieves a specific MetadataSchema.

        Returns:
            Callable[[~.GetMetadataSchemaRequest],
                    ~.MetadataSchema]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "get_metadata_schema" not in self._stubs:
            self._stubs["get_metadata_schema"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/GetMetadataSchema",
                request_serializer=metadata_service.GetMetadataSchemaRequest.serialize,
                response_deserializer=metadata_schema.MetadataSchema.deserialize,
            )
        return self._stubs["get_metadata_schema"]

    @property
    def list_metadata_schemas(
        self,
    ) -> Callable[
        [metadata_service.ListMetadataSchemasRequest],
        metadata_service.ListMetadataSchemasResponse,
    ]:
        r"""Return a callable for the list metadata schemas method over gRPC.

        Lists MetadataSchemas.

        Returns:
            Callable[[~.ListMetadataSchemasRequest],
                    ~.ListMetadataSchemasResponse]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "list_metadata_schemas" not in self._stubs:
            self._stubs["list_metadata_schemas"] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/ListMetadataSchemas",
                request_serializer=metadata_service.ListMetadataSchemasRequest.serialize,
                response_deserializer=metadata_service.ListMetadataSchemasResponse.deserialize,
            )
        return self._stubs["list_metadata_schemas"]

    @property
    def query_artifact_lineage_subgraph(
        self,
    ) -> Callable[
        [metadata_service.QueryArtifactLineageSubgraphRequest],
        lineage_subgraph.LineageSubgraph,
    ]:
        r"""Return a callable for the query artifact lineage
        subgraph method over gRPC.

        Retrieves lineage of an Artifact represented through
        Artifacts and Executions connected by Event edges and
        returned as a LineageSubgraph.

        Returns:
            Callable[[~.QueryArtifactLineageSubgraphRequest],
                    ~.LineageSubgraph]:
                A function that, when called, will call the underlying RPC
                on the server.
        """
        # Generate a "stub function" on-the-fly which will actually make
        # the request.
        # gRPC handles serialization and deserialization, so we just need
        # to pass in the functions for each.
        if "query_artifact_lineage_subgraph" not in self._stubs:
            self._stubs[
                "query_artifact_lineage_subgraph"
            ] = self.grpc_channel.unary_unary(
                "/google.cloud.aiplatform.v1beta1.MetadataService/QueryArtifactLineageSubgraph",
                request_serializer=metadata_service.QueryArtifactLineageSubgraphRequest.serialize,
                response_deserializer=lineage_subgraph.LineageSubgraph.deserialize,
            )
        return self._stubs["query_artifact_lineage_subgraph"]


__all__ = ("MetadataServiceGrpcTransport",)
