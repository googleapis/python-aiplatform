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
from vertexai.preview import (
    generative_models as preview_generative_models,
)
from vertexai.generative_models._generative_models import (
    prediction_service,
    gapic_prediction_service_types,
    gapic_content_types,
    gapic_tool_types,
)
from vertexai.generative_models import _function_calling_utils


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_RESPONSE_TEXT_PART_STRUCT = {
    "text": "The sky appears blue due to a phenomenon called Rayleigh scattering."
}

_RESPONSE_FUNCTION_CALL_PART_STRUCT = {
    "function_call": {
        "name": "get_current_weather",
        "args": {
            "location": "Boston",
        },
    }
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

    should_block = (
        last_message_part.text
        and "Please block with block_reason=OTHER" in last_message_part.text
    )
    if should_block:
        response = gapic_prediction_service_types.GenerateContentResponse(
            candidates=[],
            prompt_feedback=gapic_prediction_service_types.GenerateContentResponse.PromptFeedback(
                block_reason=gapic_prediction_service_types.GenerateContentResponse.PromptFeedback.BlockedReason.OTHER,
                block_reason_message="Blocked for testing",
            ),
        )
        return response

    is_continued_chat = len(request.contents) > 1
    has_retrieval = any(
        tool.retrieval or tool.google_search_retrieval for tool in request.tools
    )
    has_function_declarations = any(
        tool.function_declarations for tool in request.tools
    )
    had_any_function_calls = any(
        content.parts[0].function_call for content in request.contents
    )
    had_any_function_responses = any(
        content.parts[0].function_response for content in request.contents
    )
    latest_user_message_function_responses = [
        part.function_response
        for part in request.contents[-1].parts
        if part.function_response
    ]

    if had_any_function_calls:
        assert had_any_function_responses

    if had_any_function_responses:
        assert had_any_function_calls
        assert has_function_declarations

    if has_function_declarations and not had_any_function_calls:
        # response_part_struct = _RESPONSE_FUNCTION_CALL_PART_STRUCT
        # Workaround for the proto library bug
        response_part_struct = dict(
            function_call=gapic_tool_types.FunctionCall(
                name="get_current_weather",
                args={"location": "Boston"},
            )
        )
    elif has_function_declarations and latest_user_message_function_responses:
        function_response = latest_user_message_function_responses[0]
        function_response_dict = type(function_response).to_dict(function_response)
        function_response_response_dict = function_response_dict["response"]
        response_part_struct = {
            "text": f"The weather in Boston is {function_response_response_dict}"
        }
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


def get_current_weather(location: str, unit: Optional[str] = "centigrade"):
    """Gets weather in the specified location.

    Args:
        location: The location for which to get the weather.
        unit: Temperature unit. Can be Centigrade or Fahrenheit. Default: Centigrade.

    Returns:
        The weather information as a dict.
    """
    return dict(
        location=location,
        unit=unit,
        weather="Super nice, but maybe a bit hot.",
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
    def test_chat_send_message_response_blocked_errors(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response1 = chat.send_message("Why is sky blue?")
        assert response1.text
        assert len(chat.history) == 2

        with pytest.raises(generative_models.ResponseValidationError) as e:
            chat.send_message("Please block with block_reason=OTHER.")

        assert e.match("Blocked for testing")
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
        assert [
            function_call.name
            for function_call in response1.candidates[0].function_calls
        ] == ["get_current_weather"]
        function_map = {
            "get_current_weather": get_current_weather,
        }
        function_response_parts = []
        for function_call in response1.candidates[0].function_calls:
            function = function_map[function_call.name]
            function_result = function(**function_call.args)
            function_response_part = generative_models.Part.from_function_response(
                name=function_call.name,
                response=function_result,
            )
            function_response_parts.append(function_response_part)

        response2 = chat.send_message(function_response_parts)
        assert "Boston" in response2.text
        assert "nice" in response2.text
        assert not response2.candidates[0].function_calls

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
        """Tests the .to_dict, .from_dict and __repr__ methods."""
        # Testing on a full chat conversation which includes function calling
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
        )
        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        model = generative_models.GenerativeModel("gemini-pro", tools=[weather_tool])
        chat = model.start_chat()
        response = chat.send_message("What is the weather like in Boston?")
        chat.send_message(
            generative_models.Part.from_function_response(
                name="get_current_weather",
                response={
                    "location": "Boston",
                    "weather": "super nice",
                },
            ),
        )

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

        # Checking the history which contains different Part types
        for content in chat.history:
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

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    def test_chat_automatic_function_calling(self):
        generative_models = preview_generative_models
        get_current_weather_func = generative_models.FunctionDeclaration.from_func(
            get_current_weather
        )
        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        model = generative_models.GenerativeModel(
            "gemini-pro",
            # Specifying the tools once to avoid specifying them in every request
            tools=[weather_tool],
        )
        afc_responder = generative_models.AutomaticFunctionCallingResponder(
            max_automatic_function_calls=5,
        )
        chat = model.start_chat(responder=afc_responder)

        response1 = chat.send_message("What is the weather like in Boston?")
        assert response1.text.startswith("The weather in Boston is")
        assert "nice" in response1.text
        assert len(chat.history) == 4
        assert chat.history[-3].parts[0].function_call
        assert chat.history[-2].parts[0].function_response

        # Test max_automatic_function_calls:
        # Setting the AFC limit to 0 to test the error handling
        afc_responder._max_automatic_function_calls = 0
        chat2 = model.start_chat(responder=afc_responder)
        with pytest.raises(RuntimeError) as err:
            chat2.send_message("What is the weather like in Boston?")
        assert err.match("Exceeded the maximum")


EXPECTED_SCHEMA_FOR_GET_CURRENT_WEATHER = {
    "title": "get_current_weather",
    "type": "object",
    "description": "Gets weather in the specified location.",
    "properties": {
        "location": {
            "title": "Location",
            "type": "string",
            "description": "The location for which to get the weather.",
        },
        "unit": {
            "title": "Unit",
            "type": "string",
            "description": "Temperature unit. Can be Centigrade or Fahrenheit. Default: Centigrade.",
            "default": "centigrade",
            "nullable": True,
        },
    },
    "required": ["location"],
}


class TestFunctionCallingUtils:
    def test_generate_json_schema_for_callable(self):
        test_cases = [
            (get_current_weather, EXPECTED_SCHEMA_FOR_GET_CURRENT_WEATHER),
        ]
        for function, expected_schema in test_cases:
            schema = _function_calling_utils.generate_json_schema_from_function(
                function
            )
            function_name = schema["title"]
            function_description = schema["description"]
            assert schema == expected_schema

            fixed_schema = (
                _function_calling_utils.adapt_json_schema_to_google_tool_schema(schema)
            )
            assert fixed_schema
            assert "type" in fixed_schema
            assert "description" in fixed_schema
            assert "properties" in fixed_schema
            assert "required" in fixed_schema
            function_declaration = generative_models.FunctionDeclaration(
                name=function_name,
                description=function_description,
                parameters=fixed_schema,
            )
            assert function_declaration
