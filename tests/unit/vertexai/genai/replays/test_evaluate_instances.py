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
from vertexai._genai import types
import pandas as pd


def test_bleu_metric(client):
    test_bleu_input = types.BleuInput(
        instances=[
            types.BleuInstance(
                reference="The quick brown fox jumps over the lazy dog.",
                prediction="A fast brown fox leaps over a lazy dog.",
            )
        ],
        metric_spec=types.BleuSpec(),
    )
    response = client.evals._evaluate_instances(bleu_input=test_bleu_input)
    assert len(response.bleu_results.bleu_metric_values) == 1


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


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
