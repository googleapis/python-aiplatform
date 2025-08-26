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
    prompts_df = pd.DataFrame(
        {
            "prompt": ["Explain the concept of machine learning in simple terms."],
            "response": [
                "Machine learning is a type of artificial intelligence that allows"
                " computers to learn from data without being explicitly programmed."
            ],
        }
    )

    eval_dataset = types.EvaluationDataset(
        eval_dataset_df=prompts_df,
        candidate_name="gemini-2.5-flash",
    )

    predefined_metrics = [
        types.PrebuiltMetric.GENERAL_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(
        dataset=eval_dataset,
        metrics=predefined_metrics,
    )

    assert isinstance(evaluation_result, types.EvaluationResult)

    assert evaluation_result.summary_metrics is not None
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name is not None
        assert summary.mean_score is not None

    assert evaluation_result.eval_case_results is not None
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


pytestmark = pytest_helper.setup(
    file=__file__,
    globals_for_file=globals(),
    test_method="evals.evaluate",
)
