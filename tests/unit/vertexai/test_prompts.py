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
"""Unit tests for generative model prompts."""
# pylint: disable=protected-access,bad-continuation

from vertexai.generative_models._prompts import Prompt
from vertexai.generative_models import (
    Content,
    Part,
    Image,
    GenerationConfig,
    SafetySetting,
)


import io
import pytest

from unittest import mock
from typing import Any, List, MutableSequence, Optional

# TODO(b/360932655): Use mock_generate_content from test_generative_models
from vertexai.preview import rag
from vertexai.generative_models._generative_models import (
    prediction_service_v1 as prediction_service,
    types_v1 as gapic_prediction_service_types,
    types_v1 as gapic_content_types,
    types_v1 as gapic_tool_types,
)


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
) -> gapic_prediction_service_types.GenerateContentResponse:
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
    has_rag_retrieval = any(
        isinstance(tool.retrieval, rag.Retrieval) for tool in request.tools
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

    if has_retrieval and (not has_rag_retrieval) and request.contents[0].parts[0].text:
        grounding_metadata = gapic_content_types.GroundingMetadata(
            web_search_queries=[request.contents[0].parts[0].text],
        )
    elif has_rag_retrieval and request.contents[0].parts[0].text:
        grounding_metadata = gapic_content_types.GroundingMetadata(
            retrieval_queries=[request.contents[0].parts[0].text],
        )
    else:
        grounding_metadata = None

    response_part = gapic_content_types.Part(response_part_struct)
    finish_reason = gapic_content_types.Candidate.FinishReason.STOP

    # Handling the max_output_tokens limit
    if response_part.text:
        if request.generation_config.max_output_tokens:
            tokens = response_part.text.split()
            if len(tokens) >= request.generation_config.max_output_tokens:
                tokens = tokens[: request.generation_config.max_output_tokens]
                response_part.text = " ".join(tokens)
                finish_reason = gapic_content_types.Candidate.FinishReason.MAX_TOKENS

    response = gapic_prediction_service_types.GenerateContentResponse(
        candidates=[
            gapic_content_types.Candidate(
                index=0,
                content=gapic_content_types.Content(
                    role="model",
                    parts=[response_part],
                ),
                finish_reason=finish_reason,
                safety_ratings=[
                    gapic_content_types.SafetyRating(rating)
                    for rating in _RESPONSE_SAFETY_RATINGS_STRUCT
                ],
                citation_metadata=gapic_content_types.CitationMetadata(
                    citations=[
                        gapic_content_types.Citation(_RESPONSE_CITATION_STRUCT),
                    ]
                ),
                grounding_metadata=grounding_metadata,
            ),
        ],
    )

    if "Please block response with finish_reason=OTHER" in (
        last_message_part.text or ""
    ):
        finish_reason = gapic_content_types.Candidate.FinishReason.OTHER
        response.candidates[0].finish_reason = finish_reason

    request_token_count = sum(
        len(gapic_content_types.Content.to_json(content).split())
        for content in request.contents
    )
    response_token_count = sum(
        len(gapic_content_types.Content.to_json(candidate.content).split())
        for candidate in response.candidates
    )
    response.usage_metadata.prompt_token_count = request_token_count
    response.usage_metadata.candidates_token_count = response_token_count
    response.usage_metadata.total_token_count = (
        request_token_count + response_token_count
    )

    return response


def is_list_of_type(obj: Any, T: Any) -> bool:
    return isinstance(obj, list) and all(isinstance(s, T) for s in obj)


def assert_prompt_contents_equal(
    prompt_contents: List[Content],
    expected_prompt_contents: List[Content],
) -> None:
    assert len(prompt_contents) == len(expected_prompt_contents)
    for i in range(len(prompt_contents)):
        assert prompt_contents[i].role == expected_prompt_contents[i].role
        assert len(prompt_contents[i].parts) == len(expected_prompt_contents[i].parts)
        for j in range(len(prompt_contents[i].parts)):
            assert (
                prompt_contents[i].parts[j]._raw_part.text
                == expected_prompt_contents[i].parts[j]._raw_part.text
            )


def create_image():
    # Importing external library lazily to reduce the scope of import errors.
    from PIL import Image as PIL_Image  # pylint: disable=g-import-not-at-top

    pil_image: PIL_Image.Image = PIL_Image.new(mode="RGB", size=(200, 200))
    image_bytes_io = io.BytesIO()
    pil_image.save(image_bytes_io, format="jpeg")
    return Image.from_bytes(image_bytes_io.getvalue())


@pytest.mark.usefixtures("google_auth_mock")
class TestPrompt:
    """Unit tests for generative model prompts."""

    def test_string_prompt_constructor_string_variables(self):
        # Create string prompt with string only variable values
        prompt = Prompt(
            prompt_data="Rate the movie {movie1}",
            variables=[
                {
                    "movie1": "The Avengers",
                }
            ],
        )
        # String prompt data should remain as string before compilation
        assert prompt.prompt_data == "Rate the movie {movie1}"
        # Variables values should be converted to List[Part]
        assert is_list_of_type(prompt.variables[0]["movie1"], Part)

    def test_string_prompt_constructor_part_variables(self):
        # Create string prompt with List[Part] variable values
        prompt = Prompt(
            prompt_data="Rate the movie {movie1}",
            variables=[
                {
                    "movie1": [Part.from_text("The Avengers")],
                }
            ],
        )
        # Variables values should be converted to List[Part]
        assert is_list_of_type(prompt.variables[0]["movie1"], Part)

    def test_string_prompt_constructor_invalid_variables(self):
        # String prompt variables must be PartsType
        with pytest.raises(TypeError):
            Prompt(
                prompt_data="Rate the movie {movie1}",
                variables=[
                    {
                        "movie1": 12345,
                    }
                ],
            )

    def test_partstype_prompt_constructor(self):
        image = create_image()
        # Create PartsType prompt with List[Part] variable values
        prompt_data = [
            "Compare the movie posters for The Avengers and {movie2}: ",
            image,
            "{movie2_poster}",
        ]
        prompt = Prompt(
            prompt_data=prompt_data,
            variables=[{"movie2": "Frozen", "movie2_poster": [Part.from_image(image)]}],
        )
        # Variables values should be List[Part]
        assert is_list_of_type(prompt.variables[0]["movie2"], Part)
        assert is_list_of_type(prompt.variables[0]["movie2_poster"], Part)

    def test_string_prompt_assemble_contents(self):
        prompt = Prompt(
            prompt_data="Which movie is better, {movie1} or {movie2}?",
            variables=[
                {
                    "movie1": "The Avengers",
                    "movie2": "Frozen",
                }
            ],
        )
        assembled_prompt_content = prompt.assemble_contents(**prompt.variables[0])
        expected_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, The Avengers or Frozen?"),
                ],
                role="user",
            )
        ]
        assert_prompt_contents_equal(assembled_prompt_content, expected_content)

    def test_partstype_prompt_assemble_contents(self):
        image1 = create_image()
        image2 = create_image()
        prompt_data = [
            "Compare the movie posters for The Avengers and {movie2}: ",
            image1,
            "{movie2_poster}",
        ]
        prompt = Prompt(
            prompt_data=prompt_data,
            variables=[
                {
                    "movie2": "Frozen",
                    "movie2_poster": [Part.from_image(image=image2)],
                }
            ],
        )

        # Check assembled prompt content
        assembled_prompt_content = prompt.assemble_contents(**prompt.variables[0])
        expected_content = [
            Content(
                parts=[
                    Part.from_text(
                        "Compare the movie posters for The Avengers and Frozen: "
                    ),
                    Part.from_image(image=image1),
                    Part.from_image(image=image2),
                ],
                role="user",
            )
        ]
        assert_prompt_contents_equal(assembled_prompt_content, expected_content)

    def test_string_prompt_partial_assemble_contents(self):
        prompt = Prompt(
            prompt_data="Which movie is better, {movie1} or {movie2}?",
            variables=[
                {
                    "movie1": "The Avengers",
                }
            ],
        )

        # Check partially assembled prompt content
        assembled1_prompt_content = prompt.assemble_contents(**prompt.variables[0])
        expected1_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, The Avengers or {movie2}?"),
                ],
                role="user",
            )
        ]
        assert_prompt_contents_equal(assembled1_prompt_content, expected1_content)

        # Check fully assembled prompt
        assembled2_prompt_content = prompt.assemble_contents(
            movie1="Inception", movie2="Frozen"
        )
        expected2_content = [
            Content(
                parts=[
                    Part.from_text("Which movie is better, Inception or Frozen?"),
                ],
                role="user",
            )
        ]
        assert_prompt_contents_equal(assembled2_prompt_content, expected2_content)

    def test_string_prompt_assemble_unused_variables(self):
        # Variables must present in prompt_data if specified
        prompt = Prompt(prompt_data="Rate the movie {movie1}")
        with pytest.raises(ValueError):
            prompt.assemble_contents(day="Tuesday")

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    def test_prompt_generate_content(self):
        prompt = Prompt(
            prompt_data="Which movie is better, {movie1} or {movie2}?",
            variables=[
                {
                    "movie1": "The Avengers",
                    "movie2": "Frozen",
                }
            ],
            generation_config=GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
                stop_sequences=["\n\n\n"],
            ),
            model_name="gemini-1.0-pro-002",
            safety_settings=[
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=SafetySetting.HarmBlockMethod.SEVERITY,
                )
            ],
            system_instruction="Please answer in a short sentence.",
        )

        # Generate content using the assembled prompt.
        prompt.generate_content(
            contents=prompt.assemble_contents(**prompt.variables[0]),
        )

    @mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )
    def test_batch_prompt_generate_content(self):
        prompt = Prompt(
            prompt_data="Which movie is better, {movie1} or {movie2}?",
            variables=[
                {"movie1": "The Avengers", "movie2": "Frozen"},
                {"movie1": "Dune 2", "movie2": "Cars"},
                {"movie1": "Inception", "movie2": "The Matrix"},
            ],
            generation_config=GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
                stop_sequences=["\n\n\n"],
            ),
            model_name="gemini-1.0-pro-002",
            safety_settings=[
                SafetySetting(
                    category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=SafetySetting.HarmBlockMethod.SEVERITY,
                )
            ],
            system_instruction="Please answer in a short sentence.",
        )

        # Generate content using the assembled prompt.
        for i in range(len(prompt.variables)):
            prompt.generate_content(
                contents=prompt.assemble_contents(**prompt.variables[i]),
            )
