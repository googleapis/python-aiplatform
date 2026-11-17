# Copyright 2026 Google LLC
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
import os
import sys
import tempfile
from unittest import mock
import pytest
import cloudpickle
import pydantic

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform import base

from google.cloud.aiplatform_v1 import types
from google.cloud.aiplatform_v1.services import reasoning_engine_service
from vertexai import agent_engines
from vertexai.agent_engines import _agent_engines
from vertexai.agent_engines import _utils
from google.protobuf import struct_pb2


class CapitalizeEngine:
    """A sample Agent Engine."""

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()


class CapitalizeEngineWithCard(CapitalizeEngine):

    def __init__(self, card):
        self.agent_card = card

    def __getstate__(self):
        state = self.__dict__.copy()
        if hasattr(self.agent_card, "DESCRIPTOR"):
            state["agent_card"] = None
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)


class DummyPydanticCard(pydantic.BaseModel):
    name: str = "test_pydantic_card"


def _create_empty_fake_package(package_name: str) -> str:
    temp_dir = tempfile.mkdtemp()
    package_dir = os.path.join(temp_dir, package_name)
    os.makedirs(package_dir)
    init_path = os.path.join(package_dir, "__init__.py")
    open(init_path, "w").close()
    return temp_dir


_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_STAGING_BUCKET = "gs://test-bucket"
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_AGENT_ENGINE_DISPLAY_NAME = "Agent Engine Display Name"
_TEST_GCS_DIR_NAME = _agent_engines._DEFAULT_GCS_DIR_NAME
_TEST_BLOB_FILENAME = _agent_engines._BLOB_FILENAME
_TEST_REQUIREMENTS_FILE = _agent_engines._REQUIREMENTS_FILE
_TEST_EXTRA_PACKAGES_FILE = _agent_engines._EXTRA_PACKAGES_FILE
_TEST_STANDARD_API_MODE = _agent_engines._STANDARD_API_MODE
_TEST_DEFAULT_METHOD_NAME = _agent_engines._DEFAULT_METHOD_NAME
_TEST_MODE_KEY_IN_SCHEMA = _agent_engines._MODE_KEY_IN_SCHEMA

_TEST_AGENT_ENGINE_EXTRA_PACKAGE = "fake.py"

_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH = _create_empty_fake_package(
    _TEST_AGENT_ENGINE_EXTRA_PACKAGE
)

_TEST_AGENT_ENGINE_REQUIREMENTS = [
    "google-cloud-aiplatform==1.29.0",
    "langchain",
]

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

_TEST_AGENT_ENGINE_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        CapitalizeEngine().query,
        schema_name=_TEST_DEFAULT_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STANDARD_API_MODE

_TEST_AGENT_ENGINE_PACKAGE_SPEC = types.ReasoningEngineSpec.PackageSpec(
    python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
    pickle_object_gcs_uri=_TEST_AGENT_ENGINE_GCS_URI,
    dependency_files_gcs_uri=_TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI,
    requirements_gcs_uri=_TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
)

_TEST_AGENT_ENGINE_OBJ = types.ReasoningEngine(
    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
        agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
    ),
)
_TEST_AGENT_ENGINE_OBJ.spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


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
def cloudpickle_load_mock():
    with mock.patch.object(cloudpickle, "load") as cloudpickle_load_mock:
        yield cloudpickle_load_mock


@pytest.fixture(scope="module")
def create_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "create_reasoning_engine",
    ) as create_agent_engine_mock:
        create_agent_engine_lro_mock = mock.Mock(spec=ga_operation.Operation)
        create_agent_engine_lro_mock.result.return_value = _TEST_AGENT_ENGINE_OBJ
        create_agent_engine_mock.return_value = create_agent_engine_lro_mock
        yield create_agent_engine_mock


