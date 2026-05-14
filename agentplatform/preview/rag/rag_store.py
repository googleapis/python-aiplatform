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
"""RAG retrieval tool for content generation."""

import re
from typing import List, Optional, Union
import warnings

from google.cloud import aiplatform_v1beta1
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1.types import tool as gapic_tool_types
from agentplatform.preview.rag.utils import _gapic_utils
from agentplatform.preview.rag.utils import resources


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
        rag_resources: Optional[List[resources.RagResource]] = None,
        rag_retrieval_config: Optional[resources.RagRetrievalConfig] = None,
    ):
        """Initializes a Vertex RAG store tool.

        Example usage:
        ```
        import agentplatform

        agentplatform.init(project="my-project")

        # Using RagRetrievalConfig.
        config = agentplatform.preview.rag.RagRetrievalConfig(
            top_k=2,
            filter=agentplatform.preview.rag.RagRetrievalConfig.Filter(
                vector_distance_threshold=0.5
            ),
        )

        tool = Tool.from_retrieval(
            retrieval=agentplatform.preview.rag.Retrieval(
                source=agentplatform.preview.rag.VertexRagStore(
                    rag_resources=[
                        agentplatform.preview.rag.RagResource(
                            rag_corpus="projects/my-project/locations/us-central1/ragCorpora/rag-corpus-1"
                        )
                    ],
                    rag_retrieval_config=config,
                ),
            )
        )
        ```

        Args:
            rag_resources: List of RagResource to retrieve from. It can be used
                to specify corpus only or ragfiles. Currently only support one
                corpus or multiple files from one corpus. In the future we
                may open up multiple corpora support.
            rag_retrieval_config: Optional. The config containing the retrieval
                parameters, including top_k and vector_distance_threshold.
        """

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
            parent = initializer.global_config.common_location_path()
            rag_corpus_name = parent + "/ragCorpora/" + name
        else:
            raise ValueError(
                f"Invalid RagCorpus name: {name}. Proper format should"
                + " be: projects/{{project}}/locations/{{location}}/ragCorpora/{{rag_corpus_id}}"
            )

        if not rag_retrieval_config:
            api_retrival_config = aiplatform_v1beta1.RagRetrievalConfig()
        else:
            api_retrival_config = aiplatform_v1beta1.RagRetrievalConfig()
            if rag_retrieval_config.top_k:
                api_retrival_config.top_k = rag_retrieval_config.top_k
            if (
                rag_retrieval_config.filter
                and rag_retrieval_config.filter.vector_distance_threshold
                and rag_retrieval_config.filter.vector_similarity_threshold
            ):
                raise ValueError(
                    "Only one of vector_distance_threshold or"
                    " vector_similarity_threshold can be specified at a time"
                    " in rag_retrieval_config."
                )
            if (
                rag_retrieval_config.filter
                and rag_retrieval_config.filter.vector_distance_threshold
            ):
                api_retrival_config.filter.vector_distance_threshold = (
                    rag_retrieval_config.filter.vector_distance_threshold
                )
            if (
                rag_retrieval_config.filter
                and rag_retrieval_config.filter.vector_similarity_threshold
            ):
                api_retrival_config.filter.vector_similarity_threshold = (
                    rag_retrieval_config.filter.vector_similarity_threshold
                )
            if (
                rag_retrieval_config.ranking
                and rag_retrieval_config.ranking.rank_service
                and rag_retrieval_config.ranking.rank_service.model_name
                and rag_retrieval_config.ranking.llm_ranker
                and rag_retrieval_config.ranking.llm_ranker.model_name
            ):
                raise ValueError(
                    "Only one of rank_service or llm_ranker can be specified"
                    " at a time in rag_retrieval_config."
                )
            if (
                rag_retrieval_config.ranking
                and rag_retrieval_config.ranking.rank_service
            ):
                api_retrival_config.ranking.rank_service.model_name = (
                    rag_retrieval_config.ranking.rank_service.model_name
                )
            if rag_retrieval_config.ranking and rag_retrieval_config.ranking.llm_ranker:
                api_retrival_config.ranking.llm_ranker.model_name = (
                    rag_retrieval_config.ranking.llm_ranker.model_name
                )

        gapic_rag_resource = gapic_tool_types.VertexRagStore.RagResource(
            rag_corpus=rag_corpus_name,
            rag_file_ids=rag_resources[0].rag_file_ids,
        )
        self._raw_vertex_rag_store = gapic_tool_types.VertexRagStore(
            rag_resources=[gapic_rag_resource],
            rag_retrieval_config=api_retrival_config,
        )
