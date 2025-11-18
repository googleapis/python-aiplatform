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
import importlib
import json
import os
import statistics
import sys
from unittest import mock

import google.auth.credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
from vertexai import _genai
from vertexai._genai import _evals_data_converters
from vertexai._genai import _evals_metric_handlers
from vertexai._genai import _evals_visualization
from vertexai._genai import _evals_metric_loaders
from vertexai._genai import _gcs_utils
from vertexai._genai import _observability_data_converter
from vertexai._genai import evals
from vertexai._genai import types as vertexai_genai_types
from google.genai import client
from google.genai import errors as genai_errors
from google.genai import types as genai_types
import pandas as pd
import pytest


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_evals_common = _genai.evals._evals_common
_evals_utils = _genai._evals_utils

pytestmark = pytest.mark.usefixtures("google_auth_mock")


def _create_content_dump(text: str) -> dict[str, list[genai_types.Content]]:
    return {
        "contents": [
            genai_types.Content(parts=[genai_types.Part(text=text)]).model_dump(
                mode="json", exclude_none=True
            )
        ]
    }


@pytest.fixture
def mock_api_client_fixture():
    mock_client = mock.Mock(spec=client.Client)
    mock_client.project = _TEST_PROJECT
    mock_client.location = _TEST_LOCATION
    mock_client._credentials = mock.create_autospec(
        google.auth.credentials.Credentials, instance=True
    )
    mock_client._credentials.universe_domain = "googleapis.com"
    mock_client._evals_client = mock.Mock(spec=evals.Evals)
    return mock_client


@pytest.fixture
def mock_eval_dependencies(mock_api_client_fixture):
    with mock.patch("google.cloud.storage.Client") as mock_storage_client, mock.patch(
        "google.cloud.bigquery.Client"
    ) as mock_bq_client, mock.patch(
        "vertexai._genai.evals.Evals.evaluate_instances"
    ) as mock_evaluate_instances, mock.patch(
        "vertexai._genai._gcs_utils.GcsUtils.upload_json_to_prefix"
    ) as mock_upload_to_gcs, mock.patch(
        "vertexai._genai._evals_metric_loaders.LazyLoadedPrebuiltMetric._fetch_and_parse"
    ) as mock_fetch_prebuilt_metric:

        def mock_evaluate_instances_side_effect(*args, **kwargs):
            metric_config = kwargs.get("metric_config", {})
            if "exact_match_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    exact_match_results=vertexai_genai_types.ExactMatchResults(
                        exact_match_metric_values=[
                            vertexai_genai_types.ExactMatchMetricValue(score=1.0)
                        ]
                    )
                )
            elif "rouge_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    rouge_results=vertexai_genai_types.RougeResults(
                        rouge_metric_values=[
                            vertexai_genai_types.RougeMetricValue(score=0.8)
                        ]
                    )
                )
            elif "pointwise_metric_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    pointwise_metric_result=vertexai_genai_types.PointwiseMetricResult(
                        score=0.9, explanation="Mocked LLM explanation"
                    )
                )
            elif "comet_input" in metric_config:
                return vertexai_genai_types.EvaluateInstancesResponse(
                    comet_result=vertexai_genai_types.CometResult(score=0.75)
                )
            return vertexai_genai_types.EvaluateInstancesResponse()

        mock_evaluate_instances.side_effect = mock_evaluate_instances_side_effect
        mock_upload_to_gcs.return_value = (
            "gs://mock-bucket/mock_path/evaluation_result_timestamp.json"
        )
        mock_prebuilt_fluency_metric = vertexai_genai_types.LLMMetric(
            name="fluency", prompt_template="Is this fluent? {response}"
        )
        mock_prebuilt_fluency_metric._is_predefined = True
        mock_prebuilt_fluency_metric._config_source = (
            "gs://mock-metrics/fluency/v1.yaml"
        )
        mock_prebuilt_fluency_metric._version = "v1"

        mock_fetch_prebuilt_metric.return_value = mock_prebuilt_fluency_metric

        yield {
            "mock_storage_client": mock_storage_client,
            "mock_bq_client": mock_bq_client,
            "mock_evaluate_instances": mock_evaluate_instances,
            "mock_upload_to_gcs": mock_upload_to_gcs,
            "mock_fetch_prebuilt_metric": mock_fetch_prebuilt_metric,
            "mock_prebuilt_fluency_metric": mock_prebuilt_fluency_metric,
        }


