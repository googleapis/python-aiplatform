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

GCS_DEST = "gs://lakeyk-limited-bucket/eval_run_output"
UNIVERSAL_AR_METRIC = types.EvaluationRunMetric(
    metric="universal_ar_v1",
    metric_config=types.UnifiedMetric(
        predefined_metric_spec=types.PredefinedMetricSpec(
            metric_spec_name="universal_ar_v1",
        )
    ),
)
FINAL_RESPONSE_QUALITY_METRIC = types.EvaluationRunMetric(
    metric="final_response_quality_v1",
    metric_config=types.UnifiedMetric(
        predefined_metric_spec=types.PredefinedMetricSpec(
            metric_spec_name="final_response_quality_v1",
        )
    ),
)
LLM_METRIC = types.EvaluationRunMetric(
    metric="llm_metric",
    metric_config=types.UnifiedMetric(
        llm_based_metric_spec=types.LLMBasedMetricSpec(
            metric_prompt_template=(
                "\nEvaluate the fluency of the response. Provide a score from 1-5."
            )
        )
    ),
)


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
        dataset=types.EvaluationRunDataSource(
            evaluation_set="projects/503583131166/locations/us-central1/evaluationSets/6619939608513740800"
        ),
        dest=GCS_DEST,
        metrics=[
            UNIVERSAL_AR_METRIC,
            types.RubricMetric.FINAL_RESPONSE_QUALITY,
            LLM_METRIC,
        ],
        agent_info=types.evals.AgentInfo(
            agent_resource_name="project/123/locations/us-central1/reasoningEngines/456",
            name="agent-1",
            instruction="agent-1 instruction",
            tool_declarations=[tool],
        ),
        labels={"label1": "value1"},
    )
    assert isinstance(evaluation_run, types.EvaluationRun)
    assert evaluation_run.display_name == "test4"
    assert evaluation_run.state == types.EvaluationRunState.PENDING
    assert isinstance(evaluation_run.data_source, types.EvaluationRunDataSource)
    assert evaluation_run.data_source.evaluation_set == (
        "projects/503583131166/locations/us-central1/evaluationSets/6619939608513740800"
    )
    assert evaluation_run.evaluation_config == types.EvaluationRunConfig(
        output_config=genai_types.OutputConfig(
            gcs_destination=genai_types.GcsDestination(output_uri_prefix=GCS_DEST)
        ),
        metrics=[UNIVERSAL_AR_METRIC, FINAL_RESPONSE_QUALITY_METRIC, LLM_METRIC],
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
    assert evaluation_run.labels == {
        "vertex-ai-evaluation-agent-engine-id": "456",
        "label1": "value1",
    }
    assert evaluation_run.error is None


def test_create_eval_run_data_source_bigquery_request_set(client):
    """Tests that create_evaluation_run() creates a correctly structured EvaluationRun with BigQueryRequestSet."""
    evaluation_run = client.evals.create_evaluation_run(
        name="test5",
        display_name="test5",
        dataset=types.EvaluationRunDataSource(
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
        labels={"label1": "value1"},
        dest=GCS_DEST,
        metrics=[UNIVERSAL_AR_METRIC],
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
    assert evaluation_run.evaluation_config == types.EvaluationRunConfig(
        output_config=genai_types.OutputConfig(
            gcs_destination=genai_types.GcsDestination(output_uri_prefix=GCS_DEST)
        ),
        metrics=[UNIVERSAL_AR_METRIC],
    )
    assert evaluation_run.inference_configs is None
    assert evaluation_run.labels == {
        "label1": "value1",
    }
    assert evaluation_run.error is None


# Test fails in replay mode because of UUID generation mismatch.
# def test_create_eval_run_data_source_evaluation_dataset(client):
#     """Tests that create_evaluation_run() creates a correctly structured EvaluationRun with EvaluationDataset."""
#     input_df = pd.DataFrame(
#         {
#             "prompt": ["prompt1", "prompt2"],
#             "reference": ["reference1", "reference2"],
#             "response": ["response1", "response2"],
#             "intermediate_events": [
#                 [
#                     {
#                         "content": {
#                             "parts": [
#                                 {"text": "first user input"},
#                             ],
#                             "role": "user",
#                         },
#                     },
#                     {
#                         "content": {
#                             "parts": [
#                                 {"text": "first model response"},
#                             ],
#                             "role": "model",
#                         },
#                     },
#                 ],
#                 [
#                     {
#                         "content": {
#                             "parts": [
#                                 {"text": "second user input"},
#                             ],
#                             "role": "user",
#                         },
#                     },
#                     {
#                         "content": {
#                             "parts": [
#                                 {"text": "second model response"},
#                             ],
#                             "role": "model",
#                         },
#                     },
#                 ],
#             ],
#         }
#     )
#     evaluation_run = client.evals.create_evaluation_run(
#         name="test6",
#         display_name="test6",
#         dataset=types.EvaluationDataset(
#             candidate_name="candidate_1",
#             eval_dataset_df=input_df,
#         ),
#         dest=GCS_DEST,
#         metrics=[UNIVERSAL_AR_METRIC],
#     )
#     assert isinstance(evaluation_run, types.EvaluationRun)
#     assert evaluation_run.display_name == "test6"
#     assert evaluation_run.state == types.EvaluationRunState.PENDING
#     assert isinstance(evaluation_run.data_source, types.EvaluationRunDataSource)
#     # Check evaluation set
#     assert evaluation_run.data_source.evaluation_set
#     eval_set = client.evals.get_evaluation_set(
#         name=evaluation_run.data_source.evaluation_set
#     )
#     assert len(eval_set.evaluation_items) == 2
#     # Check evaluation items
#     for i, eval_item_name in enumerate(eval_set.evaluation_items):
#         eval_item = client.evals.get_evaluation_item(name=eval_item_name)
#         assert eval_item.evaluation_item_type == types.EvaluationItemType.REQUEST
#         assert eval_item.evaluation_request.prompt.text == input_df.iloc[i]["prompt"]
#         assert (
#             eval_item.evaluation_request.candidate_responses[0].text
#             == input_df.iloc[i]["response"]
#         )
#         assert (
#             eval_item.evaluation_request.candidate_responses[0].events[0].parts[0].text
#             == input_df.iloc[i]["intermediate_events"][0]["content"]["parts"][0]["text"]
#         )
#         assert (
#             eval_item.evaluation_request.candidate_responses[0].events[0].role
#             == input_df.iloc[i]["intermediate_events"][0]["content"]["role"]
#         )
#         assert (
#             eval_item.evaluation_request.candidate_responses[0].events[1].parts[0].text
#             == input_df.iloc[i]["intermediate_events"][1]["content"]["parts"][0]["text"]
#         )
#         assert (
#             eval_item.evaluation_request.candidate_responses[0].events[1].role
#             == input_df.iloc[i]["intermediate_events"][1]["content"]["role"]
#         )
#     assert evaluation_run.error is None


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_eval_run_async(client):
    """Tests that create_evaluation_run() returns a correctly structured EvaluationRun."""
    evaluation_run = await client.aio.evals.create_evaluation_run(
        name="test8",
        display_name="test8",
        dataset=types.EvaluationRunDataSource(
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
        dest=GCS_DEST,
        metrics=[UNIVERSAL_AR_METRIC],
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
    assert evaluation_run.evaluation_config == types.EvaluationRunConfig(
        output_config=genai_types.OutputConfig(
            gcs_destination=genai_types.GcsDestination(output_uri_prefix=GCS_DEST)
        ),
        metrics=[UNIVERSAL_AR_METRIC],
    )
    assert evaluation_run.error is None
    assert evaluation_run.inference_configs is None
    assert evaluation_run.error is None
    assert evaluation_run.labels is None
    assert evaluation_run.error is None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.create_evaluation_run",
)
