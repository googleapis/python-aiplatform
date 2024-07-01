# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

import threading
import time
from unittest import mock

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform_v1beta1.services import (
    evaluation_service as gapic_evaluation_services,
)
from google.cloud.aiplatform_v1beta1.types import (
    evaluation_service as gapic_evaluation_service_types,
)
from vertexai import generative_models
from vertexai.preview import evaluation
from vertexai.preview.evaluation import _base as eval_base
from vertexai.preview.evaluation import _evaluation
from vertexai.preview.evaluation import utils
from vertexai.preview.evaluation.metrics import (
    _pairwise_question_answering_quality,
)
from vertexai.preview.evaluation.metrics import (
    _pairwise_summarization_quality,
)
from vertexai.preview.evaluation.metrics import _rouge
from vertexai.preview.evaluation.metrics import (
    _summarization_quality,
)
import numpy as np
import pandas as pd
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METRICS = (
    "exact_match",
    "bleu",
    "rouge_1",
    "rouge_2",
    "rouge_l",
    "rouge_l_sum",
    "coherence",
    "fluency",
    "safety",
    "groundedness",
    "fulfillment",
    "summarization_quality",
    "summarization_helpfulness",
    "summarization_verbosity",
    "question_answering_quality",
    "question_answering_relevance",
    "question_answering_helpfulness",
    "question_answering_correctness",
)
_TEST_EVAL_DATASET = pd.DataFrame(
    {
        "response": ["test", "text"],
        "reference": ["test", "ref"],
        "context": ["test", "context"],
        "instruction": ["test", "instruction"],
    }
)
_TEST_EVAL_DATASET_WITHOUT_RESPONSE = pd.DataFrame(
    {
        "reference": ["test", "ref"],
        "context": ["test", "context"],
        "instruction": ["test", "instruction"],
    }
)

_TEST_JSONL_FILE_CONTENT = """{"prompt": "prompt", "reference": "reference"}\n
{"prompt":"test", "reference": "test"}\n
"""
_TEST_CSV_FILE_CONTENT = """reference,context,instruction\ntest,test,test\n
text,text,text\n
"""

_TEST_EXPERIMENT = "test-experiment"

_MOCK_EXACT_MATCH_RESULT = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        exact_match_results=gapic_evaluation_service_types.ExactMatchResults(
            exact_match_metric_values=[
                gapic_evaluation_service_types.ExactMatchMetricValue(score=1.0),
            ]
        )
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        exact_match_results=gapic_evaluation_service_types.ExactMatchResults(
            exact_match_metric_values=[
                gapic_evaluation_service_types.ExactMatchMetricValue(score=0.0),
            ]
        )
    ),
)
_EXPECTED_ROUGE_REQUESTS = (
    gapic_evaluation_service_types.EvaluateInstancesRequest(
        location=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
        rouge_input=gapic_evaluation_service_types.RougeInput(
            metric_spec=gapic_evaluation_service_types.RougeSpec(
                rouge_type="rougeLsum", use_stemmer=True, split_summaries=True
            ),
            instances=[
                gapic_evaluation_service_types.RougeInstance(
                    prediction="test_response", reference="test"
                ),
            ],
        ),
    ),
    gapic_evaluation_service_types.EvaluateInstancesRequest(
        location=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
        rouge_input=gapic_evaluation_service_types.RougeInput(
            metric_spec=gapic_evaluation_service_types.RougeSpec(
                rouge_type="rougeLsum", use_stemmer=True, split_summaries=True
            ),
            instances=[
                gapic_evaluation_service_types.RougeInstance(
                    prediction="test_response", reference="reference"
                ),
            ],
        ),
    ),
)
_MOCK_ROUGE_RESULT = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        rouge_results=gapic_evaluation_service_types.RougeResults(
            rouge_metric_values=[
                gapic_evaluation_service_types.RougeMetricValue(score=1.0)
            ]
        )
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        rouge_results=gapic_evaluation_service_types.RougeResults(
            rouge_metric_values=[
                gapic_evaluation_service_types.RougeMetricValue(score=0.5)
            ]
        )
    ),
)
_MOCK_FLUENCY_RESULT = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        fluency_result=gapic_evaluation_service_types.FluencyResult(
            score=5, explanation="explanation", confidence=1.0
        )
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        fluency_result=gapic_evaluation_service_types.FluencyResult(
            score=4, explanation="explanation", confidence=0.5
        )
    ),
)
_MOCK_SUMMARIZATION_QUALITY_RESULT = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        summarization_quality_result=gapic_evaluation_service_types.SummarizationQualityResult(
            score=5, explanation="explanation", confidence=1.0
        )
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        summarization_quality_result=gapic_evaluation_service_types.SummarizationQualityResult(
            score=4, explanation="explanation", confidence=0.5
        )
    ),
)


