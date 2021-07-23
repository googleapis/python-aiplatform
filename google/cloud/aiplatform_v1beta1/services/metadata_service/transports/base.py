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
from typing import Awaitable, Callable, Dict, Optional, Sequence, Union
import packaging.version
import pkg_resources

import google.auth  # type: ignore
import google.api_core  # type: ignore
from google.api_core import exceptions as core_exceptions  # type: ignore
from google.api_core import gapic_v1  # type: ignore
from google.api_core import retry as retries  # type: ignore
from google.api_core import operations_v1  # type: ignore
from google.auth import credentials as ga_credentials  # type: ignore

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

try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            "google-cloud-aiplatform",
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()

try:
    # google.auth.__version__ was added in 1.26.0
    _GOOGLE_AUTH_VERSION = google.auth.__version__
except AttributeError:
    try:  # try pkg_resources if it is available
        _GOOGLE_AUTH_VERSION = pkg_resources.get_distribution("google-auth").version
    except pkg_resources.DistributionNotFound:  # pragma: NO COVER
        _GOOGLE_AUTH_VERSION = None

_API_CORE_VERSION = google.api_core.__version__


class MetadataServiceTransport(abc.ABC):
    """Abstract transport class for MetadataService."""

    AUTH_SCOPES = ("https://www.googleapis.com/auth/cloud-platform",)

    DEFAULT_HOST: str = "aiplatform.googleapis.com"

    def __init__(
        self,
        *,
        host: str = DEFAULT_HOST,
        credentials: ga_credentials.Credentials = None,
        credentials_file: Optional[str] = None,
        scopes: Optional[Sequence[str]] = None,
        quota_project_id: Optional[str] = None,
        client_info: gapic_v1.client_info.ClientInfo = DEFAULT_CLIENT_INFO,
        **kwargs,
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
            credentials_file (Optional[str]): A file with credentials that can
                be loaded with :func:`google.auth.load_credentials_from_file`.
                This argument is mutually exclusive with credentials.
            scopes (Optional[Sequence[str]]): A list of scopes.
            quota_project_id (Optional[str]): An optional project to use for billing
                and quota.
            client_info (google.api_core.gapic_v1.client_info.ClientInfo):
                The client info used to send a user-agent string along with
                API requests. If ``None``, then default info will be used.
                Generally, you only need to set this if you're developing
                your own client library.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

        scopes_kwargs = self._get_scopes_kwargs(self._host, scopes)

        # Save the scopes.
        self._scopes = scopes or self.AUTH_SCOPES

        # If no credentials are provided, then determine the appropriate
        # defaults.
        if credentials and credentials_file:
            raise core_exceptions.DuplicateCredentialArgs(
                "'credentials_file' and 'credentials' are mutually exclusive"
            )

        if credentials_file is not None:
            credentials, _ = google.auth.load_credentials_from_file(
                credentials_file, **scopes_kwargs, quota_project_id=quota_project_id
            )

        elif credentials is None:
            credentials, _ = google.auth.default(
                **scopes_kwargs, quota_project_id=quota_project_id
            )

        # Save the credentials.
        self._credentials = credentials

    # TODO(busunkim): These two class methods are in the base transport
    # to avoid duplicating code across the transport classes. These functions
    # should be deleted once the minimum required versions of google-api-core
    # and google-auth are increased.

    # TODO: Remove this function once google-auth >= 1.25.0 is required
    @classmethod
    def _get_scopes_kwargs(
        cls, host: str, scopes: Optional[Sequence[str]]
    ) -> Dict[str, Optional[Sequence[str]]]:
        """Returns scopes kwargs to pass to google-auth methods depending on the google-auth version"""

        scopes_kwargs = {}

        if _GOOGLE_AUTH_VERSION and (
            packaging.version.parse(_GOOGLE_AUTH_VERSION)
            >= packaging.version.parse("1.25.0")
        ):
            scopes_kwargs = {"scopes": scopes, "default_scopes": cls.AUTH_SCOPES}
        else:
            scopes_kwargs = {"scopes": scopes or cls.AUTH_SCOPES}

        return scopes_kwargs

    # TODO: Remove this function once google-api-core >= 1.26.0 is required
    @classmethod
    def _get_self_signed_jwt_kwargs(
        cls, host: str, scopes: Optional[Sequence[str]]
    ) -> Dict[str, Union[Optional[Sequence[str]], str]]:
        """Returns kwargs to pass to grpc_helpers.create_channel depending on the google-api-core version"""

        self_signed_jwt_kwargs: Dict[str, Union[Optional[Sequence[str]], str]] = {}

        if _API_CORE_VERSION and (
            packaging.version.parse(_API_CORE_VERSION)
            >= packaging.version.parse("1.26.0")
        ):
            self_signed_jwt_kwargs["default_scopes"] = cls.AUTH_SCOPES
            self_signed_jwt_kwargs["scopes"] = scopes
            self_signed_jwt_kwargs["default_host"] = cls.DEFAULT_HOST
        else:
            self_signed_jwt_kwargs["scopes"] = scopes or cls.AUTH_SCOPES

        return self_signed_jwt_kwargs

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_metadata_store: gapic_v1.method.wrap_method(
                self.create_metadata_store,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_metadata_store: gapic_v1.method.wrap_method(
                self.get_metadata_store, default_timeout=5.0, client_info=client_info,
            ),
            self.list_metadata_stores: gapic_v1.method.wrap_method(
                self.list_metadata_stores, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_metadata_store: gapic_v1.method.wrap_method(
                self.delete_metadata_store,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_artifact: gapic_v1.method.wrap_method(
                self.create_artifact, default_timeout=5.0, client_info=client_info,
            ),
            self.get_artifact: gapic_v1.method.wrap_method(
                self.get_artifact, default_timeout=5.0, client_info=client_info,
            ),
            self.list_artifacts: gapic_v1.method.wrap_method(
                self.list_artifacts, default_timeout=5.0, client_info=client_info,
            ),
            self.update_artifact: gapic_v1.method.wrap_method(
                self.update_artifact, default_timeout=5.0, client_info=client_info,
            ),
            self.create_context: gapic_v1.method.wrap_method(
                self.create_context, default_timeout=5.0, client_info=client_info,
            ),
            self.get_context: gapic_v1.method.wrap_method(
                self.get_context, default_timeout=5.0, client_info=client_info,
            ),
            self.list_contexts: gapic_v1.method.wrap_method(
                self.list_contexts, default_timeout=5.0, client_info=client_info,
            ),
            self.update_context: gapic_v1.method.wrap_method(
                self.update_context, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_context: gapic_v1.method.wrap_method(
                self.delete_context, default_timeout=5.0, client_info=client_info,
            ),
            self.add_context_artifacts_and_executions: gapic_v1.method.wrap_method(
                self.add_context_artifacts_and_executions,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.add_context_children: gapic_v1.method.wrap_method(
                self.add_context_children, default_timeout=5.0, client_info=client_info,
            ),
            self.query_context_lineage_subgraph: gapic_v1.method.wrap_method(
                self.query_context_lineage_subgraph,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_execution: gapic_v1.method.wrap_method(
                self.create_execution, default_timeout=5.0, client_info=client_info,
            ),
            self.get_execution: gapic_v1.method.wrap_method(
                self.get_execution, default_timeout=5.0, client_info=client_info,
            ),
            self.list_executions: gapic_v1.method.wrap_method(
                self.list_executions, default_timeout=5.0, client_info=client_info,
            ),
            self.update_execution: gapic_v1.method.wrap_method(
                self.update_execution, default_timeout=5.0, client_info=client_info,
            ),
            self.add_execution_events: gapic_v1.method.wrap_method(
                self.add_execution_events, default_timeout=5.0, client_info=client_info,
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
                self.get_metadata_schema, default_timeout=5.0, client_info=client_info,
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
    def create_metadata_store(
        self,
    ) -> Callable[
        [metadata_service.CreateMetadataStoreRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def get_metadata_store(
        self,
    ) -> Callable[
        [metadata_service.GetMetadataStoreRequest],
        Union[metadata_store.MetadataStore, Awaitable[metadata_store.MetadataStore]],
    ]:
        raise NotImplementedError()

    @property
    def list_metadata_stores(
        self,
    ) -> Callable[
        [metadata_service.ListMetadataStoresRequest],
        Union[
            metadata_service.ListMetadataStoresResponse,
            Awaitable[metadata_service.ListMetadataStoresResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def delete_metadata_store(
        self,
    ) -> Callable[
        [metadata_service.DeleteMetadataStoreRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_artifact(
        self,
    ) -> Callable[
        [metadata_service.CreateArtifactRequest],
        Union[gca_artifact.Artifact, Awaitable[gca_artifact.Artifact]],
    ]:
        raise NotImplementedError()

    @property
    def get_artifact(
        self,
    ) -> Callable[
        [metadata_service.GetArtifactRequest],
        Union[artifact.Artifact, Awaitable[artifact.Artifact]],
    ]:
        raise NotImplementedError()

    @property
    def list_artifacts(
        self,
    ) -> Callable[
        [metadata_service.ListArtifactsRequest],
        Union[
            metadata_service.ListArtifactsResponse,
            Awaitable[metadata_service.ListArtifactsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_artifact(
        self,
    ) -> Callable[
        [metadata_service.UpdateArtifactRequest],
        Union[gca_artifact.Artifact, Awaitable[gca_artifact.Artifact]],
    ]:
        raise NotImplementedError()

    @property
    def create_context(
        self,
    ) -> Callable[
        [metadata_service.CreateContextRequest],
        Union[gca_context.Context, Awaitable[gca_context.Context]],
    ]:
        raise NotImplementedError()

    @property
    def get_context(
        self,
    ) -> Callable[
        [metadata_service.GetContextRequest],
        Union[context.Context, Awaitable[context.Context]],
    ]:
        raise NotImplementedError()

    @property
    def list_contexts(
        self,
    ) -> Callable[
        [metadata_service.ListContextsRequest],
        Union[
            metadata_service.ListContextsResponse,
            Awaitable[metadata_service.ListContextsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_context(
        self,
    ) -> Callable[
        [metadata_service.UpdateContextRequest],
        Union[gca_context.Context, Awaitable[gca_context.Context]],
    ]:
        raise NotImplementedError()

    @property
    def delete_context(
        self,
    ) -> Callable[
        [metadata_service.DeleteContextRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def add_context_artifacts_and_executions(
        self,
    ) -> Callable[
        [metadata_service.AddContextArtifactsAndExecutionsRequest],
        Union[
            metadata_service.AddContextArtifactsAndExecutionsResponse,
            Awaitable[metadata_service.AddContextArtifactsAndExecutionsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def add_context_children(
        self,
    ) -> Callable[
        [metadata_service.AddContextChildrenRequest],
        Union[
            metadata_service.AddContextChildrenResponse,
            Awaitable[metadata_service.AddContextChildrenResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def query_context_lineage_subgraph(
        self,
    ) -> Callable[
        [metadata_service.QueryContextLineageSubgraphRequest],
        Union[
            lineage_subgraph.LineageSubgraph,
            Awaitable[lineage_subgraph.LineageSubgraph],
        ],
    ]:
        raise NotImplementedError()

    @property
    def create_execution(
        self,
    ) -> Callable[
        [metadata_service.CreateExecutionRequest],
        Union[gca_execution.Execution, Awaitable[gca_execution.Execution]],
    ]:
        raise NotImplementedError()

    @property
    def get_execution(
        self,
    ) -> Callable[
        [metadata_service.GetExecutionRequest],
        Union[execution.Execution, Awaitable[execution.Execution]],
    ]:
        raise NotImplementedError()

    @property
    def list_executions(
        self,
    ) -> Callable[
        [metadata_service.ListExecutionsRequest],
        Union[
            metadata_service.ListExecutionsResponse,
            Awaitable[metadata_service.ListExecutionsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_execution(
        self,
    ) -> Callable[
        [metadata_service.UpdateExecutionRequest],
        Union[gca_execution.Execution, Awaitable[gca_execution.Execution]],
    ]:
        raise NotImplementedError()

    @property
    def add_execution_events(
        self,
    ) -> Callable[
        [metadata_service.AddExecutionEventsRequest],
        Union[
            metadata_service.AddExecutionEventsResponse,
            Awaitable[metadata_service.AddExecutionEventsResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def query_execution_inputs_and_outputs(
        self,
    ) -> Callable[
        [metadata_service.QueryExecutionInputsAndOutputsRequest],
        Union[
            lineage_subgraph.LineageSubgraph,
            Awaitable[lineage_subgraph.LineageSubgraph],
        ],
    ]:
        raise NotImplementedError()

    @property
    def create_metadata_schema(
        self,
    ) -> Callable[
        [metadata_service.CreateMetadataSchemaRequest],
        Union[
            gca_metadata_schema.MetadataSchema,
            Awaitable[gca_metadata_schema.MetadataSchema],
        ],
    ]:
        raise NotImplementedError()

    @property
    def get_metadata_schema(
        self,
    ) -> Callable[
        [metadata_service.GetMetadataSchemaRequest],
        Union[
            metadata_schema.MetadataSchema, Awaitable[metadata_schema.MetadataSchema]
        ],
    ]:
        raise NotImplementedError()

    @property
    def list_metadata_schemas(
        self,
    ) -> Callable[
        [metadata_service.ListMetadataSchemasRequest],
        Union[
            metadata_service.ListMetadataSchemasResponse,
            Awaitable[metadata_service.ListMetadataSchemasResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def query_artifact_lineage_subgraph(
        self,
    ) -> Callable[
        [metadata_service.QueryArtifactLineageSubgraphRequest],
        Union[
            lineage_subgraph.LineageSubgraph,
            Awaitable[lineage_subgraph.LineageSubgraph],
        ],
    ]:
        raise NotImplementedError()


__all__ = ("MetadataServiceTransport",)
