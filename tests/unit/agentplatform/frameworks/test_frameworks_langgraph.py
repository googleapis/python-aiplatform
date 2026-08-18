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
from typing import Any, Dict, List, Optional
from unittest import mock

from google import auth
import agentplatform
from google.cloud.aiplatform import initializer
from agentplatform import agent_engines
from agentplatform._genai import _agent_engines_utils
import pytest

from langchain_core import runnables
from langchain_core.load import dump as langchain_load_dump
from langchain_core.tools import StructuredTool


_DEFAULT_PLACE_TOOL_ACTIVITY = "museums"
_DEFAULT_PLACE_TOOL_PAGE_SIZE = 3
_DEFAULT_PLACE_PHOTO_MAXWIDTH = 400
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_MODEL = "gemini-1.0-pro"
_TEST_CONFIG = runnables.RunnableConfig(configurable={"thread_id": "thread-values"})


def place_tool_query(
    city: str,
    activity: str = _DEFAULT_PLACE_TOOL_ACTIVITY,
    page_size: int = _DEFAULT_PLACE_TOOL_PAGE_SIZE,
):
    """Searches the city for recommendations on the activity."""
    return {"city": city, "activity": activity, "page_size": page_size}


def place_photo_query(
    photo_reference: str,
    maxwidth: int = _DEFAULT_PLACE_PHOTO_MAXWIDTH,
    maxheight: Optional[int] = None,
):
    """Returns the photo for a given reference."""
    result = {"photo_reference": photo_reference, "maxwidth": maxwidth}
    if maxheight:
        result["maxheight"] = maxheight
    return result


def _checkpointer_builder(**unused_kwargs):
    try:
        from langgraph.checkpoint import memory
    except ImportError:
        from langgraph_checkpoint.checkpoint import memory

    return memory.MemorySaver()


def _get_state_messages(state: Dict[str, Any]) -> List[str]:
    messages = []
    for message in state.get("values").get("messages"):
        messages.append(message.content)
    return messages


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
def agentplatform_init_mock():
    with mock.patch.object(agentplatform, "init") as agentplatform_init_mock:
        yield agentplatform_init_mock


@pytest.fixture
def langchain_dump_mock():
    with mock.patch.object(langchain_load_dump, "dumpd") as langchain_dump_mock:
        yield langchain_dump_mock


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
    import opentelemetry.exporter.otlp.proto.http.trace_exporter

    with mock.patch.object(
        opentelemetry.exporter.otlp.proto.http.trace_exporter,
        "OTLPSpanExporter",
    ) as otlp_span_exporter_mock:
        yield otlp_span_exporter_mock


@pytest.fixture
def resource_create_mock():
    import opentelemetry.sdk.resources

    with mock.patch.object(
        opentelemetry.sdk.resources.Resource, "create"
    ) as resource_create_mock:
        yield resource_create_mock


@pytest.fixture
def otel_resource_detector_mock():
    import opentelemetry.sdk.resources

    with mock.patch.object(
        opentelemetry.sdk.resources, "OTELResourceDetector"
    ) as otel_resource_detector_mock:
        yield otel_resource_detector_mock


@pytest.fixture
def is_noop_or_proxy_tracer_provider_mock():
    with mock.patch.object(
        _agent_engines_utils, "is_noop_or_proxy_tracer_provider"
    ) as is_noop_or_proxy_tracer_provider_mock:
        is_noop_or_proxy_tracer_provider_mock.return_value = True
        yield is_noop_or_proxy_tracer_provider_mock


@pytest.fixture
def langchain_instrumentor_mock():
    with mock.patch.object(
        _agent_engines_utils,
        "_import_openinference_langchain_or_warn",
    ) as langchain_instrumentor_mock:
        yield langchain_instrumentor_mock


