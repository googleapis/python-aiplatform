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

from typing import Optional, Dict, Sequence

import proto
from google.api_core import exceptions

from google.cloud.aiplatform import utils
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.resource import _Resource
from google.cloud.aiplatform_v1beta1 import Event
from google.cloud.aiplatform_v1beta1.types import execution as gca_execution
from google.cloud.aiplatform_v1beta1.types.metadata_service import ListExecutionsRequest


class _Execution(_Resource):
    """Metadata Execution resource for AI Platform"""

    _resource_noun = "executions"
    _getter_method = "get_execution"

    def add_artifact(
        self, artifact_resource_name: str, input: bool,
    ):
        """Connect Artifact to a given Execution.

        Args:
            artifact_resource_name (str):
                Required. The full resource name of the Artifact to connect to the Execution through an Event.
            input (bool)
                Required. Whether Artifact is an input event to the Execution or not.
        """

        event = Event(
            artifact=artifact_resource_name,
            type_=Event.Type.INPUT if input else Event.Type.OUTPUT,
        )

        self.api_client.add_execution_events(
            execution=self.resource_name, events=[event],
        )

    def query_input_and_output_artifacts(self) -> Sequence[_Artifact]:
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
            _Artifact(
                resource=artifact,
                project=self.project,
                location=self.location,
                credentials=self.credentials,
            )
            for artifact in artifacts
        ]

    @classmethod
    def _create_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        resource_id: str,
        schema_title: str,
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
        )
        return client.create_execution(
            parent=parent, execution=gapic_execution, execution_id=resource_id,
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

        list_request = ListExecutionsRequest(parent=parent, filter=filter,)
        return client.list_executions(request=list_request)

    @classmethod
    def _update_resource(
        cls, client: utils.MetadataClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        """Update Executions with given input.

        Args:
            client (utils.MetadataClientWithOverride):
                Required. client to send require to Metadata Service.
            resource (proto.Message):
                Required. The proto.Message which contains the update information for the resource.
        """

        return client.update_execution(execution=resource)
