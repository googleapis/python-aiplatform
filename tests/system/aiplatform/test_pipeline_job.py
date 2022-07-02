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

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base


@pytest.mark.usefixtures("tear_down_resources")
class TestExperiments(e2e_base.TestEndToEnd):

    _temp_prefix = "tmpvrtxsdk-e2e"

    def test_add_pipeline_job_to_experiment(self, shared_state):
        from kfp.v2 import components

        # Components:
        def train(
            number_of_epochs: int,
            learning_rate: float,
        ):
            print(f"number_of_epochs={number_of_epochs}")
            print(f"learning_rate={learning_rate}")

        train_op = components.create_component_from_func(train)

        # Pipeline:
        def training_pipeline(number_of_epochs: int):
            train_op(
                number_of_epochs=number_of_epochs,
                learning_rate="0.1",
            )

        # Submitting the pipeline:
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )
        job = aiplatform.PipelineJob.from_pipeline_func(pipeline_func=training_pipeline)
        job.submit()

        shared_state["resources"].append(job)

        job.wait()
