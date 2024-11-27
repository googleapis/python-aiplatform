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
"""Retrieval query to get relevant contexts."""

import re
from typing import List, Optional

from google.cloud import aiplatform_v1
from google.cloud.aiplatform import initializer
from vertexai.rag.utils import _gapic_utils
from vertexai.rag.utils import resources


def retrieval_query(
    text: str,
    rag_resources: Optional[List[resources.RagResource]] = None,
    rag_retrieval_config: Optional[resources.RagRetrievalConfig] = None,
) -> aiplatform_v1.RetrieveContextsResponse:
    """Retrieve top k relevant docs/chunks.

    Example usage:
    ```
    import vertexai

    vertexai.init(project="my-project")

    config = vertexai.rag.rag_retrieval_config(
        top_k=2,
        filter=vertexai.rag.rag_retrieval_config.filter(
            vector_distance_threshold=0.5
        ),
    )

    results = vertexai.rag.retrieval_query(
        text="Why is the sky blue?",
        rag_resources=[vertexai.rag.RagResource(
            rag_corpus="projects/my-project/locations/us-central1/ragCorpora/rag-corpus-1",
            rag_file_ids=["rag-file-1", "rag-file-2", ...],
        )],
        rag_retrieval_config=config,
    )
    ```

    Args:
        text: The query in text format to get relevant contexts.
        rag_resources: A list of RagResource. It can be used to specify corpus
            only or ragfiles. Currently only support one corpus or multiple files
            from one corpus. In the future we may open up multiple corpora support.
        rag_retrieval_config: Optional. The config containing the retrieval
            parameters, including similarity_top_k and vector_distance_threshold

    Returns:
        RetrieveContextsResonse.
    """
    parent = initializer.global_config.common_location_path()

    client = _gapic_utils.create_rag_service_client()

    if rag_resources:
        if len(rag_resources) > 1:
            raise ValueError("Currently only support 1 RagResource.")
        name = rag_resources[0].rag_corpus
    else:
        raise ValueError("rag_resources must be specified.")

    data_client = _gapic_utils.create_rag_data_service_client()
    if data_client.parse_rag_corpus_path(name):
        rag_corpus_name = name
    elif re.match("^{}$".format(_gapic_utils._VALID_RESOURCE_NAME_REGEX), name):
        rag_corpus_name = parent + "/ragCorpora/" + name
    else:
        raise ValueError(
            f"Invalid RagCorpus name: {name}. Proper format should be:"
            " projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}"
        )

    if rag_resources:
        gapic_rag_resource = (
            aiplatform_v1.RetrieveContextsRequest.VertexRagStore.RagResource(
                rag_corpus=rag_corpus_name,
                rag_file_ids=rag_resources[0].rag_file_ids,
            )
        )
        vertex_rag_store = aiplatform_v1.RetrieveContextsRequest.VertexRagStore(
            rag_resources=[gapic_rag_resource],
        )
    else:
        vertex_rag_store = aiplatform_v1.RetrieveContextsRequest.VertexRagStore(
            rag_corpora=[rag_corpus_name],
        )

    # If rag_retrieval_config is not specified, set it to default values.
    if not rag_retrieval_config:
        api_retrival_config = aiplatform_v1.RagRetrievalConfig()
    else:
        # If rag_retrieval_config is specified, check for missing parameters.
        api_retrival_config = aiplatform_v1.RagRetrievalConfig(
            top_k=rag_retrieval_config.top_k,
        )
        if rag_retrieval_config.filter:
            api_retrival_config.filter = aiplatform_v1.RagRetrievalConfig.Filter(
                vector_distance_threshold=rag_retrieval_config.filter.vector_distance_threshold
            )
        else:
            api_retrival_config.filter = aiplatform_v1.RagRetrievalConfig.Filter(
                vector_distance_threshold=None
            )

    query = aiplatform_v1.RagQuery(
        text=text,
        rag_retrieval_config=api_retrival_config,
    )
    request = aiplatform_v1.RetrieveContextsRequest(
        vertex_rag_store=vertex_rag_store,
        parent=parent,
        query=query,
    )
    try:
        response = client.retrieve_contexts(request=request)
    except Exception as e:
        raise RuntimeError("Failed in retrieving contexts due to: ", e) from e

    return response
