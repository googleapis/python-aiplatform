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
from typing import Optional, Dict, List
from google.cloud.aiplatform.metadata import artifact
from google.cloud.aiplatform.metadata.types import types_utils


class HTML(artifact.BaseArtifactType):
    """Schemaless Artifact Type to store HTML file."""

    SCHEMA_TITLE = "system.HTML"

    def __init__(
        self,
        resource_name: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
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

        super(HTML, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=metadata,
        )


class Markdown(artifact.BaseArtifactType):
    """Schemaless Artifact Type to store Markdown file."""

    SCHEMA_TITLE = "system.Markdown"

    def __init__(
        self,
        resource_name: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
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

        super(Markdown, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=metadata,
        )


class Model(artifact.BaseArtifactType):
    """Schemaless Artifact Type to store Markdown file."""

    SCHEMA_TITLE = "system.Model"

    def __init__(
        self,
        resource_name: str,
        framework: Optional[str] = None,
        framework_version: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        framework (str):
            Optional. The framework used for this model.
        framework_version (str):
            Optional. The framework version used for this model.
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
        if framework:
            extended_metadata["framework"] = framework
        if framework_version:
            extended_metadata["framework_version"] = framework_version

        super(Model, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class Dataset(artifact.BaseArtifactType):
    """An artifact representing a system Dataset."""

    SCHEMA_TITLE = "system.Dataset"

    def __init__(
        self,
        resource_name: str,
        payload_format: Optional[str] = None,
        container_format: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        dataset_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        payload_format (str):
            Optional. TBD
        container_format (str):
            Optional. TBD
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
        extended_metadata["payload_format"] = payload_format
        extended_metadata["container_format"] = container_format

        super(Dataset, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class Metrics(artifact.BaseArtifactType):
    """Artifact type for scalar metrics."""

    SCHEMA_TITLE = "system.Metrics"

    def __init__(
        self,
        resource_name: str,
        accuracy: Optional[float] = 0,
        precision: Optional[float] = 0,
        recall: Optional[float] = 0,
        f1score: Optional[float] = 0,
        mean_absolute_error: Optional[float] = 0,
        mean_squared_error: Optional[float] = 0,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        dataset_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        accuracy (float):
            Optional. Defaults to zero.
        precision (float):
            Optional. Defaults to zero.
        recall (float):
            Optional. Defaults to zero.
        f1score (float):
            Optional. Defaults to zero.
        mean_absolute_error (float):
            Optional. Defaults to zero.
        mean_squared_error (float):
            Optional. Defaults to zero.
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
        extended_metadata["accuracy"] = accuracy
        extended_metadata["precision"] = precision
        extended_metadata["recall"] = recall
        extended_metadata["f1score"] = f1score
        extended_metadata["mean_absolute_error"] = mean_absolute_error
        extended_metadata["mean_squared_error"] = mean_squared_error

        super(Metrics, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class ConfusionMatrix(artifact.BaseArtifactType):
    """Artifact type for confusion matrix."""

    SCHEMA_TITLE = "system.ConfusionMatrix"

    def __init__(
        self,
        resource_name: str,
        column_display_names: Optional[str] = None,
        column_ids: Optional[str] = None,
        matrix_values: Optional[List[List[int]]] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        column_display_names (List[str]):
            Optional. List of strings corresponding to Confusion Matrix column headers.
        column_ids (List(str)):
            Optional. List of strings corresponding to Confusion Matrix column IDs.
        matrix_values (List[List[int]]):
            Optional. A 2D array of integers represeting the matrix values.
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

        annotation_specs = []
        for i, display_name in enumerate(column_display_names):
            annotation_spec = {}
            annotation_spec["displayName"] = display_name
            if i < len(column_ids):
                annotation_spec["id"] = column_ids[i]

            annotation_specs.append(annotation_spec)

        extended_metadata["annotationSpecs"] = annotation_specs
        extended_metadata["rows"] = matrix_values

        super(ConfusionMatrix, self).__init__(
            resource_name=resource_name,
            schema_title=self.SCHEMA_TITLE,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class ConfusionMatrixUsingDataStructure(artifact.BaseArtifactType):
    """Aternative class for Artifact type for confusion matrix."""

    SCHEMA_TITLE = "system.ConfusionMatrix"

    def __init__(
        self,
        resource_name: str,
        confusion_matrix: Optional[types_utils.ConfusionMatrix] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        confusion_matrix (types_utils.ConfusionMatrix):
            Optional. An instance of ConfusionMatrix that holds matrix values and headers.
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

        if confusion_matrix.annotation_specs:
            annotation_specs = []
            for item in confusion_matrix.annotation_specs:
                annotation_spec = {}
                annotation_spec["displayName"] = item.display_name or ""
                annotation_spec["id"] = item.id or ""
                annotation_specs.append(annotation_spec)

        extended_metadata["annotationSpecs"] = annotation_specs
        extended_metadata["rows"] = confusion_matrix.matrix_values

        super(ConfusionMatrixUsingDataStructure, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class ConfidenceMetrics(artifact.BaseArtifactType):
    """Artifact type for confidence metrics."""

    SCHEMA_TITLE = "system.ConfidenceMetrics"

    def __init__(
        self,
        resource_name: str,
        confidence_threshold: Optional[float] = 0,
        max_predictions: Optional[int] = 0,
        recall: Optional[float] = 0,
        precision: Optional[float] = 0,
        false_positive_rate: Optional[float] = 0,
        f1_score: Optional[float] = 0,
        recall_at1: Optional[float] = 0,
        precision_at1: Optional[float] = 0,
        false_positive_rate_at1: Optional[float] = 0,
        f1_score_at1: Optional[float] = 0,
        true_positive_count: Optional[int] = 0,
        false_positive_count: Optional[int] = 0,
        false_negative_count: Optional[int] = 0,
        true_negative_count: Optional[int] = 0,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        confidence_threshold (float):
            Optional. Defaults to zero.
        max_predictions (float):
            Optional. Defaults to zero.
        recall (float):
            Optional. Defaults to zero.
        precision (float):
            Optional. Defaults to zero.
        false_positive_rate (float):
            Optional. Defaults to zero.
        f1_score (float):
            Optional. Defaults to zero.
        recall_at1 (float):
            Optional. Defaults to zero.
        precision_at1 (float):
            Optional. Defaults to zero.
        false_positive_rate_at1 (float):
            Optional. Defaults to zero.
        f1_score_at1 (float):
            Optional. Defaults to zero.
        true_positive_count (float):
            Optional. Defaults to zero.
        false_positive_count (float):
            Optional. Defaults to zero.
        false_negative_count (float):
            Optional. Defaults to zero.
        true_negative_count (float):
            Optional. Defaults to zero.
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
        extended_metadata["confidenceThreshold"] = confidence_threshold
        extended_metadata["maxPredictions"] = max_predictions
        extended_metadata["recall"] = recall
        extended_metadata["precision"] = precision
        extended_metadata["falsePositiveRate"] = false_positive_rate
        extended_metadata["f1Score"] = f1_score
        extended_metadata["recallAt1"] = recall_at1
        extended_metadata["precisionAt1"] = precision_at1
        extended_metadata["falsePositiveRateAt1"] = false_positive_rate_at1
        extended_metadata["f1ScoreAt1"] = f1_score_at1
        extended_metadata["truePositiveCount"] = true_positive_count
        extended_metadata["falsePositiveCount"] = false_positive_count
        extended_metadata["falseNegativeCount"] = false_negative_count
        extended_metadata["trueNegativeCount"] = true_negative_count

        super(ConfidenceMetrics, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class ConfidenceMetricsUsingDataClass(artifact.BaseArtifactType):
    """Artifact type for confidence metrics."""

    SCHEMA_TITLE = "system.ConfidenceMetrics"

    def __init__(
        self,
        resource_name: str,
        confidence_metrics: types_utils.ConfidenceMetrics,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        Confidence_metrics (ConfidenceMetrics):
            An instance of ConfidenceMetrics data class.
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
        extended_metadata.update(confidence_metrics.to_dict())

        super(ConfidenceMetricsUsingDataClass, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class ClassificationMetrics(artifact.BaseArtifactType):
    """Artifact type for classification metrics."""

    SCHEMA_TITLE = "system.ClassificationMetrics"

    def __init__(
        self,
        resource_name: str,
        classification_metrics: Optional[types_utils.ClassificationMetrics] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        classification_metrics (ClassificationMetrics):
            Optional. An instance of ClassificationMetrics data class.
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
        if classification_metrics:
            extended_metadata.update(classification_metrics.to_dict())

        super(ClassificationMetrics, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class SlicedClassificationMetrics(artifact.BaseArtifactType):
    """Artifact type for Sliced Classification Metrics."""

    SCHEMA_TITLE = "system.SlicedClassificationMetrics"

    def __init__(
        self,
        resource_name: str,
        slice: Optional[str] = None,
        classification_metrics: Optional[types_utils.ClassificationMetrics] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        slice (str):
            Optional. Name of the data ClassificationMetrics slice.
        classification_metrics (ClassificationMetrics):
            Optional. An instance of ClassificationMetrics data class.
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

        if slice:
            extended_metadata["slice"] = slice
        if classification_metrics:
            extended_metadata[
                "sliceClassificationMetrics"
            ] = classification_metrics.to_dict()

        super(SlicedClassificationMetrics, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class TensorboardLogs(artifact.BaseArtifactType):
    """Artifact type for Tensorboard Logs."""

    SCHEMA_TITLE = "system.TensorboardLogs"

    def __init__(
        self,
        resource_name: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
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

        super(TensorboardLogs, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class TensorboardExperiment(artifact.BaseArtifactType):
    """Artifact type for Tensorboard Experiment."""

    SCHEMA_TITLE = "system.TensorboardExperiment"

    def __init__(
        self,
        resource_name: str,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        resource_name (str):
            The resource name of the Artifact following the format as follows.
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

        super(TensorboardExperiment, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=resource_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )
