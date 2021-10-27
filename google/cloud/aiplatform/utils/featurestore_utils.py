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
from typing import Dict

RESOURCE_ID_PATTERN_REGEX = r"[a-z_][a-z0-9_]{0,59}"
FEATURESTORE_NAME_PATTERN_REGEX = (
    r"projects\/(?P<project>[\w-]+)"
    r"\/locations\/(?P<location>[\w-]+)"
    r"\/featurestores\/(?P<featurestore_id>" + RESOURCE_ID_PATTERN_REGEX + r")"
)
ENTITY_TYPE_NAME_PATTERN_REGEX = (
    FEATURESTORE_NAME_PATTERN_REGEX
    + r"\/entityTypes\/(?P<entity_type_id>"
    + RESOURCE_ID_PATTERN_REGEX
    + r")"
)
FEATURE_NAME_PATTERN_REGEX = (
    ENTITY_TYPE_NAME_PATTERN_REGEX
    + r"\/features\/(?P<feature_id>"
    + RESOURCE_ID_PATTERN_REGEX
    + r")"
)


def validate_id(resource_id: str) -> bool:
    """Validates feature store resource ID pattern."""
    return bool(re.compile(r"^" + RESOURCE_ID_PATTERN_REGEX + r"$").match(resource_id))


def validate_featurestore_name(featurestore_name: str) -> Dict[str, str]:
    """Validates featurestore name pattern."""
    m = re.compile(r"^" + FEATURESTORE_NAME_PATTERN_REGEX + r"$").match(
        featurestore_name
    )
    return m.groupdict() if m else {}


def validate_entity_type_name(entity_type_name: str) -> Dict[str, str]:
    """Validates entity type name pattern."""
    m = re.compile(r"^" + ENTITY_TYPE_NAME_PATTERN_REGEX + r"$").match(entity_type_name)
    return m.groupdict() if m else {}


def validate_feature_name(feature_name: str) -> Dict[str, str]:
    """Validates feature name pattern."""
    m = re.compile(r"^" + FEATURE_NAME_PATTERN_REGEX + r"$").match(feature_name)
    return m.groupdict() if m else {}


def get_entity_type_resource_noun(featurestore_id: str) -> str:
    """Gets composite resource noun for entity_type resource."""
    return f"featurestores/{featurestore_id}/entityTypes"


def get_feature_resource_noun(featurestore_id: str, entity_type_id: str) -> str:
    """Gets composite resource noun for feature resource."""
    return f"featurestores/{featurestore_id}/entityTypes/{entity_type_id}/features"
