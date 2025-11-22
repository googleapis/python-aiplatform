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
        types.RubricMetric.GENERAL_QUALITY,
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


def test_multi_turn_predefined_metric(client):
    """Tests that evaluate works with multi-turn predefined metrics."""
    prompts_data = {
        "request": [
            {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": (
                                    "I'm a new analyst covering the semiconductor"
                                    " industry. To start, can you give me a"
                                    " high-level overview of NVIDIA's (NVDA)"
                                    " financial performance over the last two fiscal"
                                    " years?"
                                )
                            }
                        ],
                        "role": "user",
                    },
                    {
                        "parts": [
                            {
                                "text": (
                                    "Certainly. Over the last two fiscal years,"
                                    " NVIDIA has shown significant revenue growth,"
                                    " primarily driven by its Data Center and Gaming"
                                    " segments. Key metrics include a substantial"
                                    " increase in gross margin and net income. For"
                                    " FY2024, they reported revenues of $60.9"
                                    " billion, a 126% increase from the previous"
                                    " year. Would you like to dive into the specifics"
                                    " of a particular segment, like Data Center"
                                    " revenue, or look at their latest quarterly"
                                    " report?"
                                )
                            }
                        ],
                        "role": "model",
                    },
                    {
                        "parts": [
                            {
                                "text": (
                                    "Let's focus on the latest quarter. Summarize the"
                                    " key takeaways from their most recent earnings"
                                    " call and compare the reported EPS against"
                                    " analyst consensus."
                                )
                            }
                        ],
                        "role": "user",
                    },
                ]
            },
            {
                "contents": [
                    {
                        "parts": [
                            {
                                "text": (
                                    "Please analyze this chart of the S&P 500's"
                                    " daily price movement and its 50-day and"
                                    " 200-day moving averages. Identify any"
                                    " significant technical events."
                                )
                            }
                        ],
                        "role": "user",
                    },
                    {
                        "parts": [
                            {
                                "text": (
                                    "Based on the chart, the S&P 500's 50-day moving"
                                    " average has recently crossed above the 200-day"
                                    " moving average. This event is a classic"
                                    " technical indicator known as a 'Golden Cross',"
                                    " which is often interpreted by analysts as a"
                                    " bullish signal for the medium-to-long term. The"
                                    " index also appears to be testing a key"
                                    " resistance level near 5500."
                                )
                            }
                        ],
                        "role": "model",
                    },
                    {
                        "parts": [
                            {
                                "text": (
                                    "Interesting. What is the historical reliability"
                                    " of the 'Golden Cross' as a bull market"
                                    " predictor? And can you find me a video"
                                    " explaining this concept in more detail?"
                                )
                            }
                        ],
                        "role": "user",
                    },
                ]
            },
        ],
        "response": [
            "Okay, let's break down NVIDIA's most recent earnings report",
            " Would you like me to do that?",
        ],
    }

    prompts_df = pd.DataFrame(prompts_data)

    eval_dataset = types.EvaluationDataset(
        eval_dataset_df=prompts_df,
        candidate_name="gemini-2.5-flash",
    )

    predefined_metrics = [
        types.RubricMetric.MULTI_TURN_GENERAL_QUALITY,
    ]

    evaluation_result = client.evals.evaluate(
        dataset=eval_dataset,
        metrics=predefined_metrics,
    )

    assert isinstance(evaluation_result, types.EvaluationResult)
    assert evaluation_result.summary_metrics is not None
    assert len(evaluation_result.summary_metrics) > 0
    for summary in evaluation_result.summary_metrics:
        assert isinstance(summary, types.AggregatedMetricResult)
        assert summary.metric_name == "multi_turn_general_quality_v1"
        assert isinstance(summary.mean_score, float)

    assert evaluation_result.eval_case_results is not None
    assert len(evaluation_result.eval_case_results) > 0
    for case_result in evaluation_result.eval_case_results:
        assert isinstance(case_result, types.EvalCaseResult)
        assert case_result.eval_case_index is not None
        assert case_result.response_candidate_results is not None


