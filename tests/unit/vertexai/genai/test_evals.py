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

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer as aiplatform_initializer
from vertexai import _genai
from vertexai._genai import types as vertexai_genai_types
from google.genai import types as genai_types
import google.genai.errors as genai_errors
import pandas as pd
import pytest
import warnings

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


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

    @pytest.mark.usefixtures("google_auth_mock")
    def test_evaluate_instances(self):
        test_client = _genai.client.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        with warnings.catch_warnings(record=True) as captured_warnings:
            warnings.simplefilter("always")
            with mock.patch.object(
                test_client.evals, "_evaluate_instances"
            ) as mock_evaluate:
                test_client.evals._evaluate_instances(
                    bleu_input=_genai.types.BleuInput()
                )
                mock_evaluate.assert_called_once_with(
                    bleu_input=_genai.types.BleuInput()
                )
                assert captured_warnings[0].category == genai_errors.ExperimentalWarning

    @pytest.mark.usefixtures("google_auth_mock")
    def test_eval_run(self):
        test_client = _genai.client.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        with pytest.raises(NotImplementedError):
            test_client.evals.run()

    @pytest.mark.usefixtures("google_auth_mock")
    def test_eval_batch_eval(self):
        test_client = _genai.client.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        with mock.patch.object(test_client.evals, "batch_eval") as mock_batch_eval:
            test_client.evals.batch_eval(
                dataset=_genai.types.EvaluationDataset(),
                metrics=[_genai.types.Metric()],
                output_config=_genai.types.OutputConfig(),
                autorater_config=_genai.types.AutoraterConfig(),
                config=_genai.types.EvaluateDatasetConfig(),
            )
            mock_batch_eval.assert_called_once()


class TestEvalsClientInference:
    """Unit tests for the Evals client inference method."""

    def setup_method(self):
        importlib.reload(aiplatform_initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(_genai.client)
        importlib.reload(_genai.types)
        importlib.reload(_genai.evals)
        importlib.reload(_genai._evals_utils)
        importlib.reload(_genai._evals_common)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.client = _genai.client.Client(
            project=_TEST_PROJECT, location=_TEST_LOCATION
        )

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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

    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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

        config = _genai.types.EvalRunInferenceConfig(
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

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
    @mock.patch(f"{_genai._evals_utils.__name__}.GcsUtils")
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
        config = _genai.types.EvalRunInferenceConfig(dest=gcs_dest_path)

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

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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
        config = _genai.types.EvalRunInferenceConfig(dest=local_dest_path)

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

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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
        config = _genai.types.EvalRunInferenceConfig(dest=local_dest_path)

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
            ]
        )
        expected_df = pd.DataFrame(
            {
                "prompt": ["prompt 1", "prompt 2"],
                "request": ["req 1", "req 2"],
                "response": ["resp 1", "resp 2"],
            }
        )
        pd.testing.assert_frame_equal(result_df, expected_df)

        # Assert that the local file was created with the correct content
        with open(local_dest_path, "r") as f:
            saved_records = [json.loads(line) for line in f]
        expected_records = expected_df.to_dict(orient="records")
        assert saved_records == expected_records
        os.remove(local_dest_path)

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
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
        pd.testing.assert_frame_equal(result_df, expected_df)
        os.remove(local_src_path)

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
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
        pd.testing.assert_frame_equal(result_df, expected_df)
        os.remove(local_src_path)

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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
            ]
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
        pd.testing.assert_frame_equal(result_df, expected_df)

    @mock.patch(f"{_genai._evals_common.__name__}.Models")
    @mock.patch(f"{_genai._evals_utils.__name__}.EvalDatasetLoader")
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

        config = _genai.types.EvalRunInferenceConfig(
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
