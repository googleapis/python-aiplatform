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
import importlib
import json
from unittest import mock

from google import auth
import agentplatform
from google.cloud.aiplatform import initializer
from agentplatform.agent_engines.templates import (
    llama_index,
)
from agentplatform._genai.agent_engines import (
    _agent_engines_utils,
)

from llama_index.core import prompts
from llama_index.core.base.llms import types

import pytest

_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_MODEL = "gemini-1.0-pro"
_TEST_SYSTEM_INSTRUCTION = "You are a helpful bot."


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
def json_loads_mock():
    with mock.patch.object(json, "loads") as json_loads_mock:
        yield json_loads_mock


@pytest.fixture
def model_builder_mock():
    with mock.patch.object(
        llama_index,
        "_default_model_builder",
    ) as model_builder_mock:
        yield model_builder_mock


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
def llama_index_instrumentor_mock():
    with mock.patch.object(
        _agent_engines_utils,
        "_import_openinference_llama_index_or_warn",
    ) as llama_index_instrumentor_mock:
        yield llama_index_instrumentor_mock


@pytest.fixture
def llama_index_instrumentor_none_mock():
    with mock.patch.object(
        _agent_engines_utils,
        "_import_openinference_llama_index_or_warn",
    ) as llama_index_instrumentor_mock:
        llama_index_instrumentor_mock.return_value = None
        yield llama_index_instrumentor_mock


@pytest.fixture
def nest_asyncio_apply_mock():
    with mock.patch.object(
        _agent_engines_utils,
        "_import_nest_asyncio_or_warn",
    ) as nest_asyncio_apply_mock:
        yield nest_asyncio_apply_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestLlamaIndexQueryPipelineAgent:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(agentplatform)
        agentplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        self.prompt = prompts.ChatPromptTemplate(
            message_templates=[
                types.ChatMessage(
                    role=types.MessageRole.SYSTEM,
                    content=_TEST_SYSTEM_INSTRUCTION,
                ),
                types.ChatMessage(
                    role=types.MessageRole.USER,
                    content="{input}",
                ),
            ],
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_initialization(self):
        agent = llama_index.LlamaIndexQueryPipelineAgent(model=_TEST_MODEL)
        assert agent._model_name == _TEST_MODEL
        assert agent._project == _TEST_PROJECT
        assert agent._location == _TEST_LOCATION
        assert agent._runnable is None

    def test_set_up(self):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            model_builder=lambda **kwargs: kwargs,
            runnable_builder=lambda **kwargs: kwargs,
        )
        assert agent._runnable is None
        agent.set_up()
        assert agent._runnable is not None

    def test_clone(self):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            model_builder=lambda **kwargs: kwargs,
            runnable_builder=lambda **kwargs: kwargs,
        )
        agent.set_up()
        assert agent._runnable is not None
        agent_clone = agent.clone()
        assert agent._runnable is not None
        assert agent_clone._runnable is None
        agent_clone.set_up()
        assert agent_clone._runnable is not None

    def test_query(self, json_loads_mock):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
        )
        agent._runnable = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._runnable, attribute="run")
        agent.query(input="test query")
        mocks.assert_has_calls([mock.call.run.run(input="test query")])

    def test_query_with_kwargs(self, json_loads_mock):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
        )
        agent._runnable = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._runnable, attribute="run")
        agent.query(input="test query", test_arg=123)
        mocks.assert_has_calls([mock.call.run.run(input="test query", test_arg=123)])

    def test_query_with_kwargs_and_input_dict(self, json_loads_mock):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
        )
        agent._runnable = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._runnable, attribute="run")
        agent.query(input={"input": "test query"})
        mocks.assert_has_calls([mock.call.run.run(input="test query")])

    def test_query_with_batch_input(self, json_loads_mock, nest_asyncio_apply_mock):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
        )
        agent._runnable = mock.Mock()
        mocks = mock.Mock()
        mocks.attach_mock(mock=agent._runnable, attribute="run")
        agent.query(input={"input": ["test query 1", "test query 2"]}, batch=True)
        mocks.assert_has_calls(
            [mock.call.run.run(input=["test query 1", "test query 2"], batch=True)]
        )
        nest_asyncio_apply_mock.assert_called_once()

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing(
        self,
        caplog,
        tracer_provider_mock,
        simple_span_processor_mock,
        llama_index_instrumentor_mock,
    ):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            enable_tracing=True,
        )
        assert agent._instrumentor is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
        # agent.set_up()
        # assert agent._instrumentor is not None
        # assert (
        #     "enable_tracing=True but proceeding with tracing disabled"
        #     not in caplog.text
        # )

    @pytest.mark.usefixtures("caplog")
    def test_enable_tracing_warning(self, caplog, llama_index_instrumentor_none_mock):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            enable_tracing=True,
        )
        assert agent._instrumentor is None
        # TODO(b/384730642): Re-enable this test once the parent issue is fixed.
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
        llama_index_instrumentor_mock,
    ):
        agent = llama_index.LlamaIndexQueryPipelineAgent(
            model=_TEST_MODEL,
            prompt=self.prompt,
            model_builder=lambda **kwargs: kwargs,
            runnable_builder=lambda **kwargs: kwargs,
            enable_tracing=True,
        )
        assert agent._instrumentor is None

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
        llama_index_instrumentor_class = (
            llama_index_instrumentor_mock.return_value.LlamaIndexInstrumentor
        )
        llama_index_instrumentor_class.assert_called_once_with()
        llama_index_instrumentor_class.return_value.uninstrument.assert_called_once_with()
        llama_index_instrumentor_class.return_value.instrument.assert_called_once_with()
        assert agent._instrumentor is llama_index_instrumentor_class.return_value


