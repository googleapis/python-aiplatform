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

from google.cloud.aiplatform_v1beta1.types import entity_type
from google.cloud.aiplatform_v1beta1.types import entity_type as gca_entity_type
from google.cloud.aiplatform_v1beta1.types import feature
from google.cloud.aiplatform_v1beta1.types import feature as gca_feature
from google.cloud.aiplatform_v1beta1.types import featurestore
from google.cloud.aiplatform_v1beta1.types import featurestore_service
from google.longrunning import operations_pb2 as operations  # type: ignore


try:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo(
        gapic_version=pkg_resources.get_distribution(
            'google-cloud-aiplatform',
        ).version,
    )
except pkg_resources.DistributionNotFound:
    DEFAULT_CLIENT_INFO = gapic_v1.client_info.ClientInfo()

class FeaturestoreServiceTransport(abc.ABC):
    """Abstract transport class for FeaturestoreService."""

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
            self.create_featurestore: gapic_v1.method.wrap_method(
                self.create_featurestore,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_featurestore: gapic_v1.method.wrap_method(
                self.get_featurestore,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_featurestores: gapic_v1.method.wrap_method(
                self.list_featurestores,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.update_featurestore: gapic_v1.method.wrap_method(
                self.update_featurestore,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.delete_featurestore: gapic_v1.method.wrap_method(
                self.delete_featurestore,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_entity_type: gapic_v1.method.wrap_method(
                self.create_entity_type,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_entity_type: gapic_v1.method.wrap_method(
                self.get_entity_type,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_entity_types: gapic_v1.method.wrap_method(
                self.list_entity_types,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.update_entity_type: gapic_v1.method.wrap_method(
                self.update_entity_type,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.delete_entity_type: gapic_v1.method.wrap_method(
                self.delete_entity_type,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.create_feature: gapic_v1.method.wrap_method(
                self.create_feature,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.batch_create_features: gapic_v1.method.wrap_method(
                self.batch_create_features,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.get_feature: gapic_v1.method.wrap_method(
                self.get_feature,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.list_features: gapic_v1.method.wrap_method(
                self.list_features,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.update_feature: gapic_v1.method.wrap_method(
                self.update_feature,
                default_timeout=5.0,
                client_info=client_info,
            ),
            self.delete_feature: gapic_v1.method.wrap_method(
                self.delete_feature,
                default_timeout=5.0,
                client_info=client_info,
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
                self.search_features,
                default_timeout=5.0,
                client_info=client_info,
            ),

        }

    @property
    def operations_client(self) -> operations_v1.OperationsClient:
        """Return the client designed to process long-running operations."""
        raise NotImplementedError()

    @property
    def create_featurestore(self) -> typing.Callable[
            [featurestore_service.CreateFeaturestoreRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def get_featurestore(self) -> typing.Callable[
            [featurestore_service.GetFeaturestoreRequest],
            typing.Union[
                featurestore.Featurestore,
                typing.Awaitable[featurestore.Featurestore]
            ]]:
        raise NotImplementedError()

    @property
    def list_featurestores(self) -> typing.Callable[
            [featurestore_service.ListFeaturestoresRequest],
            typing.Union[
                featurestore_service.ListFeaturestoresResponse,
                typing.Awaitable[featurestore_service.ListFeaturestoresResponse]
            ]]:
        raise NotImplementedError()

    @property
    def update_featurestore(self) -> typing.Callable[
            [featurestore_service.UpdateFeaturestoreRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def delete_featurestore(self) -> typing.Callable[
            [featurestore_service.DeleteFeaturestoreRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_entity_type(self) -> typing.Callable[
            [featurestore_service.CreateEntityTypeRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def get_entity_type(self) -> typing.Callable[
            [featurestore_service.GetEntityTypeRequest],
            typing.Union[
                entity_type.EntityType,
                typing.Awaitable[entity_type.EntityType]
            ]]:
        raise NotImplementedError()

    @property
    def list_entity_types(self) -> typing.Callable[
            [featurestore_service.ListEntityTypesRequest],
            typing.Union[
                featurestore_service.ListEntityTypesResponse,
                typing.Awaitable[featurestore_service.ListEntityTypesResponse]
            ]]:
        raise NotImplementedError()

    @property
    def update_entity_type(self) -> typing.Callable[
            [featurestore_service.UpdateEntityTypeRequest],
            typing.Union[
                gca_entity_type.EntityType,
                typing.Awaitable[gca_entity_type.EntityType]
            ]]:
        raise NotImplementedError()

    @property
    def delete_entity_type(self) -> typing.Callable[
            [featurestore_service.DeleteEntityTypeRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def create_feature(self) -> typing.Callable[
            [featurestore_service.CreateFeatureRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def batch_create_features(self) -> typing.Callable[
            [featurestore_service.BatchCreateFeaturesRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def get_feature(self) -> typing.Callable[
            [featurestore_service.GetFeatureRequest],
            typing.Union[
                feature.Feature,
                typing.Awaitable[feature.Feature]
            ]]:
        raise NotImplementedError()

    @property
    def list_features(self) -> typing.Callable[
            [featurestore_service.ListFeaturesRequest],
            typing.Union[
                featurestore_service.ListFeaturesResponse,
                typing.Awaitable[featurestore_service.ListFeaturesResponse]
            ]]:
        raise NotImplementedError()

    @property
    def update_feature(self) -> typing.Callable[
            [featurestore_service.UpdateFeatureRequest],
            typing.Union[
                gca_feature.Feature,
                typing.Awaitable[gca_feature.Feature]
            ]]:
        raise NotImplementedError()

    @property
    def delete_feature(self) -> typing.Callable[
            [featurestore_service.DeleteFeatureRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def import_feature_values(self) -> typing.Callable[
            [featurestore_service.ImportFeatureValuesRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def batch_read_feature_values(self) -> typing.Callable[
            [featurestore_service.BatchReadFeatureValuesRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def export_feature_values(self) -> typing.Callable[
            [featurestore_service.ExportFeatureValuesRequest],
            typing.Union[
                operations.Operation,
                typing.Awaitable[operations.Operation]
            ]]:
        raise NotImplementedError()

    @property
    def search_features(self) -> typing.Callable[
            [featurestore_service.SearchFeaturesRequest],
            typing.Union[
                featurestore_service.SearchFeaturesResponse,
                typing.Awaitable[featurestore_service.SearchFeaturesResponse]
            ]]:
        raise NotImplementedError()


__all__ = (
    'FeaturestoreServiceTransport',
)
