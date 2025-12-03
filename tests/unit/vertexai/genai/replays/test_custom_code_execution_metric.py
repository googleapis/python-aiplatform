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


def test_custom_code_execution(client):
    """Tests that custom code execution metric produces a correctly structured EvaluationResult."""

    code_snippet = """
def evaluate(instance):
    if instance['response'] == instance['reference']:
        return 1.0
    return 0.0
"""

    custom_metric = types.Metric(
        name="my_custom_code_metric",
        remote_custom_function=code_snippet,
    )

    prompts_df = pd.DataFrame(
        {
            "prompt": ["What is 2+2?", "What is 3+3?"],
            "response": ["4", "5"],
            "reference": ["4", "6"],
        }
    )

    eval_dataset = types.EvaluationDataset(
        eval_dataset_df=prompts_df,
        candidate_name="test_model",
    )

    evaluation_result = client.evals.evaluate(
        dataset=eval_dataset,
        metrics=[custom_metric],
    )

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    assert evaluation_result.summary_metrics
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name == "my_custom_code_metric"

    assert evaluation_result.eval_case_results is not None
    assert evaluation_result.eval_case_results
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


def test_custom_code_execution_batch_evaluate(client):
    """Tests that batch_evaluate() works with custom code execution metric."""

    code_snippet = """
def evaluate(instance):
    if instance['response'] == instance['reference']:
        return 1.0
    return 0.0
"""

    custom_metric = types.Metric(
        name="my_custom_code_metric",
        remote_custom_function=code_snippet,
    )

    eval_dataset = types.EvaluationDataset(
        gcs_source=types.GcsSource(
            uris=["gs://genai-eval-sdk-replay-test/test_data/inference_results.jsonl"]
        ),
    )

    evaluation_result = client.evals.batch_evaluate(
        dataset=eval_dataset,
        metrics=[custom_metric],
        dest="gs://genai-eval-sdk-replay-test/test_data/batch_eval_output",
    )

    assert evaluation_result is not None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
