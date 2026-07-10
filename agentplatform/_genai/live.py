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

import importlib
import logging

from typing import Optional, TYPE_CHECKING
from types import ModuleType

from google.genai import _api_module
from google.genai import _common
from google.genai._api_client import BaseApiClient

logger = logging.getLogger("google_genai.live")

if TYPE_CHECKING:
    from agentplatform._genai import (
        live_runtimes as live_runtimes_module,
    )


class AsyncLive(_api_module.BaseModule):
    """[Preview] AsyncLive."""

    def __init__(self, api_client: BaseApiClient):
        super().__init__(api_client)
        self._runtimes: Optional[ModuleType] = None

    @property
    @_common.experimental_warning(
        "The Vertex SDK GenAI runtimes module is experimental, "
        "and may change in future versions."
    )
    def runtimes(self) -> "live_runtimes_module.AsyncLiveRuntimes":
        if self._runtimes is None:
            try:
                # We need to lazy load the live_runtimes module to handle
                # the possibility of ImportError when dependencies are not
                # installed.
                self._runtimes = importlib.import_module(
                    ".live_runtimes",
                    __package__,
                )
            except ImportError as e:
                raise ImportError(
                    "The 'runtimes' module requires 'additional packages'. "
                    "Please install them using pip install "
                    "google-cloud-aiplatform[agent_engines]"
                ) from e
        return self._runtimes.AsyncLiveRuntimes(self._api_client)  # type: ignore[no-any-return]
