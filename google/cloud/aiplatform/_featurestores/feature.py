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

from typing import Dict, List, Optional, Sequence, Tuple, Union

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import feature as gca_feature
from google.cloud.aiplatform import _featurestores
from google.cloud.aiplatform import utils

from google.cloud.aiplatform.utils import featurestore_utils

_LOGGER = base.Logger(__name__)


class Feature(base.VertexAiResourceNounWithFutureManager):
    """Managed feature resource for Vertex AI."""

    client_class = utils.FeaturestoreClientWithOverride

    _is_client_prediction_client = False
    _resource_noun = None
    _getter_method = "get_feature"
    _list_method = "list_features"
    _delete_method = "delete_feature"

    def __init__(
        self,
        feature_name: str,
        featurestore_id: Optional[str] = None,
        entity_type_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed feature given a feature resource name or a feature ID.

        Example Usage:

            my_feature = aiplatform.Feature(
                feature_name='projects/123/locations/us-central1/featurestores/my_featurestore_id/\
                entityTypes/my_entity_type_id/features/my_feature_id'
            )
            or
            my_feature = aiplatform.Feature(
                feature_name='my_feature_id',
                featurestore_id='my_featurestore_id',
                entity_type_id='my_entity_type_id',
            )

        Args:
            feature_name (str):
                Required. A fully-qualified feature resource name or a feature ID.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id/entityTypes/my_entity_type_id/features/my_feature_id"
                or "my_feature_id" when project and location are initialized or passed, with featurestore_id and entity_type_id passed.
            featurestore_id (str):
                Optional. Featurestore to retrieve feature from.
            entity_type_id (str):
                Optional. EntityType to retrieve feature from.
            project (str):
                Optional. Project to retrieve feature from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve feature from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Feature. Overrides
                credentials set in aiplatform.init.

        Raises:
            ValueError if the provided feature_name is not in form of a fully-qualified
            feature resource name nor a feature ID with featurestore_id and entity_type_id passed.
        """

        match = featurestore_utils.validate_feature_name(feature_name)

        if match:
            self._featurestore_id = match["featurestore_id"]
            self._entity_type_id = match["entity_type_id"]
        elif (
            featurestore_utils.validate_id(feature_name)
            and featurestore_id
            and entity_type_id
            and featurestore_utils.validate_id(featurestore_id)
            and featurestore_utils.validate_id(entity_type_id)
        ):
            self._featurestore_id = featurestore_id
            self._entity_type_id = entity_type_id
        else:
            raise ValueError(
                f"{feature_name} is not in form of a fully-qualified feature resource name "
                f"nor a feature ID with featurestore_id and entity_type_id passed."
            )

        self._resource_noun = featurestore_utils.get_feature_resource_noun(
            featurestore_id=self._featurestore_id, entity_type_id=self._entity_type_id
        )

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=feature_name,
        )
        self._gca_resource = self._get_gca_resource(resource_name=feature_name)

        self._featurestore_name = utils.full_resource_name(
            resource_name=self._featurestore_id,
            resource_noun="featurestores",
            project=self.project,
            location=self.location,
        )

        self._entity_type_name = utils.full_resource_name(
            resource_name=self._entity_type_id,
            resource_noun=featurestore_utils.get_entity_type_resource_noun(
                featurestore_id=self._featurestore_id
            ),
            project=self.project,
            location=self.location,
        )

    @property
    def featurestore_name(self) -> str:
        """Full qualified resource name of the managed featurestore in which this Feature is."""
        return self._featurestore_name

    def get_featurestore(self) -> _featurestores.Featurestore:
        """Retrieves the managed featurestore in which this Feature is.

        Returns:
            featurestores.Featurestore - The managed featurestore in which this Feature is.
        """
        return _featurestores.Featurestore(self._featurestore_name)

    @property
    def entity_type_name(self) -> str:
        """Full qualified resource name of the managed entityType in which this Feature is."""
        return self._entity_type_name

    def get_entity_type(self) -> _featurestores.EntityType:
        """Retrieves the managed entityType in which this Feature is.

        Returns:
            featurestores.EntityType - The managed entityType in which this Feature is.
        """
        return _featurestores.EntityType(self._entity_type_name)

    def update(
        self,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "Feature":
        """Updates an existing managed feature resource.

        Example Usage:

            my_feature = aiplatform.Feature(
                feature_name='my_feature_id',
                featurestore_id='my_featurestore_id',
                entity_type_id='my_entity_type_id',
            )
            my_feature.update(
                description='update my description',
            )

        Args:
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

        Returns:
            Feature - The updated feature resource object.
        """
        update_mask = list()

        if description:
            update_mask.append("description")

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_feature = gca_feature.Feature(
            name=self.resource_name, description=description, labels=labels,
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "feature", self,
        )

        update_feature_lro = self.api_client.update_feature(
            feature=gapic_feature, update_mask=update_mask, metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "feature", self.__class__, update_feature_lro
        )

        update_feature_lro.result()

        _LOGGER.log_action_completed_against_resource("feature", "updated", self)

        return self

    @classmethod
    def list(
        cls,
        entity_type_name: str,
        featurestore_id: Optional[str] = None,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["Feature"]:
        """Lists existing managed feature resources in an entityType, given an entityType resource name or an entity_type ID.

        Example Usage:

            my_features = aiplatform.Feature.list(
                entity_type_name='projects/123/locations/us-central1/featurestores/my_featurestore_id/\
                entityTypes/my_entity_type_id'
            )
            or
            my_features = aiplatform.Feature.list(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )

        Args:
            entity_type_name (str):
                Required. A fully-qualified entityType resource name or an entity_type ID to list features in
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id/entityTypes/my_entity_type_id"
                or "my_entity_type_id" when project and location are initialized or passed, with featurestore_id passed.
            featurestore_id (str):
                Optional. Featurestore to list features in.
            filter (str):
                Optional. An expression for filtering the results of the request.
                For field names both snake_case and camelCase are supported.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for descending.
                Supported fields: `display_name`, `create_time`, `update_time`
            project (str):
                Optional. Project to list features in. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to list features in. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to list features. Overrides
                credentials set in aiplatform.init.

        Returns:
            List[Features] - A list of managed feature resource objects

        Raises:
            ValueError if the provided entity_type_name is not in form of a fully-qualified
            entityType resource name nor an entity_type ID with featurestore_id passed.
        """

        match = featurestore_utils.validate_entity_type_name(entity_type_name)

        if match:
            cls._featurestore_id = match["featurestore_id"]
            cls._entity_type_id = match["entity_type_id"]
        elif (
            featurestore_utils.validate_id(entity_type_name)
            and featurestore_id
            and featurestore_utils.validate_id(featurestore_id)
        ):
            cls._featurestore_id = featurestore_id
            cls._entity_type_id = entity_type_name
        else:
            raise ValueError(
                f"{entity_type_name} is not in form of a fully-qualified entityType resource name "
                f"nor an entity_type ID with featurestore_id passed."
            )

        cls._resource_noun = featurestore_utils.get_feature_resource_noun(
            featurestore_id=cls._featurestore_id, entity_type_id=cls._entity_type_id
        )

        cls._entity_type_name = utils.full_resource_name(
            resource_name=cls._entity_type_id,
            resource_noun=featurestore_utils.get_entity_type_resource_noun(
                featurestore_id=cls._featurestore_id
            ),
            project=project,
            location=location,
        )
        return cls._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
            parent=cls._entity_type_name,
        )

    @classmethod
    def create(
        cls,
        entity_type: Union[_featurestores.EntityType, str],
        feature_id: str,
        value_type: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        sync: bool = True,
    ) -> "Feature":
        """"""
        raise NotImplementedError
