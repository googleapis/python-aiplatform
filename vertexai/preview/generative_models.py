# Copyright 2023 Google LLC
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
"""Classes for working with the Gemini models."""

import warnings

# We just want to re-export certain classes
# pylint: disable=g-multiple-import,g-importing-member
from vertexai.generative_models._generative_models import (
    preview_grounding as grounding,
    _PreviewGenerativeModel,
    _PreviewChatSession,
    GenerationConfig,
    GenerationResponse,
    AutomaticFunctionCallingResponder,
    CallableFunctionDeclaration,
    Candidate,
    Content,
    FinishReason,
    FunctionCall,
    FunctionDeclaration,
    HarmCategory,
    HarmBlockThreshold,
    Image,
    Part,
    ResponseBlockedError,
    ResponseValidationError,
    SafetySetting,
    Tool,
    ToolConfig,
)
from google.cloud.aiplatform_v1beta1.types import tool as gapic_tool_types


class GenerativeModel(_PreviewGenerativeModel):
    __doc__ = _PreviewGenerativeModel.__doc__


class ChatSession(_PreviewChatSession):
    __doc__ = _PreviewChatSession.__doc__


__all__ = [
    "grounding",
    "GenerationConfig",
    "GenerativeModel",
    "GenerationResponse",
    "AutomaticFunctionCallingResponder",
    "CallableFunctionDeclaration",
    "Candidate",
    "ChatSession",
    "Content",
    "FinishReason",
    "FunctionCall",
    "FunctionDeclaration",
    "HarmCategory",
    "HarmBlockThreshold",
    "Image",
    "Part",
    "ResponseBlockedError",
    "ResponseValidationError",
    "SafetySetting",
    "Tool",
    "ToolConfig",
]


def _preview_parse_vertex_rag_store_to_api(
    vertex_rag_store: "grounding.VertexRagStore",
) -> gapic_tool_types.VertexRagStore:
    """Converts a VertexRagStore object to a gapic_tool_types.VertexRagStore object."""
    gapic_vertex_rag_store = gapic_tool_types.VertexRagStore()

    if vertex_rag_store.rag_resources:
        gapic_rag_resources = []
        for resource in vertex_rag_store.rag_resources:
            gapic_rag_resources.append(
                gapic_tool_types.VertexRagStore.RagResource(
                    rag_corpus=resource.rag_corpus,
                    rag_file_ids=resource.rag_file_ids,
                )
            )
        gapic_vertex_rag_store.rag_resources = gapic_rag_resources
    elif vertex_rag_store.rag_corpora:
        gapic_vertex_rag_store.rag_corpora = vertex_rag_store.rag_corpora

    if vertex_rag_store.rag_retrieval_config:
        rag_retrieval_config = vertex_rag_store.rag_retrieval_config
        gapic_rag_retrieval_config = gapic_tool_types.RagRetrievalConfig()

        # Handle deprecated fields for warnings within rag_retrieval_config
        if rag_retrieval_config.top_k is not None:
            warnings.warn(
                "similarity_top_k is deprecated. Please use"
                " rag_retrieval_config.top_k instead.",
                DeprecationWarning,
            )
        if (
            rag_retrieval_config.filter
            and rag_retrieval_config.filter.vector_distance_threshold is not None
        ):
            warnings.warn(
                "vector_distance_threshold is deprecated. Please use"
                " rag_retrieval_config.filter.vector_distance_threshold instead.",
                DeprecationWarning,
            )
        if (
            rag_retrieval_config.hybrid_search
            and rag_retrieval_config.hybrid_search.alpha is not None
        ):
            warnings.warn(
                "vector_search_alpha is deprecated. Please use"
                " rag_retrieval_config.hybrid_search.alpha instead.",
                DeprecationWarning,
            )

        if rag_retrieval_config.top_k:
            gapic_rag_retrieval_config.top_k = rag_retrieval_config.top_k
        if rag_retrieval_config.filter:
            gapic_filter = gapic_tool_types.RagRetrievalConfig.Filter()
            if (
                rag_retrieval_config.filter.vector_distance_threshold is not None
                and rag_retrieval_config.filter.vector_similarity_threshold is not None
            ):
                raise ValueError(
                    "Only one of vector_distance_threshold or"
                    " vector_similarity_threshold can be specified at a time"
                    " in rag_retrieval_config."
                )
            if rag_retrieval_config.filter.vector_distance_threshold is not None:
                gapic_filter.vector_distance_threshold = (
                    rag_retrieval_config.filter.vector_distance_threshold
                )
            if rag_retrieval_config.filter.vector_similarity_threshold is not None:
                gapic_filter.vector_similarity_threshold = (
                    rag_retrieval_config.filter.vector_similarity_threshold
                )
            if rag_retrieval_config.filter.metadata_filter is not None:
                gapic_filter.metadata_filter = (
                    rag_retrieval_config.filter.metadata_filter
                )
            gapic_rag_retrieval_config.filter = gapic_filter
        if rag_retrieval_config.hybrid_search:
            if rag_retrieval_config.hybrid_search.alpha is not None:
                gapic_rag_retrieval_config.hybrid_search.alpha = (
                    rag_retrieval_config.hybrid_search.alpha
                )
        if rag_retrieval_config.ranking:
            if (
                rag_retrieval_config.ranking.rank_service
                and rag_retrieval_config.ranking.llm_ranker
            ):
                raise ValueError("Only one of rank_service and llm_ranker can be set.")
            if rag_retrieval_config.ranking.rank_service:
                gapic_rag_retrieval_config.ranking.rank_service.model_name = (
                    rag_retrieval_config.ranking.rank_service.model_name
                )
            if rag_retrieval_config.ranking.llm_ranker:
                gapic_rag_retrieval_config.ranking.llm_ranker.model_name = (
                    rag_retrieval_config.ranking.llm_ranker.model_name
                )
        gapic_vertex_rag_store.rag_retrieval_config = gapic_rag_retrieval_config

    return gapic_vertex_rag_store
