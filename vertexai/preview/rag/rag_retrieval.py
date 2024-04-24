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
from typing import List, Optional
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform_v1beta1 import (
    RagQuery,
    RetrieveContextsRequest,
    RetrieveContextsResponse,
)
from vertexai.preview.rag.utils import (
    _gapic_utils,
)


def retrieval_query(
    rag_corpora: List[str],
    text: str,
    similarity_top_k: Optional[int] = 10,
) -> RetrieveContextsResponse:
    """Retrieve top k relevant docs/chunks.

    Args:
        rag_corpora: A list of full resource name or corpus_id of the RagCorpus. Format:
        ``projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}``
        text: The query in text format to get relevant contexts.
        similarity_top_k: The number of contexts to retrieve.
    Returns:
        RetrieveContextsResonse.
    """
    parent = initializer.global_config.common_location_path()

    client = _gapic_utils.create_rag_service_client()
    vertex_rag_store = RetrieveContextsRequest.VertexRagStore()
    # Currently only support 1 RagCorpus.
    if len(rag_corpora) > 1:
        raise ValueError("Currently only support 1 RagCorpus.")
    if len(rag_corpora[0].split("/")) == 6:
        rag_corpus_name = rag_corpora[0]
    elif len(rag_corpora[0].split("/")) == 1:
        rag_corpus_name = parent + "/ragCorpora/" + rag_corpora[0]
    else:
        raise ValueError(
            "Invalid RagCorpus name: %s. Proper format should be: projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}",
            rag_corpora,
        )

    vertex_rag_store.rag_corpora = [rag_corpus_name]
    query = RagQuery(text=text, similarity_top_k=similarity_top_k)
    request = RetrieveContextsRequest(
        vertex_rag_store=vertex_rag_store,
        parent=parent,
        query=query,
    )
    try:
        response = client.retrieve_contexts(request=request)
    except Exception as e:
        raise RuntimeError("Failed in retrieving contexts due to: ", e) from e

    return response
