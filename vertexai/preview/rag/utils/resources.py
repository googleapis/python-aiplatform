# -*- coding: utf-8 -*-

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
from typing import List, Optional


@dataclasses.dataclass
class RagFile:
    """RAG file (output only).

    Attributes:
        name: Generated resource name. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}/ragFiles/{rag_file}``
        display_name: Display name that was configured at client side.
        description: The description of the RagFile.
    """

    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None


@dataclasses.dataclass
class EmbeddingModelConfig:
    """EmbeddingModelConfig.

    The representation of the embedding model config. Users input a 1P embedding
    model as a Publisher model resource, or a 1P fine tuned embedding model
    as an Endpoint resource.

    Attributes:
        publisher_model: 1P publisher model resource name. Format:
            ``publishers/google/models/{model}`` or
            ``projects/{project}/locations/{location}/publishers/google/models/{model}``
        endpoint: 1P fine tuned embedding model resource name. Format:
            ``endpoints/{endpoint}`` or
            ``projects/{project}/locations/{location}/endpoints/{endpoint}``.
        model:
            Output only. The resource name of the model that is deployed
            on the endpoint. Present only when the endpoint is not a
            publisher model. Pattern:
            ``projects/{project}/locations/{location}/models/{model}``
        model_version_id:
            Output only. Version ID of the model that is
            deployed on the endpoint. Present only when the
            endpoint is not a publisher model.
    """

    publisher_model: Optional[str] = None
    endpoint: Optional[str] = None
    model: Optional[str] = None
    model_version_id: Optional[str] = None


@dataclasses.dataclass
class RagCorpus:
    """RAG corpus(output only).

    Attributes:
        name: Generated resource name. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}``
        display_name: Display name that was configured at client side.
        description: The description of the RagCorpus.
    """

    name: Optional[str] = None
    display_name: Optional[str] = None
    description: Optional[str] = None
    embedding_model_config: Optional[EmbeddingModelConfig] = None


@dataclasses.dataclass
class RagResource:
    """RagResource.

    The representation of the rag source. It can be used to specify corpus only
    or ragfiles. Currently only support one corpus or multiple files from one
    corpus. In the future we may open up multiple corpora support.

    Attributes:
        rag_corpus: A Rag corpus resource name or corpus id. Format:
            ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}``
            or ``{rag_corpus_id}``.
        rag_files_id: List of Rag file resource name or file ids in the same corpus. Format:
            ``{rag_file}``.
    """

    rag_corpus: Optional[str] = None
    rag_file_ids: Optional[List[str]] = None
