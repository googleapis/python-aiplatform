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
from unittest import mock
from typing import Iterable, MutableSequence, Optional, Union

from google.cloud.aiplatform import initializer


import vertexai
from vertexai.preview import generative_models
from vertexai.generative_models import _generative_models
from vertexai.generative_models._generative_models import (
    prediction_service, prediction_service_types, content_types, tool_types
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_RESPONSE_TEXT_PART_STRUCT = {
    "text": "The sky appears blue due to a phenomenon called Rayleigh scattering. This scattering effect is caused by the interaction of sunlight with molecules in the Earth\'s atmosphere, primarily nitrogen and oxygen molecules. Here\'s a detailed explanation:\n\n1. **Sunlight and the Electromagnetic Spectrum:**\n   - Sunlight is composed of a spectrum of electromagnetic waves, including visible light, ultraviolet light, and infrared light. Visible light is the portion of the spectrum that our eyes can detect and perceive as colors.\n\n2. **Rayleigh Scattering:**\n   - Rayleigh scattering is the scattering of light by particles that are much smaller than the wavelength of light. In the case of the sky, the particles responsible for scattering are nitrogen and oxygen molecules in the atmosphere.\n   - When sunlight enters the atmosphere, it encounters these molecules and interacts with them. The shorter wavelength components of visible light, such as blue and violet light, are more likely to be scattered by these molecules due to their shorter wavelengths.\n\n3. **Scattering Angle:**\n   - The amount of scattering depends on the angle at which the light is scattered. Blue light is scattered more in the forward direction, meaning it is scattered more directly towards the observer\'s eyes.\n\n4. **Apparent Color of the Sky:**\n   - As a result of Rayleigh scattering, more blue light is scattered towards our eyes from all directions in the sky. This means that when we look up at the sky, we see more blue light than other colors, making the sky appear blue.\n\n5. **Variations in Sky Color:**\n   - The intensity of the blue color of the sky can vary depending on several factors, such as the time of day, the angle of the sun, and the amount of pollution or particles in the atmosphere.\n   - At sunrise and sunset, when the sunlight has to travel through more of the atmosphere, more blue light is scattered away from our eyes, leaving more red and orange light to reach us, which is why the sky appears red or orange during these times.\n   - Pollution and particles in the atmosphere can also affect the color of the sky by scattering and absorbing light, leading to variations in the intensity and hue of the blue color."
}

_RESPONSE_FUNCTION_CALL_PART_STRUCT = {
    "function_call": {
        "name": "get_current_weather",
        "args": {
            "fields": {
                "key": "location",
                "value": {
                    "string_value": "Boston"
                },
            }
        },
    }
}

_RESPONSE_AFTER_FUNCTION_CALL_PART_STRUCT = {
    "text": "The weather in Boston is super nice!"
}

_RESPONSE_SAFETY_RATINGS_STRUCT = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "probability": "NEGLIGIBLE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "probability": "NEGLIGIBLE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "probability": "NEGLIGIBLE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "probability": "NEGLIGIBLE"
    }
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
                        "description": "The city and state, e.g. San Francisco, CA"
                    },
                    "unit": {
                        "type": "string",
                        "enum": [
                            "celsius",
                            "fahrenheit",
                        ]
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    ]
}

_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT = {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
            "description": "The city and state, e.g. San Francisco, CA"
        },
        "unit": {
            "type": "string",
            "enum": [
                "celsius",
                "fahrenheit",
            ]
        }
    },
    "required": [
        "location"
    ],
}


def mock_stream_generate_content(
    self,
    request: prediction_service_types.GenerateContentRequest,
    *,
    model: Optional[str] = None,
    contents: Optional[MutableSequence[content_types.Content]] = None,
) -> Iterable[prediction_service_types.GenerateContentResponse]:
    is_continued_chat = len(request.contents) > 1
    has_tools = bool(request.tools)

    if has_tools:
        has_function_response = any(
            "function_response" in content.parts[0]
            for content in request.contents
        )
        needs_function_call = not has_function_response
        if needs_function_call:
            response_part_struct = _RESPONSE_FUNCTION_CALL_PART_STRUCT
        else:
            response_part_struct = _RESPONSE_AFTER_FUNCTION_CALL_PART_STRUCT
    elif is_continued_chat:
        response_part_struct = {
            "text": "Other planets may have different sky color."
        }
    else:
        response_part_struct = _RESPONSE_TEXT_PART_STRUCT

    response = prediction_service_types.GenerateContentResponse(
        candidates=[
            content_types.Candidate(
                index=0,
                content=content_types.Content(
                    # Model currently does not identify itself
                    # role="model",
                    parts=[
                        content_types.Part(response_part_struct),
                    ],
                ),
                finish_reason=content_types.Candidate.FinishReason.STOP,
                safety_ratings=[
                    content_types.SafetyRating(rating)
                    for rating in _RESPONSE_SAFETY_RATINGS_STRUCT
                ],
                citation_metadata=content_types.CitationMetadata(
                    citations=[
                        content_types.Citation(
                            _RESPONSE_CITATION_STRUCT
                        ),
                    ]
                ),
            ),
        ],
    )
    yield response


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
        attribute="stream_generate_content",
        new=mock_stream_generate_content,
    )
    def test_generate_content(self):
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
            )
        )
        assert response2.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="stream_generate_content",
        new=mock_stream_generate_content,
    )
    def test_generate_content_streaming(self):
        model = generative_models.GenerativeModel("gemini-pro")
        stream = model.generate_content("Why is sky blue?", stream=True)
        for chunk in stream:
            assert chunk.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="stream_generate_content",
        new=mock_stream_generate_content,
    )
    def test_chat_send_message(self):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response1 = chat.send_message("Why is sky blue?")
        assert response1.text
        response2 = chat.send_message("Is sky blue on other planets?")
        assert response2.text

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="stream_generate_content",
        new=mock_stream_generate_content,
    )
    def test_chat_function_calling(self):
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
                }
            ),
        )
        assert response2.text == "The weather in Boston is super nice!"
