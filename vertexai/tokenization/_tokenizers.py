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

import dataclasses
from typing import (
    Iterable,
    List,
    Sequence,
)

from vertexai.generative_models._generative_models import (
    ContentsType,
    Image,
    _validate_contents_type_as_valid_sequence,
    _content_types_to_gapic_contents,
)

from vertexai.tokenization._tokenizer_loading import (
    get_sentencepiece,
    get_tokenizer_name,
    load_model_proto,
)
from google.cloud.aiplatform_v1beta1.types import (
    content as gapic_content_types,
    tool as gapic_tool_types,
)
from sentencepiece import sentencepiece_model_pb2


@dataclasses.dataclass(frozen=True)
class TokensInfo:
    token_ids: Sequence[int]
    tokens: Sequence[bytes]
    role: str = None


@dataclasses.dataclass(frozen=True)
class ComputeTokensResult:
    token_info_list: Sequence[TokensInfo]


@dataclasses.dataclass(frozen=True)
class CountTokensResult:
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
        return ComputeTokensResult(token_info_list=token_infos)


def _to_gapic_contents(
    contents: ContentsType,
) -> gapic_content_types.Content:
    """Converts a GenerativeModel compatible contents type to a gapic content."""
    _validate_contents_type_as_valid_sequence(contents)
    _assert_no_image_contents_type(contents)
    gapic_contents = _content_types_to_gapic_contents(contents)
    _assert_text_only_content_types_sequence(gapic_contents)
    return gapic_contents


def _content_types_to_string_iterator(contents: ContentsType) -> Iterable[str]:
    """Converts a GenerativeModel compatible contents type to a list of strings."""
    gapic_contents = _to_gapic_contents(contents)
    for content in gapic_contents:
        yield from _to_string_array(content)


def _content_types_to_role_iterator(contents: ContentsType) -> Iterable[str]:
    gapic_contents = _to_gapic_contents(contents)
    # Flattening role by content's multi parts
    for content in gapic_contents:
        for part in content.parts:
            yield content.role


def _to_string_array(content: gapic_content_types.Content) -> Iterable[str]:
    """Converts a gapic content type to a list of strings."""
    if not content:
        raise TypeError("content must not be empty.")
    return [part.text for part in content.parts]


def _assert_no_image_contents_type(contents: ContentsType):
    """Asserts that the contents type does not contain any image content."""
    if isinstance(contents, Image) or (
        isinstance(contents, Sequence)
        and any(isinstance(content, Image) for content in contents)
    ):
        raise ValueError("Tokenizers do not support Image content type.")


def _assert_text_only_content_types_sequence(
    contents: List[gapic_content_types.Content],
):
    """Asserts that the contents type does not contain any non-text content."""
    for value in contents:
        for part in value.parts:
            _assert_text_only_gapic_part(part)


def _assert_text_only_gapic_part(value: gapic_content_types.Part):
    """Asserts that the gapic content part is a text content type."""
    if (
        gapic_content_types.FileData() != value.file_data
        or gapic_content_types.Blob() != value.inline_data
        or gapic_tool_types.FunctionCall() != value.function_call
        or gapic_tool_types.FunctionResponse() != value.function_response
        or gapic_content_types.VideoMetadata() != value.video_metadata
    ):
        raise ValueError("Tokenizers do not support non-text content types.")


def _to_canonical_contents_texts(contents: ContentsType) -> Iterable[str]:
    """Gets the canonical contents."""
    if isinstance(contents, str):
        yield contents
    elif isinstance(contents, Sequence) and all(
        isinstance(content, str) for content in contents
    ):
        yield from contents
    else:
        yield from _content_types_to_string_iterator(contents)


def _to_canonical_roles(contents: ContentsType) -> Iterable[str]:
    if isinstance(contents, str):
        yield "user"
    elif isinstance(contents, Sequence) and all(
        isinstance(content, str) for content in contents
    ):
        yield from ["user"] * len(contents)
    else:
        yield from _content_types_to_role_iterator(contents)


class Tokenizer:
    """A tokenizer that can parse text into tokens."""

    def __init__(self, tokenizer_name: str):
        """Initializes the tokenizer.

        Do not use this constructor directly. Use get_tokenizer_for_model instead.

        Args:
            name: The name of the tokenizer.
        """
        self._sentencepiece_adapter = _SentencePieceAdaptor(tokenizer_name)

    def count_tokens(self, contents: ContentsType) -> CountTokensResult:
        r"""Counts the number of tokens in the text-only contents.

        Args:
            contents: The contents to count tokens for.
                Supports either a list of Content objects (passing a multi-turn
                conversation) or a value that can be converted to a single
                Content object (passing a single message).
                Supports
                * str, Part,
                * List[Union[str, Part]],
                * List[Content]
                Throws an error if the contents contain non-text content.


        Returns:
            A CountTokensResult object containing the total number of tokens in
            the contents.
        """

        return self._sentencepiece_adapter.count_tokens(
            _to_canonical_contents_texts(contents)
        )

    def compute_tokens(self, contents: ContentsType) -> ComputeTokensResult:
        r"""Computes the tokens ids and string pieces in the text-only contents.

        Args:
            contents: The contents to count tokens for.
                Supports either a list of Content objects (passing a multi-turn
                conversation) or a value that can be converted to a single
                Content object (passing a single message).
                Supports
                * str, Part,
                * List[Union[str, Part]],
                * List[Content]
                Throws an error if the contents contain non-text content.

        Returns:
            A ComputeTokensResult object containing the tokens ids and string
            pieces in the contents.
        """
        return self._sentencepiece_adapter.compute_tokens(
            contents=_to_canonical_contents_texts(contents),
            roles=_to_canonical_roles(contents),
        )


def get_tokenizer_for_model(model_name: str) -> Tokenizer:
    """Returns a tokenizer for the given tokenizer name.

    Usage:
        ```
        tokenizer = get_tokenizer_for_model("gemini-1.5-pro-001")
        print(tokenizer.count_tokens("Hello world!"))
        ```

    Args:
        model_name: Specify the tokenizer is from which model.
    """
    if not model_name:
        raise ValueError("model_name must not be empty.")

    return Tokenizer(get_tokenizer_name(model_name))
