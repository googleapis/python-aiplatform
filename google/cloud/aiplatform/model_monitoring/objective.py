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
#

from typing import Optional, Dict

from google.cloud.aiplatform_v1.types import (
    io as gca_io,
    ThresholdConfig as gca_threshold_config,
    model_monitoring as gca_model_monitoring,
)

TF_RECORD = "tf-record"
CSV = "csv"
JSONL = "jsonl"


class _SkewDetectionConfig:
    def __init__(
        self,
        data_source: str,
        skew_thresholds: Dict[str, float],
        target_field: str,
        attribute_skew_thresholds: Dict[str, float],
        data_format: Optional[str] = None,
    ):
        """Base class for training-serving skew detection.
        Args:
            data_source (str):
                Required. Path to training dataset.

            skew_thresholds (Dict[str, float]):
                Optional. Key is the feature name and value is the
                threshold. If a feature needs to be monitored
                for skew, a value threshold must be configured
                for that feature. The threshold here is against
                feature distribution distance between the
                training and prediction feature.

            target_field (str):
                Required. The target field name the model is to
                predict. This field will be excluded when doing
                Predict and (or) Explain for the training data.

            attribute_skew_thresholds (Dict[str, float]):
                Optional. Key is the feature name and value is the
                threshold. Feature attributions indicate how much
                each feature in your model contributed to the
                predictions for each given instance.

            data_format (str):
                Optional. Data format of the dataset, only applicable
                if the input is from Google Cloud Storage.
                The possible formats are:

                "tf-record"
                The source file is a TFRecord file.

                "csv"
                The source file is a CSV file.

                "jsonl"
                The source file is a JSONL file.
        """
        self.data_source = data_source
        self.skew_thresholds = skew_thresholds
        self.attribute_skew_thresholds = attribute_skew_thresholds
        self.data_format = data_format
        self.target_field = target_field
        self.training_dataset = None

    def as_proto(self):
        """Returns _SkewDetectionConfig as a proto message."""
        skew_thresholds_mapping = {}
        attribution_score_skew_thresholds_mapping = {}
        if self.skew_thresholds is not None:
            for key in self.skew_thresholds.keys():
                skew_threshold = gca_threshold_config(value=self.skew_thresholds[key])
                skew_thresholds_mapping[key] = skew_threshold
        if self.attribute_skew_thresholds is not None:
            for key in self.attribute_skew_thresholds.keys():
                attribution_score_skew_threshold = gca_threshold_config(
                    value=self.attribute_skew_thresholds[key]
                )
                attribution_score_skew_thresholds_mapping[
                    key
                ] = attribution_score_skew_threshold
        return gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingPredictionSkewDetectionConfig(
            skew_thresholds=skew_thresholds_mapping,
            attribution_score_skew_thresholds=attribution_score_skew_thresholds_mapping,
        )


class _DriftDetectionConfig:
    def __init__(
        self,
        drift_thresholds: Dict[str, float],
        attribute_drift_thresholds: Dict[str, float],
    ):
        """Base class for prediction drift detection.
        Args:
            drift_thresholds (Dict[str, float]):
                Required. Key is the feature name and value is the
                threshold. If a feature needs to be monitored
                for drift, a value threshold must be configured
                for that feature. The threshold here is against
                feature distribution distance between different
                time windws.
            attribute_drift_thresholds (Dict[str, float]):
                Required. Key is the feature name and value is the
                threshold. The threshold here is against
                attribution score distance between different
                time windows.
        """
        self.drift_thresholds = drift_thresholds
        self.attribute_drift_thresholds = attribute_drift_thresholds

    def as_proto(self):
        """Returns drift detection config as a proto message."""
        drift_thresholds_mapping = {}
        attribution_score_drift_thresholds_mapping = {}
        if self.drift_thresholds is not None:
            for key in self.drift_thresholds.keys():
                drift_threshold = gca_threshold_config(value=self.drift_thresholds[key])
                drift_thresholds_mapping[key] = drift_threshold
        if self.attribute_drift_thresholds is not None:
            for key in self.attribute_drift_thresholds.keys():
                attribution_score_drift_threshold = gca_threshold_config(
                    value=self.attribute_drift_thresholds[key]
                )
                attribution_score_drift_thresholds_mapping[
                    key
                ] = attribution_score_drift_threshold
        return gca_model_monitoring.ModelMonitoringObjectiveConfig.PredictionDriftDetectionConfig(
            drift_thresholds=drift_thresholds_mapping,
            attribution_score_drift_thresholds=attribution_score_drift_thresholds_mapping,
        )


class _ExplanationConfig:
    def __init__(self):
        """Base class for ExplanationConfig."""
        self.enable_feature_attributes = False

    def as_proto(self):
        """Returns _ExplanationConfig as a proto message."""
        return gca_model_monitoring.ModelMonitoringObjectiveConfig.ExplanationConfig(
            enable_feature_attributes=self.enable_feature_attributes
        )