class TestEvals:
    """Unit tests for the GenAI client."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_eval_run(self):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(NotImplementedError):
            test_client.evals.run()

    @pytest.mark.usefixtures("google_auth_mock")
    @mock.patch.object(client.Client, "_get_api_client")
    @mock.patch.object(evals.Evals, "batch_evaluate")
    def test_eval_batch_evaluate(self, mock_evaluate, mock_get_api_client):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_client.evals.batch_evaluate(
            dataset=vertexai_genai_types.EvaluationDataset(),
            metrics=[vertexai_genai_types.Metric(name="test")],
            dest="gs://bucket/output",
            config=vertexai_genai_types.EvaluateDatasetConfig(),
        )
        mock_evaluate.assert_called_once()

    @pytest.mark.usefixtures("google_auth_mock")
    @mock.patch.object(_evals_common, "_execute_evaluation")
    def test_eval_evaluate_with_agent_info(self, mock_execute_evaluation):
        """Tests that agent_info is passed to _execute_evaluation."""
        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame([{"prompt": "p1", "response": "r1"}])
        )
        agent_info = {"agent1": {"name": "agent1", "instruction": "instruction1"}}
        self.client.evals.evaluate(
            dataset=dataset,
            metrics=[vertexai_genai_types.Metric(name="exact_match")],
            agent_info=agent_info,
        )
        mock_execute_evaluation.assert_called_once()
        _, kwargs = mock_execute_evaluation.call_args
        assert "agent_info" in kwargs
        assert kwargs["agent_info"] == agent_info


class TestEvalsVisualization:
    @mock.patch(
        "vertexai._genai._evals_visualization._is_ipython_env",
        return_value=True,
    )
    def test_display_evaluation_result_with_agent_trace_prefixes(self, mock_is_ipython):
        """Tests that agent trace view includes added prefixes."""
        mock_display_module = mock.MagicMock()
        mock_ipython_module = mock.MagicMock()
        mock_ipython_module.display = mock_display_module
        sys.modules["IPython"] = mock_ipython_module
        sys.modules["IPython.display"] = mock_display_module

        intermediate_events_list = [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "function_call": {
                                "name": "my_function",
                                "args": {"arg1": "value1"},
                            }
                        }
                    ],
                }
            },
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "this is model response"}],
                }
            },
        ]
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "intermediate_events": intermediate_events_list,
                },
            ]
        )
        eval_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        eval_result = vertexai_genai_types.EvaluationResult(
            evaluation_dataset=[eval_dataset],
            agent_info=vertexai_genai_types.evals.AgentInfo(name="test_agent"),
            eval_case_results=[
                vertexai_genai_types.EvalCaseResult(
                    eval_case_index=0,
                    response_candidate_results=[
                        vertexai_genai_types.ResponseCandidateResult(
                            response_index=0, metric_results={}
                        )
                    ],
                )
            ],
        )

        _evals_visualization.display_evaluation_result(eval_result)

        mock_display_module.HTML.assert_called_once()
        html_content = mock_display_module.HTML.call_args[0][0]
        assert "my_function" in html_content
        assert "this is model response" in html_content

        del sys.modules["IPython"]
        del sys.modules["IPython.display"]


class TestEvalsRunInference:
    """Unit tests for the Evals run_inference method."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(_genai.client)
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_utils)
        importlib.reload(_evals_data_converters)
        importlib.reload(_evals_common)
        importlib.reload(_evals_metric_handlers)
        importlib.reload(_genai.evals)

        if hasattr(_evals_common._thread_local_data, "agent_engine_instances"):
            del _evals_common._thread_local_data.agent_engine_instances

        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_string_model_success(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="test response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_models.return_value.generate_content.assert_called_once()
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["test prompt"],
                    "response": ["test response"],
                }
            ),
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_callable_model_sets_candidate_name(
        self, mock_eval_dataset_loader
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        def my_model_fn(contents):
            return "callable response"

        inference_result = self.client.evals.run_inference(
            model=my_model_fn,
            src=mock_df,
        )
        assert inference_result.candidate_name == "my_model_fn"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_lambda_model_candidate_name_is_none(
        self, mock_eval_dataset_loader
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        inference_result = self.client.evals.run_inference(
            model=lambda x: "lambda response",  # pylint: disable=unnecessary-lambda
            src=mock_df,
        )
        # Lambdas may or may not have a __name__ depending on Python version/env
        # but it's typically '<lambda>' if it exists.
        # The code under test uses getattr(model, "__name__", None)
        assert (
            inference_result.candidate_name == "<lambda>"
            or inference_result.candidate_name is None
        )
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_callable_model_success(self, mock_eval_dataset_loader):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        def mock_model_fn(contents):
            return "callable response"

        inference_result = self.client.evals.run_inference(
            model=mock_model_fn,
            src=mock_df,
        )
        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["test prompt"],
                    "response": ["callable response"],
                }
            ),
        )
        assert inference_result.candidate_name == "mock_model_fn"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_prompt_template(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame({"text_input": ["world"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="templated response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        config = vertexai_genai_types.EvalRunInferenceConfig(
            prompt_template="Hello {text_input}"
        )
        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )
        assert (
            mock_models.return_value.generate_content.call_args[1]["contents"]
            == "Hello world"
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "text_input": ["world"],
                    "request": ["Hello world"],
                    "response": ["templated response"],
                }
            ),
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_inference_with_gcs_destination(
        self, mock_gcs_utils, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="gcs response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        gcs_dest_dir = "gs://bucket/output"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=gcs_dest_dir)

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

        expected_gcs_path = os.path.join(gcs_dest_dir, "inference_results.jsonl")
        expected_df_to_save = pd.DataFrame(
            {
                "prompt": ["test prompt"],
                "response": ["gcs response"],
            }
        )
        saved_df = mock_gcs_utils.return_value.upload_dataframe.call_args.kwargs["df"]
        pd.testing.assert_frame_equal(saved_df, expected_df_to_save)
        mock_gcs_utils.return_value.upload_dataframe.assert_called_once_with(
            df=mock.ANY,
            gcs_destination_blob_path=expected_gcs_path,
            file_type="jsonl",
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df, expected_df_to_save
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source == vertexai_genai_types.GcsSource(
            uris=[expected_gcs_path]
        )

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("pandas.DataFrame.to_json")
    @mock.patch("os.makedirs")
    def test_inference_with_local_destination(
        self,
        mock_makedirs,
        mock_df_to_json,
        mock_eval_dataset_loader,
        mock_models,
    ):
        mock_df = pd.DataFrame({"prompt": ["local save"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="local response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        local_dest_dir = "/tmp/test/output_dir"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=local_dest_dir)

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

        mock_makedirs.assert_called_once_with(local_dest_dir, exist_ok=True)
        expected_save_path = os.path.join(local_dest_dir, "inference_results.jsonl")
        mock_df_to_json.assert_called_once_with(
            expected_save_path, orient="records", lines=True
        )
        expected_df = pd.DataFrame(
            {
                "prompt": ["local save"],
                "response": ["local response"],
            }
        )
        pd.testing.assert_frame_equal(inference_result.eval_dataset_df, expected_df)
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_from_request_column_save_to_local_dir(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame(
            {"prompt": ["prompt 1", "prompt 2"], "request": ["req 1", "req 2"]}
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_responses = [
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 1")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 2")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
        ]
        mock_models.return_value.generate_content.side_effect = (
            mock_generate_content_responses
        )

        local_dest_dir = "/tmp/test_output_dir"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=local_dest_dir)

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

        mock_models.return_value.generate_content.assert_has_calls(
            [
                mock.call(
                    model="gemini-pro",
                    contents="req 1",
                    config=genai_types.GenerateContentConfig(),
                ),
                mock.call(
                    model="gemini-pro",
                    contents="req 2",
                    config=genai_types.GenerateContentConfig(),
                ),
            ],
            any_order=True,
        )
        expected_df = pd.DataFrame(
            {
                "prompt": ["prompt 1", "prompt 2"],
                "request": ["req 1", "req 2"],
                "response": ["resp 1", "resp 2"],
            }
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.sort_values(by="request").reset_index(
                drop=True
            ),
            expected_df.sort_values(by="request").reset_index(drop=True),
        )

        saved_file_path = os.path.join(local_dest_dir, "inference_results.jsonl")
        with open(saved_file_path, "r") as f:
            saved_records = [json.loads(line) for line in f]
        expected_records = expected_df.to_dict(orient="records")
        assert sorted(saved_records, key=lambda x: x["request"]) == sorted(
            expected_records, key=lambda x: x["request"]
        )
        os.remove(saved_file_path)
        os.rmdir(local_dest_dir)
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    def test_inference_from_local_jsonl_file(self, mock_models):
        local_src_path = "/tmp/input.jsonl"
        input_records = [
            {"prompt": "prompt 1", "other_col": "val 1"},
            {"prompt": "prompt 2", "other_col": "val 2"},
        ]
        with open(local_src_path, "w") as f:
            for record in input_records:
                f.write(json.dumps(record) + "\n")

        mock_generate_content_responses = [
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 1")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 2")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
        ]
        mock_models.return_value.generate_content.side_effect = (
            mock_generate_content_responses
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=local_src_path
        )

        expected_df = pd.DataFrame(
            {
                "prompt": ["prompt 1", "prompt 2"],
                "other_col": ["val 1", "val 2"],
                "response": ["resp 1", "resp 2"],
            }
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.sort_values(by="prompt").reset_index(
                drop=True
            ),
            expected_df.sort_values(by="prompt").reset_index(drop=True),
        )
        mock_models.return_value.generate_content.assert_has_calls(
            [
                mock.call(
                    model="gemini-pro",
                    contents="prompt 1",
                    config=genai_types.GenerateContentConfig(),
                ),
                mock.call(
                    model="gemini-pro",
                    contents="prompt 2",
                    config=genai_types.GenerateContentConfig(),
                ),
            ],
            any_order=True,
        )
        os.remove(local_src_path)
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @pytest.mark.skip(reason="currently flakey")
    @mock.patch.object(_evals_common, "Models")
    def test_inference_from_local_csv_file(self, mock_models):
        local_src_path = "/tmp/input.csv"
        input_df = pd.DataFrame(
            {"prompt": ["prompt 1", "prompt 2"], "other_col": ["val 1", "val 2"]}
        )
        input_df.to_csv(local_src_path, index=False)

        mock_generate_content_responses = [
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 1")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="resp 2")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
        ]
        mock_models.return_value.generate_content.side_effect = (
            mock_generate_content_responses
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=local_src_path
        )

        expected_df = pd.DataFrame(
            {
                "prompt": ["prompt 1", "prompt 2"],
                "other_col": ["val 1", "val 2"],
                "response": ["resp 1", "resp 2"],
            }
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.sort_values(by="prompt").reset_index(
                drop=True
            ),
            expected_df.sort_values(by="prompt").reset_index(drop=True),
        )
        mock_models.return_value.generate_content.assert_has_calls(
            [
                mock.call(
                    model="gemini-pro",
                    contents="prompt 1",
                    config=genai_types.GenerateContentConfig(),
                ),
                mock.call(
                    model="gemini-pro",
                    contents="prompt 2",
                    config=genai_types.GenerateContentConfig(),
                ),
            ],
            any_order=True,
        )
        os.remove(local_src_path)
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_row_level_config_overrides(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "request": [
                    {
                        "contents": [
                            {
                                "parts": [{"text": "Placeholder prompt 1"}],
                                "role": "user",
                            }
                        ]
                    },
                    {
                        "contents": [
                            {
                                "parts": [{"text": "Placeholder prompt 2.1"}],
                                "role": "user",
                            },
                            {
                                "parts": [{"text": "Placeholder model response 2.1"}],
                                "role": "model",
                            },
                            {
                                "parts": [{"text": "Placeholder prompt 2.2"}],
                                "role": "user",
                            },
                        ],
                        "generation_config": {"temperature": 0.7, "top_k": 5},
                    },
                    {
                        "contents": [
                            {
                                "parts": [{"text": "Placeholder prompt 3"}],
                                "role": "user",
                            }
                        ],
                    },
                ],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_responses = [
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="Placeholder response 1")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="Placeholder response 2")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
            genai_types.GenerateContentResponse(
                candidates=[
                    genai_types.Candidate(
                        content=genai_types.Content(
                            parts=[genai_types.Part(text="Placeholder response 3")]
                        ),
                        finish_reason=genai_types.FinishReason.STOP,
                    )
                ],
                prompt_feedback=None,
            ),
        ]

        def mock_generate_content_logic(*args, **kwargs):
            contents = kwargs.get("contents")
            first_part_text = contents[0]["parts"][0]["text"]
            if "Placeholder prompt 1" in first_part_text:
                return mock_generate_content_responses[0]
            elif "Placeholder prompt 2.1" in first_part_text:
                return mock_generate_content_responses[1]
            elif "Placeholder prompt 3" in first_part_text:
                return mock_generate_content_responses[2]
            return genai_types.GenerateContentResponse()

        mock_models.return_value.generate_content.side_effect = (
            mock_generate_content_logic
        )

        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df
        )

        mock_models.return_value.generate_content.assert_has_calls(
            [
                mock.call(
                    model="gemini-pro",
                    contents=[
                        {
                            "parts": [{"text": "Placeholder prompt 1"}],
                            "role": "user",
                        }
                    ],
                    config=genai_types.GenerateContentConfig(),
                ),
                mock.call(
                    model="gemini-pro",
                    contents=[
                        {
                            "parts": [{"text": "Placeholder prompt 2.1"}],
                            "role": "user",
                        },
                        {
                            "parts": [{"text": "Placeholder model response 2.1"}],
                            "role": "model",
                        },
                        {
                            "parts": [{"text": "Placeholder prompt 2.2"}],
                            "role": "user",
                        },
                    ],
                    config=genai_types.GenerateContentConfig(temperature=0.7, top_k=5),
                ),
                mock.call(
                    model="gemini-pro",
                    contents=[
                        {
                            "parts": [{"text": "Placeholder prompt 3"}],
                            "role": "user",
                        }
                    ],
                    config=genai_types.GenerateContentConfig(),
                ),
            ],
            any_order=True,
        )

        request_obj_1 = {
            "contents": [{"parts": [{"text": "Placeholder prompt 1"}], "role": "user"}]
        }
        request_obj_2 = {
            "contents": [
                {"parts": [{"text": "Placeholder prompt 2.1"}], "role": "user"},
                {
                    "parts": [{"text": "Placeholder model response 2.1"}],
                    "role": "model",
                },
                {"parts": [{"text": "Placeholder prompt 2.2"}], "role": "user"},
            ],
            "generation_config": {"temperature": 0.7, "top_k": 5},
        }
        request_obj_3 = {
            "contents": [{"parts": [{"text": "Placeholder prompt 3"}], "role": "user"}],
        }
        expected_df = pd.DataFrame(
            {
                "id": [1, 2, 3],
                "request": [request_obj_1, request_obj_2, request_obj_3],
                "response": [
                    "Placeholder response 1",
                    "Placeholder response 2",
                    "Placeholder response 3",
                ],
            }
        )
        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.sort_values(by="id").reset_index(
                drop=True
            ),
            expected_df.sort_values(by="id").reset_index(drop=True),
            check_dtype=False,
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_multimodal_content(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_media_content_json = genai_types.Content(
            parts=[
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="image/png",
                        file_uri="gs://fake-bucket/image.png",
                    )
                )
            ]
        ).model_dump_json(exclude_none=True)
        mock_df = pd.DataFrame(
            {
                "text_input": ["hello world"],
                "media_content": [mock_media_content_json],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )
        mock_generate_content_response = genai_types.GenerateContentResponse(
            candidates=[
                genai_types.Candidate(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="test response")]
                    ),
                    finish_reason=genai_types.FinishReason.STOP,
                )
            ],
            prompt_feedback=None,
        )
        mock_models.return_value.generate_content.return_value = (
            mock_generate_content_response
        )

        config = vertexai_genai_types.EvalRunInferenceConfig(
            prompt_template="multimodal prompt: {media_content}{text_input}"
        )
        inference_result = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )
        assembled_prompt_json = genai_types.Content(
            parts=[
                genai_types.Part(text="multimodal prompt: "),
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="image/png",
                        file_uri="gs://fake-bucket/image.png",
                    )
                ),
                genai_types.Part(text="hello world"),
            ]
        ).model_dump_json(exclude_none=True)

        assert (
            mock_models.return_value.generate_content.call_args[1]["contents"]
            == assembled_prompt_json
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "text_input": ["hello world"],
                    "media_content": [mock_media_content_json],
                    "request": [assembled_prompt_json],
                    "response": ["test response"],
                }
            ),
        )
        assert inference_result.candidate_name == "gemini-pro"
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_and_session_inputs_dict(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    }
                ],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_engine = mock.Mock()
        mock_agent_engine.create_session.return_value = {"id": "session1"}
        stream_query_return_value = [
            {
                "id": "1",
                "content": {"parts": [{"text": "intermediate1"}]},
                "timestamp": 123,
                "author": "model",
            },
            {
                "id": "2",
                "content": {"parts": [{"text": "agent response"}]},
                "timestamp": 124,
                "author": "model",
            },
        ]

        mock_agent_engine.stream_query.return_value = iter(stream_query_return_value)
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        inference_result = self.client.evals.run_inference(
            agent="projects/test-project/locations/us-central1/reasoningEngines/123",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_vertexai_client.return_value.agent_engines.get.assert_called_once_with(
            name="projects/test-project/locations/us-central1/reasoningEngines/123"
        )
        mock_agent_engine.create_session.assert_called_once_with(
            user_id="123", state={"a": "1"}
        )
        mock_agent_engine.stream_query.assert_called_once_with(
            user_id="123", session_id="session1", message="agent prompt"
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["agent prompt"],
                    "session_inputs": [
                        {
                            "user_id": "123",
                            "state": {"a": "1"},
                        }
                    ],
                    "intermediate_events": [
                        [
                            {
                                "event_id": "1",
                                "content": {"parts": [{"text": "intermediate1"}]},
                                "creation_timestamp": 123,
                                "author": "model",
                            }
                        ]
                    ],
                    "response": ["agent response"],
                }
            ),
        )
        assert inference_result.candidate_name is None
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_and_session_inputs_literal_string(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        session_inputs_str = '{"user_id": "123", "state": {"a": "1"}}'
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [session_inputs_str],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_engine = mock.Mock()
        mock_agent_engine.create_session.return_value = {"id": "session1"}
        stream_query_return_value = [
            {
                "id": "1",
                "content": {"parts": [{"text": "intermediate1"}]},
                "timestamp": 123,
                "author": "model",
            },
            {
                "id": "2",
                "content": {"parts": [{"text": "agent response"}]},
                "timestamp": 124,
                "author": "model",
            },
        ]

        mock_agent_engine.stream_query.return_value = iter(stream_query_return_value)
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        inference_result = self.client.evals.run_inference(
            agent="projects/test-project/locations/us-central1/reasoningEngines/123",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_vertexai_client.return_value.agent_engines.get.assert_called_once_with(
            name="projects/test-project/locations/us-central1/reasoningEngines/123"
        )
        mock_agent_engine.create_session.assert_called_once_with(
            user_id="123", state={"a": "1"}
        )
        mock_agent_engine.stream_query.assert_called_once_with(
            user_id="123", session_id="session1", message="agent prompt"
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df,
            pd.DataFrame(
                {
                    "prompt": ["agent prompt"],
                    "session_inputs": [session_inputs_str],
                    "intermediate_events": [
                        [
                            {
                                "event_id": "1",
                                "content": {"parts": [{"text": "intermediate1"}]},
                                "creation_timestamp": 123,
                                "author": "model",
                            }
                        ]
                    ],
                    "response": ["agent response"],
                }
            ),
        )
        assert inference_result.candidate_name is None
        assert inference_result.gcs_source is None

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch("vertexai._genai._evals_common.vertexai.Client")
    def test_run_inference_with_agent_engine_with_response_column_raises_error(
        self,
        mock_vertexai_client,
        mock_eval_dataset_loader,
    ):
        mock_df = pd.DataFrame(
            {
                "prompt": ["agent prompt"],
                "session_inputs": [
                    {
                        "user_id": "123",
                        "state": {"a": "1"},
                    }
                ],
                "response": ["some response"],
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        mock_agent_engine = mock.Mock()
        mock_vertexai_client.return_value.agent_engines.get.return_value = (
            mock_agent_engine
        )

        with pytest.raises(ValueError) as excinfo:
            self.client.evals.run_inference(
                agent="projects/test-project/locations/us-central1/reasoningEngines/123",
                src=mock_df,
            )
        assert (
            "The eval dataset provided for agent run should not contain "
            "'intermediate_events' or 'response' columns"
        ) in str(excinfo.value)

    def test_run_inference_with_litellm_string_prompt_format(
        self,
        mock_api_client_fixture,
    ):
        """Tests inference with LiteLLM using a simple prompt string."""
        with mock.patch(
            "vertexai._genai._evals_common.litellm"
        ) as mock_litellm, mock.patch(
            "vertexai._genai._evals_common._call_litellm_completion"
        ) as mock_call_litellm_completion:
            mock_litellm.utils.get_valid_models.return_value = ["gpt-4o"]
            prompt_df = pd.DataFrame([{"prompt": "What is LiteLLM?"}])
            expected_messages = [{"role": "user", "content": "What is LiteLLM?"}]

            mock_response_dict = {
                "id": "test",
                "created": 123456,
                "model": "gpt-4o",
                "object": "chat.completion",
                "system_fingerprint": "123456",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "content": "LiteLLM is a library...",
                            "role": "assistant",
                            "annotations": [],
                        },
                        "provider_specific_fields": {},
                    }
                ],
                "usage": {
                    "completion_tokens": 114,
                    "prompt_tokens": 13,
                    "total_tokens": 127,
                },
                "service_tier": "default",
            }
            mock_call_litellm_completion.return_value = mock_response_dict
            evals_module = evals.Evals(api_client_=mock_api_client_fixture)

            result_dataset = evals_module.run_inference(
                model="gpt-4o",
                src=prompt_df,
            )

            mock_call_litellm_completion.assert_called_once()
            _, call_kwargs = mock_call_litellm_completion.call_args

            assert call_kwargs["model"] == "gpt-4o"
            assert call_kwargs["messages"] == expected_messages
            assert "response" in result_dataset.eval_dataset_df.columns
            response_content = result_dataset.eval_dataset_df["response"][0]
            assert response_content == "LiteLLM is a library..."

    def test_run_inference_with_litellm_openai_request_format(
        self,
        mock_api_client_fixture,
    ):
        """Tests inference with LiteLLM where the row contains an chat completion request body."""
        with mock.patch(
            "vertexai._genai._evals_common.litellm"
        ) as mock_litellm, mock.patch(
            "vertexai._genai._evals_common._call_litellm_completion"
        ) as mock_call_litellm_completion:
            mock_litellm.utils.get_valid_models.return_value = ["gpt-4o"]
            prompt_df = pd.DataFrame(
                [
                    {
                        "model": "gpt-4o",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a helpful assistant.",
                            },
                            {"role": "user", "content": "Hello!"},
                        ],
                    }
                ]
            )
            expected_messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"},
            ]

            mock_response_dict = {
                "id": "test",
                "created": 123456,
                "model": "gpt-4o",
                "object": "chat.completion",
                "system_fingerprint": "123456",
                "choices": [
                    {
                        "finish_reason": "stop",
                        "index": 0,
                        "message": {
                            "content": "Hello there",
                            "role": "assistant",
                            "annotations": [],
                        },
                        "provider_specific_fields": {},
                    }
                ],
                "usage": {
                    "completion_tokens": 114,
                    "prompt_tokens": 13,
                    "total_tokens": 127,
                },
                "service_tier": "default",
            }
            mock_call_litellm_completion.return_value = mock_response_dict
            evals_module = evals.Evals(api_client_=mock_api_client_fixture)

            result_dataset = evals_module.run_inference(
                model="gpt-4o",
                src=prompt_df,
            )

            mock_call_litellm_completion.assert_called_once()
            _, call_kwargs = mock_call_litellm_completion.call_args

            assert call_kwargs["model"] == "gpt-4o"
            assert call_kwargs["messages"] == expected_messages
            assert "response" in result_dataset.eval_dataset_df.columns
            response_content = result_dataset.eval_dataset_df["response"][0]
            assert response_content == "Hello there"

    def test_run_inference_with_unsupported_model_string(
        self,
        mock_api_client_fixture,
    ):
        with mock.patch(
            "vertexai._genai._evals_common.litellm"
        ) as mock_litellm_package:
            mock_litellm_package.utils.get_valid_models.return_value = []
            evals_module = evals.Evals(api_client_=mock_api_client_fixture)
            prompt_df = pd.DataFrame([{"prompt": "test"}])

            with pytest.raises(TypeError, match="Unsupported string model name"):
                evals_module.run_inference(
                    model="some-random-model/name", src=prompt_df
                )

    @mock.patch("vertexai._genai._evals_common.litellm", None)
    def test_run_inference_with_litellm_import_error(self, mock_api_client_fixture):
        evals_module = evals.Evals(api_client_=mock_api_client_fixture)
        prompt_df = pd.DataFrame([{"prompt": "test"}])
        with pytest.raises(
            ImportError,
            match="The 'litellm' library is required to use this model.",
        ):
            evals_module.run_inference(model="gpt-4o", src=prompt_df)

    @mock.patch.object(_evals_common, "_run_litellm_inference")
    @mock.patch.object(_evals_common, "_is_gemini_model")
    @mock.patch.object(_evals_common, "_is_litellm_model")
    @mock.patch.object(_evals_common, "_is_litellm_vertex_maas_model")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_run_inference_with_litellm_parsing(
        self,
        mock_eval_dataset_loader,
        mock_is_litellm_vertex_maas_model,
        mock_is_litellm_model,
        mock_is_gemini_model,
        mock_run_litellm_inference,
    ):
        """Tests the parsing logic for LiteLLM responses within _run_inference_internal."""
        mock_is_gemini_model.return_value = False
        mock_is_litellm_model.return_value = True
        mock_is_litellm_vertex_maas_model.return_value = False

        mock_df = pd.DataFrame(
            {
                "prompt": [
                    "prompt1",
                    "prompt2",
                    "prompt3",
                    "prompt4",
                    "prompt5",
                    "prompt6",
                ]
            }
        )
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        raw_responses = [
            {  # Successful response
                "choices": [{"message": {"content": "LiteLLM response 1"}}]
            },
            {"error": "LiteLLM call failed: API key error"},  # Response with error key
            {"id": "test-id-3"},  # Missing choices
            {"choices": [{"index": 0}]},  # Missing message
            {"choices": [{"message": {"role": "assistant"}}]},  # Missing content
            "Invalid JSON string",  # Non-dict response
        ]
        mock_run_litellm_inference.return_value = raw_responses
        # fmt: off
        with mock.patch("vertexai._genai._evals_common.litellm") as mock_litellm:
            # fmt: on
            mock_litellm.utils.get_valid_models.return_value = ["gpt-4o"]
            inference_result = self.client.evals.run_inference(
                model="gpt-4o",
                src=mock_df,
            )

        expected_responses = [
            "LiteLLM response 1",
            json.dumps({"error": "LiteLLM call failed: API key error"}),
            json.dumps(
                {
                    "error": "LiteLLM response missing 'choices'",
                    "details": {"id": "test-id-3"},
                }
            ),
            json.dumps(
                {
                    "error": "LiteLLM response missing 'message' in first choice",
                    "details": {"choices": [{"index": 0}]},
                }
            ),
            json.dumps(
                {
                    "error": "LiteLLM response missing 'content' in message",
                    "details": {"choices": [{"message": {"role": "assistant"}}]},
                }
            ),
            json.dumps(
                {
                    "error": "Invalid LiteLLM response format",
                    "details": "Invalid JSON string",
                }
            ),
        ]

        expected_df = pd.DataFrame(
            {
                "prompt": [
                    "prompt1",
                    "prompt2",
                    "prompt3",
                    "prompt4",
                    "prompt5",
                    "prompt6",
                ],
                "response": expected_responses,
            }
        )

        pd.testing.assert_frame_equal(
            inference_result.eval_dataset_df.reset_index(drop=True),
            expected_df.reset_index(drop=True),
            check_dtype=False,
        )
        mock_run_litellm_inference.assert_called_once()
        _, call_kwargs = mock_run_litellm_inference.call_args
        assert call_kwargs["model"] == "gpt-4o"
        pd.testing.assert_frame_equal(call_kwargs["prompt_dataset"], mock_df)


