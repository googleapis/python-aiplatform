# Copyright 2025 Google LLC
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
# pylint: disable=protected-access,bad-continuation,missing-function-docstring

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai import types
import datetime
import pytest


def test_get_eval_run(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/1957799200510967808"
    )
    evaluation_run = client.evals.get_evaluation_run(name=evaluation_run_name)
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.name == evaluation_run_name
    assert evaluation_run.display_name == "test2"
    assert evaluation_run.metadata == {"pipeline_id": "4460531348888616960"}
    assert evaluation_run.create_time == datetime.datetime(
        2025, 9, 8, 20, 55, 41, 833176, tzinfo=datetime.timezone.utc
    )
    assert evaluation_run.completion_time == datetime.datetime(
        2025, 9, 8, 20, 56, 13, 492971, tzinfo=datetime.timezone.utc
    )
    assert evaluation_run.state == types.EvaluationRunState.SUCCEEDED
    assert evaluation_run.evaluation_set_snapshot == (
        "projects/503583131166/locations/us-central1/evaluationSets/8069535738573619200"
    )
    assert evaluation_run.data_source.bigquery_request_set == types.BigQueryRequestSet(
        uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
        prompt_column="request",
        candidate_response_columns={
            "baseline_model_response": "baseline_model_response",
            "checkpoint_1": "checkpoint_1",
            "checkpoint_2": "checkpoint_2",
        },
    )
    assert evaluation_run.error is None


def test_get_eval_run_bq_source(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/1968424880881795072"
    )
    evaluation_run = client.evals.get_evaluation_run(name=evaluation_run_name)
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.name == evaluation_run_name
    assert evaluation_run.display_name == "test1"
    assert evaluation_run.data_source.bigquery_request_set == types.BigQueryRequestSet(
        uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
        prompt_column="request",
        rubrics_column="rubric",
        candidate_response_columns={
            "baseline_model_response": "baseline_model_response",
            "checkpoint_1": "checkpoint_1",
            "checkpoint_2": "checkpoint_2",
        },
        sampling_config=types.SamplingConfig(
            sampling_count=100,
            sampling_method=types.SamplingMethod.RANDOM,
            sampling_duration="60s",
        ),
    )


def test_get_eval_run_eval_set_source(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/6903525647549726720"
    )
    evaluation_run = client.evals.get_evaluation_run(name=evaluation_run_name)
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.name == evaluation_run_name
    assert evaluation_run.display_name == "test3"
    assert evaluation_run.data_source.evaluation_set == (
        "projects/503583131166/locations/us-central1/evaluationSets/6619939608513740800"
    )
    assert evaluation_run.state == types.EvaluationRunState.FAILED
    assert evaluation_run.error.message == (
        "code=INVALID_ARGUMENT, message=EvaluationRun 6903525647549726720 has no "
        "items, cause=null"
    )


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_get_eval_run_async(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    eval_run_id = "1957799200510967808"
    eval_run_name = (
        f"projects/503583131166/locations/us-central1/evaluationRuns/{eval_run_id}"
    )
    evaluation_run = await client.aio.evals.get_evaluation_run(name=eval_run_id)
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.name == eval_run_name
    assert evaluation_run.display_name == "test2"
    assert evaluation_run.data_source.bigquery_request_set == types.BigQueryRequestSet(
        uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
        prompt_column="request",
        candidate_response_columns={
            "baseline_model_response": "baseline_model_response",
            "checkpoint_1": "checkpoint_1",
            "checkpoint_2": "checkpoint_2",
        },
    )


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_evaluation_run",
)
