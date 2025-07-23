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
"""System tests for generative models."""

from typing import Any

import json
import os
import pytest

# Google imports
from google import auth
from google.auth.aio.credentials import StaticCredentials
from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from vertexai import generative_models
from vertexai.generative_models import Content
from vertexai.preview import (
    generative_models as preview_generative_models,
)
from vertexai.preview import caching


GEMINI_MODEL_NAME = "gemini-1.0-pro-002"
GEMINI_VISION_MODEL_NAME = "gemini-1.0-pro-vision"
GEMINI_15_MODEL_NAME = "gemini-1.5-pro-preview-0409"
GEMINI_15_PRO_MODEL_NAME = "gemini-1.5-pro-001"
GEMINI_15_PRO_2_MODEL_NAME = "gemini-1.5-pro-002"

STAGING_API_ENDPOINT = "STAGING_ENDPOINT"
PROD_API_ENDPOINT = "PROD_ENDPOINT"


# A dummy function for function calling
def get_current_weather(location: str, unit: str = "centigrade"):
    """Gets weather in the specified location.

    Args:
        location: The location for which to get the weather.
        unit: Optional. Temperature unit. Can be Centigrade or Fahrenheit. Defaults to Centigrade.

    Returns:
        The weather information as a dict.
    """
    return dict(
        location=location,
        unit=unit,
        weather="Super nice, but maybe a bit hot.",
    )


def get_client_api_transport(client: Any):
    return client._transport.__class__.__name__.lower()


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

_RESPONSE_SCHEMA_STRUCT = {
    "type": "object",
    "properties": {
        "location": {
            "type": "string",
        },
    },
    "required": ["location"],
}