@pytest.mark.usefixtures("google_auth_mock")
class TestEvalsMetricHandlers:
    """Unit tests for utility functions in _evals_metric_handlers."""

    def test_has_tool_call_with_tool_call(self):
        events = [
            vertexai_genai_types.evals.Event(
                event_id="1",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part(
                            function_call=genai_types.FunctionCall(
                                name="search", args={}
                            )
                        )
                    ]
                ),
            )
        ]
        assert _evals_metric_handlers._has_tool_call(events)

    def test_has_tool_call_no_tool_call(self):
        events = [
            vertexai_genai_types.evals.Event(
                event_id="1",
                content=genai_types.Content(parts=[genai_types.Part(text="hello")]),
            )
        ]
        assert not _evals_metric_handlers._has_tool_call(events)

    def test_has_tool_call_empty_events(self):
        assert not _evals_metric_handlers._has_tool_call([])

    def test_has_tool_call_none_events(self):
        assert not _evals_metric_handlers._has_tool_call(None)

    def test_has_tool_call_mixed_events(self):
        events = [
            vertexai_genai_types.evals.Event(
                event_id="1",
                content=genai_types.Content(parts=[genai_types.Part(text="hello")]),
            ),
            vertexai_genai_types.evals.Event(
                event_id="2",
                content=genai_types.Content(
                    parts=[
                        genai_types.Part(
                            function_call=genai_types.FunctionCall(
                                name="search", args={}
                            )
                        )
                    ]
                ),
            ),
        ]
        assert _evals_metric_handlers._has_tool_call(events)


@pytest.mark.usefixtures("google_auth_mock")
class TestRunAgentInternal:
    """Unit tests for the _run_agent_internal function."""

    def setup_method(self):
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_common)

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_success(self, mock_run_agent):
        mock_run_agent.return_value = [
            [
                {
                    "id": "1",
                    "content": {"parts": [{"text": "intermediate1"}]},
                    "timestamp": 123,
                    "author": "model",
                },
                {
                    "id": "2",
                    "content": {"parts": [{"text": "final response"}]},
                    "timestamp": 124,
                    "author": "model",
                },
            ]
        ]
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            prompt_dataset=prompt_dataset,
        )

        expected_df = pd.DataFrame(
            {
                "prompt": ["prompt1"],
                "intermediate_events": [
                    [
                        {
                            "event_id": "1",
                            "content": {"parts": [{"text": "intermediate1"}]},
                            "creation_timestamp": 123,
                            "author": "model",
                        }
                    ]
                ],
                "response": ["final response"],
            }
        )
        pd.testing.assert_frame_equal(result_df, expected_df)

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_error_response(self, mock_run_agent):
        mock_run_agent.return_value = [{"error": "agent run failed"}]
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            prompt_dataset=prompt_dataset,
        )

        assert "response" in result_df.columns
        response_content = result_df["response"][0]
        assert "Unexpected response type from agent run" in response_content
        assert not result_df["intermediate_events"][0]

    @mock.patch.object(_evals_common, "_run_agent")
    def test_run_agent_internal_malformed_event(self, mock_run_agent):
        mock_run_agent.return_value = [
            [
                {
                    "id": "1",
                    "content": {"parts1": [{"text123": "final response"}]},
                    "timestamp": 124,
                    "author": "model",
                },
            ]
        ]
        prompt_dataset = pd.DataFrame({"prompt": ["prompt1"]})
        mock_agent_engine = mock.Mock()
        mock_api_client = mock.Mock()
        result_df = _evals_common._run_agent_internal(
            api_client=mock_api_client,
            agent_engine=mock_agent_engine,
            prompt_dataset=prompt_dataset,
        )
        assert "response" in result_df.columns
        response_content = result_df["response"][0]
        assert "Failed to parse agent run response" in response_content
        assert not result_df["intermediate_events"][0]


class TestMetricPromptBuilder:
    """Unit tests for the MetricPromptBuilder class."""

    def test_metric_prompt_builder_minimal_fields(self):
        criteria = {"criterion1": "definition1"}
        rating_scores = {"score1": "description1"}
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            metric_definition=None,
            few_shot_examples=None,
        )
        assert builder.criteria == criteria
        assert builder.rating_scores == rating_scores
        expected_instruction = (
            "You are an expert evaluator. Your task is to evaluate the quality"
            " of the responses generated by AI models. We will provide you with"
            " the user prompt and an AI-generated responses.\nYou should first"
            " read the user input carefully for analyzing the task, and then"
            " evaluate the quality of the responses based on the Criteria"
            " provided in the Evaluation section below.\nYou will assign the"
            " response a rating following the Rating Scores and Evaluation"
            " Steps. Give step by step explanations for your rating, and only"
            " choose ratings from the Rating Scores."
        )
        expected_evaluation_steps = {
            "Step 1": (
                "Assess the response in aspects of all criteria provided. Provide"
                " assessment according to each criterion."
            ),
            "Step 2": (
                "Score based on the Rating Scores. Give a brief rationale to"
                " explain your evaluation considering each individual criterion."
            ),
        }
        assert builder.instruction == expected_instruction
        assert builder.evaluation_steps == expected_evaluation_steps
        assert "{response}" in builder.text

    def test_metric_prompt_builder_all_fields(self):
        criteria = {"criterion1": "definition1"}
        rating_scores = {"score1": "description1"}
        instruction = "Custom instruction."
        metric_definition = "Custom metric definition."
        evaluation_steps = {"step1": "custom step 1"}
        few_shot_examples = ["example1", "example2"]
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            instruction=instruction,
            metric_definition=metric_definition,
            evaluation_steps=evaluation_steps,
            few_shot_examples=few_shot_examples,
        )
        assert builder.criteria == criteria
        assert builder.rating_scores == rating_scores
        assert builder.instruction == instruction
        assert builder.metric_definition == metric_definition
        assert builder.evaluation_steps == evaluation_steps
        assert builder.few_shot_examples == few_shot_examples
        assert instruction in builder.text
        assert metric_definition in builder.text
        assert "custom step 1" in builder.text
        assert "example1" in builder.text

    def test_metric_prompt_builder_default_instruction_and_steps_in_text(self):
        criteria = {"c1": "v1"}
        rating_scores = {"s1": "d1"}
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            metric_definition=None,
            few_shot_examples=None,
        )
        expected_instruction = (
            "You are an expert evaluator. Your task is to evaluate the quality"
            " of the responses generated by AI models. We will provide you with"
            " the user prompt and an AI-generated responses.\nYou should first"
            " read the user input carefully for analyzing the task, and then"
            " evaluate the quality of the responses based on the Criteria"
            " provided in the Evaluation section below.\nYou will assign the"
            " response a rating following the Rating Scores and Evaluation"
            " Steps. Give step by step explanations for your rating, and only"
            " choose ratings from the Rating Scores."
        )
        expected_evaluation_steps = {
            "Step 1": (
                "Assess the response in aspects of all criteria provided. Provide"
                " assessment according to each criterion."
            ),
            "Step 2": (
                "Score based on the Rating Scores. Give a brief rationale to"
                " explain your evaluation considering each individual criterion."
            ),
        }
        assert expected_instruction in builder.text
        for step_desc in expected_evaluation_steps.values():
            assert step_desc in builder.text

    def test_metric_prompt_builder_custom_instruction_and_steps_in_text(self):
        criteria = {"c1": "v1"}
        rating_scores = {"s1": "d1"}
        custom_instruction = "My custom instructions."
        custom_steps = {"Step 1": "Do this first.", "Step 2": "Then do that."}
        builder = vertexai_genai_types.MetricPromptBuilder(
            criteria=criteria,
            rating_scores=rating_scores,
            instruction=custom_instruction,
            evaluation_steps=custom_steps,
            metric_definition=None,
            few_shot_examples=None,
        )
        assert custom_instruction in builder.text
        for step_desc in custom_steps.values():
            assert step_desc in builder.text

    def test_metric_prompt_builder_missing_criteria_raises_error(self):
        with pytest.raises(
            ValueError,
            match="Both 'criteria' and 'rating_scores' are required",
        ):
            vertexai_genai_types.MetricPromptBuilder(
                rating_scores={"score1": "description1"},
                criteria=None,
                metric_definition=None,
                few_shot_examples=None,
            )

    def test_metric_prompt_builder_missing_rating_scores_raises_error(self):
        with pytest.raises(
            ValueError,
            match="Both 'criteria' and 'rating_scores' are required",
        ):
            vertexai_genai_types.MetricPromptBuilder(
                criteria={"criterion1": "definition1"},
                rating_scores=None,
                metric_definition=None,
                few_shot_examples=None,
            )


