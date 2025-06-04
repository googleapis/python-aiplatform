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
import dataclasses
import importlib
import json
from typing import Optional
from unittest import mock

from google import auth
import vertexai
from google.cloud.aiplatform import initializer
from vertexai import agent_engines
from vertexai.agent_engines import _utils
import pytest


_DEFAULT_PLACE_TOOL_ACTIVITY = "museums"
_DEFAULT_PLACE_TOOL_PAGE_SIZE = 3
_DEFAULT_PLACE_PHOTO_MAXWIDTH = 400
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_MODEL = "gemini-1.0-pro"
_TEST_RUNNABLE_NAME = "test-runnable"
_TEST_SYSTEM_INSTRUCTION = "You are a helpful bot."


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
def dataclasses_asdict_mock():
    with mock.patch.object(dataclasses, "asdict") as dataclasses_asdict_mock:
        dataclasses_asdict_mock.return_value = {}
        yield dataclasses_asdict_mock


@pytest.fixture
def dataclasses_is_dataclass_mock():
    with mock.patch.object(
        dataclasses, "is_dataclass"
    ) as dataclasses_is_dataclass_mock:
        dataclasses_is_dataclass_mock.return_value = True
        yield dataclasses_is_dataclass_mock


@pytest.fixture
def to_json_serializable_autogen_object_mock():
    with mock.patch.object(
        _utils,
        "to_json_serializable_autogen_object",
    ) as to_json_serializable_autogen_object_mock:
        to_json_serializable_autogen_object_mock.return_value = {}
        yield to_json_serializable_autogen_object_mock


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
def autogen_instrumentor_mock():
    with mock.patch.object(
        _utils,
        "_import_openinference_autogen_or_warn",
    ) as autogen_instrumentor_mock:
        yield autogen_instrumentor_mock


@pytest.fixture
def autogen_instrumentor_none_mock():
    with mock.patch.object(
        _utils,
        "_import_openinference_autogen_or_warn",
    ) as autogen_instrumentor_mock:
        autogen_instrumentor_mock.return_value = None
        yield autogen_instrumentor_mock


@pytest.fixture
def autogen_tools_mock():
    with mock.patch.object(
        _utils,
        "_import_autogen_tools_or_warn",
    ) as autogen_tools_mock:
        autogen_tools_mock.return_value = mock.MagicMock()
        yield autogen_tools_mock


class MockAgent:
    def __init__(self, name=None, description=None):
        self.name = name
        self.description = description


class MockCost:
    def __init__(self, total_cost=0.0):
        self.total_cost = total_cost

    def model_dump_json(self):
        return json.dumps({"total_cost": self.total_cost})


@pytest.mark.usefixtures("google_auth_mock")
class TestAG2Agent:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL, runnable_name=_TEST_RUNNABLE_NAME
        )
        assert agent._tmpl_attrs.get("model_name") == _TEST_MODEL
        assert agent._tmpl_attrs.get("runnable_name") == _TEST_RUNNABLE_NAME
        assert agent._tmpl_attrs.get("project") == _TEST_PROJECT
        assert agent._tmpl_attrs.get("location") == _TEST_LOCATION
        assert agent._tmpl_attrs.get("runnable") is None

    def test_initialization_with_tools(self, autogen_tools_mock):
        tools = [
            place_tool_query,
            place_photo_query,
        ]
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL,
            runnable_name=_TEST_RUNNABLE_NAME,
            system_instruction=_TEST_SYSTEM_INSTRUCTION,
            tools=tools,
            runnable_builder=lambda **kwargs: kwargs,
        )
        assert agent._tmpl_attrs.get("runnable") is None
        assert agent._tmpl_attrs.get("tools")
        assert not agent._tmpl_attrs.get("ag2_tool_objects")
        agent.set_up()
        assert agent._tmpl_attrs.get("runnable") is not None
        assert agent._tmpl_attrs.get("ag2_tool_objects")

    def test_set_up(self):
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL,
            runnable_name=_TEST_RUNNABLE_NAME,
            runnable_builder=lambda **kwargs: kwargs,
        )
        assert agent._tmpl_attrs.get("runnable") is None
        agent.set_up()
        assert agent._tmpl_attrs.get("runnable") is not None

    def test_clone(self):
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL,
            runnable_name=_TEST_RUNNABLE_NAME,
            runnable_builder=lambda **kwargs: kwargs,
        )
        agent.set_up()
        assert agent._tmpl_attrs.get("runnable") is not None
        agent_clone = agent.clone()
        assert agent._tmpl_attrs.get("runnable") is not None
        assert agent_clone._tmpl_attrs.get("runnable") is None
        agent_clone.set_up()
        assert agent_clone._tmpl_attrs.get("runnable") is not None

    def test_query(self, to_json_serializable_autogen_object_mock):
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL,
            runnable_name=_TEST_RUNNABLE_NAME,
        )
        agent._tmpl_attrs["runnable"] = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._tmpl_attrs["runnable"], attribute="run")
        agent.query(input="test query")
        mocks.assert_has_calls(
            [
                mock.call.run.run(
                    message={"content": "test query"},
                    user_input=False,
                    tools=[],
                    max_turns=None,
                )
            ]
        )

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing(
        self,
        caplog,
        cloud_trace_exporter_mock,
        tracer_provider_mock,
        simple_span_processor_mock,
        autogen_instrumentor_mock,
    ):
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL,
            runnable_name=_TEST_RUNNABLE_NAME,
            enable_tracing=True,
        )
        assert agent._tmpl_attrs.get("instrumentor") is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # agent.set_up()
        # assert agent._tmpl_attrs.get("instrumentor") is not None
        # assert "enable_tracing=True but proceeding with tracing disabled" in caplog.text

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing_warning(self, caplog, autogen_instrumentor_none_mock):
        agent = agent_engines.AG2Agent(
            model=_TEST_MODEL,
            runnable_name=_TEST_RUNNABLE_NAME,
            enable_tracing=True,
        )
        assert agent._tmpl_attrs.get("instrumentor") is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # agent.set_up()
        # assert "enable_tracing=True but proceeding with tracing disabled" in caplog.text


