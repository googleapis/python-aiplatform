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
"""Tentative module in private_preview."""

from typing import List,Optional, Union
from google.cloud.aiplatform_v1beta1.types import tool as gapic_tool_types


class Retrieval:
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
        rag_corpora: List[str],
        similarity_top_k: Optional[int],
    ):
        """Initializes a Vertex RAG store tool.

        Args:
            rag_corpora: A list of Vertex Rag Corpora resource name. Format:
                projects/<>/locations/<>/ragCorpora/<>.
            similarity_top_k: Number of top k results to return from the selected
                corpora.
        """
        self._raw_vertex_rag_store = gapic_tool_types.VertexRagStore(
            rag_corpora=rag_corpora,
            similarity_top_k=similarity_top_k,
        )
