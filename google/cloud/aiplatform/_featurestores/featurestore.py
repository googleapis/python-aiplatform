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
from google.cloud.aiplatform import _featurestores
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

    def get_entity_type(self, entity_type_id: str) -> "_featurestores.EntityType":
        """Retrieves an existing managed entityType in this Featurestore.

        Args:
            entity_type_id (str):
                Required. The managed entityType resource ID in this Featurestore.
        Returns:
            featurestores.EntityType - The managed entityType resource object.
        """
        featurestore_name_components = featurestore_utils.CompatFeaturestoreServiceClient.parse_featurestore_path(
            path=self.resource_name
        )

        return _featurestores.EntityType(
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
    ) -> List["_featurestores.EntityType"]:
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
            List[EntityTypes] - A list of managed entityType resource objects.
        """
        return _featurestores.EntityType.list(
            featurestore_name=self.resource_name, filter=filter, order_by=order_by,
        )

    @base.optional_sync()
    def delete_entity_types(
        self, entity_type_ids: List[str], sync: Optional[bool] = True,
    ) -> None:
        """Deletes entity_type resources in this Featurestre given their entity_type IDs.
        WARNING: This deletion is permanent.

        Args:
            entity_type_ids (List[str]):
                Required. The list of entity_type IDs to be deleted.
            sync (bool):
                Optional. Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        for entity_type_id in entity_type_ids:
            entity_type = self.get_entity_type(entity_type_id=entity_type_id)
            entity_type.delete(sync=sync)

        if not sync:
            entity_type.wait()