class TestPromptTemplate:
    """Unit tests for the PromptTemplate class."""

    def test_prompt_template_variables(self):
        template = vertexai_genai_types.PromptTemplate(
            text="Hello {name}, welcome to {place}!"
        )
        assert template.variables == {"name", "place"}

    def test_prompt_template_assemble_simple(self):
        template = vertexai_genai_types.PromptTemplate(text="Hello {name}.")
        assert template.assemble(name="World") == "Hello World."

    def test_prompt_template_assemble_missing_variable_raises_error(self):
        template = vertexai_genai_types.PromptTemplate(text="Hello {name}.")
        with pytest.raises(
            ValueError, match="Missing value for template variable 'name'"
        ):
            template.assemble()

    def test_prompt_template_assemble_extra_variable_raises_error(self):
        template = vertexai_genai_types.PromptTemplate(text="Hello {name}.")
        with pytest.raises(
            ValueError, match="Invalid variable name 'extra_var' provided"
        ):
            template.assemble(name="Test", extra_var="unused")

    def test_prompt_template_text_must_not_be_empty(self):
        with pytest.raises(ValueError, match="Prompt template text cannot be empty"):
            vertexai_genai_types.PromptTemplate(text=" ")

    def test_prompt_template_assemble_all_text_single_part_returns_string(self):
        template = vertexai_genai_types.PromptTemplate(text="{greeting}, {name}.")
        result = template.assemble(greeting="Hi", name="There")
        assert result == "Hi, There."

    def test_prompt_template_str_representation(self):
        template_text = "This is a template: {var}"
        template = vertexai_genai_types.PromptTemplate(text=template_text)
        assert str(template) == template_text

    def test_prompt_template_repr_representation(self):
        template_text = "Test {repr}"
        template = vertexai_genai_types.PromptTemplate(text=template_text)
        assert repr(template) == f"PromptTemplate(text='{template_text}')"

    def test_prompt_template_assemble_multimodal_output(self):
        template = vertexai_genai_types.PromptTemplate(
            text="Context: {image_data} Question: {query}"
        )
        image_content_json = genai_types.Content(
            parts=[
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="image/png", file_uri="gs://fake-bucket/image.png"
                    )
                ),
            ]
        ).model_dump_json(exclude_none=True)

        result = template.assemble(image_data=image_content_json, query="What is this?")
        expected_parts = [
            genai_types.Part(text="Context: "),
            genai_types.Part(
                file_data=genai_types.FileData(
                    mime_type="image/png", file_uri="gs://fake-bucket/image.png"
                )
            ),
            genai_types.Part(text=" Question: What is this?"),
        ]
        expected_content_json = genai_types.Content(
            parts=expected_parts
        ).model_dump_json(exclude_none=True)

        assert json.loads(result) == json.loads(expected_content_json)

    def test_prompt_template_assemble_multimodal_variable_integration(self):
        template_str = "Observe: {media_part} and then answer: {txt_part}"
        template = vertexai_genai_types.PromptTemplate(text=template_str)

        media_var_value = genai_types.Content(
            parts=[
                genai_types.Part(
                    file_data=genai_types.FileData(
                        mime_type="video/mp4", file_uri="gs://fake-bucket/video.mp4"
                    )
                )
            ]
        ).model_dump_json(exclude_none=True)

        txt_var_value = "This is a simple text."

        assembled_prompt_json = template.assemble(
            media_part=media_var_value, txt_part=txt_var_value
        )

        assembled_content = genai_types.Content.model_validate_json(
            assembled_prompt_json
        )

        assert len(assembled_content.parts) == 3
        assert assembled_content.parts[0].text == "Observe: "
        assert assembled_content.parts[1].file_data.mime_type == "video/mp4"
        assert (
            assembled_content.parts[1].file_data.file_uri
            == "gs://fake-bucket/video.mp4"
        )
        assert (
            assembled_content.parts[2].text
            == " and then answer: This is a simple text."
        )


class TestGeminiEvalDataConverter:
    """Unit tests for the _GeminiEvalDataConverter class."""

    def setup_method(self):
        self.converter = _evals_data_converters._GeminiEvalDataConverter()

    def test_convert_simple_prompt_response(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {"role": "model", "parts": [{"text": "Hi"}]},
                            "finish_reason": "STOP",
                        }
                    ],
                    "usage_metadata": {
                        "prompt_token_count": 1,
                        "candidates_token_count": 1,
                        "total_token_count": 2,
                    },
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")], role="model"
        )
        assert eval_case.reference.response is None
        assert eval_case.system_instruction.parts is None
        assert eval_case.conversation_history == []

    def test_convert_with_system_instruction(self):
        raw_data = [
            {
                "request": {
                    "system_instruction": {
                        "role": "system",
                        "parts": [{"text": "Be nice."}],
                    },
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}],
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Hi there!"}],
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be nice.")], role="system"
        )
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )

    def test_convert_with_conversation_history_and_reference(self):
        raw_data_for_reference = [
            {
                "request": {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": "Initial user"}],
                        },
                        {
                            "role": "model",
                            "parts": [{"text": "Initial model"}],
                        },
                        {
                            "role": "user",
                            "parts": [{"text": "Actual prompt"}],
                        },
                        {
                            "role": "model",
                            "parts": [{"text": "This is reference"}],
                        },
                    ]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Actual response"}],
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data_for_reference)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Actual prompt")], role="user"
        )
        assert eval_case.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="This is reference")], role="model"
        )
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content == genai_types.Content(
            parts=[genai_types.Part(text="Initial user")], role="user"
        )
        assert eval_case.conversation_history[1].content == genai_types.Content(
            parts=[genai_types.Part(text="Initial model")], role="model"
        )
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Actual response")], role="model"
        )

    def test_convert_with_conversation_history_no_reference(self):
        raw_data = [
            {
                "request": {
                    "contents": [
                        {"role": "user", "parts": [{"text": "Old user msg"}]},
                        {"role": "model", "parts": [{"text": "Old model msg"}]},
                        {"role": "user", "parts": [{"text": "Current prompt"}]},
                    ]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "A response"}],
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")], role="user"
        )
        assert eval_case.reference.response is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_no_candidates_in_response(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": {
                    "candidates": [],
                    "prompt_feedback": {"block_reason": "SAFETY"},
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert len(eval_case.responses) == 1
        assert (
            eval_case.responses[0].response.parts[0].text
            == _evals_data_converters._PLACEHOLDER_RESPONSE_TEXT
        )

    def test_convert_invalid_content_structure_raises_value_error(self):
        raw_data = [
            {
                "request": {"contents": ["not a dict"]},
                "response": {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "Hi"}]}}
                    ]
                },
            }
        ]
        with pytest.raises(
            TypeError, match="Expected a dictionary for content at turn 0"
        ):
            self.converter.convert(raw_data)

        raw_data_missing_parts = [
            {
                "request": {"contents": [{"role": "user"}]},  # Missing 'parts'
                "response": {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "Hi"}]}}
                    ]
                },
            }
        ]
        with pytest.raises(
            ValueError, match="Missing 'parts' key in content structure at turn 0"
        ):
            self.converter.convert(raw_data_missing_parts)

    def test_convert_multiple_items(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Item 1"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Resp 1"}],
                            }
                        }
                    ]
                },
            },
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Item 2"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Resp 2"}],
                            }
                        }
                    ]
                },
            },
        ]
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 2
        assert result_dataset.eval_cases[0].prompt.parts[0].text == "Item 1"
        assert result_dataset.eval_cases[1].prompt.parts[0].text == "Item 2"

    def test_convert_with_raw_string_response(self):
        """Tests conversion when the response is a raw string."""
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": "Hi from a raw string",
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi from a raw string")],
        )


class TestFlattenEvalDataConverter:
    """Unit tests for the _FlattenEvalDataConverter class."""

    def setup_method(self):
        self.converter = _evals_data_converters._FlattenEvalDataConverter()

    def test_convert_simple_prompt_response(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")]
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")]
        )
        assert eval_case.reference is None
        assert eval_case.system_instruction is None
        assert eval_case.conversation_history is None

    def test_convert_with_system_instruction_and_reference(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi there!"],
                "instruction": ["Be nice."],
                "reference": ["Hey"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be nice.")]
        )
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")]
        )
        assert eval_case.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Hey")]
        )

    def test_convert_with_conversation_history(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Current prompt"],
                "response": ["A response"],
                "history": [
                    [
                        {"role": "user", "parts": [{"text": "Old user msg"}]},
                        {"role": "model", "parts": [{"text": "Old model msg"}]},
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")]
        )
        assert eval_case.reference is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_missing_response_raises_value_error(self):
        raw_data_df = pd.DataFrame({"prompt": ["Hello"]})  # Missing response
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(
            ValueError, match="Response is required but missing for eval_case_0"
        ):
            self.converter.convert(raw_data)

    def test_convert_missing_prompt_raises_value_error(self):
        raw_data_df = pd.DataFrame({"response": ["Hi"]})  # Missing prompt
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(
            ValueError, match="Prompt is required but missing for eval_case_0"
        ):
            self.converter.convert(raw_data)

    def test_convert_invalid_prompt_type_raises_value_error(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": [123],  # Invalid prompt type
                "response": ["Hi"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(ValueError, match="Invalid prompt type for case 0"):
            self.converter.convert(raw_data)

    def test_convert_invalid_response_type_raises_value_error(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": [123],  # Invalid response type
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        with pytest.raises(ValueError, match="Invalid response type for case 0"):
            self.converter.convert(raw_data)

    def test_convert_multiple_items(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Item 1", "Item 2"],
                "response": ["Resp 1", "Resp 2"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 2
        assert result_dataset.eval_cases[0].prompt.parts[0].text == "Item 1"
        assert result_dataset.eval_cases[1].prompt.parts[0].text == "Item 2"

    def test_convert_with_additional_columns(self):
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
                "custom_column": ["custom_value"],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.custom_column == "custom_value"

    def test_convert_with_agent_eval_fields(self):
        """Tests that agent eval data is converted correctly from a flattened format."""
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
                "intermediate_events": [
                    [
                        {
                            "event_id": "event1",
                            "content": {"parts": [{"text": "intermediate event"}]},
                        }
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.intermediate_events[0].event_id == "event1"

    def test_convert_with_intermediate_events_as_event_objects(self):
        """Tests that agent eval data is converted correctly when intermediate_events are Event objects."""
        raw_data_df = pd.DataFrame(
            {
                "prompt": ["Hello"],
                "response": ["Hi"],
                "intermediate_events": [
                    [
                        vertexai_genai_types.evals.Event(
                            event_id="event1",
                            content=genai_types.Content(
                                parts=[genai_types.Part(text="intermediate event")]
                            ),
                        )
                    ]
                ],
            }
        )
        raw_data = raw_data_df.to_dict(orient="records")
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.intermediate_events[0].event_id == "event1"
        assert (
            eval_case.intermediate_events[0].content.parts[0].text
            == "intermediate event"
        )


class TestOpenAIDataConverter:
    """Unit tests for the _OpenAIDataConverter class."""

    def setup_method(self):
        self.converter = _evals_data_converters._OpenAIDataConverter()

    def test_convert_simple_prompt_response(self):
        raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "Hello"}]},
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")]
        )
        assert eval_case.reference is None
        assert eval_case.system_instruction is None
        assert eval_case.conversation_history == []

    def test_convert_with_system_instruction(self):
        raw_data = [
            {
                "request": {
                    "messages": [
                        {"role": "system", "content": "Be helpful."},
                        {"role": "user", "content": "Hello"},
                    ]
                },
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be helpful.")]
        )
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )

    def test_convert_with_conversation_history_and_reference(self):
        raw_data = [
            {
                "request": {
                    "messages": [
                        {"role": "user", "content": "Initial user"},
                        {"role": "assistant", "content": "Initial model (ref)"},
                    ]
                },
                "response": {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Actual response",
                            }
                        }
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Initial user")], role="user"
        )
        assert eval_case.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Initial model (ref)")], role="assistant"
        )
        assert len(eval_case.conversation_history) == 0  # History before prompt and ref
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Actual response")]
        )

    def test_convert_with_conversation_history_no_reference(self):
        raw_data = [
            {
                "request": {
                    "messages": [
                        {"role": "user", "content": "Old user msg"},
                        {"role": "assistant", "content": "Old model msg"},
                        {"role": "user", "content": "Current prompt"},
                    ]
                },
                "response": {
                    "choices": [
                        {"message": {"role": "assistant", "content": "A response"}}
                    ]
                },
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Current prompt")], role="user"
        )
        assert eval_case.reference is None
        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0].content.parts[0].text == "Old user msg"
        assert (
            eval_case.conversation_history[1].content.parts[0].text == "Old model msg"
        )

    def test_convert_empty_choices_uses_placeholder(self):
        raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "Hello"}]},
                "response": {"choices": []},
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert len(eval_case.responses) == 1
        assert (
            eval_case.responses[0].response.parts[0].text
            == _evals_data_converters._PLACEHOLDER_RESPONSE_TEXT
        )

    def test_convert_skips_missing_request_or_response(self):
        raw_data = [{"response": {"choices": []}}, {"request": {"messages": []}}]
        result_dataset = self.converter.convert(raw_data)
        assert len(result_dataset.eval_cases) == 0


