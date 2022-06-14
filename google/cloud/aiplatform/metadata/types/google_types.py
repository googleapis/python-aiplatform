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


class VertexDataset(base.ArtifactType):
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
            Optional. Contains the metadata information that will be stored in the Artifact.
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


class VertexTensorboardRun(base.ArtifactType):
    """An artifact representing a Vertex Tensorboard Run."""

    SCHEMA_TITLE = "google.VertexTensorboardRun"

    def __init__(
        self,
        tensorboard_run_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        tensorboard_run_name (str):
            Optional. The name of the VertexTensorboardRun resource, in a form of
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}/runs/{run}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.tensorboards.experiments.runs/get
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
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = tensorboard_run_name

        super(VertexTensorboardRun, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=tensorboard_run_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class VertexModel(base.ArtifactType):
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
            Optional. Contains the metadata information that will be stored in the Artifact.
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


class VertexEndpoint(base.ArtifactType):
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
            Optional. Contains the metadata information that will be stored in the Artifact.
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


class BQMLModel(base.ArtifactType):
    """An artifact representing a BQML Model."""

    SCHEMA_TITLE = "google.BQMLModel"

    def __init__(
        self,
        resource_name: Optional[str] = None,
        bqml_project_id: Optional[str] = None,
        bqml_dataset_id: Optional[str] = None,
        bqml_model_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        bqml_project_id (str):
            The Project that hosts the corresponding BigQuery ML Model.
        bqml_dataset_id (str):
            The BigQuery Dataset ID for corresponding BigQuery ML Model.
        bqml_model_id (str):
            The BigQuery Model ID for the corresponding Model.
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
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        extended_metadata = metadata or {}
        extended_metadata["projectId"] = bqml_project_id
        extended_metadata["datasetId"] = bqml_dataset_id
        extended_metadata["modelId"] = bqml_model_id

        super(BQMLModel, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class BQTable(base.ArtifactType):
    """An artifact representing a BQML Table."""

    SCHEMA_TITLE = "google.BQTable"

    def __init__(
        self,
        resource_name: Optional[str] = None,
        bqml_project_id: Optional[str] = None,
        bqml_dataset_id: Optional[str] = None,
        bqml_table_id: Optional[str] = None,
        bqml_table_expiration_time: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        bqml_project_id (str):
            The Project that hosts the corresponding BigQuery ML Model.
        bqml_dataset_id (str):
            The BigQuery Dataset ID for corresponding BigQuery ML Model.
        bqml_model_id (str):
            The BigQuery Model ID for the corresponding Model.
        bqml_table_expiration_time (str):
            The expiration time for this BigQuery Table.
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
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        extended_metadata = metadata or {}
        extended_metadata["projectId"] = bqml_project_id
        extended_metadata["datasetId"] = bqml_dataset_id
        extended_metadata["tableId"] = bqml_table_id
        extended_metadata["expirationTime"] = bqml_table_expiration_time

        super(BQTable, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class UnmanagedContainerModel(base.ArtifactType):
    """An artifact representing a Vertex Unmanaged Container Model."""

    SCHEMA_TITLE = "google.UnmanagedContainerModel"

    def __init__(
        self,
        instance_schema_uri: str,
        parameters_schema_uri: str,
        prediction_schema_uri: str,
        container_image_uri: str,
        resource_name: Optional[str] = None,
        container_command: Optional[List[str]] = None,
        container_args: Optional[List[str]] = None,
        container_env: Optional[List[Dict[str, str]]] = None,
        container_ports: Optional[List[int]] = None,
        container_predict_route: Optional[str] = None,
        container_health_route: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        instance_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage describing the format of a single instance, which are used in PredictRequest.instances, ExplainRequest.instances and BatchPredictionJob.input_config. The schema is defined as an OpenAPI 3.0.2 `Schema Object.
        parameters_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage describing the parameters of prediction and explanation via PredictRequest.parameters, ExplainRequest.parameters and BatchPredictionJob.model_parameters. The schema is defined as an OpenAPI 3.0.2 `Schema Object.
        prediction_schema_uri (str):
            Required. Points to a YAML file stored on Google Cloud Storage describing the format of a single prediction produced by this Model, which are returned via PredictResponse.predictions, ExplainResponse.explanations, and BatchPredictionJob.output_config. The schema is defined as an OpenAPI 3.0.2 `Schema Object.
        container_image_uri (str):
            Required. URI of the Docker image to be used as the custom container for serving predictions. This URI must identify an image in Artifact Registry or Container Registry. Learn more about the `container publishing requirements
        resource_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        container_command (Sequence[str]):
            Optional. Specifies the command that runs when the container starts. This overrides the container's `ENTRYPOINT
        container_args (Sequence[str]):
            Optional. Specifies arguments for the command that runs when the container starts. This overrides the container's ```CMD``
        container_env (Sequence[google.cloud.aiplatform_v1.types.EnvVar]):
            Optional. List of environment variables to set in the container. After the container starts running, code running in the container can read these environment variables. Additionally, the command and args fields can reference these variables. Later entries in this list can also reference earlier entries. For example, the following example sets the variable ``VAR_2`` to have the value ``foo bar``: .. code:: json [ { "name": "VAR_1", "value": "foo" }, { "name": "VAR_2", "value": "$(VAR_1) bar" } ] If you switch the order of the variables in the example, then the expansion does not occur. This field corresponds to the ``env`` field of the Kubernetes Containers `v1 core API.
        container_ports (Sequence[google.cloud.aiplatform_v1.types.Port]):
            Optional. List of ports to expose from the container. Vertex AI sends any prediction requests that it receives to the first port on this list. Vertex AI also sends `liveness and health checks.
        container_predict_route (str):
            Optional. HTTP path on the container to send prediction requests to. Vertex AI forwards requests sent using projects.locations.endpoints.predict to this path on the container's IP address and port. Vertex AI then returns the container's response in the API response. For example, if you set this field to ``/foo``, then when Vertex AI receives a prediction request, it forwards the request body in a POST request to the ``/foo`` path on the port of your container specified by the first value of this ``ModelContainerSpec``'s ports field. If you don't specify this field, it defaults to the following value when you [deploy this Model to an Endpoint][google.cloud.aiplatform.v1.EndpointService.DeployModel]: /v1/endpoints/ENDPOINT/deployedModels/DEPLOYED_MODEL:predict The placeholders in this value are replaced as follows: - ENDPOINT: The last segment (following ``endpoints/``)of the Endpoint.name][] field of the Endpoint where this Model has been deployed. (Vertex AI makes this value available to your container code as the ```AIP_ENDPOINT_ID`` environment variable
        container_health_route (str):
            Optional. HTTP path on the container to send health checks to. Vertex AI intermittently sends GET requests to this path on the container's IP address and port to check that the container is healthy. Read more about `health checks
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
            Optional. Contains the metadata information that will be stored in the Artifact.
        """

        extended_metadata = metadata or {}
        extended_metadata["predictSchemata"] = {}
        extended_metadata["predictSchemata"]["instanceSchemaUri"] = instance_schema_uri
        extended_metadata["predictSchemata"][
            "parametersSchemaUri"
        ] = parameters_schema_uri
        extended_metadata["predictSchemata"][
            "predictionSchemaUri"
        ] = prediction_schema_uri

        extended_metadata["containerSpec"] = {}
        extended_metadata["containerSpec"]["imageUri"] = container_image_uri
        if container_command:
            extended_metadata["containerSpec"]["command"] = container_command
        if container_args:
            extended_metadata["containerSpec"]["args"] = container_args
        if container_env:
            extended_metadata["containerSpec"]["env"] = container_env
        if container_ports:
            extended_metadata["containerSpec"]["ports"] = container_ports
        if container_predict_route:
            extended_metadata["containerSpec"]["predictRoute"] = container_predict_route
        if container_health_route:
            extended_metadata["containerSpec"]["healthRoute"] = container_health_route

        super(UnmanagedContainerModel, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


# A possible alternative is to have container defined as an Enum class that is passed into UnmanagedContainerModel as follows:
class UnmanagedContainerModelUsingDataClass(base.ArtifactType):
    """An artifact representing a Vertex Unmanaged Container Model."""

    SCHEMA_TITLE = "google.UnmanagedContainerModel"

    def __init__(
        self,
        predict_schema_ta: utils.PredictSchemata,
        container_spec: utils.PredictSchemata,
        resource_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        predict_schema_ta (PredictSchemata):
            An instance of PredictSchemata which holds instance, parameter and prediction schema uris.
        container_spec (ContainerSpec):
            An instance of ContainerSpec which holds the container configuration for the model.
        resource_name (str):
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
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        extended_metadata = metadata or {}
        extended_metadata["predictSchemata"] = predict_schema_ta.to_dict()
        extended_metadata["containerSpec"] = container_spec.to_dict()

        super(UnmanagedContainerModelUsingDataClass, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )
