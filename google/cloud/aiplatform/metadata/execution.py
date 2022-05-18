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
from typing import Any, Dict, List, Optional, Sequence, Union

import proto
from google.api_core import exceptions
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import utils, base, models
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.compat.types import metadata_service
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.metadata import metadata_store
from google.cloud.aiplatform.metadata import resource


class Execution(resource._Resource):
    """Metadata Execution resource for Vertex AI"""

    _resource_noun = "executions"
    _getter_method = "get_execution"
    _delete_method = "delete_execution"
    _parse_resource_name_method = "parse_execution_path"
    _format_resource_name_method = "execution_path"
    _list_method = 'list_executions'

    @property
    def state(self) -> gca_execution.Execution.State:
        return self._gca_resource.state

    @classmethod
    def create(cls,
               schema_title: str,
               *,
               state: gca_execution.Execution.State=gca_execution.Execution.State.RUNNING,
               schema_version: Optional[str] = None,
               metadata: Optional[Dict[str, Any]] = None,
               resource_id: Optional[str] = None,
               display_name: Optional[str] = None,
               project: Optional[str] = None,
               location: Optional[str] = None,
               credentials = Optional[auth_credentials.Credentials]) -> 'Execution':
        self = cls._empty_constructor(
            project=project,
            location=location,
            credentials=credentials)
        super(base.VertexAiResourceNounWithFutureManager, self).__init__()

        resource = Execution._create_resource(
            client=self.api_client,
            parent=metadata_store._MetadataStore._format_resource_name(
                project=self.project, location=self.location, metadata_store='default'
            ),
            schema_title=schema_title,
            resource_id=resource_id,
            metadata=metadata,
            display_name=display_name,
            schema_version=schema_version,
            state=state
        )
        self._gca_resource = resource

        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        state = gca_execution.Execution.State.FAILED if exc_type else gca_execution.Execution.State.COMPLETE
        self.update(state=state)

    def assign_input_artifacts(self, artifacts: List[Union[artifact.Artifact, models.Model]]):
        self._add_artifact(
            artifacts=artifacts,
            input=True)

    def assign_output_artifacts(self, artifacts: List[Union[artifact.Artifact, models.Model]]):
        self._add_artifact(
            artifacts=artifacts,
            input=False)

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
                    artifact.VertexResourceArtifactResolver.resolve_or_create_resource_artifact(a).resource_name)

        events = [gca_event.Event(
            artifact=artifact_resource_name,
            type_=gca_event.Event.Type.INPUT if input else gca_event.Event.Type.OUTPUT,
        ) for artifact_resource_name in artifact_resource_names]

        self.api_client.add_execution_events(
            execution=self.resource_name,
            events=events,
        )

    def query_input_and_output_artifacts(self) -> Sequence[artifact._Artifact]:
        """query the input and output artifacts connected to the execution.

        Returns:
              A Sequence of _Artifacts
        """

        try:
            artifacts = self.api_client.query_execution_inputs_and_outputs(
                execution=self.resource_name
            ).artifacts
        except exceptions.NotFound:
            return []

        return [
            artifact._Artifact(
                resource=metadata_artifact,
                project=self.project,
                location=self.location,
                credentials=self.credentials,
            )
            for metadata_artifact in artifacts
        ]

    def _get_artifacts(
        self, event_type: gca_event.Event.Type
    ) -> List[artifact.Artifact]:
        subgraph = self.api_client.query_execution_inputs_and_outputs(
            execution=self.resource_name
        )

        artifact_map = {artifact.name: artifact for artifact in subgraph.artifacts}

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
        return self._get_artifacts(event_type=gca_event.Event.Type.INPUT)

    def get_output_artifacts(self) -> List[artifact.Artifact]:
        return self._get_artifacts(event_type=gca_event.Event.Type.OUTPUT)

    @classmethod
    def _create_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        schema_title: str,
        state: gca_execution.Execution.State=gca_execution.Execution.State.RUNNING,
        resource_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> proto.Message:
        gapic_execution = gca_execution.Execution(
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
            state=state
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

        list_request = metadata_service.ListExecutionsRequest(
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

    def update(self,
               state: Optional[gca_execution.Execution.State]=None,
               description: Optional[str]=None,
               metadata: Optional[Dict[str, Any]]=None):

        gca_resource = deepcopy(self._gca_resource)
        if state:
            gca_resource.state = state
        if description:
            gca_resource.description = description
        self._nested_update_metadata(gca_resource=gca_resource, metadata=metadata)
        self._gca_resource=self._update_resource(self.api_client, resource=gca_resource)

