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
from copy import deepcopy
from typing import Any, Dict, List, Optional, Union

import proto
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.compat.types import (
    metadata_service as gca_metadata_service,
)
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.metadata import metadata_store
from google.cloud.aiplatform.metadata import resource
from google.cloud.aiplatform.metadata.schema import base_execution


class Execution(resource._Resource):
    """Metadata Execution resource for Vertex AI"""

    _resource_noun = "executions"
    _getter_method = "get_execution"
    _delete_method = "delete_execution"
    _parse_resource_name_method = "parse_execution_path"
    _format_resource_name_method = "execution_path"
    _list_method = "list_executions"

    def __init__(
        self,
        execution_name: str,
        *,
        metadata_store_id: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing Metadata Execution given a resource name or ID.

        Args:
            execution_name (str):
                Required. A fully-qualified resource name or resource ID of the Execution.
                Example: "projects/123/locations/us-central1/metadataStores/default/executions/my-resource".
                or "my-resource" when project and location are initialized or passed.
            metadata_store_id (str):
                Optional. MetadataStore to retrieve Execution from. If not set, metadata_store_id is set to "default".
                If execution_name is a fully-qualified resource, its metadata_store_id overrides this one.
            project (str):
                Optional. Project to retrieve the artifact from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve the Execution from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this Execution. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            resource_name=execution_name,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    @property
    def state(self) -> gca_execution.Execution.State:
        """State of this Execution."""
        return self._gca_resource.state

    @classmethod
    def create(
        cls,
        schema_title: str,
        *,
        state: gca_execution.Execution.State = gca_execution.Execution.State.RUNNING,
        resource_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        description: Optional[str] = None,
        metadata_store_id: str = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials=Optional[auth_credentials.Credentials],
    ) -> "Execution":
        """
        Creates a new Metadata Execution.

        Args:
            schema_title (str):
                Required. schema_title identifies the schema title used by the Execution.
            state (gca_execution.Execution.State.RUNNING):
                Optional. State of this Execution. Defaults to RUNNING.
            resource_id (str):
                Optional. The <resource_id> portion of the Execution name with
                the format. This is globally unique in a metadataStore:
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
            metadata_store_id (str):
                Optional. The <metadata_store_id> portion of the resource name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>
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
        self = cls._empty_constructor(
            project=project, location=location, credentials=credentials
        )
        super(base.VertexAiResourceNounWithFutureManager, self).__init__()

        resource = Execution._create_resource(
            client=self.api_client,
            parent=metadata_store._MetadataStore._format_resource_name(
                project=self.project,
                location=self.location,
                metadata_store=metadata_store_id,
            ),
            schema_title=schema_title,
            resource_id=resource_id,
            metadata=metadata,
            description=description,
            display_name=display_name,
            schema_version=schema_version,
            state=state,
        )
        self._gca_resource = resource

        return self

    @classmethod
    def create_from_base_execution_schema(
        cls,
        *,
        base_execution_schema: "base_execution.BaseExecutionSchema",
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Execution":
        """
        Creates a new Metadata Execution.

        Args:
            base_execution_schema (BaseExecutionSchema):
                An instance of the BaseExecutionSchema class that can be
                provided instead of providing schema specific parameters.
            metadata_store_id (str):
                Optional. The <metadata_store_id> portion of the resource name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>
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
        resource = Execution.create(
            state=base_execution_schema.state,
            schema_title=base_execution_schema.schema_title,
            resource_id=base_execution_schema.execution_id,
            display_name=base_execution_schema.display_name,
            schema_version=base_execution_schema.schema_version,
            metadata=base_execution_schema.metadata,
            description=base_execution_schema.description,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )
        return resource

    def __enter__(self):
        if self.state is not gca_execution.Execution.State.RUNNING:
            self.update(state=gca_execution.Execution.State.RUNNING)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = (
            gca_execution.Execution.State.FAILED
            if exc_type
            else gca_execution.Execution.State.COMPLETE
        )
        self.update(state=state)

    def assign_input_artifacts(
        self, artifacts: List[Union[artifact.Artifact, models.Model]]
    ):
        """Assigns Artifacts as inputs to this Executions.

        Args:
            artifacts (List[Union[artifact.Artifact, models.Model]]):
                Required. Artifacts to assign as input.
        """
        self._add_artifact(artifacts=artifacts, input=True)

    def assign_output_artifacts(
        self, artifacts: List[Union[artifact.Artifact, models.Model]]
    ):
        """Assigns Artifacts as outputs to this Executions.

        Args:
            artifacts (List[Union[artifact.Artifact, models.Model]]):
                Required. Artifacts to assign as input.
        """
        self._add_artifact(artifacts=artifacts, input=False)

    def _add_artifact(
        self,
        artifacts: List[Union[artifact.Artifact, models.Model]],
        input: bool,
    ):
        """Connect Artifact to a given Execution.

        Args:
            artifact_resource_names (List[str]):
                Required. The full resource name of the Artifact to connect to the Execution through an Event.
            input (bool)
                Required. Whether Artifact is an input event to the Execution or not.
        """

        artifact_resource_names = []
        for a in artifacts:
            if isinstance(a, artifact.Artifact):
                artifact_resource_names.append(a.resource_name)
            else:
                artifact_resource_names.append(
                    artifact._VertexResourceArtifactResolver.resolve_or_create_resource_artifact(
                        a
                    ).resource_name
                )

        events = [
            gca_event.Event(
                artifact=artifact_resource_name,
                type_=gca_event.Event.Type.INPUT
                if input
                else gca_event.Event.Type.OUTPUT,
            )
            for artifact_resource_name in artifact_resource_names
        ]

        self.api_client.add_execution_events(
            execution=self.resource_name,
            events=events,
        )

    def _get_artifacts(
        self, event_type: gca_event.Event.Type
    ) -> List[artifact.Artifact]:
        """Get Executions input or output Artifacts.

        Args:
            event_type (gca_event.Event.Type):
                Required. The Event type, input or output.
        Returns:
            List of Artifacts.
        """
        subgraph = self.api_client.query_execution_inputs_and_outputs(
            execution=self.resource_name
        )

        artifact_map = {
            artifact_metadata.name: artifact_metadata
            for artifact_metadata in subgraph.artifacts
        }

        gca_artifacts = [
            artifact_map[event.artifact]
            for event in subgraph.events
            if event.type_ == event_type
        ]

        artifacts = []
        for gca_artifact in gca_artifacts:
            this_artifact = artifact.Artifact._empty_constructor(
                project=self.project,
                location=self.location,
                credentials=self.credentials,
            )
            this_artifact._gca_resource = gca_artifact
            artifacts.append(this_artifact)

        return artifacts

    def get_input_artifacts(self) -> List[artifact.Artifact]:
        """Get the input Artifacts of this Execution.

        Returns:
            List of input Artifacts.
        """
        return self._get_artifacts(event_type=gca_event.Event.Type.INPUT)

    def get_output_artifacts(self) -> List[artifact.Artifact]:
        """Get the output Artifacts of this Execution.

        Returns:
            List of output Artifacts.
        """
        return self._get_artifacts(event_type=gca_event.Event.Type.OUTPUT)

    @classmethod
    def _create_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        schema_title: str,
        state: gca_execution.Execution.State = gca_execution.Execution.State.RUNNING,
        resource_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> gca_execution.Execution:
        """
        Creates a new Metadata Execution.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. Instantiated Metadata Service Client.
            parent (str):
                Required: MetadataStore parent in which to create this Execution.
            schema_title (str):
                Required. schema_title identifies the schema title used by the Execution.
            state (gca_execution.Execution.State):
                Optional. State of this Execution. Defaults to RUNNING.
            resource_id (str):
                Optional. The {execution} portion of the resource name with the
                format:
                ``projects/{project}/locations/{location}/metadataStores/{metadatastore}/executions/{execution}``
                If not provided, the Execution's ID will be a UUID generated
                by the service. Must be 4-128 characters in length. Valid
                characters are ``/[a-z][0-9]-/``. Must be unique across all
                Executions in the parent MetadataStore. (Otherwise the
                request will fail with ALREADY_EXISTS, or PERMISSION_DENIED
                if the caller can't view the preexisting Execution.)
            display_name (str):
                Optional. The user-defined name of the Execution.
            schema_version (str):
                Optional. schema_version specifies the version used by the Execution.
                If not set, defaults to use the latest version.
            description (str):
                Optional. Describes the purpose of the Execution to be created.
            metadata (Dict):
                Optional. Contains the metadata information that will be stored in the Execution.

        Returns:
            Execution: Instantiated representation of the managed Metadata Execution.

        """
        gapic_execution = gca_execution.Execution(
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
            state=state,
        )
        return client.create_execution(
            parent=parent,
            execution=gapic_execution,
            execution_id=resource_id,
        )

    @classmethod
    def _list_resources(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        filter: Optional[str] = None,
    ):
        """List Executions in the parent path that matches the filter.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            parent (str):
                Required. The path where Executions are stored.
            filter (str):
                Optional. filter string to restrict the list result
        """

        list_request = gca_metadata_service.ListExecutionsRequest(
            parent=parent,
            filter=filter,
        )
        return client.list_executions(request=list_request)

    @classmethod
    def _update_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        resource: proto.Message,
    ) -> proto.Message:
        """Update Executions with given input.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            resource (proto.Message):
                Required. The proto.Message which contains the update information for the resource.
        """

        return client.update_execution(execution=resource)

    def update(
        self,
        state: Optional[gca_execution.Execution.State] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Update this Execution.

        Args:
            state (gca_execution.Execution.State):
                    Optional. State of this Execution.
            description (str):
                Optional. Describes the purpose of the Execution to be created.
            metadata (Dict[str, Any):
                Optional. Contains the metadata information that will be stored in the Execution.
        """

        gca_resource = deepcopy(self._gca_resource)
        if state:
            gca_resource.state = state
        if description:
            gca_resource.description = description
        self._nested_update_metadata(gca_resource=gca_resource, metadata=metadata)
        self._gca_resource = self._update_resource(
            self.api_client, resource=gca_resource
        )
