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

import json

from tests.unit.vertexai.genai.replays import pytest_helper
from vertexai._genai import types
from google.genai import types as genai_types
import pandas as pd
import pytest


def test_bleu_metric(client):
    test_bleu_input = types.BleuInput(
        instances=[
            types.BleuInstance(
                reference="The quick brown fox jumps over the lazy dog.",
                prediction="A fast brown fox leaps over a lazy dog.",
            )
        ],
        metric_spec=genai_types.BleuSpec(),
    )
    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            bleu_input=test_bleu_input
        )
    )
    assert len(response.bleu_results.bleu_metric_values) == 1


def test_exact_match_metric(client):
    """Tests the _evaluate_instances method with ExactMatchInput."""
    test_exact_match_input = types.ExactMatchInput(
        instances=[
            types.ExactMatchInstance(
                prediction="The quick brown fox jumps over the lazy dog.",
                reference="The quick brown fox jumps over the lazy dog.",
            )
        ],
        metric_spec=types.ExactMatchSpec(),
    )
    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            exact_match_input=test_exact_match_input
        )
    )
    assert len(response.exact_match_results.exact_match_metric_values) == 1


def test_rouge_metric(client):
    """Tests the _evaluate_instances method with RougeInput."""
    test_rouge_input = types.RougeInput(
        instances=[
            types.RougeInstance(
                prediction="A fast brown fox leaps over a lazy dog.",
                reference="The quick brown fox jumps over the lazy dog.",
            )
        ],
        metric_spec=genai_types.RougeSpec(rouge_type="rougeL"),
    )
    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            rouge_input=test_rouge_input
        )
    )
    assert len(response.rouge_results.rouge_metric_values) == 1


def test_pointwise_metric(client):
    """Tests the _evaluate_instances method with PointwiseMetricInput."""
    instance_dict = {"prompt": "What is the capital of France?", "response": "Paris"}
    json_instance = json.dumps(instance_dict)

    test_input = types.PointwiseMetricInput(
        instance=types.PointwiseMetricInstance(json_instance=json_instance),
        metric_spec=genai_types.PointwiseMetricSpec(
            metric_prompt_template="Evaluate if the response '{response}' correctly answers the prompt '{prompt}'."
        ),
    )
    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            pointwise_metric_input=test_input
        )
    )
    assert response.pointwise_metric_result is not None
    assert response.pointwise_metric_result.score is not None


def test_pointwise_metric_with_agent_data(client):
    """Tests the _evaluate_instances method with PointwiseMetricInput and agent_data."""
    instance_dict = {"prompt": "What is the capital of France?", "response": "Paris"}
    json_instance = json.dumps(instance_dict)
    agent_data = types.evals.AgentData(
        agent_config=types.evals.AgentConfig(
            tools=types.evals.Tools(
                tool=[
                    genai_types.Tool(
                        function_declarations=[
                            genai_types.FunctionDeclaration(name="search")
                        ]
                    )
                ]
            ),
            developer_instruction=types.evals.InstanceData(text="instruction"),
        ),
        events=types.evals.Events(
            event=[genai_types.Content(parts=[genai_types.Part(text="hello")])]
        ),
    )
    instance = types.EvaluationInstance(
        prompt=types.evals.InstanceData(text="What is the capital of France?"),
        response=types.evals.InstanceData(text="Paris"),
        agent_data=agent_data,
    )

    test_input = types.PointwiseMetricInput(
        instance=types.PointwiseMetricInstance(json_instance=json_instance),
        metric_spec=genai_types.PointwiseMetricSpec(
            metric_prompt_template="Evaluate if the response '{response}' correctly answers the prompt '{prompt}'."
        ),
    )
    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            pointwise_metric_input=test_input,
            instance=instance,
        )
    )
    assert response.pointwise_metric_result is not None
    assert response.pointwise_metric_result.score is not None


