# Copyright 2025 Google LLC
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
"""Classes for working with agent platform."""

from agentplatform.frameworks import a2a
from agentplatform.frameworks import adk
from agentplatform.frameworks import ag2
from agentplatform.frameworks import langchain
from agentplatform.frameworks import langgraph
from agentplatform.frameworks import llama_index


A2aAgent = a2a.A2aAgent
AdkApp = adk.AdkApp
AG2Agent = ag2.AG2Agent
LangchainAgent = langchain.LangchainAgent
LanggraphAgent = langgraph.LanggraphAgent
LlamaIndexQueryPipelineAgent = llama_index.LlamaIndexQueryPipelineAgent

__all__ = (
    "A2aAgent",
    "AdkApp",
    "AG2Agent",
    "LangchainAgent",
    "LanggraphAgent",
    "LlamaIndexQueryPipelineAgent",
)