@pytest.fixture(scope="function")
def get_gca_resource_mock():
    with mock.patch.object(
        base.VertexAiResourceNoun,
        "_get_gca_resource",
    ) as get_gca_resource_mock:
        get_gca_resource_mock.return_value = _TEST_AGENT_ENGINE_OBJ
        yield get_gca_resource_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestAgentEngineA2A:
    def setup_method(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )

    def test_create_agent_engine_with_protobuf_agent_card(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        cloudpickle_load_mock,
        get_gca_resource_mock,
    ):
        a2a_pb2 = None
        # fmt: off
        try:
            try:
                from a2a.compat.v0_3 import a2a_v0_3_pb2 as a2a_pb2
            except ImportError:
                from a2a.grpc import a2a_pb2
            has_a2a_pb2 = True
        except (ImportError, TypeError):
            has_a2a_pb2 = False
        # fmt: on

        if not has_a2a_pb2:
            pytest.skip("a2a_pb2 could not be imported.")

        card = a2a_pb2.AgentCard(name="test_agent_card")
        agent = CapitalizeEngineWithCard(card)

        agent_engines.create(
            agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
        )

        expected_reasoning_engine = types.ReasoningEngine(
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            spec=types.ReasoningEngineSpec(
                package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
                agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
        )
        from google.protobuf import json_format

        expected_class_method = struct_pb2.Struct()
        expected_class_method.CopyFrom(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        expected_class_method["a2a_agent_card"] = json_format.MessageToJson(card)
        expected_reasoning_engine.spec.class_methods.append(expected_class_method)

        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=expected_reasoning_engine,
        )

    def test_create_agent_engine_with_pydantic_agent_card(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        cloudpickle_load_mock,
        get_gca_resource_mock,
    ):
        card = DummyPydanticCard()
        agent = CapitalizeEngineWithCard(card)

        agent_engines.create(
            agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
        )

        expected_reasoning_engine = types.ReasoningEngine(
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            spec=types.ReasoningEngineSpec(
                package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
                agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
        )

        expected_class_method = struct_pb2.Struct()
        expected_class_method.CopyFrom(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        expected_class_method["a2a_agent_card"] = card.model_dump_json()
        expected_reasoning_engine.spec.class_methods.append(expected_class_method)

        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=expected_reasoning_engine,
        )

    def test_create_agent_engine_with_invalid_agent_card(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        cloudpickle_load_mock,
        get_gca_resource_mock,
    ):
        agent = CapitalizeEngineWithCard(card="invalid_card_type_string")

        with pytest.raises(
            TypeError,
            match="Unsupported AgentCard type",
        ):
            agent_engines.create(
                agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            )


class TestA2aPublicCardRoutes:
    """Verifies the public agent card is served at the Agent Runtime card paths."""

    def _build_agent(self):
        """Builds an A2aAgent from the vertexai template and runs set_up()."""
        # pylint: disable=g-import-not-at-top
        from a2a import types as a2a_types
        from vertexai.agent_engines.templates import (
            a2a as a2a_template,
        )

        # pylint: enable=g-import-not-at-top
        card = a2a_types.AgentCard(
            name="Test",
            description="Test",
            supported_interfaces=[
                a2a_types.AgentInterface(
                    url="http://example.com",
                    protocol_binding="HTTP+JSON",
                    protocol_version="1.0",
                )
            ],
            version="0.0.1",
            capabilities=a2a_types.AgentCapabilities(),
            skills=[
                a2a_types.AgentSkill(
                    id="hello_world",
                    name="Returns hello world",
                    description="just returns hello world",
                    tags=["hello world"],
                    examples=["hi"],
                )
            ],
            default_input_modes=["text/plain"],
            default_output_modes=["text/plain"],
        )
        agent = a2a_template.A2aAgent(agent_card=card)
        with mock.patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_PROJECT": _TEST_PROJECT,
                "GOOGLE_CLOUD_LOCATION": _TEST_LOCATION,
            },
        ):
            agent.set_up()
        return agent

    def _client(self, agent):
        """Builds a Starlette test client over the agent's registered routes."""
        # pylint: disable=g-import-not-at-top
        from starlette.applications import Starlette
        from starlette.testclient import TestClient

        # pylint: enable=g-import-not-at-top
        return TestClient(Starlette(routes=agent.rest_routes))

    def test_public_card_routes_not_shadowed_by_tenant_mount(self):
        """The public card resolves and is not shadowed by the tenant Mount."""
        client = self._client(self._build_agent())
        for path in ("/a2a/card", "/a2a/v1/card"):
            resp = client.get(path)
            assert resp.status_code == 200
            body = resp.json()
            assert body["name"] == "Test"
            assert body["skills"][0]["id"] == "hello_world"


