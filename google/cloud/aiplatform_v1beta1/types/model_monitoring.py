# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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
import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import io


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "ModelMonitoringObjectiveConfig",
        "ModelMonitoringAlertConfig",
        "ThresholdConfig",
        "SamplingStrategy",
    },
)


class ModelMonitoringObjectiveConfig(proto.Message):
    r"""Next ID: 6
    Attributes:
        training_dataset (google.cloud.aiplatform_v1beta1.types.ModelMonitoringObjectiveConfig.TrainingDataset):
            Training dataset for models. This field has
            to be set only if
            TrainingPredictionSkewDetectionConfig is
            specified.
        training_prediction_skew_detection_config (google.cloud.aiplatform_v1beta1.types.ModelMonitoringObjectiveConfig.TrainingPredictionSkewDetectionConfig):
            The config for skew between training data and
            prediction data.
        prediction_drift_detection_config (google.cloud.aiplatform_v1beta1.types.ModelMonitoringObjectiveConfig.PredictionDriftDetectionConfig):
            The config for drift of prediction data.
    """

    class TrainingDataset(proto.Message):
        r"""Training Dataset information.
        Attributes:
            dataset (str):
                The resource name of the Dataset used to
                train this Model.
            gcs_source (google.cloud.aiplatform_v1beta1.types.GcsSource):
                The Google Cloud Storage uri of the unmanaged
                Dataset used to train this Model.
            bigquery_source (google.cloud.aiplatform_v1beta1.types.BigQuerySource):
                The BigQuery table of the unmanaged Dataset
                used to train this Model.
            data_format (str):
                Data format of the dataset, only applicable
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
            logging_sampling_strategy (google.cloud.aiplatform_v1beta1.types.SamplingStrategy):
                Strategy to sample data from Training
                Dataset. If not set, we process the whole
                dataset.
        """

        dataset = proto.Field(proto.STRING, number=3, oneof="data_source",)
        gcs_source = proto.Field(
            proto.MESSAGE, number=4, oneof="data_source", message=io.GcsSource,
        )
        bigquery_source = proto.Field(
            proto.MESSAGE, number=5, oneof="data_source", message=io.BigQuerySource,
        )
        data_format = proto.Field(proto.STRING, number=2,)
        target_field = proto.Field(proto.STRING, number=6,)
        logging_sampling_strategy = proto.Field(
            proto.MESSAGE, number=7, message="SamplingStrategy",
        )

    class TrainingPredictionSkewDetectionConfig(proto.Message):
        r"""The config for Training & Prediction data skew detection. It
        specifies the training dataset sources and the skew detection
        parameters.

        Attributes:
            skew_thresholds (Sequence[google.cloud.aiplatform_v1beta1.types.ModelMonitoringObjectiveConfig.TrainingPredictionSkewDetectionConfig.SkewThresholdsEntry]):
                Key is the feature name and value is the
                threshold. If a feature needs to be monitored
                for skew, a value threshold must be configed for
                that feature. The threshold here is against
                feature distribution distance between the
                training and prediction feature.
        """

        skew_thresholds = proto.MapField(
            proto.STRING, proto.MESSAGE, number=1, message="ThresholdConfig",
        )

    class PredictionDriftDetectionConfig(proto.Message):
        r"""The config for Prediction data drift detection.
        Attributes:
            drift_thresholds (Sequence[google.cloud.aiplatform_v1beta1.types.ModelMonitoringObjectiveConfig.PredictionDriftDetectionConfig.DriftThresholdsEntry]):
                Key is the feature name and value is the
                threshold. If a feature needs to be monitored
                for drift, a value threshold must be configed
                for that feature. The threshold here is against
                feature distribution distance between different
                time windws.
        """

        drift_thresholds = proto.MapField(
            proto.STRING, proto.MESSAGE, number=1, message="ThresholdConfig",
        )

    training_dataset = proto.Field(proto.MESSAGE, number=1, message=TrainingDataset,)
    training_prediction_skew_detection_config = proto.Field(
        proto.MESSAGE, number=2, message=TrainingPredictionSkewDetectionConfig,
    )
    prediction_drift_detection_config = proto.Field(
        proto.MESSAGE, number=3, message=PredictionDriftDetectionConfig,
    )


class ModelMonitoringAlertConfig(proto.Message):
    r"""Next ID: 2
    Attributes:
        email_alert_config (google.cloud.aiplatform_v1beta1.types.ModelMonitoringAlertConfig.EmailAlertConfig):
            Email alert config.
    """

    class EmailAlertConfig(proto.Message):
        r"""The config for email alert.
        Attributes:
            user_emails (Sequence[str]):
                The email addresses to send the alert.
        """

        user_emails = proto.RepeatedField(proto.STRING, number=1,)

    email_alert_config = proto.Field(
        proto.MESSAGE, number=1, oneof="alert", message=EmailAlertConfig,
    )


class ThresholdConfig(proto.Message):
    r"""The config for feature monitoring threshold.
    Next ID: 3

    Attributes:
        value (float):
            Specify a threshold value that can trigger
            the alert. If this threshold config is for
            feature distribution distance:   1. For
            categorical feature, the distribution distance
            is calculated by      L-inifinity norm.
              2. For numerical feature, the distribution
            distance is calculated by      Jensen–Shannon
            divergence.
            Each feature must have a non-zero threshold if
            they need to be monitored. Otherwise no alert
            will be triggered for that feature.
    """

    value = proto.Field(proto.DOUBLE, number=1, oneof="threshold",)


class SamplingStrategy(proto.Message):
    r"""Sampling Strategy for logging, can be for both training and
    prediction dataset.
    Next ID: 2

    Attributes:
        random_sample_config (google.cloud.aiplatform_v1beta1.types.SamplingStrategy.RandomSampleConfig):
            Random sample config. Will support more
            sampling strategies later.
    """

    class RandomSampleConfig(proto.Message):
        r"""Requests are randomly selected.
        Attributes:
            sample_rate (float):
                Sample rate (0, 1]
        """

        sample_rate = proto.Field(proto.DOUBLE, number=1,)

    random_sample_config = proto.Field(
        proto.MESSAGE, number=1, message=RandomSampleConfig,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
