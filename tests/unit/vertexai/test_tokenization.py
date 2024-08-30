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

import hashlib
import io
import os
import shutil
import tempfile
from typing import List
from unittest import mock
from vertexai.generative_models import (
    Content,
    Image,
    Part,
    FunctionDeclaration,
    Tool,
)

from vertexai.tokenization import _tokenizer_loading
from vertexai.tokenization._tokenizers import (
    CountTokensResult,
    TokensInfo,
    _TextsAccumulator,
    get_tokenizer_for_model,
)
import pytest
import sentencepiece as spm
from sentencepiece import sentencepiece_model_pb2, sentencepiece_pb2
from google.cloud.aiplatform_v1beta1.types import (
    content as gapic_content_types,
    tool as gapic_tool_types,
    openapi,
)
from google.protobuf import struct_pb2


_TOKENIZER_NAME = "google/gemma"
_MODEL_NAME = "gemini-1.5-pro"
# The 0~99 ModelProto.pieces element is reserved for BYTE type in this unit test.
_TOKENIZER_MODEL = sentencepiece_model_pb2.ModelProto(
    pieces=[
        sentencepiece_model_pb2.ModelProto.SentencePiece(
            type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.BYTE
        )
        for i in range(100)
    ]
    + [
        sentencepiece_model_pb2.ModelProto.SentencePiece(
            type=sentencepiece_model_pb2.ModelProto.SentencePiece.Type.NORMAL
        )
        for i in range(101, 200)
    ]
)

_SENTENCE_1 = "hello world"
_SENTENCE_2 = "what's the weather today"
_SENTENCE_3 = "It's 70 degrees."
_SENTENCE_4 = "this sentence gets bytes type"
_EMPTY_SENTENCE = ""

_TOKENS_MAP = {
    _EMPTY_SENTENCE: {"ids": [], "tokens": []},
    _SENTENCE_1: {"ids": [101, 102], "tokens": [b"hello", b" world"]},
    _SENTENCE_2: {
        "ids": [104, 105, 106, 107, 108, 109],
        "tokens": [b"what", b"'", b"s", b"the", b"weather", b"today"],
    },
    _SENTENCE_3: {
        "ids": [107, 108, 109, 110, 111, 112, 113, 114],
        "tokens": [b"It", b"'", b"s", b"", b"7", b"0", b"degrees", b"."],
    },
    _SENTENCE_4: {
        "ids": [0, 1],  # ids 0 and 1 for BYTE test case.
        "tokens": ["<0x41>", "<0x42>"],  # expected tokenizer output are [b"A", b"B"]
    },
}

# _VALID_CONTENTS_TYPE represents test data in "contents, encode_input, encode_output, roles" schema.
_VALID_CONTENTS_TYPE = [
    (_EMPTY_SENTENCE, [_EMPTY_SENTENCE], [], []),
    (_SENTENCE_1, [_SENTENCE_1], [_TOKENS_MAP[_SENTENCE_1]], ["user"]),
    (
        [_SENTENCE_1, _SENTENCE_2],
        [_SENTENCE_1, _SENTENCE_2],
        [_TOKENS_MAP[_SENTENCE_1], _TOKENS_MAP[_SENTENCE_2]],
        ["user"] * 2,
    ),
    (Part.from_text(_SENTENCE_1), [_SENTENCE_1], [_TOKENS_MAP[_SENTENCE_1]], ["user"]),
    (
        [
            Part.from_text(_SENTENCE_1),
            Part.from_text(_SENTENCE_2),
            Part.from_text(_EMPTY_SENTENCE),
        ],
        [_SENTENCE_1, _SENTENCE_2, _EMPTY_SENTENCE],
        [
            _TOKENS_MAP[_SENTENCE_1],
            _TOKENS_MAP[_SENTENCE_2],
            _TOKENS_MAP[_EMPTY_SENTENCE],
        ],
        ["user"] * 3,
    ),
    (
        Content(role="user", parts=[Part.from_text(_SENTENCE_1)]),
        [_SENTENCE_1],
        [_TOKENS_MAP[_SENTENCE_1]],
        ["user"],
    ),
    (
        Content(
            role="user",
            parts=[
                Part.from_text(_SENTENCE_1),
                Part.from_text(_SENTENCE_2),
                Part.from_text(_EMPTY_SENTENCE),
            ],
        ),
        [_SENTENCE_1, _SENTENCE_2, _EMPTY_SENTENCE],
        [
            _TOKENS_MAP[_SENTENCE_1],
            _TOKENS_MAP[_SENTENCE_2],
            _TOKENS_MAP[_EMPTY_SENTENCE],
        ],
        ["user"] * 3,
    ),
    (
        [
            Content(
                role="user",
                parts=[
                    Part.from_text(_SENTENCE_1),
                    Part.from_text(_SENTENCE_2),
                ],
            ),
            Content(
                role="model",
                parts=[
                    Part.from_text(_SENTENCE_3),
                ],
            ),
        ],
        [_SENTENCE_1, _SENTENCE_2, _SENTENCE_3],
        [
            _TOKENS_MAP[_SENTENCE_1],
            _TOKENS_MAP[_SENTENCE_2],
            _TOKENS_MAP[_SENTENCE_3],
        ],
        ["user", "user", "model"],
    ),
    (
        [
            {
                "role": "user",
                "parts": [
                    {"text": _SENTENCE_1},
                    {"text": _SENTENCE_2},
                ],
            },
            {"role": "model", "parts": [{"text": _SENTENCE_3}]},
        ],
        [_SENTENCE_1, _SENTENCE_2, _SENTENCE_3],
        [
            _TOKENS_MAP[_SENTENCE_1],
            _TOKENS_MAP[_SENTENCE_2],
            _TOKENS_MAP[_SENTENCE_3],
        ],
        ["user", "user", "model"],
    ),
]


