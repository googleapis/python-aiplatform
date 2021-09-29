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
from google.oauth2 import service_account  # type: ignore

from google.cloud.aiplatform_v1beta1.types import entity_type
from google.cloud.aiplatform_v1beta1.types import entity_type as gca_entity_type
from google.cloud.aiplatform_v1beta1.types import feature
from google.cloud.aiplatform_v1beta1.types import feature as gca_feature
from google.cloud.aiplatform_v1beta1.types import featurestore
from google.cloud.aiplatform_v1beta1.types import featurestore_service
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


class FeaturestoreServiceTransport(abc.ABC):
    """Abstract transport class for FeaturestoreService."""

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
        always_use_jwt_access: Optional[bool] = False,
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
            always_use_jwt_access (Optional[bool]): Whether self signed JWT should
                be used for service account credentials.
        """
        # Save the hostname. Default to port 443 (HTTPS) if none is specified.
        if ":" not in host:
            host += ":443"
        self._host = host

        scopes_kwargs = self._get_scopes_kwargs(self._host, scopes)

        # Save the scopes.
        self._scopes = scopes

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

        # If the credentials are service account credentials, then always try to use self signed JWT.
        if (
            always_use_jwt_access
            and isinstance(credentials, service_account.Credentials)
            and hasattr(service_account.Credentials, "with_always_use_jwt_access")
        ):
            credentials = credentials.with_always_use_jwt_access(True)

        # Save the credentials.
        self._credentials = credentials

    # TODO(busunkim): This method is in the base transport
    # to avoid duplicating code across the transport classes. These functions
    # should be deleted once the minimum required versions of google-auth is increased.

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

    def _prep_wrapped_messages(self, client_info):
        # Precompute the wrapped methods.
        self._wrapped_methods = {
            self.create_featurestore: gapic_v1.method.wrap_method(
                self.create_featurestore, default_timeout=5.0, client_info=client_info,
            ),
            self.get_featurestore: gapic_v1.method.wrap_method(
                self.get_featurestore, default_timeout=5.0, client_info=client_info,
            ),
            self.list_featurestores: gapic_v1.method.wrap_method(
                self.list_featurestores, default_timeout=5.0, client_info=client_info,
            ),
            self.update_featurestore: gapic_v1.method.wrap_method(
                self.update_featurestore, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_featurestore: gapic_v1.method.wrap_method(
                self.delete_featurestore, default_timeout=5.0, client_info=client_info,
            ),
            self.create_entity_type: gapic_v1.method.wrap_method(
                self.create_entity_type, default_timeout=5.0, client_info=client_info,
            ),
            self.get_entity_type: gapic_v1.method.wrap_method(
                self.get_entity_type, default_timeout=5.0, client_info=client_info,
            ),
            self.list_entity_types: gapic_v1.method.wrap_method(
                self.list_entity_types, default_timeout=5.0, client_info=client_info,
            ),
            self.update_entity_type: gapic_v1.method.wrap_method(
                self.update_entity_type, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_entity_type: gapic_v1.method.wrap_method(
                self.delete_entity_type, default_timeout=5.0, client_info=client_info,
            ),
            self.create_feature: gapic_v1.method.wrap_method(
                self.create_feature, default_timeout=5.0, client_info=client_info,
            ),
            self.batch_create_features: gapic_v1.method.wrap_method(
                self.batch_create_features,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_feature: gapic_v1.method.wrap_method(
                self.get_feature, default_timeout=5.0, client_info=client_info,
            ),
            self.list_features: gapic_v1.method.wrap_method(
                self.list_features, default_timeout=5.0, client_info=client_info,
            ),
            self.update_feature: gapic_v1.method.wrap_method(
                self.update_feature, default_timeout=5.0, client_info=client_info,
            ),
            self.delete_feature: gapic_v1.method.wrap_method(
                self.delete_feature, default_timeout=5.0, client_info=client_info,
            ),
            self.import_feature_values: gapic_v1.method.wrap_method(
                self.import_feature_values,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.batch_read_feature_values: gapic_v1.method.wrap_method(
                self.batch_read_feature_values,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.export_feature_values: gapic_v1.method.wrap_method(
                self.export_feature_values,
                default_timeout=None,
                client_info=client_info,
            ),
            self.search_features: gapic_v1.method.wrap_method(
                self.search_features, default_timeout=5.0, client_info=client_info,
            ),
        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_featurestore(
        self,
    ) -> Callable[
        [featurestore_service.CreateFeaturestoreRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def get_featurestore(
        self,
    ) -> Callable[
        [featurestore_service.GetFeaturestoreRequest],
        Union[featurestore.Featurestore, Awaitable[featurestore.Featurestore]],
    ]:
        raise NotImplementedError()

    @property
    def list_featurestores(
        self,
    ) -> Callable[
        [featurestore_service.ListFeaturestoresRequest],
        Union[
            featurestore_service.ListFeaturestoresResponse,
            Awaitable[featurestore_service.ListFeaturestoresResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_featurestore(
        self,
    ) -> Callable[
        [featurestore_service.UpdateFeaturestoreRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def delete_featurestore(
        self,
    ) -> Callable[
        [featurestore_service.DeleteFeaturestoreRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_entity_type(
        self,
    ) -> Callable[
        [featurestore_service.CreateEntityTypeRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def get_entity_type(
        self,
    ) -> Callable[
        [featurestore_service.GetEntityTypeRequest],
        Union[entity_type.EntityType, Awaitable[entity_type.EntityType]],
    ]:
        raise NotImplementedError()

    @property
    def list_entity_types(
        self,
    ) -> Callable[
        [featurestore_service.ListEntityTypesRequest],
        Union[
            featurestore_service.ListEntityTypesResponse,
            Awaitable[featurestore_service.ListEntityTypesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_entity_type(
        self,
    ) -> Callable[
        [featurestore_service.UpdateEntityTypeRequest],
        Union[gca_entity_type.EntityType, Awaitable[gca_entity_type.EntityType]],
    ]:
        raise NotImplementedError()

    @property
    def delete_entity_type(
        self,
    ) -> Callable[
        [featurestore_service.DeleteEntityTypeRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def create_feature(
        self,
    ) -> Callable[
        [featurestore_service.CreateFeatureRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def batch_create_features(
        self,
    ) -> Callable[
        [featurestore_service.BatchCreateFeaturesRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def get_feature(
        self,
    ) -> Callable[
        [featurestore_service.GetFeatureRequest],
        Union[feature.Feature, Awaitable[feature.Feature]],
    ]:
        raise NotImplementedError()

    @property
    def list_features(
        self,
    ) -> Callable[
        [featurestore_service.ListFeaturesRequest],
        Union[
            featurestore_service.ListFeaturesResponse,
            Awaitable[featurestore_service.ListFeaturesResponse],
        ],
    ]:
        raise NotImplementedError()

    @property
    def update_feature(
        self,
    ) -> Callable[
        [featurestore_service.UpdateFeatureRequest],
        Union[gca_feature.Feature, Awaitable[gca_feature.Feature]],
    ]:
        raise NotImplementedError()

    @property
    def delete_feature(
        self,
    ) -> Callable[
        [featurestore_service.DeleteFeatureRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def import_feature_values(
        self,
    ) -> Callable[
        [featurestore_service.ImportFeatureValuesRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def batch_read_feature_values(
        self,
    ) -> Callable[
        [featurestore_service.BatchReadFeatureValuesRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def export_feature_values(
        self,
    ) -> Callable[
        [featurestore_service.ExportFeatureValuesRequest],
        Union[operations_pb2.Operation, Awaitable[operations_pb2.Operation]],
    ]:
        raise NotImplementedError()

    @property
    def search_features(
        self,
    ) -> Callable[
        [featurestore_service.SearchFeaturesRequest],
        Union[
            featurestore_service.SearchFeaturesResponse,
            Awaitable[featurestore_service.SearchFeaturesResponse],
        ],
    ]:
        raise NotImplementedError()


__all__ = ("FeaturestoreServiceTransport",)
