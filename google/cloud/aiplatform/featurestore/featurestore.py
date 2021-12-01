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

from typing import Any, Dict, List, Optional, Set, Sequence, Tuple, Union

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import (
    feature_selector as gca_feature_selector,
    featurestore as gca_featurestore,
    featurestore_service as gca_featurestore_service,
    io as gca_io,
)
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
        self, entity_type_ids: List[str], force: bool = False, sync: bool = True,
    ) -> None:
        """Deletes entity_type resources in this Featurestore given their entity_type IDs.
        WARNING: This deletion is permanent.

        Args:
            entity_type_ids (List[str]):
                Required. The list of entity_type IDs to be deleted.
            force (bool):
                Optional. If force is set to True, all features in each entityType
                will be deleted prior to entityType deletion. Default is False.
            sync (bool):
                Optional. Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        entity_types = []
        for entity_type_id in entity_type_ids:
            entity_type = self.get_entity_type(entity_type_id=entity_type_id)
            entity_type.delete(force=force, sync=False)
            entity_types.append(entity_type)

        for entity_type in entity_types:
            entity_type.wait()

    @base.optional_sync()
    def delete(self, force: bool = False, sync: bool = True) -> None:
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
        Raises:
            FailedPrecondition: If entityTypes are created in this Featurestore and force = False.
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
        online_store_fixed_node_count: Optional[int] = 1,
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
                Required. Config for online serving resources.
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
        if labels:
            utils.validate_labels(labels)

        gapic_featurestore = gca_featurestore.Featurestore(
            labels=labels,
            online_serving_config=gca_featurestore.Featurestore.OnlineServingConfig(
                fixed_node_count=online_store_fixed_node_count
            ),
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
        )

        create_featurestore_request = {
            "parent": initializer.global_config.common_location_path(
                project=project, location=location
            ),
            "featurestore": gapic_featurestore,
            "featurestore_id": featurestore_id,
        }

        api_client = cls._instantiate_client(location=location, credentials=credentials)

        created_featurestore_lro = api_client.create_featurestore(
            request=create_featurestore_request, metadata=request_metadata
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

    @base.optional_sync(return_input_arg="self")
    def _batch_read_feature_values(
        self,
        batch_read_feature_values_request: Dict[str, Any],
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: Optional[bool] = True,
    ) -> "Featurestore":
        """Batch read Feature values from the Featurestore to a destination storage.

        Args:
            batch_read_feature_values_request (Dict[str, Any]):
                Required. Request of batch read feature values in dict.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this method synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            Featurestore - The featurestore resource object batch read feature values from.
        """

        _LOGGER.log_action_start_against_resource(
            "Serving", "feature values", self,
        )

        batch_read_lro = self.api_client.batch_read_feature_values(
            request=batch_read_feature_values_request, metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Serve", "feature values", self.__class__, batch_read_lro
        )

        batch_read_lro.result()

        _LOGGER.log_action_completed_against_resource("feature values", "served", self)

        return self

    def _validate_and_get_feature_id_and_destination_feature_setting(
        self,
        feature_destination_fields: Optional[
            Union[Dict[str, str], List[str], Set[str]]
        ],
    ) -> Tuple[List[str], List[gca_featurestore_service.DestinationFeatureSetting]]:
        """Validates and gets feature_ids and destination_feature_settings from feature_destination_fields config.

        Args:
            feature_destination_fields (Union[Dict[str, str], List[str], Set[str]]):
                Optional. User defined feature_destination_fields config.

        Returns:
            Tuple[List[str], List[gca_featurestore_service.DestinationFeatureSetting]] - A list of feature_id and a list of DestinationFeatureSetting list

        Raises:
            TypeError - if the feature_destination_fields is not a dict, list or set.
        """
        feature_ids = []
        destination_feature_settings = []

        if not feature_destination_fields:
            return feature_ids, destination_feature_settings

        if isinstance(feature_destination_fields, dict):
            for (
                feature_id,
                feature_detination_field,
            ) in feature_destination_fields.items():
                if feature_detination_field and isinstance(
                    feature_detination_field, str
                ):
                    destination_feature_setting = gca_featurestore_service.DestinationFeatureSetting(
                        feature_id=feature_id,
                        destination_field=feature_detination_field,
                    )
                    feature_ids.append(feature_id)
                    destination_feature_settings.append(destination_feature_setting)
                else:
                    raise TypeError(
                        f"The type of feature_detination_field should be set to str, instead got {type(feature_detination_field)}"
                    )

        elif isinstance(feature_destination_fields, set) or isinstance(
            feature_destination_fields, list
        ):
            for feature_id in set(feature_destination_fields):
                destination_feature_setting = gca_featurestore_service.DestinationFeatureSetting(
                    feature_id=feature_id
                )

                feature_ids.append(feature_id)
                destination_feature_settings.append(destination_feature_setting)

        else:
            raise TypeError(
                f"The type of feature_destination_fields should be dict, list or set, instead got {type(feature_destination_fields)}"
            )

        return feature_ids, destination_feature_settings

    def _validate_and_get_batch_read_feature_values_request(
        self,
        entity_type_ids: List[str],
        entity_type_destination_fields: Optional[
            Dict[str, Union[Dict[str, str], List[str], Set[str]]]
        ] = {},
        csv_read_instances: Optional[gca_io.CsvSource] = None,
        bigquery_read_instances: Optional[gca_io.BigQuerySource] = None,
        pass_through_fields: Optional[List[str]] = None,
        bigquery_destination: Optional[gca_io.BigQueryDestination] = None,
        csv_destination: Optional[gca_io.CsvDestination] = None,
        tfrecord_destination: Optional[gca_io.TFRecordDestination] = None,
    ) -> Dict[str, Any]:
        """Validates and gets batch_read_feature_values_request

        Args:
            entity_type_ids (List[str]):
                Required. ID of the EntityType to select batch serving Features. The
                EntityType id is the specified during EntityType creation.
            entity_type_destination_fields (Dict[str, Union[Dict[str, str], List[str], Set[str]]]):
                Optional. User defined dictionary to map ID of the EntityType's Features
                to the batch serving destination field name.

                Specify the features to be batch served in each entityType, and their destination field name.
                If the features are not specified, all features will be batch served.
                If the destination field name is not specified, Feature ID will be used as destination field name.

                Example:

                     - In case all features will be batch served and using Feature ID as destination field name:

                         entity_type_ids = ['my_entity_type_id_1', 'my_entity_type_id_2', 'my_entity_type_id_3']

                         entity_type_destination_fields = {}
                         or
                         entity_type_destination_fields = {
                            'my_entity_type_id_1': {},
                            'my_entity_type_id_2': [],
                            'my_entity_type_id_3': None,
                         }

                     - In case selected features will be batch served and using Feature ID as destination field name:

                         entity_type_ids = ['my_entity_type_id_1', 'my_entity_type_id_2', 'my_entity_type_id_3']

                         feature_source_fields = {
                            'my_entity_type_id_1': ['feature_id_1_1', 'feature_id_1_2'],
                            'my_entity_type_id_2': ['feature_id_2_1', 'feature_id_2_2'],
                            'my_entity_type_id_3': ['feature_id_3_1', 'feature_id_3_2'],
                         }

                     - In case selected features will be batch served with specified destination field name

                     feature_source_fields = {
                        'my_entity_type_id_1': {
                            'feature_id_1_1': 'feature_id_1_1_destination_field',
                            'feature_id_1_2': 'feature_id_1_2_destination_field',
                        },
                        'my_entity_type_id_2': {
                            'feature_id_2_1': 'feature_id_2_1_destination_field',
                            'feature_id_2_2': 'feature_id_2_2_destination_field',
                        },
                        'my_entity_type_id_3': {
                            'feature_id_3_1': 'feature_id_3_1_destination_field',
                            'feature_id_3_2': 'feature_id_3_2_destination_field',
                        },
                     }
                Note: the above three cases can be mixed in use.

            csv_read_instances (gca_io.CsvSource):
                Optional. Each read instance consists of exactly one read timestamp
                and one or more entity IDs identifying entities of the
                corresponding EntityTypes whose Features are requested.

                Each output instance contains Feature values of requested
                entities concatenated together as of the read time.

                An example read instance may be
                ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z``.

                An example output instance may be
                ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z, foo_entity_feature1_value, bar_entity_feature2_value``.

                Timestamp in each read instance must be millisecond-aligned.

                ``csv_read_instances`` are read instances stored in a
                plain-text CSV file. The header should be:
                [ENTITY_TYPE_ID1], [ENTITY_TYPE_ID2], ..., timestamp

                The columns can be in any order.

                Values in the timestamp column must use the RFC 3339 format,
                e.g. ``2012-07-30T10:43:17.123Z``.

                This field is a member of `oneof`_ ``read_option``.
            bigquery_read_instances (gca_io.BigQuerySource):
                Optional. Similar to csv_read_instances, but from BigQuery source.

                This field is a member of `oneof`_ ``read_option``.
            pass_through_fields (List[str]):
                Optional. When not empty, the specified fields in the
                read_instances source will be joined as-is in the output,
                in addition to those fields from the Featurestore Entity.

                For BigQuery source, the type of the pass-through values
                will be automatically inferred. For CSV source, the
                pass-through values will be passed as opaque bytes.
            bigquery_destination (gca_io.BigQueryDestination):
                Optional. Output in BigQuery format.
                [BigQueryDestination.output_uri][google.cloud.aiplatform.v1.BigQueryDestination.output_uri]
                in
                [FeatureValueDestination.bigquery_destination][google.cloud.aiplatform.v1.FeatureValueDestination.bigquery_destination]
                must refer to a table.

                This field is a member of `oneof`_ ``destination``.
            csv_destination (gca_io.CsvDestination):
                Optional. Output in CSV format. Array Feature value
                types are not allowed in CSV format.

                This field is a member of `oneof`_ ``destination``.
            tfrecord_destination (gca_io.TFRecordDestination):
                Output in TFRecord format.

                Below are the mapping from Feature value type in
                Featurestore to Feature value type in TFRecord:

                ::

                    Value type in Featurestore                 | Value type in TFRecord
                    DOUBLE, DOUBLE_ARRAY                       | FLOAT_LIST
                    INT64, INT64_ARRAY                         | INT64_LIST
                    STRING, STRING_ARRAY, BYTES                | BYTES_LIST
                    true -> byte_string("true"), false -> byte_string("false")
                    BOOL, BOOL_ARRAY (true, false)             | BYTES_LIST

                This field is a member of `oneof`_ ``destination``.

        Returns:
            Dict[str, Any] - batch read feature values request in dict

        Raises:
            ValueError - if no destination is set or more than one destinations are set.
            ValueError - if read_instances is not set in supported format or file type.
        """
        entity_type_specs = []

        for entity_type_id in set(entity_type_ids):
            feature_destination_fields = entity_type_destination_fields.get(
                entity_type_id, None
            )
            (
                feature_ids,
                destination_feature_settings,
            ) = self._validate_and_get_feature_id_and_destination_feature_setting(
                feature_destination_fields=feature_destination_fields
            )

            if feature_ids and destination_feature_settings:
                entity_type_spec = gca_featurestore_service.BatchReadFeatureValuesRequest.EntityTypeSpec(
                    entity_type_id=entity_type_id,
                    feature_selector=gca_feature_selector.FeatureSelector(
                        id_matcher=gca_feature_selector.IdMatcher(ids=feature_ids)
                    ),
                    settings=destination_feature_settings,
                )
            else:
                entity_type_spec = gca_featurestore_service.BatchReadFeatureValuesRequest.EntityTypeSpec(
                    entity_type_id=entity_type_id,
                    feature_selector=gca_feature_selector.FeatureSelector(
                        id_matcher=gca_feature_selector.IdMatcher(ids=["*"])
                    ),
                )

            entity_type_specs.append(entity_type_spec)

        # oneof destination
        if bigquery_destination and not csv_destination and not tfrecord_destination:
            destination = gca_featurestore_service.FeatureValueDestination(
                bigquery_destination=bigquery_destination
            )
        elif not bigquery_destination and csv_destination and not tfrecord_destination:
            destination = gca_featurestore_service.FeatureValueDestination(
                csv_destination=csv_destination
            )
        elif not bigquery_destination and not csv_destination and tfrecord_destination:
            destination = gca_featurestore_service.FeatureValueDestination(
                tfrecord_destination=tfrecord_destination
            )
        else:
            raise ValueError(
                "One and only one of `bigquery_destination`, `csv_destination`, and `tfrecord_destination` need to be passed. "
            )

        batch_read_feature_values_request = {
            "featurestore": self.resource_name,
            "destination": destination,
            "entity_type_specs": entity_type_specs,
        }

        # oneof read_instances
        if bigquery_read_instances and csv_read_instances:
            raise ValueError(
                "At most one of `bigquery_read_instances` and `csv_read_instances` can be set, not both."
            )
        elif bigquery_read_instances and not csv_read_instances:
            batch_read_feature_values_request[
                "bigquery_read_instances"
            ] = bigquery_read_instances
        elif not bigquery_read_instances and csv_read_instances:
            batch_read_feature_values_request["csv_read_instances"] = csv_read_instances

        if pass_through_fields is not None:
            batch_read_feature_values_request["pass_through_fields"] = [
                gca_featurestore_service.BatchReadFeatureValuesRequest.PassThroughField(
                    field_name=pass_through_field
                )
                for pass_through_field in pass_through_fields
            ]

        return batch_read_feature_values_request

    def _get_read_instances(
        self, read_instances: Optional[Union[str, List[str]]] = None,
    ) -> Tuple[Optional[gca_io.BigQuerySource], Optional[gca_io.CsvSource]]:
        """Gets bigquery_read_instances or csv_read_instances

        Args:
            read_instances (Union[str, List[str]]):
                Optional. Read_instances can be either BigQuery URI to the input table,
                or Google Cloud Storage URI(-s) to the
                csv file(s).

        Returns:
            Tuple[Optional[gca_io.BigQuerySource], Optional[gca_io.CsvSource]] - bigquery read instances or csv read instances.
        """

        bigquery_read_instances, csv_read_instances = None, None

        if not read_instances:
            return bigquery_read_instances, csv_read_instances

        if isinstance(read_instances, str) and read_instances.startswith("bq://"):
            bigquery_read_instances = gca_io.BigQuerySource(input_uri=read_instances)
            return bigquery_read_instances, csv_read_instances

        if isinstance(read_instances, str):
            read_instances = [read_instances]
        if isinstance(read_instances, list):
            csv_read_instances = gca_io.CsvSource(
                gcs_source=gca_io.GcsSource(uris=read_instances)
            )
            return bigquery_read_instances, csv_read_instances

    def batch_serve_to_bq(
        self,
        bq_destination_output_uri: str,
        entity_type_ids: List[str],
        entity_type_destination_fields: Optional[
            Dict[str, Union[Dict[str, str], List[str], Set[str]]]
        ] = {},
        read_instances: Optional[Union[str, List[str]]] = None,
        pass_through_fields: Optional[List[str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "Featurestore":
        """ Batch serves feature values to BigQuery destination

        Args:
            bq_destination_output_uri (str):
                Required. BigQuery URI to the detination table.

                Example:
                    'bq://project.dataset.table_name'

                It requires an existing BigQuery destination Dataset, under the same project as the Featurestore.

            entity_type_ids (List[str]):
                Required. ID of the EntityType to select batch serving Features. The
                EntityType id is the specified during EntityType creation.
            entity_type_destination_fields (Dict[str, Union[Dict[str, str], List[str], Set[str]]]):
                Optional. User defined dictionary to map ID of the EntityType's Features
                to the batch serving destination field name.

                Specify the features to be batch served in each entityType, and their destination field name.
                If the features are not specified, all features will be batch served.
                If the destination field name is not specified, Feature ID will be used as destination field name.

                Example:

                     - In case all features will be batch served and using Feature ID as destination field name:

                         entity_type_ids = ['my_entity_type_id_1', 'my_entity_type_id_2', 'my_entity_type_id_3']

                         entity_type_destination_fields = {}
                         or
                         entity_type_destination_fields = {
                            'my_entity_type_id_1': {},
                            'my_entity_type_id_2': [],
                            'my_entity_type_id_3': None,
                         }

                     - In case selected features will be batch served and using Feature ID as destination field name:

                         entity_type_ids = ['my_entity_type_id_1', 'my_entity_type_id_2', 'my_entity_type_id_3']

                         feature_source_fields = {
                            'my_entity_type_id_1': ['feature_id_1_1', 'feature_id_1_2'],
                            'my_entity_type_id_2': ['feature_id_2_1', 'feature_id_2_2'],
                            'my_entity_type_id_3': ['feature_id_3_1', 'feature_id_3_2'],
                         }

                     - In case selected features will be batch served with specified destination field name

                     feature_source_fields = {
                        'my_entity_type_id_1': {
                            'feature_id_1_1': 'feature_id_1_1_destination_field',
                            'feature_id_1_2': 'feature_id_1_2_destination_field',
                        },
                        'my_entity_type_id_2': {
                            'feature_id_2_1': 'feature_id_2_1_destination_field',
                            'feature_id_2_2': 'feature_id_2_2_destination_field',
                        },
                        'my_entity_type_id_3': {
                            'feature_id_3_1': 'feature_id_3_1_destination_field',
                            'feature_id_3_2': 'feature_id_3_2_destination_field',
                        },
                     }
                Note: the above three cases can be mixed in use.

            read_instances (Union[str, List[str]]):
                Optional. Read_instances can be either BigQuery URI to the input table,
                or Google Cloud Storage URI(-s) to the
                csv file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
                Example:
                    'bq://project.dataset.table_name'
                    or
                    ["gs://my_bucket/my_file_1.csv", "gs://my_bucket/my_file_2.csv"]

                Each read instance consists of exactly one read timestamp
                and one or more entity IDs identifying entities of the
                corresponding EntityTypes whose Features are requested.

                Each output instance contains Feature values of requested
                entities concatenated together as of the read time.

                An example read instance may be
                ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z``.

                An example output instance may be
                ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z, foo_entity_feature1_value, bar_entity_feature2_value``.

                Timestamp in each read instance must be millisecond-aligned.

                The columns can be in any order.

                Values in the timestamp column must use the RFC 3339 format,
                e.g. ``2012-07-30T10:43:17.123Z``.

            pass_through_fields (List[str]):
                Optional. When not empty, the specified fields in the
                read_instances source will be joined as-is in the output,
                in addition to those fields from the Featurestore Entity.

                For BigQuery source, the type of the pass-through values
                will be automatically inferred. For CSV source, the
                pass-through values will be passed as opaque bytes.

        Returns:
            Featurestore - The featurestore resource object batch read feature values from.

        Raises:
            NotFound: if the BigQuery destination Dataset does not exist.
            FailedPrecondition: if the BigQuery destination Dataset/Table is in a different project.
        """
        bigquery_read_instances, csv_read_instances = self._get_read_instances(
            read_instances
        )

        batch_read_feature_values_request = self._validate_and_get_batch_read_feature_values_request(
            entity_type_ids=entity_type_ids,
            entity_type_destination_fields=entity_type_destination_fields,
            bigquery_read_instances=bigquery_read_instances,
            csv_read_instances=csv_read_instances,
            pass_through_fields=pass_through_fields,
            bigquery_destination=gca_io.BigQueryDestination(
                output_uri=bq_destination_output_uri
            ),
        )

        return self._batch_read_feature_values(
            batch_read_feature_values_request=batch_read_feature_values_request,
            request_metadata=request_metadata,
            sync=sync,
        )

    def batch_serve_to_gcs(
        self,
        gcs_destination_output_uri_prefix: str,
        gcs_destination_type: str,
        entity_type_ids: List[str],
        entity_type_destination_fields: Optional[
            Dict[str, Union[Dict[str, str], List[str], Set[str]]]
        ] = {},
        read_instances: Optional[Union[str, List[str]]] = None,
        pass_through_fields: Optional[List[str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "Featurestore":
        """ Batch serves feature values to GCS destination

        Args:
            gcs_destination_output_uri_prefix (str):
                Required. Google Cloud Storage URI to output
                directory. If the uri doesn't end with '/', a
                '/' will be automatically appended. The
                directory is created if it doesn't exist.

                Example:
                    "gs://bucket/path/to/prefix"

            gcs_destination_type (str):
                Required. The type of the destination files(s),
                the value of gcs_destination_type can only be either `csv`, or `tfrecord`.

                For CSV format. Array Feature value types are not allowed in CSV format.

                For TFRecord format.

                Below are the mapping from Feature value type in
                Featurestore to Feature value type in TFRecord:

                ::

                    Value type in Featurestore                 | Value type in TFRecord
                    DOUBLE, DOUBLE_ARRAY                       | FLOAT_LIST
                    INT64, INT64_ARRAY                         | INT64_LIST
                    STRING, STRING_ARRAY, BYTES                | BYTES_LIST
                    true -> byte_string("true"), false -> byte_string("false")
                    BOOL, BOOL_ARRAY (true, false)             | BYTES_LIST

            entity_type_ids (List[str]):
                Required. ID of the EntityType to select batch serving Features. The
                EntityType id is the specified during EntityType creation.
            entity_type_destination_fields (Dict[str, Union[Dict[str, str], List[str], Set[str]]]):
                Optional. User defined dictionary to map ID of the EntityType's Features
                to the batch serving destination field name.

                Specify the features to be batch served in each entityType, and their destination field name.
                If the features are not specified, all features will be batch served.
                If the destination field name is not specified, Feature ID will be used as destination field name.

                Example:

                     - In case all features will be batch served and using Feature ID as destination field name:

                         entity_type_ids = ['my_entity_type_id_1', 'my_entity_type_id_2', 'my_entity_type_id_3']

                         entity_type_destination_fields = {}
                         or
                         entity_type_destination_fields = {
                            'my_entity_type_id_1': {},
                            'my_entity_type_id_2': [],
                            'my_entity_type_id_3': None,
                         }

                     - In case selected features will be batch served and using Feature ID as destination field name:

                         entity_type_ids = ['my_entity_type_id_1', 'my_entity_type_id_2', 'my_entity_type_id_3']

                         feature_source_fields = {
                            'my_entity_type_id_1': ['feature_id_1_1', 'feature_id_1_2'],
                            'my_entity_type_id_2': ['feature_id_2_1', 'feature_id_2_2'],
                            'my_entity_type_id_3': ['feature_id_3_1', 'feature_id_3_2'],
                         }

                     - In case selected features will be batch served with specified destination field name

                     feature_source_fields = {
                        'my_entity_type_id_1': {
                            'feature_id_1_1': 'feature_id_1_1_destination_field',
                            'feature_id_1_2': 'feature_id_1_2_destination_field',
                        },
                        'my_entity_type_id_2': {
                            'feature_id_2_1': 'feature_id_2_1_destination_field',
                            'feature_id_2_2': 'feature_id_2_2_destination_field',
                        },
                        'my_entity_type_id_3': {
                            'feature_id_3_1': 'feature_id_3_1_destination_field',
                            'feature_id_3_2': 'feature_id_3_2_destination_field',
                        },
                     }
                Note: the above three cases can be mixed in use.

            read_instances (Union[str, List[str]]):
                Optional. Read_instances can be either BigQuery URI to the input table,
                or Google Cloud Storage URI(-s) to the
                csv file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
                Example:
                    'bq://project.dataset.table_name'
                    or
                    ["gs://my_bucket/my_file_1.csv", "gs://my_bucket/my_file_2.csv"]

                Each read instance consists of exactly one read timestamp
                and one or more entity IDs identifying entities of the
                corresponding EntityTypes whose Features are requested.

                Each output instance contains Feature values of requested
                entities concatenated together as of the read time.

                An example read instance may be
                ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z``.

                An example output instance may be
                ``foo_entity_id, bar_entity_id, 2020-01-01T10:00:00.123Z, foo_entity_feature1_value, bar_entity_feature2_value``.

                Timestamp in each read instance must be millisecond-aligned.

                The columns can be in any order.

                Values in the timestamp column must use the RFC 3339 format,
                e.g. ``2012-07-30T10:43:17.123Z``.

            pass_through_fields (List[str]):
                Optional. When not empty, the specified fields in the
                read_instances source will be joined as-is in the output,
                in addition to those fields from the Featurestore Entity.

                For BigQuery source, the type of the pass-through values
                will be automatically inferred. For CSV source, the
                pass-through values will be passed as opaque bytes.

        Returns:
            Featurestore - The featurestore resource object batch read feature values from.

        Raises:
            ValueError if gcs_destination_type is not supported.

        """

        if gcs_destination_type not in featurestore_utils.GCS_DESTINATION_TYPE:
            raise ValueError(
                "Only %s are supported gcs_destination_type, not `%s`. "
                % (
                    "`" + "`, `".join(featurestore_utils.GCS_DESTINATION_TYPE) + "`",
                    gcs_destination_type,
                )
            )

        gcs_destination = gca_io.GcsDestination(
            output_uri_prefix=gcs_destination_output_uri_prefix
        )
        csv_destination, tfrecord_destination = None, None
        if gcs_destination_type == "csv":
            csv_destination = gca_io.CsvDestination(gcs_destination=gcs_destination)
        elif gcs_destination_type == "tfrecord":
            tfrecord_destination = gca_io.TFRecordDestination(
                gcs_destination=gcs_destination
            )

        bigquery_read_instances, csv_read_instances = self._get_read_instances(
            read_instances
        )

        batch_read_feature_values_request = self._validate_and_get_batch_read_feature_values_request(
            entity_type_ids=entity_type_ids,
            entity_type_destination_fields=entity_type_destination_fields,
            bigquery_read_instances=bigquery_read_instances,
            csv_read_instances=csv_read_instances,
            pass_through_fields=pass_through_fields,
            csv_destination=csv_destination,
            tfrecord_destination=tfrecord_destination,
        )

        return self._batch_read_feature_values(
            batch_read_feature_values_request=batch_read_feature_values_request,
            request_metadata=request_metadata,
            sync=sync,
        )
