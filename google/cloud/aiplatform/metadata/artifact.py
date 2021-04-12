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

from google.cloud.aiplatform import utils
from google.cloud.aiplatform.metadata.resource import _Resource
from google.auth import credentials as auth_credentials

from google.cloud.aiplatform_v1beta1.types import artifact as gca_artifact


class _Artifact(_Resource):
    """Metadata Artifact resource for AI Platform"""

    _resource_noun = "artifacts"
    _getter_method = "get_artifact"

    @classmethod
    def create(
        cls,
        artifact_id: str,
        schema_title: str,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        metadata_store_id: Optional[str] = "default",
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "_Artifact":
        f"""Creates a new Artifact resource.

        Args:
            artifact_id (str):
                Required. The {artifact_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/artifacts/{artifact_id}.
            schema_title (str):
                Required. schema_title identifies the schema title used by the artifact.
            display_name (str):
                Optional. The user-defined name of the artifact.
            schema_version (str):
                Optional. schema_version specifies the version used by the artifact.
                If not set, defaults to use the latest version.
            description (str):
                Optional. Describes the purpose and content of the artifact resource to be created.
            metadata (Dict):
                Optional. metadata contains the metadata information that will be stored in the artifact resource.
            metadata_store_id (str):
                The {metadata_store_id} portion of the resource name with
                the format:
                projects/{project}/locations/{location}/metadataStores/{metadata_store_id}/artifacts/{artifact_id}
                If not provided, the MetadataStore's ID will be set to "default".
            project (str):
                Project to create this artifact into. Overrides project set in
                aiplatform.init.
            location (str):
                Location to create this artifact into. Overrides location set in
                aiplatform.init.
            credentials (auth_credentials.Credentials):
                Custom credentials to use to create this artifact. Overrides
                credentials set in aiplatform.init.

        Returns:
            artifact (_Artifact):
                Instantiated representation of the managed Metadata Artifact resource.

        """

        gapic_artifact = gca_artifact.Artifact(
            schema_title=schema_title,
            schema_version=schema_version,
            display_name=display_name,
            description=description,
            metadata=metadata if metadata else {},
        )

        resource_name = super().create(
            resource_id=artifact_id,
            resource_noun=cls._resource_noun,
            gapic_resource=gapic_artifact,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

        return cls(
            resource_name=resource_name,
            metadata_store_id=metadata_store_id,
            project=project,
            location=location,
            credentials=credentials,
        )

    @classmethod
    def _create_resource(
        cls,
        client: utils.MetadataClientWithOverride,
        parent: str,
        resource: proto.Message,
        resource_id: str,
    ) -> proto.Message:
        return client.create_artifact(
            parent=parent, artifact=resource, artifact_id=resource_id,
        )

    @classmethod
    def _update_resource(
        cls, client: utils.MetadataClientWithOverride, resource: proto.Message,
    ) -> proto.Message:
        return client.update_artifact(artifact=resource)