def test_predefined_metric_with_agent_data(client):
    """Tests the _evaluate_instances method with predefined metric and agent_data."""
    agent_data = types.evals.AgentData(
        agent_config=types.evals.AgentConfig(
            tools=types.evals.Tools(
                tool=[
                    genai_types.Tool(
                        function_declarations=[
                            genai_types.FunctionDeclaration(name="search")
                        ]
                    )
                ]
            ),
            developer_instruction=types.evals.InstanceData(text="instruction"),
        ),
        events=types.evals.Events(
            event=[genai_types.Content(parts=[genai_types.Part(text="hello")])]
        ),
    )
    instance = types.EvaluationInstance(
        prompt=types.evals.InstanceData(text="What is the capital of France?"),
        response=types.evals.InstanceData(text="Paris"),
        reference=types.evals.InstanceData(text="Paris"),
        agent_data=agent_data,
    )

    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            metrics=[types.Metric(name="general_quality_v1")],
            instance=instance,
        )
    )
    assert response.metric_results[0].score is not None


def test_pairwise_metric_with_autorater(client):
    """Tests the _evaluate_instances method with PairwiseMetricInput and AutoraterConfig."""

    instance_dict = {
        "baseline_response": "Short summary.",
        "candidate_response": "A longer, more detailed summary.",
    }
    json_instance = json.dumps(instance_dict)

    test_input = types.PairwiseMetricInput(
        instance=types.PairwiseMetricInstance(json_instance=json_instance),
        metric_spec=genai_types.PairwiseMetricSpec(
            metric_prompt_template="Which response is a better summary? Baseline: '{baseline_response}' or Candidate: '{candidate_response}'"
        ),
    )
    autorater_config = genai_types.AutoraterConfig(sampling_count=2)

    response = client.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            pairwise_metric_input=test_input, autorater_config=autorater_config
        )
    )
    assert response.pairwise_metric_result is not None
    assert response.pairwise_metric_result.pairwise_choice is not None


def test_run_inference_with_string_model(client):
    test_df = pd.DataFrame({"prompt": ["test prompt"]})

    inference_result = client.evals.run_inference(
        model="gemini-pro",
        src=test_df,
    )
    assert inference_result.candidate_name == "gemini-pro"
    assert inference_result.gcs_source is None


def test_run_inference_with_callable_model_sets_candidate_name(client):
    test_df = pd.DataFrame({"prompt": ["test prompt"]})

    def my_model_fn(contents):
        return "callable response"

    inference_result = client.evals.run_inference(
        model=my_model_fn,
        src=test_df,
    )
    assert inference_result.candidate_name == "my_model_fn"
    assert inference_result.gcs_source is None


def test_inference_with_prompt_template(client):
    test_df = pd.DataFrame({"text_input": ["world"]})
    config = types.EvalRunInferenceConfig(prompt_template="Hello {text_input}")
    inference_result = client.evals.run_inference(
        model="gemini-2.0-flash-exp", src=test_df, config=config
    )
    assert inference_result.candidate_name == "gemini-2.0-flash-exp"
    assert inference_result.gcs_source is None


def test_run_inference_with_agent(client):
    test_df = pd.DataFrame(
        {"prompt": ["agent prompt"], "session_inputs": ['{"user_id": "user_123"}']}
    )
    inference_result = client.evals.run_inference(
        agent="projects/977012026409/locations/us-central1/reasoningEngines/7188347537655332864",
        src=test_df,
    )
    assert inference_result.candidate_name is None
    assert inference_result.gcs_source is None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_bleu_metric_async(client):
    test_bleu_input = types.BleuInput(
        instances=[
            types.BleuInstance(
                reference="The quick brown fox jumps over the lazy dog.",
                prediction="A fast brown fox leaps over a lazy dog.",
            )
        ],
        metric_spec=genai_types.BleuSpec(),
    )
    response = await client.aio.evals.evaluate_instances(
        metric_config=types._EvaluateInstancesRequestParameters(
            bleu_input=test_bleu_input
        )
    )
    assert len(response.bleu_results.bleu_metric_values) == 1
