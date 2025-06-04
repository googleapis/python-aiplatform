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
import importlib
import json
from unittest import mock

from google import auth
import vertexai
from google.cloud.aiplatform import initializer
from vertexai.agent_engines import _utils
from vertexai.preview import reasoning_engines
from google.genai import types
import pytest


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
_TEST_MODEL = "gemini-1.0-pro"


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
def cloud_trace_exporter_mock():
    with mock.patch.object(
        _utils,
        "_import_cloud_trace_exporter_or_warn",
    ) as cloud_trace_exporter_mock:
        yield cloud_trace_exporter_mock


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
def mock_adk_major_version():
    with mock.patch(
        "google.cloud.aiplatform.vertexai.preview.reasoning_engines.templates.adk.get_adk_major_version",
        return_value=1,
    ):
        yield


class _MockRunner:
    def run(self, *args, **kwargs):
        from google.adk.events import event

        yield event.Event(
            **{
                "author": "currency_exchange_agent",
                "content": {
                    "parts": [
                        {
                            "function_call": {
                                "args": {
                                    "currency_date": "2025-04-03",
                                    "currency_from": "USD",
                                    "currency_to": "SEK",
                                },
                                "id": "af-c5a57692-9177-4091-a3df-098f834ee849",
                                "name": "get_exchange_rate",
                            }
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
                            "function_call": {
                                "args": {
                                    "currency_date": "2025-04-03",
                                    "currency_from": "USD",
                                    "currency_to": "SEK",
                                },
                                "id": "af-c5a57692-9177-4091-a3df-098f834ee849",
                                "name": "get_exchange_rate",
                            }
                        }
                    ],
                    "role": "model",
                },
                "id": "9aaItGK9",
                "invocation_id": "e-6543c213-6417-484b-9551-b67915d1d5f7",
            }
        )


@pytest.mark.usefixtures("google_auth_mock", "mock_adk_major_version")
class TestAdkApp:
    def test_adk_major_version(self):
        with mock.patch(
            "google.cloud.aiplatform.vertexai.preview.reasoning_engines.templates.adk.get_adk_major_version",
            return_value=0,
        ):
            with pytest.raises(
                ValueError,
                match=(
                    "Unsupported google-adk major version: 0, please use"
                    " google-adk>=1.0.0 for AdkApp deployment."
                ),
            ):
                reasoning_engines.AdkApp(
                    agent=Agent(name="test_agent", model=_TEST_MODEL)
                )

    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(vertexai)
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL),
        )
        assert app._tmpl_attrs.get("project") == _TEST_PROJECT
        assert app._tmpl_attrs.get("location") == _TEST_LOCATION
        assert app._tmpl_attrs.get("runner") is None

    def test_set_up(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL),
        )
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        assert app._tmpl_attrs.get("runner") is not None

    def test_clone(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL),
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
            agent=Agent(name="test_agent", model=_TEST_MODEL),
        )
        for operations in app.register_operations().values():
            for operation in operations:
                assert operation in dir(app)

    def test_stream_query(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = list(
            app.stream_query(
                user_id="test_user_id",
                message="test message",
            )
        )
        assert len(events) == 1

    def test_stream_query_with_content(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = list(
            app.stream_query(
                user_id="test_user_id",
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
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = []
        async for event in app.async_stream_query(
            user_id="test_user_id",
            message="test message",
        ):
            events.append(event)
        assert len(events) == 1

    @pytest.mark.asyncio
    async def test_async_stream_query_with_content(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        assert app._tmpl_attrs.get("runner") is None
        app.set_up()
        app._tmpl_attrs["runner"] = _MockRunner()
        events = []
        async for event in app.async_stream_query(
            user_id="test_user_id",
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
            agent=Agent(name="test_agent", model=_TEST_MODEL)
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
                "user_id": "test_user_id",
                "message": {
                    "parts": [{"text": "What is the exchange rate from USD to SEK?"}],
                    "role": "user",
                },
            }
        )
        events = list(app.streaming_agent_run_with_events(request_json=request_json))
        assert len(events) == 1

    def test_create_session(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        session1 = app.create_session(user_id="test_user_id")
        assert session1.user_id == "test_user_id"
        session2 = app.create_session(
            user_id="test_user_id", session_id="test_session_id"
        )
        assert session2.user_id == "test_user_id"
        assert session2.id == "test_session_id"

    def test_get_session(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        session1 = app.create_session(user_id="test_user_id")
        session2 = app.get_session(
            user_id="test_user_id",
            session_id=session1.id,
        )
        assert session2.user_id == "test_user_id"
        assert session1.id == session2.id

    def test_list_sessions(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        response0 = app.list_sessions(user_id="test_user_id")
        assert not response0.sessions
        session = app.create_session(user_id="test_user_id")
        response1 = app.list_sessions(user_id="test_user_id")
        assert len(response1.sessions) == 1
        assert response1.sessions[0].id == session.id
        session2 = app.create_session(user_id="test_user_id")
        response2 = app.list_sessions(user_id="test_user_id")
        assert len(response2.sessions) == 2
        assert response2.sessions[0].id == session.id
        assert response2.sessions[1].id == session2.id

    def test_delete_session(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        response = app.delete_session(user_id="test_user_id", session_id="")
        assert not response
        session = app.create_session(user_id="test_user_id")
        response1 = app.list_sessions(user_id="test_user_id")
        assert len(response1.sessions) == 1
        app.delete_session(user_id="test_user_id", session_id=session.id)
        response0 = app.list_sessions(user_id="test_user_id")
        assert not response0.sessions

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing(
        self,
        caplog,
        cloud_trace_exporter_mock,
        tracer_provider_mock,
        simple_span_processor_mock,
    ):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL),
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
            agent=Agent(name="test_agent", model=_TEST_MODEL),
            enable_tracing=True,
        )
        assert app._tmpl_attrs.get("instrumentor") is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # app.set_up()
        # assert "enable_tracing=True but proceeding with tracing disabled" in caplog.text


@pytest.mark.usefixtures("mock_adk_major_version")
class TestAdkAppErrors:
    def test_raise_get_session_not_found_error(self):
        with pytest.raises(
            RuntimeError,
            match=r"Session not found. Please create it using .create_session()",
        ):
            app = reasoning_engines.AdkApp(
                agent=Agent(name="test_agent", model=_TEST_MODEL),
            )
            app.get_session(
                user_id="non_existent_user",
                session_id="test_session_id",
            )

    def test_stream_query_invalid_message_type(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        with pytest.raises(
            TypeError,
            match="message must be a string or a dictionary representing a Content object.",
        ):
            list(app.stream_query(user_id="test_user_id", message=123))

    @pytest.mark.asyncio
    async def test_async_stream_query_invalid_message_type(self):
        app = reasoning_engines.AdkApp(
            agent=Agent(name="test_agent", model=_TEST_MODEL)
        )
        with pytest.raises(
            TypeError,
            match="message must be a string or a dictionary representing a Content object.",
        ):
            async for _ in app.async_stream_query(user_id="test_user_id", message=123):
                pass
