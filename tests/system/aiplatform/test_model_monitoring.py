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

import random
import pytest

from google.cloud import aiplatform

from tests.system.aiplatform import e2e_base

# constants used for testing
USER_EMAIL = ""
MODEL_NAME = "churn"
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

# Monitoring Interval in seconds (optional, default=3600).
MONITOR_INTERVAL = 3600

# URI to training dataset.
DATASET_BQ_URI = "bq://mco-mm.bqmlga4.train"

# Prediction target column name in training dataset.
TARGET = "churned"
MDM_JOB_PREFIX = "modelDeploymentMonitoringJobs"
RESOURCE_ID = str(random.randint(10000000, 99999999))

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

# Sampling distributions for categorical features...
DAYOFWEEK = {1: 1040, 2: 1223, 3: 1352, 4: 1217, 5: 1078, 6: 1011, 7: 1110}
LANGUAGE = {
    "en-us": 4807,
    "en-gb": 678,
    "ja-jp": 419,
    "en-au": 310,
    "en-ca": 299,
    "de-de": 147,
    "en-in": 130,
    "en": 127,
    "fr-fr": 94,
    "pt-br": 81,
    "es-us": 65,
    "zh-tw": 64,
    "zh-hans-cn": 55,
    "es-mx": 53,
    "nl-nl": 37,
    "fr-ca": 34,
    "en-za": 29,
    "vi-vn": 29,
    "en-nz": 29,
    "es-es": 25,
}
OS = {"IOS": 3980, "ANDROID": 3798, "null": 253}
MONTH = {6: 3125, 7: 1838, 8: 1276, 9: 1718, 10: 74}
COUNTRY = {
    "United States": 4395,
    "India": 486,
    "Japan": 450,
    "Canada": 354,
    "Australia": 327,
    "United Kingdom": 303,
    "Germany": 144,
    "Mexico": 102,
    "France": 97,
    "Brazil": 93,
    "Taiwan": 72,
    "China": 65,
    "Saudi Arabia": 49,
    "Pakistan": 48,
    "Egypt": 46,
    "Netherlands": 45,
    "Vietnam": 42,
    "Philippines": 39,
    "South Africa": 38,
}


@pytest.mark.usefixtures("tear_down_resources")
class TestModelDeploymentMonitoring(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_model_upload_test"

    def test_mdm_one_model_one_config(self, shared_state):
        """
        Upload pre-trained churn model from local file and deploy it for prediction.
        Then launch a model monitoring job and generate artificial traffic.
        """
        print("test info:--------")
        print(e2e_base._PROJECT)
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        model = aiplatform.Model.upload(
            display_name=MODEL_NAME,
            artifact_uri=CHURN_MODEL_PATH,
            serving_container_image_uri=IMAGE,
        )

        shared_state["resources"] = [model]

        endpoint = model.deploy(machine_type="n1-standard-2")
        shared_state["resources"].append(endpoint)
        predict_response = endpoint.predict(instances=[_DEFAULT_INPUT])
        assert len(predict_response.predictions) == 1

        # test model monitoring configurations
        job = None

        sampling_strategy = aiplatform.model_monitoring.RandomSampleConfig(
            sample_rate=LOG_SAMPLE_RATE
        )

        alert_config = aiplatform.model_monitoring.EmailAlertConfig(
            user_emails=[USER_EMAIL], enable_logging=True
        )

        schedule_config = aiplatform.model_monitoring.ScheduleConfig(
            monitor_interval=MONITOR_INTERVAL
        )

        skew_config = aiplatform.model_monitoring.EndpointSkewDetectionConfig(
            data_source=DATASET_BQ_URI,
            skew_thresholds=skew_thresholds,
            attribute_skew_thresholds=attrib_skew_thresholds,
            target_field=TARGET,
        )
        drift_config = aiplatform.model_monitoring.EndpointDriftDetectionConfig(
            drift_thresholds=drift_thresholds,
            attribute_drift_thresholds=attrib_drift_thresholds,
        )

        objective_config = aiplatform.model_monitoring.EndpointObjectiveConfig(
            skew_config, drift_config
        )

        job = aiplatform.ModelDeploymentMonitoringJob.create(
            display_name=JOB_NAME,
            logging_sampling_strategy=sampling_strategy,
            monitor_interval=MONITOR_INTERVAL,
            schedule_config=schedule_config,
            alert_config=alert_config,
            objective_configs=objective_config,
            timeout=3600,
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            endpoint=endpoint.resource_name.split("/")[-1],
            predict_instance_schema_uri="",
            analysis_instance_schema_uri="",
        )
        assert job is not None