_MOCK_PAIRWISE_SUMMARIZATION_QUALITY_RESULT = (
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        pairwise_summarization_quality_result=gapic_evaluation_service_types.PairwiseSummarizationQualityResult(
            pairwise_choice=gapic_evaluation_service_types.PairwiseChoice.BASELINE,
            explanation="explanation",
            confidence=1.0,
        )
    ),
    gapic_evaluation_service_types.EvaluateInstancesResponse(
        pairwise_summarization_quality_result=gapic_evaluation_service_types.PairwiseSummarizationQualityResult(
            pairwise_choice=gapic_evaluation_service_types.PairwiseChoice.CANDIDATE,
            explanation="explanation",
            confidence=0.5,
        )
    ),
)

_MOCK_MODEL_INFERENCE_RESPONSE = generative_models.GenerationResponse.from_dict(
    {
        "candidates": [
            {
                "content": {"parts": [{"text": "test_response"}]},
            }
        ]
    }
)
MOCK_EVAL_RESULT = eval_base.EvalResult(
    summary_metrics={
        "row_count": 1,
        "mock_metric/mean": 1.0,
        "mock_metric/std": np.nan,
    },
    metrics_table=pd.DataFrame(
        {
            "response": ["test"],
            "mock_metric": [1.0],
        }
    ),
)


@pytest.fixture
def mock_experiment_tracker():
    with mock.patch.object(
        metadata, "_experiment_tracker", autospec=True
    ) as mock_experiment_tracker:
        yield mock_experiment_tracker