_LIST_OF_UNSUPPORTED_CONTENTS = [
    Part.from_uri("gs://bucket/object", mime_type="mime_type"),
    Part.from_data(b"inline_data_bytes", mime_type="mime_type"),
    Content(
        role="user",
        parts=[Part.from_uri("gs://bucket/object", mime_type="mime_type")],
    ),
    Content(
        role="user",
        parts=[Part.from_data(b"inline_data_bytes", mime_type="mime_type")],
    ),
]

_NESTED_STRUCT_1 = struct_pb2.Struct(
    fields={"string_key": struct_pb2.Value(string_value="value1")}
)
_NESTED_STRUCT_2 = struct_pb2.Struct(
    fields={
        "list_key": struct_pb2.Value(
            list_value=struct_pb2.ListValue(
                values=[struct_pb2.Value(string_value="value2")]
            )
        )
    }
)
_NESTED_STRUCT_3 = struct_pb2.Struct(
    fields={
        "struct_key": struct_pb2.Value(
            struct_value=struct_pb2.Struct(
                fields={"string_key": struct_pb2.Value(string_value="value3")}
            )
        )
    }
)
_STRUCT = struct_pb2.Struct(
    fields={
        "string_key": struct_pb2.Value(string_value="value4"),
        "list_key": struct_pb2.Value(
            list_value=struct_pb2.ListValue(
                values=[struct_pb2.Value(string_value="value5")]
            )
        ),
        "struct_key1": struct_pb2.Value(struct_value=_NESTED_STRUCT_1),
        "struct_key2": struct_pb2.Value(struct_value=_NESTED_STRUCT_2),
        "struct_key3": struct_pb2.Value(struct_value=_NESTED_STRUCT_3),
    }
)
_STRUCT_TEXTS = [
    "struct_key3",
    "struct_key1",
    "list_key",
    "string_key",
    "struct_key2",
    "struct_key",
    "string_key",
    "value3",
    "string_key",
    "value1",
    "value5",
    "value4",
    "list_key",
    "value2",
]


@pytest.fixture
def mock_sp_processor():
    with mock.patch.object(
        spm,
        "SentencePieceProcessor",
    ) as sp_mock:
        sp_mock.return_value.LoadFromSerializedProto.return_value = True
        sp_mock.return_value.encode.side_effect = _encode_as_ids
        sp_mock.return_value.EncodeAsImmutableProto.side_effect = (
            _encode_as_immutable_proto
        )
        yield sp_mock


def _encode_as_ids(contents: List[str]):
    return [
        (
            _TOKENS_MAP[content]["ids"]
            if content in _TOKENS_MAP
            # Returns stable ids arrary when content is not predefined.
            else [0] * len(content.split(" "))
        )
        for content in contents
    ]


