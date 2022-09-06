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

import abc

from typing import Optional, Dict

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.constants import base as base_constants
from google.cloud.aiplatform.metadata import constants


class BaseArtifactSchema(artifact.Artifact):
    """Base class for Metadata Artifact types."""

    @property
    @classmethod
    @abc.abstractmethod
    def schema_title(cls) -> str:
        """Identifies the Vertex Metadta schema title used by the resource."""
        pass

    def __init__(
        self,
        *,
        artifact_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):

        """Initializes the Artifact with the given name, URI and metadata.

        This is the base class for defining various artifact types, which can be
        passed to google.Artifact to create a corresponding resource.
        Artifacts carry a `metadata` field, which is a dictionary for storing
        metadata related to this artifact. Subclasses from ArtifactType can enforce
        various structure and field requirements for the metadata field.

        Args:
            resource_id (str):
                Optional. The <resource_id> portion of the Artifact name with
                the following format, this is globally unique in a metadataStore:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
            uri (str):
                Optional. The uniform resource identifier of the artifact file. May be empty if there is no actual
                artifact file.
            display_name (str):
                Optional. The user-defined name of the Artifact.
            schema_version (str):
                Optional. schema_version specifies the version used by the Artifact.
                If not set, defaults to use the latest version.
            description (str):
                Optional. Describes the purpose of the Artifact to be created.
            metadata (Dict):
                Optional. Contains the metadata information that will be stored in the Artifact.
            state (google.cloud.gapic.types.Artifact.State):
                Optional. The state of this Artifact. This is a
                property of the Artifact, and does not imply or
                capture any ongoing process. This property is
                managed by clients (such as Vertex AI
                Pipelines), and the system does not prescribe or
                check the validity of state transitions.
        """
        # resource_id is not stored in the proto. Create method uses the
        # resource_id along with project_id and location to construct an
        # resource_name which is stored in the proto message.
        self.artifact_id = artifact_id

        # Store all other attributes using the proto structure.
        self._gca_resource = gca_artifact.Artifact()
        self._gca_resource.uri = uri
        self._gca_resource.display_name = display_name
        self._gca_resource.schema_version = (
            schema_version or constants._DEFAULT_SCHEMA_VERSION
        )
        self._gca_resource.description = description

        # If metadata is None covert to {}
        metadata = metadata if metadata else {}
        self._nested_update_metadata(self._gca_resource, metadata)
        self._gca_resource.state = state

    # TODO() Switch to @singledispatchmethod constructor overload after py>=3.8
    def _init_with_resource_name(
        self,
        *,
        artifact_name: str,
    ):

        """Initializes the Artifact instance using an existing resource.

        Args:
            artifact_name (str):
                Artifact name with the following format, this is globally unique in a metadataStore:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        """
        # Add User Agent Header for metrics tracking if one is not specified
        # If one is already specified this call was initiated by a sub class.
        if not base_constants.USER_AGENT_SDK_COMMAND:
            base_constants.USER_AGENT_SDK_COMMAND = "aiplatform.metadata.schema.base_artifact.BaseArtifactSchema._init_with_resource_name"

        super(BaseArtifactSchema, self).__init__(artifact_name=artifact_name)

    def create(
        self,
        *,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "artifact.Artifact":
        """Creates a new Metadata Artifact.

        Args:
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
        Returns:
            Artifact: Instantiated representation of the managed Metadata Artifact.
        """
        # Add User Agent Header for metrics tracking.
        base_constants.USER_AGENT_SDK_COMMAND = (
            "aiplatform.metadata.schema.base_artifact.BaseArtifactSchema.create"
        )

        # Check if metadata exists to avoid proto read error
        metadata = None
        if self._gca_resource.metadata:
            metadata = self.metadata

        new_artifact_instance = artifact.Artifact.create(
            resource_id=self.artifact_id,
            schema_title=self.schema_title,
            uri=self.uri,
            display_name=self.display_name,
            schema_version=self.schema_version,
            description=self.description,
            metadata=metadata,
            state=self.state,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

        # Reinstantiate this class using the newly created resource.
        self._init_with_resource_name(artifact_name=new_artifact_instance.resource_name)
        return self
