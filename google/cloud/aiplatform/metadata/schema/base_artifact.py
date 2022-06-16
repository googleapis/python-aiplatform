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

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from typing import Optional, Dict


class BaseArtifactSchema(object):
    """Base class for Metadata Artifact types.

    This is the base class for defining various artifact types, which can be
    passed to google.Artifact to create a corresponding resource.
    Artifacts carry a `metadata` field, which is a dictionary for storing
    metadata related to this artifact. Subclasses from ArtifactType can enforce
    various structure and field requirements for the metadata field.

    Args:
        schema_title (str):
            Optional. The schema title used by the Artifact, defaults to "system.Artifact"
        resource_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
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
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
    """

    ARTIFACT_PROPERTY_KEY_RESOURCE_NAME = "resourceName"
    SCHEMA_TITLE = "system.Artifact"

    def __init__(
        self,
        schema_title: Optional[str] = None,
        resource_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
        **kwargs,
    ):

        """Initializes the Artifact with the given name, URI and metadata."""
        self.schema_title = BaseArtifactSchema.SCHEMA_TITLE
        if schema_title:
            self.schema_title = schema_title
        self.resource_name = resource_name

        self.resource_id = None
        if resource_name:
            # Temporary work around while Artifact.create takes resource_id instead of resource_name
            # TODO: switch to using resouce_name only when create resouce supports it.
            self.resource_id = resource_name.split("/")[-1]

        self.uri = uri
        self.display_name = display_name
        self.schema_version = schema_version or constants._DEFAULT_SCHEMA_VERSION
        self.description = description
        self.metadata = metadata
        self.state = state
        self.kwargs = kwargs

    def create(
        self,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
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
        self.artifact = artifact.Artifact.create(
            base_artifact_schema=self,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
        return self.artifact
