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
from tests.system.aiplatform import e2e_base
import pytest

from google.protobuf.json_format import MessageToDict


@pytest.mark.usefixtures("tear_down_resources")
class TestPipelineJobSchedule(e2e_base.TestEndToEnd):
    _temp_prefix = "tmpvrtxsdk-e2e-pjs"

    def test_create_get_list(self, shared_state):
        from kfp import components

        # Components:
        def train(
            number_of_epochs: int,
            learning_rate: float,
        ):
            print(f"number_of_epochs={number_of_epochs}")
            print(f"learning_rate={learning_rate}")

        train_op = components.create_component_from_func(train)

        # Pipeline:
        def training_pipeline(number_of_epochs: int = 10):
            train_op(
                number_of_epochs=number_of_epochs,
                learning_rate="0.1",
            )

        # Creating the pipeline job schedule.
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )
        job = aiplatform.PipelineJob.from_pipeline_func(
            pipeline_func=training_pipeline,
        )

        pipeline_job_schedule = (
            aiplatform.preview.pipelinejobschedule.PipelineJobSchedule(
                pipeline_job=job, display_name="pipeline_job_schedule_display_name"
            )
        )

        pipeline_job_schedule.create(cron_expression="*/2 * * * *", max_run_count=2)

        shared_state.setdefault("resources", []).append(pipeline_job_schedule)

        pipeline_job_schedule.wait()

        list_with_read_mask = (
            aiplatform.preview.pipelinejobschedule.PipelineJobSchedule.list(
                enable_simple_view=True
            )
        )
        list_without_read_mask = (
            aiplatform.preview.pipelinejobschedule.PipelineJobSchedule.list()
        )

        # enable_simple_view=True should apply the `read_mask` filter to limit PipelineJobSchedule fields returned
        assert "allowQueueing" in MessageToDict(
            list_without_read_mask[0].gca_resource._pb
        )
        assert "allowQueueing" not in MessageToDict(
            list_with_read_mask[0].gca_resource._pb
        )