class TestWrapA2aOperationTimeout:
    """Verifies default and per-call timeout handling in _wrap_a2a_operation."""

    # pylint: disable=protected-access

    def test_legacy_wrap_a2a_operation_timeout(self):
        """_agent_engines._wrap_a2a_operation defaults to None and accepts per-call timeout."""
        agent_card_json = '{"name": "Test Agent", "version": "1.0.0"}'
        wrapped = _agent_engines._wrap_a2a_operation(
            "on_message_send", agent_card_json
        )
        fake_engine = mock.MagicMock()
        fake_engine.resource_name = _TEST_AGENT_ENGINE_RESOURCE_NAME

        async def _empty_stream():
            if False:  # pylint: disable=using-constant-test
                yield None

        mock_a2a_client = mock.MagicMock()
        mock_a2a_client.send_message.side_effect = lambda msg: _empty_stream()
        mock_factory = mock.MagicMock()
        mock_factory.create.return_value = mock_a2a_client
        mock_card = mock.MagicMock()
        mock_card.supported_interfaces = []
        mock_card.capabilities.streaming = False

        with (
            mock.patch.object(
                _agent_engines.httpx, "AsyncClient"
            ) as mock_async_client,
            mock.patch.object(
                _agent_engines, "AgentCard", return_value=mock_card
            ),
            mock.patch.object(_agent_engines, "AgentInterface"),
            mock.patch.object(_agent_engines, "TransportProtocol"),
            mock.patch.object(_agent_engines, "ClientConfig"),
            mock.patch.object(
                _agent_engines, "ClientFactory", return_value=mock_factory
            ),
            mock.patch.object(_agent_engines, "Message") as mock_message,
        ):
            asyncio.run(wrapped(fake_engine, message_id="m1"))
            mock_async_client.assert_called_once()
            assert mock_async_client.call_args.kwargs["timeout"] is None
            mock_message.assert_called_once_with(message_id="m1")

            mock_async_client.reset_mock()
            mock_message.reset_mock()
            mock_card.supported_interfaces = []

            asyncio.run(wrapped(fake_engine, message_id="m2", timeout=120.0))
            mock_async_client.assert_called_once()
            assert mock_async_client.call_args.kwargs["timeout"] == 120.0
            mock_message.assert_called_once_with(message_id="m2")

    def test_genai_wrap_a2a_operation_v03_per_call_timeout(self):
        """_wrap_a2a_operation_v03 pops per-call timeout and overrides http_options.timeout."""
        # pylint: disable=g-import-not-at-top
        from vertexai._genai import _agent_engines_utils

        # pylint: enable=g-import-not-at-top
        agent_card_json = '{"name": "Test Agent", "version": "1.0.0"}'
        wrapped = _agent_engines_utils._wrap_a2a_operation_v03(
            "on_message_send", agent_card_json
        )
        fake_engine = mock.MagicMock()
        fake_engine.api_resource.name = _TEST_AGENT_ENGINE_RESOURCE_NAME
        fake_engine.api_client._api_client._http_options.base_url = (
            "https://us-central1-aiplatform.googleapis.com"
        )
        fake_engine.api_client._api_client._http_options.api_version = "v1beta1"
        fake_engine.api_client._api_client._http_options.timeout = 30000
        fake_engine.api_client._api_client._credentials.token = "fake-token"

        async def _empty_stream():
            if False:  # pylint: disable=using-constant-test
                yield None

        mock_a2a_client = mock.MagicMock()
        mock_a2a_client.send_message.side_effect = lambda msg: _empty_stream()
        mock_factory = mock.MagicMock()
        mock_factory.create.return_value = mock_a2a_client
        mock_card = mock.MagicMock()
        mock_card.preferred_transport = None
        mock_card.capabilities.streaming = False

        with (
            mock.patch.object(
                _agent_engines_utils.httpx, "AsyncClient"
            ) as mock_async_client,
            mock.patch.object(
                _agent_engines_utils, "AgentCard", return_value=mock_card
            ),
            mock.patch.object(_agent_engines_utils, "TransportProtocol"),
            mock.patch.object(_agent_engines_utils, "ClientConfig"),
            mock.patch.object(
                _agent_engines_utils, "ClientFactory", return_value=mock_factory
            ),
            mock.patch.object(_agent_engines_utils, "Message") as mock_message,
        ):
            asyncio.run(wrapped(fake_engine, messageId="m1"))
            mock_async_client.assert_called_once()
            assert mock_async_client.call_args.kwargs["timeout"] == 30.0
            mock_message.assert_called_once_with(messageId="m1")

            mock_async_client.reset_mock()
            mock_message.reset_mock()

            asyncio.run(wrapped(fake_engine, messageId="m2", timeout=120.0))
            mock_async_client.assert_called_once()
            assert mock_async_client.call_args.kwargs["timeout"] == 120.0
            mock_message.assert_called_once_with(messageId="m2")

    def test_genai_wrap_a2a_operation_v10_per_call_timeout(self):
        """_wrap_a2a_operation_v10 pops per-call timeout and overrides http_options.timeout."""
        # pylint: disable=g-import-not-at-top
        from vertexai._genai import _agent_engines_utils

        # pylint: enable=g-import-not-at-top
        agent_card_json = (
            '{"name": "Test Agent", "version": "1.0.0", '
            '"supportedInterfaces": [{"url": "http://localhost:8080/a2a/rest/", '
            '"protocolBinding": "HTTP+JSON", "protocolVersion": "1.0"}]}'
        )
        wrapped = _agent_engines_utils._wrap_a2a_operation_v10(
            "on_message_send", agent_card_json
        )
        fake_engine = mock.MagicMock()
        fake_engine.api_resource.name = _TEST_AGENT_ENGINE_RESOURCE_NAME
        fake_engine.api_client._api_client._http_options.base_url = (
            "https://us-central1-aiplatform.googleapis.com"
        )
        fake_engine.api_client._api_client._http_options.api_version = "v1beta1"
        fake_engine.api_client._api_client._http_options.timeout = 30000
        fake_engine.api_client._api_client._credentials.token = "fake-token"

        async def _empty_stream():
            if False:  # pylint: disable=using-constant-test
                yield None

        mock_a2a_client = mock.MagicMock()
        mock_a2a_client.send_message.side_effect = (
            lambda req, context=None: _empty_stream()
        )
        mock_factory = mock.MagicMock()
        mock_factory.create.return_value = mock_a2a_client

        with (
            mock.patch.object(
                _agent_engines_utils.httpx, "AsyncClient"
            ) as mock_async_client,
            mock.patch.object(_agent_engines_utils, "ClientConfig"),
            mock.patch.object(
                _agent_engines_utils, "ClientFactory", return_value=mock_factory
            ),
        ):
            asyncio.run(wrapped(fake_engine, request="req1"))
            mock_async_client.assert_called_once()
            assert mock_async_client.call_args.kwargs["timeout"] == 30.0

            mock_async_client.reset_mock()

            asyncio.run(wrapped(fake_engine, request="req2", timeout=120.0))
            mock_async_client.assert_called_once()
            assert mock_async_client.call_args.kwargs["timeout"] == 120.0


