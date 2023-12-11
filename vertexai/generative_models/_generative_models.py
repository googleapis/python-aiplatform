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
"""Classes for working with generative models."""
# pylint: disable=bad-continuation, line-too-long

import copy
import io
import pathlib
from typing import Any, AsyncIterable, AsyncIterator, Awaitable, Callable, Dict, Iterable, Iterator, List, Optional, Sequence, Type, Union

try:
    from PIL import Image as PIL_Image
except ImportError:
    PIL_Image = None

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform_v1beta1 import types as aiplatform_types
from google.cloud.aiplatform_v1beta1.services import prediction_service
from google.cloud.aiplatform_v1beta1.types import content as content_types
from google.cloud.aiplatform_v1beta1.types import prediction_service as prediction_service_types
from google.cloud.aiplatform_v1beta1.types import tool as tool_types
from vertexai.language_models import _language_models as tunable_models

# Re-exporting some GAPIC types

# GAPIC types used in request
HarmCategory = content_types.HarmCategory
HarmBlockThreshold = content_types.SafetySetting.HarmBlockThreshold
# We use Dict[HarmCategory, HarmBlockThreshold] instead of List[SafetySetting]
# SafetySetting = content_types.SafetySetting
# VideoMetadata = content_types.VideoMetadata

# GAPIC types used in response
# We expose FinishReason to make it easier to check the response finish reason.
FinishReason = content_types.Candidate.FinishReason
# We expose SafetyRating to make it easier to check the response safety rating.
SafetyRating = content_types.SafetyRating
# CitationMetadata = content_types.CitationMetadata
# Citation = content_types.Citation


# These type defnitions are expanded to help the user see all the types
PartsType = Union[
    str,
    "Image",
    "Part",
    List[Union[str, "Image", "Part"]],
]

ContentDict = Dict[str, Any]
ContentsType = Union[
    List["Content"],
    List[ContentDict],
    str,
    "Image",
    "Part",
    List[Union[str, "Image", "Part"]],
]

GenerationConfigDict = Dict[str, Any]
GenerationConfigType = Union[
    "GenerationConfig",
    GenerationConfigDict,
]

SafetySettingsType = Union[
    List[content_types.SafetySetting],
    Dict[content_types.HarmCategory, content_types.SafetySetting.HarmBlockThreshold],
]


