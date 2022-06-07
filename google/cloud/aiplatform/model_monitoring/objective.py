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

import abc
from typing import Optional, Dict

# from google.cloud.aiplatform.compat.types import (
#     model_monitoring as gca_model_monitoring,
# )
# from google.cloud.aiplatform_v1.types import ThresholdConfig as gca_threshold_config
# from google.cloud.aiplatform_v1.types.io import BigQuerySource
from google.cloud.aiplatform_v1.types import (
    io as gca_io,
    ThresholdConfig as gca_threshold_config,
    model_monitoring as gca_model_monitoring,
)


class _SkewDetectionConfig(abc.ABC):
    def __init__(
        self,
        data_source: str,
        skew_thresholds: Dict[str, float],
        attribute_skew_thresholds: Optional[Dict[str, float]] = None,
        data_format: Optional[str] = None,
        target_field: Optional[str] = None,
    ):
        """"""
        # print(skew_thresholds)
        self.data_source = data_source
        self.skew_thresholds = skew_thresholds
        self.attribute_skew_thresholds = attribute_skew_thresholds
        self.data_format = data_format
        self.target_field = target_field

    def as_proto(self):
        skew_thresholds_mapping = {}
        attribution_score_skew_thresholds_mapping = {}
        for key in self.skew_thresholds.keys():
            skew_threshold = gca_threshold_config(value=self.skew_thresholds[key])
            skew_thresholds_mapping[key] = skew_threshold
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


class _DriftDetectionConfig(abc.ABC):
    def __init__(
        self,
        drift_thresholds: Dict[str, float],
        attribute_drift_thresholds: Optional[Dict[str, float]] = None,
    ):
        self.drift_thresholds = drift_thresholds
        self.attribute_drift_thresholds = attribute_drift_thresholds

    def as_proto(self):
        drift_thresholds_mapping = {}
        attribution_score_drift_thresholds_mapping = {}
        for key in self.drift_thresholds.keys():
            drift_threshold = gca_threshold_config(value=self.drift_thresholds[key])
            drift_thresholds_mapping[key] = drift_threshold
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


class _ExplanationConfig(abc.ABC):
    def __init__(self):
        self.enable_feature_attributes = False

    def as_proto(self):
        return gca_model_monitoring.ModelMonitoringObjectiveConfig.ExplanationConfig(
            enable_feature_attributes=self.enable_feature_attributes
        )


class _ObjectiveConfig(abc.ABC):
    def __init__(
        self,
        skew_detection_config: Optional["model_monitoring._SkewDetectionConfig"] = None,
        drift_detection_config: Optional[
            "model_monitoring._DriftDetectionConfig"
        ] = None,
        explanation_config: Optional["model_monitoring._ExplanationConfig"] = None,
    ):
        self.skew_detection_config = skew_detection_config
        self.drift_detection_config = drift_detection_config
        self.explanation_config = explanation_config

    def as_proto(self):
        training_dataset = None
        # print(self.skew_detection_config.target_field)
        if self.skew_detection_config is not None:
            training_dataset = (
                gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingDataset(
                    target_field=self.skew_detection_config.target_field
                )
            )
            if "bq:/" in self.skew_detection_config.data_source:
                training_dataset.bigquery_source = gca_io.BigQuerySource(
                    input_uri=self.skew_detection_config.data_source
                )
            elif "gs:/" in self.skew_detection_config.data_source:
                training_dataset.gcs_source = gca_io.GcsSource(
                    uris=[self.skew_detection_config.data_source]
                )
            else:
                training_dataset.dataset = self.skew_detection_config.data_source
            # print(training_dataset)
        return gca_model_monitoring.ModelMonitoringObjectiveConfig(
            training_dataset=training_dataset,
            training_prediction_skew_detection_config=self.skew_detection_config.as_proto(),
            prediction_drift_detection_config=self.drift_detection_config.as_proto(),
            explanation_config=self.explanation_config.as_proto(),
        )


class EndpointSkewDetectionConfig(_SkewDetectionConfig):
    """A class that configures skew detection for models deployed to an endpoint.

    Training-serving skew occurs when input data in production has a different
    distribution than the data used during model training. Model performance
    can deteriorate when production data deviates from training data.
    """

    def __init__(
        self,
        data_source: str,
        skew_thresholds: Optional[Dict[str, float]] = None,
        attribute_skew_thresholds: Optional[Dict[str, float]] = None,
        data_format: Optional[str] = None,
        target_field: Optional[str] = None,
    ):
        """Initializer for EndpointSkewDetectionConfig

        Args:
            data_source (str):
                Path to training dataset.

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

            target_field (str):
                The target field name the model is to
                predict. This field will be excluded when doing
                Predict and (or) Explain for the training data.

        Returns:
            An instance of EndpointSkewDetectionConfig
        """
        super().__init__(
            data_source,
            skew_thresholds,
            attribute_skew_thresholds,
            data_format,
            target_field,
        )


class EndpointDriftDetectionConfig(_DriftDetectionConfig):
    """A class that configures prediction drift detection for models deployed to an endpoint.

    Prediction drift occurs when feature data distribution changes noticeably
    over time, and should be set when the original training data is unavailable.
    If original training data is available, EndpointSkewDetectionConfig should
    be set instead.
    """

    def __init__(
        self,
        drift_thresholds: Optional[Dict[str, float]] = None,
        attribute_drift_thresholds: Optional[Dict[str, float]] = None,
    ):
        """Initializer for EndpointDriftDetectionConfig

        Args:
            drift_thresholds (Dict[str, float]):

            attribute_drift_thresholds (Dict[str, float]):

        Returns:
            An instance of EndpointDriftDetectionConfig
        """
        super().__init__(drift_thresholds, attribute_drift_thresholds)


class EndpointExplanationConfig(_ExplanationConfig):
    """A class that enables Vertex Explainable AI.

    Only applicable if the model has explanation_spec populated.
    """

    def __init__(self):
        super().__init__()
        self.enable_feature_attributes = True


class EndpointObjectiveConfig(_ObjectiveConfig):
    """A class that captures skew detection, drift detection, and explaination configs."""

    def __init__(
        self,
        skew_detection_config: Optional[
            "model_monitoring.EndpointSkewDetectionConfig"
        ] = None,
        drift_detection_config: Optional[
            "model_monitoring.EndpointDriftDetectionConfig"
        ] = None,
        explanation_config: Optional[
            "model_monitoring.EndpointExplanationConfig"
        ] = None,
    ):
        """"""
        super().__init__(
            skew_detection_config, drift_detection_config, explanation_config
        )
