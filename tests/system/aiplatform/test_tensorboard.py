# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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


class TestTensorboard(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-e2e-test"

    def test_create_and_get_tensorboard(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        display_name = self._make_display_name("tensorboard")

        tb = aiplatform.Tensorboard.create(display_name=display_name)

        shared_state["resources"] = [tb]

        get_tb = aiplatform.Tensorboard(tb.resource_name)

        assert tb.resource_name == get_tb.resource_name

        list_tb = aiplatform.Tensorboard.list()

        assert len(list_tb) > 0

        tb_experiment = aiplatform.TensorboardExperiment.create(
            tensorboard_experiment_id="vertex-sdk-e2e-test-experiment",
            tensorboard_name=tb.resource_name,
            display_name=self._make_display_name("tensorboard_experiment"),
            description="Vertex SDK Integration test.",
            labels={"test": "labels"},
        )

        shared_state["resources"].append(tb_experiment)

        get_tb_experiment = aiplatform.TensorboardExperiment(
            tb_experiment.resource_name
        )

        assert tb_experiment.resource_name == get_tb_experiment.resource_name

        list_tb_experiment = aiplatform.TensorboardExperiment.list(
            tensorboard_name=tb.resource_name
        )

        assert len(list_tb_experiment) > 0

        tb_run = aiplatform.TensorboardRun.create(
            tensorboard_run_id="test-run",
            tensorboard_experiment_name=tb_experiment.resource_name,
            description="Vertex SDK Integration test run",
            labels={"test": "labels"},
        )

        shared_state["resources"].append(tb_run)

        get_tb_run = aiplatform.TensorboardRun(tb_run.resource_name)

        assert tb_run.resource_name == get_tb_run.resource_name

        list_tb_run = aiplatform.TensorboardRun.list(
            tensorboard_experiment_name=tb_experiment.resource_name
        )

        assert len(list_tb_run) > 0
