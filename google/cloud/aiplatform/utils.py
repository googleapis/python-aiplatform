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


import re

from typing import Optional
from collections import namedtuple

DEFAULT_REGION = "us-central1"
SUPPORTED_REGIONS = ("us-central1", "europe-west4", "asia-east1")
PROD_API_ENDPOINT = "aiplatform.googleapis.com"

# TODO(b/170334193): Add support for resource names with non-integer IDs
# TODO(b/170334098): Add support for resource names more than one level deep
RESOURCE_NAME_PATTERN = re.compile(
    r"^projects\/(?P<project>[\w-]+)\/locations\/(?P<location>[\w-]+)\/(?P<resource>\w+)\/(?P<id>\d+)$"
)

Fields = namedtuple(
    "Fields",
    [
        "project",
        "location",
        "resource",
        "id",
    ],
)


def _match_to_fields(match: re.Match) -> Optional[Fields]:
    """Normalize RegEx groups from resource name pattern Match to class Fields"""
    if not match:
        return None

    return Fields(
        project=match["project"],
        location=match["location"],
        resource=match["resource"],
        id=match["id"],
    )


def validate_name(
    resource_name: str, resource_noun: Optional[str] = None
) -> Optional[Fields]:
    """Validates and returns extracted fields from a fully-qualified resource name.
    Returns None if name is invalid.

    Args:
        resource_name (str):
            Required. A fully-qualified AI Platform (Unified) resource name

        resource_noun (str):
            A plural resource noun to validate the resource name against.
            For example, you would pass "datasets" to validate
            "projects/123/locations/us-central1/datasets/456".

    Returns:
        fields (Fields):
            A named tuple containing four extracted fields from a resource name:
            project, location, resource, and id. These fields can be used for
            subsequent method calls in the SDK.
    """
    fields = _match_to_fields(RESOURCE_NAME_PATTERN.match(resource_name))

    if not fields:
        return None
    if resource_noun and fields.resource != resource_noun:
        return None

    return fields


def validate_region(region: str):
    """Validates region against supported regions.

    Args:
        region: region to validate
    Raises:
        ValueError if region is not in supported regions.
    """
    region = region.lower()
    if region not in SUPPORTED_REGIONS:
        raise ValueError(
            f"Unsupported region for AI Platform, select from {SUPPORTED_REGIONS}"
        )
