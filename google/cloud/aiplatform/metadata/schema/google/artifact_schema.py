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

from typing import Optional, Dict

from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.metadata.schema import base_artifact
from google.cloud.aiplatform.metadata.schema import utils

# The artifact property key for the resource_name
_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME = "resourceName"


class VertexDataset(base_artifact.BaseArtifactSchema):
    """An artifact representing a Vertex Dataset."""

    schema_title = "google.VertexDataset"

    def __init__(
        self,
        *,
        dataset_name: str,
        uri: str,
        artifact_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        dataset_name (str):
            The name of the Dataset resource, in a form of
            projects/{project}/locations/{location}/datasets/{dataset}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.datasets/get
        uri (str):
            The Vertex Dataset resource uri, in a form of
            https://{service-endpoint}/v1/{dataset_name},
            where {service-endpoint} is one of the supported service endpoints at
            https://cloud.google.com/vertex-ai/docs/reference/rest#rest_endpoints
        artifact_id (str):
            Optional. The <resource_id> portion of the Artifact name with
            the format. This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}
        extended_metadata[_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME] = dataset_name

        super(VertexDataset, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class VertexModel(base_artifact.BaseArtifactSchema):
    """An artifact representing a Vertex Model."""

    schema_title = "google.VertexModel"

    def __init__(
        self,
        *,
        vertex_model_name: str,
        uri: str,
        artifact_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        vertex_model_name (str):
            The name of the Model resource, in a form of
            projects/{project}/locations/{location}/models/{model}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.models/get
        uri (str):
            The Vertex Model resource uri, in a form of
            https://{service-endpoint}/v1/{vertex_model_name},
            where {service-endpoint} is one of the supported service endpoints at
            https://cloud.google.com/vertex-ai/docs/reference/rest#rest_endpoints
        artifact_id (str):
            Optional. The <resource_id> portion of the Artifact name with
            the format. This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}
        extended_metadata[_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME] = vertex_model_name

        super(VertexModel, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class VertexEndpoint(base_artifact.BaseArtifactSchema):
    """An artifact representing a Vertex Endpoint."""

    schema_title = "google.VertexEndpoint"

    def __init__(
        self,
        *,
        vertex_endpoint_name: str,
        uri: str,
        artifact_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        vertex_endpoint_name (str):
            The name of the Endpoint resource, in a form of
            projects/{project}/locations/{location}/endpoints/{endpoint}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/get
        uri (str):
            The Vertex Endpoint resource uri, in a form of
            https://{service-endpoint}/v1/{vertex_endpoint_name},
            where {service-endpoint} is one of the supported service endpoints at
            https://cloud.google.com/vertex-ai/docs/reference/rest#rest_endpoints
        artifact_id (str):
            Optional. The <resource_id> portion of the Artifact name with
            the format. This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}

        extended_metadata[_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME] = vertex_endpoint_name

        super(VertexEndpoint, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class UnmanagedContainerModel(base_artifact.BaseArtifactSchema):
    """An artifact representing a Vertex Unmanaged Container Model."""

    schema_title = "google.UnmanagedContainerModel"

    def __init__(
        self,
        *,
        predict_schema_ta: utils.PredictSchemata,
        container_spec: utils.ContainerSpec,
        artifact_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        predict_schema_ta (PredictSchemata):
            An instance of PredictSchemata which holds instance, parameter and prediction schema uris.
        container_spec (ContainerSpec):
            An instance of ContainerSpec which holds the container configuration for the model.
        artifact_id (str):
            Optional. The <resource_id> portion of the Artifact name with
            the format. This is globally unique in a metadataStore:
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
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}
        extended_metadata["predictSchemata"] = predict_schema_ta.to_dict()
        extended_metadata["containerSpec"] = container_spec.to_dict()

        super(UnmanagedContainerModel, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )
