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

from unittest import mock
import pytest
from agentplatform import tokenization
from agentplatform.tokenization import _tokenizers


@pytest.fixture(autouse=True)
def mock_sentencepiece_adaptor():
    with mock.patch.object(_tokenizers, "_SentencePieceAdaptor", autospec=True) as m:
        inst = m.return_value
        inst.count_tokens.return_value = tokenization.CountTokensResult(total_tokens=5)
        inst.compute_tokens.return_value = tokenization.ComputeTokensResult(
            tokens_info=[
                tokenization.TokensInfo(
                    token_ids=[1, 2], tokens=[b"hello", b"world"], role="user"
                )
            ]
        )
        yield m


@pytest.mark.parametrize(
    "model_name",
    [
        "gemini-1.0-pro",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
    ],
)
def test_tokenization_basic(model_name):
    tokenizer = tokenization.get_tokenizer_for_model(model_name)
    assert tokenizer is not None

    res = tokenizer.count_tokens("Hello world, how are you?")
    assert res.total_tokens == 5

    comp = tokenizer.compute_tokens("Hello world, how are you?")
    assert len(comp.tokens_info) == 1


def test_tokenization_invalid_model():
    with pytest.raises(ValueError):
        tokenization.get_tokenizer_for_model("non-existent-model")
