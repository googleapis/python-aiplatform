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
from vertexai import agent_engines
from test_constants import (
    test_agent,
)

_TEST_MODULE_NAME = "test_constants"
_TEST_AGENT_NAME = "test_agent"
_TEST_REGISTER_OPERATIONS = {"": ["query"], "stream": ["stream_query"]}
_TEST_SYS_PATH = "/tmp/test_sys_path"
_TEST_QUERY_INPUT = "test query"
_TEST_STREAM_QUERY_INPUT = 5


class TestModuleAgent:
    def test_initialization(self):
        agent = agent_engines.ModuleAgent(
            module_name=_TEST_MODULE_NAME,
            agent_name=_TEST_AGENT_NAME,
            register_operations=_TEST_REGISTER_OPERATIONS,
        )
        assert agent._tmpl_attrs.get("module_name") == _TEST_MODULE_NAME
        assert agent._tmpl_attrs.get("agent_name") == _TEST_AGENT_NAME
        assert agent._tmpl_attrs.get("register_operations") == _TEST_REGISTER_OPERATIONS

    def test_set_up(self):
        import os
        import sys

        agent = agent_engines.ModuleAgent(
            module_name=_TEST_MODULE_NAME,
            agent_name=_TEST_AGENT_NAME,
            register_operations=_TEST_REGISTER_OPERATIONS,
            sys_paths=[_TEST_SYS_PATH],
        )
        assert agent._tmpl_attrs.get("agent") is None
        assert agent._tmpl_attrs.get("sys_paths") == [_TEST_SYS_PATH]
        assert os.path.abspath(_TEST_SYS_PATH) not in sys.path
        agent.set_up()
        assert agent._tmpl_attrs.get("agent") is not None
        assert os.path.abspath(_TEST_SYS_PATH) in sys.path

    def test_clone(self):
        agent = agent_engines.ModuleAgent(
            module_name=_TEST_MODULE_NAME,
            agent_name=_TEST_AGENT_NAME,
            register_operations=_TEST_REGISTER_OPERATIONS,
            sys_paths=[_TEST_SYS_PATH],
            agent_framework="my_framework",
        )
        agent.set_up()
        assert agent._tmpl_attrs.get("agent") is not None
        assert agent._tmpl_attrs.get("sys_paths") == [_TEST_SYS_PATH]
        agent_clone = agent.clone()
        assert agent._tmpl_attrs.get("agent") is not None
        assert agent_clone._tmpl_attrs.get("agent") is None
        assert agent_clone._tmpl_attrs.get("sys_paths") == [_TEST_SYS_PATH]
        assert agent_clone.agent_framework == "my_framework"
        agent_clone.set_up()
        assert agent_clone._tmpl_attrs.get("agent") is not None

    def test_query(self):
        agent = agent_engines.ModuleAgent(
            module_name=_TEST_MODULE_NAME,
            agent_name=_TEST_AGENT_NAME,
            register_operations=_TEST_REGISTER_OPERATIONS,
        )
        agent.set_up()
        got_result = agent.query(input=_TEST_QUERY_INPUT)
        expected_result = agent._tmpl_attrs.get("agent").query(input=_TEST_QUERY_INPUT)
        assert got_result == expected_result
        expected_result = test_agent.query(input=_TEST_QUERY_INPUT)
        assert got_result == expected_result

    def test_stream_query(self):
        agent = agent_engines.ModuleAgent(
            module_name=_TEST_MODULE_NAME,
            agent_name=_TEST_AGENT_NAME,
            register_operations=_TEST_REGISTER_OPERATIONS,
        )
        agent.set_up()
        for got_result, expected_result in zip(
            agent.stream_query(n=_TEST_STREAM_QUERY_INPUT),
            agent._tmpl_attrs.get("agent").stream_query(n=_TEST_STREAM_QUERY_INPUT),
        ):
            assert got_result == expected_result
        for got_result, expected_result in zip(
            agent.stream_query(n=_TEST_STREAM_QUERY_INPUT),
            test_agent.stream_query(n=_TEST_STREAM_QUERY_INPUT),
        ):
            assert got_result == expected_result
