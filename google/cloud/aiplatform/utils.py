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


import abc
from collections import namedtuple
import logging
import re
from typing import Any, Match, Optional, Type, TypeVar, Tuple

from google.api_core import client_options
from google.api_core import gapic_v1
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import constants
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.compat.services import (
    dataset_service_client_v1beta1,
    endpoint_service_client_v1beta1,
    job_service_client_v1beta1,
    model_service_client_v1beta1,
    pipeline_service_client_v1beta1,
    prediction_service_client_v1beta1,
)
from google.cloud.aiplatform.compat.services import (
    dataset_service_client_v1,
    endpoint_service_client_v1,
    job_service_client_v1,
    model_service_client_v1,
    pipeline_service_client_v1,
    prediction_service_client_v1,
)

from google.cloud.aiplatform.compat.types import (
    accelerator_type as gca_accelerator_type,
)

AiPlatformServiceClient = TypeVar(
    "AiPlatformServiceClient",
    # v1beta1
    dataset_service_client_v1beta1.DatasetServiceClient,
    endpoint_service_client_v1beta1.EndpointServiceClient,
    model_service_client_v1beta1.ModelServiceClient,
    prediction_service_client_v1beta1.PredictionServiceClient,
    pipeline_service_client_v1beta1.PipelineServiceClient,
    job_service_client_v1beta1.JobServiceClient,
    # v1
    dataset_service_client_v1.DatasetServiceClient,
    endpoint_service_client_v1.EndpointServiceClient,
    model_service_client_v1.ModelServiceClient,
    prediction_service_client_v1.PredictionServiceClient,
    pipeline_service_client_v1.PipelineServiceClient,
    job_service_client_v1.JobServiceClient,
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


class ClientWithOverride:
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

    @property
    @abc.abstractmethod
    def _is_temporary(self) -> bool:
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _default_version(self) -> str:
        pass

    @property
    @classmethod
    @abc.abstractmethod
    def _version_map(self) -> Tuple:
        pass

    def __init__(
        self,
        client_options: client_options.ClientOptions,
        client_info: gapic_v1.client_info.ClientInfo,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Stores parameters needed to instantiate client.

        client_options (client_options.ClientOptions):
            Required. Client options to pass to client.
        client_info (gapic_v1.client_info.ClientInfo):
            Required. Client info to pass to client.
        credentials (auth_credentials.credentials):
            Optional. Client credentials to pass to client.
        """

        self._clients = {
            version: self.WrappedClient(
                client_class=client_class,
                client_options=client_options,
                client_info=client_info,
                credentials=credentials,
            )
            if self._is_temporary
            else client_class(
                client_options=client_options,
                client_info=client_info,
                credentials=credentials,
            )
            for version, client_class in self._version_map
        }

    def __getattr__(self, name: str) -> Any:
        """Instantiates client and returns attribute of the client."""
        return getattr(self._clients[self._default_version], name)

    def select_version(self, version: str) -> AiPlatformServiceClient:
        return self._clients[version]


class DatasetClientWithOverride(ClientWithOverride):
    _is_temporary = True
    _default_version = compat.DEFAULT_VERSION
    _version_map = (
        (compat.V1, dataset_service_client_v1.DatasetServiceClient),
        (compat.V1BETA1, dataset_service_client_v1beta1.DatasetServiceClient),
    )


class EndpointClientWithOverride(ClientWithOverride):
    _is_temporary = True
    _default_version = compat.DEFAULT_VERSION
    _version_map = (
        (compat.V1, endpoint_service_client_v1.EndpointServiceClient),
        (compat.V1BETA1, endpoint_service_client_v1beta1.EndpointServiceClient),
    )


class JobpointClientWithOverride(ClientWithOverride):
    _is_temporary = True
    _default_version = compat.DEFAULT_VERSION
    _version_map = (
        (compat.V1, job_service_client_v1.JobServiceClient),
        (compat.V1BETA1, job_service_client_v1beta1.JobServiceClient),
    )


class ModelClientWithOverride(ClientWithOverride):
    _is_temporary = True
    _default_version = compat.DEFAULT_VERSION
    _version_map = (
        (compat.V1, model_service_client_v1.ModelServiceClient),
        (compat.V1BETA1, model_service_client_v1beta1.ModelServiceClient),
    )


class PipelineClientWithOverride(ClientWithOverride):
    _is_temporary = True
    _default_version = compat.DEFAULT_VERSION
    _version_map = (
        (compat.V1, pipeline_service_client_v1.PipelineServiceClient),
        (compat.V1BETA1, pipeline_service_client_v1beta1.PipelineServiceClient),
    )


class PredictionClientWithOverride(ClientWithOverride):
    _is_temporary = False
    _default_version = compat.DEFAULT_VERSION
    _version_map = (
        (compat.V1, prediction_service_client_v1.PredictionServiceClient),
        (compat.V1BETA1, prediction_service_client_v1beta1.PredictionServiceClient),
    )


AiPlatformServiceClientWithOverride = TypeVar(
    "AiPlatformServiceClientWithOverride",
    DatasetClientWithOverride,
    EndpointClientWithOverride,
    JobpointClientWithOverride,
    ModelClientWithOverride,
    PipelineClientWithOverride,
    PredictionClientWithOverride,
)


class LoggingWarningFilter(logging.Filter):
    def filter(self, record):
        return record.levelname == logging.WARNING
