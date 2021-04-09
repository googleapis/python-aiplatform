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
import proto
import logging
from typing import Optional, Dict

from google.api_core import exceptions
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.metadata.resource import _Resource
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform_v1beta1.types import context as gca_context


class _Context(_Resource):
    """Metadata Context resource for AI Platform"""

    _resource_noun = "contexts"
    _getter_method = "get_context"

    def __init__(
        self,
        context_name: str,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing Context given a Context name or ID.

        Args:
            context_name (str):
                A fully-qualified Context resource name or context ID
                Example: "projects/123/locations/us-central1/metadataStores/default/contexts/my-context".
                or "my-context" when project and location are initialized or passed.
            metadata_store_id (str):
                MetadataStore to retrieve resource from. If not set, metadata_store_id is set to "default".
                If context_name is a fully-qualified Context, its metadata_store_id overrides this one.
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
            resource_name=context_name,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    @classmethod
    def create(
        cls,
        context_id: str,
        schema_title: str,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = {},
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "_Context":
        """Creates a new Context resource.

        Args:
            context_id (str):
                Required. The {context_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/contexts/{context_id}.
            schema_title (str):
                Required. schema_title identifies the schema title used by the context.
            display_name (str):
                Optional. The user-defined name of the context.
            schema_version (str):
                Optional. schema_version specifies the version used by the context.
                If not set, defaults to use the latest version.
            description (str):
                Optional. Describes the purpose and content of the context resource to be created.
            metadata (Dict):
                Optional. metadata contains the metadata information that will be stored in the context resource.
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/contexts/{context_id}
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project to create this context into. Overrides project set in
                aiplatform.init.
            location (str):
                Location to create this context into. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to create this context. Overrides
                credentials set in aiplatform.init.

        Returns:
            context (_Context):
                Instantiated representation of the managed Metadata Context resource.

        """

        gapic_context = gca_context.Context(
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata,
        )

        resource_name = super().create(
            resource_id=context_id,
            resource_noun=cls._resource_noun,
            gapic_resource=gapic_context,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

        return cls(
            context_name=resource_name,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    @classmethod
    def create_resource(
        cls,
        client: utils.AiPlatformServiceClientWithOverride,
        parent: str,
        resource: proto.Message,
        resource_id: str,
    ) -> proto.Message:
        return client.create_context(
            parent=parent, context=resource, context_id=resource_id,
        )

    @classmethod
    def update(
        cls,
        context_id: str,
        metadata: Optional[Dict] = {},
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "_Artifact":
        f"""Updates a Context resource.

        Args:
            context_id (str):
                Required. The {context_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/contexts/{context_id}.
            metadata (Dict):
                Optional. metadata information to update the context with.
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/contexts/{context_id}
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project where this context belongs. Overrides project set in
                aiplatform.init.
            location (str):
                Location where this context belongs. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to update this context. Overrides
                credentials set in aiplatform.init.

        Returns:
            context (_Context):
                Updated representation of the managed Metadata Context resource.

        """

        gapic_context = cls(
            context_name=context_id,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )._gca_resource
        gapic_context.metadata = metadata

        resource_name = super().update(
            resource_id=context_id,
            resource_noun=cls._resource_noun,
            gapic_resource=gapic_context,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

        if not resource_name:
            raise ValueError("Error while updating context")

        return cls(
            context_name=resource_name,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    @classmethod
    def update_resource(
        cls, client: utils.AiPlatformServiceClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        return client.update_context(context=resource)

    @classmethod
    def get(
        cls,
        context_name: str,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "_Context":
        f"""Returns a Context resource.

        Args:
            context_name (str):
                A fully-qualified Context resource name or artifact ID
                Example: "projects/123/locations/us-central1/metadataStores/default/contexts/my-context".
                or "my-context" when project and location are initialized or passed.
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/contexts/my-context
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project to get this context into. Overrides project set in
                aiplatform.init.
            location (str):
                Location to get this context into. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to get this context. Overrides
                credentials set in aiplatform.init.

        Returns:
            context (_Context):
                Instantiated representation of the managed Metadata Context resource.

        """

        try:
            return cls(
                context_name=context_name,
                metadata_store_id=metadata_store_id,
                project=project,
                location=location,
                credentials=credentials,
            )._gca_resource
        except exceptions.NotFound:
            logging.info(f"Context {context_name} not found.")
