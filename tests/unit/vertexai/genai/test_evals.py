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

import importlib
import json
import os
from unittest import mock
import warnings

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
from vertexai import _genai
from vertexai._genai import _evals_metric_handlers
from vertexai._genai import _evals_data_converters
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
    @mock.patch.object(client.Client, "_get_api_client")
    @mock.patch.object(evals.Evals, "_evaluate_instances")
    def test_evaluate_instances(self, mock_evaluate, mock_get_api_client):
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            self.client.evals._evaluate_instances(
                bleu_input=vertexai_genai_types.BleuInput()
            )
            mock_evaluate.assert_called_once_with(
                bleu_input=vertexai_genai_types.BleuInput()
            )
            assert captured_warnings[0].category == genai_errors.ExperimentalWarning

    @pytest.mark.usefixtures("google_auth_mock")
    def test_eval_run(self):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(NotImplementedError):
            test_client.evals.run()

    @pytest.mark.usefixtures("google_auth_mock")
    @mock.patch.object(client.Client, "_get_api_client")
    @mock.patch.object(evals.Evals, "batch_eval")
    def test_eval_batch_eval(self, mock_evaluate, mock_get_api_client):
        test_client = vertexai.Client(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_client.evals.batch_eval(
            dataset=vertexai_genai_types.EvaluationDataset(),
            metrics=[vertexai_genai_types.Metric(name="test")],
            output_config=vertexai_genai_types.OutputConfig(),
            autorater_config=vertexai_genai_types.AutoraterConfig(),
            config=vertexai_genai_types.EvaluateDatasetConfig(),
        )
        mock_evaluate.assert_called_once()


class TestEvalsClientInference:
    """Unit tests for the Evals client inference method."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(_genai.client)
        importlib.reload(vertexai_genai_types)
        importlib.reload(_genai.evals)
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

        result_df = self.client.evals.run_inference(
            model="gemini-pro",
            src=mock_df,
        )

        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        mock_models.return_value.generate_content.assert_called_once()
        pd.testing.assert_frame_equal(
            result_df,
            pd.DataFrame(
                {
                    "prompt": ["test prompt"],
                    "response": ["test response"],
                }
            ),
        )

    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_callable_model_success(self, mock_eval_dataset_loader):
        mock_df = pd.DataFrame({"prompt": ["test prompt"]})
        mock_eval_dataset_loader.return_value.load.return_value = mock_df.to_dict(
            orient="records"
        )

        def mock_model_fn(contents):
            return "callable response"

        result_df = self.client.evals.run_inference(
            model=mock_model_fn,
            src=mock_df,
        )
        mock_eval_dataset_loader.return_value.load.assert_called_once_with(mock_df)
        pd.testing.assert_frame_equal(
            result_df,
            pd.DataFrame(
                {
                    "prompt": ["test prompt"],
                    "response": ["callable response"],
                }
            ),
        )

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
        result_df = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )
        assert (
            mock_models.return_value.generate_content.call_args[1]["contents"]
            == "Hello world"
        )
        pd.testing.assert_frame_equal(
            result_df,
            pd.DataFrame(
                {
                    "text_input": ["world"],
                    "request": ["Hello world"],
                    "response": ["templated response"],
                }
            ),
        )

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    @mock.patch.object(_evals_utils, "GcsUtils")
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

        gcs_dest_path = "gs://bucket/output.jsonl"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=gcs_dest_path)

        result_df = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

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
            gcs_destination_blob_path=gcs_dest_path,
            file_type="jsonl",
        )
        pd.testing.assert_frame_equal(result_df, expected_df_to_save)

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

        local_dest_path = "/tmp/test/output_dir/results.jsonl"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=local_dest_path)

        result_df = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

        mock_makedirs.assert_called_once_with("/tmp/test/output_dir", exist_ok=True)
        mock_df_to_json.assert_called_once_with(
            local_dest_path, orient="records", lines=True
        )
        expected_df = pd.DataFrame(
            {
                "prompt": ["local save"],
                "response": ["local response"],
            }
        )
        pd.testing.assert_frame_equal(result_df, expected_df)

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_from_request_column_save_locally(
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

        local_dest_path = "/tmp/output.jsonl"
        config = vertexai_genai_types.EvalRunInferenceConfig(dest=local_dest_path)

        result_df = self.client.evals.run_inference(
            model="gemini-pro", src=mock_df, config=config
        )

        # Assert that generate_content was called with the 'request' column
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
            result_df.sort_values(by="request").reset_index(drop=True),
            expected_df.sort_values(by="request").reset_index(drop=True),
        )

        # Assert that the local file was created with the correct content
        with open(local_dest_path, "r") as f:
            saved_records = [json.loads(line) for line in f]
        expected_records = expected_df.to_dict(orient="records")
        assert sorted(saved_records, key=lambda x: x["request"]) == sorted(
            expected_records, key=lambda x: x["request"]
        )
        os.remove(local_dest_path)

    @mock.patch.object(_evals_common, "Models")
    def test_inference_from_local_jsonl_file(self, mock_models):
        # Create a temporary JSONL file
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

        result_df = self.client.evals.run_inference(
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
            result_df.sort_values(by="prompt").reset_index(drop=True),
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

    @mock.patch.object(_evals_common, "Models")
    def test_inference_from_local_csv_file(self, mock_models):
        # Create a temporary CSV file
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

        result_df = self.client.evals.run_inference(
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
            result_df.sort_values(by="prompt").reset_index(drop=True),
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

    @mock.patch.object(_evals_common, "Models")
    @mock.patch.object(_evals_utils, "EvalDatasetLoader")
    def test_inference_with_row_level_config_overrides(
        self, mock_eval_dataset_loader, mock_models
    ):
        mock_df = pd.DataFrame(
            {
                "request": [
                    json.dumps(
                        {"prompt": "req 1", "generation_config": {"top_p": 0.5}}
                    ),
                    json.dumps(
                        {"prompt": "req 2", "generation_config": {"top_p": 0.9}}
                    ),
                ]
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

        result_df = self.client.evals.run_inference(model="gemini-pro", src=mock_df)

        mock_models.return_value.generate_content.assert_has_calls(
            [
                mock.call(
                    model="gemini-pro",
                    contents=json.dumps(
                        {"prompt": "req 1", "generation_config": {"top_p": 0.5}}
                    ),
                    config=genai_types.GenerateContentConfig(top_p=0.5),
                ),
                mock.call(
                    model="gemini-pro",
                    contents=json.dumps(
                        {"prompt": "req 2", "generation_config": {"top_p": 0.9}}
                    ),
                    config=genai_types.GenerateContentConfig(top_p=0.9),
                ),
            ],
            any_order=True,
        )

        expected_df = pd.DataFrame(
            {
                "request": [
                    json.dumps(
                        {"prompt": "req 1", "generation_config": {"top_p": 0.5}}
                    ),
                    json.dumps(
                        {"prompt": "req 2", "generation_config": {"top_p": 0.9}}
                    ),
                ],
                "response": ["resp 1", "resp 2"],
            }
        )
        pd.testing.assert_frame_equal(
            result_df.sort_values(by="request").reset_index(drop=True),
            expected_df.sort_values(by="request").reset_index(drop=True),
        )

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
        result_df = self.client.evals.run_inference(
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
            result_df,
            pd.DataFrame(
                {
                    "text_input": ["hello world"],
                    "media_content": [mock_media_content_json],
                    "request": [assembled_prompt_json],
                    "response": ["test response"],
                }
            ),
        )


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
                        },  # history
                        {
                            "role": "model",
                            "parts": [{"text": "Initial model"}],
                        },  # history
                        {
                            "role": "user",
                            "parts": [{"text": "Actual prompt"}],
                        },  # prompt
                        {
                            "role": "model",
                            "parts": [{"text": "This is reference"}],
                        },  # reference
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
        # Last message in contents is from user, so it becomes the prompt.
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
        assert eval_case.responses[0].response is None

    def test_convert_invalid_content_structure_raises_value_error(self):
        raw_data = [
            {
                "request": {"contents": ["not a dict"]},  # Invalid content
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.GEMINI,
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
        with pytest.raises(ValueError, match="Input 'raw_datasets' cannot be empty."):
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.GEMINI,
        ]
        with pytest.raises(
            ValueError,
            match="A list of schemas must be provided, one for each raw dataset.",
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
            match="A list of schemas must be provided, one for each raw dataset.",
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.GEMINI,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
            _evals_data_converters._EvalDatasetSchema.FLATTEN,
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
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
            )
        with pytest.raises(
            ValueError,
            match="Input 'raw_datasets' cannot be empty and must be a list of lists",
        ):
            _evals_data_converters.merge_response_datasets_into_canonical_format(
                raw_datasets=["invalid_dataset"],
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
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
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestLLMMetricHandlerPayload:
    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(genai_types)
        importlib.reload(vertexai_genai_types)
        importlib.reload(_evals_data_converters)
        importlib.reload(_evals_metric_handlers)

        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        self.mock_api_client = mock.Mock(spec=client.Client)
        self.mock_evals_module = evals.Evals(api_client_=self.mock_api_client)

    def test_build_request_payload_basic_filtering_and_fields(self):
        metric = vertexai_genai_types.LLMMetric(
            name="test_quality",
            prompt_template="Eval: {prompt} with {response}. Context: "
            "{custom_context}. Ref: {reference}",
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
            custom_context="Custom context value.",  # pylint: disable=unexpected-keyword-arg
            extra_field_not_in_template="This should be excluded.",  # pylint: disable=unexpected-keyword-arg
            eval_case_id="case-123",
        )

        payload = handler._build_request_payload(eval_case=eval_case, response_index=0)

        expected_json_instance_dict = {
            "prompt": "User prompt text",
            "response": "Model response text",
            "custom_context": "Custom context value.",
            "reference": "Ground truth text",
        }

        actual_json_instance_str = payload["pointwise_metric_input"]["instance"][
            "json_instance"
        ]
        actual_json_instance_dict = json.loads(actual_json_instance_str)

        assert actual_json_instance_dict == expected_json_instance_dict
        assert "extra_field_not_in_template" not in actual_json_instance_dict
        assert "eval_case_id" not in actual_json_instance_dict

        assert (
            "custom_output_format_config"
            not in payload["pointwise_metric_input"]["metric_spec"]
        )
        assert (
            "system_instruction" not in payload["pointwise_metric_input"]["metric_spec"]
        )
        assert "autorater_config" not in payload

    def test_build_request_payload_various_field_types(self):
        metric = vertexai_genai_types.LLMMetric(
            name="complex_eval",
            prompt_template=(
                "P: {prompt}, R: {response}, Hist: {conversation_history}, "
                "SysInstruct: {system_instruction}, "
                "DictField: {dict_field}, ListField: {list_field}, "
                "IntField: {int_field}, BoolField: {bool_field}"
            ),
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
                vertexai_genai_types.Message(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Turn 1 user")], role="user"
                    )
                ),
                vertexai_genai_types.Message(
                    content=genai_types.Content(
                        parts=[genai_types.Part(text="Turn 1 model")], role="model"
                    )
                ),
            ],
            system_instruction=genai_types.Content(
                parts=[genai_types.Part(text="System instructions here.")]
            ),
            dict_field={  # pylint: disable=unexpected-keyword-arg
                "key1": "val1",
                "key2": [1, 2],
            },
            list_field=["a", "b", {"c": 3}],  # pylint: disable=unexpected-keyword-arg
            int_field=42,  # pylint: disable=unexpected-keyword-arg
            bool_field=True,  # pylint: disable=unexpected-keyword-arg
        )

        payload = handler._build_request_payload(eval_case=eval_case, response_index=0)
        actual_json_instance_dict = json.loads(
            payload["pointwise_metric_input"]["instance"]["json_instance"]
        )

        expected_json_instance_dict = {
            "prompt": "The Prompt",
            "response": "The Response",
            "conversation_history": "user: Turn 1 user\nmodel: Turn 1 model",
            "system_instruction": "System instructions here.",
            "dict_field": json.dumps({"key1": "val1", "key2": [1, 2]}),
            "list_field": json.dumps(["a", "b", {"c": 3}]),
            "int_field": "42",
            "bool_field": "True",
        }
        assert actual_json_instance_dict == expected_json_instance_dict

    def test_build_request_payload_optional_metric_configs_set(self):
        metric = vertexai_genai_types.LLMMetric(
            name="configured_metric",
            prompt_template="P: {prompt}, R: {response}",
            return_raw_output=True,
            judge_model_system_instruction="Be a fair judge.",
            judge_model="gemini-pro",
            judge_model_sampling_count=10,
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

        expected_json_instance = {"prompt": "p", "response": "r"}
        actual_json_instance = json.loads(
            payload["pointwise_metric_input"]["instance"]["json_instance"]
        )
        assert actual_json_instance == expected_json_instance

        metric_spec_payload = payload["pointwise_metric_input"]["metric_spec"]
        assert (
            metric_spec_payload["metric_prompt_template"]
            == "P: {prompt}, R: {response}"
        )
        assert metric_spec_payload["custom_output_format_config"]["return_raw_output"]
        assert metric_spec_payload["system_instruction"] == "Be a fair judge."

        autorater_config_payload = payload["autorater_config"]
        assert autorater_config_payload["autorater_model"] == "gemini-pro"
        assert autorater_config_payload["sampling_count"] == 10

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
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
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
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
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
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
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
                schemas=[_evals_data_converters._EvalDatasetSchema.FLATTEN],
            )
