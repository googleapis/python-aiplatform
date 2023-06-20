# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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
    schedule_v1beta1 as gca_schedule,
)
from google.cloud.aiplatform.preview.pipelinejobschedule import (
    pipeline_job_schedules,
)
from tests.system.aiplatform import e2e_base

from kfp import components
from kfp.v2 import compiler

import pytest
from google.protobuf.json_format import MessageToDict


@pytest.mark.usefixtures(
    "tear_down_resources", "prepare_staging_bucket", "delete_staging_bucket"
)
class TestPreviewPipelineJobSchedule(e2e_base.TestEndToEnd):
    _temp_prefix = "tmpvrtxsdk-e2e-pjs"

    def test_create_get_pause_resume_update_list(self, shared_state):
        # Components:
        def train(
            number_of_epochs: int,
            learning_rate: float,
        ):
            print(f"number_of_epochs={number_of_epochs}")
            print(f"learning_rate={learning_rate}")

        train_op = components.create_component_from_func(train)

        # Pipeline:
        def training_pipeline(number_of_epochs: int = 2):
            train_op(
                number_of_epochs=number_of_epochs,
                learning_rate="0.1",
            )

        # Creating the pipeline job schedule.
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        ir_file = "pipeline.json"
        compiler.Compiler().compile(
            pipeline_func=training_pipeline,
            package_path=ir_file,
            pipeline_name="system-test-training-pipeline",
        )
        job = aiplatform.PipelineJob(
            template_path=ir_file,
            display_name="display_name",
        )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=job, display_name="pipeline_job_schedule_display_name"
        )

        max_run_count = 2
        cron_expression = "*/5 * * * *"
        pipeline_job_schedule.create(
            cron_expression=cron_expression,
            max_run_count=max_run_count,
            max_concurrent_run_count=2,
        )

        shared_state.setdefault("resources", []).append(pipeline_job_schedule)

        # Pausing the pipeline job schedule.
        pipeline_job_schedule.pause()
        assert pipeline_job_schedule.state == gca_schedule.Schedule.State.PAUSED

        # Before updating, confirm the cron_expression is correctly set from the create step.
        assert pipeline_job_schedule.cron_expression == cron_expression

        # Updating the pipeline job schedule.
        new_cron_expression = "* * * * *"
        pipeline_job_schedule.update(cron_expression=new_cron_expression)
        assert pipeline_job_schedule.cron_expression == new_cron_expression

        # Resuming the pipeline job schedule.
        pipeline_job_schedule.resume(catch_up=True)
        assert pipeline_job_schedule.state == gca_schedule.Schedule.State.ACTIVE

        pipeline_job_schedule.wait()

        # Confirming that correct number of runs were scheduled and completed by this pipeline job schedule.
        list_jobs_with_read_mask = pipeline_job_schedule.list_jobs(
            enable_simple_view=True
        )
        assert len(list_jobs_with_read_mask) == max_run_count

        list_jobs_without_read_mask = pipeline_job_schedule.list_jobs()

        # enable_simple_view=True should apply the `read_mask` filter to limit PipelineJob fields returned
        assert "serviceAccount" in MessageToDict(
            list_jobs_without_read_mask[0].gca_resource._pb
        )
        assert "serviceAccount" not in MessageToDict(
            list_jobs_with_read_mask[0].gca_resource._pb
        )
