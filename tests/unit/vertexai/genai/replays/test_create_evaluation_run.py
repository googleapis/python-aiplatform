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
import pytest


def test_create_eval_run_data_source_evaluation_set(client):
    """Tests that create_evaluation_run() creates a correctly structured EvaluationRun."""
    client._api_client._http_options.api_version = "v1beta1"
    tool = genai_types.Tool(
        function_declarations=[
            genai_types.FunctionDeclaration(
                name="get_weather",
                description="Get weather in a location",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                },
            )
        ]
    )
    evaluation_run = client.evals.create_evaluation_run(
        name="test4",
        display_name="test4",
        data_source=types.EvaluationRunDataSource(
            evaluation_set="projects/503583131166/locations/us-central1/evaluationSets/6619939608513740800"
        ),
        agent_info=types.AgentInfo(
            name="agent-1",
            instruction="agent-1 instruction",
            tool_declarations=[tool],
        ),
        dest="gs://lakeyk-test-limited/eval_run_output",
    )
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.display_name == "test4"
    assert evaluation_run.state == types.EvaluationRunState.PENDING
    assert isinstance(evaluation_run.data_source, types.EvaluationRunDataSource)
    assert evaluation_run.data_source.evaluation_set == (
        "projects/503583131166/locations/us-central1/evaluationSets/6619939608513740800"
    )
    assert evaluation_run.inference_configs[
        "agent-1"
    ] == types.EvaluationRunInferenceConfig(
        agent_config=types.EvaluationRunAgentConfig(
            developer_instruction=genai_types.Content(
                parts=[genai_types.Part(text="agent-1 instruction")]
            ),
            tools=[tool],
        )
    )
    assert evaluation_run.error is None


def test_create_eval_run_data_source_bigquery_request_set(client):
    """Tests that create_evaluation_run() creates a correctly structured EvaluationRun with BigQueryRequestSet."""
    evaluation_run = client.evals.create_evaluation_run(
        name="test5",
        display_name="test5",
        data_source=types.EvaluationRunDataSource(
            bigquery_request_set=types.BigQueryRequestSet(
                uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
                prompt_column="request",
                candidate_response_columns={
                    "baseline_model_response": "baseline_model_response",
                    "checkpoint_1": "checkpoint_1",
                    "checkpoint_2": "checkpoint_2",
                },
            )
        ),
        dest="gs://lakeyk-test-limited/eval_run_output",
    )
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.display_name == "test5"
    assert evaluation_run.state == types.EvaluationRunState.PENDING
    assert isinstance(evaluation_run.data_source, types.EvaluationRunDataSource)
    assert evaluation_run.data_source.bigquery_request_set == (
        types.BigQueryRequestSet(
            uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
            prompt_column="request",
            candidate_response_columns={
                "baseline_model_response": "baseline_model_response",
                "checkpoint_1": "checkpoint_1",
                "checkpoint_2": "checkpoint_2",
            },
        )
    )
    assert evaluation_run.inference_configs is None
    assert evaluation_run.error is None


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_eval_run_async(client):
    """Tests that create_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run = await client.aio.evals.create_evaluation_run(
        name="test8",
        display_name="test8",
        data_source=types.EvaluationRunDataSource(
            bigquery_request_set=types.BigQueryRequestSet(
                uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
                prompt_column="request",
                candidate_response_columns={
                    "baseline_model_response": "baseline_model_response",
                    "checkpoint_1": "checkpoint_1",
                    "checkpoint_2": "checkpoint_2",
                },
            )
        ),
        dest="gs://lakeyk-test-limited/eval_run_output",
    )
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.display_name == "test8"
    assert evaluation_run.data_source.bigquery_request_set == types.BigQueryRequestSet(
        uri="bq://lakeyk-test-limited.inference_batch_prediction_input.1317387725199900672_1b",
        prompt_column="request",
        candidate_response_columns={
            "baseline_model_response": "baseline_model_response",
            "checkpoint_1": "checkpoint_1",
            "checkpoint_2": "checkpoint_2",
        },
    )
    assert evaluation_run.inference_configs is None
    assert evaluation_run.error is None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.create_evaluation_run",
)
