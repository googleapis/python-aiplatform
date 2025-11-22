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
from google.genai import types as genai_types
import datetime
import pytest


def test_get_eval_run(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    client._api_client._http_options.api_version = "v1beta1"
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/5133048044039700480"
    )
    evaluation_run = client.evals.get_evaluation_run(
        name=evaluation_run_name, include_evaluation_items=True
    )
    check_run_5133048044039700480(client, evaluation_run, evaluation_run_name)
    check_run_5133048044039700480_evaluation_item_results(
        client, evaluation_run, evaluation_run_name
    )


def test_get_eval_run_include_evaluation_items_false(client):
    """Tests that get_evaluation_run() returns a correctly structured EvaluationRun."""
    client._api_client._http_options.api_version = "v1beta1"
    evaluation_run_name = (
        "projects/503583131166/locations/us-central1/evaluationRuns/5133048044039700480"
    )
    evaluation_run = client.evals.get_evaluation_run(name=evaluation_run_name)
    check_run_5133048044039700480(client, evaluation_run, evaluation_run_name)
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
    eval_run_id = "5133048044039700480"
    evaluation_run_name = (
        f"projects/503583131166/locations/us-central1/evaluationRuns/{eval_run_id}"
    )
    evaluation_run = await client.aio.evals.get_evaluation_run(name=eval_run_id)
    check_run_5133048044039700480(client, evaluation_run, evaluation_run_name)
    assert evaluation_run.evaluation_item_results is None


def check_run_5133048044039700480(
    client, evaluation_run: types.EvaluationRun, evaluation_run_name: str
):
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.name == evaluation_run_name
    assert evaluation_run.display_name == "sdk-test-1"
    assert evaluation_run.metadata == {"pipeline_id": "4868043098678099968"}
    assert evaluation_run.create_time == datetime.datetime(
        2025, 10, 21, 19, 25, 58, 669441, tzinfo=datetime.timezone.utc
    )
    assert evaluation_run.completion_time == datetime.datetime(
        2025, 10, 21, 19, 26, 15, 855568, tzinfo=datetime.timezone.utc
    )
    assert evaluation_run.state == types.EvaluationRunState.SUCCEEDED
    assert evaluation_run.evaluation_set_snapshot == (
        "projects/503583131166/locations/us-central1/evaluationSets/3122155626046685184"
    )
    assert (
        evaluation_run.data_source.evaluation_set
        == "projects/503583131166/locations/us-central1/evaluationSets/3122155626046685184"
    )
    assert evaluation_run.evaluation_run_results.evaluation_set == (
        "projects/503583131166/locations/us-central1/evaluationSets/129513673658990592"
    )
    assert evaluation_run.inference_configs == {
        "gemini-2.0-flash-001@default": types.EvaluationRunInferenceConfig(
            agent_config=types.EvaluationRunAgentConfig(
                developer_instruction={
                    "parts": [{"text": "example agent developer instruction"}]
                },
                tools=[
                    genai_types.Tool(
                        function_declarations=[
                            genai_types.FunctionDeclaration(
                                name="check_chime",
                                description="Check chime.",
                                parameters={
                                    "type": "OBJECT",
                                    "properties": {
                                        "nums": {
                                            "type": "STRING",
                                            "description": "List of numbers to be verified.",
                                        }
                                    },
                                    "required": ["nums"],
                                },
                            ),
                        ],
                    )
                ],
            )
        ),
    }
    assert evaluation_run.evaluation_run_results.summary_metrics == (
        types.SummaryMetric(
            metrics={
                "gemini-2.0-flash-001@default/safety_v1/VARIANCE": 0.08950617055834077,
                "gemini-2.0-flash-001@default/safety_v1/MAXIMUM": 1,
                "gemini-2.0-flash-001@default/universal/AVERAGE": 0.7888888915379842,
                "gemini-2.0-flash-001@default/universal/P90": 1,
                "gemini-2.0-flash-001@default/safety_v1/MEDIAN": 1,
                "gemini-2.0-flash-001@default/universal/P95": 1,
                "gemini-2.0-flash-001@default/universal/VARIANCE": 0.08950617055834077,
                "gemini-2.0-flash-001@default/universal/STANDARD_DEVIATION": 0.2991758188061675,
                "gemini-2.0-flash-001@default/universal/MEDIAN": 1,
                "gemini-2.0-flash-001@default/safety_v1/STANDARD_DEVIATION": 0.2991758188061675,
                "gemini-2.0-flash-001@default/universal/MODE": 1,
                "gemini-2.0-flash-001@default/safety_v1/MODE": 1,
                "gemini-2.0-flash-001@default/safety_v1/MINIMUM": 0.3333333432674408,
                "gemini-2.0-flash-001@default/safety_v1/P90": 1,
                "gemini-2.0-flash-001@default/safety_v1/P95": 1,
                "gemini-2.0-flash-001@default/universal/P99": 1,
                "gemini-2.0-flash-001@default/safety_v1/AVERAGE": 0.7888888915379842,
                "gemini-2.0-flash-001@default/universal/MINIMUM": 0.3333333432674408,
                "gemini-2.0-flash-001@default/universal/MAXIMUM": 1,
                "gemini-2.0-flash-001@default/safety_v1/P99": 1,
            },
            total_items=3,
        )
    )
    assert evaluation_run.error is None