def _build_sentencepiece_text(content: str):
    return [
        sentencepiece_pb2.SentencePieceText.SentencePiece(piece=token, id=token_id)
        for token_id, token in zip(
            _TOKENS_MAP[content]["ids"], _TOKENS_MAP[content]["tokens"]
        )
    ]


def _encode_as_immutable_proto(contents: List[str]):
    return [
        sentencepiece_pb2.SentencePieceText(pieces=_build_sentencepiece_text(content))
        for content in contents
    ]


@pytest.fixture
def mock_requests_get():
    with mock.patch("requests.get") as requests_get_mock:
        model = _TOKENIZER_MODEL
        requests_get_mock.return_value.content = model.SerializeToString()
        yield requests_get_mock


@pytest.fixture
def mock_hashlib_sha256():
    with mock.patch("hashlib.sha256") as sha256_mock:
        sha256_mock.return_value.hexdigest.return_value = (
            "61a7b147390c64585d6c3543dd6fc636906c9af3865a5548f27f31aee1d4c8e2"
        )
        yield sha256_mock


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


@pytest.mark.usefixtures("mock_requests_get", "mock_hashlib_sha256")
class TestTokenizers:
    """Unit tests for the tokenizers."""

    def setup_method(self):
        model_dir = os.path.join(tempfile.gettempdir(), "vertexai_tokenizer_model")
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)

    def test_valid_contents_type_for_bytes_token_type(self, mock_sp_processor):
        _tokenizer_loading.get_sentencepiece.cache_clear()
        assert get_tokenizer_for_model(_MODEL_NAME).compute_tokens(
            [_SENTENCE_4]
        ).tokens_info == (
            [TokensInfo(token_ids=[0, 1], tokens=[b"A", b"B"], role="user")]
        )
        assert get_tokenizer_for_model(_MODEL_NAME).count_tokens(
            [_SENTENCE_4]
        ) == CountTokensResult(total_tokens=2)
        mock_sp_processor.return_value.EncodeAsImmutableProto.assert_called_once_with(
            [_SENTENCE_4]
        )

    @pytest.mark.parametrize(
        "contents, encode_input, encode_output, roles",
        _VALID_CONTENTS_TYPE,
    )
    def test_count_tokens_valid_contents_type(
        self, mock_sp_processor, contents, encode_input, encode_output, roles
    ):
        _tokenizer_loading.get_sentencepiece.cache_clear()
        expected_count = CountTokensResult(
            sum(len(output["ids"]) for output in encode_output)
        )
        assert (
            get_tokenizer_for_model(_MODEL_NAME).count_tokens(contents)
            == expected_count
        )
        mock_sp_processor.return_value.encode.assert_called_once_with(encode_input)

    @pytest.mark.parametrize(
        "contents, encode_input, encode_output, roles",
        _VALID_CONTENTS_TYPE,
    )
    def testcompute_tokens_valid_contents_type(
        self, mock_sp_processor, contents, encode_input, encode_output, roles
    ):
        _tokenizer_loading.get_sentencepiece.cache_clear()
        assert (
            get_tokenizer_for_model(_MODEL_NAME).compute_tokens(contents)
        ).tokens_info == (
            [
                TokensInfo(token_ids=output["ids"], tokens=output["tokens"], role=role)
                for role, output in zip(roles, encode_output)
            ]
            if len(encode_output) > 0
            else [TokensInfo(token_ids=[], tokens=[], role="user")]
        )

        mock_sp_processor.return_value.EncodeAsImmutableProto.assert_called_once_with(
            encode_input
        )

    @pytest.mark.parametrize(
        "contents",
        _LIST_OF_UNSUPPORTED_CONTENTS,
    )
    def test_count_tokens_unsupported_contents_type(
        self,
        mock_sp_processor,
        contents,
    ):
        _tokenizer_loading.get_sentencepiece.cache_clear()
        with pytest.raises(ValueError) as e:
            get_tokenizer_for_model(_MODEL_NAME).count_tokens(contents)
        e.match("Tokenizers do not support non-text content types.")

    def test_system_instruction_count_tokens(self, mock_sp_processor):
        _tokenizer_loading.get_sentencepiece.cache_clear()
        tokenizer = get_tokenizer_for_model(_MODEL_NAME)
        result = tokenizer.count_tokens(
            ["hello world"], system_instruction=["You are a chatbot."]
        )
        assert result.total_tokens == 6

    def test_function_call_count_tokens(self, mock_sp_processor):
        tokenizer = get_tokenizer_for_model(_MODEL_NAME)
        part = Part._from_gapic(
            gapic_content_types.Part(
                function_call=gapic_tool_types.FunctionCall(
                    name="test_function_call",
                    args=_STRUCT,
                ),
            )
        )

        result = tokenizer.count_tokens(part)

        assert result.total_tokens

    def test_function_response_count_tokens(self, mock_sp_processor):
        tokenizer = get_tokenizer_for_model(_MODEL_NAME)
        part = Part._from_gapic(
            gapic_content_types.Part(
                function_response=gapic_tool_types.FunctionResponse(
                    name="test_function_response", response=_STRUCT
                ),
            )
        )

        result = tokenizer.count_tokens(part)

        assert result.total_tokens

    def test_tools_count_tokens(self, mock_sp_processor):
        tokenizer = get_tokenizer_for_model(_MODEL_NAME)
        get_current_weather_func = FunctionDeclaration.from_func(get_current_weather)
        weather_tool = Tool(
            function_declarations=[get_current_weather_func],
        )

        result = tokenizer.count_tokens(contents=[], tools=[weather_tool])

        assert result.total_tokens

    def test_image_mime_types(self, mock_sp_processor):
        # Importing external library lazily to reduce the scope of import errors.
        from PIL import Image as PIL_Image  # pylint: disable=g-import-not-at-top

        pil_image: PIL_Image.Image = PIL_Image.new(mode="RGB", size=(200, 200))
        image_bytes_io = io.BytesIO()
        pil_image.save(image_bytes_io, format="PNG")
        _tokenizer_loading.get_sentencepiece.cache_clear()
        with pytest.raises(ValueError) as e:
            get_tokenizer_for_model(_MODEL_NAME).count_tokens(
                Image.from_bytes(image_bytes_io.getvalue())
            )
        e.match("Tokenizers do not support Image content type.")