class GenerativeModel:

    _USER_ROLE = "user"
    _MODEL_ROLE = "model"

    def __init__(
        self,
        model_name: str,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ):
        if "/" not in model_name:
            model_name = "publishers/google/models/" + model_name

        project = aiplatform_initializer.global_config.project
        location = aiplatform_initializer.global_config.location

        self._model_name = model_name
        self._prediction_resource_name = f"projects/{project}/locations/{location}/{model_name}"
        self._generation_config = generation_config
        self._safety_settings = safety_settings
        self._tools = tools

        # Validating the parameters
        self._prepare_request(
            contents="test",
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )

    @property
    def _prediction_client(self) -> prediction_service.PredictionServiceClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_prediction_client_value", None):
            self._prediction_client_value = aiplatform_initializer.global_config.create_client(
                client_class=prediction_service.PredictionServiceClient,
                prediction_client=True,
            )
        return self._prediction_client_value

    @property
    def _prediction_async_client(self) -> prediction_service.PredictionServiceAsyncClient:
        # Switch to @functools.cached_property once its available.
        if not getattr(self, "_prediction_async_client_value", None):
            self._prediction_async_client_value = (
                aiplatform_initializer.global_config.create_client(
                    client_class=prediction_service.PredictionServiceAsyncClient,
                    prediction_client=True,
                )
            )
        return self._prediction_async_client_value

    def _prepare_request(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> prediction_service_types.GenerateContentRequest:
        if not contents:
            raise TypeError("contents must not be empty")

        generation_config = generation_config or self._generation_config
        safety_settings = safety_settings or self._safety_settings
        tools = tools or self._tools

        # contents can either be a list of Content objects (most generic case)
        if isinstance(contents, Sequence) and any(isinstance(c, content_types.Content) for c in contents):
            if not all(isinstance(c, content_types.Content) for c in contents):
                raise TypeError(
                    "When passing a list with Content objects, every item in a list must be a Content object."
                )
        elif isinstance(contents, Sequence) and any(isinstance(c, Content) for c in contents):
            if not all(isinstance(c, Content) for c in contents):
                raise TypeError(
                    "When passing a list with Content objects, every item in a list must be a Content object."
                )
            contents = [content._raw_content for content in contents]
        elif isinstance(contents, Sequence) and any(isinstance(c, dict) for c in contents):
            if not all(isinstance(c, dict) for c in contents):
                raise TypeError(
                    "When passing a list with Content dict objects, every item in a list must be a Content dict object."
                )
            contents = [content_types.Content(content_dict) for content_dict in contents]
        # or a value that can be converted to a *single* Content object
        else:
            contents = [_to_content(contents)]

        gapic_generation_config: content_types.GenerationConfig = None
        if generation_config:
            if isinstance(generation_config, content_types.GenerationConfig):
                gapic_generation_config = generation_config
            elif isinstance(generation_config, GenerationConfig):
                gapic_generation_config = generation_config._raw_generation_config
            elif isinstance(generation_config, Dict):
                gapic_generation_config = content_types.GenerationConfig(**generation_config)
            else:
                raise TypeError(
                    "generation_config must either be a GenerationConfig object or a dictionary representation of it."
                )
        gapic_safety_settings = None
        if safety_settings:
            if isinstance(safety_settings, Sequence):
                if not all(isinstance(safety_setting, content_types.SafetySetting) for safety_setting in safety_settings):
                    raise TypeError(
                        "When passing a list with SafetySettings objects, every item in a list must be a SafetySetting object."
                    )
                gapic_safety_settings = safety_settings
            elif isinstance(safety_settings, dict):
                gapic_safety_settings = [
                    content_types.SafetySetting(
                        category=content_types.HarmCategory(category),
                        threshold=content_types.SafetySetting.HarmBlockThreshold(threshold),
                    )
                    for category, threshold in safety_settings.items()
                ]
            else:
                raise TypeError(
                    "safety_settings must either be a list of SafetySettings objects or a dictionary mapping from HarmCategory to HarmBlockThreshold."
                )
        gapic_tools = None
        if tools:
            gapic_tools = []
            for tool in tools:
                if isinstance(tool, tool_types.Tool):
                    gapic_tools.append(tool)
                elif isinstance(tool, Tool):
                    gapic_tools.append(tool._raw_tool)
                else:
                    raise TypeError(
                        "Unexpected tool type: {tool}."
                    )

        return prediction_service_types.GenerateContentRequest(
            # The `model` parameter now needs to be set for the vision models.
            # Always need to pass the resource via the `model` parameter.
            # Even when resource is an endpoint.
            model=self._prediction_resource_name,
            contents=contents,
            generation_config=gapic_generation_config,
            safety_settings=gapic_safety_settings,
            tools=gapic_tools
        )

    def _parse_response(
        self,
        response: prediction_service_types.GenerateContentResponse,
    ) -> "GenerationResponse":
        return GenerationResponse._from_gapic(response)

    def generate_content(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
        stream: bool = False,
    ) -> Union[
        "GenerationResponse",
        Iterable["GenerationResponse"],
    ]:
        if stream:
            return self._generate_content_streaming(
                contents=contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )
        else:
            return self._generate_content(
                contents=contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )

    def generate_content_async(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
        stream: bool = False,
    ) -> Union[
        Awaitable["GenerationResponse"],
        Awaitable[AsyncIterable["GenerationResponse"]],
    ]:
        if stream:
            return self._generate_content_streaming_async(
                contents=contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )
        else:
            return self._generate_content_async(
                contents=contents,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )

    def _generate_content(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> "GenerationResponse":
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        # generate_content is not available
        # gapic_response = self._prediction_client.generate_content(request=request)
        gapic_response = None
        stream = self._prediction_client.stream_generate_content(request=request)
        for gapic_chunk in stream:
            if gapic_response:
                _append_gapic_response(gapic_response, gapic_chunk)
            else:
                gapic_response = gapic_chunk
        return self._parse_response(gapic_response)

    async def _generate_content_async(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> "GenerationResponse":
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        # generate_content is not available
        # gapic_response = await self._prediction_async_client.generate_content(request=request)
        gapic_response = None
        stream = await self._prediction_async_client.stream_generate_content(request=request)
        async for gapic_chunk in stream:
            if gapic_response:
                _append_gapic_response(gapic_response, gapic_chunk)
            else:
                gapic_response = gapic_chunk
        return self._parse_response(gapic_response)

    def _generate_content_streaming(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> Iterable["GenerationResponse"]:
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        response_stream = self._prediction_client.stream_generate_content(request=request)
        for chunk in response_stream:
            yield self._parse_response(chunk)

    async def _generate_content_streaming_async(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> AsyncIterable["GenerationResponse"]:
        request = self._prepare_request(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        response_stream = await self._prediction_async_client.stream_generate_content(request=request)
        async def async_generator():
            async for chunk in response_stream:
                yield self._parse_response(chunk)
        return async_generator()

    def count_tokens(self, contents: ContentsType) -> prediction_service_types.CountTokensResponse:
        return self._prediction_client.count_tokens(
            request=prediction_service_types.CountTokensRequest(
                endpoint=self._prediction_resource_name,
                model=self._prediction_resource_name,
                contents=self._prepare_request(contents=contents).contents,
            )
        )

    async def count_tokens_async(self, contents: ContentsType) -> prediction_service_types.CountTokensResponse:
        return await self._prediction_async_client.count_tokens(
            request=prediction_service_types.CountTokensRequest(
                endpoint=self._prediction_resource_name,
                model=self._prediction_resource_name,
                contents=self._prepare_request(contents=contents).contents,
            )
        )

    def start_chat(
        self,
        *,
        history: Optional[List[content_types.Content]] = None,
    ) -> "ChatSession":
        return ChatSession(
            model=self,
            history=history,
        )


_SUCCESSFUL_FINISH_REASONS = [
    content_types.Candidate.FinishReason.STOP,
    # Many responses have this finish reason
    content_types.Candidate.FinishReason.FINISH_REASON_UNSPECIFIED,
]


class ChatSession:
    _USER_ROLE = "user"
    _MODEL_ROLE = "model"

    def __init__(
        self,
        model: GenerativeModel,
        *,
        history: Optional[List["Content"]] = None,
        raise_on_blocked: bool = True,
    ):
        self._model = model
        self._history = history or []
        self._raise_on_blocked = raise_on_blocked

    @property
    def history(self) -> List["Content"]:
        return self._history

    def send_message(
        self,
        content: PartsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
        stream: bool = False,
    ) -> Union["GenerationResponse", Iterable["GenerationResponse"]]:
        if stream:
            return self._send_message_streaming(
                content=content,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )
        else:
            return self._send_message(
                content=content,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )

    def send_message_async(
        self,
        content: PartsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
        stream: bool = False,
    ) -> Union[
        Awaitable["GenerationResponse"],
        Awaitable[AsyncIterable["GenerationResponse"]],
    ]:
        if stream:
            return self._send_message_streaming_async(
                content=content,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )
        else:
            return self._send_message_async(
                content=content,
                generation_config=generation_config,
                safety_settings=safety_settings,
                tools=tools,
            )

    def _send_message(
        self,
        content: PartsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> "GenerationResponse":
        # Preparing the message history to send
        request_message = Content._from_gapic(_to_content(value=content, role=self._USER_ROLE))
        request_history = list(self._history)
        request_history.append(request_message)

        response = self._model._generate_content(
            contents=request_history,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        # By default we're not adding incomplete interactions to history.
        if self._raise_on_blocked:
            if response.candidates[0].finish_reason not in _SUCCESSFUL_FINISH_REASONS:
                raise ResponseBlockedError(
                    message="The request was blocked.",
                    request_contents=request_history,
                    responses=[response],
                )

        # Adding the request and the first response candidate to history
        response_message = response.candidates[0].content
        # Response role is NOT set by the model.
        response_message.role = self._MODEL_ROLE
        self._history.append(request_message)
        self._history.append(response_message)
        return response

    async def _send_message_async(
        self,
        content: PartsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> "GenerationResponse":
        # Preparing the message history to send
        request_message = Content._from_gapic(_to_content(value=content, role=self._USER_ROLE))
        request_history = list(self._history)
        request_history.append(request_message)

        response = await self._model._generate_content_async(
            contents=request_history,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        # By default we're not adding incomplete interactions to history.
        if self._raise_on_blocked:
            if response.candidates[0].finish_reason not in _SUCCESSFUL_FINISH_REASONS:
                raise ResponseBlockedError(
                    message="The request was blocked.",
                    request_contents=request_history,
                    responses=[response],
                )
        # Adding the request and the first response candidate to history
        response_message = response.candidates[0].content
        # Response role is NOT set by the model.
        response_message.role = self._MODEL_ROLE
        self._history.append(request_message)
        self._history.append(response_message)
        return response

    def _send_message_streaming(
        self,
        content: PartsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> Iterable["GenerationResponse"]:
        # Preparing the message history to send
        request_message = Content._from_gapic(_to_content(value=content, role=self._USER_ROLE))
        request_history = list(self._history)
        request_history.append(request_message)

        stream = self._model._generate_content_streaming(
            contents=request_history,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        chunks = []
        full_response = None
        for chunk in stream:
            chunks.append(chunk)
            if full_response:
                _append_response(full_response, chunk)
            else:
                full_response = chunk
            # By default we're not adding incomplete interactions to history.
            if self._raise_on_blocked:
                if chunk.candidates[0].finish_reason not in _SUCCESSFUL_FINISH_REASONS:
                    raise ResponseBlockedError(
                        message="The request was blocked.",
                        request_contents=request_history,
                        responses=chunks,
                    )
            yield chunk
        if not full_response:
            return

        # Adding the request and the first response candidate to history
        response_message = full_response.candidates[0].content
        # Response role is NOT set by the model.
        response_message.role = self._MODEL_ROLE
        self._history.append(request_message)
        self._history.append(response_message)

    async def _send_message_streaming_async(
        self,
        content: PartsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        tools: Optional[List["Tool"]] = None,
    ) -> AsyncIterable["GenerationResponse"]:
        # Preparing the message history to send
        request_message = Content._from_gapic(_to_content(value=content, role=self._USER_ROLE))
        request_history = list(self._history)
        request_history.append(request_message)

        stream = await self._model._generate_content_streaming_async(
            contents=request_history,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
        )
        async def async_generator():
            chunks = []
            full_response = None
            async for chunk in stream:
                chunks.append(chunk)
                if full_response:
                    _append_response(full_response, chunk)
                else:
                    full_response = chunk
                # By default we're not adding incomplete interactions to history.
                if self._raise_on_blocked:
                    if chunk.candidates[0].finish_reason not in _SUCCESSFUL_FINISH_REASONS:
                        raise ResponseBlockedError(
                            message="The request was blocked.",
                            request_contents=request_history,
                            responses=chunks,
                        )
                yield chunk
            if not full_response:
                return
            # Adding the request and the first response candidate to history
            response_message = full_response.candidates[0].content
            # Response role is NOT set by the model.
            response_message.role = self._MODEL_ROLE
            self._history.append(request_message)
            self._history.append(response_message)
        return async_generator()


class ResponseBlockedError(Exception):
    def __init__(
        self,
        message: str,
        request_contents: List["Content"],
        responses: List["GenerationResponse"],
    ):
        super().__init__(message)
        self.request = request_contents
        self.responses = responses


# Structures


# Adding constructors to some common GAPIC types

# It's not possible to inherit from GAPIC structures.
# class GenerationConfig(content_types.GenerationConfig):
#     def __init__(
#         self,
#         *,
#         temperature: Optional[float] = None,
#         top_p: Optional[float] = None,
#         top_k: Optional[int] = None,
#         candidate_count: Optional[int] = None,
#         max_output_tokens: Optional[int] = None,
#         stop_sequences: Optional[List[str]] = None,
#         # logprobs: Optional[int] = None,
#         presence_penalty: Optional[float] = None,
#         frequency_penalty: Optional[float] = None,
#         # Requires tokenization support
#         # logit_bias: Optional[Dict[str, float]] = None,
#         echo: Optional[bool] = None,
#     ):
#         super().__init__(
#             temperature=temperature,
#             top_p=top_p,
#             top_k=top_k,
#             candidate_count=candidate_count,
#             max_output_tokens=max_output_tokens,
#             stop_sequences=stop_sequences,
#             # logprobs=logprobs,
#             presence_penalty=presence_penalty,
#             frequency_penalty=frequency_penalty,
#             # logit_bias=logit_bias,
#             echo=echo,
#         )


class GenerationConfig:
    def __init__(
        self,
        *,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        candidate_count: Optional[int] = None,
        max_output_tokens: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
    ):
        self._raw_generation_config = content_types.GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            candidate_count=candidate_count,
            max_output_tokens=max_output_tokens,
            stop_sequences=stop_sequences,
        )

    @classmethod
    def _from_gapic(
        cls,
        raw_generation_config: content_types.GenerationConfig,
    ) -> "Tool":
        response = cls()
        response._raw_generation_config = raw_generation_config
        return response

    @classmethod
    def from_dict(cls, generation_config_dict: Dict[str, Any]) -> "Tool":
        raw_generation_config = content_types.GenerationConfig(generation_config_dict)
        return cls._from_gapic(raw_generation_config=raw_generation_config)

    def __repr__(self):
        return self._raw_tool.__repr__()


class Tool:
    _raw_tool: tool_types.Tool

    def __init__(
        self,
        function_declarations: List["FunctionDeclaration"],
    ):
        gapic_function_declarations=[
            function_declaration._raw_function_declaration
            for function_declaration in function_declarations
        ]
        self._raw_tool = tool_types.Tool(
            function_declarations=gapic_function_declarations
        )

    @classmethod
    def _from_gapic(
        cls,
        raw_tool: tool_types.Tool,
    ) -> "Tool":
        response = cls([])
        response._raw_tool = raw_tool
        return response

    @classmethod
    def from_dict(cls, tool_dict: Dict[str, Any]) -> "Tool":
        tool_dict = copy.deepcopy(tool_dict)
        function_declarations = tool_dict["function_declarations"]
        for function_declaration in function_declarations:
            function_declaration["parameters"] = _convert_schema_dict_to_gapic(
                function_declaration["parameters"]
            )
        raw_tool = tool_types.Tool(tool_dict)
        return cls._from_gapic(raw_tool=raw_tool)

    def __repr__(self):
        return self._raw_tool.__repr__()


class FunctionDeclaration:
    def __init__(
        self,
        *,
        name: str,
        parameters: Dict[str, Any],
        description: Optional[str] = None,
    ):
        gapic_schema_dict = _convert_schema_dict_to_gapic(parameters)
        gapic_schema = aiplatform_types.Schema(gapic_schema_dict)
        self._raw_function_declaration = tool_types.FunctionDeclaration(
            name=name, description=description, parameters=gapic_schema
        )


def _convert_schema_dict_to_gapic(schema_dict: dict):
    gapic_schema_dict = copy.copy(schema_dict)
    if "type" in gapic_schema_dict:
        gapic_schema_dict["type_"] = gapic_schema_dict.pop("type").upper()
    if "format" in gapic_schema_dict:
        gapic_schema_dict["format_"] = gapic_schema_dict.pop("format")
    if "items" in gapic_schema_dict:
        gapic_schema_dict["items"] = _convert_schema_dict_to_gapic(
            gapic_schema_dict["items"]
        )
    properties = gapic_schema_dict.get("properties")
    if properties:
        for property_name, property_schema in properties.items():
            properties[property_name] = _convert_schema_dict_to_gapic(property_schema)
    return gapic_schema_dict


class GenerationResponse:

    def __init__(self):
        raw_response = prediction_service_types.GenerateContentResponse()
        self._raw_response = raw_response

    @classmethod
    def _from_gapic(
        cls,
        raw_response: prediction_service_types.GenerateContentResponse,
    ) -> "GenerationResponse":
        response = cls()
        response._raw_response = raw_response
        return response

    @classmethod
    def from_dict(cls, response_dict: Dict[str, Any]) -> "GenerationResponse":
        raw_response = prediction_service_types.GenerateContentResponse(response_dict)
        return cls._from_gapic(raw_response=raw_response)

    def __repr__(self):
        return self._raw_response.__repr__()

    @property
    def candidates(self) -> List["Candidate"]:
        return [
            Candidate._from_gapic(raw_candidate=raw_candidate)
            for raw_candidate in self._raw_response.candidates
        ]

    # # GenerationCandidate properties
    # @property
    # def finish_reason(self) -> content_types.Candidate.FinishReason:
    #     return self.candidates[0].finish_reason

    # GenerationPart properties
    @property
    def text(self) -> str:
        if len(self.candidates) > 1:
            raise ValueError("Multiple candidates are not supported")
        return self.candidates[0].content.parts[0].text


# StreamingGenerationResponse = Iterable[GenerationResponse]

class StreamingGenerationResponse:
    def __init__(self):
        self._stream = None
        self._on_completion = None

    def _private_init__(
        self,
        stream: Iterable[prediction_service_types.GenerateContentResponse],
        on_completion: Callable[[List[prediction_service_types.GenerateContentResponse]], None],
    ):
        self._stream = stream
        self._on_completion = on_completion

    def __iter__(self) -> Iterator[GenerationResponse]:
        chunks = []
        for chunk in self._stream:
            chunks.append(chunk)
            yield GenerationResponse._from_gapic(raw_response=chunk)
        if self._on_completion:
            self._on_completion(chunks)


# AsyncStreamingGenerationResponse = Awaitable[AsyncIterable[GenerationResponse]]
# AsyncStreamingGenerationResponse = AsyncIterable[GenerationResponse]

class AsyncStreamingGenerationResponse:
    def __init__(self):
        self._stream = None
        self._on_completion = None

    def _private_init__(
        self,
        stream: AsyncIterable[prediction_service_types.GenerateContentResponse],
        on_completion: Callable[[List[prediction_service_types.GenerateContentResponse]], None],
    ):
        self._stream = stream
        self._on_completion = on_completion

    async def __aiter__(self) -> AsyncIterator[GenerationResponse]:
        chunks = []
        async for chunk in self._stream:
            chunks.append(chunk)
            yield GenerationResponse._from_gapic(raw_response=chunk)
        if self._on_completion:
            self._on_completion(chunks)


class Candidate:

    def __init__(self):
        raw_candidate = content_types.Candidate()
        self._raw_candidate = raw_candidate

    @classmethod
    def _from_gapic(cls, raw_candidate: content_types.Candidate) -> "Candidate":
        candidate = cls()
        candidate._raw_candidate = raw_candidate
        return candidate

    @classmethod
    def from_dict(cls, candidate_dict: Dict[str, Any]) -> "Candidate":
        raw_candidate = content_types.Candidate(candidate_dict)
        return cls._from_gapic(raw_candidate=raw_candidate)

    def __repr__(self):
        return self._raw_candidate.__repr__()

    @property
    def content(self) -> "Content":
        return Content._from_gapic(
            raw_content=self._raw_candidate.content,
        )

    @property
    def finish_reason(self) -> content_types.Candidate.FinishReason:
        return self._raw_candidate.finish_reason

    @property
    def finish_message(self) -> str:
        return self._raw_candidate.finish_message

    @property
    def index(self) -> int:
        return self._raw_candidate.index

    @property
    def safety_ratings(self) -> Sequence[content_types.SafetyRating]:
        return self._raw_candidate.safety_ratings

    @property
    def citation_metadata(self) -> content_types.CitationMetadata:
        return self._raw_candidate.citation_metadata

    # GenerationPart properties
    @property
    def text(self) -> str:
        return self.content.text


class Content:

    def __init__(
        self,
        *,
        parts: List["Part"] = None,
        role: Optional[str] = None,
    ):
        raw_parts = [part._raw_part for part in parts or []]
        self._raw_content = content_types.Content(parts=raw_parts, role=role)

    @classmethod
    def _from_gapic(cls, raw_content: content_types.Content) -> "Content":
        content = cls()
        content._raw_content = raw_content
        return content

    @classmethod
    def from_dict(cls, content_dict: Dict[str, Any]) -> "Content":
        raw_content = content_types.Content(content_dict)
        return cls._from_gapic(raw_content=raw_content)

    def __repr__(self):
        return self._raw_content.__repr__()

    @property
    def parts(self) -> List["Part"]:
        return [
            Part._from_gapic(raw_part=raw_part)
            for raw_part in self._raw_content.parts
        ]

    @property
    def role(self) -> str:
        return self._raw_content.role

    @role.setter
    def role(self, role: str) -> None:
        self._raw_content.role = role

    # GenerationPart properties
    @property
    def text(self) -> str:
        if len(self.parts) > 1:
            raise ValueError("Multiple parts are not supported")
        return self.parts[0].text


class Part:

    def __init__(self):
        raw_part = content_types.Part()
        self._raw_part = raw_part

    @classmethod
    def _from_gapic(cls, raw_part: content_types.Part) -> "Part":
        part = cls()
        part._raw_part = raw_part
        return part

    @classmethod
    def from_dict(cls, part_dict: Dict[str, Any]) -> "Part":
        raw_part = content_types.Part(part_dict)
        return cls._from_gapic(raw_part=raw_part)

    def __repr__(self):
        return self._raw_part.__repr__()

    @staticmethod
    def from_data(data: bytes, mime_type: str) -> "Part":
        return Part._from_gapic(
            raw_part=content_types.Part(
                inline_data=content_types.Blob(data=data, mime_type=mime_type)
            )
        )

    @staticmethod
    def from_uri(uri: str, mime_type: str) -> "Part":
        return Part._from_gapic(
            raw_part=content_types.Part(
                file_data=content_types.FileData(file_uri=uri, mime_type=mime_type)
            )
        )

    @staticmethod
    def from_text(text: str) -> "Part":
        return Part._from_gapic(raw_part=content_types.Part(text=text))

    @staticmethod
    def from_image(image: "Image") -> "Part":
        return Part.from_data(data=image.data, mime_type=image._mime_type)

    @staticmethod
    def from_function_response(name: str, response: Dict[str, Any]) -> "Part":
        return Part._from_gapic(
            raw_part=content_types.Part(
                function_response=tool_types.FunctionResponse(
                    name=name,
                    response=response,
                )
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return self._raw_part.to_dict()

    @property
    def text(self) -> str:
        return self._raw_part.text

    @property
    def mime_type(self) -> Optional[str]:
        return self._raw_part.mime_type

    @property
    def inline_data(self) -> content_types.Blob:
        return self._raw_part.inline_data

    @property
    def file_data(self) -> content_types.FileData:
        return self._raw_part.file_data

    @property
    def function_call(self) -> tool_types.FunctionCall:
        return self._raw_part.function_call

    @property
    def function_response(self) -> tool_types.FunctionResponse:
        return self._raw_part.function_response

    @property
    def _image(self) -> "Image":
        return Image.from_bytes(data=self._raw_part.inline_data.data)


def _to_content(
    value: Union[
        content_types.Content,
        Content,
        str,
        "Image",
        Part,
        content_types.Part,
        List[Union[str, "Image", Part, content_types.Part]],
    ],
    role: str = GenerativeModel._USER_ROLE,
) -> content_types.Content:
    if not value:
        raise TypeError("value must not be empty")
    if isinstance(value, content_types.Content):
        return value
    if isinstance(value, Content):
        return value._raw_content
    if isinstance(value, (str, Image, Part, content_types.Part)):
        items = [value]
    elif isinstance(value, list):
        items = value
    else:
        raise TypeError(f"Unexpected value type: {value}")
    parts: List[content_types.Part] = []
    for item in items:
        if isinstance(item, content_types.Part):
            part = item
        elif isinstance(item, Part):
            part = item._raw_part
        elif isinstance(item, str):
            part = content_types.Part(text=item)
        elif isinstance(item, Image):
            part = content_types.Part(inline_data=content_types.Blob(data=item.data, mime_type=item._mime_type))
        elif isinstance(item, content_types.Content):
            raise TypeError(f"_to_content does not support a list of Content objects: {value}")
        else:
            raise TypeError(f"Unexpected item type: {item}")
        parts.append(part)
    return content_types.Content(parts=parts, role=role)


def _append_response(
    base_response: GenerationResponse,
    new_response: GenerationResponse,
):
    _append_gapic_response(
        base_response=base_response._raw_response,
        new_response=new_response._raw_response
    )


def _append_gapic_response(
    base_response: prediction_service_types.GenerateContentResponse,
    new_response: prediction_service_types.GenerateContentResponse,
):
    for idx, candidate in enumerate(new_response.candidates):
        assert candidate.index == idx
        if idx < len(base_response.candidates):
            assert base_response.candidates[idx].index == idx
            _append_gapic_candidate(base_response.candidates[idx], candidate)
        else:
            assert(idx == len(base_response.candidates))
            base_response.candidates.append(candidate)
    # prompt_feedback is always taken from the base_response
    # usage_metadata is always taken from the new_response
    if new_response.usage_metadata:
        base_response.usage_metadata = new_response.usage_metadata


def _append_gapic_candidate(
    base_candidate: content_types.Candidate,
    new_candidate: content_types.Candidate,
):
    # index: Is already correct
    assert base_candidate.index == new_candidate.index

    _append_gapic_content(base_candidate.content, new_candidate.content)

    # For these attributes, the last value wins
    if new_candidate.finish_reason:
        base_candidate.finish_reason = new_candidate.finish_reason
    if new_candidate.safety_ratings:
        base_candidate.safety_ratings = new_candidate.safety_ratings
    if new_candidate.finish_message:
        base_candidate.finish_message = new_candidate.finish_message
    if new_candidate.citation_metadata:
        base_candidate.citation_metadata = new_candidate.citation_metadata


def _append_gapic_content(
    base_content: content_types.Content,
    new_content: content_types.Content,
):
    # `role` should be the same
    assert base_content.role == new_content.role
    for part_idx, part in enumerate(new_content.parts):
        if part_idx < len(base_content.parts):
            _append_gapic_part(base_content.parts[part_idx], part)
        else:
            assert(part_idx == len(new_content.parts))
            base_content.parts.append(part)


def _append_gapic_part(
    base_part: content_types.Part,
    new_part: content_types.Part,
):
    # Text is appended. For other cases, new wins.
    if new_part.text:
        base_part.text += new_part.text
    else:
        base_part._pb = copy.deepcopy(new_part._pb)


_FORMAT_TO_MIME_TYPE = {
    "png": "image/png",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
}


class Image:
    """Image."""

    _image_bytes: bytes
    _loaded_image: Optional["PIL_Image.Image"] = None

    @staticmethod
    def load_from_file(location: str) -> "Image":
        """Loads image from file.

        Args:
            location: Local path from where to load the image.

        Returns:
            Loaded image as an `Image` object.
        """
        image_bytes = pathlib.Path(location).read_bytes()
        image = Image()
        image._image_bytes = image_bytes
        return image

    @staticmethod
    def from_bytes(data: bytes) -> "Image":
        """Loads image from image bytes.

        Args:
            data: Image bytes.

        Returns:
            Loaded image as an `Image` object.
        """
        image = Image()
        image._image_bytes = data
        return image

    @property
    def _pil_image(self) -> "PIL_Image.Image":
        if self._loaded_image is None:
            if not PIL_Image:
                raise RuntimeError(
                    "The PIL module is not available. Please install the Pillow package."
                )
            self._loaded_image = PIL_Image.open(io.BytesIO(self._image_bytes))
        return self._loaded_image

    @property
    def _mime_type(self) -> str:
        """Returns the MIME type of the image."""
        if PIL_Image:
            return _FORMAT_TO_MIME_TYPE[self._pil_image.format.lower()]
        else:
            # Fall back to jpeg
            return "image/jpeg"

    @property
    def data(self) -> bytes:
        """Returns the image data."""
        return self._image_bytes

    def _repr_png_(self):
        return self._pil_image._repr_png_()

    # For some reason PIL.JpegImagePlugin.JpegImageFile._repr_jpeg_ does not exist
    # def _repr_jpeg_(self):
    #     return self._pil_image._repr_jpeg_()

    # Does not help with images
    # def _repr_pretty_(self, *args, **kwargs):
    #     self._pil_image._repr_pretty_(*args, **kwargs)


####
# Tuning


TuningEvaluationSpec = tunable_models.TuningEvaluationSpec


class _TunableGenerativeModelMixin:
    """Model that can be tuned."""

    _TUNING_PIPELINE_URI = "https://us-kfp.pkg.dev/ml-pipeline/large-language-model-pipelines/tune-large-model/v3.0.0"

    def list_tuned_model_names(self) -> Sequence[str]:
        """Lists the names of tuned models.

        Returns:
            A list of tuned models that can be used with the `get_tuned_model` method.
        """
        tuning_model_id = self._model_name.rsplit("/", 1)[-1]
        return tunable_models._list_tuned_model_names(model_id=tuning_model_id)

    @classmethod
    def get_tuned_model(cls: Type[GenerativeModel], tuned_model_name: str) -> "GenerativeModel":
        """Loads the specified tuned language model."""

        tuned_vertex_model = aiplatform.Model(tuned_model_name)
        tuned_model_labels = tuned_vertex_model.labels

        tuning_model_id = tuned_model_labels.get(tunable_models._TUNING_BASE_MODEL_ID_LABEL_KEY)
        if not tuning_model_id:
            raise ValueError(
                f"The provided model {tuned_model_name} does not have a base model ID."
            )

        tuned_model_deployments = tuned_vertex_model.gca_resource.deployed_models
        if tuned_model_deployments:
            # Deploying the model
            endpoint_name = tuned_vertex_model.deploy().resource_name
        else:
            endpoint_name = tuned_model_deployments[0].endpoint

        base_model_id = tunable_models._get_model_id_from_tuning_model_id(tuning_model_id)

        model = cls(model_name=base_model_id)
        model._prediction_resource_name = endpoint_name
        return model

    def tune_model(
        self,
        training_data: Union[str, "tunable_models.pandas.core.frame.DataFrame"],
        *,
        train_steps: Optional[int] = None,
        learning_rate_multiplier: Optional[float] = None,
        model_display_name: Optional[str] = None,
        tuning_evaluation_spec: Optional["TuningEvaluationSpec"] = None,
        accelerator_type: Optional[tunable_models._ACCELERATOR_TYPE_TYPE] = None,
    ) -> "tunable_models._LanguageModelTuningJob":
        """Tunes a model based on training data.

        This method launches and returns an asynchronous model tuning job.
        Usage:
        ```
        tuning_job = model.tune_model(...)
        ... do some other work
        tuned_model = tuning_job.get_tuned_model()  # Blocks until tuning is complete
        ```

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            train_steps: Number of training batches to tune on (batch size is 8 samples).
            learning_rate: Deprecated. Use learning_rate_multiplier instead.
                Learning rate to use in tuning.
            learning_rate_multiplier: Learning rate multiplier to use in tuning.
            model_display_name: Custom display name for the tuned model.
            tuning_evaluation_spec: Specification for the model evaluation during tuning.
            accelerator_type: Type of accelerator to use. Can be "TPU" or "GPU".

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        return tunable_models._TunableModelMixin.tune_model(
            self=self,
            training_data=training_data,
            train_steps=train_steps,
            learning_rate_multiplier=learning_rate_multiplier,
            tuning_job_location=aiplatform_initializer.global_config.location,
            tuned_model_location=aiplatform_initializer.global_config.location,
            model_display_name=model_display_name,
            tuning_evaluation_spec=tuning_evaluation_spec,
            accelerator_type=accelerator_type,
        )

    def _tune_model(
        self,
        training_data: Union[str, "tunable_models.pandas.core.frame.DataFrame"],
        *,
        tuning_parameters: Dict[str, Any],
        tuning_job_location: Optional[str] = None,
        tuned_model_location: Optional[str] = None,
        model_display_name: Optional[str] = None,
    ):
        """Tunes a model based on training data.

        This method launches a model tuning job that can take some time.

        Args:
            training_data: A Pandas DataFrame or a URI pointing to data in JSON lines format.
                The dataset schema is model-specific.
                See https://cloud.google.com/vertex-ai/docs/generative-ai/models/tune-models#dataset_format
            tuning_parameters: Tuning pipeline parameter values.
            tuning_job_location: GCP location where the tuning job should be run.
            tuned_model_location: GCP location where the tuned model should be deployed.
            model_display_name: Custom display name for the tuned model.

        Returns:
            A `LanguageModelTuningJob` object that represents the tuning job.
            Calling `job.result()` blocks until the tuning is complete and returns a `LanguageModel` object.

        Raises:
            ValueError: If the "tuning_job_location" value is not supported
            ValueError: If the "tuned_model_location" value is not supported
            RuntimeError: If the model does not support tuning
        """
        if tuning_job_location not in tunable_models._TUNING_LOCATIONS:
            raise ValueError(
                "Please specify the tuning job location (`tuning_job_location`)."
                f"Tuning is supported in the following locations: {tunable_models._TUNING_LOCATIONS}"
            )
        if tuned_model_location not in tunable_models._TUNED_MODEL_LOCATIONS:
            raise ValueError(
                "Tuned model deployment is only supported in the following locations: "
                f"{tunable_models._TUNED_MODEL_LOCATIONS}"
            )

        tuning_model_id = self._model_name.rsplit("/", 1)[-1]
        pipeline_job = tunable_models._launch_tuning_job(
            training_data=training_data,
            model_id=tuning_model_id,
            tuning_pipeline_uri=self._TUNING_PIPELINE_URI,
            tuning_parameters=tuning_parameters,
            model_display_name=model_display_name,
            tuning_job_location=tuning_job_location,
            tuned_model_location=tuned_model_location,
        )

        job = tunable_models._LanguageModelTuningJob(
            base_model=self,
            job=pipeline_job,
        )
        return job


class PreviewGenerativeModel(GenerativeModel, _TunableGenerativeModelMixin):
    pass
