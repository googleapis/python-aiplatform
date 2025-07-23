# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

# pylint: disable=protected-access, g-multiple-import

import pytest

from google import auth
from google.cloud import aiplatform
from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state,
)
from tests.system.aiplatform import e2e_base
from google.cloud.aiplatform.utils import gcs_utils
from vertexai import language_models
from vertexai.preview import (
    language_models as preview_language_models,
)
from vertexai.preview.language_models import (
    ChatModel,
    CodeGenerationModel,
    InputOutputTextPair,
    TextGenerationModel,
    TextGenerationResponse,
    TextEmbeddingModel,
)

STAGING_DIR_URI = "gs://ucaip-samples-us-central1/tmp/staging"


@pytest.mark.skip(reason="Models are deprecated.")
class TestLanguageModels(e2e_base.TestEndToEnd):
    """System tests for language models."""

    _temp_prefix = "temp_language_models_test_"

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_text_generation(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = TextGenerationModel.from_pretrained("google/text-bison@001")
        grounding_source = language_models.GroundingSource.WebSearch()
        response = model.predict(
            "What is the best recipe for cupcakes? Recipe:",
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=5,
            stop_sequences=["# %%"],
            grounding_source=grounding_source,
        )
        assert response.text or response.is_blocked

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_text_generation_preview_count_tokens(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = preview_language_models.TextGenerationModel.from_pretrained(
            "google/text-bison@001"
        )

        response = model.count_tokens(["How are you doing?"])

        assert response.total_tokens
        assert response.total_billable_characters

    @pytest.mark.asyncio
    async def test_text_generation_model_predict_async(self):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        model = TextGenerationModel.from_pretrained("google/text-bison@001")
        grounding_source = language_models.GroundingSource.WebSearch()
        response = await model.predict_async(
            "What is the best recipe for cupcakes? Recipe:",
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=5,
            stop_sequences=["# %%"],
            grounding_source=grounding_source,
        )
        assert response.text or response.is_blocked

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_text_generation_streaming(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = TextGenerationModel.from_pretrained("google/text-bison@001")

        for response in model.predict_streaming(
            "What is the best recipe for cupcakes? Recipe:",
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=5,
        ):
            assert response.text or response.is_blocked

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_preview_text_generation_from_pretrained(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = preview_language_models.TextGenerationModel.from_pretrained(
            "google/text-bison@001"
        )

        response = model.predict(
            "What is the best recipe for cupcakes? Recipe:",
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=5,
            stop_sequences=["# %%"],
        )
        assert response.text or response.is_blocked

        assert isinstance(model, preview_language_models.TextGenerationModel)

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_chat_on_chat_model(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )
        chat_model = ChatModel.from_pretrained("google/chat-bison@001")
        grounding_source = language_models.GroundingSource.WebSearch()
        chat = chat_model.start_chat(
            context="My name is Ned. You are my personal assistant. My favorite movies are Lord of the Rings and Hobbit.",
            examples=[
                InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            temperature=0.0,
            stop_sequences=["# %%"],
        )

        message1 = "Are my favorite movies based on a book series?"
        response1 = chat.send_message(
            message1,
            grounding_source=grounding_source,
        )
        assert response1.text
        assert response1.grounding_metadata
        assert len(chat.message_history) == 2
        assert chat.message_history[0].author == chat.USER_AUTHOR
        assert chat.message_history[0].content == message1
        assert chat.message_history[1].author == chat.MODEL_AUTHOR

        message2 = "When were these books published?"
        response2 = chat.send_message(
            message2, temperature=0.1, grounding_source=grounding_source
        )
        assert response2.text
        assert response2.grounding_metadata
        assert len(chat.message_history) == 4
        assert chat.message_history[2].author == chat.USER_AUTHOR
        assert chat.message_history[2].content == message2
        assert chat.message_history[3].author == chat.MODEL_AUTHOR

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_chat_model_preview_count_tokens(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        chat_model = ChatModel.from_pretrained("google/chat-bison@001")

        chat = chat_model.start_chat()

        chat.send_message("What should I do today?")

        response_with_history = chat.count_tokens("Any ideas?")

        response_without_history = chat_model.start_chat().count_tokens(
            "What should I do today?"
        )

        assert (
            response_with_history.total_tokens > response_without_history.total_tokens
        )
        assert (
            response_with_history.total_billable_characters
            > response_without_history.total_billable_characters
        )

    @pytest.mark.asyncio
    async def test_chat_model_async(self):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        chat_model = ChatModel.from_pretrained("google/chat-bison@001")
        grounding_source = language_models.GroundingSource.WebSearch()
        chat = chat_model.start_chat(
            context="My name is Ned. You are my personal assistant. My favorite movies are Lord of the Rings and Hobbit.",
            examples=[
                InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            temperature=0.0,
            stop_sequences=["# %%"],
        )

        message1 = "Are my favorite movies based on a book series?"
        response1 = await chat.send_message_async(
            message1,
            grounding_source=grounding_source,
        )
        assert response1.text
        assert response1.grounding_metadata
        assert len(chat.message_history) == 2
        assert chat.message_history[0].author == chat.USER_AUTHOR
        assert chat.message_history[0].content == message1
        assert chat.message_history[1].author == chat.MODEL_AUTHOR

        message2 = "When were these books published?"
        response2 = await chat.send_message_async(
            message2,
            temperature=0.1,
            grounding_source=grounding_source,
        )
        assert response2.text
        assert response2.grounding_metadata
        assert len(chat.message_history) == 4
        assert chat.message_history[2].author == chat.USER_AUTHOR
        assert chat.message_history[2].content == message2
        assert chat.message_history[3].author == chat.MODEL_AUTHOR

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_chat_model_send_message_streaming(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        chat_model = ChatModel.from_pretrained("google/chat-bison@001")
        chat = chat_model.start_chat(
            context="My name is Ned. You are my personal assistant. My favorite movies are Lord of the Rings and Hobbit.",
            examples=[
                InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            temperature=0.0,
        )

        message1 = "Are my favorite movies based on a book series?"
        for response in chat.send_message_streaming(message1):
            assert isinstance(response, TextGenerationResponse)
        assert len(chat.message_history) == 2
        assert chat.message_history[0].author == chat.USER_AUTHOR
        assert chat.message_history[0].content == message1
        assert chat.message_history[1].author == chat.MODEL_AUTHOR

        message2 = "When were these books published?"
        for response2 in chat.send_message_streaming(
            message2,
            temperature=0.1,
        ):
            assert isinstance(response2, TextGenerationResponse)
        assert len(chat.message_history) == 4
        assert chat.message_history[2].author == chat.USER_AUTHOR
        assert chat.message_history[2].content == message2
        assert chat.message_history[3].author == chat.MODEL_AUTHOR

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_text_embedding(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = TextEmbeddingModel.from_pretrained("google/textembedding-gecko@001")
        # One short text, one llong text (to check truncation)
        texts = ["What is life?", "What is life?" * 1000]
        embeddings = model.get_embeddings(texts)
        assert len(embeddings) == 2
        assert len(embeddings[0].values) == 768
        assert embeddings[0].statistics.token_count > 0
        assert not embeddings[0].statistics.truncated

        assert len(embeddings[1].values) == 768
        assert embeddings[1].statistics.token_count > 1000
        assert embeddings[1].statistics.truncated

    @pytest.mark.asyncio
    async def test_text_embedding_async(self):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        model = TextEmbeddingModel.from_pretrained("google/textembedding-gecko@001")
        # One short text, one llong text (to check truncation)
        texts = ["What is life?", "What is life?" * 1000]
        embeddings = await model.get_embeddings_async(texts)
        assert len(embeddings) == 2
        assert len(embeddings[0].values) == 768
        assert embeddings[0].statistics.token_count > 0
        assert not embeddings[0].statistics.truncated

        assert len(embeddings[1].values) == 768
        assert embeddings[1].statistics.token_count > 1000
        assert embeddings[1].statistics.truncated

    # TODO(b/339907038): Re-enable test after timeout issue is fixed.
    @pytest.mark.skip(reason="Causes system tests timeout")
    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_tuning(self, shared_state, api_transport):
        """Test tuning, listing and loading models."""
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
            api_transport=api_transport,
        )

        model = language_models.TextGenerationModel.from_pretrained("text-bison@001")

        import pandas

        training_data = pandas.DataFrame(
            data=[
                {"input_text": "Input 0", "output_text": "Output 0"},
                {"input_text": "Input 1", "output_text": "Output 1"},
                {"input_text": "Input 2", "output_text": "Output 2"},
                {"input_text": "Input 3", "output_text": "Output 3"},
                {"input_text": "Input 4", "output_text": "Output 4"},
                {"input_text": "Input 5", "output_text": "Output 5"},
                {"input_text": "Input 6", "output_text": "Output 6"},
                {"input_text": "Input 7", "output_text": "Output 7"},
                {"input_text": "Input 8", "output_text": "Output 8"},
                {"input_text": "Input 9", "output_text": "Output 9"},
            ]
        )

        dataset_uri = (
            STAGING_DIR_URI + "/veretx_llm_tuning_training_data.text-bison.dummy.jsonl"
        )
        gcs_utils._upload_pandas_df_to_gcs(
            df=training_data, upload_gcs_path=dataset_uri
        )

        tuning_job = model.tune_model(
            training_data=training_data,
            train_steps=1,
            tuning_job_location="europe-west4",
            tuned_model_location="us-central1",
            learning_rate_multiplier=2.0,
            tuning_evaluation_spec=preview_language_models.TuningEvaluationSpec(
                evaluation_data=dataset_uri,
                evaluation_interval=37,
                enable_early_stopping=True,
            ),
        )
        tuned_model1 = tuning_job.get_tuned_model()

        # According to the Pipelines design, external resources created by a pipeline
        # must not be modified or deleted. Otherwise caching will break next pipeline runs.
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(tuned_model1._endpoint)
        shared_state["resources"].extend(
            aiplatform.Model(model_name=deployed_model.model)
            for deployed_model in tuned_model1._endpoint.list_models()
        )
        # Deleting the Endpoint is a little less bad since the LLM SDK will recreate it, but it's not advised for the same reason.

        # Testing the new model returned by the `tuning_job.get_tuned_model` method
        response1 = tuned_model1.predict(
            "What is the best recipe for cupcakes? Recipe:",
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=5,
        )
        assert response1.text or response1.is_blocked

        # Testing listing and getting tuned models
        tuned_model_names = model.list_tuned_model_names()
        assert tuned_model_names
        tuned_model_name = tuned_model_names[0]

        tuned_model = TextGenerationModel.get_tuned_model(tuned_model_name)

        tuned_model_response = tuned_model.predict(
            "What is the best recipe for cupcakes? Recipe:",
            max_output_tokens=128,
            temperature=0.0,
            top_p=1.0,
            top_k=5,
        )
        assert tuned_model_response.text or tuned_model_response.is_blocked

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_batch_prediction_for_text_generation(self, api_transport):
        source_uri = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/batch_prediction_prompts1.jsonl"
        destination_uri_prefix = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/predictions/text-bison@001_"

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = TextGenerationModel.from_pretrained("text-bison@001")
        job = model.batch_predict(
            dataset=source_uri,
            destination_uri_prefix=destination_uri_prefix,
            model_parameters={"temperature": 0, "top_p": 1, "top_k": 5},
        )

        job.wait_for_resource_creation()
        job.wait()
        gapic_job = job._gca_resource
        job.delete()

        assert gapic_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_batch_prediction_for_textembedding(self, api_transport):
        source_uri = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/batch_prediction_prompts_textembedding_dummy1.jsonl"
        destination_uri_prefix = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/predictions/textembedding-gecko@001_"

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
        job = model.batch_predict(
            dataset=source_uri,
            destination_uri_prefix=destination_uri_prefix,
            model_parameters={},
        )

        job.wait_for_resource_creation()
        job.wait()
        gapic_job = job._gca_resource
        job.delete()

        assert gapic_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_batch_prediction_for_code_generation(self, api_transport):
        source_uri = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/code-bison.batch_prediction_prompts.1.jsonl"
        destination_uri_prefix = "gs://ucaip-samples-us-central1/model/llm/batch_prediction/predictions/code-bison@001_"

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = CodeGenerationModel.from_pretrained("code-bison@001")
        job = model.batch_predict(
            dataset=source_uri,
            destination_uri_prefix=destination_uri_prefix,
            model_parameters={"temperature": 0},
        )

        job.wait_for_resource_creation()
        job.wait()
        gapic_job = job._gca_resource
        job.delete()

        assert gapic_job.state == gca_job_state.JobState.JOB_STATE_SUCCEEDED

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_code_generation_streaming(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        model = language_models.CodeGenerationModel.from_pretrained("code-bison@001")

        for response in model.predict_streaming(
            prefix="def reverse_string(s):",
            # code-bison does not support suffix
            # suffix="    return s",
            max_output_tokens=128,
            temperature=0.0,
        ):
            assert response.text

    @pytest.mark.parametrize("api_transport", ["grpc", "rest"])
    def test_code_chat_model_send_message_streaming(self, api_transport):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport=api_transport,
        )

        chat_model = language_models.CodeChatModel.from_pretrained("codechat-bison@001")
        chat = chat_model.start_chat()

        message1 = "Please help write a function to calculate the max of two numbers"
        for response in chat.send_message_streaming(message1):
            assert response.text