class TestModelLoad:
    def setup_method(self):
        model_dir = os.path.join(tempfile.gettempdir(), "vertexai_tokenizer_model")
        if os.path.exists(model_dir):
            shutil.rmtree(model_dir)
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)

    def get_cache_path(self, file_url: str):
        model_dir = os.path.join(tempfile.gettempdir(), "vertexai_tokenizer_model")
        filename = hashlib.sha1(file_url.encode()).hexdigest()
        return os.path.join(model_dir, filename)

    def test_download_and_save_to_cache(self, mock_hashlib_sha256, mock_requests_get):
        _tokenizer_loading._load_model_proto_bytes(_TOKENIZER_NAME)
        cache_path = self.get_cache_path(
            _tokenizer_loading._TOKENIZERS[_TOKENIZER_NAME].model_url
        )
        assert os.path.exists(cache_path)
        mock_requests_get.assert_called_once()
        with open(cache_path, "rb") as f:
            assert f.read() == _TOKENIZER_MODEL.SerializeToString()

    @mock.patch("hashlib.sha256", autospec=True)
    def test_download_file_is_corrupted(self, hash_mock, mock_requests_get):
        hash_mock.return_value.hexdigest.return_value = "inconsistent_hash"
        with pytest.raises(ValueError) as e:
            _tokenizer_loading._load_model_proto_bytes(_TOKENIZER_NAME)
        e.match(regexp=r"Downloaded model file is corrupted.*")

        mock_requests_get.assert_called_once()

    def test_load_model_proto_from_cache(self, mock_hashlib_sha256, mock_requests_get):
        cache_path = self.get_cache_path(
            _tokenizer_loading._TOKENIZERS[_TOKENIZER_NAME].model_url
        )
        model_contents = sentencepiece_model_pb2.ModelProto(
            pieces=[sentencepiece_model_pb2.ModelProto.SentencePiece(piece="a")]
        ).SerializeToString()
        with open(cache_path, "wb") as f:
            f.write(model_contents)
        assert (
            _tokenizer_loading._load_model_proto_bytes(_TOKENIZER_NAME)
            == model_contents
        )
        assert os.path.exists(cache_path)
        mock_requests_get.assert_not_called()

    @mock.patch("hashlib.sha256", autospec=True)
    def test_load_model_proto_from_corrupted_cache(self, hash_mock, mock_requests_get):
        cache_path = self.get_cache_path(
            _tokenizer_loading._TOKENIZERS[_TOKENIZER_NAME].model_url
        )
        model_contents = sentencepiece_model_pb2.ModelProto(
            pieces=[sentencepiece_model_pb2.ModelProto.SentencePiece(piece="a")]
        ).SerializeToString()
        with open(cache_path, "wb") as f:
            f.write(model_contents)
        hash_mock.return_value.hexdigest.side_effect = [
            "inconsistent_hash",  # first read from cache
            _tokenizer_loading._TOKENIZERS[
                _TOKENIZER_NAME
            ].model_hash,  # then read from network
        ]
        _tokenizer_loading._load_model_proto_bytes(_TOKENIZER_NAME)
        mock_requests_get.assert_called_once()
        with open(cache_path, "rb") as f:
            assert f.read() == _TOKENIZER_MODEL.SerializeToString()


