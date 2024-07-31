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

from vertexai.preview.rag.rag_data import (
    create_corpus,
    list_corpora,
    get_corpus,
    delete_corpus,
    upload_file,
    import_files,
    import_files_async,
    get_file,
    list_files,
    delete_file,
)

from vertexai.preview.rag.rag_retrieval import (
    retrieval_query,
)

from vertexai.preview.rag.rag_store import (
    Retrieval,
    VertexRagStore,
)
from vertexai.preview.rag.utils.resources import (
    EmbeddingModelConfig,
    JiraSource,
    JiraQuery,
    RagCorpus,
    RagFile,
    RagResource,
    SlackChannel,
    SlackChannelsSource,
)


__all__ = (
    "create_corpus",
    "list_corpora",
    "get_corpus",
    "delete_corpus",
    "upload_file",
    "import_files",
    "import_files_async",
    "get_file",
    "list_files",
    "delete_file",
    "retrieval_query",
    "EmbeddingModelConfig",
    "Retrieval",
    "VertexRagStore",
    "RagResource",
    "RagFile",
    "RagCorpus",
    "JiraSource",
    "JiraQuery",
    "SlackChannel",
    "SlackChannelsSource",
)
