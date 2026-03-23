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
    client._api_client._http_options.api_version = "v1beta1"
    evaluation_run_name = (
        "projects/977012026409/locations/us-central1/evaluationRuns/3940878372367761408"
    )
    evaluation_run = client.evals.get_evaluation_run(
        name=evaluation_run_name, include_evaluation_items=True
    )
    check_run_3940878372367761408(client, evaluation_run, evaluation_run_name)
    check_run_3940878372367761408_evaluation_item_results(
        client, evaluation_run, evaluation_run_name
    )


def test_get_eval_run_include_evaluation_items_false(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    client._api_client._http_options.api_version = "v1beta1"
    evaluation_run_name = (
        "projects/977012026409/locations/us-central1/evaluationRuns/3940878372367761408"
    )
    evaluation_run = client.evals.get_evaluation_run(name=evaluation_run_name)
    check_run_3940878372367761408(client, evaluation_run, evaluation_run_name)
    assert evaluation_run.evaluation_item_results is None


def test_get_eval_run_bq_source(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/1968424880881795072"
    )
    evaluation_run = client.evals.get_evaluation_run(
        name=evaluation_run_name, include_evaluation_items=True
    )
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
    evaluation_run = client.evals.get_evaluation_run(
        name=evaluation_run_name, include_evaluation_items=True
    )
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
    client._api_client._http_options.api_version = "v1beta1"
    eval_run_id = "3940878372367761408"
    evaluation_run_name = (
        f"projects/977012026409/locations/us-central1/evaluationRuns/{eval_run_id}"
    )
    evaluation_run = await client.aio.evals.get_evaluation_run(name=eval_run_id)
    check_run_3940878372367761408(client, evaluation_run, evaluation_run_name)
    assert evaluation_run.evaluation_item_results is None


def check_run_3940878372367761408(
    client, evaluation_run: types.EvaluationRun, evaluation_run_name: str
):
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.name == evaluation_run_name
    assert (
        evaluation_run.display_name
        == "evaluation_run_9a464a39-6d40-4d4e-a5e2-a4ceabea4b15"
    )
    assert evaluation_run.metadata == {"pipeline_id": "8162140658019074048"}
    assert evaluation_run.create_time == datetime.datetime(
        2026, 3, 18, 1, 10, 13, 360535, tzinfo=datetime.timezone.utc
    )
    assert evaluation_run.completion_time == datetime.datetime(
        2026, 3, 18, 1, 11, 0, 448191, tzinfo=datetime.timezone.utc
    )
    assert evaluation_run.state == types.EvaluationRunState.SUCCEEDED
    assert evaluation_run.evaluation_set_snapshot == (
        "projects/977012026409/locations/us-central1/evaluationSets/3885168317211607040"
    )
    assert (
        evaluation_run.data_source.evaluation_set
        == "projects/977012026409/locations/us-central1/evaluationSets/3991900109943078912"
    )
    assert evaluation_run.evaluation_run_results.evaluation_set == (
        "projects/977012026409/locations/us-central1/evaluationSets/3885168317211607040"
    )
    assert evaluation_run.evaluation_run_results.summary_metrics.total_items == 2
    assert evaluation_run.error is None


def check_run_3940878372367761408_evaluation_item_results(
    client, evaluation_run: types.EvaluationRun, evaluation_run_name: str
):
    eval_result = evaluation_run.evaluation_item_results
    assert isinstance(eval_result, types.EvaluationResult)
    assert eval_result.summary_metrics == [
        types.AggregatedMetricResult(
            metric_name="general_quality_v1",
            mean_score=0.13333333656191826,
            stdev_score=0.03333333507180214,
        ),
    ]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_evaluation_run",
)