class _ObjectiveConfig:
    def __init__(
        self,
        skew_detection_config: Optional[
            "gca_model_monitoring._SkewDetectionConfig"
        ] = None,
        drift_detection_config: Optional[
            "gca_model_monitoring._DriftDetectionConfig"
        ] = None,
        explanation_config: Optional["gca_model_monitoring._ExplanationConfig"] = None,
    ):
        """Base class for ObjectiveConfig.
        Args:
            skew_detection_config (_SkewDetectionConfig):
                Optional. An instance of _SkewDetectionConfig.
            drift_detection_config (_DriftDetectionConfig):
                Optional. An instance of _DriftDetectionConfig.
            explanation_config (_ExplanationConfig):
                Optional. An instance of _ExplanationConfig.
        """
        self.skew_detection_config = skew_detection_config
        self.drift_detection_config = drift_detection_config
        self.explanation_config = explanation_config

    def as_proto(self):
        """Returns _ObjectiveConfig as a proto message."""
        training_dataset = None
        if self.skew_detection_config is not None:
            training_dataset = self.skew_detection_config.training_dataset
        return gca_model_monitoring.ModelMonitoringObjectiveConfig(
            training_dataset=training_dataset,
            training_prediction_skew_detection_config=self.skew_detection_config.as_proto()
            if self.skew_detection_config is not None
            else None,
            prediction_drift_detection_config=self.drift_detection_config.as_proto()
            if self.drift_detection_config is not None
            else None,
            explanation_config=self.explanation_config.as_proto()
            if self.explanation_config is not None
            else None,
        )


class SkewDetectionConfig(_SkewDetectionConfig):
    """A class that configures skew detection for models deployed to an endpoint.

    Training-serving skew occurs when input data in production has a different
    distribution than the data used during model training. Model performance
    can deteriorate when production data deviates from training data.
    """

    def __init__(
        self,
        data_source: str,
        target_field: str,
        skew_thresholds: Optional[Dict[str, float]] = None,
        attribute_skew_thresholds: Optional[Dict[str, float]] = None,
        data_format: Optional[str] = None,
    ):
        """Initializer for SkewDetectionConfig.

        Args:
            data_source (str):
                Required. Path to training dataset.

            target_field (str):
                Required. The target field name the model is to
                predict. This field will be excluded when doing
                Predict and (or) Explain for the training data.

            skew_thresholds (Dict[str, float]):
                Optional. Key is the feature name and value is the
                threshold. If a feature needs to be monitored
                for skew, a value threshold must be configured
                for that feature. The threshold here is against
                feature distribution distance between the
                training and prediction feature.

            attribute_skew_thresholds (Dict[str, float]):
                Optional. Key is the feature name and value is the
                threshold. Feature attributions indicate how much
                each feature in your model contributed to the
                predictions for each given instance.

            data_format (str):
                Optional. Data format of the dataset, only applicable
                if the input is from Google Cloud Storage.
                The possible formats are:

                "tf-record"
                The source file is a TFRecord file.

                "csv"
                The source file is a CSV file.

                "jsonl"
                The source file is a JSONL file.

        Raises:
            ValueError for unsupported data formats.
        """
        super().__init__(
            data_source,
            skew_thresholds,
            target_field,
            attribute_skew_thresholds,
            data_format,
        )

        training_dataset = (
            gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingDataset(
                target_field=target_field
            )
        )
        if data_source.startswith("bq:/"):
            training_dataset.bigquery_source = gca_io.BigQuerySource(
                input_uri=data_source
            )
        elif data_source.startswith("gs:/"):
            training_dataset.gcs_source = gca_io.GcsSource(uris=[data_source])
            if data_format is not None and data_format not in [TF_RECORD, CSV, JSONL]:
                raise ValueError(
                    "Unsupported value. `data_format` must be one of %s, %s, or %s"
                    % (TF_RECORD, CSV, JSONL)
                )
            training_dataset.data_format = data_format
        else:
            training_dataset.dataset = data_source
        self.training_dataset = training_dataset


class DriftDetectionConfig(_DriftDetectionConfig):
    """A class that configures prediction drift detection for models deployed to an endpoint.

    Prediction drift occurs when feature data distribution changes noticeably
    over time, and should be set when the original training data is unavailable.
    If original training data is available, SkewDetectionConfig should
    be set instead.
    """

    def __init__(
        self,
        drift_thresholds: Optional[Dict[str, float]] = None,
        attribute_drift_thresholds: Optional[Dict[str, float]] = None,
    ):
        """Initializer for DriftDetectionConfig.

        Args:
            drift_thresholds (Dict[str, float]):
                Optional. Key is the feature name and value is the
                threshold. If a feature needs to be monitored
                for drift, a value threshold must be configured
                for that feature. The threshold here is against
                feature distribution distance between different
                time windws.

            attribute_drift_thresholds (Dict[str, float]):
                Optional. Key is the feature name and value is the
                threshold. The threshold here is against
                attribution score distance between different
                time windows.
        """
        super().__init__(drift_thresholds, attribute_drift_thresholds)


class ExplanationConfig(_ExplanationConfig):
    """A class that enables Vertex Explainable AI.

    Only applicable if the model has explanation_spec populated. By default, explanation config is disabled. Instantiating this class will enable the config.
    """

    def __init__(self):
        """Initializer for ExplanationConfig."""
        super().__init__()
        self.enable_feature_attributes = True


class ObjectiveConfig(_ObjectiveConfig):
    """A class that captures skew detection, drift detection, and explanation configs."""

    def __init__(
        self,
        skew_detection_config: Optional["SkewDetectionConfig"] = None,
        drift_detection_config: Optional["DriftDetectionConfig"] = None,
        explanation_config: Optional["ExplanationConfig"] = None,
    ):
        """Initializer for ObjectiveConfig.
        Args:
            skew_detection_config (SkewDetectionConfig):
                Optional. An instance of SkewDetectionConfig.
            drift_detection_config (DriftDetectionConfig):
                Optional. An instance of DriftDetectionConfig.
            explanation_config (ExplanationConfig):
                Optional. An instance of ExplanationConfig.
        """
        super().__init__(
            skew_detection_config, drift_detection_config, explanation_config
        )
