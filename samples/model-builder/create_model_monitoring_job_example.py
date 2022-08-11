# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.cloud import aiplatform
from google.cloud.aiplatform import model_monitoring
from typing import Optional, Dict, Union, List


#  [START aiplatform_sdk_create_model_monitoring_job_example]
def create_model_monitoring_job_example(
    project: str,
    location: str,
    display_name: str,
    endpoint: Union[str, "aiplatform.Endpoint"],
    skew_thresholds: Optional[Dict[str, float]] = None,
    attribute_skew_thresholds: Optional[Dict[str, float]] = None,
    drift_thresholds: Optional[Dict[str, float]] = None,
    sample_rate: Optional[float] = None,
    emails: Optional[List[str]] = None,
    schedule: Optional[float] = None,
    target_field: Optional[str] = None,
    data_source: Optional[str] = None,
    data_format: Optional[str] = None,
):
    aiplatform.init(project=project, location=location)

    skew_detection_config = model_monitoring.SkewDetectionConfig(
        data_source=data_source,
        target_field=target_field,
        skew_thresholds=skew_thresholds,
        attribute_skew_thresholds=attribute_skew_thresholds,
        data_format=data_format,
    )

    drift_detection_config = model_monitoring.DriftDetectionConfig(
        drift_thresholds=drift_thresholds
    )

    objective_config = model_monitoring.ObjectiveConfig(
        skew_detection_config=skew_detection_config,
        drift_detection_config=drift_detection_config,
    )

    monitoring_job = aiplatform.ModelDeploymentMonitoringJob.create(
        display_name=display_name,
        endpoint=endpoint,
        logging_sampling_strategy=model_monitoring.RandomSampleConfig(
            sample_rate=sample_rate
        ),
        schedule_config=model_monitoring.ScheduleConfig(monitor_interval=schedule),
        alert_config=model_monitoring.EmailAlertConfig(user_emails=emails),
        objective_config=objective_config,
    )

    return monitoring_job


#  [END aiplatform_sdk_create_model_monitoring_job_example]
