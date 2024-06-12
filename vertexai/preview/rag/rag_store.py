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
"""RAG retrieval tool for content generation."""

import re
from typing import List, Optional, Union
from google.cloud.aiplatform_v1beta1.types import tool as gapic_tool_types
from google.cloud.aiplatform import initializer
from vertexai.preview.rag.utils import _gapic_utils
from vertexai.preview.rag.utils.resources import RagResource
from vertexai.preview import generative_models


class Retrieval(generative_models.grounding.Retrieval):
    """Defines a retrieval tool that a model can call to access external knowledge."""

    def __init__(
        self,
        source: Union["VertexRagStore"],
        disable_attribution: Optional[bool] = False,
    ):
        self._raw_retrieval = gapic_tool_types.Retrieval(
            vertex_rag_store=source._raw_vertex_rag_store,
            disable_attribution=disable_attribution,
        )


class VertexRagStore:
    """Retrieve from Vertex RAG Store."""

    def __init__(
        self,
        rag_resources: Optional[List[RagResource]] = None,
        rag_corpora: Optional[List[str]] = None,
        similarity_top_k: Optional[int] = 10,
        vector_distance_threshold: Optional[float] = 0.3,
    ):
        """Initializes a Vertex RAG store tool.

        Example usage:
        ```
        import vertexai

        vertexai.init(project="my-project")

        results = vertexai.preview.rag.retrieval_query(
            text="Why is the sky blue?",
            rag_resources=[vertexai.preview.rag.RagResource(
                rag_corpus="projects/my-project/locations/us-central1/ragCorpora/rag-corpus-1",
                rag_file_ids=["rag-file-1", "rag-file-2", ...],
            )],
            similarity_top_k=2,
            vector_distance_threshold=0.5,
        )
        ```

        Args:
            rag_resources: List of RagResource to retrieve from. It can be used
                to specify corpus only or ragfiles. Currently only support one
                corpus or multiple files from one corpus. In the future we
                may open up multiple corpora support.
            rag_corpora: If rag_resources is not specified, use rag_corpora as a
                list of rag corpora names.
            similarity_top_k: Number of top k results to return from the selected
                corpora.
            vector_distance_threshold (float):
                Optional. Only return results with vector distance smaller than the threshold.

        """

        if rag_resources:
            if len(rag_resources) > 1:
                raise ValueError("Currently only support 1 RagResource.")
            name = rag_resources[0].rag_corpus
        elif rag_corpora:
            if len(rag_corpora) > 1:
                raise ValueError("Currently only support 1 RagCorpus.")
            name = rag_corpora[0]
        else:
            raise ValueError("rag_resources or rag_corpora must be specified.")

        data_client = _gapic_utils.create_rag_data_service_client()
        if data_client.parse_rag_corpus_path(name):
            rag_corpus_name = name
        elif re.match("^{}$".format(_gapic_utils._VALID_RESOURCE_NAME_REGEX), name):
            parent = initializer.global_config.common_location_path()
            rag_corpus_name = parent + "/ragCorpora/" + name
        else:
            raise ValueError(
                "Invalid RagCorpus name: %s. Proper format should be: projects/{project}/locations/{location}/ragCorpora/{rag_corpus_id}",
                rag_corpora,
            )
        if rag_resources:
            gapic_rag_resource = gapic_tool_types.VertexRagStore.RagResource(
                rag_corpus=rag_corpus_name,
                rag_file_ids=rag_resources[0].rag_file_ids,
            )
            self._raw_vertex_rag_store = gapic_tool_types.VertexRagStore(
                rag_resources=[gapic_rag_resource],
                similarity_top_k=similarity_top_k,
                vector_distance_threshold=vector_distance_threshold,
            )
        else:
            self._raw_vertex_rag_store = gapic_tool_types.VertexRagStore(
                rag_corpora=[rag_corpus_name],
                similarity_top_k=similarity_top_k,
                vector_distance_threshold=vector_distance_threshold,
            )