class TestCreateAgentCard:
    """Tests for create_agent_card security_schemes, security, and kwargs support."""

    def test_create_agent_card_with_security_and_kwargs(self):
        """Verifies create_agent_card forwards security_schemes, security, and kwargs."""
        # pylint: disable=g-import-not-at-top
        from a2a import types as a2a_types
        from vertexai.agent_engines.templates import (
            a2a as a2a_template,
        )

        # pylint: enable=g-import-not-at-top
        skill = a2a_types.AgentSkill(
            id="hello_world",
            name="Returns hello world",
            description="just returns hello world",
            tags=["hello world"],
            examples=["hi"],
        )
        security_schemes = {
            "bearer_auth": a2a_types.SecurityScheme(
                http_auth_security_scheme=a2a_types.HTTPAuthSecurityScheme(
                    scheme="Bearer",
                    bearer_format="JWT",
                )
            )
        }
        security = [{"bearer_auth": ["read", "write"]}]

        card = a2a_template.create_agent_card(
            agent_name="Secure Agent",
            description="An agent with security schemes",
            skills=[skill],
            security_schemes=security_schemes,
            security=security,
            documentation_url="https://example.com/docs",
        )

        assert card.name == "Secure Agent"
        assert card.documentation_url == "https://example.com/docs"
        assert "bearer_auth" in card.security_schemes
        assert (
            card.security_schemes[
                "bearer_auth"
            ].http_auth_security_scheme.scheme
            == "Bearer"
        )
        assert len(card.security_requirements) == 1
        assert list(
            card.security_requirements[0].schemes["bearer_auth"].list
        ) == ["read", "write"]

    def test_create_agent_card_with_security_requirement_proto(self):
        """Verifies create_agent_card accepts SecurityRequirement, StringList, and wrapper dicts."""
        # pylint: disable=g-import-not-at-top
        from a2a import types as a2a_types
        from vertexai.agent_engines.templates import (
            a2a as a2a_template,
        )

        # pylint: enable=g-import-not-at-top
        skill = a2a_types.AgentSkill(
            id="hello_world",
            name="Returns hello world",
            description="just returns hello world",
            tags=["hello world"],
            examples=["hi"],
        )
        security = [
            a2a_types.SecurityRequirement(
                schemes={"bearer_auth": a2a_types.StringList(list=["read"])}
            ),
            {"oauth2": a2a_types.StringList(list=["write"])},
            {"schemes": {"api_key": ["admin"]}},
            {"schemes": ["custom_scope"]},
        ]

        card = a2a_template.create_agent_card(
            agent_name="Secure Agent",
            description="An agent with security requirements",
            skills=[skill],
            security=security,
        )

        assert len(card.security_requirements) == 4
        assert list(
            card.security_requirements[0].schemes["bearer_auth"].list
        ) == ["read"]
        assert list(
            card.security_requirements[1].schemes["oauth2"].list
        ) == ["write"]
        assert list(
            card.security_requirements[2].schemes["api_key"].list
        ) == ["admin"]
        assert list(
            card.security_requirements[3].schemes["schemes"].list
        ) == ["custom_scope"]

    def test_create_agent_card_with_v03_agent_card_fallback(self, monkeypatch):
        """Verifies create_agent_card falls back to security key for non-proto AgentCard."""
        # pylint: disable=g-import-not-at-top
        from vertexai.agent_engines.templates import (
            a2a as a2a_template,
        )

        # pylint: enable=g-import-not-at-top
        mock_a2a_types = mock.MagicMock()
        del mock_a2a_types.AgentCard.DESCRIPTOR
        mock_a2a_types.AgentCard.side_effect = lambda **kw: kw
        monkeypatch.setitem(sys.modules, "a2a.types", mock_a2a_types)

        security = [{"oauth2": ["openid"]}]
        card = a2a_template.create_agent_card(
            agent_name="Fallback Agent",
            description="Fallback description",
            skills=[mock.MagicMock()],
            security=security,
        )
        assert card["security"] == security

    def test_preview_create_agent_card_with_security_and_kwargs(
        self, monkeypatch
    ):
        """Verifies preview create_agent_card forwards security_schemes, security, and kwargs."""
        # pylint: disable=g-import-not-at-top
        from vertexai.preview.reasoning_engines.templates import (
            a2a as preview_a2a_template,
        )

        # pylint: enable=g-import-not-at-top
        mock_a2a_types = mock.MagicMock()
        mock_a2a_types.AgentCard.side_effect = lambda **kw: kw
        monkeypatch.setitem(sys.modules, "a2a.types", mock_a2a_types)

        security_schemes = {"oauth2": {"type": "oauth2"}}
        security = [{"oauth2": ["openid"]}]

        card = preview_a2a_template.create_agent_card(
            agent_name="Preview Secure Agent",
            description="Preview agent description",
            skills=[mock.MagicMock()],
            security_schemes=security_schemes,
            security=security,
            documentation_url="https://example.com/preview-docs",
        )

        assert card["name"] == "Preview Secure Agent"
        assert card["security_schemes"] == security_schemes
        assert card["security"] == security
        assert card["documentation_url"] == "https://example.com/preview-docs"

        basic_card = preview_a2a_template.create_agent_card(
            agent_name="Preview Basic Agent",
            description="Preview basic description",
            skills=[mock.MagicMock()],
        )
        assert "security_schemes" not in basic_card
        assert "security" not in basic_card
