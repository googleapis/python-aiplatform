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
import time

from google.cloud import aiplatform
from google.cloud.aiplatform import model_monitoring
from google.cloud.aiplatform.compat.types import job_state as gca_job_state
from google.api_core import exceptions as core_exceptions
from tests.system.aiplatform import e2e_base

from google.cloud.aiplatform_v1.types import (
    io as gca_io,
    model_monitoring as gca_model_monitoring,
)

# constants used for testing
USER_EMAIL = ""
PERMANENT_CHURN_ENDPOINT_ID = "8289570005524152320"
CHURN_MODEL_PATH = "gs://mco-mm/churn"

JOB_NAME = "churn"

# Sampling rate (optional, default=.8)
LOG_SAMPLE_RATE = 0.8

# Monitoring Interval in hours
MONITOR_INTERVAL = 1

# URI to training dataset.
DATASET_BQ_URI = "bq://mco-mm.bqmlga4.train"

# Prediction target column name in training dataset.
TARGET = "churned"

# Skew and drift thresholds.
DEFAULT_THRESHOLD_VALUE = 0.001
SKEW_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
DRIFT_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
ATTRIB_SKEW_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
ATTRIB_DRIFT_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}

# global test constants
sampling_strategy = model_monitoring.RandomSampleConfig(sample_rate=LOG_SAMPLE_RATE)

alert_config = model_monitoring.EmailAlertConfig(
    user_emails=[USER_EMAIL], enable_logging=True
)

schedule_config = model_monitoring.ScheduleConfig(monitor_interval=MONITOR_INTERVAL)

skew_config = model_monitoring.SkewDetectionConfig(
    data_source=DATASET_BQ_URI,
    skew_thresholds=SKEW_THRESHOLDS,
    attribute_skew_thresholds=ATTRIB_SKEW_THRESHOLDS,
    target_field=TARGET,
)

drift_config = model_monitoring.DriftDetectionConfig(
    drift_thresholds=DRIFT_THRESHOLDS,
    attribute_drift_thresholds=ATTRIB_DRIFT_THRESHOLDS,
)

drift_config2 = model_monitoring.DriftDetectionConfig(
    drift_thresholds=DRIFT_THRESHOLDS,
)

objective_config = model_monitoring.ObjectiveConfig(skew_config, drift_config)

objective_config2 = model_monitoring.ObjectiveConfig(skew_config, drift_config2)


