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
import io
import pytest
from typing import Dict, Iterable, List, MutableSequence, Optional
from unittest import mock

from google.api_core import operation as ga_operation
import vertexai
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1 import types as types_v1
from google.cloud.aiplatform_v1.services import (
    prediction_service as prediction_service_v1,
)
from google.cloud.aiplatform_v1beta1 import types as types_v1beta1
from google.cloud.aiplatform_v1beta1.services import endpoint_service
from vertexai import generative_models
from vertexai.preview import (
    generative_models as preview_generative_models,
    rag,
)
from vertexai.generative_models._generative_models import (
    prediction_service,
    gapic_prediction_service_types,
    gapic_content_types,
    gapic_tool_types,
    _fix_schema_dict_for_gapic_in_place,
)
from google.cloud.aiplatform_v1.types.cached_content import (
    CachedContent as GapicCachedContent,
)
from google.cloud.aiplatform_v1.services import (
    gen_ai_cache_service,
)
from vertexai.generative_models import _function_calling_utils
from vertexai.caching import CachedContent
from google.protobuf import field_mask_pb2


_TEST_PROJECT = "test-project"
_TEST_PROJECT2 = "test-project2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION2 = "europe-west4"


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

_REQUEST_FUNCTION_RESPONSE_SCHEMA_STRUCT = {
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
        "weather": {
            "type": "string",
        },
    },
}


