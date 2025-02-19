from google.genai import _api_client
from .agentengines import AgentEngines


class Client:
    def __init__(self, api_client: _api_client.BaseApiClient):
        self._api_client = api_client
        self._agent_engines = AgentEngines(api_client)

    @property
    def agent_engines(self) -> AgentEngines:
        return self._agent_engines