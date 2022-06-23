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

from typing import Optional, Dict

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import execution
from google.cloud.aiplatform.metadata import metadata


class BaseExecutionSchema(object):
    """Base class for Metadata Execution schema."""

    SCHEMA_TITLE = "system.ContainerExecution"

    def __init__(
        self,
        schema_title: Optional[str] = None,
        state: gca_execution.Execution.State = gca_execution.Execution.State.RUNNING,
        resource_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
    ):

        """Initializes the Execution with the given name, URI and metadata.

        Args:
            schema_title (str):
                Required. schema_title identifies the schema title used by the Execution.
            state (gca_execution.Execution.State.RUNNING):
                Optional. State of this Execution. Defaults to RUNNING.
            resource_id (str):
                Optional. The <resource_id> portion of the Execution name with
                the following format, this is globally unique in a metadataStore.
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
            display_name (str):
                Optional. The user-defined name of the Execution.
            schema_version (str):
                Optional. schema_version specifies the version used by the Execution.
                If not set, defaults to use the latest version.
            metadata (Dict):
                Optional. Contains the metadata information that will be stored in the Execution.
            description (str):
                Optional. Describes the purpose of the Execution to be created.
        """
        self.schema_title = BaseExecutionSchema.SCHEMA_TITLE
        if schema_title:
            self.schema_title = schema_title
        self.state = state
        self.resource_id = resource_id
        self.display_name = display_name
        self.schema_version = schema_version or constants._DEFAULT_SCHEMA_VERSION
        self.metadata = metadata
        self.description = description

    def create(
        self,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "execution.Execution":
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
        self.execution = execution.Execution.create_from_base_execution_schema(
            base_execution_schema=self,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
        return self.execution

    def start_execution(
        self,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "execution.Execution":
        """Create and starts a new Metadata Execution.

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
        return metadata._ExperimentTracker().start_execution(
            base_execution_schema=self,
            resume=False,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