class TestObservabilityDataConverter:
    """Unit tests for the ObservabilityDataConverter class."""

    def setup_method(self):
        self.converter = _observability_data_converter.ObservabilityDataConverter()

    def test_convert_simple_request_response(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)

        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 1

        eval_case = result_dataset.eval_cases[0]
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")], role="system"
        )
        assert eval_case.reference is None
        assert eval_case.system_instruction is None
        assert not eval_case.conversation_history

    def test_convert_with_system_instruction(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
                "system_instruction": json.dumps(
                    {
                        "role": "user",
                        "parts": [{"content": "Be helpful", "type": "text"}],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]
        assert eval_case.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Be helpful")], role="user"
        )

    def test_convert_with_conversation_history(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                )
                + "\n"
                + json.dumps(
                    {"role": "system", "parts": [{"content": "Hi", "type": "text"}]}
                )
                + "\n"
                + json.dumps(
                    {
                        "role": "user",
                        "parts": [
                            {"content": "What's the meaning of life?", "type": "text"}
                        ],
                    }
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "42.", "type": "text"}],
                    }
                ),
            }
        ]

        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="What's the meaning of life?")], role="user"
        )

        assert len(eval_case.conversation_history) == 2
        assert eval_case.conversation_history[0] == vertexai_genai_types.evals.Message(
            content=genai_types.Content(
                parts=[genai_types.Part(text="Hello")], role="user"
            ),
            turn_id="0",
            author="user",
        )
        assert eval_case.conversation_history[1] == vertexai_genai_types.evals.Message(
            content=genai_types.Content(
                parts=[genai_types.Part(text="Hi")], role="system"
            ),
            turn_id="1",
            author="system",
        )

    def test_convert_multiple_request_response(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            },
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Goodbye", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Bye", "type": "text"}],
                    }
                ),
            },
        ]
        result_dataset = self.converter.convert(raw_data)

        assert isinstance(result_dataset, vertexai_genai_types.EvaluationDataset)
        assert len(result_dataset.eval_cases) == 2

        eval_case = result_dataset.eval_cases[0]
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Hi")], role="system"
        )

        eval_case = result_dataset.eval_cases[1]
        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Goodbye")], role="user"
        )
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Bye")], role="system"
        )

    def test_convert_skips_unknown_part_type(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {
                        "role": "user",
                        "parts": [
                            {"content": 123, "type": ""},
                            {"content": 456},
                            {"content": "Hello", "type": "text"},
                        ],
                    }
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]

        result_dataset = self.converter.convert(raw_data)
        eval_case = result_dataset.eval_cases[0]

        assert eval_case.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Hello")], role="user"
        )

    def test_convert_skips_missing_request(self):
        raw_data = [
            {
                "format": "observability",
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert not result_dataset.eval_cases

    def test_convert_skips_missing_response(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)
        assert not result_dataset.eval_cases

    def test_convert_tool_call_parts(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "type": "tool_call",
                                "id": "tool_id",
                                "name": "tool_name",
                                "arguments": {"param": "1"},
                            }
                        ],
                    }
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [
                            {
                                "type": "tool_call_response",
                                "id": "tool_id",
                                "result": {"field": "2"},
                            }
                        ],
                    }
                ),
            }
        ]
        result_dataset = self.converter.convert(raw_data)

        eval_case = result_dataset.eval_cases[0]
        assert eval_case.prompt == genai_types.Content(
            parts=[
                genai_types.Part(
                    function_call=genai_types.FunctionCall(
                        id="tool_id", name="tool_id", args={"param": "1"}
                    )
                )
            ],
            role="user",
        )
        assert len(eval_case.responses) == 1
        assert eval_case.responses[0].response == genai_types.Content(
            parts=[
                genai_types.Part(
                    function_response=genai_types.FunctionResponse(
                        id="tool_id", name="tool_id", response={"field": "2"}
                    )
                )
            ],
            role="system",
        )


class TestAgentInfo:
    """Unit tests for the AgentInfo class."""

    def test_agent_info_creation(self):
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
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent1",
            instruction="instruction1",
            description="description1",
            tool_declarations=[tool],
        )
        assert agent_info.name == "agent1"
        assert agent_info.instruction == "instruction1"
        assert agent_info.description == "description1"
        assert agent_info.tool_declarations == [tool]

    @mock.patch.object(genai_types.FunctionDeclaration, "from_callable_with_api_option")
    def test_load_from_agent(self, mock_from_callable):
        def my_search_tool(query: str) -> str:
            """Searches for information."""
            return f"search result for {query}"

        mock_function_declaration = mock.Mock(spec=genai_types.FunctionDeclaration)
        mock_from_callable.return_value = mock_function_declaration

        mock_agent = mock.Mock()
        mock_agent.name = "mock_agent"
        mock_agent.instruction = "mock instruction"
        mock_agent.description = "mock description"
        mock_agent.tools = [my_search_tool]

        agent_info = vertexai_genai_types.evals.AgentInfo.load_from_agent(
            agent=mock_agent,
            agent_resource_name="projects/123/locations/abc/reasoningEngines/456",
        )

        assert agent_info.name == "mock_agent"
        assert agent_info.instruction == "mock instruction"
        assert agent_info.description == "mock description"
        assert (
            agent_info.agent_resource_name
            == "projects/123/locations/abc/reasoningEngines/456"
        )
        assert len(agent_info.tool_declarations) == 1
        assert isinstance(agent_info.tool_declarations[0], genai_types.Tool)
        assert agent_info.tool_declarations[0].function_declarations == [
            mock_function_declaration
        ]
        mock_from_callable.assert_called_once_with(callable=my_search_tool)


class TestEvent:
    """Unit tests for the Event class."""

    def test_event_creation(self):
        event = vertexai_genai_types.evals.Event(
            event_id="event1",
            content=genai_types.Content(
                parts=[genai_types.Part(text="intermediate event")]
            ),
            author="user",
        )
        assert event.event_id == "event1"
        assert event.content.parts[0].text == "intermediate event"
        assert event.author == "user"


class TestEvalCase:
    """Unit tests for the EvalCase class."""

    def test_eval_case_with_agent_eval_fields(self):
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
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent1",
            instruction="instruction1",
            tool_declarations=[tool],
        )
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
            intermediate_events=intermediate_events,
        )

        assert eval_case.agent_info == agent_info
        assert eval_case.intermediate_events == intermediate_events


class TestSessionInput:
    """Unit tests for the SessionInput class."""

    def test_session_input_creation(self):
        session_input = vertexai_genai_types.evals.SessionInput(
            user_id="user1",
            state={"key": "value"},
        )
        assert session_input.user_id == "user1"
        assert session_input.state == {"key": "value"}


class TestMetric:
    """Unit tests for the Metric class."""

    def test_metric_creation_success(self):
        metric = vertexai_genai_types.Metric(name="TestMetric")
        assert metric.name == "testmetric"
        assert metric.custom_function is None

    def test_metric_creation_with_custom_function(self):
        def my_custom_function(data: dict):
            return 1.0

        metric = vertexai_genai_types.Metric(
            name="custom_metric", custom_function=my_custom_function
        )
        assert metric.name == "custom_metric"
        assert metric.custom_function == my_custom_function

    def test_metric_name_validation_empty_raises_error(self):
        with pytest.raises(ValueError, match="Metric name cannot be empty."):
            vertexai_genai_types.Metric(name="")
        with pytest.raises(ValueError, match="Metric name cannot be empty."):
            vertexai_genai_types.Metric(name=None)

    def test_llm_metric_prompt_template_validation_empty_raises_error(self):
        with pytest.raises(ValueError, match="Prompt template cannot be empty."):
            vertexai_genai_types.LLMMetric(name="test_metric", prompt_template=None)
        with pytest.raises(
            ValueError, match="Prompt template cannot be an empty string."
        ):
            vertexai_genai_types.LLMMetric(name="test_metric", prompt_template="")
        with pytest.raises(
            ValueError, match="Prompt template cannot be an empty string."
        ):
            vertexai_genai_types.LLMMetric(name="test_metric", prompt_template="  ")

    def test_llm_metric_sampling_count_validation_raise_errors(self):
        with pytest.raises(
            ValueError, match="judge_model_sampling_count must be between 1 and 32."
        ):
            vertexai_genai_types.LLMMetric(
                name="test_metric",
                prompt_template="test_prompt_template",
                judge_model_sampling_count=0,
            )
        with pytest.raises(
            ValueError, match="judge_model_sampling_count must be between 1 and 32."
        ):
            vertexai_genai_types.LLMMetric(
                name="test_metric",
                prompt_template="test_prompt_template",
                judge_model_sampling_count=-1,
            )
        with pytest.raises(
            ValueError, match="judge_model_sampling_count must be between 1 and 32."
        ):
            vertexai_genai_types.LLMMetric(
                name="test_metric",
                prompt_template="test_prompt_template",
                judge_model_sampling_count=100,
            )

    def test_metric_name_validation_lowercase(self):
        metric = vertexai_genai_types.Metric(name="UPPERCASEMetric")
        assert metric.name == "uppercasemetric"

    @mock.patch("vertexai._genai.types.common.yaml.dump")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_metric_to_yaml_file_with_version_and_set_fields(
        self, mock_open_file, mock_yaml_dump
    ):
        metric_obj = vertexai_genai_types.Metric(
            name="MyMetricToDump",
            prompt_template="Evaluate: {input}",
            judge_model="gemini-1.5-pro",
            judge_model_sampling_count=5,
            return_raw_output=False,
            custom_function=lambda x: x,
            judge_model_system_instruction=None,
        )
        test_file_path = "/fake/path/metric_output.yaml"
        test_version = "v1.0.1"

        metric_obj.to_yaml_file(test_file_path, version=test_version)

        mock_open_file.assert_called_once_with(test_file_path, "w", encoding="utf-8")

        expected_data_to_dump = {
            "name": "mymetrictodump",
            "prompt_template": "Evaluate: {input}",
            "judge_model": "gemini-1.5-pro",
            "judge_model_sampling_count": 5,
            "return_raw_output": False,
            "version": test_version,
        }

        mock_yaml_dump.assert_called_once_with(
            expected_data_to_dump,
            mock_open_file(),
            sort_keys=False,
            allow_unicode=True,
        )

    @mock.patch("vertexai._genai.types.common.yaml.dump")
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    def test_metric_to_yaml_file_without_version_minimal_fields(
        self, mock_open_file, mock_yaml_dump
    ):
        metric_obj = vertexai_genai_types.Metric(name="MinimalMetric")
        test_file_path = "/fake/path/minimal_metric.yaml"

        metric_obj.to_yaml_file(test_file_path)

        mock_open_file.assert_called_once_with(test_file_path, "w", encoding="utf-8")
        expected_data_to_dump = {
            "name": "minimalmetric",
        }
        mock_yaml_dump.assert_called_once_with(
            expected_data_to_dump,
            mock_open_file(),
            sort_keys=False,
            allow_unicode=True,
        )

    @mock.patch("vertexai._genai.types.common.yaml", None)
    def test_metric_to_yaml_file_raises_importerror_if_yaml_is_none(self):
        metric_obj = vertexai_genai_types.Metric(name="ErrorMetric")
        with pytest.raises(
            ImportError, match="YAML serialization requires the pyyaml library"
        ):
            metric_obj.to_yaml_file("/fake/path/error.yaml")