@pytest.fixture
def langchain_instrumentor_none_mock():
    with mock.patch.object(
        _agent_engines_utils,
        "_import_openinference_langchain_or_warn",
    ) as langchain_instrumentor_mock:
        langchain_instrumentor_mock.return_value = None
        yield langchain_instrumentor_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestLanggraphAgent:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(agentplatform)
        agentplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        assert agent._tmpl_attrs.get("model_name") == _TEST_MODEL
        assert agent._tmpl_attrs.get("project") == _TEST_PROJECT
        assert agent._tmpl_attrs.get("location") == _TEST_LOCATION
        assert agent._tmpl_attrs.get("runnable") is None

    def test_initialization_with_tools(self):
        tools = [
            place_tool_query,
            StructuredTool.from_function(place_photo_query),
        ]
        agent = agent_engines.LanggraphAgent(
            model=_TEST_MODEL,
            tools=tools,
            model_builder=lambda **kwargs: kwargs,
            runnable_builder=lambda **kwargs: kwargs,
        )
        for tool, agent_tool in zip(tools, agent._tmpl_attrs.get("tools")):
            assert isinstance(agent_tool, type(tool))
        assert agent._tmpl_attrs.get("runnable") is None
        agent.set_up()
        assert agent._tmpl_attrs.get("runnable") is not None

    def test_set_up(self):
        agent = agent_engines.LanggraphAgent(
            model=_TEST_MODEL,
            model_builder=lambda **kwargs: kwargs,
            runnable_builder=lambda **kwargs: kwargs,
        )
        assert agent._tmpl_attrs.get("runnable") is None
        agent.set_up()
        assert agent._tmpl_attrs.get("runnable") is not None

    def test_clone(self):
        agent = agent_engines.LanggraphAgent(
            model=_TEST_MODEL,
            model_builder=lambda **kwargs: kwargs,
            runnable_builder=lambda **kwargs: kwargs,
        )
        agent.set_up()
        assert agent._tmpl_attrs.get("runnable") is not None
        agent_clone = agent.clone()
        assert agent._tmpl_attrs.get("runnable") is not None
        assert agent_clone._tmpl_attrs.get("runnable") is None
        agent_clone.set_up()
        assert agent_clone._tmpl_attrs.get("runnable") is not None

    def test_query(self, langchain_dump_mock):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._tmpl_attrs.get("runnable"), attribute="invoke")
        agent.query(input="test query")
        mocks.assert_has_calls(
            [
                mock.call.invoke.invoke(
                    input={"input": "test query", "messages": [("user", "test query")]},
                    config=None,
                )
            ]
        )

    def test_stream_query(self, langchain_dump_mock):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent._tmpl_attrs["runnable"].stream.return_value = []
        list(agent.stream_query(input="test stream query"))
        agent._tmpl_attrs["runnable"].stream.assert_called_once_with(
            input={
                "input": "test stream query",
                "messages": [("user", "test stream query")],
            },
            config=None,
        )

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing(
        self,
        caplog,
        tracer_provider_mock,
        simple_span_processor_mock,
        langchain_instrumentor_mock,
    ):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL, enable_tracing=True)
        assert agent._tmpl_attrs.get("instrumentor") is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # agent.set_up()
        # assert agent._instrumentor is not None
        # assert (
        #     "enable_tracing=True but proceeding with tracing disabled"
        #     not in caplog.text
        # )

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing_warning(self, caplog, langchain_instrumentor_none_mock):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL, enable_tracing=True)
        assert agent._tmpl_attrs.get("instrumentor") is None
        # TODO(b/383923584): Re-enable this test once the parent issue is fixed.
        # agent.set_up()
        # assert "enable_tracing=True but proceeding with tracing disabled" in caplog.text

    def test_tracing_setup(
        self,
        tracer_provider_mock,
        simple_span_processor_mock,
        otlp_span_exporter_mock,
        resource_create_mock,
        otel_resource_detector_mock,
        is_noop_or_proxy_tracer_provider_mock,
        langchain_instrumentor_mock,
    ):
        agent = agent_engines.LanggraphAgent(
            model=_TEST_MODEL,
            runnable_builder=lambda **kwargs: kwargs,
            enable_tracing=True,
        )
        assert agent._tmpl_attrs.get("instrumentor") is None

        agent.set_up()

        otlp_span_exporter_mock.assert_called_once_with(
            session=mock.ANY,
            endpoint="https://telemetry.googleapis.com/v1/traces",
        )
        resource_create_mock.assert_called_with(
            attributes={"gcp.project_id": _TEST_PROJECT},
        )
        tracer_provider_mock.assert_called_with(
            resource=resource_create_mock.return_value.merge.return_value,
        )
        simple_span_processor_mock.assert_called_once_with(
            span_exporter=otlp_span_exporter_mock.return_value,
        )
        tracer_provider_mock.return_value.add_span_processor.assert_called_once_with(
            simple_span_processor_mock.return_value,
        )
        langchain_instrumentor_class = (
            langchain_instrumentor_mock.return_value.LangChainInstrumentor
        )
        langchain_instrumentor_class.assert_called_once_with()
        langchain_instrumentor_class.return_value.uninstrument.assert_called_once_with()
        langchain_instrumentor_class.return_value.instrument.assert_called_once_with()
        assert (
            agent._tmpl_attrs.get("instrumentor")
            is langchain_instrumentor_class.return_value
        )

    def test_get_state_history_empty(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state_history.return_value = []
        history = list(agent.get_state_history())
        assert history == []

    def test_get_state_history(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state_history.return_value = [
            mock.Mock(),
            mock.Mock(),
        ]
        agent._tmpl_attrs["runnable"].get_state_history.return_value[
            0
        ]._asdict.return_value = {"test_key_1": "test_value_1"}
        agent._tmpl_attrs["runnable"].get_state_history.return_value[
            1
        ]._asdict.return_value = {"test_key_2": "test_value_2"}
        history = list(agent.get_state_history())
        assert history == [
            {"test_key_1": "test_value_1"},
            {"test_key_2": "test_value_2"},
        ]

    def test_get_state_history_with_config(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state_history.return_value = [
            mock.Mock(),
            mock.Mock(),
        ]
        agent._tmpl_attrs["runnable"].get_state_history.return_value[
            0
        ]._asdict.return_value = {"test_key_1": "test_value_1"}
        agent._tmpl_attrs["runnable"].get_state_history.return_value[
            1
        ]._asdict.return_value = {"test_key_2": "test_value_2"}
        history = list(agent.get_state_history(config=_TEST_CONFIG))
        assert history == [
            {"test_key_1": "test_value_1"},
            {"test_key_2": "test_value_2"},
        ]

    def test_get_state(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state.return_value = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state.return_value._asdict.return_value = {
            "test_key": "test_value"
        }
        state = agent.get_state()
        assert state == {"test_key": "test_value"}

    def test_get_state_with_config(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state.return_value = mock.Mock()
        agent._tmpl_attrs["runnable"].get_state.return_value._asdict.return_value = {
            "test_key": "test_value"
        }
        state = agent.get_state(config=_TEST_CONFIG)
        assert state == {"test_key": "test_value"}

    def test_update_state(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent.update_state()
        agent._tmpl_attrs["runnable"].update_state.assert_called_once()

    def test_update_state_with_config(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent.update_state(config=_TEST_CONFIG)
        agent._tmpl_attrs["runnable"].update_state.assert_called_once_with(
            config=_TEST_CONFIG
        )

    def test_update_state_with_config_and_kwargs(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        agent._tmpl_attrs["runnable"] = mock.Mock()
        agent.update_state(config=_TEST_CONFIG, test_key="test_value")
        agent._tmpl_attrs["runnable"].update_state.assert_called_once_with(
            config=_TEST_CONFIG, test_key="test_value"
        )

    def test_register_operations(self):
        agent = agent_engines.LanggraphAgent(model=_TEST_MODEL)
        expected_operations = {
            "": ["query", "get_state", "update_state"],
            "stream": ["stream_query", "get_state_history"],
        }
        assert agent.register_operations() == expected_operations


def _return_input_no_typing(input_):
    """Returns input back to user."""
    return input_


class TestConvertToolsOrRaiseErrors:
    def test_raise_untyped_input_args(self, agentplatform_init_mock):
        with pytest.raises(TypeError, match=r"has untyped input_arg"):
            agent_engines.LanggraphAgent(
                model=_TEST_MODEL, tools=[_return_input_no_typing]
            )
