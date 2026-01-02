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


def test_evaluation_result(client):
    """Tests that evaluate() produces a correctly structured EvaluationResult."""
    prompts_df = pd.DataFrame({"prompt": ["What is Taylor Swift's most recent album?"]})

    eval_dataset = client.evals.run_inference(
        model="gemini-2.5-flash",
        src=prompts_df,
    )

    metrics_to_run = [
        types.RubricMetric.TEXT_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(
        dataset=eval_dataset,
        metrics=metrics_to_run,
    )

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None
        assert summary.mean_score is not None

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) > 0
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


def test_evaluation_byor(client):
    """Tests that evaluate() with BYOR (Bring-Your-Own Response) produces a correctly structured EvaluationResult."""
    byor_df = pd.DataFrame(
        {
            "prompt": [
                "Write a simple story about a dinosaur",
                "Generate a poem about Vertex AI",
            ],
            "response": [
                "Once upon a time, there was a T-Rex named Rexy.",
                "In clouds of code, a mind of silicon born...",
            ],
        }
    )

    metrics_to_run = [
        types.RubricMetric.GENERAL_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(
        dataset=byor_df,
        metrics=metrics_to_run,
    )

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None
        assert summary.mean_score is not None
        assert summary.pass_rate is not None

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) > 0
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
