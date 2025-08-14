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

"""Live AgentEngine API client."""

import contextlib
import json
from typing import Any, AsyncIterator, Dict, Optional
import google.auth

from google.genai import _api_module
from .types import QueryAgentEngineConfig, QueryAgentEngineConfigOrDict


try:
    from websockets.asyncio.client import ClientConnection
    from websockets.asyncio.client import connect as ws_connect
except ModuleNotFoundError:
    # This try/except is for TAP, mypy complains about it which is why we have the type: ignore
    from websockets.client import ClientConnection  # type: ignore
    from websockets.client import connect as ws_connect  # type: ignore


class AsyncLiveAgentEngineSession:
    """[Preview] AsyncSession."""

    def __init__(self, websocket: ClientConnection):
        self._ws = websocket

    async def send(self, query_input: Dict[str, Any]) -> None:
        """Send a query input to the Agent.

        Args:
          query_input: A JSON serializable Python Dict to be send to the Agent.
        """

        await self._ws.send(json.dumps({"bidi_stream_input": query_input}))

    async def receive(self) -> Dict[str, Any]:
        """Receive one response from the Agent.

        Returns:
          A response from the Agent.

        Raises:
          websockets.exceptions.ConnectionClosed: If the connection is closed.
        """

        response = await self._ws.recv()
        return json.loads(response)

    async def close(self) -> None:
        """Close the connection."""
        await self._ws.close()


class AsyncLiveAgentEngines(_api_module.BaseModule):
    """AsyncLiveAgentEngines.

      Example usage:

      .. code-block:: python

        from pathlib import Path

        from google import genai
        from google.genai import types

        class MyAgentEngine(client):
          def bidi_stream_query(self, input_queue: asyncio.Queue):
            while True:
              input = await input_queue.get()
              yield {"output": f"Agent received {input}!"}

        client = genai.Client()
        agent_engine = client.agent_engines.create(agent)

        async with agent_engine.connect(
            setup={"class_method": "bidi_stream_query"},
        ) as session:
          await session.send(input={"input": "Hello world"})

          response = await session.receive()
          # {"output": "Agent received Hello world!"}
          ...
    """

    @contextlib.asynccontextmanager
    async def connect(
        self,
        *,
        agent_engine: str,
        config: Optional[QueryAgentEngineConfigOrDict] = None,
    ) -> AsyncIterator[AsyncLiveAgentEngineSession]:
        """Connect to the agent deployed to Agent Engine in a live (bidirectional streaming) session.

        Args:
          agent_engine: The resource name of the Agent Engine to use for the
            live session.
          class_method: The class method to use for the live
            session.
          initial_input: The initial input to send to the Agent.
            This is a JSON serializable Python Dict.

        Yields:
          An AsyncLiveAgentEngineSession object.
        """
        if isinstance(config, dict):
            config = QueryAgentEngineConfig(**config)
        request_dict = {
            "setup": {
                "name": f"projects/{self._api_client.project}/locations/{self._api_client.location}/reasoningEngines/{agent_engine}"
            }
        }
        if config.class_method:
            request_dict["setup"]["class_method"] = config.class_method
        if config.input:
            request_dict["setup"]["input"] =config.input

        request = json.dumps(request_dict)

        if not self._api_client._credentials:
            # Get bearer token through Application Default Credentials.
            creds, _ = google.auth.default(  # type: ignore
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
        else:
            creds = self._api_client._credentials
            # creds.valid is False, and creds.token is None
            # Need to refresh credentials to populate those
            if not (creds.token and creds.valid):
                auth_req = google.auth.transport.requests.Request()  # type: ignore
                creds.refresh(auth_req)
        bearer_token = creds.token

        original_headers = self._api_client._http_options.headers
        headers = original_headers.copy() if original_headers is not None else {}
        headers["Authorization"] = f"Bearer {bearer_token}"

        base_url = self._api_client._websocket_base_url()
        if isinstance(base_url, bytes):
            base_url = base_url.decode("utf-8")
        uri = (
            f"{base_url}/ws/"
            "google.cloud.aiplatform.v1beta1.ReasoningEngineExecutionService/"
            "BidiQueryReasoningEngine"
        )

        async with ws_connect(
            uri, additional_headers=headers, **self._api_client._websocket_ssl_ctx
        ) as ws:
            await ws.send(request)
            yield AsyncLiveAgentEngineSession(websocket=ws)