# Input and expected output schema for renaming tests.
_RENAMING_INPUT_SCHEMA = {
    "type": "object",
    "min_properties": 1,
    "maxProperties": 3,
    "properties": {
        "names": {
            "type": "ArRaY",
            "minItems": 2,
            "max_items": 4,
            "items": {
                "type": "String",
                "minLength": 3,
                "maxLength": 5,
            },
        },
        "date": {
            "any_of": [
                {
                    "type": "strinG",
                    "format": "date",
                },
                {
                    "anyOf": [
                        {
                            "type": "inTegEr",
                            "minimum": 20241001,
                        },
                    ],
                },
            ],
        },
        "ordered": {
            "type": "OBJECT",
            "properties": {
                "a": {"type": "stRIng"},
                "b": {"type": "Integer"},
                "c": {
                    "type": "objeCT",
                    "properties": {
                        "x": {"type": "string"},
                        "y": {"type": "number"},
                        "z": {"type": "integer"},
                    },
                    "property_ordering": ["z", "y", "x"],
                },
            },
            "propertyOrdering": ["b", "a", "c"],
        },
    },
}
_RENAMING_EXPECTED_SCHEMA = {
    "type": "OBJECT",
    "min_properties": "1",  # NB: int64 is converted to string
    "max_properties": "3",
    "properties": {
        "names": {
            "type": "ARRAY",
            "min_items": "2",
            "max_items": "4",
            "items": {
                "type": "STRING",
                "min_length": "3",
                "max_length": "5",
            },
        },
        "date": {
            "any_of": [
                {
                    "type": "STRING",
                    "format": "date",
                },
                {
                    "any_of": [
                        {
                            "type": "INTEGER",
                            "minimum": 20241001,
                        },
                    ],
                },
            ],
        },
        "ordered": {
            "type": "OBJECT",
            "properties": {
                "a": {"type": "STRING"},
                "b": {"type": "INTEGER"},
                "c": {
                    "type": "OBJECT",
                    "properties": {
                        "x": {"type": "STRING"},
                        "y": {"type": "NUMBER"},
                        "z": {"type": "INTEGER"},
                    },
                    "property_ordering": ["z", "y", "x"],  # explicit order kept
                },
            },
            "property_ordering": ["b", "a", "c"],  # explicit order kept
        },
    },
    "property_ordering": ["names", "date", "ordered"],  # implicit order added
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
        first_tool_with_function_declarations = next(
            tool for tool in request.tools if tool.function_declarations
        )
        if (
            first_tool_with_function_declarations.function_declarations[0].name
            == update_weather_data.__name__
        ):
            response_part_struct = dict(
                function_call=gapic_tool_types.FunctionCall(
                    name=update_weather_data.__name__,
                    args={
                        "location": "Boston",
                        "temperature": 60,
                        "forecasts": [61, 62],
                        "extra_info": {"humidity": 50},
                    },
                )
            )
        else:
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


@pytest.fixture
def mock_generate_content_fixture():
    """Mocks PredictionServiceClient.generate_content()."""

    with mock.patch.object(
        prediction_service.PredictionServiceClient,
        "generate_content",
        new=mock_generate_content,
    ) as generate_content:
        yield generate_content


def mock_stream_generate_content(
    self,
    request: gapic_prediction_service_types.GenerateContentRequest,
    *,
    model: Optional[str] = None,
    contents: Optional[MutableSequence[gapic_content_types.Content]] = None,
) -> Iterable[gapic_prediction_service_types.GenerateContentResponse]:
    response = mock_generate_content(
        self=self, request=request, model=model, contents=contents
    )
    # When a streaming response gets blocked, the last chunk has no content.
    # Creating such last chunk.
    blocked_chunk = None
    candidate_0 = response.candidates[0] if response.candidates else None
    if candidate_0 and candidate_0.finish_reason not in (
        gapic_content_types.Candidate.FinishReason.STOP,
        gapic_content_types.Candidate.FinishReason.MAX_TOKENS,
    ):
        blocked_chunk = gapic_prediction_service_types.GenerateContentResponse(
            candidates=[
                gapic_content_types.Candidate(
                    index=0,
                    finish_reason=candidate_0.finish_reason,
                    finish_message=candidate_0.finish_message,
                    safety_ratings=candidate_0.safety_ratings,
                )
            ]
        )
        candidate_0.finish_reason = None
        candidate_0.finish_message = None
    yield response
    if blocked_chunk:
        yield blocked_chunk


def mock_generate_content_v1(
    self,
    request: types_v1.GenerateContentRequest,
    *,
    model: Optional[str] = None,
    contents: Optional[MutableSequence[types_v1.Content]] = None,
) -> types_v1.GenerateContentResponse:
    request_v1beta1 = types_v1beta1.GenerateContentRequest.deserialize(
        type(request).serialize(request)
    )
    response_v1beta1 = mock_generate_content(
        self=self,
        request=request_v1beta1,
    )
    response_v1 = types_v1.GenerateContentResponse.deserialize(
        type(response_v1beta1).serialize(response_v1beta1)
    )
    return response_v1


def mock_stream_generate_content_v1(
    self,
    request: types_v1.GenerateContentRequest,
    *,
    model: Optional[str] = None,
    contents: Optional[MutableSequence[types_v1.Content]] = None,
) -> Iterable[types_v1.GenerateContentResponse]:
    request_v1beta1 = types_v1beta1.GenerateContentRequest.deserialize(
        type(request).serialize(request)
    )
    for response_v1beta1 in mock_stream_generate_content(
        self=self,
        request=request_v1beta1,
    ):
        response_v1 = types_v1.GenerateContentResponse.deserialize(
            type(response_v1beta1).serialize(response_v1beta1)
        )
        yield response_v1


def patch_genai_services(func: callable):
    """Patches GenAI services (v1 and v1beta1, streaming and non-streaming)."""

    func = mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content,
    )(func)
    func = mock.patch.object(
        target=prediction_service_v1.PredictionServiceClient,
        attribute="generate_content",
        new=mock_generate_content_v1,
    )(func)
    func = mock.patch.object(
        target=prediction_service.PredictionServiceClient,
        attribute="stream_generate_content",
        new=mock_stream_generate_content,
    )(func)
    func = mock.patch.object(
        target=prediction_service_v1.PredictionServiceClient,
        attribute="stream_generate_content",
        new=mock_stream_generate_content_v1,
    )(func)
    return func


@pytest.fixture
def mock_get_cached_content_fixture():
    """Mocks GenAiCacheServiceClient.get_cached_content()."""

    def get_cached_content(self, name, retry=None):
        del self, retry
        response = GapicCachedContent(
            name=f"{name}",
            model="gemini-pro-from-mock-get-cached-content",
        )
        return response

    with mock.patch.object(
        gen_ai_cache_service.client.GenAiCacheServiceClient,
        "get_cached_content",
        new=get_cached_content,
    ) as get_cached_content:
        yield get_cached_content


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


def update_weather_data(
    location: str, temperature: int, forecasts: List[int], extra_info: Dict[str, int]
):
    """Updates the weather data in the specified location."""
    return dict(
        location=location,
        temperature=temperature,
        forecasts=forecasts,
        extra_info=extra_info,
        result="Success",
    )


