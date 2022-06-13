# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

from typing import Optional, Dict, Union

import proto

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import (
    metadata_service as gca_metadata_service,
)
from google.cloud.aiplatform.metadata import resource
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform.metadata import constants

_LOGGER = base.Logger(__name__)


class BaseArtifactType(object):
    """Base class for Metadata Artifact types.

    This is the base class for defining various artifact types, which can be
    passed to google.Artifact to create a corresponding resource.
    Artifacts carry a `metadata` field, which is a dictionary for storing
    metadata related to this artifact. Subclasses from ArtifactType can enforce
    various structure and field requiremetns for the metadata field.

     Args:
         schema_title (str):
             Required. schema_title identifies the schema title used by the Artifact.
         resource_name (str):
             The resource name of the Artifact following the format as follows.
             This is globally unique in a metadataStore:
             projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
         display_name (str):
             Optional. The user-defined name of the Artifact.
         schema_version (str):
             Optional. schema_version specifies the version used by the Artifact.
             If not set, defaults to use the latest version.
         description (str):
             Optional. Describes the purpose of the Artifact to be created.
         metadata (Dict):
             Optional. Contains the metadata information that will be stored in the Artifact.
    """

    ARTIFACT_PROPERTY_KEY_RESOURCE_NAME = "resourceName"
    SCHEMA_TITLE = "system.Artifact"

    def __init__(
        self,
        schema_title: str,
        resource_name: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):

        """Initializes the Artifact with the given name, URI and metadata."""
        self.schema_title = schema_title
        self.resource_name = resource_name

        self.resource_id = None
        if resource_name:
            # Temporary work around while Artifact.create takes resource_id instead of resource_name
            self.resource_id = resource_name.split("/")[-1]

        self.uri = uri
        self.display_name = display_name
        self.schema_version = schema_version or constants._DEFAULT_SCHEMA_VERSION
        self.description = description
        self.metadata = metadata


