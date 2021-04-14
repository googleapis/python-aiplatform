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
from typing import Optional, Dict, Sequence

from google.cloud.aiplatform import utils, initializer
from google.cloud.aiplatform.metadata.resource import _Resource

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform_v1beta1.types import context as gca_context


class _Context(_Resource):
    """Metadata Context resource for AI Platform"""

    _resource_noun = "contexts"
    _getter_method = "get_context"

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
        gapic_context = gca_context.Context(
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
        )
        return client.create_context(
            parent=parent, context=gapic_context, context_id=resource_id,
        )

    @classmethod
    def _update_resource(
        cls, client: utils.MetadataClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        return client.update_context(context=resource)

    @classmethod
    def add_artifacts_or_executions(
        cls,
        context_id: str,
        artifact_ids: Optional[Sequence[str]] = None,
        execution_ids: Optional[Sequence[str]] = None,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Creates a new Metadata resource.

        Args:
            context_id (str):
                Required. The <resource_id> portion of the context name with
                the format:
                projects/123/locations/us-central1/metadataStores/<metadata_store_id>/<resource_noun>/<resource_id>.
            artifact_ids (Sequence[str]):
                Optional. The resource_ids of the Artifacts to attribute to the Context.
            execution_ids (Sequence[str]):
                Optional. The resource_ids of the Executions to associate with the Context.
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

        context_resource_name = utils.full_resource_name(
            resource_name=context_id,
            resource_noun=f"metadataStores/{metadata_store_id}/{cls._resource_noun}",
            project=project,
            location=location,
        )

        artifact_resource_names = None
        execution_resource_names = None
        if artifact_ids is not None:
            artifact_resource_names = list(
                map(
                    lambda x: utils.full_resource_name(
                        resource_name=x,
                        resource_noun=f"metadataStores/{metadata_store_id}/artifacts",
                        project=project,
                        location=location,
                    ),
                    artifact_ids,
                )
            )
        if execution_ids is not None:
            execution_resource_names = list(
                map(
                    lambda x: utils.full_resource_name(
                        resource_name=x,
                        resource_noun=f"metadataStores/{metadata_store_id}/executions",
                        project=project,
                        location=location,
                    ),
                    execution_ids,
                )
            )

        api_client.add_context_artifacts_and_executions(
            context=context_resource_name,
            artifacts=artifact_resource_names,
            executions=execution_resource_names,
        )
