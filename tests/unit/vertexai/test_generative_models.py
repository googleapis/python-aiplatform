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
from typing import Iterable, MutableSequence, Optional
from unittest import mock

import vertexai
from google.cloud.aiplatform import initializer
from vertexai import generative_models
from vertexai.preview import generative_models as preview_generative_models
from vertexai.generative_models._generative_models import (
    prediction_service,
    gapic_prediction_service_types,
    gapic_content_types,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_RESPONSE_TEXT_PART_STRUCT = {
    "text": "The sky appears blue due to a phenomenon called Rayleigh scattering."
}

_RESPONSE_FUNCTION_CALL_PART_STRUCT = {
    "function_call": {
        "name": "get_current_weather",
        "args": {
            "fields": {
                "key": "location",
                "value": {"string_value": "Boston"},
            }
        },
    }
}

_RESPONSE_AFTER_FUNCTION_CALL_PART_STRUCT = {
    "text": "The weather in Boston is super nice!"
}

_RESPONSE_SAFETY_RATINGS_STRUCT = [
    {"category": "HARM_CATEGORY_HARASSMENT", "probability": "NEGLIGIBLE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "probability": "NEGLIGIBLE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "probability": "NEGLIGIBLE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "probability": "NEGLIGIBLE"},
]

_RESPONSE_CITATION_STRUCT = {
    "start_index": 528,
    "end_index": 656,
    "uri": "https://www.quora.com/What-makes-the-sky-blue-during-the-day",
}


_REQUEST_TOOL_STRUCT = {
    "function_declarations": [
        {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit",
                        ],
                    },
                },
                "required": ["location"],
            },
        }
    ]
}

_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT = {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA",
        },
        "unit": {
            "type": "string",
            "enum": [
                "celsius",
                "fahrenheit",
            ],
        },
    },
    "required": ["location"],
}


def mock_generate_content(
    self,
    request: gapic_prediction_service_types.GenerateContentRequest,
    *,
    model: Optional[str] = None,
    contents: Optional[MutableSequence[gapic_content_types.Content]] = None,
) -> Iterable[gapic_prediction_service_types.GenerateContentResponse]:
    last_message_part = request.contents[-1].parts[0]
    should_fail = last_message_part.text and "Please fail" in last_message_part.text
    if should_fail:
        response = gapic_prediction_service_types.GenerateContentResponse(
            candidates=[
                gapic_content_types.Candidate(
                    finish_reason=gapic_content_types.Candidate.FinishReason.SAFETY,
                    finish_message="Failed due to: " + last_message_part.text,
                    safety_ratings=[
                        gapic_content_types.SafetyRating(rating)
                        for rating in _RESPONSE_SAFETY_RATINGS_STRUCT
                    ],
                ),
            ],
        )
        return response

    is_continued_chat = len(request.contents) > 1
    has_retrieval = any(
        tool.retrieval or tool.google_search_retrieval for tool in request.tools
    )
    has_function_declarations = any(
        tool.function_declarations for tool in request.tools
    )
    has_function_request = any(
        content.parts[0].function_call for content in request.contents
    )
    has_function_response = any(
        content.parts[0].function_response for content in request.contents
    )

    if has_function_request:
        assert has_function_response

    if has_function_response:
        assert has_function_request
        assert has_function_declarations

    if has_function_declarations:
        needs_function_call = not has_function_response
        if needs_function_call:
            response_part_struct = _RESPONSE_FUNCTION_CALL_PART_STRUCT
        else:
            response_part_struct = _RESPONSE_AFTER_FUNCTION_CALL_PART_STRUCT
    elif is_continued_chat:
        response_part_struct = {"text": "Other planets may have different sky color."}
    else:
        response_part_struct = _RESPONSE_TEXT_PART_STRUCT

    response = gapic_prediction_service_types.GenerateContentResponse(
        candidates=[
            gapic_content_types.Candidate(
                index=0,
                content=gapic_content_types.Content(
                    # Model currently does not identify itself
                    # role="model",
                    parts=[
                        gapic_content_types.Part(response_part_struct),
                    ],
                ),
                finish_reason=gapic_content_types.Candidate.FinishReason.STOP,
                safety_ratings=[
                    gapic_content_types.SafetyRating(rating)
                    for rating in _RESPONSE_SAFETY_RATINGS_STRUCT
                ],
                citation_metadata=gapic_content_types.CitationMetadata(
                    citations=[
                        gapic_content_types.Citation(_RESPONSE_CITATION_STRUCT),
                    ]
                ),
                grounding_metadata=gapic_content_types.GroundingMetadata(
                    web_search_queries=[request.contents[0].parts[0].text],
                    grounding_attributions=[
                        gapic_content_types.GroundingAttribution(
                            segment=gapic_content_types.Segment(
                                start_index=0,
                                end_index=67,
                            ),
                            confidence_score=0.69857746,
                            web=gapic_content_types.GroundingAttribution.Web(
                                uri="https://math.ucr.edu/home/baez/physics/General/BlueSky/blue_sky.html",
                                title="Why is the sky blue? - UCR Math",
                            ),
                        ),
                    ],
                )
                if has_retrieval and request.contents[0].parts[0].text
                else None,
            ),
        ],
    )
    return response


