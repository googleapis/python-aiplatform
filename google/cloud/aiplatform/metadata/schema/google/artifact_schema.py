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

import copy
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
        vertex_dataset_name: str,
        artifact_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        vertex_dataset_name (str):
            The name of the Dataset resource, in a form of
            projects/{project}/locations/{location}/datasets/{dataset}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.datasets/get
            This is used to generate the resource uri as follows:
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
        extended_metadata[_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME] = vertex_dataset_name

        super(VertexDataset, self).__init__(
            uri=utils.create_uri_from_resource_name(resource_name=vertex_dataset_name),
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
        artifact_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        vertex_model_name (str):
            The name of the Model resource, in a form of
            projects/{project}/locations/{location}/models/{model}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.models/get
            This is used to generate the resource uri as follows:
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
        extended_metadata[_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME] = vertex_model_name

        super(VertexModel, self).__init__(
            uri=utils.create_uri_from_resource_name(resource_name=vertex_model_name),
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
        artifact_id: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        vertex_endpoint_name (str):
            The name of the Endpoint resource, in a form of
            projects/{project}/locations/{location}/endpoints/{endpoint}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.endpoints/get
            This is used to generate the resource uri as follows:
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
        extended_metadata[_ARTIFACT_PROPERTY_KEY_RESOURCE_NAME] = vertex_endpoint_name

        super(VertexEndpoint, self).__init__(
            uri=utils.create_uri_from_resource_name(resource_name=vertex_endpoint_name),
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
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
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


class ClassificationMetrics(base_artifact.BaseArtifactSchema):
    """A Google artifact representing evaluation Classification Metrics."""

    schema_title = "google.ClassificationMetrics"

    def __init__(
        self,
        *,
        au_prc: Optional[float] = None,
        au_roc: Optional[float] = None,
        log_loss: Optional[float] = None,
        artifact_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        au_prc (float):
            Optional. The Area Under Precision-Recall Curve metric.
            Micro-averaged for the overall evaluation.
        au_roc (float):
            Optional. The Area Under Receiver Operating Characteristic curve metric.
            Micro-averaged for the overall evaluation.
        log_loss (float):
            Optional. The Log Loss metric.
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
        if au_prc:
            extended_metadata["auPrc"] = au_prc
        if au_roc:
            extended_metadata["auRoc"] = au_roc
        if log_loss:
            extended_metadata["logLoss"] = log_loss

        super(ClassificationMetrics, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class RegressionMetrics(base_artifact.BaseArtifactSchema):
    """A Google artifact representing evaluation Regression Metrics."""

    schema_title = "google.RegressionMetrics"

    def __init__(
        self,
        *,
        root_mean_squared_error: Optional[float] = None,
        mean_absolute_error: Optional[float] = None,
        mean_absolute_percentage_error: Optional[float] = None,
        r_squared: Optional[float] = None,
        root_mean_squared_log_error: Optional[float] = None,
        artifact_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        root_mean_squared_error (float):
            Optional. Root Mean Squared Error (RMSE).
        mean_absolute_error (float):
            Optional. Mean Absolute Error (MAE).
        mean_absolute_percentage_error (float):
            Optional. Mean absolute percentage error.
        r_squared (float):
            Optional. Coefficient of determination as Pearson correlation coefficient.
        root_mean_squared_log_error (float):
            Optional. Root mean squared log error.
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
        if root_mean_squared_error:
            extended_metadata["rootMeanSquaredError"] = root_mean_squared_error
        if mean_absolute_error:
            extended_metadata["meanAbsoluteError"] = mean_absolute_error
        if mean_absolute_percentage_error:
            extended_metadata[
                "meanAbsolutePercentageError"
            ] = mean_absolute_percentage_error
        if r_squared:
            extended_metadata["rSquared"] = r_squared
        if root_mean_squared_log_error:
            extended_metadata["rootMeanSquaredLogError"] = root_mean_squared_log_error

        super(RegressionMetrics, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class ForecastingMetrics(base_artifact.BaseArtifactSchema):
    """A Google artifact representing evaluation Forecasting Metrics."""

    schema_title = "google.ForecastingMetrics"

    def __init__(
        self,
        *,
        root_mean_squared_error: Optional[float] = None,
        mean_absolute_error: Optional[float] = None,
        mean_absolute_percentage_error: Optional[float] = None,
        r_squared: Optional[float] = None,
        root_mean_squared_log_error: Optional[float] = None,
        weighted_absolute_percentage_error: Optional[float] = None,
        root_mean_squared_percentage_error: Optional[float] = None,
        symmetric_mean_absolute_percentage_error: Optional[float] = None,
        artifact_id: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: Optional[gca_artifact.Artifact.State] = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        root_mean_squared_error (float):
            Optional. Root Mean Squared Error (RMSE).
        mean_absolute_error (float):
            Optional. Mean Absolute Error (MAE).
        mean_absolute_percentage_error (float):
            Optional. Mean absolute percentage error.
        r_squared (float):
            Optional. Coefficient of determination as Pearson correlation coefficient.
        root_mean_squared_log_error (float):
            Optional. Root mean squared log error.
        weighted_absolute_percentage_error (float):
            Optional. Weighted Absolute Percentage Error.
            Does not use weights, this is just what the metric is called.
            Undefined if actual values sum to zero.
            Will be very large if actual values sum to a very small number.
        root_mean_squared_percentage_error (float):
            Optional. Root Mean Square Percentage Error. Square root of MSPE.
            Undefined/imaginary when MSPE is negative.
        symmetric_mean_absolute_percentage_error (float):
            Optional. Symmetric Mean Absolute Percentage Error.
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
        extended_metadata = copy.deepcopy(metadata) if metadata else {}
        if root_mean_squared_error:
            extended_metadata["rootMeanSquaredError"] = root_mean_squared_error
        if mean_absolute_error:
            extended_metadata["meanAbsoluteError"] = mean_absolute_error
        if mean_absolute_percentage_error:
            extended_metadata[
                "meanAbsolutePercentageError"
            ] = mean_absolute_percentage_error
        if r_squared:
            extended_metadata["rSquared"] = r_squared
        if root_mean_squared_log_error:
            extended_metadata["rootMeanSquaredLogError"] = root_mean_squared_log_error
        if weighted_absolute_percentage_error:
            extended_metadata[
                "weightedAbsolutePercentageError"
            ] = weighted_absolute_percentage_error
        if root_mean_squared_percentage_error:
            extended_metadata[
                "rootMeanSquaredPercentageError"
            ] = root_mean_squared_percentage_error
        if symmetric_mean_absolute_percentage_error:
            extended_metadata[
                "symmetricMeanAbsolutePercentageError"
            ] = symmetric_mean_absolute_percentage_error

        super(ForecastingMetrics, self).__init__(
            uri=uri,
            artifact_id=artifact_id,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )
