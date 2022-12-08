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

import pytest

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base


@pytest.mark.usefixtures("tear_down_resources")
class TestTensorboard(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-e2e-test"

    def test_create_and_get_tensorboard(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        display_name = self._make_display_name("tensorboard")

        tb = aiplatform.Tensorboard.create(
            display_name=display_name,
            create_request_timeout=None,
        )

        shared_state["resources"] = [tb]
        shared_state["tensorboard"] = tb

        get_tb = aiplatform.Tensorboard(tb.resource_name)

        assert tb.resource_name == get_tb.resource_name

        list_tb = aiplatform.Tensorboard.list()

        assert len(list_tb) > 0

    def test_create_and_get_tensorboard_experiment(self, shared_state):
        assert shared_state["tensorboard"]
        tb = shared_state["tensorboard"]

        tb_experiment = aiplatform.TensorboardExperiment.create(
            tensorboard_experiment_id="vertex-sdk-e2e-test-experiment",
            tensorboard_name=tb.resource_name,
            display_name=self._make_display_name("tensorboard_experiment"),
            description="Vertex SDK Integration test.",
            labels={"test": "labels"},
            create_request_timeout=None,
        )

        shared_state["resources"].append(tb_experiment)
        shared_state["tensorboard_experiment"] = tb_experiment

        get_tb_experiment = aiplatform.TensorboardExperiment(
            tb_experiment.resource_name
        )

        assert tb_experiment.resource_name == get_tb_experiment.resource_name

        list_tb_experiment = aiplatform.TensorboardExperiment.list(
            tensorboard_name=tb.resource_name
        )

        assert len(list_tb_experiment) > 0

    def test_create_and_get_tensorboard_run(self, shared_state):
        assert shared_state["tensorboard_experiment"]
        tb_experiment = shared_state["tensorboard_experiment"]

        tb_run = aiplatform.TensorboardRun.create(
            tensorboard_run_id="test-run",
            tensorboard_experiment_name=tb_experiment.resource_name,
            description="Vertex SDK Integration test run",
            labels={"test": "labels"},
            create_request_timeout=None,
        )

        shared_state["resources"].append(tb_run)
        shared_state["tensorboard_run"] = tb_run

        get_tb_run = aiplatform.TensorboardRun(tb_run.resource_name)

        assert tb_run.resource_name == get_tb_run.resource_name

        list_tb_run = aiplatform.TensorboardRun.list(
            tensorboard_experiment_name=tb_experiment.resource_name
        )

        assert len(list_tb_run) > 0

    def test_create_and_get_tensorboard_time_series(self, shared_state):
        assert shared_state["tensorboard_run"]
        tb_run = shared_state["tensorboard_run"]

        tb_time_series = aiplatform.TensorboardTimeSeries.create(
            display_name="test-time-series",
            tensorboard_run_name=tb_run.resource_name,
            description="Vertex SDK Integration test run",
        )

        shared_state["resources"].append(tb_time_series)
        shared_state["tensorboard_time_series"] = tb_time_series

        get_tb_time_series = aiplatform.TensorboardTimeSeries(
            tb_time_series.resource_name
        )

        assert tb_time_series.resource_name == get_tb_time_series.resource_name

        list_tb_time_series = aiplatform.TensorboardTimeSeries.list(
            tensorboard_run_name=tb_run.resource_name
        )

        assert len(list_tb_time_series) > 0

    def test_write_tensorboard_scalar_data(self, shared_state):
        assert shared_state["tensorboard_time_series"]
        assert shared_state["tensorboard_run"]
        tb_run = shared_state["tensorboard_run"]
        tb_time_series = shared_state["tensorboard_time_series"]

        tb_run.write_tensorboard_scalar_data(
            time_series_data={tb_time_series.display_name: 1.0},
            step=1,
        )