def mock_stream_generate_content(
    self,
    request: gapic_prediction_service_types.GenerateContentRequest,
    *,
    model: Optional[str] = None,
    contents: Optional[MutableSequence[gapic_content_types.Content]] = None,
) -> Iterable[gapic_prediction_service_types.GenerateContentResponse]:
    yield mock_generate_content(
        self=self, request=request, model=model, contents=contents
    )


@pytest.mark.usefixtures("google_auth_mock")
class TestGenerativeModels:
    """Unit tests for the generative models."""

    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content(self, generative_models: generative_models):
        model = generative_models.GenerativeModel("gemini-pro")
        response = model.generate_content("Why is sky blue?")
        assert response.text

        response2 = model.generate_content(
            "Why is sky blue?",
            generation_config=generative_models.GenerationConfig(
                temperature=0.2,
                top_p=0.9,
                top_k=20,
                candidate_count=1,
                max_output_tokens=200,
                stop_sequences=["\n\n\n"],
            ),
        )
        assert response2.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="stream_generate_content",
        new=mock_stream_generate_content,
    )
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_streaming(self, generative_models: generative_models):
        model = generative_models.GenerativeModel("gemini-pro")
        stream = model.generate_content("Why is sky blue?", stream=True)
        for chunk in stream:
            assert chunk.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_send_message(self, generative_models: generative_models):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response1 = chat.send_message("Why is sky blue?")
        assert response1.text
        response2 = chat.send_message("Is sky blue on other planets?")
        assert response2.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_send_message_response_validation_errors(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response1 = chat.send_message("Why is sky blue?")
        assert response1.text
        assert len(chat.history) == 2

        with pytest.raises(generative_models.ResponseValidationError):
            chat.send_message("Please fail!")
        # Checking that history did not get updated
        assert len(chat.history) == 2

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_function_calling(self, generative_models: generative_models):
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
        )
        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        model = generative_models.GenerativeModel(
            "gemini-pro",
            # Specifying the tools once to avoid specifying them in every request
            tools=[weather_tool],
        )
        chat = model.start_chat()

        response1 = chat.send_message("What is the weather like in Boston?")
        assert (
            response1.candidates[0].content.parts[0].function_call.name
            == "get_current_weather"
        )
        response2 = chat.send_message(
            generative_models.Part.from_function_response(
                name="get_current_weather",
                response={
                    "content": {"weather_there": "super nice"},
                },
            ),
        )
        assert response2.text == "The weather in Boston is super nice!"

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_conversion_methods(self, generative_models: generative_models):
        """Tests the .to_dict, .from_dict and __repr__ methods"""
        model = generative_models.GenerativeModel("gemini-pro")
        response = model.generate_content("Why is sky blue?")

        response_new = generative_models.GenerationResponse.from_dict(
            response.to_dict()
        )
        assert repr(response_new) == repr(response)

        for candidate in response.candidates:
            candidate_new = generative_models.Candidate.from_dict(candidate.to_dict())
            assert repr(candidate_new) == repr(candidate)

            content = candidate.content
            content_new = generative_models.Content.from_dict(content.to_dict())
            assert repr(content_new) == repr(content)

            for part in content.parts:
                part_new = generative_models.Part.from_dict(part.to_dict())
                assert repr(part_new) == repr(part)

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    def test_generate_content_grounding_google_search_retriever(self):
        model = preview_generative_models.GenerativeModel("gemini-pro")
        google_search_retriever_tool = (
            preview_generative_models.Tool.from_google_search_retrieval(
                preview_generative_models.grounding.GoogleSearchRetrieval(
                    disable_attribution=False
                )
            )
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[google_search_retriever_tool]
        )
        assert response.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    def test_generate_content_grounding_vertex_ai_search_retriever(self):
        model = preview_generative_models.GenerativeModel("gemini-pro")
        google_search_retriever_tool = preview_generative_models.Tool.from_retrieval(
            retrieval=preview_generative_models.grounding.Retrieval(
                source=preview_generative_models.grounding.VertexAISearch(
                    datastore=f"projects/{_TEST_PROJECT}/locations/global/collections/default_collection/dataStores/test-datastore",
                )
            )
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[google_search_retriever_tool]
        )
        assert response.text
