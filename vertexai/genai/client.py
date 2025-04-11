from typing import Optional, Union

import google.auth
from google.genai import _api_client
from google.genai import client
from google.genai import types
from . import endpoints


class Client:
  def __init__(
      self,
      *,
      api_key: Optional[str] = None,
      credentials: Optional[google.auth.credentials.Credentials] = None,
      project: Optional[str] = None,
      location: Optional[str] = None,
      debug_config: Optional[client.DebugConfig] = None,
      http_options: Optional[
          Union[types.HttpOptions, types.HttpOptionsDict]
      ] = None,
  ):
    """Initializes the client.

    Args:
       api_key (str): The `API key
         <https://ai.google.dev/gemini-api/docs/api-key>`_ to use for
         authentication. Applies to the Gemini Developer API only.
       credentials (google.auth.credentials.Credentials): The credentials to use
         for authentication when calling the Vertex AI APIs. Credentials can be
         obtained from environment variables and default credentials. For more
         information, see `Set up Application Default Credentials
         <https://cloud.google.com/docs/authentication/provide-credentials-adc>`_.
         Applies to the Vertex AI API only.
       project (str): The `Google Cloud project ID
         <https://cloud.google.com/vertex-ai/docs/start/cloud-environment>`_ to
         use for quota. Can be obtained from environment variables (for example,
         ``GOOGLE_CLOUD_PROJECT``). Applies to the Vertex AI API only.
       location (str): The `location
         <https://cloud.google.com/vertex-ai/generative-ai/docs/learn/locations>`_
         to send API requests to (for example, ``us-central1``). Can be obtained
         from environment variables. Applies to the Vertex AI API only.
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
        api_key=api_key,
        credentials=credentials,
        project=project,
        location=location,
        debug_config=self._debug_config,
        http_options=http_options,
    )

    self._endpoints = endpoints.Endpoints(self._api_client)

  @property
  def endpoints(self) -> endpoints.Endpoints:
    return self._endpoints
