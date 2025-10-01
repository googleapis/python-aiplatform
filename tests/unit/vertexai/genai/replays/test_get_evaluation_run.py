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
from vertexai._genai import _evals_visualization
import datetime
import pytest


def test_get_eval_run(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/1957799200510967808"
    )
    evaluation_run = client.evals.get_evaluation_run(name=evaluation_run_name)
    check_run_1957799200510967808(evaluation_run, evaluation_run_name)


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
    evaluation_run_name = (
        f"projects/503583131166/locations/us-central1/evaluationRuns/{eval_run_id}"
    )
    evaluation_run = await client.aio.evals.get_evaluation_run(name=eval_run_id)
    check_run_1957799200510967808(evaluation_run, evaluation_run_name)


def check_run_1957799200510967808(
    evaluation_run: types.EvaluationRun, evaluation_run_name: str
):
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
    assert evaluation_run.evaluation_results.evaluation_set == (
        "projects/503583131166/locations/us-central1/evaluationSets/102386522778501120"
    )
    assert evaluation_run.evaluation_results.summary_metrics == (
        types.SummaryMetric(
            metrics={
                "checkpoint_1/user_defined/MODE": 5,
                "checkpoint_2/universal/P90": 1,
                "gemini-2.0-flash-001@default/universal/AVERAGE": 0.6943817985685249,
                "gemini-2.0-flash-001@default/user_defined/P90": 5,
                "gemini-2.0-flash-001@default/universal/VARIANCE": 0.03146487552180889,
                "gemini-2.0-flash-001@default/user_defined/P95": 5,
                "checkpoint_1/universal/MINIMUM": 0.8571428656578064,
                "checkpoint_1/universal/VARIANCE": 0.0015452162403157982,
                "gemini-2.0-flash-001@default/universal/STANDARD_DEVIATION": 0.17738341388587855,
                "checkpoint_2/user_defined/P95": 5,
                "checkpoint_2/universal/MODE": 1,
                "checkpoint_2/user_defined/P90": 5,
                "checkpoint_2/universal/P99": 1,
                "gemini-2.0-flash-001@default/universal/MAXIMUM": 1,
                "checkpoint_2/universal/P95": 1,
                "checkpoint_2/user_defined/P99": 5,
                "checkpoint_2/universal/MINIMUM": 0.7777777910232544,
                "gemini-2.0-flash-001@default/universal/P90": 0.8777777791023255,
                "checkpoint_1/universal/AVERAGE": 0.986633250587865,
                "checkpoint_1/universal/MAXIMUM": 1,
                "checkpoint_1/universal/STANDARD_DEVIATION": 0.0393092386127714,
                "gemini-2.0-flash-001@default/universal/P95": 0.9000000059604645,
                "gemini-2.0-flash-001@default/user_defined/MAXIMUM": 5,
                "gemini-2.0-flash-001@default/user_defined/MINIMUM": 3,
                "gemini-2.0-flash-001@default/user_defined/VARIANCE": 0.4044321329639886,
                "checkpoint_2/user_defined/MAXIMUM": 5,
                "checkpoint_1/universal/MEDIAN": 1,
                "gemini-2.0-flash-001@default/universal/MEDIAN": 0.7142857313156128,
                "gemini-2.0-flash-001@default/user_defined/AVERAGE": 4.736842105263158,
                "gemini-2.0-flash-001@default/user_defined/MEDIAN": 5,
                "checkpoint_2/user_defined/AVERAGE": 5,
                "checkpoint_2/user_defined/MEDIAN": 5,
                "checkpoint_2/user_defined/STANDARD_DEVIATION": 0,
                "checkpoint_2/universal/MAXIMUM": 1,
                "checkpoint_1/universal/MODE": 1,
                "checkpoint_2/user_defined/MINIMUM": 5,
                "checkpoint_1/user_defined/VARIANCE": 0,
                "checkpoint_2/universal/VARIANCE": 0.005771725970062436,
                "checkpoint_2/universal/AVERAGE": 0.9438178790243048,
                "checkpoint_1/user_defined/MINIMUM": 5,
                "gemini-2.0-flash-001@default/universal/P99": 0.9800000011920929,
                "gemini-2.0-flash-001@default/universal/MINIMUM": 0.2857142984867096,
                "checkpoint_2/user_defined/VARIANCE": 0,
                "checkpoint_1/user_defined/MEDIAN": 5,
                "checkpoint_2/universal/STANDARD_DEVIATION": 0.07597187617837561,
                "checkpoint_1/user_defined/AVERAGE": 5,
                "checkpoint_1/user_defined/MAXIMUM": 5,
                "gemini-2.0-flash-001@default/user_defined/MODE": 5,
                "checkpoint_1/user_defined/P95": 5,
                "checkpoint_1/universal/P99": 1,
                "checkpoint_1/user_defined/P90": 5,
                "checkpoint_2/universal/MEDIAN": 1,
                "checkpoint_1/universal/P95": 1,
                "checkpoint_1/user_defined/STANDARD_DEVIATION": 0,
                "gemini-2.0-flash-001@default/user_defined/STANDARD_DEVIATION": 0.6359497880839245,
                "checkpoint_1/user_defined/P99": 5,
                "gemini-2.0-flash-001@default/universal/MODE": [
                    0.75,
                    0.8571428656578064,
                ],
                "checkpoint_2/user_defined/MODE": 5,
                "checkpoint_1/universal/P90": 1,
                "gemini-2.0-flash-001@default/user_defined/P99": 5,
            },
            total_items=19,
        )
    )
    assert evaluation_run.error is None
    eval_result = _evals_visualization._get_eval_result_from_eval_run(
        evaluation_run.evaluation_results
    )
    assert isinstance(eval_result, types.EvaluationResult)
    assert eval_result.summary_metrics == [
        types.AggregatedMetricResult(
            metric_name="checkpoint_1/universal",
            mean_score=0.986633250587865,
            stdev_score=0.0393092386127714,
        ),
        types.AggregatedMetricResult(
            metric_name="checkpoint_2/universal",
            mean_score=0.9438178790243048,
            stdev_score=0.07597187617837561,
        ),
        types.AggregatedMetricResult(
            metric_name="gemini-2.0-flash-001@default/universal",
            mean_score=0.6943817985685249,
            stdev_score=0.17738341388587855,
        ),
        types.AggregatedMetricResult(
            metric_name="checkpoint_1/user_defined", mean_score=5, stdev_score=0
        ),
        types.AggregatedMetricResult(
            metric_name="checkpoint_2/user_defined", mean_score=5, stdev_score=0
        ),
        types.AggregatedMetricResult(
            metric_name="gemini-2.0-flash-001@default/user_defined",
            mean_score=4.736842105263158,
            stdev_score=0.6359497880839245,
        ),
    ]


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_evaluation_run",
)