class TestModelDeploymentMonitoring(e2e_base.TestEndToEnd):
    _temp_prefix = "temp_e2e_model_monitoring_test_"
    endpoint = aiplatform.Endpoint(PERMANENT_CHURN_ENDPOINT_ID)

    def test_mdm_two_models_one_valid_config(self):
        """
        Enable model monitoring on two existing models deployed to the same endpoint.
        """
        # test model monitoring configurations
        job = aiplatform.ModelDeploymentMonitoringJob.create(
            display_name=self._make_display_name(key=JOB_NAME),
            logging_sampling_strategy=sampling_strategy,
            schedule_config=schedule_config,
            alert_config=alert_config,
            objective_configs=objective_config,
            create_request_timeout=3600,
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            endpoint=self.endpoint,
            predict_instance_schema_uri="",
            analysis_instance_schema_uri="",
        )
        assert job is not None

        gapic_job = job._gca_resource
        assert (
            gapic_job.logging_sampling_strategy.random_sample_config.sample_rate
            == LOG_SAMPLE_RATE
        )
        assert (
            gapic_job.model_deployment_monitoring_schedule_config.monitor_interval.seconds
            == MONITOR_INTERVAL * 3600
        )
        assert (
            gapic_job.model_monitoring_alert_config.email_alert_config.user_emails
            == [USER_EMAIL]
        )
        assert gapic_job.model_monitoring_alert_config.enable_logging

        gca_obj_config = gapic_job.model_deployment_monitoring_objective_configs[
            0
        ].objective_config

        expected_training_dataset = (
            gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingDataset(
                bigquery_source=gca_io.BigQuerySource(input_uri=DATASET_BQ_URI),
                target_field=TARGET,
            )
        )
        assert gca_obj_config.training_dataset == expected_training_dataset
        assert (
            gca_obj_config.training_prediction_skew_detection_config
            == skew_config.as_proto()
        )
        assert (
            gca_obj_config.prediction_drift_detection_config == drift_config.as_proto()
        )

        job_resource = job._gca_resource.name

        # test job update and delete()
        timeout = time.time() + 3600
        new_obj_config = model_monitoring.ObjectiveConfig(skew_config)

        while time.time() < timeout:
            if job.state == gca_job_state.JobState.JOB_STATE_RUNNING:
                job.update(objective_configs=new_obj_config)
                assert str(job._gca_resource.prediction_drift_detection_config) == ""
                break
            time.sleep(5)

        job.delete()
        with pytest.raises(core_exceptions.NotFound):
            job.api_client.get_model_deployment_monitoring_job(name=job_resource)

    def test_mdm_two_models_two_valid_configs(self):
        [deployed_model1, deployed_model2] = list(
            map(lambda x: x.id, self.endpoint.list_models())
        )
        all_configs = {
            deployed_model1: objective_config,
            deployed_model2: objective_config2,
        }
        job = None
        job = aiplatform.ModelDeploymentMonitoringJob.create(
            display_name=self._make_display_name(key=JOB_NAME),
            logging_sampling_strategy=sampling_strategy,
            schedule_config=schedule_config,
            alert_config=alert_config,
            objective_configs=all_configs,
            create_request_timeout=3600,
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            endpoint=self.endpoint,
            predict_instance_schema_uri="",
            analysis_instance_schema_uri="",
        )
        assert job is not None

        gapic_job = job._gca_resource
        assert (
            gapic_job.logging_sampling_strategy.random_sample_config.sample_rate
            == LOG_SAMPLE_RATE
        )
        assert (
            gapic_job.model_deployment_monitoring_schedule_config.monitor_interval.seconds
            == MONITOR_INTERVAL * 3600
        )
        assert (
            gapic_job.model_monitoring_alert_config.email_alert_config.user_emails
            == [USER_EMAIL]
        )
        assert gapic_job.model_monitoring_alert_config.enable_logging

        expected_training_dataset = (
            gca_model_monitoring.ModelMonitoringObjectiveConfig.TrainingDataset(
                bigquery_source=gca_io.BigQuerySource(input_uri=DATASET_BQ_URI),
                target_field=TARGET,
            )
        )

        for config in gapic_job.model_deployment_monitoring_objective_configs:
            gca_obj_config = config.objective_config
            deployed_model_id = config.deployed_model_id
            assert gca_obj_config.training_dataset == expected_training_dataset
            assert (
                gca_obj_config.training_prediction_skew_detection_config
                == all_configs[deployed_model_id].skew_detection_config.as_proto()
            )
            assert (
                gca_obj_config.prediction_drift_detection_config
                == all_configs[deployed_model_id].drift_detection_config.as_proto()
            )

        job.delete()

    def test_mdm_invalid_config_incorrect_model_id(self):
        with pytest.raises(ValueError) as e:
            aiplatform.ModelDeploymentMonitoringJob.create(
                display_name=self._make_display_name(key=JOB_NAME),
                logging_sampling_strategy=sampling_strategy,
                schedule_config=schedule_config,
                alert_config=alert_config,
                objective_configs=objective_config,
                create_request_timeout=3600,
                project=e2e_base._PROJECT,
                location=e2e_base._LOCATION,
                endpoint=self.endpoint,
                predict_instance_schema_uri="",
                analysis_instance_schema_uri="",
                deployed_model_ids=[""],
            )
        assert "Invalid model ID" in str(e.value)

    def test_mdm_invalid_config_xai(self):
        with pytest.raises(RuntimeError) as e:
            objective_config.explanation_config = model_monitoring.ExplanationConfig()
            aiplatform.ModelDeploymentMonitoringJob.create(
                display_name=self._make_display_name(key=JOB_NAME),
                logging_sampling_strategy=sampling_strategy,
                schedule_config=schedule_config,
                alert_config=alert_config,
                objective_configs=objective_config,
                create_request_timeout=3600,
                project=e2e_base._PROJECT,
                location=e2e_base._LOCATION,
                endpoint=self.endpoint,
                predict_instance_schema_uri="",
                analysis_instance_schema_uri="",
            )
        assert (
            "`explanation_config` should only be enabled if the model has `explanation_spec populated"
            in str(e.value)
        )

    def test_mdm_two_models_invalid_configs_xai(self):
        [deployed_model1, deployed_model2] = list(
            map(lambda x: x.id, self.endpoint.list_models())
        )
        objective_config.explanation_config = model_monitoring.ExplanationConfig()
        all_configs = {
            deployed_model1: objective_config,
            deployed_model2: objective_config2,
        }
        with pytest.raises(RuntimeError) as e:
            objective_config.explanation_config = model_monitoring.ExplanationConfig()
            aiplatform.ModelDeploymentMonitoringJob.create(
                display_name=self._make_display_name(key=JOB_NAME),
                logging_sampling_strategy=sampling_strategy,
                schedule_config=schedule_config,
                alert_config=alert_config,
                objective_configs=all_configs,
                create_request_timeout=3600,
                project=e2e_base._PROJECT,
                location=e2e_base._LOCATION,
                endpoint=self.endpoint,
                predict_instance_schema_uri="",
                analysis_instance_schema_uri="",
            )
        assert (
            "`explanation_config` should only be enabled if the model has `explanation_spec populated"
            in str(e.value)
        )
