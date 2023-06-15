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

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from vertexai.preview.language_models import (
    ChatModel,
    InputOutputTextPair,
    TextGenerationModel,
    TextEmbeddingModel,
)


class TestLanguageModels(e2e_base.TestEndToEnd):
    """System tests for language models."""

    _temp_prefix = "temp_language_models_test_"

    def test_text_generation(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = TextGenerationModel.from_pretrained("google/text-bison@001")

        assert model.predict(
            "What is the best recipe for banana bread? Recipe:",
            max_output_tokens=128,
            temperature=0,
            top_p=1,
            top_k=5,
        ).text

    def test_chat_on_chat_model(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

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

        assert chat.send_message("Are my favorite movies based on a book series?").text
        assert len(chat._history) == 1
        assert chat.send_message(
            "When where these books published?",
            temperature=0.1,
        ).text
        assert len(chat._history) == 2

    def test_text_embedding(self):
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = TextEmbeddingModel.from_pretrained("google/textembedding-gecko@001")
        embeddings = model.get_embeddings(["What is life?"])
        assert embeddings
        for embedding in embeddings:
            vector = embedding.values
            assert len(vector) == 768

    def test_tuning(self, shared_state):
        """Test tuning, listing and loading models."""
        aiplatform.init(project=e2e_base._PROJECT, location=e2e_base._LOCATION)

        model = TextGenerationModel.from_pretrained("google/text-bison@001")

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

        model.tune_model(
            training_data=training_data,
            train_steps=1,
            tuning_job_location="europe-west4",
            tuned_model_location="us-central1",
        )
        # According to the Pipelines design, external resources created by a pipeline
        # must not be modified or deleted. Otherwise caching will break next pipeline runs.
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(model._endpoint)
        shared_state["resources"].extend(
            aiplatform.Model(model_name=deployed_model.model)
            for deployed_model in model._endpoint.list_models()
        )
        # Deleting the Endpoint is a little less bad since the LLM SDK will recreate it, but it's not advised for the same reason.

        response = model.predict(
            "What is the best recipe for banana bread? Recipe:",
            max_output_tokens=128,
            temperature=0,
            top_p=1,
            top_k=5,
        )
        assert response.text

        tuned_model_names = model.list_tuned_model_names()
        assert tuned_model_names
        tuned_model_name = tuned_model_names[0]

        tuned_model = TextGenerationModel.get_tuned_model(tuned_model_name)

        tuned_model_response = tuned_model.predict(
            "What is the best recipe for banana bread? Recipe:",
            max_output_tokens=128,
            temperature=0,
            top_p=1,
            top_k=5,
        )
        assert tuned_model_response.text