class TestToJsonSerializableLlamaIndexObject:
    """Tests for `_utils.to_json_serializable_llama_index_object`."""

    def test_llama_index_response(self):
        mock_response: _agent_engines_utils.LlamaIndexResponse = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexResponse
        )
        mock_response.response = "test response"
        mock_response.source_nodes = [
            mock.Mock(
                spec=_agent_engines_utils.LlamaIndexBaseModel,
                model_dump_json=lambda: '{"name": "model1"}',
            ),
            mock.Mock(
                spec=_agent_engines_utils.LlamaIndexBaseModel,
                model_dump_json=lambda: '{"name": "model2"}',
            ),
        ]
        mock_response.metadata = {"key": "value"}

        want = {
            "response": "test response",
            "source_nodes": ['{"name": "model1"}', '{"name": "model2"}'],
            "metadata": {"key": "value"},
        }
        got = _agent_engines_utils.to_json_serializable_llama_index_object(
            mock_response
        )
        assert got == want

    def test_llama_index_chat_response(self):
        mock_chat_response: _agent_engines_utils.LlamaIndexChatResponse = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexChatResponse
        )
        mock_chat_response.message = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexBaseModel,
            model_dump_json=lambda: '{"content": "chat message"}',
        )

        want = {"content": "chat message"}
        got = _agent_engines_utils.to_json_serializable_llama_index_object(
            mock_chat_response
        )
        assert got == want

    def test_llama_index_base_model(self):
        mock_base_model: _agent_engines_utils.LlamaIndexBaseModel = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexBaseModel
        )
        mock_base_model.model_dump_json = lambda: '{"name": "test_model"}'

        want = {"name": "test_model"}
        got = _agent_engines_utils.to_json_serializable_llama_index_object(
            mock_base_model
        )
        assert got == want

    def test_sequence_of_llama_index_base_model(self):
        mock_base_model1: _agent_engines_utils.LlamaIndexBaseModel = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexBaseModel
        )
        mock_base_model1.model_dump_json = lambda: '{"name": "test_model1"}'
        mock_base_model2: _agent_engines_utils.LlamaIndexBaseModel = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexBaseModel
        )
        mock_base_model2.model_dump_json = lambda: '{"name": "test_model2"}'
        mock_base_model_list = [mock_base_model1, mock_base_model2]

        want = [{"name": "test_model1"}, {"name": "test_model2"}]
        got = _agent_engines_utils.to_json_serializable_llama_index_object(
            mock_base_model_list
        )
        assert got == want

    def test_sequence_of_mixed_types(self):
        mock_base_model: _agent_engines_utils.LlamaIndexBaseModel = mock.Mock(
            spec=_agent_engines_utils.LlamaIndexBaseModel
        )
        mock_base_model.model_dump_json = lambda: '{"name": "test_model"}'
        mock_string = "test_string"
        mock_list = [mock_base_model, mock_string]

        want = [{"name": "test_model"}, "test_string"]
        got = _agent_engines_utils.to_json_serializable_llama_index_object(mock_list)
        assert got == want

    def test_other_type(self):
        test_dict = {"name": "test_model"}
        want = "{'name': 'test_model'}"
        got = _agent_engines_utils.to_json_serializable_llama_index_object(test_dict)
        assert got == want
