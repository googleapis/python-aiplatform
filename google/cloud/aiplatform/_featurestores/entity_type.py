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
from google.cloud.aiplatform.compat.types import entity_type as gca_entity_type
from google.cloud.aiplatform import _featurestores
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import featurestore_utils

_LOGGER = base.Logger(__name__)
_ALL_FEATURE_IDS = "*"


class EntityType(base.VertexAiResourceNounWithFutureManager):
    """Managed entityType resource for Vertex AI."""

    client_class = utils.FeaturestoreClientWithOverride

    _is_client_prediction_client = False
    _resource_noun = None
    _getter_method = "get_entity_type"
    _list_method = "list_entity_types"
    _delete_method = "delete_entity_type"

    def __init__(
        self,
        entity_type_name: str,
        featurestore_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed entityType given an entityType resource name or an entity_type ID.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='projects/123/locations/us-central1/featurestores/my_featurestore_id/\
                entityTypes/my_entity_type_id'
            )
            or
            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )

        Args:
            entity_type_name (str):
                Required. A fully-qualified entityType resource name or an entity_type ID.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id/entityTypes/my_entity_type_id"
                or "my_entity_type_id" when project and location are initialized or passed, with featurestore_id passed.
            featurestore_id (str):
                Optional. Featurestore ID to retrieve entityType from, when entity_type_name is passed as entity_type ID.
            project (str):
                Optional. Project to retrieve entityType from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve entityType from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this EntityType. Overrides
                credentials set in aiplatform.init.
        """

        (
            featurestore_id,
            _,
        ) = featurestore_utils.validate_and_get_entity_type_resource_ids(
            entity_type_name=entity_type_name, featurestore_id=featurestore_id
        )

        # TODO(b/208269923): Temporary workaround, update when base class supports nested resource
        self._resource_noun = f"featurestores/{featurestore_id}/entityTypes"

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=entity_type_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=entity_type_name)

    @property
    def featurestore_name(self) -> str:
        """Full qualified resource name of the managed featurestore in which this EntityType is."""
        entity_type_name_components = featurestore_utils.CompatFeaturestoreServiceClient.parse_entity_type_path(
            path=self.resource_name
        )
        return featurestore_utils.CompatFeaturestoreServiceClient.featurestore_path(
            project=entity_type_name_components["project"],
            location=entity_type_name_components["location"],
            featurestore=entity_type_name_components["featurestore"],
        )

    def get_featurestore(self) -> _featurestores.Featurestore:
        """Retrieves the managed featurestore in which this EntityType is.

        Returns:
            featurestores.Featurestore - The managed featurestore in which this EntityType is.
        """
        return _featurestores.Featurestore(self.featurestore_name)

    def get_feature(self, feature_id: str) -> "_featurestores.Feature":
        """Retrieves an existing managed feature in this EntityType.

        Args:
            feature_id (str):
                Required. The managed feature resource ID in this EntityType.
        Returns:
            featurestores.Feature - The managed feature resource object.
        """
        entity_type_name_components = featurestore_utils.CompatFeaturestoreServiceClient.parse_entity_type_path(
            path=self.resource_name
        )

        return _featurestores.Feature(
            feature_name=featurestore_utils.CompatFeaturestoreServiceClient.feature_path(
                project=entity_type_name_components["project"],
                location=entity_type_name_components["location"],
                featurestore=entity_type_name_components["featurestore"],
                entity_type=entity_type_name_components["entity_type"],
                feature=feature_id,
            )
        )

    def update(
        self,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "EntityType":
        """Updates an existing managed entityType resource.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_entity_type.update(
                description='update my description',
            )

        Args:
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
                labels can be associated with one Feature
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        Returns:
            EntityType - The updated entityType resource object.
        """
        update_mask = list()

        if description:
            update_mask.append("description")

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_entity_type = gca_entity_type.EntityType(
            name=self.resource_name, description=description, labels=labels,
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "entityType", self,
        )

        update_entity_type_lro = self.api_client.update_entity_type(
            entity_type=gapic_entity_type,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "entityType", self.__class__, update_entity_type_lro
        )

        update_entity_type_lro.result()

        _LOGGER.log_action_completed_against_resource("entityType", "updated", self)

        return self

    @classmethod
    def list(
        cls,
        featurestore_name: str,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["EntityType"]:
        """Lists existing managed entityType resources in a featurestore, given a featurestore resource name or a featurestore ID.

        Example Usage:

            my_entityTypes = aiplatform.EntityType.list(
                featurestore_name='projects/123/locations/us-central1/featurestores/my_featurestore_id'
            )
            or
            my_entityTypes = aiplatform.EntityType.list(
                featurestore_name='my_featurestore_id'
            )

        Args:
            featurestore_name (str):
                Required. A fully-qualified featurestore resource name or a featurestore ID to list entityTypes in
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id"
                or "my_featurestore_id" when project and location are initialized or passed.
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
            project (str):
                Optional. Project to list entityTypes in. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to list entityTypes in. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to list entityTypes. Overrides
                credentials set in aiplatform.init.

        Returns:
            List[EntityTypes] - A list of managed entityType resource objects
        """

        return cls._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
            parent=utils.full_resource_name(
                resource_name=featurestore_name,
                resource_noun="featurestores",
                project=project,
                location=location,
            ),
        )

    def list_features(
        self, filter: Optional[str] = None, order_by: Optional[str] = None,
    ) -> List["_featurestores.Feature"]:
        """Lists existing managed feature resources in this EntityType.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_entityType.list_features()

        Args:
            filter (str):
                Optional. Lists the Features that match the filter expression. The
                following filters are supported:

                -  ``value_type``: Supports = and != comparisons.
                -  ``create_time``: Supports =, !=, <, >, >=, and <=
                   comparisons. Values must be in RFC 3339 format.
                -  ``update_time``: Supports =, !=, <, >, >=, and <=
                   comparisons. Values must be in RFC 3339 format.
                -  ``labels``: Supports key-value equality as well as key
                   presence.

                Examples:

                -  ``value_type = DOUBLE`` --> Features whose type is
                   DOUBLE.
                -  ``create_time > \"2020-01-31T15:30:00.000000Z\" OR update_time > \"2020-01-31T15:30:00.000000Z\"``
                   --> EntityTypes created or updated after
                   2020-01-31T15:30:00.000000Z.
                -  ``labels.active = yes AND labels.env = prod`` -->
                   Features having both (active: yes) and (env: prod)
                   labels.
                -  ``labels.env: *`` --> Any Feature which has a label with
                   'env' as the key.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for
                descending. Supported fields:

                -  ``feature_id``
                -  ``value_type``
                -  ``create_time``
                -  ``update_time``

        Returns:
            List[Features] - A list of managed feature resource objects.
        """
        return _featurestores.Feature.list(
            entity_type_name=self.resource_name, filter=filter, order_by=order_by,
        )

    @base.optional_sync()
    def delete_features(
        self, feature_ids: List[str], sync: Optional[bool] = True,
    ) -> None:
        """Deletes feature resources in this EntityType given their feature IDs.
        WARNING: This deletion is permanent.

        Args:
            feature_ids (List[str]):
                Required. The list of feature IDs to be deleted.
            sync (bool):
                Optional. Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        for feature_id in feature_ids:
            feature = self.get_feature(feature_id=feature_id)
            feature.delete(sync=sync)

        if not sync:
            feature.wait()

    @classmethod
    @base.optional_sync()
    def create(
        cls,
        entity_type_id: str,
        featurestore_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: Optional[bool] = True,
    ) -> "EntityType":
        """Creates a new EntityType resources in a Featurestore.

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
            entity_type_id (str):
                Required. The ID to use for the EntityType, which will
                become the final component of the EntityType's resource
                name.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within a featurestore.
            featurestore_name (str):
                Required. A fully-qualified featurestore resource name or a featurestore ID to create EntityType in.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id"
                or "my_featurestore_id" when project and location are initialized or passed.
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
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            EntityType - EntityType resource objects

        """
        featurestore_id = featurestore_utils.validate_and_get_featurestore_resource_id(
            featurestore_name=featurestore_name,
        )

        if labels:
            utils.validate_labels(labels)

        cls._resource_noun = featurestore_utils.get_entity_type_resource_noun(
            featurestore_id=featurestore_id
        )

        featurestore_name = utils.full_resource_name(
            resource_name=featurestore_id,
            resource_noun=featurestore_utils.FEATURESTORE_RESOURCE_NOUN,
            project=project,
            location=location,
        )

        gapic_entity_type = gca_entity_type.EntityType(
            description=description, labels=labels,
        )

        create_entity_type_request = {
            "parent": featurestore_name,
            "entity_type": gapic_entity_type,
            "entity_type_id": entity_type_id,
        }

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        created_entity_type_lro = api_client.create_entity_type(
            request=create_entity_type_request, metadata=request_metadata
        )

        _LOGGER.log_create_with_lro(cls, created_entity_type_lro)

        created_entity_type = created_entity_type_lro.result()

        _LOGGER.log_create_complete(cls, created_entity_type, "entity_type")

        entity_type_obj = cls(
            entity_type_name=created_entity_type.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        return entity_type_obj

    def create_feature(
        self,
        feature_id: str,
        value_type: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: Optional[bool] = True,
    ) -> "_featurestores.Feature":
        """Creates a new Feature resources in an EntityType.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_feature = my_entity_type.create_feature(
                feature_id='my_feature_id',
                value_type='INT64',
            )

        Args:
            feature_id (str):
                Required. The ID to use for the Feature, which will become
                the final component of the Feature's resource name, which is immutable.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within an EntityType.
            value_type (str):
                Required. Immutable. Type of Feature value.
                One of BOOL, BOOL_ARRAY, DOUBLE, DOUBLE_ARRAY, INT64, INT64_ARRAY, STRING, STRING_ARRAY, BYTES.
            description (str):
                Optional. Description of the Feature.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Features.
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
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            featurestores.Feature - feature resource objects

        """
        return _featurestores.Feature.create(
            feature_id=feature_id,
            value_type=value_type,
            entity_type_name=self.resource_name,
            description=description,
            labels=labels,
            request_metadata=request_metadata,
            sync=sync,
        )
