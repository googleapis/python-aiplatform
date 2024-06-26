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

import pytest
import nltk
from nltk.corpus import udhr
from google.cloud import aiplatform
from vertexai.preview.tokenization import (
    get_tokenizer_for_model,
)
from vertexai.generative_models import GenerativeModel
from tests.system.aiplatform import e2e_base
from google import auth


_MODELS = ["gemini-1.0-pro", "gemini-1.5-pro", "gemini-1.5-flash"]
_CORPUS = [
    "udhr",
]
_CORPUS_LIB = [
    udhr,
]
_MODEL_CORPUS_PARAMS = [
    (model_name, corpus_name, corpus_lib)
    for model_name in _MODELS
    for (corpus_name, corpus_lib) in zip(_CORPUS, _CORPUS_LIB)
]


class TestTokenization(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_tokenization_test_"

    def setup_method(self):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
        )

    @pytest.mark.parametrize(
        "model_name, corpus_name, corpus_lib",
        _MODEL_CORPUS_PARAMS,
    )
    def test_count_tokens_local(self, model_name, corpus_name, corpus_lib):
        tokenizer = get_tokenizer_for_model(model_name)
        model = GenerativeModel(model_name)
        nltk.download(corpus_name, quiet=True)
        for id, book in enumerate(corpus_lib.fileids()):
            text = corpus_lib.raw(book)
            service_result = model.count_tokens(text)
            local_result = tokenizer.count_tokens(text)
            assert service_result.total_tokens == local_result.total_tokens
