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
USER_EMAIL = "rosiezou@cloudadvocacyorg.joonix.net"
PERMANENT_CHURN_MODEL_ID = "5295507484113371136"
CHURN_MODEL_PATH = "gs://mco-mm/churn"
DEFAULT_INPUT = {
    "cnt_ad_reward": 0,
    "cnt_challenge_a_friend": 0,
    "cnt_completed_5_levels": 1,
    "cnt_level_complete_quickplay": 3,
    "cnt_level_end_quickplay": 5,
    "cnt_level_reset_quickplay": 2,
    "cnt_level_start_quickplay": 6,
    "cnt_post_score": 34,
    "cnt_spend_virtual_currency": 0,
    "cnt_use_extra_steps": 0,
    "cnt_user_engagement": 120,
    "country": "Denmark",
    "dayofweek": 3,
    "julianday": 254,
    "language": "da-dk",
    "month": 9,
    "operating_system": "IOS",
    "user_pseudo_id": "104B0770BAE16E8B53DF330C95881893",
}

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


@pytest.mark.usefixtures("tear_down_resources")
class TestModelDeploymentMonitoring(e2e_base.TestEndToEnd):
    _temp_prefix = "temp_e2e_model_monitoring_test_"

    def test_create_endpoint(self, shared_state):
        # initial setup
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
        self.endpoint = aiplatform.Endpoint.create(self._make_display_name("endpoint"))
        shared_state["resources"] = [self.endpoint]
        self.model = aiplatform.Model(PERMANENT_CHURN_MODEL_ID)
        self.endpoint.deploy(
            self.model,
            deployed_model_display_name=self._make_display_name(key=JOB_NAME),
        )
        self.endpoint.deploy(
            self.model,
            deployed_model_display_name=self._make_display_name(key=JOB_NAME),
            traffic_percentage=50,
        )

    def test_mdm_two_models_one_valid_config(self, shared_state):
        """
        Enable model monitoring on two existing models deployed to the same endpoint.
        """
        assert len(shared_state["resources"]) == 1
        self.endpoint = shared_state["resources"][0]
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
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
        )

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
        assert len(gapic_job.model_deployment_monitoring_objective_configs) == 2

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

        # delete this job and re-configure it to only enable drift detection for faster testing
        job.delete()
        job_resource = job._gca_resource.name

        # test job delete
        with pytest.raises(core_exceptions.NotFound):
            job.api_client.get_model_deployment_monitoring_job(name=job_resource)

    # TODO(b/275569167) Uncomment this after timeout issue is resolved
    @pytest.mark.skip(reason="System tests timing out")
    def test_mdm_pause_and_update_config(self, shared_state):
        """Test objective config updates for existing MDM job"""
        assert len(shared_state["resources"]) == 1
        self.endpoint = shared_state["resources"][0]
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
        job = aiplatform.ModelDeploymentMonitoringJob.create(
            display_name=self._make_display_name(key=JOB_NAME),
            logging_sampling_strategy=sampling_strategy,
            schedule_config=schedule_config,
            alert_config=alert_config,
            objective_configs=model_monitoring.ObjectiveConfig(
                drift_detection_config=drift_config
            ),
            create_request_timeout=3600,
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            endpoint=self.endpoint,
        )
        # test unsuccessful job update when it's pending
        DRIFT_THRESHOLDS["cnt_user_engagement"] += 0.01
        new_obj_config = model_monitoring.ObjectiveConfig(
            drift_detection_config=model_monitoring.DriftDetectionConfig(
                drift_thresholds=DRIFT_THRESHOLDS,
                attribute_drift_thresholds=ATTRIB_DRIFT_THRESHOLDS,
            )
        )
        if job.state == gca_job_state.JobState.JOB_STATE_PENDING:
            with pytest.raises(core_exceptions.FailedPrecondition):
                job.update(objective_configs=new_obj_config)

        # generate traffic to force MDM job to come online
        for i in range(2000):
            DEFAULT_INPUT["cnt_user_engagement"] += i
            self.endpoint.predict([DEFAULT_INPUT], use_raw_predict=True)

        # test job update
        while True:
            time.sleep(1)
            if job.state == gca_job_state.JobState.JOB_STATE_RUNNING:
                job.update(objective_configs=new_obj_config)
                break

        # verify job update
        while True:
            time.sleep(1)
            if job.state == gca_job_state.JobState.JOB_STATE_RUNNING:
                gca_obj_config = (
                    job._gca_resource.model_deployment_monitoring_objective_configs[
                        0
                    ].objective_config
                )
                assert (
                    gca_obj_config.prediction_drift_detection_config
                    == new_obj_config.drift_detection_config.as_proto()
                )
                break

        # test pause
        job.pause()
        while job.state != gca_job_state.JobState.JOB_STATE_PAUSED:
            time.sleep(1)
        job.delete()

        # confirm deletion
        with pytest.raises(core_exceptions.NotFound):
            job.state

    def test_mdm_two_models_two_valid_configs(self, shared_state):
        assert len(shared_state["resources"]) == 1
        self.endpoint = shared_state["resources"][0]
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
        [deployed_model1, deployed_model2] = list(
            map(lambda x: x.id, self.endpoint.list_models())
        )
        all_configs = {
            deployed_model1: objective_config,
            deployed_model2: objective_config2,
        }
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
        )

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

    def test_mdm_invalid_config_incorrect_model_id(self, shared_state):
        assert len(shared_state["resources"]) == 1
        self.endpoint = shared_state["resources"][0]
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
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
                deployed_model_ids=[""],
            )
        assert "Invalid model ID" in str(e.value)

    def test_mdm_invalid_config_xai(self, shared_state):
        assert len(shared_state["resources"]) == 1
        self.endpoint = shared_state["resources"][0]
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
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
            )
        assert (
            "`explanation_config` should only be enabled if the model has `explanation_spec populated"
            in str(e.value)
        )

    def test_mdm_two_models_invalid_configs_xai(self, shared_state):
        assert len(shared_state["resources"]) == 1
        self.endpoint = shared_state["resources"][0]
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
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
            )
        assert (
            "`explanation_config` should only be enabled if the model has `explanation_spec populated"
            in str(e.value)
        )
