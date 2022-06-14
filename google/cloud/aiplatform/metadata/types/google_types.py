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
from typing import Optional, Dict, NamedTuple, List
from dataclasses import dataclass
from google.cloud.aiplatform.metadata.types import base
from google.cloud.aiplatform.metadata.types import utils


class VertexDataset(base.BaseArtifactSchema):
    """An artifact representing a Vertex Dataset."""

    SCHEMA_TITLE = "google.VertexDataset"

    def __init__(
        self,
        dataset_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs,
    ):
        """Args:
        dataset_name (str):
            Optional. The name of the Dataset resource, in a form of
            projects/{project}/locations/{location}/datasets/{datasets_name}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.datasets/get
        uri (str):
            Optional. The URI for the assets of this Artifact.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = dataset_name
        super(VertexDataset, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=dataset_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class VertexModel(base.BaseArtifactSchema):
    """An artifact representing a Vertex Model."""

    SCHEMA_TITLE = "google.VertexModel"

    def __init__(
        self,
        vertex_model_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs,
    ):
        """Args:
        vertex_model_name (str):
            Optional. The name of the VertexModel resource, in a form of
            projects/{project}/locations/{location}/models/{model}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.models/get
        uri (str):
            Optional. The URI for the assets of this Artifact.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
        """

        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = vertex_model_name

        super(VertexModel, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=vertex_model_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class VertexEndpoint(base.BaseArtifactSchema):
    """An artifact representing a Vertex Endpoint."""

    SCHEMA_TITLE = "google.VertexEndpoint"

    def __init__(
        self,
        vertex_endpoint_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs,
    ):
        """Args:
        vertex_endpoint_name (str):
            Optional. The name of the VertexEndpoint resource, in a form of
            projects/{project}/locations/{location}/endpoints/{endpoint}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/get
        uri (str):
            Optional. The URI for the assets of this Artifact.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = vertex_endpoint_name

        super(VertexEndpoint, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=vertex_endpoint_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class UnmanagedContainerModel(base.BaseArtifactSchema):
    """An artifact representing a Vertex Unmanaged Container Model."""

    SCHEMA_TITLE = "google.UnmanagedContainerModel"

    def __init__(
        self,
        predict_schema_ta: utils.PredictSchemata,
        container_spec: utils.PredictSchemata,
        unmanaged_container_model_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs,
    ):
        """Args:
        predict_schema_ta (PredictSchemata):
            An instance of PredictSchemata which holds instance, parameter and prediction schema uris.
        container_spec (ContainerSpec):
            An instance of ContainerSpec which holds the container configuration for the model.
        unmanaged_container_model_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        uri (str):
            Optional. The URI for the assets of this Artifact.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = unmanaged_container_model_name
        extended_metadata["predictSchemata"] = predict_schema_ta.to_dict()
        extended_metadata["containerSpec"] = container_spec.to_dict()

        super(UnmanagedContainerModel, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=unmanaged_container_model_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )
 