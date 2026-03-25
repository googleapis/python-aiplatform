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

# Handwritten placeholder code for the runtimes.py file.
# Should be replaced by the generated file.

import importlib
import logging
import typing

from google.genai import _api_module


if typing.TYPE_CHECKING:
    from . import runtime_revisions as runtime_revisions_module

    _ = runtime_revisions_module


logger = logging.getLogger("vertexai_genai.runtimes")

logger.setLevel(logging.INFO)


class Runtimes(_api_module.BaseModule):

    _revisions = None

    @property
    def revisions(self) -> "runtime_revisions_module.RuntimeRevisions":
        if self._revisions is None:
            try:
                # We need to lazy load the revisions module to handle the
                # possibility of ImportError when dependencies are not installed.
                self._revisions = importlib.import_module(
                    ".runtime_revisions", __package__
                )
            except ImportError as e:
                raise ImportError(
                    "The 'agent_engines.runtimes.revisions' module requires "
                    "additional packages. Please install them using pip install "
                    "google-cloud-aiplatform[agent_engines]"
                ) from e
        return self._revisions.RuntimeRevisions(self._api_client)  # type: ignore[no-any-return]


class AsyncRuntimes(_api_module.BaseModule):

    _revisions = None

    @property
    def revisions(self) -> "runtime_revisions_module.AsyncRuntimeRevisions":
        if self._revisions is None:
            try:
                # We need to lazy load the revisions module to handle the
                # possibility of ImportError when dependencies are not installed.
                self._revisions = importlib.import_module(
                    ".runtime_revisions", __package__
                )
            except ImportError as e:
                raise ImportError(
                    "The 'agent_engines.runtimes.revisions' module requires "
                    "additional packages. Please install them using pip install "
                    "google-cloud-aiplatform[agent_engines]"
                ) from e
        return self._revisions.AsyncRuntimeRevisions(self._api_client)  # type: ignore[no-any-return]
