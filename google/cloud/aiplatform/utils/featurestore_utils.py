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

import re
from typing import Dict, List, NamedTuple, Optional, Tuple, Union

from google.cloud.aiplatform.compat.services import featurestore_service_client
from google.cloud.aiplatform.compat.types import feature as gca_feature
from google.cloud.aiplatform import utils

CompatFeaturestoreServiceClient = featurestore_service_client.FeaturestoreServiceClient

RESOURCE_ID_PATTERN_REGEX = r"[a-z_][a-z0-9_]{0,59}"
FEATURESTORE_RESOURCE_NOUN = "featurestores"
_FEATURE_VALUE_TYPE_UNSPECIFIED = "VALUE_TYPE_UNSPECIFIED"


def validate_id(resource_id: str) -> bool:
    """Validates feature store resource ID pattern."""
    return bool(re.compile(r"^" + RESOURCE_ID_PATTERN_REGEX + r"$").match(resource_id))


def validate_and_get_entity_type_resource_ids(
    entity_type_name: str, featurestore_id: Optional[str] = None,
) -> Tuple[str, str]:
    """Validates and gets featurestore ID and entity_type ID of the entity_type resource.

    Args:
        entity_type_name (str):
            Required. A fully-qualified entityType resource name or an entity_type ID
            Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id/entityTypes/my_entity_type_id"
            or "my_entity_type_id", with featurestore_id passed.
        featurestore_id (str):
            Optional. Featurestore ID of the entity_type resource.

    Returns:
        Tuple[str, str] - featurestore ID and entity_type ID

    Raises:
        ValueError if the provided entity_type_name is not in form of a fully-qualified
        entityType resource name nor an entity_type ID with featurestore_id passed.
    """
    match = CompatFeaturestoreServiceClient.parse_entity_type_path(
        path=entity_type_name
    )

    if match:
        featurestore_id = match["featurestore"]
        entity_type_id = match["entity_type"]
    elif (
        validate_id(entity_type_name)
        and featurestore_id
        and validate_id(featurestore_id)
    ):
        entity_type_id = entity_type_name
    else:
        raise ValueError(
            f"{entity_type_name} is not in form of a fully-qualified entityType resource name "
            f"nor an entity_type ID with featurestore_id passed."
        )
    return (featurestore_id, entity_type_id)


def validate_and_get_feature_resource_ids(
    feature_name: str,
    featurestore_id: Optional[str] = None,
    entity_type_id: Optional[str] = None,
) -> Tuple[str, str, str]:
    """Validates and gets featurestore ID, entity_type ID, and feature ID for the feature resource.
    Args:
        feature_name (str):
            Required. A fully-qualified feature resource name or a feature ID.
            Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id/entityTypes/my_entity_type_id/features/my_feature_id"
            or "my_feature_id" when project and location are initialized or passed, with featurestore_id and entity_type_id passed.
        featurestore_id (str):
            Optional. Featurestore ID of the feature resource.
        entity_type_id (str):
            Optional. EntityType ID of the feature resource.

    Returns:
        Tuple[str, str, str] - featurestore ID, entity_type ID, and feature ID

    Raises:
        ValueError if the provided feature_name is not in form of a fully-qualified
        feature resource name nor a feature ID with featurestore_id and entity_type_id passed.
    """

    match = CompatFeaturestoreServiceClient.parse_feature_path(path=feature_name)

    if match:
        featurestore_id = match["featurestore"]
        entity_type_id = match["entity_type"]
        feature_id = match["feature"]
    elif (
        validate_id(feature_name)
        and featurestore_id
        and entity_type_id
        and validate_id(featurestore_id)
        and validate_id(entity_type_id)
    ):
        feature_id = feature_name
    else:
        raise ValueError(
            f"{feature_name} is not in form of a fully-qualified feature resource name "
            f"nor a feature ID with featurestore_id and entity_type_id passed."
        )
    return (featurestore_id, entity_type_id, feature_id)


def validate_value_type(value_type: str) -> bool:
    """Validates user provided feature value_type string.

    Args:
        value_type (str):
            Required. Immutable. Type of Feature value.
            One of BOOL, BOOL_ARRAY, DOUBLE, DOUBLE_ARRAY, INT64, INT64_ARRAY, STRING, STRING_ARRAY, BYTES.
    Returns:
        bool: True if valid specified value_type
    Raises:
        ValueError if value_type is invalid or unspecified.
    """
    if (
        value_type not in gca_feature.Feature.ValueType._member_names_
        or getattr(gca_feature.Feature.ValueType, value_type)
        == gca_feature.Feature.ValueType.VALUE_TYPE_UNSPECIFIED
    ):
        raise ValueError(
            f"Given value_type `{value_type}` invalid or unspecified. "
            f"Choose one of {gca_feature.Feature.ValueType._member_names_} except `{_FEATURE_VALUE_TYPE_UNSPECIFIED}`"
        )
    return True


def validate_and_get_batch_create_features_requests(
    feature_configs: Dict[str, Dict[str, Union[bool, int, Dict[str, str], str]]]
) -> List[Dict[str, Union[int, str, Dict[str, str]]]]:
    """ Validates feature_configs and get batch_create_features_requests

    Args:
        feature_configs (Dict[str, Dict[str, Union[bool, int, Dict[str, str], str]]]):
            Required. A user defined Dict containing configurations for feature creation.

    Returns:
        List[Dict[str, Union[int, str, Dict[str, str]]]] - list of feature creation request
    """

    batch_create_features_requests = [
        _FeatureConfig(
            feature_id=feature_id,
            value_type=feature_config.get(
                "value_type", _FEATURE_VALUE_TYPE_UNSPECIFIED
            ),
            description=feature_config.get("description", None),
            labels=feature_config.get("labels", {}),
        ).request_dict
        for feature_id, feature_config in feature_configs.items()
    ]

    return batch_create_features_requests


class _FeatureConfig(NamedTuple):
    """Configuration for feature creation.

    Usage:

    config = _FeatureConfig(
        feature_id='my_feature_id',
        value_type='int64',
        description='my description',
        labels={'my_key': 'my_value'},
    )
    """

    feature_id: str
    value_type: str = _FEATURE_VALUE_TYPE_UNSPECIFIED
    description: Optional[str] = None
    labels: Optional[Dict[str, str]] = {}

    def _get_feature_id(self) -> str:
        """Validates and returns the feature_id.

        Returns:
            str - valid feature ID.

        Raise:
            ValueError if feature_id is invalid
        """
        if validate_id(self.feature_id):
            return self.feature_id
        raise ValueError(
            f"The value of feature_id may be up to 60 characters, and valid characters are `[a-z0-9_]`. "
            f"The first character cannot be a number. Instead, get {self.feature_id}."
        )

    def _get_value_type_enum(self) -> int:
        """Validates value_type and returns the enum of the value type.

        Returns:
            int - valid value type enum.
        """

        # Raises ValueError if invalid value_type
        validate_value_type(value_type=self.value_type)

        value_type_enum = getattr(gca_feature.Feature.ValueType, self.value_type)

        return value_type_enum

    @property
    def request_dict(self) -> Dict[str, Union[int, str, Dict[str, str]]]:
        """Return request as a Dict."""

        if self.labels:
            utils.validate_labels(self.labels)

        gapic_feature = gca_feature.Feature(
            description=self.description,
            value_type=self._get_value_type_enum(),
            labels=self.labels,
        )

        create_feature_request = {
            "feature": gapic_feature,
            "feature_id": self._get_feature_id(),
        }

        return create_feature_request
