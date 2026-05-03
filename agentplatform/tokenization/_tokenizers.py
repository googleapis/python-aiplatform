# Copyright 2026 Google LLC
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

import dataclasses
from typing import (
    Iterable,
    List,
    Sequence,
    Optional,
    Union,
)

from agentplatform.tokenization._tokenizer_loading import (
    get_sentencepiece,
    get_tokenizer_name,
    load_model_proto,
)
from google.cloud.aiplatform_v1beta1.types import (
    content as gapic_content_types,
    tool as gapic_tool_types,
    openapi,
)
from google3.third_party.sentencepiece.src import sentencepiece_model_pb2
from google.protobuf import struct_pb2

ContentsType = Union[
    str,
    gapic_content_types.Part,
    Sequence[Union[str, gapic_content_types.Part]],
    gapic_content_types.Content,
    Sequence[gapic_content_types.Content],
]


def _to_gapic_contents(contents: ContentsType) -> List[gapic_content_types.Content]:
    if isinstance(contents, str):
        return [
            gapic_content_types.Content(
                parts=[gapic_content_types.Part(text=contents)], role="user"
            )
        ]
    elif hasattr(contents, "text"):
        return [gapic_content_types.Content(parts=[contents], role="user")]
    elif isinstance(contents, gapic_content_types.Content):
        return [contents]
    elif isinstance(contents, Sequence):
        if not contents:
            return []
        if isinstance(contents[0], gapic_content_types.Content):
            return list(contents)
        parts = []
        for p in contents:
            if isinstance(p, str):
                parts.append(gapic_content_types.Part(text=p))
            else:
                parts.append(p)
        return [gapic_content_types.Content(parts=parts, role="user")]
    else:
        raise ValueError(f"Unsupported type for contents: {type(contents)}")


def _to_content(
    contents: Union[
        str,
        gapic_content_types.Part,
        Sequence[Union[str, gapic_content_types.Part]],
        gapic_content_types.Content,
    ],
) -> gapic_content_types.Content:
    if isinstance(contents, gapic_content_types.Content):
        return contents
    parts = []
    if isinstance(contents, str):
        parts.append(gapic_content_types.Part(text=contents))
    elif hasattr(contents, "text"):
        parts.append(contents)
    elif isinstance(contents, Sequence):
        for p in contents:
            if isinstance(p, str):
                parts.append(gapic_content_types.Part(text=p))
            else:
                parts.append(p)
    else:
        raise ValueError(f"Unsupported type for contents: {type(contents)}")
    return gapic_content_types.Content(parts=parts, role="user")


@dataclasses.dataclass(frozen=True)
class TokensInfo:
    token_ids: Sequence[int]
    tokens: Sequence[bytes]
    role: str = None


@dataclasses.dataclass(frozen=True)
class ComputeTokensResult:
    """Represents token string pieces and ids output in compute_tokens function.

    Attributes:
        tokens_info: Lists of tokens_info from the input.
            The input `contents: ContentsType` could have
            multiple string instances and each tokens_info
            item represents each string instance. Each token
            info consists tokens list, token_ids list and
            a role.
    """

    tokens_info: Sequence[TokensInfo]


@dataclasses.dataclass(frozen=True)
class CountTokensResult:
    """Represents an token numbers output in count_tokens function.

    Attributes:
        total_tokens: number of total tokens.
    """

    total_tokens: int


def _parse_hex_byte(token: str) -> int:
    """Parses a hex byte string of the form '<0xXX>' and returns the integer value.

    Raises ValueError if the input is malformed or the byte value is invalid.
    """

    if len(token) != 6:
        raise ValueError(f"Invalid byte length: {token}")
    if not token.startswith("<0x") or not token.endswith(">"):
        raise ValueError(f"Invalid byte format: {token}")

    try:
        val = int(token[3:5], 16)  # Parse the hex part directly
    except ValueError:
        raise ValueError(f"Invalid hex value: {token}")

    if val >= 256:
        raise ValueError(f"Byte value out of range: {token}")

    return val


def _token_str_to_bytes(
    token: str, type: sentencepiece_model_pb2.ModelProto.SentencePiece.Type
) -> bytes:
    if type == sentencepiece_model_pb2.ModelProto.SentencePiece.Type.BYTE:
        return _parse_hex_byte(token).to_bytes(length=1, byteorder="big")
    else:
        return token.replace("▁", " ").encode("utf-8")


