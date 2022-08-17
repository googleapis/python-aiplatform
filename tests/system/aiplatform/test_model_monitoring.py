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
MODEL_DISPLAYNAME_KEY = "churn"
MODEL_DISPLAYNAME_KEY2 = "churn2"
IMAGE = "us-docker.pkg.dev/cloud-aiplatform/prediction/tf2-cpu.2-5:latest"
ENDPOINT = "us-central1-aiplatform.googleapis.com"
CHURN_MODEL_PATH = "gs://mco-mm/churn"
_DEFAULT_INPUT = {
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
SKEW_DEFAULT_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
SKEW_CUSTOM_THRESHOLDS = {"cnt_level_start_quickplay": 0.01}
DRIFT_DEFAULT_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
DRIFT_CUSTOM_THRESHOLDS = {"cnt_level_start_quickplay": 0.01}
ATTRIB_SKEW_DEFAULT_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
ATTRIB_SKEW_CUSTOM_THRESHOLDS = {"cnt_level_start_quickplay": 0.01}
ATTRIB_DRIFT_DEFAULT_THRESHOLDS = {
    "country": DEFAULT_THRESHOLD_VALUE,
    "cnt_user_engagement": DEFAULT_THRESHOLD_VALUE,
}
ATTRIB_DRIFT_CUSTOM_THRESHOLDS = {"cnt_level_start_quickplay": 0.01}

skew_thresholds = SKEW_DEFAULT_THRESHOLDS.copy()
skew_thresholds.update(SKEW_CUSTOM_THRESHOLDS)
drift_thresholds = DRIFT_DEFAULT_THRESHOLDS.copy()
drift_thresholds.update(DRIFT_CUSTOM_THRESHOLDS)
attrib_skew_thresholds = ATTRIB_SKEW_DEFAULT_THRESHOLDS.copy()
attrib_skew_thresholds.update(ATTRIB_SKEW_CUSTOM_THRESHOLDS)
attrib_drift_thresholds = ATTRIB_DRIFT_DEFAULT_THRESHOLDS.copy()
attrib_drift_thresholds.update(ATTRIB_DRIFT_CUSTOM_THRESHOLDS)

# global test constants
sampling_strategy = model_monitoring.RandomSampleConfig(sample_rate=LOG_SAMPLE_RATE)

alert_config = model_monitoring.EmailAlertConfig(
    user_emails=[USER_EMAIL], enable_logging=True
)

schedule_config = model_monitoring.ScheduleConfig(monitor_interval=MONITOR_INTERVAL)

skew_config = model_monitoring.SkewDetectionConfig(
    data_source=DATASET_BQ_URI,
    skew_thresholds=skew_thresholds,
    attribute_skew_thresholds=attrib_skew_thresholds,
    target_field=TARGET,
)

drift_config = model_monitoring.DriftDetectionConfig(
    drift_thresholds=drift_thresholds,
    attribute_drift_thresholds=attrib_drift_thresholds,
)

drift_config2 = model_monitoring.DriftDetectionConfig(
    drift_thresholds=drift_thresholds,
    attribute_drift_thresholds=ATTRIB_DRIFT_DEFAULT_THRESHOLDS,
)

objective_config = model_monitoring.ObjectiveConfig(skew_config, drift_config)

objective_config2 = model_monitoring.ObjectiveConfig(skew_config, drift_config2)


@pytest.mark.usefixtures("tear_down_resources")
class TestModelDeploymentMonitoring(e2e_base.TestEndToEnd):
    _temp_prefix = "temp_e2e_model_monitoring_test_"

    def temp_endpoint(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        model = aiplatform.Model.upload(
            display_name=self._make_display_name(key=MODEL_DISPLAYNAME_KEY),
            artifact_uri=CHURN_MODEL_PATH,
            serving_container_image_uri=IMAGE,
        )
        shared_state["resources"] = [model]
        endpoint = model.deploy(machine_type="n1-standard-2")
        predict_response = endpoint.predict(instances=[_DEFAULT_INPUT])
        assert len(predict_response.predictions) == 1
        shared_state["resources"].append(endpoint)
        return [endpoint, model]

    def temp_endpoint_with_two_models(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        model1 = aiplatform.Model.upload(
            display_name=self._make_display_name(key=MODEL_DISPLAYNAME_KEY),
            artifact_uri=CHURN_MODEL_PATH,
            serving_container_image_uri=IMAGE,
        )

        model2 = aiplatform.Model.upload(
            display_name=self._make_display_name(key=MODEL_DISPLAYNAME_KEY2),
            artifact_uri=CHURN_MODEL_PATH,
            serving_container_image_uri=IMAGE,
        )
        shared_state["resources"] = [model1, model2]
        endpoint = aiplatform.Endpoint.create(
            display_name=self._make_display_name(key=MODEL_DISPLAYNAME_KEY)
        )
        endpoint.deploy(
            model=model1, machine_type="n1-standard-2", traffic_percentage=100
        )
        endpoint.deploy(
            model=model2, machine_type="n1-standard-2", traffic_percentage=30
        )
        predict_response = endpoint.predict(instances=[_DEFAULT_INPUT])
        assert len(predict_response.predictions) == 1
        shared_state["resources"].append(endpoint)
        return [endpoint, model1, model2]

    def test_mdm_one_model_one_valid_config(self, shared_state):
        """
        Upload pre-trained churn model from local file and deploy it for prediction.
        """
        # test model monitoring configurations
        [temp_endpoint, model] = self.temp_endpoint(shared_state)

        job = None

        job = aiplatform.ModelDeploymentMonitoringJob.create(
            display_name=self._make_display_name(key=JOB_NAME),
            logging_sampling_strategy=sampling_strategy,
            schedule_config=schedule_config,
            alert_config=alert_config,
            objective_configs=objective_config,
            create_request_timeout=3600,
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            endpoint=temp_endpoint,
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
        temp_endpoint.undeploy_all()
        temp_endpoint.delete()
        model.delete()

    def test_mdm_two_models_two_valid_configs(self, shared_state):
        [
            temp_endpoint_with_two_models,
            model1,
            model2,
        ] = self.temp_endpoint_with_two_models(shared_state)
        [deployed_model1, deployed_model2] = list(
            map(lambda x: x.id, temp_endpoint_with_two_models.list_models())
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
            endpoint=temp_endpoint_with_two_models,
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
            assert (
                gca_obj_config.training_dataset == expected_training_dataset
            )
            assert (
                gca_obj_config.training_prediction_skew_detection_config
                == all_configs[deployed_model_id].skew_detection_config.as_proto()
            )
            assert (
                gca_obj_config.prediction_drift_detection_config
                == all_configs[deployed_model_id].drift_detection_config.as_proto()
            )

        job.delete()
        temp_endpoint_with_two_models.undeploy_all()
        temp_endpoint_with_two_models.delete()
        model1.delete()
        model2.delete()

    def test_mdm_invalid_config_incorrect_model_id(self, shared_state):
        [temp_endpoint, model] = self.temp_endpoint(shared_state)
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
                endpoint=temp_endpoint,
                predict_instance_schema_uri="",
                analysis_instance_schema_uri="",
                deployed_model_ids=[""],
            )
        assert "Invalid model ID" in str(e.value)
        temp_endpoint.undeploy_all()
        temp_endpoint.delete()
        model.delete()

    def test_mdm_invalid_config_xai(self, shared_state):
        [temp_endpoint, model] = self.temp_endpoint(shared_state)
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
                endpoint=temp_endpoint,
                predict_instance_schema_uri="",
                analysis_instance_schema_uri="",
            )
        assert (
            "`explanation_config` should only be enabled if the model has `explanation_spec populated"
            in str(e.value)
        )
        temp_endpoint.undeploy_all()
        temp_endpoint.delete()
        model.delete()

    def test_mdm_two_models_invalid_configs_xai(self, shared_state):
        [
            temp_endpoint_with_two_models,
            model1,
            model2,
        ] = self.temp_endpoint_with_two_models(shared_state)
        [deployed_model1, deployed_model2] = list(
            map(lambda x: x.id, temp_endpoint_with_two_models.list_models())
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
                endpoint=temp_endpoint_with_two_models,
                predict_instance_schema_uri="",
                analysis_instance_schema_uri="",
            )
        assert (
            "`explanation_config` should only be enabled if the model has `explanation_spec populated"
            in str(e.value)
        )
        temp_endpoint_with_two_models.undeploy_all()
        temp_endpoint_with_two_models.delete()
        model1.delete()
        model2.delete()
