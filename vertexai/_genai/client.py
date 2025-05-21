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

from typing import Optional, Union

import google.auth
from google.genai import client
from google.genai import types
from .evals import Evals
from .evals import AsyncEvals


class AsyncClient:
    """Async Client for the GenAI SDK."""

    def __init__(self, api_client: client.Client):
        self._api_client = api_client
        self._aio = AsyncClient(self._api_client)
        self._evals = AsyncEvals(self._api_client)

    @property
    def evals(self) -> AsyncEvals:
        return self._evals


class Client:
    """Client for the GenAI SDK.

    Use this client to interact with Vertex-specific Gemini features.
    """

    def __init__(
        self,
        *,
        credentials: Optional[google.auth.credentials.Credentials] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        debug_config: Optional[client.DebugConfig] = None,
        http_options: Optional[Union[types.HttpOptions, types.HttpOptionsDict]] = None,
    ):
        """Initializes the client.

        Args:
           credentials (google.auth.credentials.Credentials): The credentials to use
             for authentication when calling the Vertex AI APIs. Credentials can be
             obtained from environment variables and default credentials. For more
             information, see `Set up Application Default Credentials
             <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
           project (str): The `Google Cloud project ID
             <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to
             use for quota. Can be obtained from environment variables (for example,
             ``GOOGLE_CLOUD_PROJECT``).
           location (str): The `location
             <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
             to send API requests to (for example, ``us-central1``). Can be obtained
             from environment variables.
           debug_config (DebugConfig): Config settings that control network behavior
             of the client. This is typically used when running test code.
           http_options (Union[HttpOptions, HttpOptionsDict]): Http options to use
             for the client.
        """

        self._debug_config = debug_config or client.DebugConfig()
        if isinstance(http_options, dict):
            http_options = types.HttpOptions(**http_options)

        self._api_client = client.Client._get_api_client(
            vertexai=True,
            credentials=credentials,
            project=project,
            location=location,
            debug_config=self._debug_config,
            http_options=http_options,
        )

        self._evals = Evals(self._api_client)

    @property
    def evals(self) -> Evals:
        return self._evals