@pytest.mark.usefixtures("google_auth_mock")
class TestEvaluation:
    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_create_eval_task(self):
        test_content_column_name = "test_content_column_name"
        test_reference_column_name = "test_reference_column_name"
        test_response_column_name = "test_response_column_name"

        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET,
            metrics=_TEST_METRICS,
            experiment=_TEST_EXPERIMENT,
            content_column_name=test_content_column_name,
            reference_column_name=test_reference_column_name,
            response_column_name=test_response_column_name,
        )

        assert test_eval_task.dataset.equals(_TEST_EVAL_DATASET)
        assert test_eval_task.metrics == _TEST_METRICS
        assert test_eval_task.experiment == _TEST_EXPERIMENT
        assert test_eval_task.content_column_name == test_content_column_name
        assert test_eval_task.reference_column_name == test_reference_column_name
        assert test_eval_task.response_column_name == test_response_column_name

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_compute_automatic_metrics(self, api_transport):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )
        eval_dataset = pd.DataFrame(
            {
                "response": ["test", "text"],
                "reference": ["test", "ref"],
            }
        )
        test_metrics = ["exact_match"]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        mock_metric_results = _MOCK_EXACT_MATCH_RESULT
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=mock_metric_results,
        ):
            test_result = test_eval_task.evaluate()

        assert test_result.summary_metrics["row_count"] == 2
        assert test_result.summary_metrics["exact_match/mean"] == 0.5
        assert test_result.summary_metrics["exact_match/std"] == pytest.approx(0.7, 0.1)
        assert list(test_result.metrics_table.columns.values) == [
            "response",
            "reference",
            "exact_match",
        ]
        assert test_result.metrics_table[["response", "reference"]].equals(eval_dataset)
        assert list(test_result.metrics_table["exact_match"].values) == [1.0, 0.0]

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_compute_pointwise_metrics(self, api_transport):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )
        eval_dataset = pd.DataFrame(
            {
                "response": ["test", "text"],
            }
        )
        test_metrics = ["fluency"]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        mock_metric_results = _MOCK_FLUENCY_RESULT
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=mock_metric_results,
        ):
            test_result = test_eval_task.evaluate()

        assert test_result.summary_metrics["row_count"] == 2
        assert test_result.summary_metrics["fluency/mean"] == 4.5
        assert test_result.summary_metrics["fluency/std"] == pytest.approx(0.7, 0.1)
        assert set(test_result.metrics_table.columns.values) == set(
            [
                "response",
                "fluency",
                "fluency/explanation",
                "fluency/confidence",
            ]
        )
        assert test_result.metrics_table[["response"]].equals(eval_dataset)
        assert list(test_result.metrics_table["fluency"].values) == [5, 4]
        assert list(test_result.metrics_table["fluency/explanation"].values) == [
            "explanation",
            "explanation",
        ]
        assert list(test_result.metrics_table["fluency/confidence"].values) == [
            1.0,
            0.5,
        ]

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_compute_pointwise_metrics_with_custom_metric_spec(self, api_transport):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )
        eval_dataset = pd.DataFrame(
            {
                "context": ["test", "context"],
                "instruction": ["test", "instruction"],
                "reference": ["test", "reference"],
            }
        )
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_MODEL_INFERENCE_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        test_metrics = [
            _summarization_quality.SummarizationQuality(
                use_reference=True,
            )
        ]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        mock_metric_results = _MOCK_SUMMARIZATION_QUALITY_RESULT
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=mock_metric_results,
        ):
            test_result = test_eval_task.evaluate(
                model=mock_model,
                prompt_template="{instruction} test prompt template {context}",
            )

        assert test_result.summary_metrics["row_count"] == 2
        assert test_result.summary_metrics["summarization_quality/mean"] == 4.5
        assert test_result.summary_metrics[
            "summarization_quality/std"
        ] == pytest.approx(0.7, 0.1)
        assert set(test_result.metrics_table.columns.values) == set(
            [
                "context",
                "instruction",
                "reference",
                "completed_prompt",
                "response",
                "summarization_quality",
                "summarization_quality/explanation",
                "summarization_quality/confidence",
            ]
        )
        assert list(test_result.metrics_table["summarization_quality"].values) == [5, 4]
        assert list(
            test_result.metrics_table["summarization_quality/explanation"].values
        ) == [
            "explanation",
            "explanation",
        ]
        assert list(
            test_result.metrics_table["summarization_quality/confidence"].values
        ) == [
            1.0,
            0.5,
        ]

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_compute_automatic_metrics_with_custom_metric_spec(self, api_transport):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )
        eval_dataset = pd.DataFrame(
            {
                "content": ["test", "content"],
                "reference": ["test", "reference"],
            }
        )
        mock_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_model.generate_content.return_value = _MOCK_MODEL_INFERENCE_RESPONSE
        mock_model._model_name = "publishers/google/model/gemini-1.0-pro"
        test_metrics = [
            _rouge.Rouge(
                rouge_type="rougeLsum",
                use_stemmer=True,
                split_summaries=True,
            )
        ]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=_MOCK_ROUGE_RESULT,
        ) as mock_evaluate_instances:
            test_result = test_eval_task.evaluate(
                model=mock_model,
            )

        assert test_result.summary_metrics["row_count"] == 2
        assert test_result.summary_metrics["rouge/mean"] == 0.75
        assert test_result.summary_metrics["rouge/std"] == pytest.approx(0.35, 0.1)
        assert set(test_result.metrics_table.columns.values) == set(
            [
                "content",
                "reference",
                "response",
                "rouge",
            ]
        )
        assert list(test_result.metrics_table["rouge"].values) == [1, 0.5]

        api_requests = [
            call.kwargs["request"] for call in mock_evaluate_instances.call_args_list
        ]
        assert api_requests == list(_EXPECTED_ROUGE_REQUESTS)

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_compute_pairwise_metrics_with_model_inference(self, api_transport):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )
        eval_dataset = pd.DataFrame(
            {
                "context": ["test", "context"],
                "instruction": ["test", "instruction"],
            }
        )
        mock_baseline_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_baseline_model.generate_content.return_value = (
            _MOCK_MODEL_INFERENCE_RESPONSE
        )
        mock_baseline_model._model_name = "publishers/google/model/gemini-pro"
        mock_candidate_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_candidate_model.generate_content.return_value = (
            _MOCK_MODEL_INFERENCE_RESPONSE
        )
        mock_candidate_model._model_name = "publishers/google/model/gemini-pro"
        test_metrics = [
            _pairwise_summarization_quality.PairwiseSummarizationQuality(
                baseline_model=mock_baseline_model,
                use_reference=False,
            )
        ]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        mock_metric_results = _MOCK_PAIRWISE_SUMMARIZATION_QUALITY_RESULT
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=mock_metric_results,
        ):
            test_result = test_eval_task.evaluate(
                model=mock_candidate_model,
                prompt_template="{instruction} test prompt template {context}",
            )

        assert test_result.summary_metrics["row_count"] == 2
        assert set(test_result.metrics_table.columns.values) == set(
            [
                "context",
                "instruction",
                "completed_prompt",
                "response",
                "baseline_model_response",
                "pairwise_summarization_quality/pairwise_choice",
                "pairwise_summarization_quality/explanation",
                "pairwise_summarization_quality/confidence",
            ]
        )
        assert list(
            test_result.metrics_table[
                "pairwise_summarization_quality/pairwise_choice"
            ].values
        ) == ["BASELINE", "CANDIDATE"]
        assert list(
            test_result.metrics_table[
                "pairwise_summarization_quality/explanation"
            ].values
        ) == [
            "explanation",
            "explanation",
        ]
        assert list(
            test_result.metrics_table[
                "pairwise_summarization_quality/confidence"
            ].values
        ) == [
            1.0,
            0.5,
        ]
        assert set(test_result.summary_metrics.keys()) == set(
            [
                "row_count",
                "pairwise_summarization_quality/candidate_model_win_rate",
                "pairwise_summarization_quality/baseline_model_win_rate",
            ]
        )
        assert (
            test_result.summary_metrics[
                "pairwise_summarization_quality/candidate_model_win_rate"
            ]
            == 0.5
        )
        assert (
            test_result.summary_metrics[
                "pairwise_summarization_quality/baseline_model_win_rate"
            ]
            == 0.5
        )

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_compute_pairwise_metrics_without_inference(self, api_transport):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )
        eval_dataset = pd.DataFrame(
            {
                "response": ["test", "text"],
                "baseline_model_response": ["baseline", "response"],
                "reference": ["test", "reference"],
            }
        )
        test_metrics = [
            _pairwise_summarization_quality.PairwiseSummarizationQuality(
                baseline_model=None,
                use_reference=True,
            )
        ]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        mock_metric_results = _MOCK_PAIRWISE_SUMMARIZATION_QUALITY_RESULT
        with mock.patch.object(
            target=gapic_evaluation_services.EvaluationServiceClient,
            attribute="evaluate_instances",
            side_effect=mock_metric_results,
        ):
            test_result = test_eval_task.evaluate()

        assert test_result.summary_metrics["row_count"] == 2
        assert set(test_result.metrics_table.columns.values) == set(
            [
                "response",
                "baseline_model_response",
                "reference",
                "pairwise_summarization_quality/pairwise_choice",
                "pairwise_summarization_quality/explanation",
                "pairwise_summarization_quality/confidence",
            ]
        )
        assert list(
            test_result.metrics_table[
                "pairwise_summarization_quality/pairwise_choice"
            ].values
        ) == ["BASELINE", "CANDIDATE"]
        assert list(
            test_result.metrics_table[
                "pairwise_summarization_quality/explanation"
            ].values
        ) == [
            "explanation",
            "explanation",
        ]
        assert list(
            test_result.metrics_table[
                "pairwise_summarization_quality/confidence"
            ].values
        ) == [
            1.0,
            0.5,
        ]
        assert set(test_result.summary_metrics.keys()) == set(
            [
                "row_count",
                "pairwise_summarization_quality/candidate_model_win_rate",
                "pairwise_summarization_quality/baseline_model_win_rate",
            ]
        )
        assert (
            test_result.summary_metrics[
                "pairwise_summarization_quality/candidate_model_win_rate"
            ]
            == 0.5
        )
        assert (
            test_result.summary_metrics[
                "pairwise_summarization_quality/baseline_model_win_rate"
            ]
            == 0.5
        )

    def test_eval_result_experiment_run_logging(self):
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET,
            metrics=_TEST_METRICS,
            experiment=_TEST_EXPERIMENT,
        )

        with mock.patch.multiple(
            metadata._experiment_tracker,
            _experiment=mock.MagicMock(name=_TEST_EXPERIMENT),
            _experiment_run=None,
            set_experiment=mock.DEFAULT,
            reset=mock.DEFAULT,
        ):
            with mock.patch.multiple(
                vertexai.preview,
                start_run=mock.MagicMock(),
                log_params=mock.DEFAULT,
                log_metrics=mock.DEFAULT,
            ) as mock_metadata:
                with mock.patch.object(
                    target=_evaluation,
                    attribute="evaluate",
                    side_effect=[MOCK_EVAL_RESULT],
                ):
                    test_result = test_eval_task.evaluate()

        assert test_result.summary_metrics["row_count"] == 1
        assert test_result.summary_metrics["mock_metric/mean"] == 1.0
        assert test_result.summary_metrics["mock_metric/std"] == "NaN"
        mock_metadata["log_metrics"].assert_called_once_with(
            {
                "row_count": 1,
                "mock_metric/mean": 1.0,
                "mock_metric/std": "NaN",
            }
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestEvaluationErrors:
    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_evaluate_empty_metrics(self):
        test_eval_task = evaluation.EvalTask(dataset=_TEST_EVAL_DATASET, metrics=[])
        with pytest.raises(ValueError, match="Metrics cannot be empty."):
            test_eval_task.evaluate()

    def test_evaluate_invalid_metrics(self):
        metric_name = "invalid_metric"
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET, metrics=[metric_name]
        )
        with pytest.raises(
            ValueError, match=f"Metric name: {metric_name} not supported."
        ):
            test_eval_task.evaluate()

    def test_evaluate_duplicate_string_metric(self):
        metrics = ["summarization_quality", "summarization_quality"]
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET, metrics=metrics
        )
        with pytest.raises(
            ValueError,
            match="Duplicate string metric name found: 'summarization_quality'",
        ):
            test_eval_task.evaluate()

    def test_evaluate_duplicate_string_metric_with_metric_bundle(self):
        metrics = ["summarization_quality", "summarization_pointwise_reference_free"]
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET, metrics=metrics
        )
        with pytest.raises(
            ValueError,
            match="Duplicate string metric name found: 'summarization_quality'",
        ):
            test_eval_task.evaluate()

    def test_evaluate_duplicate_metric_instances(self):
        metrics = [
            _rouge.Rouge(rouge_type="rouge6"),
            _rouge.Rouge(rouge_type="rougeLsum"),
        ]
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET, metrics=metrics
        )
        with pytest.raises(
            ValueError,
            match="Duplicate Metric instances of the same metric name found: 'rouge'",
        ):
            test_eval_task.evaluate()

    def test_evaluate_invalid_experiment_run_name(self):
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET, metrics=_TEST_METRICS
        )
        with pytest.raises(ValueError, match="Experiment is not set"):
            test_eval_task.evaluate(experiment_run_name="invalid_experiment_run_name")

        with pytest.raises(ValueError, match="Experiment is not set"):
            test_eval_task.display_runs()

    def test_evaluate_experiment_name_already_exists(self, mock_experiment_tracker):
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET,
            metrics=_TEST_METRICS,
            experiment="test_eval_experiment_name",
        )
        mock_experiment_tracker.experiment_run.return_value = "experiment_run_1"
        with pytest.raises(ValueError, match="Experiment run already exists"):
            test_eval_task.evaluate(experiment_run_name="experiment_run_2")

    def test_evaluate_invalid_dataset_content_column(self):
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET_WITHOUT_RESPONSE,
            metrics=_TEST_METRICS,
        )
        with pytest.raises(KeyError, match="Required column `content` not found"):
            test_eval_task.evaluate(model=mock.MagicMock())

    def test_evaluate_invalid_prompt_template_placeholder(self):
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET_WITHOUT_RESPONSE,
            metrics=_TEST_METRICS,
        )
        with pytest.raises(ValueError, match="Failed to complete prompt template"):
            test_eval_task.evaluate(
                prompt_template="test_prompt_template {invalid_placeholder}",
            )

    def test_evaluate_pairwise_metrics_with_multiple_baseline_models(self):
        eval_dataset = pd.DataFrame(
            {
                "context": ["test", "context"],
                "instruction": ["test", "instruction"],
            }
        )
        mock_baseline_model_1 = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_baseline_model_1._model_name = "publishers/google/model/gemini-1.0-pro"
        mock_baseline_model_2 = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_baseline_model_2._model_name = "publishers/google/model/gemini-1.5-pro"
        mock_candidate_model = mock.create_autospec(
            generative_models.GenerativeModel, instance=True
        )
        mock_candidate_model._model_name = "publishers/google/model/gemini-1.0-ultra"
        test_metrics = [
            _pairwise_summarization_quality.PairwiseSummarizationQuality(
                baseline_model=mock_baseline_model_1,
            ),
            _pairwise_question_answering_quality.PairwiseQuestionAnsweringQuality(
                baseline_model=mock_baseline_model_2,
            ),
        ]
        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        with pytest.raises(
            ValueError,
            match="Not all PairwiseMetric instances have the same baseline_model",
        ):
            test_eval_task.evaluate(model=mock_candidate_model)

    def test_evaluate_invalid_model_and_dataset_input(self):
        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET,
            metrics=_TEST_METRICS,
        )
        with pytest.raises(
            ValueError,
            match=("The `model` parameter is specified, but the evaluation `dataset`"),
        ):
            test_eval_task.evaluate(
                model=generative_models.GenerativeModel(model_name="invalid_model_name")
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestEvaluationUtils:
    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_create_evaluation_service_client(self):
        client = utils.create_evaluation_service_client()
        assert isinstance(client, utils._EvaluationServiceClientWithOverride)

    def test_load_dataset_from_dataframe(self):
        data = {"col1": [1, 2], "col2": ["a", "b"]}
        df = pd.DataFrame(data)
        loaded_df = utils.load_dataset(df)
        assert loaded_df.equals(df)

    def test_load_dataset_from_dict(self):
        data = {"col1": [1, 2], "col2": ["a", "b"]}
        loaded_df = utils.load_dataset(data)
        assert isinstance(loaded_df, pd.DataFrame)
        assert loaded_df.to_dict("list") == data

    def test_load_dataset_from_gcs_jsonl(self):
        source = "gs://test_bucket/test_file.jsonl"
        with mock.patch.object(
            utils,
            "_read_gcs_file_contents",
            return_value=_TEST_JSONL_FILE_CONTENT,
        ):
            loaded_df = utils.load_dataset(source)

        assert isinstance(loaded_df, pd.DataFrame)
        assert loaded_df.to_dict("list") == {
            "prompt": ["prompt", "test"],
            "reference": ["reference", "test"],
        }

    def test_load_dataset_from_gcs_csv(self):
        source = "gs://test_bucket/test_file.csv"
        with mock.patch.object(
            utils, "_read_gcs_file_contents", return_value=_TEST_CSV_FILE_CONTENT
        ):
            loaded_df = utils.load_dataset(source)

        assert isinstance(loaded_df, pd.DataFrame)
        assert loaded_df.to_dict("list") == {
            "reference": ["test", "text"],
            "context": ["test", "text"],
            "instruction": ["test", "text"],
        }

    def test_load_dataset_from_bigquery(self):
        source = "bq://project-id.dataset.table_name"
        with mock.patch.object(
            utils, "_load_bigquery", return_value=_TEST_EVAL_DATASET
        ):
            loaded_df = utils.load_dataset(source)

        assert isinstance(loaded_df, pd.DataFrame)
        assert loaded_df.equals(_TEST_EVAL_DATASET)

    def test_initialization(self):
        limiter = utils.RateLimiter(rate=2)
        assert limiter.seconds_per_event == 0.5

        with pytest.raises(ValueError, match="Rate must be a positive number"):
            utils.RateLimiter(-1)
        with pytest.raises(ValueError, match="Rate must be a positive number"):
            utils.RateLimiter(0)

    def test_admit(self):
        rate_limiter = utils.RateLimiter(rate=2)

        assert rate_limiter._admit() == 0

        time.sleep(0.1)
        delay = rate_limiter._admit()
        assert delay == pytest.approx(0.4, 0.01)

        time.sleep(0.5)
        delay = rate_limiter._admit()
        assert delay == 0

    def test_sleep_and_advance(self):
        rate_limiter = utils.RateLimiter(rate=2)

        start_time = time.time()
        rate_limiter.sleep_and_advance()
        assert (time.time() - start_time) < 0.1

        start_time = time.time()
        rate_limiter.sleep_and_advance()
        assert (time.time() - start_time) >= 0.5

    def test_thread_safety(self):
        rate_limiter = utils.RateLimiter(rate=2)
        start_time = time.time()

        def target():
            rate_limiter.sleep_and_advance()

        threads = [threading.Thread(target=target) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        # Verify that the total minimum time should be 4.5 seconds
        # (9 intervals of 0.5 seconds each).
        total_time = time.time() - start_time
        assert total_time >= 4.5


class TestPromptTemplate:
    def test_init(self):
        template_str = "Hello, {name}!"
        prompt_template = evaluation.PromptTemplate(template_str)
        assert prompt_template.template == template_str

    def test_get_placeholders(self):
        template_str = "Hello, {name}! Today is {day}."
        prompt_template = evaluation.PromptTemplate(template_str)
        assert prompt_template.placeholders == {"name", "day"}

    def test_format(self):
        template_str = "Hello, {name}! Today is {day}."
        prompt_template = evaluation.PromptTemplate(template_str)
        completed_prompt = prompt_template.assemble(name="John", day="Monday")
        assert str(completed_prompt) == "Hello, John! Today is Monday."

    def test_format_missing_placeholder(self):
        template_str = "Hello, {name}!"
        prompt_template = evaluation.PromptTemplate(template_str)
        completed_prompt = prompt_template.assemble()
        assert str(completed_prompt) == "Hello, {name}!"
        assert prompt_template.placeholders == {"name"}

    def test_partial_format(self):
        template_str = "Hello, {name}! Today is {day}."
        prompt_template = evaluation.PromptTemplate(template_str)
        partially_completed_prompt = prompt_template.assemble(name="John")

        assert isinstance(partially_completed_prompt, evaluation.PromptTemplate)
        assert str(partially_completed_prompt) == "Hello, John! Today is {day}."
        assert partially_completed_prompt.placeholders == {"day"}

        completed_prompt = partially_completed_prompt.assemble(day="Monday")
        assert str(completed_prompt) == "Hello, John! Today is Monday."

    def test_str(self):
        template_str = "Hello, world!"
        prompt_template = evaluation.PromptTemplate(template_str)
        assert str(prompt_template) == template_str

    def test_repr(self):
        template_str = "Hello, {name}!"
        prompt_template = evaluation.PromptTemplate(template_str)
        assert repr(prompt_template) == f"PromptTemplate('{template_str}')"