@pytest.mark.usefixtures("google_auth_mock")
@pytest.mark.parametrize("api_transport", ["grpc", "rest"])
class TestGenerativeModels:
    """Unit tests for the generative models."""

    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, api_transport: str):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_transport=api_transport,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generative_model_constructor_model_name(
        self, generative_models: generative_models
    ):
        project_location_prefix = (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/"
        )

        model_name1 = "gemini-pro"
        model1 = generative_models.GenerativeModel(model_name1)
        assert (
            model1._prediction_resource_name
            == project_location_prefix + "publishers/google/models/" + model_name1
        )
        assert model1._model_name == "publishers/google/models/gemini-pro"

        model_name2 = "models/gemini-pro"
        model2 = generative_models.GenerativeModel(model_name2)
        assert (
            model2._prediction_resource_name
            == project_location_prefix + "publishers/google/" + model_name2
        )
        assert model2._model_name == "publishers/google/models/gemini-pro"

        model_name3 = "publishers/some_publisher/models/some_model"
        model3 = generative_models.GenerativeModel(model_name3)
        assert model3._prediction_resource_name == project_location_prefix + model_name3
        assert model3._model_name == "publishers/some_publisher/models/some_model"

        model_name4 = (
            f"projects/{_TEST_PROJECT2}/locations/{_TEST_LOCATION2}/endpoints/endpoint1"
        )
        model4 = generative_models.GenerativeModel(model_name4)
        assert model4._prediction_resource_name == model_name4
        assert _TEST_LOCATION2 in model4._prediction_client._api_endpoint
        assert model4._model_name == model_name4

        with pytest.raises(ValueError):
            generative_models.GenerativeModel("foo/bar/models/gemini-pro")

    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generative_model_from_cached_content(
        self, generative_models: generative_models, mock_get_cached_content_fixture
    ):
        project_location_prefix = (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/"
        )
        cached_content = CachedContent("cached-content-id-in-from-cached-content-test")

        model = generative_models.GenerativeModel.from_cached_content(
            cached_content=cached_content
        )

        assert (
            model._prediction_resource_name
            == project_location_prefix
            + "publishers/google/models/"
            + "gemini-pro-from-mock-get-cached-content"
        )
        assert (
            model._cached_content.model_name
            == "gemini-pro-from-mock-get-cached-content"
        )
        assert (
            model._cached_content.resource_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/"
            "cachedContents/cached-content-id-in-from-cached-content-test"
        )
        assert (
            model._cached_content.name
            == "cached-content-id-in-from-cached-content-test"
        )

    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generative_model_from_cached_content_with_resource_name(
        self, mock_get_cached_content_fixture, generative_models: generative_models
    ):
        project_location_prefix = (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/"
        )

        model = generative_models.GenerativeModel.from_cached_content(
            cached_content="cached-content-id-in-from-cached-content-test"
        )

        assert (
            model._prediction_resource_name
            == project_location_prefix
            + "publishers/google/models/"
            + "gemini-pro-from-mock-get-cached-content"
        )
        assert (
            model._cached_content.model_name
            == "gemini-pro-from-mock-get-cached-content"
        )
        assert (
            model._cached_content.resource_name
            == f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/"
            "cachedContents/cached-content-id-in-from-cached-content-test"
        )
        assert (
            model._cached_content.name
            == "cached-content-id-in-from-cached-content-test"
        )

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content(
        self, generative_models: generative_models, api_transport: str
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        response = model.generate_content("Why is sky blue?")
        assert response.text
        # TODO(avolkov): Add usage metadata to the mock
        assert response.usage_metadata.total_token_count

        model2 = generative_models.GenerativeModel(
            "gemini-pro",
            system_instruction=[
                "Talk like a pirate.",
                "Don't use rude words.",
            ],
        )
        response2 = model2.generate_content(
            "Why is sky blue?",
            generation_config=generative_models.GenerationConfig(
                temperature=0.2,
                top_p=0.9,
                top_k=20,
                candidate_count=1,
                max_output_tokens=200,
                stop_sequences=["\n\n\n"],
                presence_penalty=0.0,
                frequency_penalty=0.0,
                logprobs=5,
                response_logprobs=True,
                response_modalities=["TEXT"],
            ),
            safety_settings=[
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
                ),
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    method=generative_models.SafetySetting.HarmBlockMethod.PROBABILITY,
                ),
            ],
        )
        assert response2.text

        model3 = generative_models.GenerativeModel("gemini-1.5-pro-preview-0409")
        response3 = model3.generate_content(
            "Why is sky blue? Respond in JSON.",
            generation_config=generative_models.GenerationConfig(
                temperature=0.2,
                top_p=0.9,
                top_k=20,
                candidate_count=1,
                max_output_tokens=200,
                stop_sequences=["\n\n\n"],
                response_mime_type="application/json",
            ),
            safety_settings=[
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
                ),
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    method=generative_models.SafetySetting.HarmBlockMethod.PROBABILITY,
                ),
            ],
        )
        assert response3.text

        model4 = generative_models.GenerativeModel("gemini-1.5-pro-preview-0409")
        response4 = model4.generate_content(
            "Why is sky blue? Respond in JSON.",
            generation_config=generative_models.GenerationConfig(
                temperature=0.2,
                top_p=0.9,
                top_k=20,
                candidate_count=1,
                max_output_tokens=200,
                stop_sequences=["\n\n\n"],
                response_mime_type="application/json",
            ),
            safety_settings=[
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
                ),
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    method=generative_models.SafetySetting.HarmBlockMethod.PROBABILITY,
                ),
            ],
            labels={"label1": "value1", "label2": "value2"},
        )
        assert response4.text

        model5 = generative_models.GenerativeModel("gemini-1.5-pro-002")
        response5 = model5.generate_content(
            contents=[
                generative_models.Part.from_uri(
                    "gs://cloud-samples-data/generative-ai/audio/pixel.mp3",
                    mime_type="audio/mpeg",
                ),
                "What is the audio about?",
            ],
            generation_config=generative_models.GenerationConfig(
                audio_timestamp=True,
            ),
            safety_settings=[
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                    method=generative_models.SafetySetting.HarmBlockMethod.SEVERITY,
                ),
                generative_models.SafetySetting(
                    category=generative_models.SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    threshold=generative_models.SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                    method=generative_models.SafetySetting.HarmBlockMethod.PROBABILITY,
                ),
            ],
        )
        assert response5.text

    @mock.patch.object(
        target=prediction_service_v1.PredictionServiceClient,
        attribute="generate_content",
        new=lambda self, request: gapic_prediction_service_types.GenerateContentResponse(
            candidates=[
                gapic_content_types.Candidate(
                    index=0,
                    content=gapic_content_types.Content(
                        role="model",
                        parts=[
                            gapic_content_types.Part(
                                {"text": f"response to {request.cached_content}"}
                            )
                        ],
                    ),
                ),
            ],
        ),
    )
    def test_generate_content_with_cached_content(
        self,
        mock_get_cached_content_fixture,
    ):
        cached_content = CachedContent("cached-content-id-in-from-cached-content-test")

        model = generative_models.GenerativeModel.from_cached_content(
            cached_content=cached_content
        )

        response = model.generate_content("Why is sky blue?")

        assert response.text == "response to " + cached_content.resource_name

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_streaming(self, generative_models: generative_models):
        model = generative_models.GenerativeModel("gemini-pro")
        stream = model.generate_content("Why is sky blue?", stream=True)
        for chunk in stream:
            assert chunk.text

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_with_function_calling_integer_args(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        weather_tool = generative_models.Tool(
            function_declarations=[
                generative_models.FunctionDeclaration.from_func(update_weather_data)
            ],
        )
        response = model.generate_content(
            "Please update the weather data in Boston, with temperature 60, "
            "forecasts are 61 and 62, and humidity is 50",
            tools=[weather_tool],
        )
        assert (
            response.candidates[0].content.parts[0].function_call.name
            == "update_weather_data"
        )
        assert [
            function_call.name
            for function_call in response.candidates[0].function_calls
        ] == ["update_weather_data"]
        for args in (
            response.candidates[0].function_calls[0].args,
            response.candidates[0].function_calls[0].to_dict()["args"],
        ):
            assert args["location"] == "Boston"
            assert args["temperature"] == 60
            assert isinstance(args["temperature"], int)
            assert 61 in args["forecasts"] and 62 in args["forecasts"]
            assert all(isinstance(forecast, int) for forecast in args["forecasts"])
            assert args["extra_info"]["humidity"] == 50
            assert isinstance(args["extra_info"]["humidity"], int)
            assert args["location"] == "Boston"

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_response_accessor_errors(
        self, generative_models: generative_models
    ):
        """Checks that the exception text contains response information."""
        model = generative_models.GenerativeModel("gemini-pro")

        # Case when response has no candidates
        response1 = model.generate_content("Please block with block_reason=OTHER")

        assert response1.prompt_feedback.block_reason.name == "OTHER"

        with pytest.raises(ValueError) as e:
            _ = response1.text
        assert e.match("no candidates")
        assert e.match("prompt_feedback")

        # Case when response candidate content has no parts
        response2 = model.generate_content("Please fail!")

        with pytest.raises(ValueError) as e:
            _ = response2.text
        assert e.match("no parts")
        assert e.match("finish_reason")

        with pytest.raises(ValueError) as e:
            _ = response2.candidates[0].text
        assert e.match("no parts")
        assert e.match("finish_reason")

        # Case when response candidate content part has no text
        weather_tool = generative_models.Tool(
            function_declarations=[
                generative_models.FunctionDeclaration.from_func(get_current_weather)
            ],
        )
        response3 = model.generate_content(
            "What's the weather like in Boston?", tools=[weather_tool]
        )
        with pytest.raises(ValueError) as e:
            print(response3.text)
        assert e.match("no text")
        assert e.match("function_call")

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_model_optimizer(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("model-optimizer-exp-04-09")

        response = model.generate_content(
            "Why is sky blue?",
            generation_config=generative_models.GenerationConfig(
                model_config=generative_models.GenerationConfig.ModelConfig(
                    feature_selection_preference=generative_models.GenerationConfig.ModelConfig.FeatureSelectionPreference.BALANCED
                )
            ),
        )
        assert response.text

    @patch_genai_services
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

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_send_message_streaming(self, generative_models: generative_models):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        stream1 = chat.send_message("Why is sky blue?", stream=True)
        for chunk in stream1:
            assert chunk.candidates
        stream2 = chat.send_message("Is sky blue on other planets?", stream=True)
        for chunk in stream2:
            assert chunk.candidates

    @patch_genai_services
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

    @patch_genai_services
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
        # Checking that the original response and the block reason are accessible.
        assert e.value.responses[0].prompt_feedback.block_reason.name == "OTHER"
        # Checking that history did not get updated
        assert len(chat.history) == 2

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_send_message_response_candidate_blocked_error(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        chat = model.start_chat()

        with pytest.raises(generative_models.ResponseValidationError):
            chat.send_message("Please block response with finish_reason=OTHER.")

        # Checking that history did not get updated
        assert not chat.history

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_finish_reason_max_tokens_in_generate_content_and_send_message(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel(
            "gemini-1.0-pro",
            generation_config=generative_models.GenerationConfig(
                max_output_tokens=5,
            ),
        )
        chat = model.start_chat()

        # Test that generate_content succeeds:
        response1 = model.generate_content("Why is sky blue?")
        assert response1.text
        assert len(response1.text.split()) <= 5
        assert response1.candidates[0].finish_reason.name == "MAX_TOKENS"

        # Test that ChatSession.send_message raises error:
        with pytest.raises(generative_models.ResponseValidationError):
            chat.send_message("Please block response with finish_reason=OTHER.")

        # Verify that history did not get updated
        assert not chat.history

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_function_calling(self, generative_models: generative_models):
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
            response=_REQUEST_FUNCTION_RESPONSE_SCHEMA_STRUCT,
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

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_function_calling_with_integer_args(
        self, generative_models: generative_models
    ):
        get_current_weather_func = generative_models.FunctionDeclaration.from_func(
            update_weather_data
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

        response1 = chat.send_message(
            "Please update the weather data in Boston, with temperature 60, "
            "forecasts are 61 and 62, and humidity is 50"
        )
        assert (
            response1.candidates[0].content.parts[0].function_call.name
            == "update_weather_data"
        )
        assert [
            function_call.name
            for function_call in response1.candidates[0].function_calls
        ] == ["update_weather_data"]
        for args in (
            response1.candidates[0].function_calls[0].args,
            response1.candidates[0].function_calls[0].to_dict()["args"],
        ):
            assert args["location"] == "Boston"
            assert args["temperature"] == 60
            assert isinstance(args["temperature"], int)
            assert 61 in args["forecasts"] and 62 in args["forecasts"]
            assert all(isinstance(forecast, int) for forecast in args["forecasts"])
            assert args["extra_info"]["humidity"] == 50
            assert isinstance(args["extra_info"]["humidity"], int)
            assert args["location"] == "Boston"

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_chat_forced_function_calling(self, generative_models: generative_models):
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
            response=_REQUEST_FUNCTION_RESPONSE_SCHEMA_STRUCT,
        )
        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        tool_config = generative_models.ToolConfig(
            function_calling_config=generative_models.ToolConfig.FunctionCallingConfig(
                mode=generative_models.ToolConfig.FunctionCallingConfig.Mode.ANY,
                allowed_function_names=["get_current_weather"],
            )
        )

        model = generative_models.GenerativeModel(
            "gemini-pro",
            # Specifying the tools once to avoid specifying them in every request
            tools=[weather_tool],
            tool_config=tool_config,
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

    @patch_genai_services
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
            response=_REQUEST_FUNCTION_RESPONSE_SCHEMA_STRUCT,
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

        # Checking that the enums are serialized as strings, not integers.
        assert response.to_dict()["candidates"][0]["finish_reason"] == "STOP"

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_grounding_google_search_retriever(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        google_search_retriever_tool = (
            generative_models.Tool.from_google_search_retrieval(
                generative_models.grounding.GoogleSearchRetrieval()
            )
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[google_search_retriever_tool]
        )
        assert response.text

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_grounding_vertex_ai_search_retriever(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        vertex_ai_search_retriever_tool = generative_models.Tool.from_retrieval(
            retrieval=generative_models.grounding.Retrieval(
                source=generative_models.grounding.VertexAISearch(
                    datastore=f"projects/{_TEST_PROJECT}/locations/global/collections/default_collection/dataStores/test-datastore",
                )
            )
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[vertex_ai_search_retriever_tool]
        )
        assert response.text

    @patch_genai_services
    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    def test_generate_content_grounding_vertex_ai_search_retriever_with_project_and_location(
        self, generative_models: generative_models
    ):
        model = generative_models.GenerativeModel("gemini-pro")
        vertex_ai_search_retriever_tool = generative_models.Tool.from_retrieval(
            retrieval=generative_models.grounding.Retrieval(
                source=generative_models.grounding.VertexAISearch(
                    datastore="test-datastore",
                    project=_TEST_PROJECT,
                    location="global",
                )
            )
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[vertex_ai_search_retriever_tool]
        )
        assert response.text

    @patch_genai_services
    def test_generate_content_vertex_rag_retriever(self):
        model = preview_generative_models.GenerativeModel("gemini-pro")
        rag_resources = [
            rag.RagResource(
                rag_corpus=f"projects/{_TEST_PROJECT}/locations/us-central1/ragCorpora/1234556",
                rag_file_ids=["123", "456"],
            ),
        ]
        rag_retriever_tool = preview_generative_models.Tool.from_retrieval(
            retrieval=rag.Retrieval(
                source=rag.VertexRagStore(
                    rag_resources=rag_resources,
                    similarity_top_k=1,
                    vector_distance_threshold=0.4,
                ),
            ),
        )
        response = model.generate_content(
            "Why is sky blue?", tools=[rag_retriever_tool]
        )
        assert response.text

    @patch_genai_services
    def test_chat_automatic_function_calling_with_function_returning_dict(self):
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

    @patch_genai_services
    def test_chat_automatic_function_calling_with_function_returning_value(self):
        # Define a new function that returns a value instead of a dict.
        def get_current_weather(location: str):
            """Gets weather in the specified location.

            Args:
                location: The location for which to get the weather.

            Returns:
                The weather information as a str.
            """
            if location == "Boston":
                return "Super nice, but maybe a bit hot."
            return "Unavailable"

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

    @pytest.mark.parametrize(
        "generative_models",
        [generative_models, preview_generative_models],
    )
    @pytest.mark.parametrize(
        argnames=("image_format", "mime_type"),
        argvalues=[
            ("PNG", "image/png"),
            ("JPEG", "image/jpeg"),
            ("GIF", "image/gif"),
        ],
    )
    def test_image_mime_types(
        self, generative_models: generative_models, image_format: str, mime_type: str
    ):
        pytest.importorskip("PIL")
        # Importing external library lazily to reduce the scope of import errors.
        from PIL import Image as PIL_Image  # pylint: disable=g-import-not-at-top

        pil_image: PIL_Image.Image = PIL_Image.new(mode="RGB", size=(200, 200))
        image_bytes_io = io.BytesIO()
        pil_image.save(image_bytes_io, format=image_format)
        image = generative_models.Image.from_bytes(image_bytes_io.getvalue())
        image_part = generative_models.Part.from_image(image)
        assert image_part.mime_type == mime_type

    def test_generation_config_response_schema_dict_renaming(self):
        config = generative_models.GenerationConfig.from_dict(
            {
                "response_schema": _RENAMING_INPUT_SCHEMA,
            }
        )
        assert config.to_dict()["response_schema"] == _RENAMING_EXPECTED_SCHEMA

        config = generative_models.GenerationConfig(
            response_schema=_RENAMING_INPUT_SCHEMA,
        )
        assert config.to_dict()["response_schema"] == _RENAMING_EXPECTED_SCHEMA

    def test_tool_schema_dict_renaming(self):
        # The `Tool` constructor does not take a dict so we don't test it here.
        tool = generative_models.Tool.from_dict(
            {
                "function_declarations": [
                    {
                        "parameters": _RENAMING_INPUT_SCHEMA,
                    }
                ],
            }
        )
        assert (
            tool.to_dict()["function_declarations"][0]["parameters"]
            == _RENAMING_EXPECTED_SCHEMA
        )

    def test_function_declaration_schema_dict_renaming(self):
        # `FunctionDeclaration` doesn't have a `from_dict()` method to test.
        function = generative_models.FunctionDeclaration(
            name="test",
            parameters=_RENAMING_INPUT_SCHEMA,
        )
        assert function.to_dict()["parameters"] == _RENAMING_EXPECTED_SCHEMA

    def test_prefix_items_renaming(self):
        actual = {
            "type": "array",
            "prefixItems": [
                {"type": "boolean"},
                {
                    "type": "arraY",
                    "prefix_items": [
                        {"type": "INTeger"},
                        {"type": "string"},
                        {"type": "number"},
                    ],
                },
            ],
        }
        _fix_schema_dict_for_gapic_in_place(actual)
        expected = {
            "type": "ARRAY",
            "prefixItems": [
                {"type": "BOOLEAN"},
                {
                    "type": "ARRAY",
                    "prefixItems": [
                        {"type": "INTEGER"},
                        {"type": "STRING"},
                        {"type": "NUMBER"},
                    ],
                },
            ],
        }
        assert actual == expected

    def test_additional_properties_renaming(self):
        actual = {
            "type": "object",
            "properties": {
                "snake_case_false_pruned": {
                    "type": "object",
                    "additional_properties": False,
                },
                "snake_case_true_replaced_with_empty_dict": {
                    "type": "object",
                    "additional_properties": True,
                },
                "snake_case_sub_schema_processed": {
                    "type": "object",
                    "additional_properties": {"type": "string"},
                },
                "camelCase_false_pruned": {
                    "type": "object",
                    "additionalProperties": False,
                },
                "camelCase_true_replaced_with_empty_dict": {
                    "type": "object",
                    "additionalProperties": True,
                },
                "camelCase_sub_schema_processed": {
                    "type": "object",
                    "additionalProperties": {"type": "string"},
                },
            },
        }
        _fix_schema_dict_for_gapic_in_place(actual)
        expected = {
            "type": "OBJECT",
            "properties": {
                "snake_case_false_pruned": {
                    "type": "OBJECT",
                },
                "snake_case_true_replaced_with_empty_dict": {
                    "type": "OBJECT",
                    "additionalProperties": {},
                },
                "snake_case_sub_schema_processed": {
                    "type": "OBJECT",
                    "additionalProperties": {"type": "STRING"},
                },
                "camelCase_false_pruned": {
                    "type": "OBJECT",
                },
                "camelCase_true_replaced_with_empty_dict": {
                    "type": "OBJECT",
                    "additionalProperties": {},
                },
                "camelCase_sub_schema_processed": {
                    "type": "OBJECT",
                    "additionalProperties": {"type": "STRING"},
                },
            },
            "propertyOrdering": [
                "snake_case_false_pruned",
                "snake_case_true_replaced_with_empty_dict",
                "snake_case_sub_schema_processed",
                "camelCase_false_pruned",
                "camelCase_true_replaced_with_empty_dict",
                "camelCase_sub_schema_processed",
            ],
        }
        assert actual == expected

    def test_defs_ref_renaming(self):
        for actual, expected in [
            (
                {
                    "type": "integer",
                    "$defs": {
                        "Foo": {"type": "string"},
                        "Foos": {
                            "type": "array",
                            "items": {"$ref": "#/$defs/Foo"},
                        },
                    },
                },
                {
                    "type": "INTEGER",
                    "defs": {
                        "Foo": {"type": "STRING"},
                        "Foos": {
                            "type": "ARRAY",
                            # NB: Reference expansion accepts paths with "$defs"
                            # or "defs", so this needn't be normalized.
                            "items": {"ref": "#/$defs/Foo"},
                        },
                    },
                },
            ),
            (
                {
                    "type": "integer",
                    "defs": {
                        "Foo": {"type": "string"},
                        "Foos": {
                            "type": "array",
                            "items": {"ref": "#/defs/Foo"},
                        },
                    },
                },
                {
                    "type": "INTEGER",
                    "defs": {
                        "Foo": {"type": "STRING"},
                        "Foos": {
                            "type": "ARRAY",
                            "items": {"ref": "#/defs/Foo"},
                        },
                    },
                },
            ),
        ]:
            _fix_schema_dict_for_gapic_in_place(actual)
            assert actual == expected

    @pytest.mark.parametrize(
        "generative_models",
        [preview_generative_models],  # Only preview supports set_logging_config
    )
    @mock.patch.object(endpoint_service.EndpointServiceClient, "update_endpoint")
    def test_set_logging_config_for_endpoint(
        self, mock_update_endpoint, generative_models: generative_models
    ):
        endpoint_name = (
            f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/12345"
        )
        model = generative_models.GenerativeModel(endpoint_name)

        mock_update_endpoint.return_value = types_v1beta1.Endpoint(name=endpoint_name)

        enabled = True
        sampling_rate = 0.5
        bigquery_destination = f"bq://{_TEST_PROJECT}.my_dataset.my_table"
        enable_otel_logging = True

        model.set_request_response_logging_config(
            enabled=enabled,
            sampling_rate=sampling_rate,
            bigquery_destination=bigquery_destination,
            enable_otel_logging=enable_otel_logging,
        )

        expected_logging_config = types_v1beta1.PredictRequestResponseLoggingConfig(
            enabled=enabled,
            sampling_rate=sampling_rate,
            bigquery_destination=types_v1beta1.BigQueryDestination(
                output_uri=bigquery_destination
            ),
            enable_otel_logging=enable_otel_logging,
        )
        expected_endpoint = types_v1beta1.Endpoint(
            name=endpoint_name,
            predict_request_response_logging_config=expected_logging_config,
        )
        expected_update_mask = field_mask_pb2.FieldMask(
            paths=["predict_request_response_logging_config"]
        )

        mock_update_endpoint.assert_called_once_with(
            types_v1beta1.UpdateEndpointRequest(
                endpoint=expected_endpoint,
                update_mask=expected_update_mask,
            )
        )

    @pytest.mark.parametrize(
        "generative_models",
        [preview_generative_models],  # Only preview supports set_logging_config
    )
    @mock.patch.object(
        endpoint_service.EndpointServiceClient, "set_publisher_model_config"
    )
    def test_set_logging_config_for_publisher_model(
        self, mock_set_publisher_model_config, generative_models: generative_models
    ):
        model_name = "gemini-pro"
        model = generative_models.GenerativeModel(model_name)
        full_model_name = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/{model_name}"

        enabled = False
        sampling_rate = 1.0
        bigquery_destination = f"bq://{_TEST_PROJECT}.another_dataset"
        enable_otel_logging = False

        mock_operation = mock.Mock(spec=ga_operation.Operation)
        mock_set_publisher_model_config.return_value = mock_operation
        mock_operation.result.return_value = types_v1beta1.PublisherModelConfig(
            logging_config=types_v1beta1.PredictRequestResponseLoggingConfig(
                enabled=enabled,
                sampling_rate=sampling_rate,
                bigquery_destination=types_v1beta1.BigQueryDestination(
                    output_uri=bigquery_destination
                ),
                enable_otel_logging=enable_otel_logging,
            )
        )

        model.set_request_response_logging_config(
            enabled=enabled,
            sampling_rate=sampling_rate,
            bigquery_destination=bigquery_destination,
            enable_otel_logging=enable_otel_logging,
        )

        expected_logging_config = types_v1beta1.PredictRequestResponseLoggingConfig(
            enabled=enabled,
            sampling_rate=sampling_rate,
            bigquery_destination=types_v1beta1.BigQueryDestination(
                output_uri=bigquery_destination
            ),
            enable_otel_logging=enable_otel_logging,
        )
        expected_publisher_model_config = types_v1beta1.PublisherModelConfig(
            logging_config=expected_logging_config
        )

        mock_set_publisher_model_config.assert_called_once_with(
            types_v1beta1.SetPublisherModelConfigRequest(
                name=full_model_name,
                publisher_model_config=expected_publisher_model_config,
            )
        )
        mock_operation.result.assert_called_once()


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
