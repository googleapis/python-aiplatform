# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

from typing import Dict, List, Optional, Sequence, Tuple

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import featurestore as gca_featurestore
from google.cloud.aiplatform import featurestore
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import featurestore_utils

_LOGGER = base.Logger(__name__)


class Featurestore(base.VertexAiResourceNounWithFutureManager):
    """Managed featurestore resource for Vertex AI."""

    client_class = utils.FeaturestoreClientWithOverride

    _is_client_prediction_client = False
    _resource_noun = "featurestores"
    _getter_method = "get_featurestore"
    _list_method = "list_featurestores"
    _delete_method = "delete_featurestore"

    def __init__(
        self,
        featurestore_name: str,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed featurestore given a featurestore resource name or a featurestore ID.

        Example Usage:

            my_featurestore = aiplatform.Featurestore(
                featurestore_name='projects/123/locations/us-central1/featurestores/my_featurestore_id'
            )
            or
            my_featurestore = aiplatform.Featurestore(
                featurestore_name='my_featurestore_id'
            )

        Args:
            featurestore_name (str):
                Required. A fully-qualified featurestore resource name or a featurestore ID.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id"
                or "my_featurestore_id" when project and location are initialized or passed.
            project (str):
                Optional. Project to retrieve featurestore from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve featurestore from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Featurestore. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=featurestore_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=featurestore_name)

    def get_entity_type(self, entity_type_id: str) -> "featurestore.EntityType":
        """Retrieves an existing managed entityType in this Featurestore.

        Args:
            entity_type_id (str):
                Required. The managed entityType resource ID in this Featurestore.
        Returns:
            featurestore.EntityType - The managed entityType resource object.
        """
        featurestore_name_components = featurestore_utils.CompatFeaturestoreServiceClient.parse_featurestore_path(
            path=self.resource_name
        )

        return featurestore.EntityType(
            entity_type_name=featurestore_utils.CompatFeaturestoreServiceClient.entity_type_path(
                project=featurestore_name_components["project"],
                location=featurestore_name_components["location"],
                featurestore=featurestore_name_components["featurestore"],
                entity_type=entity_type_id,
            )
        )

    def update(
        self,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "Featurestore":
        """Updates an existing managed featurestore resource.

        Example Usage:

            my_featurestore = aiplatform.Featurestore(
                featurestore_name='my_featurestore_id',
            )
            my_featurestore.update(
                labels={'update my key': 'update my value'},
            )

        Args:
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Featurestores.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one Feature
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            Featurestore - The updated featurestore resource object.
        """

        return self._update(labels=labels, request_metadata=request_metadata)

    # TODO(b/206818784): Add enable_online_store and disable_online_store methods
    def update_online_store(
        self,
        fixed_node_count: int,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "Featurestore":
        """Updates the online store of an existing managed featurestore resource.

        Example Usage:

            my_featurestore = aiplatform.Featurestore(
                featurestore_name='my_featurestore_id',
            )
            my_featurestore.update_online_store(
                fixed_node_count=2,
            )

        Args:
            fixed_node_count (int):
                Required. Config for online serving resources, can only update the node count to >= 1.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            Featurestore - The updated featurestore resource object.
        """
        return self._update(
            fixed_node_count=fixed_node_count, request_metadata=request_metadata
        )

    def _update(
        self,
        labels: Optional[Dict[str, str]] = None,
        fixed_node_count: Optional[int] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "Featurestore":
        """Updates an existing managed featurestore resource.

        Args:
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Featurestores.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one Feature
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            fixed_node_count (int):
                Optional. Config for online serving resources, can only update the node count to >= 1.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            Featurestore - The updated featurestore resource object.
        """
        update_mask = list()

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        if fixed_node_count is not None:
            update_mask.append("online_serving_config.fixed_node_count")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_featurestore = gca_featurestore.Featurestore(
            name=self.resource_name,
            labels=labels,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=fixed_node_count
            ),
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "featurestore", self,
        )

        update_featurestore_lro = self.api_client.update_featurestore(
            featurestore=gapic_featurestore,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "featurestore", self.__class__, update_featurestore_lro
        )

        update_featurestore_lro.result()

        _LOGGER.log_action_completed_against_resource("featurestore", "updated", self)

        return self

    def list_entity_types(
        self, filter: Optional[str] = None, order_by: Optional[str] = None,
    ) -> List["featurestore.EntityType"]:
        """Lists existing managed entityType resources in this Featurestore.

        Example Usage:

            my_featurestore = aiplatform.Featurestore(
                featurestore_name='my_featurestore_id',
            )
            my_featurestore.list_entity_types()

        Args:
            filter (str):
                Optional. Lists the EntityTypes that match the filter expression. The
                following filters are supported:

                -  ``create_time``: Supports ``=``, ``!=``, ``<``, ``>``,
                   ``>=``, and ``<=`` comparisons. Values must be in RFC
                   3339 format.
                -  ``update_time``: Supports ``=``, ``!=``, ``<``, ``>``,
                   ``>=``, and ``<=`` comparisons. Values must be in RFC
                   3339 format.
                -  ``labels``: Supports key-value equality as well as key
                   presence.

                Examples:

                -  ``create_time > \"2020-01-31T15:30:00.000000Z\" OR update_time > \"2020-01-31T15:30:00.000000Z\"``
                   --> EntityTypes created or updated after
                   2020-01-31T15:30:00.000000Z.
                -  ``labels.active = yes AND labels.env = prod`` -->
                   EntityTypes having both (active: yes) and (env: prod)
                   labels.
                -  ``labels.env: *`` --> Any EntityType which has a label
                   with 'env' as the key.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for
                descending.

                Supported fields:

                -  ``entity_type_id``
                -  ``create_time``
                -  ``update_time``

        Returns:
            List[featurestore.EntityType] - A list of managed entityType resource objects.
        """
        return featurestore.EntityType.list(
            featurestore_name=self.resource_name, filter=filter, order_by=order_by,
        )

    @base.optional_sync()
    def delete_entity_types(
        self, entity_type_ids: List[str], sync: bool = True, force: bool = False,
    ) -> None:
        """Deletes entity_type resources in this Featurestore given their entity_type IDs.
        WARNING: This deletion is permanent.

        Args:
            entity_type_ids (List[str]):
                Required. The list of entity_type IDs to be deleted.
            sync (bool):
                Optional. Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
            force (bool):
                Optional. If force is set to True, all features in each entityType
                will be deleted prior to entityType deletion. Default is False.
        """
        entity_types = []
        for entity_type_id in entity_type_ids:
            entity_type = self.get_entity_type(entity_type_id=entity_type_id)
            entity_type.delete(force=force, sync=False)
            entity_types.append(entity_type)

        for entity_type in entity_types:
            entity_type.wait()

    @base.optional_sync()
    def delete(self, sync: bool = True, force: bool = False) -> None:
        """Deletes this Featurestore resource. If force is set to True,
        all entityTypes in this Featurestore will be deleted prior to featurestore deletion,
        and all features in each entityType will be deleted prior to each entityType deletion.

        WARNING: This deletion is permanent.

        Args:
            force (bool):
                If set to true, any EntityTypes and
                Features for this Featurestore will also
                be deleted. (Otherwise, the request will
                only work if the Featurestore has no
                EntityTypes.)
            sync (bool):
                Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        _LOGGER.log_action_start_against_resource("Deleting", "", self)
        lro = getattr(self.api_client, self._delete_method)(
            name=self.resource_name, force=force
        )
        _LOGGER.log_action_started_against_resource_with_lro(
            "Delete", "", self.__class__, lro
        )
        lro.result()
        _LOGGER.log_action_completed_against_resource("deleted.", "", self)

    @classmethod
    @base.optional_sync()
    def create(
        cls,
        featurestore_id: str,
        online_store_fixed_node_count: Optional[int] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        encryption_spec_key_name: Optional[str] = None,
        sync: bool = True,
    ) -> "Featurestore":
        """Creates a Featurestore resource.

        Example Usage:

            my_entity_type = aiplatform.EntityType.create(
                entity_type_id='my_entity_type_id',
                featurestore_name='projects/123/locations/us-central1/featurestores/my_featurestore_id'
            )
            or
            my_entity_type = aiplatform.EntityType.create(
                entity_type_id='my_entity_type_id',
                featurestore_name='my_featurestore_id',
            )

        Args:
            featurestore_id (str):
                Required. The ID to use for this Featurestore, which will
                become the final component of the Featurestore's resource
                name.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within the project and location.
            online_store_fixed_node_count (int):
                Optional. Config for online serving resources.
                When not specified, default node count is 1. The
                number of nodes will not scale automatically but
                can be scaled manually by providing different
                values when updating.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Featurestore.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one
                Featurestore(System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            project (str):
                Optional. Project to create EntityType in. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to create EntityType in. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create EntityTypes. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            encryption_spec (str):
                Optional. Customer-managed encryption key
                spec for data storage. If set, both of the
                online and offline data storage will be secured
                by this key.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            Featurestore - Featurestore resource object

        """
        gapic_featurestore = gca_featurestore.Featurestore(
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=online_store_fixed_node_count or 1
            )
        )

        if labels:
            utils.validate_labels(labels)
            gapic_featurestore.labels = labels

        if encryption_spec_key_name:
            gapic_featurestore.encryption_spec = initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            )

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        created_featurestore_lro = api_client.create_featurestore(
            parent=initializer.global_config.common_location_path(
                project=project, location=location
            ),
            featurestore=gapic_featurestore,
            featurestore_id=featurestore_id,
            metadata=request_metadata,
        )

        _LOGGER.log_create_with_lro(cls, created_featurestore_lro)

        created_featurestore = created_featurestore_lro.result()

        _LOGGER.log_create_complete(cls, created_featurestore, "featurestore")

        featurestore_obj = cls(
            featurestore_name=created_featurestore.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        return featurestore_obj

    def create_entity_type(
        self,
        entity_type_id: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "featurestore.EntityType":
        """Creates an EntityType resource in this Featurestore.

        Example Usage:

            my_featurestore = aiplatform.Featurestore.create(
                featurestore_id='my_featurestore_id'
            )
            my_entity_type = my_featurestore.create_entity_type(
                entity_type_id='my_entity_type_id',
            )

        Args:
            entity_type_id (str):
                Required. The ID to use for the EntityType, which will
                become the final component of the EntityType's resource
                name.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within a featurestore.
            description (str):
                Optional. Description of the EntityType.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your EntityTypes.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one EntityType
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            featurestore.EntityType - EntityType resource object

        """
        return featurestore.EntityType.create(
            entity_type_id=entity_type_id,
            featurestore_name=self.resource_name,
            description=description,
            labels=labels,
            request_metadata=request_metadata,
            sync=sync,
        )