def check_run_5133048044039700480_evaluation_item_results(
    client, evaluation_run: types.EvaluationRun, evaluation_run_name: str
):
    eval_result = evaluation_run.evaluation_item_results
    assert isinstance(eval_result, types.EvaluationResult)
    assert eval_result.summary_metrics == [
        types.AggregatedMetricResult(
            metric_name="safety_v1",
            mean_score=0.7888888915379842,
            stdev_score=0.2991758188061675,
        ),
        types.AggregatedMetricResult(
            metric_name="universal",
            mean_score=0.7888888915379842,
            stdev_score=0.2991758188061675,
        ),
    ]
    # Check the agent info.
    assert eval_result.agent_info == types.evals.AgentInfo(
        name="gemini-2.0-flash-001@default",
        instruction="example agent developer instruction",
        description=None,
        tool_declarations=[
            genai_types.Tool(
                function_declarations=[
                    genai_types.FunctionDeclaration(
                        name="check_chime",
                        description="Check chime.",
                        parameters={
                            "type": "OBJECT",
                            "properties": {
                                "nums": {
                                    "type": "STRING",
                                    "description": "List of numbers to be verified.",
                                }
                            },
                            "required": ["nums"],
                        },
                    ),
                ],
            )
        ],
    )
    # Check the first eval case result.
    eval_case_result = eval_result.eval_case_results[0]
    assert isinstance(eval_case_result, types.EvalCaseResult)
    # Check the response candidate results.
    response_candidate_result = eval_case_result.response_candidate_results[0]
    assert response_candidate_result.response_index == 0
    universal_metric_result = response_candidate_result.metric_results["universal"]
    assert isinstance(universal_metric_result, types.EvalCaseMetricResult)
    assert universal_metric_result.metric_name == "universal"
    assert universal_metric_result.score > 0
    assert universal_metric_result.explanation is None
    # Check the first rubric verdict.
    rubric_verdict_0 = universal_metric_result.rubric_verdicts[0]
    assert isinstance(rubric_verdict_0, types.evals.RubricVerdict)
    assert rubric_verdict_0.evaluated_rubric == types.evals.Rubric(
        content=types.evals.RubricContent(
            property=types.evals.RubricContentProperty(
                description="The response is in English."
            )
        ),
        importance="HIGH",
        type="LANGUAGE:PRIMARY_RESPONSE_LANGUAGE",
    )
    assert rubric_verdict_0.reasoning is not None
    assert rubric_verdict_0.verdict is True
    # Check the first evaluation dataset.
    eval_dataset = eval_result.evaluation_dataset[0]
    assert isinstance(eval_dataset, types.EvaluationDataset)
    assert eval_dataset.candidate_name == "gemini-2.0-flash-001@default"
    assert eval_dataset.eval_dataset_df.shape[0] == 3
    assert eval_dataset.eval_dataset_df.shape[1] > 3


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.get_evaluation_run",
)