class _SentencePieceAdaptor:
    r"""An internal tokenizer that can parse text input into tokens."""

    def __init__(self, tokenizer_name: str):
        r"""Initializes the tokenizer.

        Args:
            name: The name of the tokenizer.
        """
        self._model_proto = load_model_proto(tokenizer_name)
        self._tokenizer = get_sentencepiece(tokenizer_name)

    def count_tokens(self, contents: Iterable[str]) -> CountTokensResult:
        r"""Counts the number of tokens in the input."""
        tokens_list = self._tokenizer.encode(list(contents))

        return CountTokensResult(
            total_tokens=sum(len(tokens) for tokens in tokens_list)
        )

    def compute_tokens(
        self, *, contents: Iterable[str], roles: Iterable[str]
    ) -> ComputeTokensResult:
        """Computes the tokens ids and string pieces in the input."""
        content_list = list(contents)
        tokens_protos = self._tokenizer.EncodeAsImmutableProto(content_list)
        roles = list(roles)

        token_infos = []
        for tokens_proto, role in zip(tokens_protos, roles):
            token_infos.append(
                TokensInfo(
                    token_ids=[piece.id for piece in tokens_proto.pieces],
                    tokens=[
                        _token_str_to_bytes(
                            piece.piece, self._model_proto.pieces[piece.id].type
                        )
                        for piece in tokens_proto.pieces
                    ],
                    role=role,
                )
            )
        return ComputeTokensResult(tokens_info=token_infos)


def _content_types_to_role_iterator(contents: ContentsType) -> Iterable[str]:
    gapic_contents = _to_gapic_contents(contents)
    for content in gapic_contents:
        for part in content.parts:
            yield content.role


def _is_string_inputs(contents: ContentsType) -> bool:
    return (
        isinstance(contents, str)
        or isinstance(contents, Sequence)
        and all(isinstance(content, str) for content in contents)
    )


def _to_canonical_roles(contents: ContentsType) -> Iterable[str]:
    if isinstance(contents, str):
        yield "user"
    elif isinstance(contents, Sequence) and all(
        isinstance(content, str) for content in contents
    ):
        yield from ["user"] * len(contents)
    else:
        yield from _content_types_to_role_iterator(contents)


