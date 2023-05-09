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

# pylint: disable=protected-access,bad-continuation

import pytest

from importlib import reload
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform.compat.services import (
    model_garden_service_client_v1beta1,
)
from google.cloud.aiplatform.compat.services import prediction_service_client
from google.cloud.aiplatform.compat.types import (
    prediction_service as gca_prediction_service,
)
from google.cloud.aiplatform_v1beta1.types import (
    publisher_model as gca_publisher_model,
)

from vertexai.preview import language_models


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEXT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/text-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/text-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_generation_1.0.0.yaml",
    },
}

_CHAT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/chat-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/chat-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/chat_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/chat_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/chat_generation_1.0.0.yaml",
    },
}

_TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/textembedding-gecko",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/chat-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_embedding_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_embedding_1.0.0.yaml",
    },
}

_TEST_TEXT_GENERATION_PREDICTION = {
    "safetyAttributes": {
        "categories": ["Violent"],
        "blocked": False,
        "scores": [0.10000000149011612],
    },
    "content": """
Ingredients:
* 3 cups all-purpose flour

Instructions:
1. Preheat oven to 350 degrees F (175 degrees C).""",
}

_TEST_CHAT_GENERATION_PREDICTION1 = {
    "safetyAttributes": {
        "scores": [],
        "blocked": False,
        "categories": [],
    },
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 1",
        }
    ],
}
_TEST_CHAT_GENERATION_PREDICTION2 = {
    "safetyAttributes": {
        "scores": [],
        "blocked": False,
        "categories": [],
    },
    "candidates": [
        {
            "author": "1",
            "content": "Chat response 2",
        }
    ],
}

_TEXT_EMBEDDING_VECTOR_LENGTH = 768
_TEST_TEXT_EMBEDDING_PREDICTION = {
    "embeddings": {
        "values": list([1.0] * _TEXT_EMBEDDING_VECTOR_LENGTH),
    }
}


@pytest.mark.usefixtures("google_auth_mock")
class TestLanguageModels:
    """Unit tests for the language models."""

    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_text_generation(self):
        """Tests the text generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.TextGenerationModel.from_pretrained(
                "google/text-bison@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/text-bison@001", retry=base._DEFAULT_RETRY
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_TEXT_GENERATION_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            response = model.predict(
                "What is the best recipe for banana bread? Recipe:",
                max_output_tokens=128,
                temperature=0,
                top_p=1,
                top_k=5,
            )

        assert response.text == _TEST_TEXT_GENERATION_PREDICTION["content"]

    def test_chat(self):
        """Tests the chat generation model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _CHAT_BISON_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.ChatModel.from_pretrained("google/chat-bison@001")

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/chat-bison@001", retry=base._DEFAULT_RETRY
        )

        chat = model.start_chat(
            context="""
            My name is Ned.
            You are my personal assistant.
            My favorite movies are Lord of the Rings and Hobbit.
            """,
            examples=[
                language_models.InputOutputTextPair(
                    input_text="Who do you work for?",
                    output_text="I work for Ned.",
                ),
                language_models.InputOutputTextPair(
                    input_text="What do I like?",
                    output_text="Ned likes watching movies.",
                ),
            ],
            temperature=0.0,
        )

        gca_predict_response1 = gca_prediction_service.PredictResponse()
        gca_predict_response1.predictions.append(_TEST_CHAT_GENERATION_PREDICTION1)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response1,
        ):
            response = chat.send_message(
                "Are my favorite movies based on a book series?"
            )
            assert (
                response.text
                == _TEST_CHAT_GENERATION_PREDICTION1["candidates"][0]["content"]
            )
            assert len(chat._history) == 1

        gca_predict_response2 = gca_prediction_service.PredictResponse()
        gca_predict_response2.predictions.append(_TEST_CHAT_GENERATION_PREDICTION2)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response2,
        ):
            response = chat.send_message(
                "When where these books published?",
                temperature=0.1,
            )
            assert (
                response.text
                == _TEST_CHAT_GENERATION_PREDICTION2["candidates"][0]["content"]
            )
            assert len(chat._history) == 2

    def test_text_embedding(self):
        """Tests the text embedding model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with mock.patch.object(
            target=model_garden_service_client_v1beta1.ModelGardenServiceClient,
            attribute="get_publisher_model",
            return_value=gca_publisher_model.PublisherModel(
                _TEXT_EMBEDDING_GECKO_PUBLISHER_MODEL_DICT
            ),
        ) as mock_get_publisher_model:
            model = language_models.TextEmbeddingModel.from_pretrained(
                "google/textembedding-gecko@001"
            )

        mock_get_publisher_model.assert_called_once_with(
            name="publishers/google/models/textembedding-gecko@001",
            retry=base._DEFAULT_RETRY,
        )

        gca_predict_response = gca_prediction_service.PredictResponse()
        gca_predict_response.predictions.append(_TEST_TEXT_EMBEDDING_PREDICTION)

        with mock.patch.object(
            target=prediction_service_client.PredictionServiceClient,
            attribute="predict",
            return_value=gca_predict_response,
        ):
            embeddings = model.get_embeddings(["What is life?"])
            assert embeddings
            for embedding in embeddings:
                vector = embedding.values
                assert len(vector) == _TEXT_EMBEDDING_VECTOR_LENGTH
                assert vector == _TEST_TEXT_EMBEDDING_PREDICTION["embeddings"]["values"]
