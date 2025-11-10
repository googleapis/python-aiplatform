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
import asyncio
import base64
import importlib
import json
import os
import re
from unittest import mock
from typing import Optional

from google import auth
import vertexai
from google.cloud.aiplatform import initializer
from vertexai.agent_engines import _utils
from vertexai.preview import reasoning_engines
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
def tracer_provider_mock():
    with mock.patch("opentelemetry.sdk.trace.TracerProvider") as tracer_provider_mock:
        yield tracer_provider_mock


@pytest.fixture
def simple_span_processor_mock():
    with mock.patch(
        "opentelemetry.sdk.trace.export.SimpleSpanProcessor"
    ) as simple_span_processor_mock:
        yield simple_span_processor_mock


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
        "google.cloud.aiplatform.vertexai.preview.reasoning_engines.templates.adk._default_instrumentor_builder"
    ) as default_instrumentor_builder_mock:
        yield default_instrumentor_builder_mock


@pytest.fixture
def adk_version_mock():
    with mock.patch(
        "google.cloud.aiplatform.vertexai.preview.reasoning_engines.templates.adk.get_adk_version"
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

    async def run_live(self, *args, **kwargs):
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
            "google.cloud.aiplatform.vertexai.preview.reasoning_engines.templates.adk.get_adk_version",
            return_value="0.5.0",
        ):
            with pytest.raises(
                ValueError,
                match=(
                    "Unsupported google-adk version: 0.5.0, please use"
                    " google-adk>=1.0.0 for AdkApp deployment."
                ),
            ):
                reasoning_engines.AdkApp(
                    agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
                )

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(vertexai)
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
        )
        assert app._tmpl_attrs.get("project") == _TEST_PROJECT
        assert app._tmpl_attrs.get("location") == _TEST_LOCATION
        assert app._tmpl_attrs.get("runner") is None

    def test_set_up(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
        )
        assert app._tmpl_attrs.get("runner") is None
        assert app._tmpl_attrs.get("session_service") is None
        assert app._tmpl_attrs.get("artifact_service") is None
        assert app._tmpl_attrs.get("memory_service") is None
        assert app._tmpl_attrs.get("credential_service") is None
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None
        assert app._tmpl_attrs.get("session_service") is not None
        assert app._tmpl_attrs.get("artifact_service") is not None
        assert app._tmpl_attrs.get("memory_service") is not None
        assert app._tmpl_attrs.get("credential_service") is not None

    def test_clone(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
        )
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None
        app_clone = app.clone()
        assert app._tmpl_attrs.get("runner") is not None
        assert app_clone._tmpl_attrs.get("runner") is None
        app_clone.set_up()
        assert app_clone._tmpl_attrs.get("runner") is not None

    def test_register_operations(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
        )
        for operations in app.register_operations().values():
            for operation in operations:
                assert operation in dir(app)

    def test_stream_query(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
        {"GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true"},
    )
    async def test_async_stream_query_force_flush_otel(
        self,
        trace_provider_force_flush_mock: mock.Mock,
        logger_provider_force_flush_mock: mock.Mock,
    ):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL), enable_tracing=True
        )
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
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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

    def test_streaming_agent_run_with_events(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
        events = list(app.streaming_agent_run_with_events(request_json=request_json))
        assert len(events) == 1

    @pytest.mark.asyncio
    @mock.patch.dict(
        os.environ,
        {"GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY": "true"},
    )
    async def test_streaming_agent_run_with_events_force_flush_otel(
        self,
        trace_provider_force_flush_mock: mock.Mock,
        logger_provider_force_flush_mock: mock.Mock,
    ):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
            enable_tracing=True,
        )
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
        list(app.streaming_agent_run_with_events(request_json=request_json))

        trace_provider_force_flush_mock.assert_called_once()
        logger_provider_force_flush_mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_bidi_stream_query(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        request_queue = asyncio.Queue()
        request_dict = {
            "user_id": _TEST_USER_ID,
            "live_request": {
                "input": "What is the exchange rate from USD to SEK?",
            },
        }

        await request_queue.put(request_dict)
        await request_queue.put(None)  # Sentinel to end the stream.
        events = []
        async for event in app.bidi_stream_query(request_queue):
            events.append(event)
        assert len(events) == 1

    def test_create_session(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        session1 = app.create_session(user_id=_TEST_USER_ID)
        assert session1.user_id == _TEST_USER_ID
        session2 = app.create_session(
            user_id=_TEST_USER_ID, session_id="test_session_id"
        )
        assert session2.user_id == _TEST_USER_ID
        assert session2.id == "test_session_id"

    def test_get_session(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        session1 = app.create_session(user_id=_TEST_USER_ID)
        session2 = app.get_session(
            user_id=_TEST_USER_ID,
            session_id=session1.id,
        )
        assert session2.user_id == _TEST_USER_ID
        assert session1.id == session2.id

    def test_list_sessions(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        response = app.delete_session(user_id=_TEST_USER_ID, session_id="")
        assert not response
        session = app.create_session(user_id=_TEST_USER_ID)
        response1 = app.list_sessions(user_id=_TEST_USER_ID)
        assert len(response1.sessions) == 1
        app.delete_session(user_id=_TEST_USER_ID, session_id=session.id)
        response0 = app.list_sessions(user_id=_TEST_USER_ID)
        assert not response0.sessions

    @pytest.mark.asyncio
    async def test_async_add_session_to_memory(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        assert app._tmpl_attrs.get("memory_service") is None
        session = app.create_session(user_id=_TEST_USER_ID)
        list(
            app.stream_query(
                user_id=_TEST_USER_ID,
                session_id=session.id,
                message="My cat's name is Garfield",
            )
        )
        await app.async_add_session_to_memory(
            session=app.get_session(
                user_id=_TEST_USER_ID,
                session_id=session.id,
            )
        )
        response = await app.async_search_memory(
            user_id=_TEST_USER_ID,
            query=_TEST_SEARCH_MEMORY_QUERY,
        )
        assert len(response.memories) >= 1

    @pytest.mark.asyncio
    async def test_async_add_session_to_memory_dict(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
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
            ("1.17.0", False, False, False, False),
            ("1.17.0", False, True, False, True),
            ("1.17.0", False, None, False, False),
            ("1.17.0", True, False, False, False),
            ("1.17.0", True, True, True, True),
            ("1.17.0", True, None, True, False),
            ("1.17.0", None, False, False, False),
            ("1.17.0", None, True, True, True),
            ("1.17.0", None, None, False, False),
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

        app = reasoning_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=enable_tracing)

        # Act
        app.set_up()

        # Assert
        default_instrumentor_builder_mock.assert_called_once_with(
            _TEST_PROJECT,
            enable_tracing=want_tracing_setup,
            enable_logging=want_logging_setup,
        )

    @mock.patch.dict(
        os.environ,
        {
            "GOOGLE_CLOUD_AGENT_ENGINE_ID": "test_agent_id",
            "OTEL_RESOURCE_ATTRIBUTES": "some-attribute=some-value",
        },
    )
    def test_tracing_setup(
        self,
        monkeypatch: pytest.MonkeyPatch,
        trace_provider_mock: mock.Mock,
        otlp_span_exporter_mock: mock.Mock,
    ):
        monkeypatch.setattr(
            "uuid.uuid4", lambda: uuid.UUID("12345678123456781234567812345678")
        )
        monkeypatch.setattr("os.getpid", lambda: 123123123)
        app = reasoning_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=True)
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

    @mock.patch.dict(os.environ)
    def test_span_content_capture_disabled_by_default(self):
        app = reasoning_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "false"

    @mock.patch.dict(
        os.environ, {"OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT": "true"}
    )
    def test_span_content_capture_disabled_with_env_var(self):
        app = reasoning_engines.AdkApp(agent=_TEST_AGENT)
        app.set_up()
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "false"

    @mock.patch.dict(os.environ)
    def test_span_content_capture_enabled_with_tracing(self):
        app = reasoning_engines.AdkApp(agent=_TEST_AGENT, enable_tracing=True)
        app.set_up()
        assert os.environ["ADK_CAPTURE_MESSAGE_CONTENT_IN_SPANS"] == "true"

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing(
        self,
        caplog,
        tracer_provider_mock,
        simple_span_processor_mock,
    ):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
            enable_tracing=True,
        )
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
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
            enable_tracing=True,
        )
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
    #     app = reasoning_engines.AdkApp(
    #         agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
    #         enable_tracing=enable_tracing
    #     )
    #     assert (
    #         "[WARNING] Your 'enable_tracing=False' setting" in caplog.text
    #     ) == want_warning


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


class TestAdkAppErrors:
    def test_raise_get_session_not_found_error(self):
        with pytest.raises(
            RuntimeError,
            match=r"Session not found. Please create it using .create_session()",
        ):
            app = reasoning_engines.AdkApp(
                agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL),
            )
            app.get_session(
                user_id="non_existent_user",
                session_id="test_session_id",
            )

    def test_stream_query_invalid_message_type(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        with pytest.raises(
            TypeError,
            match="message must be a string or a dictionary representing a Content object.",
        ):
            list(app.stream_query(user_id=_TEST_USER_ID, message=123))

    @pytest.mark.asyncio
    async def test_async_stream_query_invalid_message_type(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        with pytest.raises(
            TypeError,
            match="message must be a string or a dictionary representing a Content object.",
        ):
            async for _ in app.async_stream_query(user_id=_TEST_USER_ID, message=123):
                pass

    @pytest.mark.asyncio
    async def test_bidi_stream_query_invalid_request_queue(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        request_queue = []
        with pytest.raises(
            TypeError,
            match="request_queue must be an asyncio.Queue instance.",
        ):
            async for _ in app.bidi_stream_query(request_queue):
                pass

    @pytest.mark.asyncio
    async def test_bidi_stream_query_invalid_first_request(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name=_TEST_AGENT_NAME, model=_TEST_MODEL)
        )
        request_queue = asyncio.Queue()
        request_dict = {
            "live_request": {
                "input": "What is the exchange rate from USD to SEK?",
            },
        }
        await request_queue.put(request_dict)
        with pytest.raises(
            ValueError,
            match="The first request must have a user_id.",
        ):
            async for _ in app.bidi_stream_query(request_queue):
                pass
