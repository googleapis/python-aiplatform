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
from typing import Optional
from unittest import mock

from google import auth
from google.auth import credentials as auth_credentials
import vertexai
from google.cloud.aiplatform import initializer
from vertexai.preview import reasoning_engines
from vertexai.preview.generative_models import grounding
from vertexai.generative_models import Tool
import pytest


from langchain_core import prompts
from langchain.load import dump as langchain_load_dump
from langchain.agents.format_scratchpad import format_to_openai_function_messages
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


@pytest.fixture
def mock_chatvertexai():
    with mock.patch("langchain_google_vertexai.ChatVertexAI") as model_mock:
        yield model_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestLangchainAgent:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(vertexai)
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.prompt = {
            "input": lambda x: x["input"],
            "agent_scratchpad": (
                lambda x: format_to_openai_function_messages(x["intermediate_steps"])
            ),
        } | prompts.ChatPromptTemplate.from_messages(
            [
                ("user", "{input}"),
                prompts.MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.output_parser = mock.Mock()

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        agent = reasoning_engines.LangchainAgent(model=_TEST_MODEL)
        assert agent._model_name == _TEST_MODEL
        assert agent._project == _TEST_PROJECT
        assert agent._location == _TEST_LOCATION
        assert agent._runnable is None

    def test_initialization_with_tools(self, mock_chatvertexai):
        tools = [
            place_tool_query,
            StructuredTool.from_function(place_photo_query),
            Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval()),
        ]
        agent = reasoning_engines.LangchainAgent(
            model=_TEST_MODEL,
            tools=tools,
        )
        for tool, agent_tool in zip(tools, agent._tools):
            assert isinstance(agent_tool, type(tool))
        assert agent._runnable is None
        agent.set_up()
        assert agent._runnable is not None

    def test_set_up(self):
        agent = reasoning_engines.LangchainAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            output_parser=self.output_parser,
        )
        assert agent._runnable is None
        agent.set_up()
        assert agent._runnable is not None

    def test_clone(self):
        agent = reasoning_engines.LangchainAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            output_parser=self.output_parser,
        )
        agent.set_up()
        assert agent._runnable is not None
        agent_clone = agent.clone()
        assert agent._runnable is not None
        assert agent_clone._runnable is None
        agent_clone.set_up()
        assert agent_clone._runnable is not None

    def test_query(self, langchain_dump_mock):
        agent = reasoning_engines.LangchainAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            output_parser=self.output_parser,
        )
        agent._runnable = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._runnable, attribute="invoke")
        agent.query(input="test query")
        mocks.assert_has_calls(
            [mock.call.invoke.invoke(input={"input": "test query"}, config=None)]
        )


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