class TestMergeResponseDatasets:
    """Unit tests for the merge_response_datasets_into_canonical_format function."""

    def test_merge_two_flatten_datasets(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {"prompt": "Prompt 1", "response": "Response 1b"},
            {"prompt": "Prompt 2", "response": "Response 2b"},
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 1")]
        )
        assert len(merged_dataset.eval_cases[0].responses) == 2
        assert merged_dataset.eval_cases[0].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1a")])
        assert merged_dataset.eval_cases[0].responses[
            1
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1b")])
        assert merged_dataset.eval_cases[1].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 2")]
        )
        assert len(merged_dataset.eval_cases[1].responses) == 2
        assert merged_dataset.eval_cases[1].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 2a")])
        assert merged_dataset.eval_cases[1].responses[
            1
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 2b")])

    def test_merge_flatten_and_openai_datasets(self):
        raw_dataset_flatten = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1 Flatten",
                "reference": "Ref 1",
            },
        ]
        raw_dataset_openai = [
            {
                "request": {
                    "messages": [
                        {"role": "user", "content": "Prompt 1"},
                        {"role": "assistant", "content": "Ref 1"},
                    ]
                },
                "response": {
                    "choices": [
                        {
                            "message": {
                                "role": "assistant",
                                "content": "Response 1 OpenAI",
                            }
                        }
                    ]
                },
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.OPENAI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_flatten, raw_dataset_openai], schemas=schemas
            )
        )
        assert len(merged_dataset.eval_cases) == 1
        case0 = merged_dataset.eval_cases[0]
        assert case0.prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 1")]
        )
        assert case0.reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Ref 1")]
        )
        assert len(case0.responses) == 2
        assert case0.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1 Flatten")]
        )
        assert case0.responses[1].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1 OpenAI")]
        )

    def test_merge_two_openai_datasets(self):
        raw_dataset_openai_1 = [
            {
                "request": {
                    "messages": [
                        {"role": "developer", "content": "Sys1"},
                        {"role": "user", "content": "P1"},
                    ]
                },
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "R1a"}}]
                },
            }
        ]
        raw_dataset_openai_2 = [
            {
                "request": {
                    "messages": [
                        {"role": "system", "content": "Sys1"},
                        {"role": "user", "content": "P1"},
                    ]
                },
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "R1b"}}]
                },
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.OPENAI,
            _evals_data_converters.EvalDatasetSchema.OPENAI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_openai_1, raw_dataset_openai_2], schemas=schemas
            )
        )
        assert len(merged_dataset.eval_cases) == 1
        case0 = merged_dataset.eval_cases[0]
        assert case0.prompt == genai_types.Content(
            parts=[genai_types.Part(text="P1")], role="user"
        )
        assert case0.system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Sys1")]
        )
        assert len(case0.responses) == 2
        assert case0.responses[0].response == genai_types.Content(
            parts=[genai_types.Part(text="R1a")]
        )
        assert case0.responses[1].response == genai_types.Content(
            parts=[genai_types.Part(text="R1b")]
        )

    def test_merge_flatten_and_gemini_datasets(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Prompt 1"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 1b"}],
                            }
                        }
                    ]
                },
            },
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Prompt 2"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 2b"}],
                            }
                        }
                    ]
                },
            },
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.GEMINI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 1")]
        )
        assert len(merged_dataset.eval_cases[0].responses) == 2
        assert merged_dataset.eval_cases[0].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1a")])
        assert merged_dataset.eval_cases[0].responses[
            1
        ].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1b")], role="model"
        )
        assert merged_dataset.eval_cases[1].prompt == genai_types.Content(
            parts=[genai_types.Part(text="Prompt 2")]
        )
        assert len(merged_dataset.eval_cases[1].responses) == 2
        assert merged_dataset.eval_cases[1].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 2a")])
        assert merged_dataset.eval_cases[1].responses[
            1
        ].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 2b")], role="model"
        )

    def test_merge_empty_input_list(self):
        with pytest.raises(
            ValueError,
            match="Input 'raw_datasets' cannot be empty and must be a list of lists.",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[], schemas=[]
            )

    def test_merge_mismatched_number_of_eval_cases(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {"prompt": "Prompt 1", "response": "Response 1b"},
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        with pytest.raises(
            ValueError,
            match="All datasets must have the same number of evaluation cases",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )

    def test_merge_mismatched_schemas_list_length(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        raw_dataset_2 = [
            {"prompt": "Prompt 1", "response": "Response 1b"},
            {"prompt": "Prompt 2", "response": "Response 2b"},
        ]
        raw_dataset_3 = [
            {"prompt": "Prompt 1", "response": "Response 1c"},
            {"prompt": "Prompt 2", "response": "Response 2c"},
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.GEMINI,
        ]
        with pytest.raises(
            ValueError,
            match=(
                "A list of schemas must be provided, one for each raw dataset. Got 2"
                " schemas for 3 datasets."
            ),
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2, raw_dataset_3],
                schemas=schemas,
            )

    def test_merge_empty_schemas_list(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
            {"prompt": "Prompt 2", "response": "Response 2a"},
        ]
        with pytest.raises(
            ValueError,
            match=(
                "A list of schemas must be provided, one for each raw dataset. Got 0"
                " schemas for 1 datasets."
            ),
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1], schemas=[]
            )

    def test_merge_with_custom_columns(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "custom_col_1": "value_1_1",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2a",
                "custom_col_1": "value_2_1",
            },
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "custom_col_2": "value_1_2",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2b",
                "custom_col_2": "value_2_2",
            },
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].custom_col_1 == "value_1_1"
        assert merged_dataset.eval_cases[0].custom_col_2 == "value_1_2"
        assert merged_dataset.eval_cases[1].custom_col_1 == "value_2_1"
        assert merged_dataset.eval_cases[1].custom_col_2 == "value_2_2"

    def test_merge_with_different_custom_columns(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "custom_col_1": "value_1_1",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2a",
                "custom_col_1": "value_2_1",
            },
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "custom_col_2": "value_1_2",
                "custom_col_3": "value_1_3",
            },
            {
                "prompt": "Prompt 2",
                "response": "Response 2b",
                "custom_col_2": "value_2_2",
                "custom_col_3": "value_2_3",
            },
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 2
        assert merged_dataset.eval_cases[0].custom_col_1 == "value_1_1"
        assert merged_dataset.eval_cases[0].custom_col_2 == "value_1_2"
        assert merged_dataset.eval_cases[0].custom_col_3 == "value_1_3"
        assert merged_dataset.eval_cases[1].custom_col_1 == "value_2_1"
        assert merged_dataset.eval_cases[1].custom_col_2 == "value_2_2"
        assert merged_dataset.eval_cases[1].custom_col_3 == "value_2_3"

    def test_merge_with_intermediate_events(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "intermediate_events": [
                    {
                        "event_id": "event1",
                        "content": {"parts": [{"text": "intermediate event"}]},
                    }
                ],
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "intermediate_events": [
                    {
                        "event_id": "event2",
                        "content": {"parts": [{"text": "intermediate event 2"}]},
                    }
                ],
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].intermediate_events) == 1
        assert merged_dataset.eval_cases[0].intermediate_events[0].event_id == "event1"

    def test_merge_with_metadata(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "metadata": {"model": "model_1"},
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1

    def test_merge_with_different_number_of_responses(self):
        raw_dataset_1 = [{"prompt": "Prompt 1", "response": "Response 1a"}]
        raw_dataset_2 = [
            {
                # Gemini schema
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Prompt 1"}]}]
                },
                "response": {
                    "candidates": [
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 1b"}],
                            }
                        },
                        {
                            "content": {
                                "role": "model",
                                "parts": [{"text": "Response 1c"}],
                            }
                        },
                    ]
                },
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.GEMINI,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].responses) == 2
        assert merged_dataset.eval_cases[0].responses[
            0
        ].response == genai_types.Content(parts=[genai_types.Part(text="Response 1a")])
        assert merged_dataset.eval_cases[0].responses[
            1
        ].response == genai_types.Content(
            parts=[genai_types.Part(text="Response 1b")], role="model"
        )

    def test_merge_with_conversation_history(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "history": [
                    {"role": "user", "parts": [{"text": "Old user msg 1"}]},
                    {"role": "model", "parts": [{"text": "Old model msg 1"}]},
                ],
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "history": [
                    {"role": "user", "parts": [{"text": "Old user msg 2"}]},
                    {"role": "model", "parts": [{"text": "Old model msg 2"}]},
                ],
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].conversation_history) == 2
        assert (
            merged_dataset.eval_cases[0].conversation_history[0].content.parts[0].text
            == "Old user msg 1"
        )
        assert (
            merged_dataset.eval_cases[0].conversation_history[1].content.parts[0].text
            == "Old model msg 1"
        )

    def test_merge_with_empty_conversation_history(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "history": [],
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "history": [],
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert len(merged_dataset.eval_cases[0].conversation_history) == 0

    def test_merge_with_reference(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "reference": "Reference 1",
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "reference": "Reference 2",
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert merged_dataset.eval_cases[0].reference.response == genai_types.Content(
            parts=[genai_types.Part(text="Reference 1")]
        )

    def test_merge_with_system_instruction(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1a",
                "instruction": "Instruction 1",
            }
        ]
        raw_dataset_2 = [
            {
                "prompt": "Prompt 1",
                "response": "Response 1b",
                "instruction": "Instruction 2",
            }
        ]
        schemas = [
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
            _evals_data_converters.EvalDatasetSchema.FLATTEN,
        ]

        merged_dataset = (
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                [raw_dataset_1, raw_dataset_2], schemas=schemas
            )
        )

        assert len(merged_dataset.eval_cases) == 1
        assert merged_dataset.eval_cases[0].system_instruction == genai_types.Content(
            parts=[genai_types.Part(text="Instruction 1")]
        )

    def test_merge_with_invalid_schema_type(self):
        raw_dataset_1 = [
            {"prompt": "Prompt 1", "response": "Response 1a"},
        ]
        with pytest.raises(
            ValueError,
            match="Unsupported dataset schema: invalid_schema",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1], schemas=["invalid_schema"]
            )

    def test_merge_with_invalid_raw_dataset_type(self):
        with pytest.raises(
            TypeError,
            match="Input 'raw_datasets' must be a list",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets="invalid_dataset",
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )
        with pytest.raises(
            ValueError,
            match=("Input 'raw_datasets' cannot be empty and must be a list of lists"),
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=["invalid_dataset"],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_invalid_eval_case_type(self):
        raw_dataset_1 = [
            "invalid_eval_case",
        ]
        with pytest.raises(
            TypeError,
            match="Expected a dictionary for item at index 0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestPredefinedMetricHandler:
    """Unit tests for the PredefinedMetricHandler class."""

    def test_eval_case_to_agent_data(self):
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
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent1",
            instruction="instruction1",
            tool_declarations=[tool],
        )
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
            intermediate_events=intermediate_events,
        )

        agent_data = (
            _evals_metric_handlers.PredefinedMetricHandler._eval_case_to_agent_data(
                eval_case
            )
        )

        assert agent_data.agent_config.developer_instruction.text == "instruction1"
        assert agent_data.agent_config.tools.tool == [tool]
        assert agent_data.events.event[0].parts[0].text == "intermediate event"

    def test_eval_case_to_agent_data_events_only(self):
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=None,
            intermediate_events=intermediate_events,
        )

        agent_data = (
            _evals_metric_handlers.PredefinedMetricHandler._eval_case_to_agent_data(
                eval_case
            )
        )

        assert agent_data.agent_config is None
        assert agent_data.events.event[0].parts[0].text == "intermediate event"

    def test_eval_case_to_agent_data_empty_event_content(self):
        intermediate_events = [
            vertexai_genai_types.evals.Event(
                event_id="event1",
                content=None,
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=None,
            intermediate_events=intermediate_events,
        )

        agent_data = (
            _evals_metric_handlers.PredefinedMetricHandler._eval_case_to_agent_data(
                eval_case
            )
        )

        assert agent_data.agent_config is None
        assert not agent_data.events.event

    def test_eval_case_to_agent_data_empty_intermediate_events_list(self):
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent1",
            instruction="instruction1",
            tool_declarations=[],
        )

        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
        )

        agent_data = (
            _evals_metric_handlers.PredefinedMetricHandler._eval_case_to_agent_data(
                eval_case
            )
        )

        assert not agent_data.events.event

    def test_eval_case_to_agent_data_agent_info_empty_tools(self):
        agent_info = vertexai_genai_types.evals.AgentInfo(
            name="agent1",
            instruction="instruction1",
            tool_declarations=[],
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=agent_info,
            intermediate_events=None,
        )

        agent_data = (
            _evals_metric_handlers.PredefinedMetricHandler._eval_case_to_agent_data(
                eval_case
            )
        )

        assert agent_data.agent_config.developer_instruction.text == "instruction1"
        assert not agent_data.agent_config.tools.tool

    def test_eval_case_to_agent_data_agent_info_empty(self):
        intermediate_events = [
            vertexai_genai_types.Event(
                event_id="event1",
                content=genai_types.Content(
                    parts=[genai_types.Part(text="intermediate event")]
                ),
            )
        ]
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            agent_info=None,
            intermediate_events=intermediate_events,
        )

        agent_data = (
            _evals_metric_handlers.PredefinedMetricHandler._eval_case_to_agent_data(
                eval_case
            )
        )

        assert agent_data.agent_config is None

    @mock.patch.object(_evals_metric_handlers.logger, "warning")
    def test_tool_use_quality_metric_no_tool_call_logs_warning(
        self, mock_warning, mock_api_client_fixture
    ):
        """Tests that PredefinedMetricHandler warns for tool_use_quality_v1 if no tool call."""
        metric = vertexai_genai_types.Metric(name="tool_use_quality_v1")
        handler = _evals_metric_handlers.PredefinedMetricHandler(
            module=evals.Evals(api_client_=mock_api_client_fixture), metric=metric
        )
        eval_case = vertexai_genai_types.EvalCase(
            eval_case_id="case-no-tool-call",
            prompt=genai_types.Content(parts=[genai_types.Part(text="Hello")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="Hi")])
                )
            ],
            intermediate_events=[
                vertexai_genai_types.evals.Event(
                    event_id="event1",
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="intermediate event")]
                    ),
                )
            ],
        )
        handler._build_request_payload(eval_case, response_index=0)
        mock_warning.assert_called_once_with(
            "Metric 'tool_use_quality_v1' requires tool usage in "
            "'intermediate_events', but no tool usage was found for case %s.",
            "case-no-tool-call",
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestLLMMetricHandlerPayload:
    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_data_converters)
        importlib.reload(_evals_metric_handlers)

        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        self.mock_api_client = mock.Mock(spec=client.Client)
        self.mock_evals_module = evals.Evals(api_client_=self.mock_api_client)

    def test_build_request_payload_basic_filtering_and_fields(self):
        metric = vertexai_genai_types.LLMMetric(
            name="test_quality",
            prompt_template="Eval: {prompt} with {response}. Context: {custom_context}. Ref: {reference}",
        )
        handler = _evals_metric_handlers.LLMMetricHandler(
            module=self.mock_evals_module, metric=metric
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(
                parts=[genai_types.Part(text="User prompt text")]
            ),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(
                        parts=[genai_types.Part(text="Model response text")]
                    )
                )
            ],
            reference=vertexai_genai_types.ResponseCandidate(
                response=genai_types.Content(
                    parts=[genai_types.Part(text="Ground truth text")]
                )
            ),
            custom_context="Custom context value.",
            extra_field_not_in_template="This should be excluded.",
            eval_case_id="case-123",
        )

        payload = handler._build_request_payload(eval_case=eval_case, response_index=0)

        expected_content_map = {
            "prompt": _create_content_dump("User prompt text"),
            "response": _create_content_dump("Model response text"),
            "custom_context": _create_content_dump("Custom context value."),
            "reference": _create_content_dump("Ground truth text"),
        }
        actual_content_map_dict = payload["pointwise_metric_input"]["instance"][
            "content_map_instance"
        ]["values"]

        assert actual_content_map_dict == expected_content_map
        assert "extra_field_not_in_template" not in actual_content_map_dict
        assert "eval_case_id" not in actual_content_map_dict

    def test_build_request_payload_various_field_types(self):
        metric = vertexai_genai_types.LLMMetric(
            name="test_various_fields",
            prompt_template="{prompt}{response}{conversation_history}{system_instruction}{dict_field}{list_field}{int_field}{bool_field}",
        )
        handler = _evals_metric_handlers.LLMMetricHandler(
            module=self.mock_evals_module, metric=metric
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="The Prompt")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(
                        parts=[genai_types.Part(text="The Response")]
                    )
                )
            ],
            conversation_history=[
                vertexai_genai_types.evals.Message(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Turn 1 user")], role="user"
                    )
                ),
                vertexai_genai_types.evals.Message(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Turn 1 model")], role="model"
                    )
                ),
            ],
            system_instruction=genai_types.Content(
                parts=[genai_types.Part(text="System instructions here.")]
            ),
            dict_field={"key1": "val1", "key2": [1, 2]},
            list_field=["a", "b", {"c": 3}],
            int_field=42,
            bool_field=True,
        )

        payload = handler._build_request_payload(eval_case=eval_case, response_index=0)
        actual_content_map_dict = payload["pointwise_metric_input"]["instance"][
            "content_map_instance"
        ]["values"]

        expected_texts = {
            "prompt": "The Prompt",
            "response": "The Response",
            "conversation_history": "user: Turn 1 user\nmodel: Turn 1 model",
            "system_instruction": "System instructions here.",
            "dict_field": json.dumps({"key1": "val1", "key2": [1, 2]}),
            "list_field": json.dumps(["a", "b", {"c": 3}]),
            "int_field": "42",
            "bool_field": "True",
        }
        expected_content_map = {
            key: _create_content_dump(text) for key, text in expected_texts.items()
        }

        assert actual_content_map_dict == expected_content_map

    def test_build_request_payload_optional_metric_configs_set(self):
        metric = vertexai_genai_types.LLMMetric(
            name="test_optional_configs",
            prompt_template="{prompt}{response}",
            judge_model="gemini-1.5-pro",
            judge_model_sampling_count=5,
            judge_model_system_instruction="You are a fair judge.",
            return_raw_output=True,
        )
        handler = _evals_metric_handlers.LLMMetricHandler(
            module=self.mock_evals_module, metric=metric
        )
        eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(parts=[genai_types.Part(text="p")]),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(parts=[genai_types.Part(text="r")])
                )
            ],
        )

        payload = handler._build_request_payload(eval_case=eval_case, response_index=0)

        expected_content_map = {
            "prompt": _create_content_dump("p"),
            "response": _create_content_dump("r"),
        }
        actual_content_map_dict = payload["pointwise_metric_input"]["instance"][
            "content_map_instance"
        ]["values"]
        assert actual_content_map_dict == expected_content_map

        metric_spec_payload = payload["pointwise_metric_input"]["metric_spec"]
        assert (
            metric_spec_payload["custom_output_format_config"]["return_raw_output"]
            is True
        )
        assert metric_spec_payload["system_instruction"] == "You are a fair judge."

        autorater_config_payload = payload["autorater_config"]
        assert autorater_config_payload["autorater_model"] == "gemini-1.5-pro"
        assert autorater_config_payload["sampling_count"] == 5

    def test_merge_with_invalid_prompt_type(self):
        raw_dataset_1 = [
            {
                "prompt": 123,
                "response": "Response 1a",
            },
        ]
        with pytest.raises(
            ValueError,
            match="Invalid prompt type for case 0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_invalid_response_type(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
                "response": 123,
            },
        ]
        with pytest.raises(
            ValueError,
            match="Invalid response type",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_missing_prompt(self):
        raw_dataset_1 = [
            {
                "response": "Response 1a",
            },
        ]
        with pytest.raises(
            ValueError,
            match="Prompt is required but missing for eval_case_0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )

    def test_merge_with_missing_response(self):
        raw_dataset_1 = [
            {
                "prompt": "Prompt 1",
            },
        ]
        with pytest.raises(
            ValueError,
            match="Response is required but missing for eval_case_0",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=[raw_dataset_1],
                schemas=[_evals_data_converters.EvalDatasetSchema.FLATTEN],
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestAutoDetectDatasetSchema:
    def test_auto_detect_gemini_schema(self):
        raw_data = [
            {
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "Hello"}]}]
                },
                "response": {
                    "candidates": [
                        {"content": {"role": "model", "parts": [{"text": "Hi"}]}}
                    ]
                },
            }
        ]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.GEMINI
        )

    def test_auto_detect_flatten_schema(self):
        raw_data = [{"prompt": "Hello", "response": "Hi"}]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.FLATTEN
        )

    def test_auto_detect_openai_schema(self):
        raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "Hello"}]},
                "response": {
                    "choices": [{"message": {"role": "assistant", "content": "Hi"}}]
                },
            }
        ]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.OPENAI
        )

    def test_auto_detect_observability_schema(self):
        raw_data = [
            {
                "format": "observability",
                "request": json.dumps(
                    {"role": "user", "parts": [{"content": "Hello", "type": "text"}]}
                ),
                "response": json.dumps(
                    {
                        "role": "system",
                        "parts": [{"content": "Hi", "type": "text"}],
                    }
                ),
            }
        ]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.OBSERVABILITY
        )

    def test_auto_detect_unknown_schema(self):
        raw_data = [{"foo": "bar"}]
        assert (
            _evals_data_converters.auto_detect_dataset_schema(raw_data)
            == _evals_data_converters.EvalDatasetSchema.UNKNOWN
        )

    def test_auto_detect_empty_dataset(self):
        assert (
            _evals_data_converters.auto_detect_dataset_schema([])
            == _evals_data_converters.EvalDatasetSchema.UNKNOWN
        )


