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
from typing import Optional, Tuple

from google.cloud.aiplatform.compat.services import featurestore_service_client

CompatFeaturestoreServiceClient = featurestore_service_client.FeaturestoreServiceClient

RESOURCE_ID_PATTERN_REGEX = r"[a-z_][a-z0-9_]{0,59}"


def validate_id(resource_id: str) -> bool:
    """Validates feature store resource ID pattern."""
    return bool(re.compile(r"^" + RESOURCE_ID_PATTERN_REGEX + r"$").match(resource_id))


def validate_and_get_featurestore_resource_id(featurestore_name: str) -> str:
    """Validates and gets featurestore ID of the featurestore resource.

    Args:
            featurestore_name (str):
                Required. A fully-qualified featurestore resource name or a featurestore ID
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id"
                or "my_featurestore_id" when project and location are initialized or passed.

    Returns:
        str - featurestore ID

    Raises:
        ValueError if the provided featurestore_name is not in form of a fully-qualified
        featurestore resource name nor an featurestore ID.
    """
    match = CompatFeaturestoreServiceClient.parse_featurestore_path(
        path=featurestore_name
    )

    if match:
        featurestore_id = match["featurestore"]
    elif validate_id(featurestore_name):
        featurestore_id = featurestore_name
    else:
        raise ValueError(
            f"{featurestore_name} is not in form of a fully-qualified featurestore resource name nor an featurestore ID."
        )

    return featurestore_id


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
