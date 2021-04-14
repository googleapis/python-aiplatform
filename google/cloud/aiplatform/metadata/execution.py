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
from typing import Optional, Dict

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.metadata.resource import _Resource
from google.cloud.aiplatform_v1beta1 import Event

from google.cloud.aiplatform_v1beta1.types import execution as gca_execution


class _Execution(_Resource):
    """Metadata Execution resource for AI Platform"""

    _resource_noun = "executions"
    _getter_method = "get_execution"

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
    def _update_resource(
        cls, client: utils.MetadataClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        return client.update_execution(execution=resource)

    @classmethod
    def add_artifact(
        cls,
        execution_id: str,
        artifact_id: str,
        input: bool,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Creates a new Metadata resource.

        Args:
            execution_id (str):
                Required. The <resource_id> portion of the Execution name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/<resource_noun>/<resource_id>.
            artifact_id (str):
                Required. The resource_ids of the Artifact to connect to the Execution through an Event.
            input (bool)
                Required. Whether Artifact is an input event to the Execution or not.
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
        """
        api_client = cls._instantiate_client(location=location, credentials=credentials)

        execution_resource_name = utils.full_resource_name(
            resource_name=execution_id,
            resource_noun=f"metadataStores/{metadata_store_id}/{cls._resource_noun}",
            project=project,
            location=location,
        )
        artifact_resource_name = utils.full_resource_name(
            resource_name=artifact_id,
            resource_noun=f"metadataStores/{metadata_store_id}/artifacts",
            project=project,
            location=location,
        )

        event = Event(
            artifact=artifact_resource_name,
            type_=Event.Type.INPUT if input else Event.Type.OUTPUT,
        )

        api_client.add_execution_events(
            execution=execution_resource_name, events=[event],
        )
