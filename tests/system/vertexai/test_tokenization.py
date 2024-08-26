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
        "model_name, corpus_name, corpus_lib",
        _MODEL_CORPUS_PARAMS,
    )
    def test_count_tokens_local(
        self, model_name, corpus_name, corpus_lib, api_endpoint_env_name
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
        "model_name, corpus_name, corpus_lib",
        _MODEL_CORPUS_PARAMS,
    )
    def test_compute_tokens(
        self, model_name, corpus_name, corpus_lib, api_endpoint_env_name
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
            for local, service in zip(
                local_result.token_info_list, response.tokens_info
            ):
                assert local.tokens == service.tokens
                assert local.token_ids == service.token_ids
