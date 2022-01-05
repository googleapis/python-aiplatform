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

from typing import Optional, Dict

import proto

from google.api_core import exceptions
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import metadata_service
from google.cloud.aiplatform.metadata import resource
from google.cloud.aiplatform import utils

class _Artifact(resource._Resource):
    """Metadata Artifact resource for Vertex AI"""

    _resource_noun = "artifacts"
    _getter_method = "get_artifact"
    _delete_method = "delete_artifact"
    _parse_resource_name_method = "parse_artifact_path"
    _format_resource_name_method = "artifact_path"

    @classmethod
    def _create_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        resource_id: str,
        schema_title: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> proto.Message:
        gapic_artifact = gca_artifact.Artifact(
            uri=uri,
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
        )
        return client.create_artifact(
            parent=parent, artifact=gapic_artifact, artifact_id=resource_id,
        )

    @classmethod
    def _create(
        cls,
        resource_id: str,
        schema_title: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Creates a new Metadata resource.

        Args:
            resource_id (str):
                Required. The <resource_id> portion of the resource name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/<resource_noun>/<resource_id>.
            schema_title (str):
                Required. schema_title identifies the schema title used by the resource.
            display_name (str):
                Optional. The user-defined name of the resource.
            schema_version (str):
                Optional. schema_version specifies the version used by the resource.
                If not set, defaults to use the latest version.
            description (str):
                Optional. Describes the purpose of the resource to be created.
            metadata (Dict):
                Optional. Contains the metadata information that will be stored in the resource.
            metadata_store_id (str):
                The <metadata_store_id> portion of the resource name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/<resource_noun>/<resource_id>
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project used to create this resource. Overrides project set in
                aiplatform.init.
            location (str):
                Location used to create this resource. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials used to create this resource. Overrides
                credentials set in aiplatform.init.

        Returns:
            resource (_Resource):
                Instantiated representation of the managed Metadata resource.

        """
        api_client = cls._instantiate_client(location=location, credentials=credentials)

        parent = (
            initializer.global_config.common_location_path(
                project=project, location=location
            )
            + f"/metadataStores/{metadata_store_id}"
        )

        try:
            resource = cls._create_resource(
                client=api_client,
                parent=parent,
                resource_id=resource_id,
                schema_title=schema_title,
                uri=uri,
                display_name=display_name,
                schema_version=schema_version,
                description=description,
                metadata=metadata,
            )
        except exceptions.AlreadyExists:
            logging.info(f"Resource '{resource_id}' already exist")
            return

        return cls(
            resource=resource,
            project=project,
            location=location,
            credentials=credentials,
        )



    @classmethod
    def _update_resource(
        cls, client: utils.MetadataClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        """Update Artifacts with given input.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            resource (proto.Message):
                Required. The proto.Message which contains the update information for the resource.
        """

        return client.update_artifact(artifact=resource)

    @classmethod
    def _list_resources(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        filter: Optional[str] = None,
    ):
        """List artifacts in the parent path that matches the filter.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            parent (str):
                Required. The path where Artifacts are stored.
            filter (str):
                Optional. filter string to restrict the list result
        """
        list_request = metadata_service.ListArtifactsRequest(
            parent=parent, filter=filter,
        )
        return client.list_artifacts(request=list_request)
