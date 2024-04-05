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
from vertexai.preview import evaluation
from vertexai.preview.evaluation import utils
import pandas as pd
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METRICS = [
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
]
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


_MOCK_EXACT_MATCH_RESULT = [
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
]

_MOCK_FLUENCY_RESULT = [
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
]


@pytest.fixture
def mock_async_event_loop():
    with mock.patch("asyncio.get_event_loop") as mock_async_event_loop:
        yield mock_async_event_loop


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
        test_experiment = "test_experiment_name"
        test_content_column_name = "test_content_column_name"
        test_reference_column_name = "test_reference_column_name"
        test_response_column_name = "test_response_column_name"

        test_eval_task = evaluation.EvalTask(
            dataset=_TEST_EVAL_DATASET,
            metrics=_TEST_METRICS,
            experiment=test_experiment,
            content_column_name=test_content_column_name,
            reference_column_name=test_reference_column_name,
            response_column_name=test_response_column_name,
        )

        assert test_eval_task.dataset.equals(_TEST_EVAL_DATASET)
        assert test_eval_task.metrics == _TEST_METRICS
        assert test_eval_task.experiment == test_experiment
        assert test_eval_task.content_column_name == test_content_column_name
        assert test_eval_task.reference_column_name == test_reference_column_name
        assert test_eval_task.response_column_name == test_response_column_name

    def test_evaluate_saved_response(self, mock_async_event_loop):
        eval_dataset = _TEST_EVAL_DATASET
        test_metrics = _TEST_METRICS
        mock_summary_metrics = {
            "row_count": 2,
            "mock_metric/mean": 0.5,
            "mock_metric/std": 0.5,
        }
        mock_metrics_table = pd.DataFrame(
            {
                "response": ["test", "text"],
                "reference": ["test", "ref"],
                "mock_metric": [1.0, 0.0],
            }
        )
        mock_async_event_loop.return_value.run_until_complete.return_value = (
            mock_summary_metrics,
            mock_metrics_table,
        )

        test_eval_task = evaluation.EvalTask(dataset=eval_dataset, metrics=test_metrics)
        test_result = test_eval_task.evaluate()

        assert test_result.summary_metrics == mock_summary_metrics
        assert test_result.metrics_table.equals(mock_metrics_table)

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
            target=gapic_evaluation_services.EvaluationServiceAsyncClient,
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
            target=gapic_evaluation_services.EvaluationServiceAsyncClient,
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


@pytest.mark.usefixtures("google_auth_mock")
class TestEvaluationUtils:
    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_create_evaluation_service_async_client(self):
        client = utils.create_evaluation_service_async_client()
        assert isinstance(client, utils._EvaluationServiceAsyncClientWithOverride)

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
