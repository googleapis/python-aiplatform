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

"""[Preview] Live API client."""

import logging


from google.genai import _api_module
from google.genai import _common
from google.genai._api_client import BaseApiClient
from . import live_agent_engines

logger = logging.getLogger('google_genai.live')


class AsyncLive(_api_module.BaseModule):
  """[Preview] AsyncLive."""

  def __init__(self, api_client: BaseApiClient):
    super().__init__(api_client)
    self._agent_engines = live_agent_engines.AsyncLiveAgentEngines(api_client)

  @property
  @_common.experimental_warning(
        "The Vertex SDK GenAI agent engines module is experimental, "
        "and may change in future versions."
  )
  def agent_engines(self) -> live_agent_engines.AsyncLiveAgentEngines:
    return self._agent_engines