class Artifact(resource._Resource):
    """Metadata Artifact resource for Vertex AI"""

    def __init__(
        self,
        artifact_name: str,
        *,
        metadata_store_id: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing Metadata Artifact given a resource name or ID.

        Args:
            artifact_name (str):
                Required. A fully-qualified resource name or resource ID of the Artifact.
                Example: "projects/123/locations/us-central1/metadataStores/default/artifacts/my-resource".
                or "my-resource" when project and location are initialized or passed.
            metadata_store_id (str):
                Optional. MetadataStore to retrieve Artifact from. If not set, metadata_store_id is set to "default".
                If artifact_name is a fully-qualified resource, its metadata_store_id overrides this one.
            project (str):
                Optional. Project to retrieve the artifact from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve the Artifact from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Artifact. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            resource_name=artifact_name,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    _resource_noun = "artifacts"
    _getter_method = "get_artifact"
    _delete_method = "delete_artifact"
    _parse_resource_name_method = "parse_artifact_path"
    _format_resource_name_method = "artifact_path"
    _list_method = "list_artifacts"

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
    ) -> gca_artifact.Artifact:
        gapic_artifact = gca_artifact.Artifact(
            uri=uri,
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
            state=gca_artifact.Artifact.State.LIVE,
        )
        return client.create_artifact(
            parent=parent,
            artifact=gapic_artifact,
            artifact_id=resource_id,
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

        self = cls._empty_constructor(
            project=project, location=location, credentials=credentials
        )
        self._gca_resource = resource

        return self

    @classmethod
    def _update_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        resource: proto.Message,
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
        list_request = gca_metadata_service.ListArtifactsRequest(
            parent=parent,
            filter=filter,
        )
        return client.list_artifacts(request=list_request)

    @classmethod
    def create(
        cls,
        *,
        schema_title: Optional[str] = None,
        resource_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        base_artifact: Optional[BaseArtifactType] = None,
    ):
        """Creates a new Metadata Artifact.

        Args:
            schema_title (str):
                Optional. Either schema_title or base_artifact must be provided. Identifies the schema title used by the Artifact.
            resource_id (str):
                Optional. The <resource_id> portion of the Artifact name with
                the format. This is globally unique in a metadataStore:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
            display_name (str):
                Optional. The user-defined name of the Artifact.
            schema_version (str):
                Optional. schema_version specifies the version used by the Artifact.
                If not set, defaults to use the latest version.
            description (str):
                Optional. Describes the purpose of the Artifact to be created.
            metadata (Dict):
                Optional. Contains the metadata information that will be stored in the Artifact.
            metadata_store_id (str):
                Optional. The <metadata_store_id> portion of the resource name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Optional. Project used to create this Artifact. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location used to create this Artifact. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials used to create this Artifact. Overrides
                credentials set in aiplatform.init.
            base_artifact (BaseArtifactType):
                Optional. An instance of the BaseArtifactType class that can be provided instead of providing artifact specific parameters. It overrides
                the values provided for schema_title, resource_id, uri, display_name, schema_version, description, and metadata.

        Returns:
            Artifact: Instantiated representation of the managed Metadata Artifact.
        """
        if base_artifact:
            return cls._create(
                resource_id=base_artifact.resource_id,
                schema_title=base_artifact.schema_title,
                uri=base_artifact.uri,
                display_name=base_artifact.display_name,
                schema_version=base_artifact.schema_version,
                description=base_artifact.description,
                metadata=base_artifact.metadata,
                metadata_store_id=metadata_store_id,
                project=project,
                location=location,
                credentials=credentials,
            )
        # since base_artifact is not provided schema_title can not be emtpy.
        if not schema_title:
            raise ValueError(
                f"Either a base_artifact or the schema_title must be provided."
            )

        return cls._create(
            resource_id=resource_id,
            schema_title=schema_title,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=metadata,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    @property
    def uri(self) -> Optional[str]:
        "Uri for this Artifact."
        return self.gca_resource.uri

    @classmethod
    def get_with_uri(
        cls,
        uri: str,
        *,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Artifact":
        """Get an Artifact by it's uri.

        Args:
            uri(str):
                Required. Uri of the Artifact to retrieve.
            metadata_store_id (str):
                Optional. MetadataStore to retrieve Artifact from. If not set, metadata_store_id is set to "default".
                If artifact_name is a fully-qualified resource, its metadata_store_id overrides this one.
            project (str):
                Optional. Project to retrieve the artifact from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve the Artifact from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Artifact. Overrides
                credentials set in aiplatform.init.
        Returns:
            Artifact: Artifact with given uri.
        Raises:
            ValueError: If no Artifact exists with the provided uri.

        """

        matched_artifacts = cls.list(
            filter=f'uri = "{uri}"',
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

        if not matched_artifacts:
            raise ValueError(
                f"No artifact with uri {uri} is in the `{metadata_store_id}` MetadataStore."
            )

        if len(matched_artifacts) > 1:
            resource_names = "\n".join(a.resource_name for a in matched_artifacts)
            _LOGGER.warn(
                f"Mutiple artifacts with uri {uri} were found: {resource_names}"
            )
            _LOGGER.warn(f"Returning {matched_artifacts[0].resource_name}")

        return matched_artifacts[0]

    @property
    def lineage_console_uri(self) -> str:
        """Cloud console uri to view this Artifact Lineage."""
        metadata_store = self._parse_resource_name(self.resource_name)["metadata_store"]
        return f"https://console.cloud.google.com/vertex-ai/locations/{self.location}/metadata-stores/{metadata_store}/artifacts/{self.name}?project={self.project}"

    def __repr__(self) -> str:
        if self._gca_resource:
            return f"{object.__repr__(self)} \nresource name: {self.resource_name}\nuri: {self.uri}\nschema_title:{self.gca_resource.schema_title}"

        return base.FutureManager.__repr__(self)


class _VertexResourceArtifactResolver:

    _resource_to_artifact_type = {models.Model: "google.VertexModel"}

    @classmethod
    def supports_metadata(cls, resource: base.VertexAiResourceNoun) -> bool:
        """Returns True if Vertex resource is supported in Vertex Metadata otherwise False.

        Args:
            resource (base.VertexAiResourceNoun):
                Requried. Instance of Vertex AI Resource.
        Returns:
            True if Vertex resource is supported in Vertex Metadata otherwise False.
        """
        return type(resource) in cls._resource_to_artifact_type

    @classmethod
    def validate_resource_supports_metadata(cls, resource: base.VertexAiResourceNoun):
        """Validates Vertex resource is supported in Vertex Metadata.

        Args:
            resource (base.VertexAiResourceNoun):
                Required. Instance of Vertex AI Resource.
        Raises:
            ValueError: If Vertex AI Resource is not support in Vertex Metadata.
        """
        if not cls.supports_metadata(resource):
            raise ValueError(
                f"Vertex {type(resource)} is not supported in Vertex Metadata."
                f"Only {list(cls._resource_to_artifact_type.keys())} are supported"
            )

    @classmethod
    def resolve_vertex_resource(
        cls, resource: Union[models.Model]
    ) -> Optional[Artifact]:
        """Resolves Vertex Metadata Artifact that represents this Vertex Resource.

        Args:
            resource (base.VertexAiResourceNoun):
                Required. Instance of Vertex AI Resource.
        Returns:
            Artifact: Artifact that represents this Vertex Resource. None if Resource not found in Metadata store.
        """
        cls.validate_resource_supports_metadata(resource)
        resource.wait()
        metadata_type = cls._resource_to_artifact_type[type(resource)]
        uri = metadata_utils.make_gcp_resource_url(resource=resource)

        artifacts = Artifact.list(
            filter=metadata_utils._make_filter_string(
                schema_title=metadata_type,
                uri=uri,
            ),
            project=resource.project,
            location=resource.location,
            credentials=resource.credentials,
        )

        artifacts.sort(key=lambda a: a.create_time)
        if artifacts:
            # most recent
            return artifacts[-1]

    @classmethod
    def create_vertex_resource_artifact(cls, resource: Union[models.Model]) -> Artifact:
        """Creates Vertex Metadata Artifact that represents this Vertex Resource.

        Args:
            resource (base.VertexAiResourceNoun):
                Required. Instance of Vertex AI Resource.
        Returns:
            Artifact: Artifact that represents this Vertex Resource.
        """
        cls.validate_resource_supports_metadata(resource)
        resource.wait()
        metadata_type = cls._resource_to_artifact_type[type(resource)]
        uri = metadata_utils.make_gcp_resource_url(resource=resource)

        return Artifact.create(
            schema_title=metadata_type,
            display_name=getattr(resource.gca_resource, "display_name", None),
            uri=uri,
            metadata={"resourceName": resource.resource_name},
            project=resource.project,
            location=resource.location,
            credentials=resource.credentials,
        )

    @classmethod
    def resolve_or_create_resource_artifact(
        cls, resource: Union[models.Model]
    ) -> Artifact:
        """Create of gets Vertex Metadata Artifact that represents this Vertex Resource.

        Args:
            resource (base.VertexAiResourceNoun):
                Required. Instance of Vertex AI Resource.
        Returns:
            Artifact: Artifact that represents this Vertex Resource.
        """
        artifact = cls.resolve_vertex_resource(resource=resource)
        if artifact:
            return artifact
        return cls.create_vertex_resource_artifact(resource=resource)