class TestTextsAccumulator:
    def setup_method(self):
        self.texts_accumulator = _TextsAccumulator()

    def test_function_declaration_unsupported_field(self):
        function_declaration = gapic_tool_types.FunctionDeclaration(
            parameters=openapi.Schema(nullable=True)
        )
        with pytest.raises(ValueError):
            self.texts_accumulator.add_tool(
                gapic_tool_types.Tool(function_declarations=[function_declaration])
            )

    def test_function_call_unsupported_field(self):
        function_call = gapic_tool_types.FunctionCall(
            name="test_function_call",
            args=struct_pb2.Struct(
                fields={
                    "bool_key": struct_pb2.Value(bool_value=True),
                }
            ),
        )
        with pytest.raises(ValueError):
            self.texts_accumulator.add_function_call(function_call)

    def test_function_response_unsupported_field(self):
        function_call = gapic_tool_types.FunctionResponse(
            name="test_function_response",
            response=struct_pb2.Struct(
                fields={
                    "bool_key": struct_pb2.Value(bool_value=True),
                }
            ),
        )
        with pytest.raises(ValueError):
            self.texts_accumulator.add_function_response(function_call)

    def test_function_declaration(self):
        schema1 = openapi.Schema(
            format="schema1_format", description="schema1_description"
        )
        schema2 = openapi.Schema(
            format="schema2_format", description="schema2_description"
        )
        example = struct_pb2.Value(string_value="value1")
        function_declaration = gapic_tool_types.FunctionDeclaration(
            name="function_declaration_name",
            description="function_declaration_description",
            parameters=openapi.Schema(
                format="schema_format",
                description="schema_description",
                enum=["schema_enum1", "schema_enum2"],
                required=["schema_required1", "schema_required2"],
                items=schema1,
                properties={"property_key": schema2},
                example=example,
            ),
        )

        self.texts_accumulator.add_tool(
            gapic_tool_types.Tool(function_declarations=[function_declaration])
        )
        assert self.texts_accumulator.get_texts() == [
            "function_declaration_name",
            "function_declaration_description",
            "schema_format",
            "schema_description",
            "schema_enum1",
            "schema_enum2",
            "schema_required1",
            "schema_required2",
            "schema1_format",
            "schema1_description",
            "property_key",
            "schema2_format",
            "schema2_description",
            "value1",
        ]

    def test_function_call(self):
        function_call = gapic_tool_types.FunctionCall(
            name="test_function_call",
            args=_STRUCT,
        )

        self.texts_accumulator.add_function_call(function_call)

        assert (
            self.texts_accumulator.get_texts() == ["test_function_call"] + _STRUCT_TEXTS
        )

    def test_function_response(self):
        function_response = gapic_tool_types.FunctionResponse(
            name="test_function_response", response=_STRUCT
        )

        self.texts_accumulator.add_function_response(function_response)

        assert (
            self.texts_accumulator.get_texts()
            == ["test_function_response"] + _STRUCT_TEXTS
        )