class TestEvalsRunEvaluation:
    """Unit tests for the evaluate method."""

    def test_execute_evaluation_computation_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test reference",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        computation_metric = vertexai_genai_types.Metric(name="exact_match")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[computation_metric],
        )

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "exact_match"
        assert summary_metric.mean_score == 1.0
        assert summary_metric.num_cases_total == 1
        assert summary_metric.num_cases_valid == 1
        assert len(result.eval_case_results) == 1
        case_result = result.eval_case_results[0]
        assert case_result.eval_case_index == 0
        assert len(case_result.response_candidate_results) == 1
        candidate_result = case_result.response_candidate_results[0]
        assert candidate_result.metric_results["exact_match"].score == 1.0

        mock_eval_dependencies["mock_evaluate_instances"].assert_called_once()
        call_args = mock_eval_dependencies["mock_evaluate_instances"].call_args
        assert "exact_match_input" in call_args[1]["metric_config"]

    def test_execute_evaluation_with_agent_info(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test reference",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        predefined_metric = vertexai_genai_types.PredefinedMetricSpec(
            metric_spec_name="tool_search_validity"
        )
        tool = {
            "function_declarations": [
                {
                    "name": "get_weather",
                    "description": "Get weather in a location",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                }
            ]
        }
        agent_info = {
            "name": "agent1",
            "instruction": "instruction1",
            "description": "description1",
            "tool_declarations": [tool],
        }

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[predefined_metric],
            agent_info=agent_info,
        )

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert len(result.eval_case_results) == 1
        assert result.agent_info.name == "agent1"
        assert result.agent_info.instruction == "instruction1"
        assert result.agent_info.tool_declarations == [
            genai_types.Tool(
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
        ]

    def test_execute_evaluation_translation_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "src lang",
                    "response": "tgt lang",
                    "reference": "ref lang",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        translation_metric = vertexai_genai_types.Metric(name="comet")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[translation_metric],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "comet"
        assert summary_metric.mean_score == 0.75
        mock_eval_dependencies["mock_evaluate_instances"].assert_called_once()
        call_args = mock_eval_dependencies["mock_evaluate_instances"].call_args
        assert "comet_input" in call_args[1]["metric_config"]

    def test_execute_evaluation_llm_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        llm_metric = vertexai_genai_types.LLMMetric(
            name="text_quality", prompt_template="Evaluate: {response}"
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[llm_metric],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "text_quality"
        assert summary_metric.mean_score == 0.9
        case_result = result.eval_case_results[0]
        candidate_result = case_result.response_candidate_results[0]
        assert (
            candidate_result.metric_results["text_quality"].explanation
            == "Mocked LLM explanation"
        )

        mock_eval_dependencies["mock_evaluate_instances"].assert_called_once()
        call_args = mock_eval_dependencies["mock_evaluate_instances"].call_args
        assert "pointwise_metric_input" in call_args[1]["metric_config"]

    def test_execute_evaluation_hallucination_metric(self, mock_api_client_fixture):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[
                vertexai_genai_types.RubricMetric.HALLUCINATION,
                vertexai_genai_types.RubricMetric.TOOL_USE_QUALITY,
            ],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 2
        assert result.summary_metrics[0].metric_name == "hallucination_v1"
        assert result.summary_metrics[1].metric_name == "tool_use_quality_v1"

    @mock.patch.object(_evals_data_converters, "get_dataset_converter")
    def test_execute_evaluation_with_openai_schema(
        self,
        mock_get_converter,
        mock_api_client_fixture,
        mock_eval_dependencies,
    ):
        mock_openai_raw_data = [
            {
                "request": {"messages": [{"role": "user", "content": "OpenAI Prompt"}]},
                "response": {
                    "choices": [
                        {
                            "message": {
                                "index": 0,
                                "message": {
                                    "role": "assistant",
                                    "content": "OpenAI Response",
                                    "refusal": None,
                                    "annotations": [],
                                },
                                "logprobs": None,
                                "finish_reason": "stop",
                            }
                        }
                    ]
                },
            }
        ]
        converted_eval_case = vertexai_genai_types.EvalCase(
            prompt=genai_types.Content(
                parts=[genai_types.Part(text="OpenAI Prompt")], role="user"
            ),
            responses=[
                vertexai_genai_types.ResponseCandidate(
                    response=genai_types.Content(
                        parts=[genai_types.Part(text="Candidate Response")]
                    )
                )
            ],
        )
        mock_converted_dataset = vertexai_genai_types.EvaluationDataset(
            eval_cases=[converted_eval_case]
        )

        mock_converter_instance = mock.Mock(
            spec=_evals_data_converters._OpenAIDataConverter
        )
        mock_converter_instance.convert.return_value = mock_converted_dataset
        mock_get_converter.return_value = mock_converter_instance

        input_dataset_for_loader = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(mock_openai_raw_data)
        )
        llm_metric = vertexai_genai_types.LLMMetric(
            name="test_metric", prompt_template="Evaluate: {response}"
        )

        with mock.patch.object(_evals_utils, "EvalDatasetLoader") as mock_loader_class:
            mock_loader_instance = mock_loader_class.return_value
            mock_loader_instance.load.return_value = mock_openai_raw_data

            with mock.patch.object(
                _evals_metric_handlers.LLMMetricHandler, "get_metric_result"
            ) as mock_llm_process:
                mock_llm_process.return_value = (
                    vertexai_genai_types.EvalCaseMetricResult(
                        metric_name="test_metric", score=0.75
                    )
                )

                result = _evals_common._execute_evaluation(
                    api_client=mock_api_client_fixture,
                    dataset=input_dataset_for_loader,
                    metrics=[llm_metric],
                    dataset_schema="OPENAI",
                )

        mock_loader_instance.load.assert_called_once_with(
            input_dataset_for_loader.eval_dataset_df
        )
        mock_get_converter.assert_called_with(
            _evals_data_converters.EvalDatasetSchema.OPENAI
        )
        mock_converter_instance.convert.assert_called_once_with(mock_openai_raw_data)

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "test_metric"
        assert summary_metric.mean_score == 0.75

    def test_execute_evaluation_custom_metric(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def my_custom_metric_fn(data: dict):
            return 0.5

        custom_metric = vertexai_genai_types.Metric(
            name="my_custom", custom_function=my_custom_metric_fn
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[custom_metric],
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "my_custom"
        assert summary_metric.mean_score == 0.5
        mock_eval_dependencies["mock_evaluate_instances"].assert_not_called()

    def test_llm_metric_default_aggregation_mixed_results(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {"prompt": "P1", "response": "R1"},
                {"prompt": "P2", "response": "R2"},
                {"prompt": "P3", "response": "R3"},
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        llm_metric = vertexai_genai_types.LLMMetric(
            name="quality", prompt_template="Rate: {response}"
        )

        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.side_effect = [
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="quality", score=0.8, explanation="Good"
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="quality", score=0.6, explanation="Okay"
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="quality", error_message="Processing failed"
                ),
            ]

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )

            assert mock_llm_process.call_count == 3
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary = result.summary_metrics[0]
            assert summary.metric_name == "quality"
            assert summary.num_cases_total == 3
            assert summary.num_cases_valid == 2
            assert summary.num_cases_error == 1
            assert summary.mean_score == pytest.approx(0.7)
            assert summary.stdev_score == pytest.approx(statistics.stdev([0.8, 0.6]))

    def test_llm_metric_custom_aggregation_success(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "P1", "response": "R1"}, {"prompt": "P2", "response": "R2"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def custom_agg_fn(results: list[vertexai_genai_types.EvalCaseMetricResult]):
            return {
                "my_custom_stat": 123,
                "mean_score": 0.75,
                "num_cases_valid": len(results),
            }

        llm_metric = vertexai_genai_types.LLMMetric(
            name="custom_quality",
            prompt_template="Rate: {response}",
            aggregate_summary_fn=custom_agg_fn,
        )

        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.side_effect = [
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="custom_quality", score=0.8
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="custom_quality", score=0.7
                ),
            ]

            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert mock_llm_process.call_count == 2
            assert result.evaluation_dataset == [input_dataset]
            assert len(result.summary_metrics) == 1
            summary = result.summary_metrics[0]
            assert summary.metric_name == "custom_quality"
            assert summary.num_cases_total == 2
            assert summary.num_cases_valid == 2
            assert summary.mean_score == 0.75
            assert summary.model_dump(exclude_none=True)["my_custom_stat"] == 123

    def test_llm_metric_custom_aggregation_error_fallback(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "P1", "response": "R1"}, {"prompt": "P2", "response": "R2"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def custom_agg_fn_error(
            results: list[vertexai_genai_types.EvalCaseMetricResult],
        ):
            raise ValueError("Custom aggregation failed")

        llm_metric = vertexai_genai_types.LLMMetric(
            name="error_fallback_quality",
            prompt_template="Rate: {response}",
            aggregate_summary_fn=custom_agg_fn_error,
        )
        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.side_effect = [
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="error_fallback_quality", score=0.9
                ),
                vertexai_genai_types.EvalCaseMetricResult(
                    metric_name="error_fallback_quality", score=0.5
                ),
            ]
            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert mock_llm_process.call_count == 2
            assert result.evaluation_dataset == [input_dataset]
            summary = result.summary_metrics[0]
            assert summary.metric_name == "error_fallback_quality"
            assert summary.num_cases_total == 2
            assert summary.num_cases_valid == 2
            assert summary.num_cases_error == 0
            assert summary.mean_score == pytest.approx(0.7)
            assert summary.stdev_score == pytest.approx(statistics.stdev([0.9, 0.5]))

    def test_llm_metric_custom_aggregation_invalid_return_type_fallback(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame([{"prompt": "P1", "response": "R1"}])
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        def custom_agg_fn_invalid_type(
            results: list[vertexai_genai_types.EvalCaseMetricResult],
        ):
            return "not a dict"

        llm_metric = vertexai_genai_types.LLMMetric(
            name="invalid_type_fallback",
            prompt_template="Rate: {response}",
            aggregate_summary_fn=custom_agg_fn_invalid_type,
        )
        with mock.patch(
            "vertexai._genai._evals_metric_handlers.LLMMetricHandler.get_metric_result"
        ) as mock_llm_process:
            mock_llm_process.return_value = vertexai_genai_types.EvalCaseMetricResult(
                metric_name="invalid_type_fallback", score=0.8
            )
            result = _evals_common._execute_evaluation(
                api_client=mock_api_client_fixture,
                dataset=input_dataset,
                metrics=[llm_metric],
            )
            assert result.evaluation_dataset == [input_dataset]
            summary = result.summary_metrics[0]
            assert summary.mean_score == 0.8
            assert summary.num_cases_valid == 1

    def test_execute_evaluation_lazy_loaded_prebuilt_metric_instance(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        lazy_metric_instance = _evals_metric_loaders.LazyLoadedPrebuiltMetric(
            name="fluency", version="v1"
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[lazy_metric_instance],
        )

        mock_eval_dependencies["mock_fetch_prebuilt_metric"].assert_called_once_with(
            mock_api_client_fixture
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "fluency"
        assert summary_metric.mean_score == 0.9

    def test_execute_evaluation_prebuilt_metric_via_loader(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )

        prebuilt_metric = vertexai_genai_types.RubricMetric.FLUENCY

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[prebuilt_metric],
        )

        mock_eval_dependencies["mock_fetch_prebuilt_metric"].assert_called_once_with(
            mock_api_client_fixture
        )
        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert result.evaluation_dataset == [input_dataset]
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "fluency"
        assert summary_metric.mean_score == 0.9

    def test_execute_evaluation_with_gcs_destination(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        dataset_df = pd.DataFrame(
            [
                {
                    "prompt": "Test prompt",
                    "response": "Test response",
                    "reference": "Test response",
                }
            ]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        metric = vertexai_genai_types.Metric(name="exact_match")
        gcs_dest = "gs://my-bucket/eval_results/"

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
            dest=gcs_dest,
        )

        mock_eval_dependencies["mock_upload_to_gcs"].assert_called_once_with(
            data=result.model_dump(
                mode="json", exclude_none=True, exclude={"evaluation_dataset"}
            ),
            gcs_dest_prefix=gcs_dest,
            filename_prefix="evaluation_result",
        )

    def test_execute_evaluation_multiple_datasets(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        df1 = pd.DataFrame([{"prompt": "p1", "response": "r1a", "reference": "ref1"}])
        df2 = pd.DataFrame([{"prompt": "p1", "response": "r1b", "reference": "ref1"}])
        dataset1 = vertexai_genai_types.EvaluationDataset(eval_dataset_df=df1)
        dataset2 = vertexai_genai_types.EvaluationDataset(eval_dataset_df=df2)
        metric = vertexai_genai_types.Metric(name="exact_match")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=[dataset1, dataset2],
            metrics=[metric],
        )

        assert isinstance(result, vertexai_genai_types.EvaluationResult)
        assert len(result.eval_case_results) == 1
        case_result = result.eval_case_results[0]
        assert len(case_result.response_candidate_results) == 2
        assert case_result.response_candidate_results[0].response_index == 0
        assert (
            case_result.response_candidate_results[0]
            .metric_results["exact_match"]
            .score
            == 1.0
        )
        assert case_result.response_candidate_results[1].response_index == 1
        assert (
            case_result.response_candidate_results[1]
            .metric_results["exact_match"]
            .score
            == 1.0
        )

        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "exact_match"
        assert summary_metric.num_cases_total == 2
        assert summary_metric.mean_score == 1.0

        assert mock_eval_dependencies["mock_evaluate_instances"].call_count == 2

    def test_execute_evaluation_deduplicates_candidate_names(
        self, mock_api_client_fixture, mock_eval_dependencies
    ):
        """Tests that duplicate candidate names are indexed."""
        dataset1 = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p1", "response": "r1", "reference": "ref1"}]
            ),
            candidate_name="gemini-pro",
        )
        dataset2 = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p1", "response": "r2", "reference": "ref1"}]
            ),
            candidate_name="gemini-flash",
        )
        dataset3 = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p1", "response": "r3", "reference": "ref1"}]
            ),
            candidate_name="gemini-pro",
        )

        mock_eval_dependencies["mock_evaluate_instances"].return_value = (
            vertexai_genai_types.EvaluateInstancesResponse(
                exact_match_results=vertexai_genai_types.ExactMatchResults(
                    exact_match_metric_values=[
                        vertexai_genai_types.ExactMatchMetricValue(score=1.0)
                    ]
                )
            )
        )

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=[dataset1, dataset2, dataset3],
            metrics=[vertexai_genai_types.Metric(name="exact_match")],
        )

        assert result.metadata.candidate_names == [
            "gemini-pro #1",
            "gemini-flash",
            "gemini-pro #2",
        ]

    @mock.patch("vertexai._genai._evals_common.datetime")
    def test_execute_evaluation_adds_creation_timestamp(
        self, mock_datetime, mock_api_client_fixture, mock_eval_dependencies
    ):
        """Tests that creation_timestamp is added to the result metadata."""
        import datetime

        mock_now = datetime.datetime(
            2025, 6, 18, 12, 0, 0, tzinfo=datetime.timezone.utc
        )
        mock_datetime.datetime.now.return_value = mock_now

        dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=pd.DataFrame(
                [{"prompt": "p", "response": "r", "reference": "r"}]
            )
        )
        metric = vertexai_genai_types.Metric(name="exact_match")

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=dataset,
            metrics=[metric],
        )

        assert result.metadata is not None
        assert result.metadata.creation_timestamp == mock_now

    @mock.patch(
        "vertexai._genai._evals_metric_handlers._evals_constant.SUPPORTED_PREDEFINED_METRICS",
        frozenset(["summarization_quality"]),
    )
    @mock.patch("time.sleep", return_value=None)
    @mock.patch("vertexai._genai.evals.Evals._evaluate_instances")
    def test_predefined_metric_retry_on_resource_exhausted(
        self,
        mock_private_evaluate_instances,
        mock_sleep,
        mock_api_client_fixture,
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        metric = vertexai_genai_types.Metric(name="summarization_quality")
        metric_result = vertexai_genai_types.MetricResult(
            score=0.9,
            explanation="Mocked predefined explanation",
            rubric_verdicts=[],
            error=None,
        )
        error_response_json = {
            "error": {
                "code": 429,
                "message": ("Judge model resource exhausted. Please try again later."),
                "status": "RESOURCE_EXHAUSTED",
            }
        }
        mock_private_evaluate_instances.side_effect = [
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            vertexai_genai_types.EvaluateInstancesResponse(
                metric_results=[metric_result]
            ),
        ]

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
        )

        assert mock_private_evaluate_instances.call_count == 3
        assert mock_sleep.call_count == 2
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "summarization_quality"
        assert summary_metric.mean_score == 0.9

    @mock.patch(
        "vertexai._genai._evals_metric_handlers._evals_constant.SUPPORTED_PREDEFINED_METRICS",
        frozenset(["summarization_quality"]),
    )
    @mock.patch("time.sleep", return_value=None)
    @mock.patch("vertexai._genai.evals.Evals._evaluate_instances")
    def test_predefined_metric_retry_fail_on_resource_exhausted(
        self,
        mock_private_evaluate_instances,
        mock_sleep,
        mock_api_client_fixture,
    ):
        dataset_df = pd.DataFrame(
            [{"prompt": "Test prompt", "response": "Test response"}]
        )
        input_dataset = vertexai_genai_types.EvaluationDataset(
            eval_dataset_df=dataset_df
        )
        error_response_json = {
            "error": {
                "code": 429,
                "message": ("Judge model resource exhausted. Please try again later."),
                "status": "RESOURCE_EXHAUSTED",
            }
        }
        metric = vertexai_genai_types.Metric(name="summarization_quality")
        mock_private_evaluate_instances.side_effect = [
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
            genai_errors.ClientError(code=429, response_json=error_response_json),
        ]

        result = _evals_common._execute_evaluation(
            api_client=mock_api_client_fixture,
            dataset=input_dataset,
            metrics=[metric],
        )

        assert mock_private_evaluate_instances.call_count == 3
        assert mock_sleep.call_count == 2
        assert len(result.summary_metrics) == 1
        summary_metric = result.summary_metrics[0]
        assert summary_metric.metric_name == "summarization_quality"
        assert summary_metric.mean_score is None
        assert summary_metric.num_cases_error == 1
        assert (
            "Judge model resource exhausted after 3 retries"
        ) in result.eval_case_results[0].response_candidate_results[0].metric_results[
            "summarization_quality"
        ].error_message


