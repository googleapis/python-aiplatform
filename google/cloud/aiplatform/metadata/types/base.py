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
from typing import Optional, Dict
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.metadata import execution
from google.cloud.aiplatform import base

from google.cloud.aiplatform.metadata import constants

_LOGGER = base.Logger(__name__)


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
            self.resource_id = resource_name.split("/")[-1]

        self.uri = uri
        self.display_name = display_name
        self.schema_version = schema_version or constants._DEFAULT_SCHEMA_VERSION
        self.description = description
        self.metadata = metadata
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
            base_artifact=self,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
        return self.execution


class BaseExecutionSchema(object):
    """Base class for Metadata Execution schema.

    This is the base class for defining various execution types.

    Args:
        schema_title (str):
            Required. schema_title identifies the schema title used by the Execution.
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        resource_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
    """

    ARTIFACT_PROPERTY_KEY_RESOURCE_NAME = "resourceName"
    SCHEMA_TITLE = "system.ContainerExecution"

    def __init__(
        self,
        schema_title: Optional[str] = None,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        resource_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):

        """Initializes the Execution with the given name, URI and metadata."""
        self.schema_title = BaseExecutionSchema.SCHEMA_TITLE
        if schema_title:
            self.schema_title = schema_title
        self.resource_name = resource_name
        self.state = state

        self.resource_id = None
        if resource_name:
            # Temporary work around while Execution.create takes resource_id instead of resource_name
            self.resource_id = resource_name.split("/")[-1]

        self.display_name = display_name
        self.schema_version = schema_version or constants._DEFAULT_SCHEMA_VERSION
        self.metadata = metadata
        self.description = description
        self.kwargs = kwargs

    def create(
        self,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Creates a new Metadata Execution.

        Args:
            metadata_store_id (str):
                Optional. The <metadata_store_id> portion of the resource name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Optional. Project used to create this Execution. Overrides project set in
                aiplatform.init.
            location (str):
                Optional. Location used to create this Execution. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials used to create this Execution. Overrides
                credentials set in aiplatform.init.
        Returns:
            Execution: Instantiated representation of the managed Metadata Execution.

        """
        self.exectuion = execution.Execution.create(
            base_artifact=self,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
        return self.artifact