@pytest.mark.parametrize("api_endpoint_env_name", [PROD_API_ENDPOINT])
@pytest.mark.parametrize("api_transport", ["grpc", "rest"])
@pytest.mark.skip(reason="Models are deprecated.")
class TestGenerativeModels(e2e_base.TestEndToEnd):
    """System tests for generative models."""

    _temp_prefix = "temp_generative_models_test_"

    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, api_endpoint_env_name, api_transport):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        if api_endpoint_env_name == STAGING_API_ENDPOINT:
            api_endpoint = os.getenv(api_endpoint_env_name) or None
        else:
            api_endpoint = None
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
            api_endpoint=api_endpoint,
            api_transport=api_transport,
        )

    def test_generate_content_with_cached_content_from_text(
        self, api_endpoint_env_name
    ):
        cached_content = caching.CachedContent.create(
            model_name=GEMINI_15_PRO_MODEL_NAME,
            system_instruction="Please answer all the questions like a pirate.",
            contents=[
                Content.from_dict(
                    {
                        "role": "user",
                        "parts": [
                            {
                                "file_data": {
                                    "mime_type": "application/pdf",
                                    "file_uri": "gs://ucaip-samples-us-central1/sdk_system_test_resources/megatro-llm.pdf",
                                }
                            }
                            for _ in range(10)
                        ]
                        + [
                            {"text": "Please try to summarize the previous contents."},
                        ],
                    }
                )
            ],
        )

        model = preview_generative_models.GenerativeModel.from_cached_content(
            cached_content=cached_content
        )

        response = model.generate_content(
            "Why is sky blue?",
            generation_config=preview_generative_models.GenerationConfig(temperature=0),
        )
        try:
            assert response.text
        finally:
            cached_content.delete()

    def test_generate_content_from_text(self, api_endpoint_env_name, api_transport):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(
            "Why is sky blue?",
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response.text
        assert api_transport in get_client_api_transport(model._prediction_client)

    def test_generate_content_latency(self, api_endpoint_env_name):
        import time
        from unittest import mock
        from vertexai.generative_models._generative_models import (
            prediction_service_v1 as prediction_service,
        )

        gapic_response_time = None
        gapic_generate_content = (
            prediction_service.PredictionServiceClient.generate_content
        )

        def generate_content_patch(self, *args, **kwargs):
            nonlocal gapic_response_time
            gapic_start_time = time.time()
            response = gapic_generate_content(self, *args, **kwargs)
            gapic_response_time = time.time() - gapic_start_time
            return response

        with mock.patch.object(
            prediction_service.PredictionServiceClient,
            "generate_content",
            generate_content_patch,
        ):
            sdk_start_time = time.time()
            model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
            model.generate_content(
                "Why is sky blue?",
                generation_config=generative_models.GenerationConfig(temperature=0),
            )
            sdk_response_time = time.time() - sdk_start_time

        sdk_latency = sdk_response_time - gapic_response_time

        percent_latency = (sdk_response_time - gapic_response_time) / sdk_response_time

        # Assert SDK adds <= 0.01 seconds of latency and <=.01% of the overall latency
        assert sdk_latency <= 0.01
        assert percent_latency <= 0.01

    @pytest.mark.asyncio
    async def test_generate_content_async(self, api_endpoint_env_name, api_transport):
        # Retrieve access token from ADC required to construct
        # google.auth.aio.credentials.StaticCredentials for async REST transport.
        # TODO: Update this when google.auth.aio.default is supported for async.
        if api_transport == "rest":
            # Construct google.auth.aio.credentials.StaticCredentials
            # using the access token from ADC for async REST transport.
            default_credentials, _ = auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            auth_req = auth.transport.requests.Request()
            default_credentials.refresh(auth_req)

            async_credentials = StaticCredentials(token=default_credentials.token)
            aiplatform.initializer._set_async_rest_credentials(async_credentials)
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        response = await model.generate_content_async(
            "Why is sky blue?",
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response.text
        assert api_transport in get_client_api_transport(
            model._prediction_async_client._client
        )
        await model._close_async_client()

    def test_generate_content_streaming(self, api_endpoint_env_name, api_transport):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        stream = model.generate_content(
            "Why is sky blue?",
            stream=True,
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        for chunk in stream:
            assert (
                chunk.text
                or chunk.candidates[0].finish_reason
                is generative_models.FinishReason.STOP
            )
        assert api_transport in get_client_api_transport(model._prediction_client)

    @pytest.mark.asyncio
    async def test_generate_content_streaming_async(
        self, api_endpoint_env_name, api_transport
    ):
        # Retrieve access token from ADC required to construct
        # google.auth.aio.credentials.StaticCredentials for async REST transport.
        # TODO: Update this when google.auth.aio.default is supported for async.
        if api_transport == "rest":
            # Construct google.auth.aio.credentials.StaticCredentials
            # using the access token from ADC for async REST transport.
            default_credentials, _ = auth.default(
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            auth_req = auth.transport.requests.Request()
            default_credentials.refresh(auth_req)

            async_credentials = StaticCredentials(token=default_credentials.token)
            aiplatform.initializer._set_async_rest_credentials(async_credentials)
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        async_stream = await model.generate_content_async(
            "Why is sky blue?",
            stream=True,
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        async for chunk in async_stream:
            assert (
                chunk.text
                or chunk.candidates[0].finish_reason
                is generative_models.FinishReason.STOP
            )
        assert api_transport in get_client_api_transport(
            model._prediction_async_client._client
        )
        await model._close_async_client()

    def test_generate_content_with_parameters(
        self, api_endpoint_env_name, api_transport
    ):
        model = generative_models.GenerativeModel(
            GEMINI_MODEL_NAME,
            system_instruction=[
                "Talk like a pirate.",
                "Don't use rude words.",
            ],
        )
        response = model.generate_content(
            contents="Why is sky blue?",
            generation_config=generative_models.GenerationConfig(
                temperature=0,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
                stop_sequences=["STOP!"],
                response_logprobs=True,
                logprobs=3,
            ),
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        assert response.text
        assert api_transport in get_client_api_transport(model._prediction_client)

    def test_generate_content_with_gemini_15_parameters(self, api_endpoint_env_name):
        model = generative_models.GenerativeModel(GEMINI_15_MODEL_NAME)
        response = model.generate_content(
            contents="Why is sky blue? Respond in JSON Format.",
            generation_config=generative_models.GenerationConfig(
                temperature=0,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                seed=5,
                max_output_tokens=100,
                stop_sequences=["STOP!"],
                presence_penalty=0.0,
                frequency_penalty=0.0,
                response_mime_type="application/json",
                response_schema=_RESPONSE_SCHEMA_STRUCT,
            ),
            safety_settings={
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
            },
        )
        assert response.text
        assert json.loads(response.text)

    def test_generate_content_from_list_of_content_dict(
        self, api_endpoint_env_name, api_transport
    ):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(
            contents=[{"role": "user", "parts": [{"text": "Why is sky blue?"}]}],
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response.text
        assert api_transport in get_client_api_transport(model._prediction_client)

    @pytest.mark.skip(
        reason="Breaking change in the gemini-pro-vision model. See b/315803556#comment3"
    )
    def test_generate_content_from_remote_image(self, api_endpoint_env_name):
        vision_model = generative_models.GenerativeModel(GEMINI_VISION_MODEL_NAME)
        image_part = generative_models.Part.from_uri(
            uri="gs://download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg",
            mime_type="image/jpeg",
        )
        response = vision_model.generate_content(
            image_part,
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response.text
        assert "cat" in response.text

    def test_generate_content_from_text_and_remote_image(
        self, api_endpoint_env_name, api_transport
    ):
        vision_model = generative_models.GenerativeModel(GEMINI_VISION_MODEL_NAME)
        image_part = generative_models.Part.from_uri(
            uri="gs://download.tensorflow.org/example_images/320px-Felis_catus-cat_on_snow.jpg",
            mime_type="image/jpeg",
        )
        response = vision_model.generate_content(
            contents=["What is shown in this image?", image_part],
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response.text
        assert "cat" in response.text
        assert api_transport in get_client_api_transport(
            vision_model._prediction_client
        )

    def test_generate_content_from_text_and_remote_video(
        self, api_endpoint_env_name, api_transport
    ):
        vision_model = generative_models.GenerativeModel(GEMINI_VISION_MODEL_NAME)
        video_part = generative_models.Part.from_uri(
            uri="gs://cloud-samples-data/video/animals.mp4",
            mime_type="video/mp4",
        )
        response = vision_model.generate_content(
            contents=["What is in the video?", video_part],
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response.text
        assert "Zootopia" in response.text
        assert api_transport in get_client_api_transport(
            vision_model._prediction_client
        )

    def test_generate_content_from_text_and_remote_audio(
        self, api_endpoint_env_name, api_transport
    ):
        pro_model = generative_models.GenerativeModel(GEMINI_15_PRO_2_MODEL_NAME)
        audio_part = generative_models.Part.from_uri(
            uri="gs://cloud-samples-data/generative-ai/audio/pixel.mp3",
            mime_type="audio/mp3",
        )
        response = pro_model.generate_content(
            contents=["What is in the audio?", audio_part],
            generation_config=generative_models.GenerationConfig(audio_timestamp=True),
        )
        assert response.text
        assert api_transport in get_client_api_transport(pro_model._prediction_client)

    def test_grounding_google_search_retriever(self, api_endpoint_env_name):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        google_search_retriever_tool = (
            generative_models.Tool.from_google_search_retrieval(
                generative_models.grounding.GoogleSearchRetrieval()
            )
        )
        response = model.generate_content(
            "Why is sky blue?",
            tools=[google_search_retriever_tool],
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert (
            response.candidates[0].finish_reason
            is generative_models.FinishReason.RECITATION
            or response.text
        )

    def test_grounding_google_search_retriever_with_dynamic_retrieval(
        self, api_endpoint_env_name
    ):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        google_search_retriever_tool = generative_models.Tool.from_google_search_retrieval(
            generative_models.grounding.GoogleSearchRetrieval(
                generative_models.grounding.DynamicRetrievalConfig(
                    mode=generative_models.grounding.DynamicRetrievalConfig.Mode.MODE_DYNAMIC,
                    dynamic_threshold=0.05,
                )
            )
        )
        response = model.generate_content(
            "Why is sky blue?",
            tools=[google_search_retriever_tool],
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert (
            response.candidates[0].finish_reason
            is generative_models.FinishReason.RECITATION
            or response.text
        )

    # Chat

    def test_send_message_from_text(self, api_endpoint_env_name, api_transport):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        chat = model.start_chat()
        response1 = chat.send_message(
            "I really like fantasy movies.",
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response1.text
        assert len(chat.history) == 2

        response2 = chat.send_message(
            "What things do I like?.",
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response2.text
        assert len(chat.history) == 4
        assert api_transport in get_client_api_transport(model._prediction_client)

    def test_chat_function_calling(self, api_endpoint_env_name):
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
        )

        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        model = generative_models.GenerativeModel(
            GEMINI_MODEL_NAME,
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
                    "content": {"weather": "super nice"},
                },
            ),
        )
        assert response2.text

    def test_generate_content_function_calling(self, api_endpoint_env_name):
        get_current_weather_func = generative_models.FunctionDeclaration(
            name="get_current_weather",
            description="Get the current weather in a given location",
            parameters=_REQUEST_FUNCTION_PARAMETER_SCHEMA_STRUCT,
        )

        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        model = generative_models.GenerativeModel(
            GEMINI_MODEL_NAME,
            # Specifying the tools once to avoid specifying them in every request
            tools=[weather_tool],
        )

        # Define the user's prompt in a Content object that we can reuse in model calls
        prompt = "What is the weather like in Boston?"
        user_prompt_content = generative_models.Content(
            role="user",
            parts=[
                generative_models.Part.from_text(prompt),
            ],
        )

        # Send the prompt and instruct the model to generate content using the Tool
        response = model.generate_content(
            user_prompt_content,
            generation_config={"temperature": 0},
            tools=[weather_tool],
        )
        response_function_call_content = response.candidates[0].content

        assert (
            response.candidates[0].content.parts[0].function_call.name
            == "get_current_weather"
        )

        assert response.candidates[0].function_calls[0].args["location"]
        assert len(response.candidates[0].function_calls) == 1
        assert (
            response.candidates[0].function_calls[0]
            == response.candidates[0].content.parts[0].function_call
        )

        # fake api_response data
        api_response = {
            "location": "Boston, MA",
            "temperature": 38,
            "description": "Partly Cloudy",
            "icon": "partly-cloudy",
            "humidity": 65,
            "wind": {"speed": 10, "direction": "NW"},
        }

        response = model.generate_content(
            [
                user_prompt_content,
                response_function_call_content,
                generative_models.Content(
                    role="user",
                    parts=[
                        generative_models.Part.from_function_response(
                            name="get_current_weather",
                            response=api_response,
                        )
                    ],
                ),
            ],
            tools=[weather_tool],
        )
        assert response
        assert len(response.candidates[0].function_calls) == 0

        # Get the model summary response
        summary = response.candidates[0].content.parts[0].text

        assert summary

    def test_chat_automatic_function_calling(self, api_endpoint_env_name):
        get_current_weather_func = generative_models.FunctionDeclaration.from_func(
            get_current_weather
        )

        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )

        model = preview_generative_models.GenerativeModel(
            GEMINI_MODEL_NAME,
            # Specifying the tools once to avoid specifying them in every request
            tools=[weather_tool],
        )

        chat = model.start_chat(
            responder=preview_generative_models.AutomaticFunctionCallingResponder(
                max_automatic_function_calls=1,
            )
        )

        response = chat.send_message("What is the weather like in Boston?")

        assert response.text
        assert "nice" in response.text
        assert len(chat.history) == 4
        assert chat.history[-3].parts[0].function_call
        assert chat.history[-3].parts[0].function_call.name == "get_current_weather"
        assert chat.history[-2].parts[0].function_response
        assert chat.history[-2].parts[0].function_response.name == "get_current_weather"

    def test_additional_request_metadata(self, api_endpoint_env_name):
        aiplatform.init(request_metadata=[("foo", "bar")])
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(
            "Why is sky blue?",
            generation_config=generative_models.GenerationConfig(temperature=0),
        )
        assert response

    def test_compute_tokens_from_text(self, api_endpoint_env_name):
        model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.compute_tokens(["Why is sky blue?", "Explain it like I'm 5."])
        assert len(response.tokens_info) == 2
        for token_info in response.tokens_info:
            assert token_info.tokens
            assert token_info.token_ids
            assert len(token_info.token_ids) == len(token_info.tokens)
            assert token_info.role
            # Lightly validate that the tokens are not Base64 encoded
            assert b"=" not in token_info.tokens

    def test_count_tokens_from_text(self):
        plain_model = generative_models.GenerativeModel(GEMINI_MODEL_NAME)
        model = generative_models.GenerativeModel(
            GEMINI_MODEL_NAME, system_instruction=["You are a chatbot."]
        )
        get_current_weather_func = generative_models.FunctionDeclaration.from_func(
            get_current_weather
        )
        weather_tool = generative_models.Tool(
            function_declarations=[get_current_weather_func],
        )
        content = ["Why is sky blue?", "Explain it like I'm 5."]

        response_without_si = plain_model.count_tokens(content)
        response_with_si = model.count_tokens(content)
        response_with_si_and_tool = model.count_tokens(
            content,
            tools=[weather_tool],
        )

        # system instruction + user prompt
        assert response_with_si.total_tokens > response_without_si.total_tokens
        assert (
            response_with_si.total_billable_characters
            > response_without_si.total_billable_characters
        )
        # system instruction + user prompt + tool
        assert response_with_si_and_tool.total_tokens > response_with_si.total_tokens
        assert (
            response_with_si_and_tool.total_billable_characters
            > response_with_si.total_billable_characters
        )
