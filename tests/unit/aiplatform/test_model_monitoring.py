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

import pytest

from google.cloud.aiplatform import model_monitoring

from google.cloud.aiplatform_v1.types import (
    io as gca_io,
    model_monitoring as gca_model_monitoring,
)

_TEST_TARGET_FIELD = "target"
_TEST_BQ_DATASOURCE = "bq://test/data"
_TEST_GCS_DATASOURCE = "gs://test/data"
_TEST_OTHER_DATASOURCE = ""
_TEST_DRIFT_TRESHOLD = {"key": 0.2}
_TEST_EMAIL1 = "test1"
_TEST_EMAIL2 = "test2"
_TEST_NOTIFICATION_CHANNEL = "projects/123/notificationChannels/456"
_TEST_VALID_DATA_FORMATS = ["tf-record", "csv", "jsonl"]
_TEST_SAMPLING_RATE = 0.8
_TEST_MONITORING_INTERVAL = 1
_TEST_SKEW_THRESHOLDS = [None, 0.2, {"key": 0.1}]
_TEST_ATTRIBUTE_SKEW_THRESHOLDS = [None, {"key": 0.1}]


class TestModelMonitoringConfigs:
    """Tests for model monitoring configs."""

    @pytest.mark.parametrize(
        "data_source",
        [_TEST_BQ_DATASOURCE, _TEST_GCS_DATASOURCE, _TEST_OTHER_DATASOURCE],
    )
    @pytest.mark.parametrize("data_format", _TEST_VALID_DATA_FORMATS)
    @pytest.mark.parametrize("skew_thresholds", _TEST_SKEW_THRESHOLDS)
    def test_skew_config_proto_value(self, data_source, data_format, skew_thresholds):
        """Tests if skew config can be constrctued properly to gapic proto."""
        attribute_skew_thresholds = {"key": 0.1}
        skew_config = model_monitoring.SkewDetectionConfig(
            data_source=data_source,
            skew_thresholds=skew_thresholds,
            target_field=_TEST_TARGET_FIELD,
            attribute_skew_thresholds=attribute_skew_thresholds,
            data_format=data_format,
        )
        # data_format and data source are not used at
        # TrainingPredictionSkewDetectionConfig.
        if isinstance(skew_thresholds, dict):
            expected_gapic_proto = gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingPredictionSkewDetectionConfig(
                skew_thresholds={
                    key: gca_model_monitoring.ThresholdConfig(value=val)
                    for key, val in skew_thresholds.items()
                },
                attribution_score_skew_thresholds={
                    key: gca_model_monitoring.ThresholdConfig(value=val)
                    for key, val in attribute_skew_thresholds.items()
                },
            )
        else:
            expected_gapic_proto = gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingPredictionSkewDetectionConfig(
                default_skew_threshold=gca_model_monitoring.ThresholdConfig(
                    value=skew_thresholds
                )
                if skew_thresholds is not None
                else None,
                attribution_score_skew_thresholds={
                    key: gca_model_monitoring.ThresholdConfig(value=val)
                    for key, val in attribute_skew_thresholds.items()
                },
            )
        assert skew_config.as_proto() == expected_gapic_proto

    @pytest.mark.parametrize(
        "data_source",
        [_TEST_BQ_DATASOURCE, _TEST_GCS_DATASOURCE, _TEST_OTHER_DATASOURCE],
    )
    @pytest.mark.parametrize("data_format", _TEST_VALID_DATA_FORMATS)
    @pytest.mark.parametrize("skew_thresholds", _TEST_SKEW_THRESHOLDS)
    @pytest.mark.parametrize(
        "attribute_skew_thresholds", _TEST_ATTRIBUTE_SKEW_THRESHOLDS
    )
    def test_valid_configs(
        self, data_source, data_format, skew_thresholds, attribute_skew_thresholds
    ):
        """Test config creation validity."""
        random_sample_config = model_monitoring.RandomSampleConfig(
            sample_rate=_TEST_SAMPLING_RATE
        )

        schedule_config = model_monitoring.ScheduleConfig(
            monitor_interval=_TEST_MONITORING_INTERVAL
        )

        email_alert_config = model_monitoring.EmailAlertConfig(
            user_emails=[_TEST_EMAIL1, _TEST_EMAIL2]
        )

        alert_config = model_monitoring.AlertConfig(
            user_emails=[_TEST_EMAIL1, _TEST_EMAIL2],
            enable_logging=True,
            notification_channels=[_TEST_NOTIFICATION_CHANNEL],
        )

        prediction_drift_config = model_monitoring.DriftDetectionConfig(
            drift_thresholds=_TEST_DRIFT_TRESHOLD
        )

        skew_config = model_monitoring.SkewDetectionConfig(
            data_source=data_source,
            skew_thresholds=skew_thresholds,
            target_field=_TEST_TARGET_FIELD,
            attribute_skew_thresholds=attribute_skew_thresholds,
            data_format=data_format,
        )
        expected_training_dataset = (
            gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingDataset(
                bigquery_source=gca_io.BigQuerySource(input_uri=_TEST_BQ_DATASOURCE),
                target_field=_TEST_TARGET_FIELD,
            )
        )

        xai_config = model_monitoring.ExplanationConfig()

        objective_config = model_monitoring.ObjectiveConfig(
            skew_detection_config=skew_config,
            drift_detection_config=prediction_drift_config,
            explanation_config=xai_config,
        )

        if data_source == _TEST_BQ_DATASOURCE:
            assert (
                objective_config.as_proto().training_dataset
                == expected_training_dataset
            )
        assert (
            objective_config.as_proto().training_prediction_skew_detection_config
            == skew_config.as_proto()
        )
        assert (
            objective_config.as_proto().prediction_drift_detection_config
            == prediction_drift_config.as_proto()
        )
        assert objective_config.as_proto().explanation_config == xai_config.as_proto()
        assert (
            _TEST_EMAIL1 in email_alert_config.as_proto().email_alert_config.user_emails
        )
        assert (
            _TEST_EMAIL2 in email_alert_config.as_proto().email_alert_config.user_emails
        )
        assert _TEST_EMAIL1 in alert_config.as_proto().email_alert_config.user_emails
        assert _TEST_EMAIL2 in alert_config.as_proto().email_alert_config.user_emails
        assert (
            _TEST_NOTIFICATION_CHANNEL in alert_config.as_proto().notification_channels
        )
        assert (
            random_sample_config.as_proto().random_sample_config.sample_rate
            == _TEST_SAMPLING_RATE
        )
        assert (
            schedule_config.as_proto().monitor_interval.seconds
            == _TEST_MONITORING_INTERVAL * 3600
        )

    @pytest.mark.parametrize("data_source", [_TEST_GCS_DATASOURCE])
    @pytest.mark.parametrize("data_format", ["other"])
    @pytest.mark.parametrize("skew_thresholds", _TEST_SKEW_THRESHOLDS)
    @pytest.mark.parametrize(
        "attribute_skew_thresholds", _TEST_ATTRIBUTE_SKEW_THRESHOLDS
    )
    def test_invalid_data_format(
        self, data_source, data_format, skew_thresholds, attribute_skew_thresholds
    ):
        if data_format == "other":
            with pytest.raises(ValueError) as e:
                model_monitoring.ObjectiveConfig(
                    skew_detection_config=model_monitoring.SkewDetectionConfig(
                        data_source=data_source,
                        skew_thresholds=skew_thresholds,
                        target_field=_TEST_TARGET_FIELD,
                        attribute_skew_thresholds=attribute_skew_thresholds,
                        data_format=data_format,
                    )
                ).as_proto()
            assert (
                "Unsupported value in skew detection config. `data_format` must be one of tf-record, csv, or jsonl"
                in str(e.value)
            )
