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

import os
import pytest
import nltk

from nltk.corpus import udhr
from google.cloud import aiplatform
from vertexai.preview.tokenization import (
    get_tokenizer_for_model as tokenizer_preview,
)
from vertexai.tokenization._tokenizers import (
    get_tokenizer_for_model as tokenizer_ga,
)
from vertexai.generative_models import (
    GenerativeModel,
    Part,
    Tool,
)
from tests.system.aiplatform import e2e_base
from google import auth
from google.cloud.aiplatform_v1beta1.types import (
    content as gapic_content_types,
    tool as gapic_tool_types,
    openapi,
)
from google.protobuf import struct_pb2


_MODELS = ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
_CORPUS = [
    "udhr",
]
_CORPUS_LIB = [
    udhr,
]
_VERSIONED_TOKENIZER = [tokenizer_preview, tokenizer_ga]
_MODEL_CORPUS_PARAMS = [
    (get_tokenizer_for_model, model_name, corpus_name, corpus_lib)
    for get_tokenizer_for_model in _VERSIONED_TOKENIZER
    for model_name in _MODELS
    for (corpus_name, corpus_lib) in zip(_CORPUS, _CORPUS_LIB)
]
_STRUCT = struct_pb2.Struct(
    fields={
        "string_key": struct_pb2.Value(string_value="value"),
    }
)
_FUNCTION_CALL = gapic_tool_types.FunctionCall(name="test_function_call", args=_STRUCT)
_FUNCTION_RESPONSE = gapic_tool_types.FunctionResponse(
    name="function_response",
    response=_STRUCT,
)


_SCHEMA_1 = openapi.Schema(format="schema1_format", description="schema1_description")
_SCHEMA_2 = openapi.Schema(format="schema2_format", description="schema2_description")
_EXAMPLE = struct_pb2.Value(string_value="value1")

_FUNCTION_DECLARATION_1 = gapic_tool_types.FunctionDeclaration(
    name="function_declaration_name",
    description="function_declaration_description",
    parameters=openapi.Schema(
        format="schema_format",
        description="schema_description",
        enum=["schema_enum1", "schema_enum2"],
        required=["schema_required1", "schema_required2"],
        items=_SCHEMA_2,
        properties={"property_key": _SCHEMA_1},
        example=_EXAMPLE,
    ),
)
_FUNCTION_DECLARATION_2 = gapic_tool_types.FunctionDeclaration(
    parameters=openapi.Schema(
        nullable=True,
        default=struct_pb2.Value(string_value="value1"),
        min_items=0,
        max_items=0,
        min_properties=0,
        max_properties=0,
        minimum=0,
        maximum=0,
        min_length=0,
        max_length=0,
        pattern="pattern",
    ),
    response=_SCHEMA_1,
)

STAGING_API_ENDPOINT = "STAGING_ENDPOINT"
PROD_API_ENDPOINT = "PROD_ENDPOINT"


