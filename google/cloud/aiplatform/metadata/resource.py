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
import abc
import re
import proto
import logging
from typing import Optional

from google.api_core import exceptions
from google.cloud.aiplatform import utils
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base, initializer


class _Resource(base.AiPlatformResourceNounWithFutureManager, abc.ABC):
    """Metadata Resource for AI Platform"""

    client_class = utils.MetadataClientWithOverride
    _is_client_prediction_client = False
    _delete_method = None

    def __init__(
        self,
        resource_name: str,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing Metadata resource given a resource name or ID.

        Args:
            resource_name (str):
                A fully-qualified resource name or ID
                Example: "projects/123/locations/us-central1/metadataStores/default/{resource_noun}/my-resource".
                or "my-resource" when project and location are initialized or passed.
            metadata_store_id (str):
                MetadataStore to retrieve resource from. If not set, metadata_store_id is set to "default".
                If resource_name is a fully-qualified resource, its metadata_store_id overrides this one.
            project (str):
                Optional project to retrieve resource from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional location to retrieve resource from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to upload this model. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project, location=location, credentials=credentials,
        )

        # If we receive a full resource name, we extract the metadata_store_id and use that
        if resource_name.find("/") != -1:
            metadata_store_id = _Resource._extract_metadata_store_id(
                resource_name, self._resource_noun
            )

        full_resource_name = utils.full_resource_name(
            resource_name=resource_name,
            resource_noun=f"metadataStores/{metadata_store_id}/{self._resource_noun}",
            project=self.project,
            location=self.location,
        )

        self._gca_resource = getattr(self.api_client, self._getter_method)(
            name=full_resource_name
        )

    @classmethod
    def create(
        cls,
        resource_id: str,
        resource_noun: str,
        gapic_resource: proto.Message,
        metadata_store_id: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Creates a new Metadata resource.

        Args:
            resource_id (str):
                Required. The {resource_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/{resource_noun}/{resource_id}.
            resource_noun (str):
                Required. The resource noun to create the resource under.
            gapic_resource (proto.Message):
                Required. The gapic object used to construct the resource.
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/{resource_noun}/{resource_id}
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project to create this resource into. Overrides project set in
                aiplatform.init.
            location (str):
                Location to create this resource into. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to create this resource. Overrides
                credentials set in aiplatform.init.

        Returns:
            resource_name (str):
                The name of the instantiated resource.

        """
        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = (
            initializer.global_config.common_location_path(
                project=project, location=location
            )
            + f"/metadataStores/{metadata_store_id}"
        )

        try:
            cls.create_resource(
                client=api_client,
                parent=parent,
                resource=gapic_resource,
                resource_id=resource_id,
            )
        except exceptions.AlreadyExists:
            logging.info(f"Resource '{resource_id}' already exist")

        return f"{parent}/{resource_noun}/{resource_id}"

    @classmethod
    @abc.abstractmethod
    def create_resource(
        cls,
        client: utils.AiPlatformServiceClientWithOverride,
        parent: str,
        resource: proto.Message,
        resource_id: str,
    ) -> proto.Message:
        """Create resource method."""
        pass

    @classmethod
    def update(
        cls,
        resource_id: str,
        resource_noun: str,
        gapic_resource: proto.Message,
        metadata_store_id: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Updates an existing Metadata resource.

        Args:
            resource_id (str):
                Required. The {resource_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/{resource_noun}/{resource_id}.
            resource_noun (str):
                Required. The resource noun to update the resource under.
            gapic_resource (proto.Message):
                Required. The gapic object used to construct the resource.
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/{resource_noun}/{resource_id}
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project where this resource belongs. Overrides project set in
                aiplatform.init.
            location (str):
                Location where this resource belongs. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to update this resource. Overrides
                credentials set in aiplatform.init.

        Returns:
            resource_name (str):
                The name of the instantiated resource.

        """
        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = (
            initializer.global_config.common_location_path(
                project=project, location=location
            )
            + f"/metadataStores/{metadata_store_id}"
        )

        cls.update_resource(
            client=api_client, resource=gapic_resource,
        )

        return f"{parent}/{resource_noun}/{resource_id}"

    @classmethod
    @abc.abstractmethod
    def update_resource(
        cls, client: utils.AiPlatformServiceClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        """Update resource method."""
        pass

    @classmethod
    def _extract_metadata_store_id(cls, resource_name, resource_noun) -> str:
        """Extracts the metadata store id from the resource name.

        Args:
            resource_name (str):
                Required. A fully-qualified metadata resource name. For example
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/{resource_noun}/{resource_id}.
            resource_noun (str):
                Required. The resource_noun portion of the resource_name
        Returns:
            metadata_store_id (str):
                The metadata store id for the particular resource name.
        Raises:
            ValueError if it does not exist.
        """
        pattern = re.compile(
            r"^projects\/(?P<project>[\w-]+)\/locations\/(?P<location>[\w-]+)\/metadataStores\/(?P<store>[\w-]+)\/"
            + resource_noun
            + r"\/(?P<id>[\w-]+)$"
        )
        match = pattern.match(resource_name)
        if not match:
            raise ValueError(
                f"failed to extract metadata_store_id from resource {resource_name}"
            )
        return match["store"]