def test_evaluation_grounding_metric(client):
    """Tests that grounding metric produces a correctly structured EvaluationResult."""
    prompts_df = pd.DataFrame(
        {
            "prompt": ["Explain the concept of machine learning in simple terms."],
            "response": [
                "Machine learning is a type of artificial intelligence that allows"
                " computers to learn from data without being explicitly programmed."
            ],
            "context": [
                "Article: 'Intro to AI', Section 2.1\n"
                "Machine learning (ML) is a subfield of artificial intelligence (AI). "
                "The core idea of machine learning is that it allows computer systems to "
                "learn from and adapt to new data without being explicitly programmed. "
                "Instead of a developer writing code for every possible scenario, the "
                "system builds a model based on patterns in training data."
            ],
        }
    )

    eval_dataset = types.EvaluationDataset(
        eval_dataset_df=prompts_df,
        candidate_name="gemini-2.5-flash",
    )

    evaluation_result = client.evals.evaluate(
        dataset=eval_dataset,
        metrics=[
            types.RubricMetric.GROUNDING,
        ],
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


def test_evaluation_gecko_text2image_metric(client):
    """Tests that Gecko text2image metric produces a correctly structured EvaluationResult."""
    prompts_df = pd.DataFrame(
        {
            "prompt": ["sunset over a calm ocean"],
            "response": [
                {
                    "parts": [
                        {
                            "file_data": {
                                "mime_type": "image/png",
                                "file_uri": (
                                    "gs://cloud-samples-data/generative-ai/evaluation/"
                                    "images/sunset.png"
                                ),
                            }
                        }
                    ],
                    "role": "model",
                },
            ],
        }
    )

    data_with_rubrics = client.evals.generate_rubrics(
        src=prompts_df,
        rubric_group_name="gecko_image_rubrics",
        predefined_spec_name=types.RubricMetric.GECKO_TEXT2IMAGE,
    )

    assert isinstance(data_with_rubrics, types.EvaluationDataset)
    assert data_with_rubrics.eval_dataset_df is not None
    assert len(data_with_rubrics.eval_dataset_df) == 1
    for _, case in data_with_rubrics.eval_dataset_df.iterrows():
        assert case.rubric_groups is not None
        assert "gecko_image_rubrics" in case.rubric_groups

    evaluation_result = client.evals.evaluate(
        dataset=data_with_rubrics,
        metrics=[
            types.RubricMetric.GECKO_TEXT2IMAGE,
        ],
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


def test_evaluation_gecko_text2video_metric(client):
    """Tests that Gecko text2video metric produces a correctly structured EvaluationResult."""
    prompts_df = pd.DataFrame(
        {
            "prompt": [
                "A boat sailing leisurely along the Seine River with the Eiffel Tower "
                "in background"
            ],
            "response": [
                {
                    "parts": [
                        {
                            "file_data": {
                                "mime_type": "video/mp4",
                                "file_uri": (
                                    "gs://cloud-samples-data/generative-ai/evaluation/"
                                    "videos/boat.mp4"
                                ),
                            }
                        }
                    ],
                    "role": "model",
                },
            ],
        }
    )

    data_with_rubrics = client.evals.generate_rubrics(
        src=prompts_df,
        rubric_group_name="gecko_video_rubrics",
        predefined_spec_name=types.RubricMetric.GECKO_TEXT2VIDEO,
    )

    assert isinstance(data_with_rubrics, types.EvaluationDataset)
    assert data_with_rubrics.eval_dataset_df is not None
    assert len(data_with_rubrics.eval_dataset_df) == 1
    for _, case in data_with_rubrics.eval_dataset_df.iterrows():
        assert case.rubric_groups is not None
        assert "gecko_video_rubrics" in case.rubric_groups

    evaluation_result = client.evals.evaluate(
        dataset=data_with_rubrics,
        metrics=[
            types.RubricMetric.GECKO_TEXT2VIDEO,
        ],
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
