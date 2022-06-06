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
from typing import Optional, Dict
from google.cloud.aiplatform.metadata import artifact


class VertexDataset(artifact.BaseArtifactType):
    """An artifact representing a Vertex Dataset."""

    def __init__(
        self,
        dataset_resource_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        dataset_resource_name: Optional[str] = None,
    ):
        """Args:
        schema_title (str):
            Required. schema_title identifies the schema title used by the Artifact.
        dataset_resource_id (str):
            The name of the Dataset resource, in a form of
            projects/{project}/locations/{location}/datasets/{datasets_name}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.datasets/get
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        SCHEMA_TITLE = "google.VertexDataset"
        super(VertexDataset, self).__init__(
            schema_title=SCHEMA_TITLE,
            resource_id=dataset_resource_id,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata={
                artifact.BaseArtifactType.ARTIFACT_PROPERTY_KEY_RESOURCE_NAME: dataset_resource_name
            },
        )