@pytest.mark.parametrize(
    "api_endpoint_env_name", [STAGING_API_ENDPOINT, PROD_API_ENDPOINT]
)
class TestTokenization(e2e_base.TestEndToEnd):
    """System tests for tokenization."""

    _temp_prefix = "temp_tokenization_test_"

    @pytest.fixture(scope="function", autouse=True)
    def setup_method(self, api_endpoint_env_name):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        if api_endpoint_env_name == STAGING_API_ENDPOINT:
            api_endpoint = os.getenv(api_endpoint_env_name)
        else:
            api_endpoint = None
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
            api_endpoint=api_endpoint,
        )

    @pytest.mark.parametrize(
        "get_tokenizer_for_model, model_name, corpus_name, corpus_lib",
        _MODEL_CORPUS_PARAMS,
    )
    def test_count_tokens_local(
        self,
        get_tokenizer_for_model,
        model_name,
        corpus_name,
        corpus_lib,
        api_endpoint_env_name,
    ):
        # The Gemini 1.5 flash model requires the model version
        # number suffix (001) in staging only
        if api_endpoint_env_name == STAGING_API_ENDPOINT:
            model_name = model_name + "-001"
        tokenizer = get_tokenizer_for_model(model_name)
        model = GenerativeModel(model_name)
        nltk.download(corpus_name, quiet=True)
        for id, book in enumerate(corpus_lib.fileids()):
            text = corpus_lib.raw(book)
            service_result = model.count_tokens(text)
            local_result = tokenizer.count_tokens(text)
            assert service_result.total_tokens == local_result.total_tokens

    @pytest.mark.parametrize(
        "get_tokenizer_for_model, model_name, corpus_name, corpus_lib",
        _MODEL_CORPUS_PARAMS,
    )
    def test_compute_tokens(
        self,
        get_tokenizer_for_model,
        model_name,
        corpus_name,
        corpus_lib,
        api_endpoint_env_name,
    ):
        # The Gemini 1.5 flash model requires the model version
        # number suffix (001) in staging only
        if api_endpoint_env_name == STAGING_API_ENDPOINT:
            model_name = model_name + "-001"
        tokenizer = get_tokenizer_for_model(model_name)
        model = GenerativeModel(model_name)
        nltk.download(corpus_name, quiet=True)
        for id, book in enumerate(corpus_lib.fileids()):
            text = corpus_lib.raw(book)
            response = model.compute_tokens(text)
            local_result = tokenizer.compute_tokens(text)
            for local, service in zip(local_result.tokens_info, response.tokens_info):
                assert local.tokens == service.tokens
                assert local.token_ids == service.token_ids

    @pytest.mark.parametrize(
        "model_name",
        _MODELS,
    )
    def test_count_tokens_system_instruction(self, model_name):
        tokenizer = tokenizer_preview(model_name)
        model = GenerativeModel(model_name, system_instruction=["You are a chatbot."])

        assert (
            tokenizer.count_tokens(
                "hello", system_instruction=["You are a chatbot."]
            ).total_tokens
            == model.count_tokens("hello").total_tokens
        )

    @pytest.mark.parametrize(
        "model_name",
        _MODELS,
    )
    def test_count_tokens_system_instruction_is_function_call(self, model_name):
        part = Part._from_gapic(gapic_content_types.Part(function_call=_FUNCTION_CALL))

        tokenizer = tokenizer_preview(model_name)
        model = GenerativeModel(model_name, system_instruction=[part])

        assert (
            tokenizer.count_tokens("hello", system_instruction=[part]).total_tokens
            == model.count_tokens("hello").total_tokens
        )

    @pytest.mark.parametrize(
        "model_name",
        _MODELS,
    )
    def test_count_tokens_system_instruction_is_function_response(self, model_name):
        part = Part._from_gapic(
            gapic_content_types.Part(function_response=_FUNCTION_RESPONSE)
        )
        tokenizer = tokenizer_preview(model_name)
        model = GenerativeModel(model_name, system_instruction=[part])

        assert tokenizer.count_tokens(part, system_instruction=[part]).total_tokens
        assert (
            tokenizer.count_tokens("hello", system_instruction=[part]).total_tokens
            == model.count_tokens("hello").total_tokens
        )

    @pytest.mark.parametrize(
        "model_name",
        _MODELS,
    )
    def test_count_tokens_tool_is_function_declaration(self, model_name):
        tokenizer = tokenizer_preview(model_name)
        model = GenerativeModel(model_name)
        tool1 = Tool._from_gapic(
            gapic_tool_types.Tool(function_declarations=[_FUNCTION_DECLARATION_1])
        )
        tool2 = Tool._from_gapic(
            gapic_tool_types.Tool(function_declarations=[_FUNCTION_DECLARATION_2])
        )

        assert tokenizer.count_tokens("hello", tools=[tool1]).total_tokens
        with pytest.raises(ValueError):
            tokenizer.count_tokens("hello", tools=[tool2]).total_tokens
        assert (
            tokenizer.count_tokens("hello", tools=[tool1]).total_tokens
            == model.count_tokens("hello", tools=[tool1]).total_tokens
        )

    @pytest.mark.parametrize(
        "model_name",
        _MODELS,
    )
    def test_count_tokens_content_is_function_call(self, model_name):
        part = Part._from_gapic(gapic_content_types.Part(function_call=_FUNCTION_CALL))
        tokenizer = tokenizer_preview(model_name)
        model = GenerativeModel(model_name)

        assert tokenizer.count_tokens(part).total_tokens
        assert (
            tokenizer.count_tokens(part).total_tokens
            == model.count_tokens(part).total_tokens
        )

    @pytest.mark.parametrize(
        "model_name",
        _MODELS,
    )
    def test_count_tokens_content_is_function_response(self, model_name):
        part = Part._from_gapic(
            gapic_content_types.Part(function_response=_FUNCTION_RESPONSE)
        )
        tokenizer = tokenizer_preview(model_name)
        model = GenerativeModel(model_name)

        assert tokenizer.count_tokens(part).total_tokens
        assert (
            tokenizer.count_tokens(part).total_tokens
            == model.count_tokens(part).total_tokens
        )
