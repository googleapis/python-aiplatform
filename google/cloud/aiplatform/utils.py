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

from typing import Optional, TypeVar, Match
from collections import namedtuple

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.services.dataset_service import (
    client as dataset_client,
)
from google.cloud.aiplatform_v1beta1.services.model_service import (
    client as model_client,
)

DEFAULT_REGION = "us-central1"
SUPPORTED_REGIONS = ("us-central1", "europe-west4", "asia-east1")
PROD_API_ENDPOINT = "aiplatform.googleapis.com"

AiPlatformServiceClient = TypeVar(
    "AiPlatformServiceClient",
    dataset_client.DatasetServiceClient,
    model_client.ModelServiceClient,
)

# TODO(b/170334193): Add support for resource names with non-integer IDs
# TODO(b/170334098): Add support for resource names more than one level deep
RESOURCE_NAME_PATTERN = re.compile(
    r"^projects\/(?P<project>[\w-]+)\/locations\/(?P<location>[\w-]+)\/(?P<resource>\w+)\/(?P<id>\d+)$"
)
RESOURCE_ID_PATTERN = re.compile(r"^\d+$")

Fields = namedtuple("Fields", ["project", "location", "resource", "id"],)


def _match_to_fields(match: Match) -> Optional[Fields]:
    """Normalize RegEx groups from resource name pattern Match to class Fields"""
    if not match:
        return None

    return Fields(
        project=match["project"],
        location=match["location"],
        resource=match["resource"],
        id=match["id"],
    )


def validate_id(resource_id: str) -> bool:
    """Validate int64 resource ID number"""
    return bool(RESOURCE_ID_PATTERN.match(resource_id))


def extract_fields_from_resource_name(
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


def full_resource_name(
    resource_name: str,
    resource_noun: str,
    project: Optional[str] = None,
    location: Optional[str] = None,
) -> str:
    """
    Returns fully qualified resource name.

    Args:
        resource_name (str):
            Required. A fully-qualified AI Platform (Unified) resource name or
            resource ID.
        resource_noun (str):
            A plural resource noun to validate the resource name against.
            For example, you would pass "datasets" to validate
            "projects/123/locations/us-central1/datasets/456".
        project (str):
            Optional project to retrieve resource_noun from. If not set, project
            set in aiplatform.init will be used.
        location (str):
            Optional location to retrieve resource_noun from. If not set, location
            set in aiplatform.init will be used.

    Returns:
        resource_name (str):
            A fully-qualified AI Platform (Unified) resource name.

    Raises:
        ValueError:
            If resource name, resource ID or project ID not provided.
    """
    validate_resource_noun(resource_noun)
    # Fully qualified resource name, i.e. "projects/.../locations/.../datasets/12345"
    valid_name = extract_fields_from_resource_name(
        resource_name=resource_name, resource_noun=resource_noun
    )

    user_project = project or initializer.global_config.project
    user_location = location or initializer.global_config.location

    # Partial resource name (i.e. "12345") with known project and location
    if (
        not valid_name
        and validate_project(user_project)
        and validate_region(user_location)
        and validate_id(resource_name)
    ):
        resource_name = f"projects/{user_project}/locations/{user_location}/{resource_noun}/{resource_name}"
    # Invalid resource_name parameter
    elif not valid_name:
        raise ValueError(f"Please provide a valid {resource_noun[:-1]} name or ID")

    return resource_name


# TODO(b/172286889) validate resource noun
def validate_resource_noun(resource_noun: str) -> bool:
    """Validates resource noun.

    Args:
        resource_noun: resource noun to validate
    Returns:
        bool: True if no errors raised
    Raises:
        ValueError: If resource noun not supported.
    """
    if resource_noun:
        return True
    raise ValueError("Please provide a valid resource noun")


# TODO(b/172288287) validate project
def validate_project(project: str) -> bool:
    """Validates project.

    Args:
        project: project to validate
    Returns:
        bool: True if no errors raised
    Raises:
        ValueError: If project does not exist.
    """
    if project:
        return True
    raise ValueError("Please provide a valid project ID")


def validate_region(region: str):
    """Validates region against supported regions.

    Args:
        region: region to validate
    Returns:
        bool: True if no errors raised
    Raises:
        ValueError: If region is not in supported regions.
    """
    if not region:
        raise ValueError(f"Please provide a region, select from {SUPPORTED_REGIONS}")

    region = region.lower()
    if region not in SUPPORTED_REGIONS:
        raise ValueError(
            f"Unsupported region for AI Platform, select from {SUPPORTED_REGIONS}"
        )

    return True