class _TextsAccumulator:
    """Accumulates texts from contents and tools.

    This class is used to accumulate countable texts from contents and tools.
    """

    def __init__(self):
        self._texts = []

    def get_texts(self) -> Iterable[str]:
        return self._texts

    def add_texts(self, texts: Union[Iterable[str], str]) -> None:
        if isinstance(texts, str):
            self._texts.append(texts)
        else:
            self._texts.extend(texts)

    def add_content(self, content: gapic_content_types.Content) -> None:
        counted_content = gapic_content_types.Content()
        for part in content.parts:
            counted_part = gapic_content_types.Part()
            if "file_data" in part or "inline_data" in part:
                raise ValueError("Tokenizers do not support non-text content types.")
            if "video_metadata" in part:
                counted_part.video_metadata = part.video_metadata
            if "function_call" in part:
                self.add_function_call(part.function_call)
                counted_part.function_call = part.function_call
            if "function_response" in part:
                self.add_function_response(part.function_response)
                counted_part.function_response = part.function_response
            if "text" in part:
                counted_part.text = part.text
                self._texts.append(part.text)
            counted_content.parts.append(counted_part)
        counted_content.role = content.role
        if content._pb != counted_content._pb:
            raise ValueError(
                f"Content contains unsupported types for token counting. Supported fields {counted_content}. Got {content}."
            )

    def add_function_call(self, function_call: gapic_tool_types.FunctionCall) -> None:
        """Processes a function call and adds relevant text to the accumulator.

        Args:
            function_call: The function call to process.
        """
        self._texts.append(function_call.name)
        counted_function_call = gapic_tool_types.FunctionCall(name=function_call.name)
        counted_struct = self._struct_traverse(function_call._pb.args)
        counted_function_call.args = counted_struct
        if counted_function_call._pb != function_call._pb:
            raise ValueError(
                f"Function call argument contains unsupported types for token counting. Supported fields {counted_function_call}. Got {function_call}."
            )

    def add_function_calls(
        self, function_calls: Iterable[gapic_tool_types.FunctionCall]
    ) -> None:
        for function_call in function_calls:
            self.add_function_call(function_call)

    def add_tool(self, tool: gapic_tool_types.Tool) -> gapic_tool_types.Tool:
        counted_tool = gapic_tool_types.Tool()
        for function_declaration in tool.function_declarations:
            counted_function_declaration = self._function_declaration_traverse(
                function_declaration
            )
            counted_tool.function_declarations.append(counted_function_declaration)
        if counted_tool._pb != tool._pb:
            raise ValueError(
                f"Tool argument contains unsupported types for token counting. Supported fields {counted_tool}. Got {tool}."
            )

    def add_tools(self, tools: Iterable[gapic_tool_types.Tool]) -> None:
        for tool in tools:
            self.add_tool(tool)

    def add_function_responses(
        self, function_responses: Iterable[gapic_tool_types.FunctionResponse]
    ) -> None:
        for function_response in function_responses:
            self.add_function_response(function_response)

    def add_function_response(
        self, function_response: gapic_tool_types.FunctionResponse
    ) -> None:
        counted_function_response = gapic_tool_types.FunctionResponse()
        self._texts.append(function_response.name)
        counted_struct = self._struct_traverse(function_response._pb.response)
        counted_function_response.name = function_response.name
        counted_function_response.response = counted_struct
        if counted_function_response._pb != function_response._pb:
            raise ValueError(
                f"Function response argument contains unsupported types for token counting. Supported fields {counted_function_response}. Got {function_response}."
            )

    def _function_declaration_traverse(
        self, function_declaration: gapic_tool_types.FunctionDeclaration
    ) -> gapic_tool_types.FunctionDeclaration:
        counted_function_declaration = gapic_tool_types.FunctionDeclaration()
        self._texts.append(function_declaration.name)
        counted_function_declaration.name = function_declaration.name
        if function_declaration.description:
            self._texts.append(function_declaration.description)
            counted_function_declaration.description = function_declaration.description
        if function_declaration.parameters:
            counted_parameters = self._schema_traverse(function_declaration.parameters)
            counted_function_declaration.parameters = counted_parameters
        if function_declaration.response:
            counted_response = self._schema_traverse(function_declaration.response)
            counted_function_declaration.response = counted_response
        return counted_function_declaration

    def _schema_traverse(self, schema: openapi.Schema) -> openapi.Schema:
        """Processes a schema and adds relevant text to the accumulator.

        Args:
            schema: The schema to process.

        Returns:
            The new schema object with only countable fields.
        """
        counted_schema = openapi.Schema()
        if "type_" in schema:
            counted_schema.type = schema.type
        if "title" in schema:
            counted_schema.title = schema.title
        if "default" in schema:
            counted_schema.default = schema.default
        if "format_" in schema:
            self._texts.append(schema.format_)
            counted_schema.format_ = schema.format_
        if "description" in schema:
            self._texts.append(schema.description)
            counted_schema.description = schema.description
        if "enum" in schema:
            self._texts.extend(schema.enum)
            counted_schema.enum = schema.enum
        if "required" in schema:
            self._texts.extend(schema.required)
            counted_schema.required = schema.required
        if "property_ordering" in schema:
            counted_schema.property_ordering = schema.property_ordering
        if "items" in schema:
            counted_schema_items = self._schema_traverse(schema.items)
            counted_schema.items = counted_schema_items
        if "properties" in schema:
            d = {}
            for key, value in schema.properties.items():
                self._texts.append(key)
                counted_value = self._schema_traverse(value)
                d[key] = counted_value
            counted_schema.properties.update(d)
        if "example" in schema:
            counted_schema_example = self._value_traverse(schema._pb.example)
            counted_schema.example = counted_schema_example
        return counted_schema

    def _struct_traverse(self, struct: struct_pb2.Struct) -> struct_pb2.Struct:
        """Processes a struct and adds relevant text to the accumulator.

        Args:
            struct: The struct to process.

        Returns:
            The new struct object with only countable fields.
        """
        counted_struct = struct_pb2.Struct()
        self._texts.extend(list(struct.fields.keys()))
        for key, val in struct.fields.items():
            counted_struct_fields = self._value_traverse(val)
            if isinstance(counted_struct_fields, str):
                counted_struct.fields[key] = counted_struct_fields
            else:
                counted_struct.fields[key].MergeFrom(counted_struct_fields)
        return counted_struct

    def _value_traverse(self, value: struct_pb2.Value) -> struct_pb2.Value:
        """Processes a struct field and adds relevant text to the accumulator.

        Args:
            struct: The struct field to process.

        Returns:
            The new struct field object with only countable fields.
        """
        kind = value.WhichOneof("kind")
        counted_value = struct_pb2.Value()
        if kind == "string_value":
            self._texts.append(value.string_value)
            counted_value.string_value = value.string_value
        elif kind == "struct_value":
            counted_struct = self._struct_traverse(value.struct_value)
            counted_value.struct_value.MergeFrom(counted_struct)
        elif kind == "list_value":
            counted_list_value = struct_pb2.ListValue()
            for item in value.list_value.values:
                counted_value = self._value_traverse(item)
                counted_list_value.values.append(counted_value)
            counted_value.list_value.MergeFrom(counted_list_value)
        return counted_value


