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

import abc
import typing
import pkg_resources

from google import auth  # type: ignore
from google.api_core import exceptions  # type: ignore
from google.api_core import gapic_v1    # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials  # type: ignore

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
from google.longrunning import operations_pb2 as operations  # type: ignore


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            'google-cloud-aiplatform',
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()

class MetadataServiceTransport(abc.ABC):
    """Abstract transport class for MetadataService."""

    AUTH_SCOPES = (
        'https://www.googleapis.com/auth/cloud-platform',
    )

    def __init__(
            self, *,
            host: str = 'aiplatform.googleapis.com',
            credentials: credentials.Credentials = None,
            credentials_file: typing.Optional[str] = None,
            scopes: typing.Optional[typing.Sequence[str]] = AUTH_SCOPES,
            quota_project_id: typing.Optional[str] = None,
            client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
            **kwargs,
            ) -> None:
        """Instantiate the transport.

        Args:
            host (Optional[str]): The hostname to connect to.
            credentials (Optional[google.auth.credentials.Credentials]): The
                authorization credentials to attach to requests. These
                credentials identify the application to the service; if none
                are specified, the client will attempt to ascertain the
                credentials from the environment.
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scope (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ':' not in host:
            host += ':443'
        self._host = host

        # Save the scopes.
        self._scopes = scopes or self.AUTH_SCOPES

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise exceptions.DuplicateCredentialArgs("'credentials_file' and 'credentials' are mutually exclusive")

        if credentials_file is not None:
            credentials, _ = auth.load_credentials_from_file(
                                credentials_file,
                                scopes=self._scopes,
                                quota_project_id=quota_project_id
                            )

        elif credentials is None:
            credentials, _ = auth.default(scopes=self._scopes, quota_project_id=quota_project_id)

        # Save the credentials.
        self._credentials = credentials

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_metadata_store: gapic_v1.method.wrap_method(
                self.create_metadata_store,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_metadata_store: gapic_v1.method.wrap_method(
                self.get_metadata_store,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_metadata_stores: gapic_v1.method.wrap_method(
                self.list_metadata_stores,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.delete_metadata_store: gapic_v1.method.wrap_method(
                self.delete_metadata_store,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_artifact: gapic_v1.method.wrap_method(
                self.create_artifact,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_artifact: gapic_v1.method.wrap_method(
                self.get_artifact,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_artifacts: gapic_v1.method.wrap_method(
                self.list_artifacts,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.update_artifact: gapic_v1.method.wrap_method(
                self.update_artifact,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_context: gapic_v1.method.wrap_method(
                self.create_context,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_context: gapic_v1.method.wrap_method(
                self.get_context,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_contexts: gapic_v1.method.wrap_method(
                self.list_contexts,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.update_context: gapic_v1.method.wrap_method(
                self.update_context,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.delete_context: gapic_v1.method.wrap_method(
                self.delete_context,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.add_context_artifacts_and_executions: gapic_v1.method.wrap_method(
                self.add_context_artifacts_and_executions,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.add_context_children: gapic_v1.method.wrap_method(
                self.add_context_children,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.query_context_lineage_subgraph: gapic_v1.method.wrap_method(
                self.query_context_lineage_subgraph,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_execution: gapic_v1.method.wrap_method(
                self.create_execution,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_execution: gapic_v1.method.wrap_method(
                self.get_execution,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_executions: gapic_v1.method.wrap_method(
                self.list_executions,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.update_execution: gapic_v1.method.wrap_method(
                self.update_execution,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.add_execution_events: gapic_v1.method.wrap_method(
                self.add_execution_events,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.query_execution_inputs_and_outputs: gapic_v1.method.wrap_method(
                self.query_execution_inputs_and_outputs,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_metadata_schema: gapic_v1.method.wrap_method(
                self.create_metadata_schema,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_metadata_schema: gapic_v1.method.wrap_method(
                self.get_metadata_schema,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_metadata_schemas: gapic_v1.method.wrap_method(
                self.list_metadata_schemas,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.query_artifact_lineage_subgraph: gapic_v1.method.wrap_method(
                self.query_artifact_lineage_subgraph,
                default_timeout=None,
                client_info=client_info,
            ),

        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_metadata_store(self) -> typing.Callable[
            [metadata_service.CreateMetadataStoreRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def get_metadata_store(self) -> typing.Callable[
            [metadata_service.GetMetadataStoreRequest],
            typing.Union[
                metadata_store.MetadataStore,
                typing.Awaitable[metadata_store.MetadataStore]
            ]]:
        raise NotImplementedError()

    @property
    def list_metadata_stores(self) -> typing.Callable[
            [metadata_service.ListMetadataStoresRequest],
            typing.Union[
                metadata_service.ListMetadataStoresResponse,
                typing.Awaitable[metadata_service.ListMetadataStoresResponse]
            ]]:
        raise NotImplementedError()

    @property
    def delete_metadata_store(self) -> typing.Callable[
            [metadata_service.DeleteMetadataStoreRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_artifact(self) -> typing.Callable[
            [metadata_service.CreateArtifactRequest],
            typing.Union[
                gca_artifact.Artifact,
                typing.Awaitable[gca_artifact.Artifact]
            ]]:
        raise NotImplementedError()

    @property
    def get_artifact(self) -> typing.Callable[
            [metadata_service.GetArtifactRequest],
            typing.Union[
                artifact.Artifact,
                typing.Awaitable[artifact.Artifact]
            ]]:
        raise NotImplementedError()

    @property
    def list_artifacts(self) -> typing.Callable[
            [metadata_service.ListArtifactsRequest],
            typing.Union[
                metadata_service.ListArtifactsResponse,
                typing.Awaitable[metadata_service.ListArtifactsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def update_artifact(self) -> typing.Callable[
            [metadata_service.UpdateArtifactRequest],
            typing.Union[
                gca_artifact.Artifact,
                typing.Awaitable[gca_artifact.Artifact]
            ]]:
        raise NotImplementedError()

    @property
    def create_context(self) -> typing.Callable[
            [metadata_service.CreateContextRequest],
            typing.Union[
                gca_context.Context,
                typing.Awaitable[gca_context.Context]
            ]]:
        raise NotImplementedError()

    @property
    def get_context(self) -> typing.Callable[
            [metadata_service.GetContextRequest],
            typing.Union[
                context.Context,
                typing.Awaitable[context.Context]
            ]]:
        raise NotImplementedError()

    @property
    def list_contexts(self) -> typing.Callable[
            [metadata_service.ListContextsRequest],
            typing.Union[
                metadata_service.ListContextsResponse,
                typing.Awaitable[metadata_service.ListContextsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def update_context(self) -> typing.Callable[
            [metadata_service.UpdateContextRequest],
            typing.Union[
                gca_context.Context,
                typing.Awaitable[gca_context.Context]
            ]]:
        raise NotImplementedError()

    @property
    def delete_context(self) -> typing.Callable[
            [metadata_service.DeleteContextRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def add_context_artifacts_and_executions(self) -> typing.Callable[
            [metadata_service.AddContextArtifactsAndExecutionsRequest],
            typing.Union[
                metadata_service.AddContextArtifactsAndExecutionsResponse,
                typing.Awaitable[metadata_service.AddContextArtifactsAndExecutionsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def add_context_children(self) -> typing.Callable[
            [metadata_service.AddContextChildrenRequest],
            typing.Union[
                metadata_service.AddContextChildrenResponse,
                typing.Awaitable[metadata_service.AddContextChildrenResponse]
            ]]:
        raise NotImplementedError()

    @property
    def query_context_lineage_subgraph(self) -> typing.Callable[
            [metadata_service.QueryContextLineageSubgraphRequest],
            typing.Union[
                lineage_subgraph.LineageSubgraph,
                typing.Awaitable[lineage_subgraph.LineageSubgraph]
            ]]:
        raise NotImplementedError()

    @property
    def create_execution(self) -> typing.Callable[
            [metadata_service.CreateExecutionRequest],
            typing.Union[
                gca_execution.Execution,
                typing.Awaitable[gca_execution.Execution]
            ]]:
        raise NotImplementedError()

    @property
    def get_execution(self) -> typing.Callable[
            [metadata_service.GetExecutionRequest],
            typing.Union[
                execution.Execution,
                typing.Awaitable[execution.Execution]
            ]]:
        raise NotImplementedError()

    @property
    def list_executions(self) -> typing.Callable[
            [metadata_service.ListExecutionsRequest],
            typing.Union[
                metadata_service.ListExecutionsResponse,
                typing.Awaitable[metadata_service.ListExecutionsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def update_execution(self) -> typing.Callable[
            [metadata_service.UpdateExecutionRequest],
            typing.Union[
                gca_execution.Execution,
                typing.Awaitable[gca_execution.Execution]
            ]]:
        raise NotImplementedError()

    @property
    def add_execution_events(self) -> typing.Callable[
            [metadata_service.AddExecutionEventsRequest],
            typing.Union[
                metadata_service.AddExecutionEventsResponse,
                typing.Awaitable[metadata_service.AddExecutionEventsResponse]
            ]]:
        raise NotImplementedError()

    @property
    def query_execution_inputs_and_outputs(self) -> typing.Callable[
            [metadata_service.QueryExecutionInputsAndOutputsRequest],
            typing.Union[
                lineage_subgraph.LineageSubgraph,
                typing.Awaitable[lineage_subgraph.LineageSubgraph]
            ]]:
        raise NotImplementedError()

    @property
    def create_metadata_schema(self) -> typing.Callable[
            [metadata_service.CreateMetadataSchemaRequest],
            typing.Union[
                gca_metadata_schema.MetadataSchema,
                typing.Awaitable[gca_metadata_schema.MetadataSchema]
            ]]:
        raise NotImplementedError()

    @property
    def get_metadata_schema(self) -> typing.Callable[
            [metadata_service.GetMetadataSchemaRequest],
            typing.Union[
                metadata_schema.MetadataSchema,
                typing.Awaitable[metadata_schema.MetadataSchema]
            ]]:
        raise NotImplementedError()

    @property
    def list_metadata_schemas(self) -> typing.Callable[
            [metadata_service.ListMetadataSchemasRequest],
            typing.Union[
                metadata_service.ListMetadataSchemasResponse,
                typing.Awaitable[metadata_service.ListMetadataSchemasResponse]
            ]]:
        raise NotImplementedError()

    @property
    def query_artifact_lineage_subgraph(self) -> typing.Callable[
            [metadata_service.QueryArtifactLineageSubgraphRequest],
            typing.Union[
                lineage_subgraph.LineageSubgraph,
                typing.Awaitable[lineage_subgraph.LineageSubgraph]
            ]]:
        raise NotImplementedError()


__all__ = (
    'MetadataServiceTransport',
)
