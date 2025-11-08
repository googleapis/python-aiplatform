# Copyright 2024 Google LLC
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
import base64
import importlib
import json
import os
import cloudpickle
import sys
import re
from unittest import mock
from typing import Optional

from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import storage
import vertexai
from google.cloud import aiplatform
from google.cloud.aiplatform_v1 import types as aip_types
from google.cloud.aiplatform_v1.services import reasoning_engine_service
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from vertexai.agent_engines import _utils
from vertexai import agent_engines
from vertexai.agent_engines.templates import adk as adk_template
from vertexai.agent_engines import _agent_engines
from google.api_core import operation as ga_operation
from google.genai import types
import pytest
import uuid


try:
    from google.adk.agents import llm_agent

    Agent = llm_agent.Agent
except ImportError:

    class Agent:
        def __init__(self, name: str, model: str):
            self.name = name
            self.model = model


_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_API_KEY = "test-api-key"
_TEST_MODEL = "gemini-2.0-flash"
_TEST_USER_ID = "test_user_id"
_TEST_AGENT_NAME = "test_agent"
_TEST_AGENT = Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
_TEST_SESSION = {
    "id": "ca18c25a-644b-4e13-9b24-78c150ec3eb9",
    "app_name": "default-app-name",
    "user_id": _TEST_USER_ID,
    "events": [
        {
            "author": "user",
            "content": {
                "parts": [{"text": "My cat's name is Garfield"}],
                "role": "user",
            },
        },
        {
            "author": "my_personal_agent",
            "content": {
                "parts": [{"text": "Okay, good to know!"}],
                "role": "model",
            },
        },
    ],
}
_TEST_SEARCH_MEMORY_QUERY = "What is my cat's name"
_TEST_RUN_CONFIG = {
    "save_input_blobs_as_artifacts": False,
    "support_cfc": False,
    "streaming_mode": "sse",
    "max_llm_calls": 500,
}
_TEST_STAGING_BUCKET = "gs://test-bucket"
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_AGENT_ENGINE_DISPLAY_NAME = "Agent Engine Display Name"
_TEST_GCS_DIR_NAME = _agent_engines._DEFAULT_GCS_DIR_NAME
_TEST_BLOB_FILENAME = _agent_engines._BLOB_FILENAME
_TEST_REQUIREMENTS_FILE = _agent_engines._REQUIREMENTS_FILE
_TEST_EXTRA_PACKAGES_FILE = _agent_engines._EXTRA_PACKAGES_FILE
_TEST_AGENT_ENGINE_GCS_URI = "{}/{}/{}".format(
    _TEST_STAGING_BUCKET,
    _TEST_GCS_DIR_NAME,
    _TEST_BLOB_FILENAME,
)
_TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI = "{}/{}/{}".format(
    _TEST_STAGING_BUCKET,
    _TEST_GCS_DIR_NAME,
    _TEST_EXTRA_PACKAGES_FILE,
)
_TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI = "{}/{}/{}".format(
    _TEST_STAGING_BUCKET,
    _TEST_GCS_DIR_NAME,
    _TEST_REQUIREMENTS_FILE,
)
_TEST_AGENT_ENGINE_PACKAGE_SPEC = aip_types.ReasoningEngineSpec.PackageSpec(
    python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
    pickle_object_gcs_uri=_TEST_AGENT_ENGINE_GCS_URI,
    dependency_files_gcs_uri=_TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI,
    requirements_gcs_uri=_TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
)
_ADK_AGENT_FRAMEWORK = adk_template.AdkApp.agent_framework
_TEST_AGENT_ENGINE_OBJ = aip_types.ReasoningEngine(
    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
    spec=aip_types.ReasoningEngineSpec(
        package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
        agent_framework=_ADK_AGENT_FRAMEWORK,
    ),
)

GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY = (
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        credentials_mock = mock.Mock()
        credentials_mock.with_quota_project.return_value = None
        google_auth_mock.return_value = (
            credentials_mock,
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.fixture
def vertexai_init_mock():
    with mock.patch.object(vertexai, "init") as vertexai_init_mock:
        yield vertexai_init_mock


@pytest.fixture
def otlp_span_exporter_mock():
    with mock.patch(
        "opentelemetry.exporter.otlp.proto.http.trace_exporter.OTLPSpanExporter"
    ) as otlp_span_exporter_mock:
        yield otlp_span_exporter_mock


@pytest.fixture
def trace_provider_mock():
    import opentelemetry.sdk.trace

    with mock.patch.object(
        opentelemetry.sdk.trace, "TracerProvider"
    ) as tracer_provider_mock:
        yield tracer_provider_mock


@pytest.fixture
def trace_provider_force_flush_mock():
    import opentelemetry.trace
    import opentelemetry.sdk.trace

    with mock.patch.object(
        opentelemetry.trace, "get_tracer_provider"
    ) as get_tracer_provider_mock:
        get_tracer_provider_mock.return_value = mock.Mock(
            spec=opentelemetry.sdk.trace.TracerProvider()
        )
        yield get_tracer_provider_mock.return_value.force_flush


@pytest.fixture
def logger_provider_force_flush_mock():
    import opentelemetry._logs
    import opentelemetry.sdk._logs

    with mock.patch.object(
        opentelemetry._logs, "get_logger_provider"
    ) as get_logger_provider_mock:
        get_logger_provider_mock.return_value = mock.Mock(
            spec=opentelemetry.sdk._logs.LoggerProvider()
        )
        yield get_logger_provider_mock.return_value.force_flush


@pytest.fixture
def default_instrumentor_builder_mock():
    with mock.patch(
        "google.cloud.aiplatform.vertexai.agent_engines.templates.adk._default_instrumentor_builder"
    ) as default_instrumentor_builder_mock:
        yield default_instrumentor_builder_mock


@pytest.fixture
def simple_span_processor_mock():
    with mock.patch(
        "opentelemetry.sdk.trace.export.SimpleSpanProcessor"
    ) as simple_span_processor_mock:
        yield simple_span_processor_mock


@pytest.fixture
def adk_version_mock():
    with mock.patch(
        "google.cloud.aiplatform.vertexai.agent_engines.templates.adk.get_adk_version"
    ) as adk_version_mock:
        yield adk_version_mock


class _MockRunner:
    def run(self, *args, **kwargs):
        from google.adk.events import event

        yield event.Event(
            **{
                "author": "currency_exchange_agent",
                "content": {
                    "parts": [
                        {
                            "thought_signature": b"test_signature",
                            "function_call": {
                                "args": {
                                    "currency_date": "2025-04-03",
                                    "currency_from": "USD",
                                    "currency_to": "SEK",
                                },
                                "id": "af-c5a57692-9177-4091-a3df-098f834ee849",
                                "name": "get_exchange_rate",
                            },
                        }
                    ],
                    "role": "model",
                },
                "id": "9aaItGK9",
                "invocation_id": "e-6543c213-6417-484b-9551-b67915d1d5f7",
            }
        )

    async def run_async(self, *args, **kwargs):
        from google.adk.events import event

        yield event.Event(
            **{
                "author": "currency_exchange_agent",
                "content": {
                    "parts": [
                        {
                            "thought_signature": b"test_signature",
                            "function_call": {
                                "args": {
                                    "currency_date": "2025-04-03",
                                    "currency_from": "USD",
                                    "currency_to": "SEK",
                                },
                                "id": "af-c5a57692-9177-4091-a3df-098f834ee849",
                                "name": "get_exchange_rate",
                            },
                        }
                    ],
                    "role": "model",
                },
                "id": "9aaItGK9",
                "invocation_id": "e-6543c213-6417-484b-9551-b67915d1d5f7",
            }
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestAdkApp:
    def test_adk_version(self):
        with mock.patch(
            "google.cloud.aiplatform.vertexai.agent_engines.templates.adk.get_adk_version",
            return_value="0.5.0",
        ):
            with pytest.raises(
                ValueError,
                match=(
                    "Unsupported google-adk version: 0.5.0, please use"
                    " google-adk>=1.5.0 for AdkApp deployment on Agent Engine."
                ),
            ):
                agent_engines.AdkApp(agent=_TEST_AGENT)

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(vertexai)
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("project") == _TEST_PROJECT
        assert app._tmpl_attrs.get("location") == _TEST_LOCATION
        assert app._tmpl_attrs.get("runner") is None

    def test_set_up(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None

    def test_clone(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None
        app_clone = app.clone()
        assert app._tmpl_attrs.get("runner") is not None
        assert app_clone._tmpl_attrs.get("runner") is None
        app_clone.set_up()
        assert app_clone._tmpl_attrs.get("runner") is not None

    def test_register_operations(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        for operations in app.register_operations().values():
            for operation in operations:
                assert operation in dir(app)

    def test_stream_query(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = list(
            app.stream_query(
                user_id=_TEST_USER_ID,
                message="test message",
            )
        )
        assert len(events) == 1

    def test_stream_query_with_content(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = list(
            app.stream_query(
                user_id=_TEST_USER_ID,
                message=types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text="test message with content",
                        )
                    ],
                ).model_dump(),
            )
        )
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_async_stream_query(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = []
        async for event in app.async_stream_query(
            user_id=_TEST_USER_ID,
            message="test message",
        ):
            events.append(event)
        assert len(events) == 1

    @pytest.mark.asyncio
    @mock.patch.dict(
        os.environ,
        {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
    )
    async def test_async_stream_query_force_flush_otel(
        self,
        trace_provider_force_flush_mock: mock.Mock,
        logger_provider_force_flush_mock: mock.Mock,
    ):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        async for _ in app.async_stream_query(
            user_id=_TEST_USER_ID,
            message="test message",
        ):
            pass

        trace_provider_force_flush_mock.assert_called_once()
        logger_provider_force_flush_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_stream_query_with_content(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = []
        async for event in app.async_stream_query(
            user_id=_TEST_USER_ID,
            message=types.Content(
                role="user",
                parts=[
                    types.Part(
                        text="test message with content",
                    )
                ],
            ).model_dump(),
        ):
            events.append(event)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_streaming_agent_run_with_events(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        app._tmpl_attrs["in_memory_runner"] = _MockRunner()
        request_json = json.dumps(
            {
                "artifacts": [
                    {
                        "file_name": "test_file_name",
                        "versions": [{"version": "v1", "data": "v1data"}],
                    }
                ],
                "authorizations": {
                    "test_user_id1": {"access_token": "test_access_token"},
                    "test_user_id2": {"accessToken": "test-access-token"},
                },
                "user_id": _TEST_USER_ID,
                "message": {
                    "parts": [{"text": "What is the exchange rate from USD to SEK?"}],
                    "role": "user",
                },
            }
        )
        events = []
        async for event in app.streaming_agent_run_with_events(
            request_json=request_json,
        ):
            events.append(event)
        assert len(events) == 1

    @pytest.mark.asyncio
    @mock.patch.dict(
        os.environ,
        {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
    )
    async def test_streaming_agent_run_with_events_force_flush_otel(
        self,
        trace_provider_force_flush_mock: mock.Mock,
        logger_provider_force_flush_mock: mock.Mock,
    ):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        app._tmpl_attrs["in_memory_runner"] = _MockRunner()
        request_json = json.dumps(
            {
                "artifacts": [
                    {
                        "file_name": "test_file_name",
                        "versions": [{"version": "v1", "data": "v1data"}],
                    }
                ],
                "authorizations": {
                    "test_user_id1": {"access_token": "test_access_token"},
                    "test_user_id2": {"accessToken": "test-access-token"},
                },
                "user_id": _TEST_USER_ID,
                "message": {
                    "parts": [{"text": "What is the exchange rate from USD to SEK?"}],
                    "role": "user",
                },
            }
        )
        async for _ in app.streaming_agent_run_with_events(
            request_json=request_json,
        ):
            pass

        trace_provider_force_flush_mock.assert_called_once()
        logger_provider_force_flush_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_create_session(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        session1 = await app.async_create_session(user_id=_TEST_USER_ID)
        assert session1.user_id == _TEST_USER_ID
        session2 = await app.async_create_session(
            user_id=_TEST_USER_ID, session_id="test_session_id"
        )
        assert session2.user_id == _TEST_USER_ID
        assert session2.id == "test_session_id"

    @pytest.mark.asyncio
    async def test_async_get_session(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        session1 = await app.async_create_session(user_id=_TEST_USER_ID)
        session2 = await app.async_get_session(
            user_id=_TEST_USER_ID,
            session_id=session1.id,
        )
        assert session2.user_id == _TEST_USER_ID
        assert session1.id == session2.id

    @pytest.mark.asyncio
    async def test_async_list_sessions(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        response0 = await app.async_list_sessions(user_id=_TEST_USER_ID)
        assert not response0.sessions
        session = await app.async_create_session(user_id=_TEST_USER_ID)
        response1 = await app.async_list_sessions(user_id=_TEST_USER_ID)
        assert len(response1.sessions) == 1
        assert response1.sessions[0].id == session.id
        session2 = await app.async_create_session(user_id=_TEST_USER_ID)
        response2 = await app.async_list_sessions(user_id=_TEST_USER_ID)
        assert len(response2.sessions) == 2
        assert response2.sessions[0].id == session.id
        assert response2.sessions[1].id == session2.id

    @pytest.mark.asyncio
    async def test_async_delete_session(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        response = await app.async_delete_session(
            user_id=_TEST_USER_ID,
            session_id="",
        )
        assert not response
        session = await app.async_create_session(user_id=_TEST_USER_ID)
        response1 = await app.async_list_sessions(user_id=_TEST_USER_ID)
        assert len(response1.sessions) == 1
        await app.async_delete_session(
            user_id=_TEST_USER_ID,
            session_id=session.id,
        )
        response0 = await app.async_list_sessions(user_id=_TEST_USER_ID)
        assert not response0.sessions

    def test_create_session(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        session1 = app.create_session(user_id=_TEST_USER_ID)
        assert session1.user_id == _TEST_USER_ID
        session2 = app.create_session(
            user_id=_TEST_USER_ID, session_id="test_session_id"
        )
        assert session2.user_id == _TEST_USER_ID
        assert session2.id == "test_session_id"

    def test_get_session(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        session1 = app.create_session(user_id=_TEST_USER_ID)
        session2 = app.get_session(
            user_id=_TEST_USER_ID,
            session_id=session1.id,
        )
        assert session2.user_id == _TEST_USER_ID
        assert session1.id == session2.id

    def test_list_sessions(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        response0 = app.list_sessions(user_id=_TEST_USER_ID)
        assert not response0.sessions
        session = app.create_session(user_id=_TEST_USER_ID)
        response1 = app.list_sessions(user_id=_TEST_USER_ID)
        assert len(response1.sessions) == 1
        assert response1.sessions[0].id == session.id
        session2 = app.create_session(user_id=_TEST_USER_ID)
        response2 = app.list_sessions(user_id=_TEST_USER_ID)
        assert len(response2.sessions) == 2
        assert response2.sessions[0].id == session.id
        assert response2.sessions[1].id == session2.id

    def test_delete_session(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        response = app.delete_session(user_id=_TEST_USER_ID, session_id="")
        assert not response
        session = app.create_session(user_id=_TEST_USER_ID)
        response1 = app.list_sessions(user_id=_TEST_USER_ID)
        assert len(response1.sessions) == 1
        app.delete_session(user_id=_TEST_USER_ID, session_id=session.id)
        response0 = app.list_sessions(user_id=_TEST_USER_ID)
        assert not response0.sessions

    @pytest.mark.asyncio
    async def test_async_add_session_to_memory_dict(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        response = await app.async_search_memory(
            user_id=_TEST_USER_ID,
            query=_TEST_SEARCH_MEMORY_QUERY,
        )
        assert not response.memories
        await app.async_add_session_to_memory(session=_TEST_SESSION)
        response = await app.async_search_memory(
            user_id=_TEST_USER_ID,
            query=_TEST_SEARCH_MEMORY_QUERY,
        )
        assert len(response.memories) >= 1

    @pytest.mark.asyncio
    async def test_async_search_memory(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        response = await app.async_search_memory(
            user_id=_TEST_USER_ID,
            query=_TEST_SEARCH_MEMORY_QUERY,
        )
        assert not response.memories
        await app.async_add_session_to_memory(session=_TEST_SESSION)
        response = await app.async_search_memory(
            user_id=_TEST_USER_ID,
            query=_TEST_SEARCH_MEMORY_QUERY,
        )
        assert len(response.memories) >= 1

    @pytest.mark.parametrize(
        "adk_version,enable_tracing,enable_telemetry,want_tracing_setup,want_logging_setup",
        [
            ("1.16.0", False, False, False, False),
            ("1.16.0", False, True, False, True),
            ("1.16.0", False, None, False, False),
            ("1.16.0", True, False, False, False),
            ("1.16.0", True, True, True, True),
            ("1.16.0", True, None, True, False),
            ("1.16.0", None, False, False, False),
            ("1.16.0", None, True, False, True),
            ("1.16.0", None, None, False, False),
            ("1.16.0", None, "unspecified", False, False),
            ("1.16.0", False, "unspecified", False, False),
            ("1.16.0", True, "unspecified", True, False),
            ("1.17.0", False, False, False, False),
            ("1.17.0", False, True, False, True),
            ("1.17.0", False, None, False, False),
            ("1.17.0", True, False, False, False),
            ("1.17.0", True, True, True, True),
            ("1.17.0", True, None, True, False),
            ("1.17.0", None, False, False, False),
            ("1.17.0", None, True, True, True),
            ("1.17.0", None, None, False, False),
            ("1.17.0", None, "unspecified", False, False),
            ("1.17.0", False, "unspecified", False, False),
            ("1.17.0", True, "unspecified", True, False),
        ],
    )
    @mock.patch.dict(os.environ)
    def test_default_instrumentor_enablement(
        self,
        adk_version: str,
        enable_tracing: Optional[bool],
        enable_telemetry: Optional[bool],
        want_tracing_setup: bool,
        want_logging_setup: bool,
        default_instrumentor_builder_mock: mock.Mock,
        adk_version_mock: mock.Mock,
    ):
        # Arrange
        adk_version_mock.return_value = adk_version
        if enable_telemetry is not None:
            os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"] = str(
                enable_telemetry
            )

        app = agent_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=enable_tracing)

        # Act
        app.set_up()

        # Assert
        default_instrumentor_builder_mock.assert_called_once_with(
            _TEST_PROJECT,
            enable_tracing=want_tracing_setup,
            enable_logging=want_logging_setup,
        )

    @pytest.mark.parametrize(
        "adk_version,enable_tracing,enable_telemetry,want_custom_instrumentor_called",
        [
            ("1.16.0", False, False, False),
            ("1.16.0", False, True, False),
            ("1.16.0", False, None, False),
            ("1.16.0", True, False, False),
            ("1.16.0", True, True, True),
            ("1.16.0", True, None, True),
            ("1.16.0", None, False, False),
            ("1.16.0", None, True, False),
            ("1.16.0", None, None, False),
            ("1.16.0", None, "unspecified", False),
            ("1.16.0", False, "unspecified", False),
            ("1.16.0", True, "unspecified", True),
            ("1.17.0", False, False, False),
            ("1.17.0", False, True, False),
            ("1.17.0", False, None, False),
            ("1.17.0", True, False, False),
            ("1.17.0", True, True, True),
            ("1.17.0", True, None, True),
            ("1.17.0", None, False, False),
            ("1.17.0", None, True, True),
            ("1.17.0", None, None, False),
            ("1.17.0", None, "unspecified", False),
            ("1.17.0", False, "unspecified", False),
            ("1.17.0", True, "unspecified", True),
        ],
    )
    @mock.patch.dict(os.environ)
    def test_custom_instrumentor_enablement(
        self,
        adk_version: str,
        enable_tracing: Optional[bool],
        enable_telemetry: Optional[bool],
        want_custom_instrumentor_called: bool,
        adk_version_mock: mock.Mock,
    ):
        # Arrange
        adk_version_mock.return_value = adk_version
        if enable_telemetry is not None:
            os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"] = str(
                enable_telemetry
            )
        custom_instrumentor = mock.Mock()
        app = agent_engines.AdkApp(
            agent=_TEST_AGENT,
            enable_tracing=enable_tracing,
            instrumentor_builder=custom_instrumentor,
        )

        # Act
        app.set_up()

        # Assert
        if want_custom_instrumentor_called:
            custom_instrumentor.assert_called_once_with(_TEST_PROJECT)
        else:
            custom_instrumentor.assert_not_called()

    @mock.patch.dict(
        os.environ,
        {
            "GOOGLE_CLOUD_AGENT_ENGINE_ID": "test_agent_id",
            "OTEL_RESOURCE_ATTRIBUTES": "some-attribute=some-value",
        },
    )
    def test_tracing_setup(
        self,
        monkeypatch,
        trace_provider_mock: mock.Mock,
        otlp_span_exporter_mock: mock.Mock,
    ):
        monkeypatch.setattr(
            "uuid.uuid4", lambda: uuid.UUID("12345678123456781234567812345678")
        )
        monkeypatch.setattr("os.getpid", lambda: 123123123)
        app = agent_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=True)
        app.set_up()

        expected_attributes = {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.36.0",
            "gcp.project_id": "test-project",
            "cloud.account.id": "test-project",
            "cloud.platform": "gcp.agent_engine",
            "service.name": "test_agent_id",
            "cloud.resource_id": "//aiplatform.googleapis.com/projects/test-project/locations/us-central1/reasoningEngines/test_agent_id",
            "service.instance.id": "12345678123456781234567812345678-123123123",
            "cloud.region": "us-central1",
            "some-attribute": "some-value",
        }

        otlp_span_exporter_mock.assert_called_once_with(
            session=mock.ANY,
            endpoint="https://telemetry.googleapis.com/v1/traces",
            headers=mock.ANY,
        )

        user_agent = otlp_span_exporter_mock.call_args.kwargs["headers"]["User-Agent"]
        assert (
            re.fullmatch(
                r"Vertex-Agent-Engine\/[\d\.]+ OTel-OTLP-Exporter-Python\/[\d\.]+",
                user_agent,
            )
            is not None
        )
        assert (
            trace_provider_mock.call_args.kwargs["resource"].attributes
            == expected_attributes
        )

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing(
        self,
        caplog,
        tracer_provider_mock,
        simple_span_processor_mock,
    ):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("instrumentor") is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # agent.set_up()
        # assert agent._tmpl_attrs.get("instrumentor") is not None
        # assert (
        #     "enable_tracing=True but proceeding with tracing disabled"
        #     not in caplog.text
        # )

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing_warning(self, caplog):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("instrumentor") is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # app.set_up()
        # assert "enable_tracing=True but proceeding with tracing disabled" in caplog.text

    # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
    # @pytest.mark.parametrize(
    #     "enable_tracing,want_warning",
    #     [
    #         (True, False),
    #         (False, True),
    #         (None, False),
    #     ],
    # )
    # @pytest.mark.usefixtures("caplog")
    # def test_tracing_disabled_warning(self, enable_tracing, want_warning, caplog):
    #     _ = agent_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=enable_tracing)
    #     assert (
    #         "[WARNING] Your 'enable_tracing=False' setting" in caplog.text
    #     ) == want_warning

    @mock.patch.dict(os.environ)
    def test_span_content_capture_disabled_by_default(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "false"

    @mock.patch.dict(
        os.environ, {"OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true"}
    )
    def test_span_content_capture_disabled_with_env_var(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "false"

    @mock.patch.dict(os.environ)
    def test_span_content_capture_enabled_with_tracing(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=True)
        app.set_up()
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "true"


def test_dump_event_for_json():
    from google.adk.events import event

    raw_signature = b"test_signature"
    # Create an event with both a ThoughtPart and a FunctionCallPart
    test_event = event.Event(
        **{
            "author": _TEST_AGENT_NAME,
            "content": {
                "parts": [
                    {
                        "thought_signature": raw_signature,
                        "text": "This is a test",
                    },
                ],
                "role": "model",
            },
            "id": "test_id",
            "invocation_id": "test_invocation_id",
        }
    )
    dumped_event = _utils.dump_event_for_json(test_event)

    part = dumped_event["content"]["parts"][0]
    assert "text" in part
    assert part["text"] == "This is a test"
    assert "thought_signature" in part
    assert isinstance(part["thought_signature"], str)
    assert base64.b64decode(part["thought_signature"]) == raw_signature


def test_adk_app_initialization_with_api_key():
    importlib.reload(initializer)
    importlib.reload(vertexai)
    try:
        vertexai.init(api_key=_TEST_API_KEY)
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("project") is None
        assert app._tmpl_attrs.get("location") is None
        assert app._tmpl_attrs.get("express_mode_api_key") == _TEST_API_KEY
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None
        assert os.environ.get("GOOGLE_API_KEY") == _TEST_API_KEY
        assert "GOOGLE_CLOUD_LOCATION" not in os.environ
        assert "GOOGLE_CLOUD_PROJECT" not in os.environ
    finally:
        initializer.global_pool.shutdown(wait=True)


def test_adk_app_initialization_with_env_api_key():
    try:
        os.environ["GOOGLE_API_KEY"] == _TEST_API_KEY
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        assert app._tmpl_attrs.get("project") is None
        assert app._tmpl_attrs.get("location") is None
        assert app._tmpl_attrs.get("express_mode_api_key") == _TEST_API_KEY
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None
        assert "GOOGLE_CLOUD_LOCATION" not in os.environ
        assert "GOOGLE_CLOUD_PROJECT" not in os.environ
    finally:
        initializer.global_pool.shutdown(wait=True)


@pytest.mark.usefixtures("mock_adk_version")
class TestAdkAppErrors:
    @pytest.mark.asyncio
    async def test_raise_get_session_not_found_error(self):
        with pytest.raises(
            RuntimeError,
            match=r"Session not found. Please create it using .create_session()",
        ):
            app = agent_engines.AdkApp(agent=_TEST_AGENT)
            await app.async_get_session(
                user_id="non_existent_user",
                session_id="test_session_id",
            )

    @pytest.mark.asyncio
    async def test_async_stream_query_invalid_message_type(self):
        app = agent_engines.AdkApp(agent=_TEST_AGENT)
        with pytest.raises(
            TypeError,
            match="message must be a string or a dictionary representing a Content object.",
        ):
            async for _ in app.async_stream_query(user_id=_TEST_USER_ID, message=123):
                pass


@pytest.fixture(scope="module")
def create_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "create_reasoning_engine",
    ) as create_agent_engine_mock:
        create_agent_engine_lro_mock = mock.Mock(ga_operation.Operation)
        create_agent_engine_lro_mock.result.return_value = _TEST_AGENT_ENGINE_OBJ
        create_agent_engine_mock.return_value = create_agent_engine_lro_mock
        yield create_agent_engine_mock


@pytest.fixture(scope="module")
def get_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "get_reasoning_engine",
    ) as get_agent_engine_mock:
        api_client_mock = mock.Mock()
        api_client_mock.get_reasoning_engine.return_value = _TEST_AGENT_ENGINE_OBJ
        get_agent_engine_mock.return_value = api_client_mock
        yield get_agent_engine_mock


@pytest.fixture(scope="module")
def cloud_storage_create_bucket_mock():
    with mock.patch.object(storage, "Client") as cloud_storage_mock:
        bucket_mock = mock.Mock(spec=storage.Bucket)
        bucket_mock.blob.return_value.open.return_value = "blob_file"
        bucket_mock.blob.return_value.upload_from_filename.return_value = None
        bucket_mock.blob.return_value.upload_from_string.return_value = None

        cloud_storage_mock.get_bucket = mock.Mock(
            side_effect=ValueError("bucket not found")
        )
        cloud_storage_mock.bucket.return_value = bucket_mock
        cloud_storage_mock.create_bucket.return_value = bucket_mock

        yield cloud_storage_mock


@pytest.fixture(scope="module")
def cloudpickle_dump_mock():
    with mock.patch.object(cloudpickle, "dump") as cloudpickle_dump_mock:
        yield cloudpickle_dump_mock


@pytest.fixture(scope="module")
def cloudpickle_load_mock():
    with mock.patch.object(cloudpickle, "load") as cloudpickle_load_mock:
        yield cloudpickle_load_mock


@pytest.fixture(scope="function")
def get_gca_resource_mock():
    with mock.patch.object(
        base.VertexAiResourceNoun,
        "_get_gca_resource",
    ) as get_gca_resource_mock:
        get_gca_resource_mock.return_value = _TEST_AGENT_ENGINE_OBJ
        yield get_gca_resource_mock


# Function scope is required for the pytest parameterized tests.
@pytest.fixture(scope="function")
def update_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "update_reasoning_engine",
    ) as update_agent_engine_mock:
        yield update_agent_engine_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestAgentEngines:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "env_vars,expected_env_vars",
        [
            ({}, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (None, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (
                {"some_env": "some_val"},
                {
                    "some_env": "some_val",
                    GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified",
                },
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
            ),
        ],
    )
    def test_create_default_telemetry_enablement(
        self,
        create_agent_engine_mock: mock.Mock,
        cloud_storage_create_bucket_mock: mock.Mock,
        cloudpickle_dump_mock: mock.Mock,
        cloudpickle_load_mock: mock.Mock,
        get_gca_resource_mock: mock.Mock,
        env_vars: dict[str, str],
        expected_env_vars: dict[str, str],
    ):
        agent_engines.create(
            agent_engine=agent_engines.AdkApp(agent=_TEST_AGENT),
            env_vars=env_vars,
        )
        create_agent_engine_mock.assert_called_once()
        deployment_spec = create_agent_engine_mock.call_args.kwargs[
            "reasoning_engine"
        ].spec.deployment_spec
        assert _utils.to_dict(deployment_spec)["env"] == [
            {"name": key, "value": value} for key, value in expected_env_vars.items()
        ]

    @pytest.mark.parametrize(
        "env_vars,expected_env_vars",
        [
            ({}, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (None, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (
                {"some_env": "some_val"},
                {
                    "some_env": "some_val",
                    GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified",
                },
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
            ),
        ],
    )
    def test_update_default_telemetry_enablement(
        self,
        update_agent_engine_mock: mock.Mock,
        cloud_storage_create_bucket_mock: mock.Mock,
        cloudpickle_dump_mock: mock.Mock,
        cloudpickle_load_mock: mock.Mock,
        get_gca_resource_mock: mock.Mock,
        get_agent_engine_mock: mock.Mock,
        env_vars: dict[str, str],
        expected_env_vars: dict[str, str],
    ):
        agent_engines.update(
            resource_name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            description="foobar",  # avoid "At least one of ... must be specified" errors.
            env_vars=env_vars,
        )
        update_agent_engine_mock.assert_called_once()
        deployment_spec = update_agent_engine_mock.call_args.kwargs[
            "request"
        ].reasoning_engine.spec.deployment_spec
        assert _utils.to_dict(deployment_spec)["env"] == [
            {"name": key, "value": value} for key, value in expected_env_vars.items()
        ]
