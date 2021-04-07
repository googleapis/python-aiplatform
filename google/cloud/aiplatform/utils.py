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
import logging

from typing import Any, Match, Optional, Type, TypeVar, Tuple
from collections import namedtuple

from google.api_core import client_options
from google.api_core import gapic_v1
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import constants
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.types import (
    accelerator_type as gca_accelerator_type,
)
from google.cloud.aiplatform_v1beta1.services.dataset_service import (
    client as dataset_client,
)
from google.cloud.aiplatform_v1beta1.services.endpoint_service import (
    client as endpoint_client,
)
from google.cloud.aiplatform_v1beta1.services.job_service import (
    client as job_service_client,
)
from google.cloud.aiplatform_v1beta1.services.model_service import (
    client as model_client,
)
from google.cloud.aiplatform_v1beta1.services.pipeline_service import (
    client as pipeline_service_client,
)
from google.cloud.aiplatform_v1beta1.services.prediction_service import (
    client as prediction_client,
)

AiPlatformServiceClient = TypeVar(
    "AiPlatformServiceClient",
    dataset_client.DatasetServiceClient,
    endpoint_client.EndpointServiceClient,
    model_client.ModelServiceClient,
    prediction_client.PredictionServiceClient,
    pipeline_service_client.PipelineServiceClient,
    job_service_client.JobServiceClient,
)

RESOURCE_NAME_PATTERN = re.compile(
    r"^projects\/(?P<project>[\w-]+)\/locations\/(?P<location>[\w-]+)\/(?P<resource>[\w\-\/]+)\/(?P<id>[\w-]+)$"
)
RESOURCE_ID_PATTERN = re.compile(r"^[\w-]+$")

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
            A resource noun to validate the resource name against.
            For example, you would pass "datasets" to validate
            "projects/123/locations/us-central1/datasets/456".
            In the case of deeper naming structures, e.g.,
            "projects/123/locations/us-central1/metadataStores/123/contexts/456",
            you would pass "metadataStores/123/contexts" as the resource_noun.
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
            A resource noun to validate the resource name against.
            For example, you would pass "datasets" to validate
            "projects/123/locations/us-central1/datasets/456".
            In the case of deeper naming structures, e.g.,
            "projects/123/locations/us-central1/metadataStores/123/contexts/456",
            you would pass "metadataStores/123/contexts" as the resource_noun.
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
    # Fully qualified resource name, e.g., "projects/.../locations/.../datasets/12345" or
    # "projects/.../locations/.../metadataStores/.../contexts/12345"
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


# TODO(b/172932277) verify display name only contains utf-8 chars
def validate_display_name(display_name: str):
    """Verify display name is at most 128 chars

    Args:
        display_name: display name to verify
    Raises:
        ValueError: display name is longer than 128 characters
    """
    if len(display_name) > 128:
        raise ValueError("Display name needs to be less than 128 characters.")


def validate_region(region: str) -> bool:
    """Validates region against supported regions.

    Args:
        region: region to validate
    Returns:
        bool: True if no errors raised
    Raises:
        ValueError: If region is not in supported regions.
    """
    if not region:
        raise ValueError(
            f"Please provide a region, select from {constants.SUPPORTED_REGIONS}"
        )

    region = region.lower()
    if region not in constants.SUPPORTED_REGIONS:
        raise ValueError(
            f"Unsupported region for AI Platform, select from {constants.SUPPORTED_REGIONS}"
        )

    return True


def validate_accelerator_type(accelerator_type: str) -> bool:
    """Validates user provided accelerator_type string for training and prediction

    Args:
        accelerator_type (str):
            Represents a hardware accelerator type.
    Returns:
        bool: True if valid accelerator_type
    Raises:
        ValueError if accelerator type is invalid.
    """
    if accelerator_type not in gca_accelerator_type.AcceleratorType._member_names_:
        raise ValueError(
            f"Given accelerator_type `{accelerator_type}` invalid. "
            f"Choose one of {gca_accelerator_type.AcceleratorType._member_names_}"
        )
    return True


def extract_bucket_and_prefix_from_gcs_path(gcs_path: str) -> Tuple[str, Optional[str]]:
    """Given a complete GCS path, return the bucket name and prefix as a tuple.

    Example Usage:

        bucket, prefix = extract_bucket_and_prefix_from_gcs_path(
            "gs://example-bucket/path/to/folder"
        )

        # bucket = "example-bucket"
        # prefix = "path/to/folder"

    Args:
        gcs_path (str):
            Required. A full path to a Google Cloud Storage folder or resource.
            Can optionally include "gs://" prefix or end in a trailing slash "/".

    Returns:
        Tuple[str, Optional[str]]
            A (bucket, prefix) pair from provided GCS path. If a prefix is not
            present, a None will be returned in its place.
    """
    if gcs_path.startswith("gs://"):
        gcs_path = gcs_path[5:]
    if gcs_path.endswith("/"):
        gcs_path = gcs_path[:-1]

    gcs_parts = gcs_path.split("/", 1)
    gcs_bucket = gcs_parts[0]
    gcs_blob_prefix = None if len(gcs_parts) == 1 else gcs_parts[1]

    return (gcs_bucket, gcs_blob_prefix)


class WrappedClient:
    """Wrapper class for client that creates client at API invocation time."""

    def __init__(
        self,
        client_class: Type[AiPlatformServiceClient],
        client_options: client_options.ClientOptions,
        client_info: gapic_v1.client_info.ClientInfo,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Stores parameters needed to instantiate client.

        client_class (AiPlatformServiceClient):
            Required. Class of the client to use.
        client_options (client_options.ClientOptions):
            Required. Client options to pass to client.
        client_info (gapic_v1.client_info.ClientInfo):
            Required. Client info to pass to client.
        credentials (auth_credentials.credentials):
            Optional. Client credentials to pass to client.
        """

        self._client_class = client_class
        self._credentials = credentials
        self._client_options = client_options
        self._client_info = client_info

    def __getattr__(self, name: str) -> Any:
        """Instantiates client and returns attribute of the client."""
        temporary_client = self._client_class(
            credentials=self._credentials,
            client_options=self._client_options,
            client_info=self._client_info,
        )
        return getattr(temporary_client, name)


class LoggingWarningFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == logging.WARNING