def _return_input_no_typing(input_):
    """Returns input back to user."""
    return input_


class TestConvertToolsOrRaiseErrors:
    def test_raise_untyped_input_args(self, vertexai_init_mock):
        with pytest.raises(TypeError, match=r"has untyped input_arg"):
            agent_engines.AG2Agent(
                model=_TEST_MODEL,
                runnable_name=_TEST_RUNNABLE_NAME,
                tools=[_return_input_no_typing],
            )


class TestToJsonSerializableAutoGenObject:
    """Tests for `_utils.to_json_serializable_autogen_object`."""

    def test_autogen_chat_result(
        self,
        dataclasses_asdict_mock,
        dataclasses_is_dataclass_mock,
    ):
        mock_chat_result: _utils.AutogenChatResult = mock.Mock(
            spec=_utils.AutogenChatResult
        )
        _utils.to_json_serializable_autogen_object(mock_chat_result)
        dataclasses_is_dataclass_mock.assert_called_once_with(mock_chat_result)
        dataclasses_asdict_mock.assert_called_once_with(mock_chat_result)

    def test_autogen_run_response(self):
        mock_response: _utils.AutogenRunResponse = mock.Mock(
            spec=_utils.AutogenRunResponse
        )
        mock_agent = MockAgent(
            name="TestAgent",
            description="Agent Description",
        )
        mock_cost = MockCost(total_cost=5.5)
        mock_response.summary = "summary"
        mock_response.messages = [{"role": "user", "content": "Hello"}]
        mock_response.context_variables = {"var1": "value1"}
        mock_response.last_speaker = mock_agent
        mock_response.cost = mock_cost
        mock_response.process = mock.MagicMock()

        want = {
            "summary": "summary",
            "messages": [{"role": "user", "content": "Hello"}],
            "context_variables": {"var1": "value1"},
            "last_speaker": {
                "name": "TestAgent",
                "description": "Agent Description",
            },
            "cost": {"total_cost": 5.5},
        }
        got = _utils.to_json_serializable_autogen_object(mock_response)
        mock_response.process.assert_called_once()
        assert got == want

    def test_autogen_empty_run_response(self):
        mock_response: _utils.AutogenRunResponse = mock.Mock(
            spec=_utils.AutogenRunResponse
        )
        want = {
            "summary": None,
            "messages": [],
            "context_variables": None,
            "last_speaker": None,
            "cost": None,
        }
        got = _utils.to_json_serializable_autogen_object(mock_response)
        assert got == want


class TestDataClassToJsonSerializable:
    """Tests for `_utils._dataclass_to_dict_or_raise`."""

    def test_valid_dataclass(self):
        @dataclasses.dataclass
        class SimpleDataClass:
            field1: str
            field2: int

        instance = SimpleDataClass(field1="value1", field2=123)
        want = {"field1": "value1", "field2": 123}
        got = _utils._dataclass_to_dict_or_raise(instance)
        assert got == want

    def test_not_a_dataclass_raises_type_error(self):
        class NotADataclass:
            pass

        instance = NotADataclass()
        with pytest.raises(TypeError, match="Object is not a dataclass"):
            _utils._dataclass_to_dict_or_raise(instance)