class TestEvaluationDataset:
    """Contains set of tests for the EvaluationDataset class methods."""

    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_load_from_observability_eval_cases(self, mock_gcs_utils):
        """Tests that load_from_observability_eval_cases reads data from GCS."""

        def read_file_contents_side_effect(src: str) -> str:
            if src == "gs://project/input.json":
                return "input"
            elif src == "gs://project/output.json":
                return "output"
            elif src == "gs://project/system_instruction.json":
                return "system_instruction"
            else:
                return ""

        mock_gcs_utils.return_value.read_file_contents.side_effect = (
            read_file_contents_side_effect
        )

        eval_cases = [
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input.json",
                output_src="gs://project/output.json",
                system_instruction_src="gs://project/system_instruction.json",
            )
        ]
        result = (
            vertexai_genai_types.EvaluationDataset.load_from_observability_eval_cases(
                eval_cases
            )
        )

        mock_gcs_utils.return_value.read_file_contents.assert_has_calls(
            [
                mock.call("gs://project/input.json"),
                mock.call("gs://project/output.json"),
                mock.call("gs://project/system_instruction.json"),
            ],
            any_order=True,
        )
        assert result.eval_dataset_df is not None
        pd.testing.assert_frame_equal(
            result.eval_dataset_df,
            pd.DataFrame(
                {
                    "format": ["observability"],
                    "request": ["input"],
                    "response": ["output"],
                    "system_instruction": ["system_instruction"],
                }
            ),
        )

    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_load_from_observability_eval_cases_no_system_instruction(
        self, mock_gcs_utils
    ):
        """Tests load_from_observability_eval_cases works without system_instruction."""

        def read_file_contents_side_effect(src: str) -> str:
            if src == "gs://project/input.json":
                return "input"
            elif src == "gs://project/output.json":
                return "output"
            elif src == "gs://project/system_instruction.json":
                return "system_instruction"
            else:
                return ""

        mock_gcs_utils.return_value.read_file_contents.side_effect = (
            read_file_contents_side_effect
        )

        eval_cases = [
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input.json",
                output_src="gs://project/output.json",
            )
        ]
        result = (
            vertexai_genai_types.EvaluationDataset.load_from_observability_eval_cases(
                eval_cases
            )
        )

        mock_gcs_utils.return_value.read_file_contents.assert_has_calls(
            [
                mock.call("gs://project/input.json"),
                mock.call("gs://project/output.json"),
            ],
            any_order=True,
        )
        assert result.eval_dataset_df is not None
        pd.testing.assert_frame_equal(
            result.eval_dataset_df,
            pd.DataFrame(
                {
                    "format": ["observability"],
                    "request": ["input"],
                    "response": ["output"],
                    "system_instruction": [""],
                }
            ),
        )

    @mock.patch.object(_gcs_utils, "GcsUtils")
    def test_load_from_observability_eval_cases_multiple_cases(self, mock_gcs_utils):
        """Test load_from_observability_eval_cases can handle multiple cases."""

        def read_file_contents_side_effect(src: str) -> str:
            if src == "gs://project/input_1.json":
                return "input_1"
            elif src == "gs://project/input_2.json":
                return "input_2"
            elif src == "gs://project/output_1.json":
                return "output_1"
            elif src == "gs://project/output_2.json":
                return "output_2"
            elif src == "gs://project/system_instruction_1.json":
                return "system_instruction_1"
            elif src == "gs://project/system_instruction_2.json":
                return "system_instruction_2"
            else:
                return ""

        mock_gcs_utils.return_value.read_file_contents.side_effect = (
            read_file_contents_side_effect
        )

        eval_cases = [
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input_1.json",
                output_src="gs://project/output_1.json",
                system_instruction_src="gs://project/system_instruction_1.json",
            ),
            vertexai_genai_types.ObservabilityEvalCase(
                input_src="gs://project/input_2.json",
                output_src="gs://project/output_2.json",
                system_instruction_src="gs://project/system_instruction_2.json",
            ),
        ]
        result = (
            vertexai_genai_types.EvaluationDataset.load_from_observability_eval_cases(
                eval_cases
            )
        )

        assert result.eval_dataset_df is not None
        pd.testing.assert_frame_equal(
            result.eval_dataset_df,
            pd.DataFrame(
                {
                    "format": ["observability", "observability"],
                    "request": ["input_1", "input_2"],
                    "response": ["output_1", "output_2"],
                    "system_instruction": [
                        "system_instruction_1",
                        "system_instruction_2",
                    ],
                }
            ),
        )
