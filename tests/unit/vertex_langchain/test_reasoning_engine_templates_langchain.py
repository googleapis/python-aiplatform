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
from typing import Optional
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import vertexai
from google.cloud.aiplatform import initializer
from vertexai.preview import reasoning_engines
import pytest


from langchain_core import agents
from langchain_core import messages
from langchain_core import outputs
from langchain_core import tools as lc_tools
from langchain.load import dump as langchain_load_dump
from langchain.tools.base import StructuredTool


_DEFAULT_PLACE_TOOL_ACTIVITY = "museums"
_DEFAULT_PLACE_TOOL_PAGE_SIZE = 3
_DEFAULT_PLACE_PHOTO_MAXWIDTH = 400
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_MODEL = "gemini-1.0-pro"


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
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.fixture
def vertexai_init_mock():
    with mock.patch.object(vertexai, "init") as vertexai_init_mock:
        yield vertexai_init_mock


@pytest.fixture
def langchain_dump_mock():
    with mock.patch.object(langchain_load_dump, "dumpd") as langchain_dump_mock:
        yield langchain_dump_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestLangchainAgent:
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
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        assert agent._model_name == _TEST_MODEL
        assert agent._project == _TEST_PROJECT
        assert agent._location == _TEST_LOCATION
        assert agent._runnable is None

    def test_initialization_with_tools(self):
        agent = reasoning_engines.LangchainAgent(
            model=_TEST_MODEL,
            tools=[
                place_tool_query,
                StructuredTool.from_function(place_photo_query),
            ],
        )
        for tool in agent._tools:
            assert isinstance(tool, lc_tools.BaseTool)

    def test_set_up(self, vertexai_init_mock):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        assert agent._runnable is None
        agent.set_up()
        assert agent._runnable is not None

    def test_query(self, langchain_dump_mock):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        agent._runnable = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._runnable, attribute="invoke")
        agent.query(input="test query")
        mocks.assert_has_calls(
            [mock.call.invoke.invoke(input={"input": "test query"}, config=None)]
        )


class TestDefaultOutputParser:
    def test_parse_result_function_call(self, vertexai_init_mock):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        agent.set_up()
        tool_input = {
            "photo_reference": "abcd1234",
            "maxwidth": _DEFAULT_PLACE_PHOTO_MAXWIDTH,
        }
        result = agent._output_parser.parse_result(
            [
                outputs.ChatGeneration(
                    message=messages.AIMessage(
                        content="",
                        additional_kwargs={
                            "function_call": {
                                "name": "place_tool_query",
                                "arguments": json.dumps(tool_input),
                            },
                        },
                    )
                )
            ]
        )
        assert isinstance(result, agents.AgentActionMessageLog)
        assert result.tool == "place_tool_query"
        assert result.tool_input == tool_input

    def test_parse_result_not_function_call(self, vertexai_init_mock):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        agent.set_up()
        content = "test content"
        result = agent._output_parser.parse_result(
            [
                outputs.ChatGeneration(
                    message=messages.AIMessage(content=content),
                )
            ]
        )
        assert isinstance(result, agents.AgentFinish)
        assert result.return_values == {"output": content}
        assert result.log == content


class TestDefaultOutputParserErrors:
    def test_parse_result_non_chat_generation_errors(self, vertexai_init_mock):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        agent.set_up()
        with pytest.raises(ValueError, match=r"only works on ChatGeneration"):
            agent._output_parser.parse_result(["text"])

    def test_parse_text_errors(self, vertexai_init_mock):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        agent.set_up()
        with pytest.raises(ValueError, match=r"Can only parse messages"):
            agent._output_parser.parse("text")


class TestConvertToolsOrRaise:
    def test_convert_tools_or_raise(self, vertexai_init_mock):
        pass


def _return_input_no_typing(input_):
    """Returns input back to user."""
    return input_


class TestConvertToolsOrRaiseErrors:
    def test_raise_untyped_input_args(self, vertexai_init_mock):
        with pytest.raises(TypeError, match=r"has untyped input_arg"):
            reasoning_engines.LangchainAgent(
                model=_TEST_MODEL,
                tools=[_return_input_no_typing],
            )
