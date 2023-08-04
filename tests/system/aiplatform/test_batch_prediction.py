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

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import (
    job_state_v1beta1 as gca_job_state_v1beta1,
)
from tests.system.aiplatform import e2e_base


_PERMANENT_CHURN_MODEL_ID = "5295507484113371136"
_PERMANENT_CHURN_TRAINING_DATA = (
    "gs://ucaip-samples-us-central1/model/churn/churn_bp_insample_short.csv"
)
_PERMANENT_CHURN_TESTING_DATA = (
    "gs://ucaip-samples-us-central1/model/churn/churn_bp_outsample_short.jsonl"
)
_PERMANENT_CHURN_GS_DEST = "gs://ucaip-samples-us-central1/model/churn/"

_TEST_JOB_DISPLAY_NAME = "system"
_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2
_TEST_STARTING_REPLICA_COUNT = 2
_TEST_MAX_REPLICA_COUNT = 12
_TEST_BATCH_SIZE = 16


class TestBatchPredictionJob(e2e_base.TestEndToEnd):
    _temp_prefix = "temp_e2e_batch_prediction_test_"

    def test_model_monitoring(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)
        model = aiplatform.Model(_PERMANENT_CHURN_MODEL_ID)
        skew_detection_config = aiplatform.model_monitoring.SkewDetectionConfig(
            data_source=_PERMANENT_CHURN_TRAINING_DATA,
            target_field="churned",
            skew_thresholds={"cnt_level_start_quickplay": 0.001},
            data_format="csv",
        )
        drift_detection_config = aiplatform.model_monitoring.DriftDetectionConfig(
            drift_thresholds={"cnt_user_engagement": 0.01}
        )
        mm_config = aiplatform.model_monitoring.ObjectiveConfig(
            skew_detection_config=skew_detection_config,
            drift_detection_config=drift_detection_config,
        )

        bpj = aiplatform.BatchPredictionJob.create(
            job_display_name=self._make_display_name(key=_TEST_JOB_DISPLAY_NAME),
            model_name=model,
            gcs_source=_PERMANENT_CHURN_TESTING_DATA,
            gcs_destination_prefix=_PERMANENT_CHURN_GS_DEST,
            machine_type=_TEST_MACHINE_TYPE,
            starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
            max_replica_count=_TEST_MAX_REPLICA_COUNT,
            generate_explanation=True,
            sync=True,
            model_monitoring_objective_config=mm_config,
        )
        bpj.wait_for_resource_creation()
        bpj.wait()
        gapic_bpj = bpj._gca_resource
        bpj.delete()

        assert gapic_bpj.state == gca_job_state_v1beta1.JobState.JOB_STATE_SUCCEEDED
        assert (
            gapic_bpj.model_monitoring_config.objective_configs[0]
            == mm_config.as_proto()
        )