class Tokenizer:
    """A tokenizer that can parse text into tokens."""

    def __init__(self, tokenizer_name: str):
        """Initializes the tokenizer.

        Do not use this constructor directly. Use get_tokenizer_for_model instead.

        Args:
            name: The name of the tokenizer.

        """
        self._sentencepiece_adapter = _SentencePieceAdaptor(tokenizer_name)

    def count_tokens(
        self,
        contents: ContentsType,
        *,
        tools: Optional[List[gapic_tool_types.Tool]] = None,
        system_instruction: Optional[
            Union[
                str,
                gapic_content_types.Part,
                Sequence[Union[str, gapic_content_types.Part]],
                gapic_content_types.Content,
            ]
        ] = None,
    ) -> CountTokensResult:
        r"""Counts the number of tokens in the text-only contents.

        Args:
            contents: The contents to count tokens for.
                Supports either a list of Content objects (passing a multi-turn
                conversation) or a value that can be converted to a single
                Content object (passing a single message).
            tools: A list of tools (functions) that the model can try calling.
            system_instruction: The provided system instructions for the model.

        Returns:
            A CountTokensResult object containing the total number of tokens in
            the contents.
        """

        text_accumulator = _TextsAccumulator()
        if _is_string_inputs(contents):
            text_accumulator.add_texts(contents)
        else:
            gapic_contents = _to_gapic_contents(contents)
            for content in gapic_contents:
                text_accumulator.add_content(content)

        if tools:
            text_accumulator.add_tools(
                (getattr(tool, "_raw_tool", tool) for tool in tools)
            )

        if system_instruction:
            if _is_string_inputs(system_instruction):
                text_accumulator.add_texts(system_instruction)
            else:
                text_accumulator.add_content(_to_content(system_instruction))

        return self._sentencepiece_adapter.count_tokens(text_accumulator.get_texts())

    def compute_tokens(self, contents: ContentsType) -> ComputeTokensResult:
        r"""Computes the tokens ids and string pieces in the text-only contents.

        Args:
            contents: The contents to count tokens for.

        Returns:
            A ComputeTokensResult object containing the tokens ids and string
            pieces in the contents.
        """
        text_accumulator = _TextsAccumulator()
        if _is_string_inputs(contents):
            text_accumulator.add_texts(contents)
        else:
            gapic_contents = _to_gapic_contents(contents)
            for content in gapic_contents:
                text_accumulator.add_content(content)

        return self._sentencepiece_adapter.compute_tokens(
            contents=text_accumulator.get_texts(),
            roles=_to_canonical_roles(contents),
        )


def get_tokenizer_for_model(model_name: str) -> Tokenizer:
    """Returns a tokenizer for the given tokenizer name.

    Usage:
        ```
        tokenizer = get_tokenizer_for_model("gemini-1.5-pro-001")
        print(tokenizer.count_tokens("Hello world!"))
        ```

    Supported models can be found at
    https://cloud.google.com/vertex-ai/generative-ai/docs/learn/models.

    Args:
        model_name: Specify the tokenizer is from which model.
    """
    if not model_name:
        raise ValueError("model_name must not be empty.")

    return Tokenizer(get_tokenizer_name(model_name))
