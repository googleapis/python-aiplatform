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

from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import vertexai
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.services import (
    evaluation_service as gapic_evaluation_services,
)
from google.cloud.aiplatform_v1beta1.types import (
    evaluation_service as gapic_evaluation_service_types,
)
from vertexai import generative_models
from vertexai.preview.evaluation import eval_task
from vertexai.preview.evaluation.metrics import (
    predefined_rubric_metrics,
)
import pandas as pd
import pytest


PredefinedRubricMetrics = predefined_rubric_metrics.PredefinedRubricMetrics
EvalTask = eval_task.EvalTask
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_EVAL_DATASET = pd.DataFrame(
    {
        "prompt": ["test_prompt", "text_prompt", "test_prompt_3"],
        "response": ["test", "text", "test_response_3"],
    }
)
_TEST_PAIRWISE_EVAL_DATASET = pd.DataFrame(
    {
        "prompt": ["test_prompt", "text_prompt", "test_prompt_3"],
        "response": ["test", "text", "test_response_3"],
        "baseline_model_response": ["test", "text", "test_response_3"],
    }
)
_TEST_MULTIMODAL_EVAL_DATASET = pd.DataFrame(
    {
        "prompt": ["test_prompt", "text_prompt"],
        "image": [
            (
                '{"contents": [{"parts": [{"file_data": {"mime_type": "image/png",'
                ' "file_uri": "gs://test-bucket/image3.png"}}]}]}'
            ),
            (
                '{"contents": [{"parts": [{"file_data": {"mime_type": "image/png",'
                ' "file_uri": "gs://test-bucket/image4.png"}}]}]}'
            ),
        ],
        "response": ["test", "text"],
    }
)
_TEST_PAIRWISE_MULTIMODAL_EVAL_DATASET = pd.DataFrame(
    {
        "prompt": ["test_prompt", "text_prompt"],
        "image": [
            (
                '{"contents": [{"parts": [{"file_data": {"mime_type": "image/png",'
                ' "file_uri": "gs://test-bucket/image3.png"}}]}]}'
            ),
            (
                '{"contents": [{"parts": [{"file_data": {"mime_type": "image/png",'
                ' "file_uri": "gs://test-bucket/image4.png"}}]}]}'
            ),
        ],
        "description": ["description", "description"],
        "response": ["test", "text"],
        "baseline_model_response": ["test", "text"],
    }
)
_MOCK_RUBRIC_GENERATION_RESPONSE = generative_models.GenerationResponse.from_dict(
    {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": """```json{"questions": ["test_rubric"]}```"""}]
                },
            }
        ]
    }
)
_MOCK_POINTWISE_RESULT = gapic_evaluation_service_types.PointwiseMetricResult(
    custom_output=gapic_evaluation_service_types.CustomOutput(
        raw_outputs=gapic_evaluation_service_types.RawOutput(
            raw_output=[
                """The appropriate rubrics for this prompt are:
                                  <question>
                                  STEP 1: ...
                                  Question: question 1
                                  Verdict: yes
                                  </question>
                                  <question>
                                  STEP 1: ...
                                  Question: question 2
                                  Verdict: no
                                  </question>""",
                """The appropriate rubrics for this prompt are:
                                  <question>
                                  STEP 1: ...
                                  Question: question 1
                                  Verdict: yes
                                  </question>
                                  <question>
                                  STEP 1: ...
                                  Question: question 2
                                  Verdict: no
                                  </question>""",
            ],
        ),
    )
)
_MOCK_PAIRWISE_RESULT = gapic_evaluation_service_types.PairwiseMetricResult(
    custom_output=gapic_evaluation_service_types.CustomOutput(
        raw_outputs=gapic_evaluation_service_types.RawOutput(
            raw_output=[
                """"[[Response A Answers:]]\n"
                    "Response A\n"
                    "[[Rubric Score:]]\n"
                    "Rubric Score\n"
                    "[[Response B Answers:]]\n"
                    "Response A\n"
                    "[[Rubric Score:]]\n"
                    "Rubric Score\n"
                    "[[SxS Rating: B > A]]""",
                """"[[Response A Answers:]]\n"
                    "Response A\n"
                    "[[Rubric Score:]]\n"
                    "Rubric Score\n"
                    "[[Response B Answers:]]\n"
                    "Response A\n"
                    "[[Rubric Score:]]\n"
                    "Rubric Score\n"
                    "[[SxS Rating: B > A]]""",
            ],
        ),
    )
)
_MOCK_PAIRWISE_RESPONSE = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        pairwise_metric_result=_MOCK_PAIRWISE_RESULT
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        pairwise_metric_result=_MOCK_PAIRWISE_RESULT
    ),
)
_MOCK_POINTWISE_RESPONSE = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        pointwise_metric_result=_MOCK_POINTWISE_RESULT
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        pointwise_metric_result=_MOCK_POINTWISE_RESULT
    ),
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestPredefinedRubricMetrics:
    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_pointwise_instruction_following_metric(self):
        metric = PredefinedRubricMetrics.Pointwise.INSTRUCTION_FOLLOWING
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_RUBRIC_GENERATION_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_POINTWISE_RESPONSE,
        ):
            eval_result = EvalTask(
                dataset=_TEST_EVAL_DATASET, metrics=[metric]
            ).evaluate()
            assert eval_result.metrics_table.columns.tolist() == [
                "prompt",
                "response",
                "rubrics",
                "rb_instruction_following/score",
                "rb_instruction_following/rubric_verdict_pairs",
                "rb_instruction_following/raw_outputs",
            ]

    def test_pairwise_instruction_following_metric(self):
        metric = PredefinedRubricMetrics.Pairwise.INSTRUCTION_FOLLOWING
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_RUBRIC_GENERATION_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_PAIRWISE_RESPONSE,
        ):
            eval_result = EvalTask(
                dataset=_TEST_PAIRWISE_EVAL_DATASET, metrics=[metric]
            ).evaluate()
            assert eval_result.metrics_table.columns.tolist() == [
                "prompt",
                "response",
                "baseline_model_response",
                "rubrics",
                "pairwise_rb_instruction_following/pairwise_choice",
                "pairwise_rb_instruction_following/score",
                "pairwise_rb_instruction_following/baseline_rubric_verdict_pairs",
                "pairwise_rb_instruction_following/candidate_rubric_verdict_pairs",
                "pairwise_rb_instruction_following/raw_outputs",
            ]

    def test_pointwise_text_quality_metric(self):
        metric = PredefinedRubricMetrics.Pointwise.TEXT_QUALITY
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_RUBRIC_GENERATION_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_POINTWISE_RESPONSE,
        ):
            eval_result = EvalTask(
                dataset=_TEST_EVAL_DATASET, metrics=[metric]
            ).evaluate()
            assert eval_result.metrics_table.columns.tolist() == [
                "prompt",
                "response",
                "rubrics",
                "rb_text_quality/score",
                "rb_text_quality/rubric_verdict_pairs",
                "rb_text_quality/raw_outputs",
            ]

    def test_pairwise_text_quality_metric(self):
        metric = PredefinedRubricMetrics.Pairwise.TEXT_QUALITY
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_RUBRIC_GENERATION_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_PAIRWISE_RESPONSE,
        ):
            eval_result = EvalTask(
                dataset=_TEST_PAIRWISE_EVAL_DATASET, metrics=[metric]
            ).evaluate()
            assert eval_result.metrics_table.columns.tolist() == [
                "prompt",
                "response",
                "baseline_model_response",
                "rubrics",
                "pairwise_rb_text_quality/pairwise_choice",
                "pairwise_rb_text_quality/score",
                "pairwise_rb_text_quality/baseline_rubric_verdict_pairs",
                "pairwise_rb_text_quality/candidate_rubric_verdict_pairs",
                "pairwise_rb_text_quality/raw_outputs",
            ]

    def test_pointwise_multimodal_understanding_metric(self):
        metric = PredefinedRubricMetrics.Pointwise.MULTIMODAL_UNDERSTANDING
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_RUBRIC_GENERATION_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_POINTWISE_RESPONSE,
        ):
            eval_result = EvalTask(
                dataset=_TEST_MULTIMODAL_EVAL_DATASET, metrics=[metric]
            ).evaluate()
            assert eval_result.metrics_table.columns.tolist() == [
                "prompt",
                "image",
                "response",
                "rubrics",
                "rb_multimodal_understanding/score",
                "rb_multimodal_understanding/rubric_verdict_pairs",
                "rb_multimodal_understanding/raw_outputs",
            ]

    def test_pairwise_multimodal_understanding_metric(self):
        metric = PredefinedRubricMetrics.Pairwise.MULTIMODAL_UNDERSTANDING
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_RUBRIC_GENERATION_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_PAIRWISE_RESPONSE,
        ):
            eval_result = EvalTask(
                dataset=_TEST_PAIRWISE_MULTIMODAL_EVAL_DATASET, metrics=[metric]
            ).evaluate()
            assert eval_result.metrics_table.columns.tolist() == [
                "prompt",
                "image",
                "description",
                "response",
                "baseline_model_response",
                "rubrics",
                "pairwise_rb_multimodal_understanding/pairwise_choice",
                "pairwise_rb_multimodal_understanding/score",
                "pairwise_rb_multimodal_understanding/baseline_rubric_verdict_pairs",
                "pairwise_rb_multimodal_understanding/candidate_rubric_verdict_pairs",
                "pairwise_rb_multimodal_understanding/raw_outputs",
            ]
