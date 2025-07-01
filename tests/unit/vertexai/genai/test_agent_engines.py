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
import asyncio
import importlib
import json
import os
import pytest
import sys
import tempfile
from typing import Any, AsyncIterable, Dict, Iterable, List
from unittest import mock
from urllib.parse import urlencode

from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer
from vertexai._genai import agent_engines
from vertexai._genai import types as _genai_types
from vertexai.agent_engines import _agent_engines
from vertexai.agent_engines import _utils
from google.genai import client as genai_client
from google.genai import types as genai_types


_TEST_AGENT_FRAMEWORK = "test-agent-framework"


class CapitalizeEngine:
    """A sample Agent Engine."""

    def set_up(self):
        pass

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    def clone(self):
        return self


class AsyncQueryEngine:
    """A sample Agent Engine that implements `async_query`."""

    def set_up(self):
        pass

    async def async_query(self, unused_arbitrary_string_name: str):
        """Runs the query asynchronously."""
        return unused_arbitrary_string_name.upper()

    def clone(self):
        return self


class AsyncStreamQueryEngine:
    """A sample Agent Engine that implements `async_stream_query`."""

    def set_up(self):
        pass

    async def async_stream_query(
        self, unused_arbitrary_string_name: str
    ) -> AsyncIterable[Any]:
        """Runs the async stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self


class StreamQueryEngine:
    """A sample Agent Engine that implements `stream_query`."""

    def set_up(self):
        pass

    def stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self


class OperationRegistrableEngine:
    """Add a test class that implements OperationRegistrable."""

    agent_framework = _TEST_AGENT_FRAMEWORK

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    async def async_query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the query asynchronously."""
        return unused_arbitrary_string_name.upper()

    # Add a custom method to test the custom method registration.
    def custom_method(self, x: str) -> str:
        return x.upper()

    # Add a custom async method to test the custom async method registration.
    async def custom_async_method(self, x: str):
        return x.upper()

    def stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    async def async_stream_query(
        self, unused_arbitrary_string_name: str
    ) -> AsyncIterable[Any]:
        """Runs the async stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    # Add a custom method to test the custom stream method registration.
    def custom_stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    # Add a custom method to test the custom stream method registration.
    def custom_stream_method(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    async def custom_async_stream_method(
        self, unused_arbitrary_string_name: str
    ) -> AsyncIterable[Any]:
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self

    def register_operations(self) -> Dict[str, List[str]]:
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_DEFAULT_METHOD_NAME,
                _TEST_CUSTOM_METHOD_NAME,
            ],
            _TEST_ASYNC_API_MODE: [
                _TEST_DEFAULT_ASYNC_METHOD_NAME,
                _TEST_CUSTOM_ASYNC_METHOD_NAME,
            ],
            _TEST_STREAM_API_MODE: [
                _TEST_DEFAULT_STREAM_METHOD_NAME,
                _TEST_CUSTOM_STREAM_METHOD_NAME,
            ],
            _TEST_ASYNC_STREAM_API_MODE: [
                _TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
                _TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
            ],
        }


class SameRegisteredOperationsEngine:
    """Add a test class that is different from `OperationRegistrableEngine` but has the same registered operations."""

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    async def async_query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the query asynchronously."""
        return unused_arbitrary_string_name.upper()

    # Add a custom method to test the custom method registration
    def custom_method(self, x: str) -> str:
        return x.upper()

    # Add a custom method that is not registered.
    def custom_method_2(self, x: str) -> str:
        return x.upper()

    # Add a custom async method to test the custom async method registration.
    async def custom_async_method(self, x: str):
        return x.upper()

    def stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    async def async_stream_query(
        self, unused_arbitrary_string_name: str
    ) -> AsyncIterable[Any]:
        """Runs the async stream engine."""
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    # Add a custom method to test the custom stream method registration.
    def custom_stream_method(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    async def custom_async_stream_method(
        self, unused_arbitrary_string_name: str
    ) -> AsyncIterable[Any]:
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self

    def register_operations(self) -> Dict[str, List[str]]:
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_DEFAULT_METHOD_NAME,
                _TEST_CUSTOM_METHOD_NAME,
            ],
            _TEST_ASYNC_API_MODE: [
                _TEST_DEFAULT_ASYNC_METHOD_NAME,
                _TEST_CUSTOM_ASYNC_METHOD_NAME,
            ],
            _TEST_STREAM_API_MODE: [
                _TEST_DEFAULT_STREAM_METHOD_NAME,
                _TEST_CUSTOM_STREAM_METHOD_NAME,
            ],
            _TEST_ASYNC_STREAM_API_MODE: [
                _TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
                _TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
            ],
        }


class OperationNotRegisteredEngine:
    """Add a test class that has a method that is not registered."""

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    def custom_method(self, x: str) -> str:
        return x.upper()

    def clone(self):
        return self

    def register_operations(self) -> Dict[str, List[str]]:
        # `query` method is not exported in registered operations.
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_CUSTOM_METHOD_NAME,
            ]
        }


class RegisteredOperationNotExistEngine:
    """Add a test class that has a method that is registered but does not exist."""

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    def custom_method(self, x: str) -> str:
        return x.upper()

    def clone(self):
        return self

    def register_operations(self) -> Dict[str, List[str]]:
        # Registered method `missing_method` is not a method of the AgentEngine.
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_DEFAULT_METHOD_NAME,
                _TEST_CUSTOM_METHOD_NAME,
                "missing_method",
            ]
        }


class MethodToBeUnregisteredEngine:
    """An Agent Engine that has a method to be unregistered."""

    def method_to_be_unregistered(self, unused_arbitrary_string_name: str) -> str:
        """Method to be unregistered."""
        return unused_arbitrary_string_name.upper()

    def register_operations(self) -> Dict[str, List[str]]:
        # Registered method `missing_method` is not a method of the AgentEngine.
        return {_TEST_STANDARD_API_MODE: [_TEST_METHOD_TO_BE_UNREGISTERED_NAME]}


_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_STAGING_BUCKET = "gs://test-bucket"
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_OPERATION_ID = "4589432830794137600"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_AGENT_ENGINE_OPERATION_NAME = f"{_TEST_PARENT}/operations/{_TEST_OPERATION_ID}"
_TEST_AGENT_ENGINE_DISPLAY_NAME = "Agent Engine Display Name"
_TEST_AGENT_ENGINE_DESCRIPTION = "Agent Engine Description"
_TEST_AGENT_ENGINE_LIST_FILTER = f'display_name="{_TEST_AGENT_ENGINE_DISPLAY_NAME}"'
_TEST_GCS_DIR_NAME = _agent_engines._DEFAULT_GCS_DIR_NAME
_TEST_BLOB_FILENAME = _agent_engines._BLOB_FILENAME
_TEST_REQUIREMENTS_FILE = _agent_engines._REQUIREMENTS_FILE
_TEST_EXTRA_PACKAGES_FILE = _agent_engines._EXTRA_PACKAGES_FILE
_TEST_STANDARD_API_MODE = _agent_engines._STANDARD_API_MODE
_TEST_ASYNC_API_MODE = _agent_engines._ASYNC_API_MODE
_TEST_STREAM_API_MODE = _agent_engines._STREAM_API_MODE
_TEST_ASYNC_STREAM_API_MODE = _agent_engines._ASYNC_STREAM_API_MODE
_TEST_DEFAULT_METHOD_NAME = _agent_engines._DEFAULT_METHOD_NAME
_TEST_DEFAULT_ASYNC_METHOD_NAME = _agent_engines._DEFAULT_ASYNC_METHOD_NAME
_TEST_DEFAULT_STREAM_METHOD_NAME = _agent_engines._DEFAULT_STREAM_METHOD_NAME
_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME = (
    _agent_engines._DEFAULT_ASYNC_STREAM_METHOD_NAME
)
_TEST_CAPITALIZE_ENGINE_METHOD_DOCSTRING = "Runs the engine."
_TEST_STREAM_METHOD_DOCSTRING = "Runs the stream engine."
_TEST_ASYNC_STREAM_METHOD_DOCSTRING = "Runs the async stream engine."
_TEST_MODE_KEY_IN_SCHEMA = _agent_engines._MODE_KEY_IN_SCHEMA
_TEST_METHOD_NAME_KEY_IN_SCHEMA = _agent_engines._METHOD_NAME_KEY_IN_SCHEMA
_TEST_CUSTOM_METHOD_NAME = "custom_method"
_TEST_CUSTOM_ASYNC_METHOD_NAME = "custom_async_method"
_TEST_CUSTOM_STREAM_METHOD_NAME = "custom_stream_method"
_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME = "custom_async_stream_method"
_TEST_CUSTOM_METHOD_DEFAULT_DOCSTRING = """
    Runs the Agent Engine to serve the user request.

    This will be based on the `.custom_method(...)` of the python object that
    was passed in when creating the Agent Engine. The method will invoke the
    `query` API client of the python object.

    Args:
        **kwargs:
            Optional. The arguments of the `.custom_method(...)` method.

    Returns:
        dict[str, Any]: The response from serving the user request.
"""
_TEST_CUSTOM_ASYNC_METHOD_DEFAULT_DOCSTRING = """
    Runs the Agent Engine to serve the user request.

    This will be based on the `.custom_async_method(...)` of the python object that
    was passed in when creating the Agent Engine. The method will invoke the
    `async_query` API client of the python object.

    Args:
        **kwargs:
            Optional. The arguments of the `.custom_async_method(...)` method.

    Returns:
        Coroutine[Any]: The response from serving the user request.
"""
_TEST_CUSTOM_STREAM_METHOD_DEFAULT_DOCSTRING = """
    Runs the Agent Engine to serve the user request.

    This will be based on the `.custom_stream_method(...)` of the python object that
    was passed in when creating the Agent Engine. The method will invoke the
    `stream_query` API client of the python object.

    Args:
        **kwargs:
            Optional. The arguments of the `.custom_stream_method(...)` method.

    Returns:
        Iterable[Any]: The response from serving the user request.
"""
_TEST_CUSTOM_ASYNC_STREAM_METHOD_DEFAULT_DOCSTRING = """
    Runs the Agent Engine to serve the user request.

    This will be based on the `.custom_async_stream_method(...)` of the python object that
    was passed in when creating the Agent Engine. The method will invoke the
    `async_stream_query` API client of the python object.

    Args:
        **kwargs:
            Optional. The arguments of the `.custom_async_stream_method(...)` method.

    Returns:
        AsyncIterable[Any]: The response from serving the user request.
"""
_TEST_METHOD_TO_BE_UNREGISTERED_NAME = "method_to_be_unregistered"
_TEST_QUERY_PROMPT = "Find the first fibonacci number greater than 999"
_TEST_AGENT_ENGINE_ENV_KEY = "GOOGLE_CLOUD_AGENT_ENGINE_ENV"
_TEST_AGENT_ENGINE_ENV_VALUE = "test_env_value"
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
_TEST_AGENT_ENGINE_REQUIREMENTS = [
    "google-cloud-aiplatform==1.29.0",
    "langchain",
]
_TEST_AGENT_ENGINE_INVALID_EXTRA_PACKAGES = [
    "lib",
    "main.py",
]
_TEST_AGENT_ENGINE_QUERY_SCHEMA = _utils.generate_schema(
    CapitalizeEngine().query,
    schema_name=_TEST_DEFAULT_METHOD_NAME,
)
_TEST_AGENT_ENGINE_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STANDARD_API_MODE
_TEST_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
_TEST_AGENT_ENGINE_FRAMEWORK = _agent_engines._DEFAULT_AGENT_FRAMEWORK
_TEST_AGENT_ENGINE_CLASS_METHOD_1 = {
    "description": "Runs the engine.",
    "name": "query",
    "parameters": {
        "type": "object",
        "properties": {
            "unused_arbitrary_string_name": {"type": "string"},
        },
        "required": ["unused_arbitrary_string_name"],
    },
    "api_mode": "",
}
_TEST_AGENT_ENGINE_CLASS_METHOD_ASYNC_QUERY = {
    "description": "Runs the engine.",
    "name": "async_query",
    "parameters": {
        "type": "object",
        "properties": {
            "unused_arbitrary_string_name": {"type": "string"},
        },
        "required": ["unused_arbitrary_string_name"],
    },
    "api_mode": "async",
}
_TEST_AGENT_ENGINE_CLASS_METHOD_STREAM_QUERY = {
    "description": "Runs the engine.",
    "name": "stream_query",
    "parameters": {
        "type": "object",
        "properties": {
            "unused_arbitrary_string_name": {"type": "string"},
        },
        "required": ["unused_arbitrary_string_name"],
    },
    "api_mode": "stream",
}
_TEST_AGENT_ENGINE_CLASS_METHOD_ASYNC_STREAM_QUERY = {
    "description": "Runs the engine.",
    "name": "async_stream_query",
    "parameters": {
        "type": "object",
        "properties": {
            "unused_arbitrary_string_name": {"type": "string"},
        },
        "required": ["unused_arbitrary_string_name"],
    },
    "api_mode": "async_stream",
}
_TEST_AGENT_ENGINE_ENV_VARS_INPUT = {
    "TEST_ENV_VAR": "TEST_ENV_VAR_VALUE",
    "TEST_ENV_VAR_2": "TEST_ENV_VAR_VALUE_2",
    "TEST_SECRET_ENV_VAR": {
        "secret": "TEST_SECRET_NAME_1",
        "version": "TEST_SECRET_VERSION_1",
    },
}
_TEST_AGENT_ENGINE_SPEC = _genai_types.ReasoningEngineSpecDict(
    agent_framework=_TEST_AGENT_ENGINE_FRAMEWORK,
    class_methods=[_TEST_AGENT_ENGINE_CLASS_METHOD_1],
    deployment_spec={
        "env": [
            {"name": "TEST_ENV_VAR", "value": "TEST_ENV_VAR_VALUE"},
            {"name": "TEST_ENV_VAR_2", "value": "TEST_ENV_VAR_VALUE_2"},
        ],
        "secret_env": [
            {
                "name": "TEST_SECRET_ENV_VAR",
                "secret_ref": {
                    "secret": "TEST_SECRET_NAME_1",
                    "version": "TEST_SECRET_VERSION_1",
                },
            },
        ],
    },
    package_spec=_genai_types.ReasoningEngineSpecPackageSpecDict(
        python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
        pickle_object_gcs_uri=_TEST_AGENT_ENGINE_GCS_URI,
        dependency_files_gcs_uri=_TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI,
        requirements_gcs_uri=_TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
    ),
)
_TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE = [{"output": "hello"}, {"output": "world"}]
_TEST_AGENT_ENGINE_OPERATION_SCHEMAS = []
_TEST_AGENT_ENGINE_EXTRA_PACKAGE = "fake.py"
_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA = _utils.generate_schema(
    AsyncQueryEngine().async_query,
    schema_name=_TEST_DEFAULT_ASYNC_METHOD_NAME,
)
_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_ASYNC_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA = _utils.generate_schema(
    OperationRegistrableEngine().custom_method,
    schema_name=_TEST_CUSTOM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA[
    _TEST_MODE_KEY_IN_SCHEMA
] = _TEST_STANDARD_API_MODE
_TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA = _utils.generate_schema(
    OperationRegistrableEngine().custom_async_method,
    schema_name=_TEST_CUSTOM_ASYNC_METHOD_NAME,
)
_TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA[
    _TEST_MODE_KEY_IN_SCHEMA
] = _TEST_ASYNC_API_MODE
_TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA = _utils.generate_schema(
    StreamQueryEngine().stream_query,
    schema_name=_TEST_DEFAULT_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STREAM_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA = _utils.generate_schema(
    OperationRegistrableEngine().custom_stream_method,
    schema_name=_TEST_CUSTOM_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA[
    _TEST_MODE_KEY_IN_SCHEMA
] = _TEST_STREAM_API_MODE
_TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA = _utils.generate_schema(
    AsyncStreamQueryEngine().async_stream_query,
    schema_name=_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA[
    _TEST_MODE_KEY_IN_SCHEMA
] = _TEST_ASYNC_STREAM_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA = _utils.generate_schema(
    OperationRegistrableEngine().custom_async_stream_method,
    schema_name=_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA[
    _TEST_MODE_KEY_IN_SCHEMA
] = _TEST_ASYNC_STREAM_API_MODE
_TEST_OPERATION_REGISTRABLE_SCHEMAS = [
    _TEST_AGENT_ENGINE_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA,
    _TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA,
    _TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA,
    _TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA,
]
_TEST_OPERATION_NOT_REGISTERED_SCHEMAS = [
    _TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA,
]
_TEST_REGISTERED_OPERATION_NOT_EXIST_SCHEMAS = [
    _TEST_AGENT_ENGINE_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA,
]
_TEST_NO_OPERATION_REGISTRABLE_SCHEMAS = [
    _TEST_AGENT_ENGINE_QUERY_SCHEMA,
]
_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA = _utils.generate_schema(
    MethodToBeUnregisteredEngine().method_to_be_unregistered,
    schema_name=_TEST_METHOD_TO_BE_UNREGISTERED_NAME,
)
_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA[
    _TEST_MODE_KEY_IN_SCHEMA
] = _TEST_STANDARD_API_MODE
_TEST_ASYNC_QUERY_SCHEMAS = [_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA]
_TEST_STREAM_QUERY_SCHEMAS = [
    _TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA,
]
_TEST_ASYNC_STREAM_QUERY_SCHEMAS = [
    _TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA,
]
_TEST_PACKAGE_DISTRIBUTIONS = {
    "requests": ["requests"],
    "cloudpickle": ["cloudpickle"],
    "pydantic": ["pydantic"],
}
_TEST_OPERATION_NAME = "test_operation_name"


def _create_empty_fake_package(package_name: str) -> str:
    """Creates a temporary directory structure representing an empty fake Python package.

    Args:
        package_name (str): The name of the fake package.

    Returns:
        str: The path to the top-level directory of the fake package.
    """
    temp_dir = tempfile.mkdtemp()
    package_dir = os.path.join(temp_dir, package_name)
    os.makedirs(package_dir)

    # Create an empty __init__.py file to mark it as a package
    init_path = os.path.join(package_dir, "__init__.py")
    open(init_path, "w").close()

    return temp_dir


_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH = _create_empty_fake_package(
    _TEST_AGENT_ENGINE_EXTRA_PACKAGE
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.fixture(scope="module")
def importlib_metadata_version_mock():
    with mock.patch.object(
        importlib.metadata, "version"
    ) as importlib_metadata_version_mock:

        def get_version(pkg):
            versions = {
                "requests": "2.0.0",
                "cloudpickle": "3.0.0",
                "pydantic": "1.11.1",
            }
            return versions.get(pkg, "unknown")

        importlib_metadata_version_mock.side_effect = get_version
        yield importlib_metadata_version_mock


class InvalidCapitalizeEngineWithoutQuerySelf:
    """A sample Agent Engine with an invalid query method."""

    def set_up(self):
        pass

    def query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutAsyncQuerySelf:
    """A sample Agent Engine with an invalid async_query method."""

    def set_up(self):
        pass

    async def async_query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutStreamQuerySelf:
    """A sample Agent Engine with an invalid query_stream_query method."""

    def set_up(self):
        pass

    def stream_query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutAsyncStreamQuerySelf:
    """A sample Agent Engine with an invalid async_stream_query method."""

    def set_up(self):
        pass

    async def async_stream_query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutRegisterOperationsSelf:
    """A sample Agent Engine with an invalid register_operations method."""

    def set_up(self):
        pass

    def register_operations() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutQueryMethod:
    """A sample Agent Engine without a query method."""

    def set_up(self):
        pass

    def invoke(self) -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithNoncallableQueryStreamQuery:
    """A sample Agent Engine with a noncallable query attribute."""

    def __init__(self):
        self.query = "RESPONSE"

    def set_up(self):
        pass


@pytest.mark.usefixtures("google_auth_mock")
class TestAgentEngineHelpers:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(os)
        os.environ[_TEST_AGENT_ENGINE_ENV_KEY] = _TEST_AGENT_ENGINE_ENV_VALUE
        self.client = vertexai.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        self.test_agent = CapitalizeEngine()

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(_agent_engines, "_prepare")
    def test_create_agent_engine_config_lightweight(self, mock_prepare):
        config = self.client.agent_engines._create_config(
            mode="create",
            staging_bucket=_TEST_STAGING_BUCKET,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
        )
        assert config == {
            "display_name": _TEST_AGENT_ENGINE_DISPLAY_NAME,
            "description": _TEST_AGENT_ENGINE_DESCRIPTION,
        }

    @mock.patch.object(_agent_engines, "_prepare")
    def test_create_agent_engine_config_full(self, mock_prepare):
        config = self.client.agent_engines._create_config(
            mode="create",
            agent_engine=self.test_agent,
            staging_bucket=_TEST_STAGING_BUCKET,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
            gcs_dir_name=_TEST_GCS_DIR_NAME,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
        )
        assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
        assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
        assert config["spec"]["agent_framework"] == "custom"
        assert config["spec"]["package_spec"] == {
            "python_version": _TEST_PYTHON_VERSION,
            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
            "dependency_files_gcs_uri": _TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI,
            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
        }
        assert config["spec"]["deployment_spec"] == {
            "env": [
                {"name": "TEST_ENV_VAR", "value": "TEST_ENV_VAR_VALUE"},
                {"name": "TEST_ENV_VAR_2", "value": "TEST_ENV_VAR_VALUE_2"},
            ],
            "secret_env": [
                {
                    "name": "TEST_SECRET_ENV_VAR",
                    "secret_ref": {
                        "secret": "TEST_SECRET_NAME_1",
                        "version": "TEST_SECRET_VERSION_1",
                    },
                },
            ],
        }
        assert config["spec"]["class_methods"] == [_TEST_AGENT_ENGINE_CLASS_METHOD_1]

    @mock.patch.object(_agent_engines, "_prepare")
    def test_update_agent_engine_config_full(self, mock_prepare):
        config = self.client.agent_engines._create_config(
            mode="update",
            agent_engine=self.test_agent,
            staging_bucket=_TEST_STAGING_BUCKET,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
            gcs_dir_name=_TEST_GCS_DIR_NAME,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
        )
        assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
        assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
        assert config["spec"]["agent_framework"] == "custom"
        assert config["spec"]["package_spec"] == {
            "python_version": _TEST_PYTHON_VERSION,
            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
            "dependency_files_gcs_uri": _TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI,
            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
        }
        assert config["spec"]["deployment_spec"] == {
            "env": [
                {"name": "TEST_ENV_VAR", "value": "TEST_ENV_VAR_VALUE"},
                {"name": "TEST_ENV_VAR_2", "value": "TEST_ENV_VAR_VALUE_2"},
            ],
            "secret_env": [
                {
                    "name": "TEST_SECRET_ENV_VAR",
                    "secret_ref": {
                        "secret": "TEST_SECRET_NAME_1",
                        "version": "TEST_SECRET_VERSION_1",
                    },
                },
            ],
        }
        assert config["spec"]["class_methods"] == [_TEST_AGENT_ENGINE_CLASS_METHOD_1]
        assert config["update_mask"] == ",".join(
            [
                "display_name",
                "description",
                "spec.package_spec.pickle_object_gcs_uri",
                "spec.package_spec.dependency_files_gcs_uri",
                "spec.package_spec.requirements_gcs_uri",
                "spec.deployment_spec.env",
                "spec.deployment_spec.secret_env",
                "spec.class_methods",
                "spec.agent_framework",
            ]
        )

    def test_get_agent_operation(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(
                    {
                        "name": _TEST_AGENT_ENGINE_OPERATION_NAME,
                        "done": True,
                        "response": _TEST_AGENT_ENGINE_SPEC,
                    }
                ),
            )
            operation = self.client.agent_engines._get_agent_operation(
                operation_name=_TEST_AGENT_ENGINE_OPERATION_NAME,
            )
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_OPERATION_NAME}},
                None,
            )
            assert isinstance(operation, _genai_types.AgentEngineOperation)
            assert operation.done
            assert isinstance(operation.response, _genai_types.ReasoningEngine)

    def test_await_operation(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(
                    {
                        "name": _TEST_AGENT_ENGINE_OPERATION_NAME,
                        "done": True,
                        "response": _TEST_AGENT_ENGINE_SPEC,
                    }
                ),
            )
            agent_engine = self.client.agent_engines._await_operation(
                operation_name=_TEST_AGENT_ENGINE_OPERATION_NAME,
            )
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_OPERATION_NAME}},
                None,
            )
            assert isinstance(agent_engine, _genai_types.AgentEngineOperation)

    def test_register_api_methods(self):
        agent = self.client.agent_engines._register_api_methods(
            agent=_genai_types.AgentEngine(
                api_client=self.client.agent_engines._api_client,
                api_resource=_genai_types.ReasoningEngine(
                    spec=_genai_types.ReasoningEngineSpec(
                        class_methods=[
                            _TEST_AGENT_ENGINE_CLASS_METHOD_1,
                        ]
                    ),
                ),
            )
        )
        assert agent.query.__doc__ == _TEST_AGENT_ENGINE_CLASS_METHOD_1.get(
            "description"
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestAgentEngine:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(os)
        os.environ[_TEST_AGENT_ENGINE_ENV_KEY] = _TEST_AGENT_ENGINE_ENV_VALUE
        self.client = vertexai.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        self.test_agent = CapitalizeEngine()

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_get_agent_engine(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.get(name=_TEST_AGENT_ENGINE_RESOURCE_NAME)
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME}},
                None,
            )

    def test_list_agent_engine(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            expected_query_params = {"filter": _TEST_AGENT_ENGINE_LIST_FILTER}
            list(self.client.agent_engines.list(config=expected_query_params))
            request_mock.assert_called_with(
                "get",
                f"reasoningEngines?{urlencode(expected_query_params)}",
                {"_query": expected_query_params},
                None,
            )

    @mock.patch.object(_agent_engines, "_prepare")
    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_create_agent_engine(self, mock_await_operation, mock_prepare):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent_engine=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    description=_TEST_AGENT_ENGINE_DESCRIPTION,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                    staging_bucket=_TEST_STAGING_BUCKET,
                    gcs_dir_name=_TEST_GCS_DIR_NAME,
                    env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
                ),
            )
            mock_await_operation.assert_called_once_with(
                operation_name=None,
                poll_interval_seconds=10,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "agentFramework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "classMethods": mock.ANY,  # dict ordering was too flakey
                        "deploymentSpec": _TEST_AGENT_ENGINE_SPEC.get(
                            "deployment_spec"
                        ),
                        "packageSpec": _TEST_AGENT_ENGINE_SPEC.get("package_spec"),
                    },
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_create_agent_engine_lightweight(
        self,
        mock_await_operation,
        mock_create_config,
    ):
        mock_create_config.return_value = _genai_types.CreateAgentEngineConfig(
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
        )
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    description=_TEST_AGENT_ENGINE_DESCRIPTION,
                )
            )
            mock_await_operation.assert_called_once_with(
                operation_name=None,
                poll_interval_seconds=1,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_create_agent_engine_with_env_vars_dict(
        self,
        mock_await_operation,
        mock_create_config,
    ):
        mock_create_config.return_value = {
            "display_name": _TEST_AGENT_ENGINE_DISPLAY_NAME,
            "description": _TEST_AGENT_ENGINE_DESCRIPTION,
            "spec": {
                "package_spec": {
                    "python_version": _TEST_PYTHON_VERSION,
                    "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                    "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                },
                "class_methods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
                "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
            },
        }
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent_engine=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                    env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
                    staging_bucket=_TEST_STAGING_BUCKET,
                ),
            )
            mock_create_config.assert_called_with(
                mode="create",
                agent_engine=self.test_agent,
                staging_bucket=_TEST_STAGING_BUCKET,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=None,
                gcs_dir_name=None,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "agentFramework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "classMethods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
                        "packageSpec": {
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "python_version": _TEST_PYTHON_VERSION,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                },
                None,
            )

    @mock.patch.object(_agent_engines, "_prepare")
    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_update_agent_engine_requirements(self, mock_await_operation, mock_prepare):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                agent_engine=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    staging_bucket=_TEST_STAGING_BUCKET,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                ),
            )
            update_mask = ",".join(
                [
                    "spec.package_spec.pickle_object_gcs_uri",
                    "spec.package_spec.requirements_gcs_uri",
                    "spec.class_methods",
                    "spec.agent_framework",
                ]
            )
            query_params = {"updateMask": update_mask}
            request_mock.assert_called_with(
                "patch",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}?{urlencode(query_params)}",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "spec": {
                        "agentFramework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "classMethods": mock.ANY,
                        "packageSpec": {
                            "python_version": _TEST_PYTHON_VERSION,
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                    "_query": {"updateMask": update_mask},
                },
                None,
            )

    @mock.patch.object(_agent_engines, "_prepare")
    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_update_agent_engine_extra_packages(
        self, mock_await_operation, mock_prepare
    ):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                agent_engine=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    staging_bucket=_TEST_STAGING_BUCKET,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                ),
            )
            update_mask = ",".join(
                [
                    "spec.package_spec.pickle_object_gcs_uri",
                    "spec.package_spec.dependency_files_gcs_uri",
                    "spec.package_spec.requirements_gcs_uri",
                    "spec.class_methods",
                    "spec.agent_framework",
                ]
            )
            query_params = {"updateMask": update_mask}
            request_mock.assert_called_with(
                "patch",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}?{urlencode(query_params)}",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "spec": {
                        "agentFramework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "classMethods": mock.ANY,
                        "packageSpec": {
                            "python_version": _TEST_PYTHON_VERSION,
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "dependency_files_gcs_uri": _TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                    "_query": {"updateMask": update_mask},
                },
                None,
            )

    @mock.patch.object(_agent_engines, "_prepare")
    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_update_agent_engine_env_vars(self, mock_await_operation, mock_prepare):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                agent_engine=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    staging_bucket=_TEST_STAGING_BUCKET,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
                ),
            )
            update_mask = ",".join(
                [
                    "spec.package_spec.pickle_object_gcs_uri",
                    "spec.package_spec.requirements_gcs_uri",
                    "spec.deployment_spec.env",
                    "spec.deployment_spec.secret_env",
                    "spec.class_methods",
                    "spec.agent_framework",
                ]
            )
            query_params = {"updateMask": update_mask}
            request_mock.assert_called_with(
                "patch",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}?{urlencode(query_params)}",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "spec": {
                        "agentFramework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "classMethods": mock.ANY,
                        "packageSpec": {
                            "python_version": _TEST_PYTHON_VERSION,
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                        "deploymentSpec": _TEST_AGENT_ENGINE_SPEC.get(
                            "deployment_spec"
                        ),
                    },
                    "_query": {"updateMask": update_mask},
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_update_agent_engine_display_name(self, mock_await_operation):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                ),
            )
            request_mock.assert_called_with(
                "patch",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}?updateMask=display_name",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "_query": {"updateMask": "display_name"},
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_await_operation")
    def test_update_agent_engine_description(self, mock_await_operation):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation()
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                config=_genai_types.AgentEngineConfig(
                    description=_TEST_AGENT_ENGINE_DESCRIPTION,
                ),
            )
            request_mock.assert_called_with(
                "patch",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}?updateMask=description",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "_query": {"updateMask": "description"},
                },
                None,
            )

    def test_delete_agent_engine(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.delete(name=_TEST_AGENT_ENGINE_RESOURCE_NAME)
            request_mock.assert_called_with(
                "delete",
                _TEST_AGENT_ENGINE_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME}},
                None,
            )

    def test_delete_agent_engine_force(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.delete(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                force=True,
            )
        request_mock.assert_called_with(
            "delete",
            _TEST_AGENT_ENGINE_RESOURCE_NAME,
            {"_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME}, "force": True},
            None,
        )

    def test_query_agent_engine(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            agent = self.client.agent_engines._register_api_methods(
                agent=_genai_types.AgentEngine(
                    api_client=self.client.agent_engines,
                    api_resource=_genai_types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=_genai_types.ReasoningEngineSpec(
                            class_methods=[
                                _TEST_AGENT_ENGINE_CLASS_METHOD_1,
                            ]
                        ),
                    ),
                )
            )
            agent.query(query=_TEST_QUERY_PROMPT)
            request_mock.assert_called_with(
                "post",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}:query",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "classMethod": "query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    def test_query_agent_engine_async(self):
        agent = self.client.agent_engines._register_api_methods(
            agent=_genai_types.AgentEngine(
                api_async_client=agent_engines.AsyncAgentEngines(
                    api_client_=self.client.agent_engines._api_client
                ),
                api_resource=_genai_types.ReasoningEngine(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    spec=_genai_types.ReasoningEngineSpec(
                        class_methods=[
                            _TEST_AGENT_ENGINE_CLASS_METHOD_ASYNC_QUERY,
                        ]
                    ),
                ),
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "async_request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            asyncio.run(agent.async_query(query=_TEST_QUERY_PROMPT))
            request_mock.assert_called_with(
                "post",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}:query",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "classMethod": "async_query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    def test_query_agent_engine_stream(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request_streamed"
        ) as request_mock:
            agent = self.client.agent_engines._register_api_methods(
                agent=_genai_types.AgentEngine(
                    api_client=self.client.agent_engines,
                    api_resource=_genai_types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=_genai_types.ReasoningEngineSpec(
                            class_methods=[
                                _TEST_AGENT_ENGINE_CLASS_METHOD_STREAM_QUERY,
                            ]
                        ),
                    ),
                )
            )
            list(agent.stream_query(query=_TEST_QUERY_PROMPT))
            request_mock.assert_called_with(
                "post",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}:streamQuery?alt=sse",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "classMethod": "stream_query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    def test_query_agent_engine_async_stream(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "request_streamed"
        ) as request_mock:
            agent = self.client.agent_engines._register_api_methods(
                agent=_genai_types.AgentEngine(
                    api_client=self.client.agent_engines,
                    api_resource=_genai_types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=_genai_types.ReasoningEngineSpec(
                            class_methods=[
                                _TEST_AGENT_ENGINE_CLASS_METHOD_ASYNC_STREAM_QUERY,
                            ]
                        ),
                    ),
                )
            )

            async def consume():
                async for response in agent.async_stream_query(
                    query=_TEST_QUERY_PROMPT
                ):
                    print(response)

            asyncio.run(consume())
            request_mock.assert_called_with(
                "post",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}:streamQuery?alt=sse",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                    "classMethod": "async_stream_query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    @pytest.mark.parametrize(
        "test_case_name, test_class_methods_spec, want_operation_schema_api_modes",
        [
            (
                "Default (Not Operation Registrable) Engine",
                _TEST_NO_OPERATION_REGISTRABLE_SCHEMAS,
                [
                    (
                        _utils.generate_schema(
                            CapitalizeEngine().query,
                            schema_name=_TEST_DEFAULT_METHOD_NAME,
                        ),
                        _TEST_STANDARD_API_MODE,
                    )
                ],
            ),
            (
                "Operation Registrable Engine",
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
                [
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().query,
                            schema_name=_TEST_DEFAULT_METHOD_NAME,
                        ),
                        _TEST_STANDARD_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().custom_method,
                            schema_name=_TEST_CUSTOM_METHOD_NAME,
                        ),
                        _TEST_STANDARD_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().async_query,
                            schema_name=_TEST_DEFAULT_ASYNC_METHOD_NAME,
                        ),
                        _TEST_ASYNC_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().custom_async_method,
                            schema_name=_TEST_CUSTOM_ASYNC_METHOD_NAME,
                        ),
                        _TEST_ASYNC_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().stream_query,
                            schema_name=_TEST_DEFAULT_STREAM_METHOD_NAME,
                        ),
                        _TEST_STREAM_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().custom_stream_method,
                            schema_name=_TEST_CUSTOM_STREAM_METHOD_NAME,
                        ),
                        _TEST_STREAM_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().async_stream_query,
                            schema_name=_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
                        ),
                        _TEST_ASYNC_STREAM_API_MODE,
                    ),
                    (
                        _utils.generate_schema(
                            OperationRegistrableEngine().custom_async_stream_method,
                            schema_name=_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
                        ),
                        _TEST_ASYNC_STREAM_API_MODE,
                    ),
                ],
            ),
            (
                "Operation Not Registered Engine",
                _TEST_OPERATION_NOT_REGISTERED_SCHEMAS,
                [
                    (
                        _utils.generate_schema(
                            OperationNotRegisteredEngine().custom_method,
                            schema_name=_TEST_CUSTOM_METHOD_NAME,
                        ),
                        _TEST_STANDARD_API_MODE,
                    ),
                ],
            ),
        ],
    )
    @mock.patch.object(genai_client.Client, "_get_api_client")
    @mock.patch.object(agent_engines.AgentEngines, "_get")
    def test_operation_schemas(
        self,
        mock_get,
        mock_get_api_client,
        test_case_name,
        test_class_methods_spec,
        want_operation_schema_api_modes,
    ):
        test_agent_engine = _genai_types.AgentEngine(
            api_resource=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_genai_types.ReasoningEngineSpec(
                    class_methods=test_class_methods_spec,
                ),
            ),
        )
        want_operation_schemas = []
        for want_operation_schema, api_mode in want_operation_schema_api_modes:
            want_operation_schema[_TEST_MODE_KEY_IN_SCHEMA] = api_mode
            want_operation_schemas.append(want_operation_schema)
        assert test_agent_engine.operation_schemas() == want_operation_schemas


@pytest.mark.usefixtures("google_auth_mock")
class TestAgentEngineErrors:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        self.client = vertexai.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        self.test_agent = CapitalizeEngine()

    @pytest.mark.parametrize(
        "test_case_name, test_operation_schemas, want_log_output",
        [
            (
                "No API mode in operation schema",
                [
                    {
                        _TEST_METHOD_NAME_KEY_IN_SCHEMA: _TEST_DEFAULT_METHOD_NAME,
                    },
                ],
                (
                    "Failed to register API methods. Please follow the guide to "
                    "register the API methods: "
                    "https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/develop/custom#custom-methods. "
                    "Error: {Operation schema {'name': 'query'} does not "
                    "contain an `api_mode` field.}"
                ),
            ),
            (
                "No method name in operation schema",
                [
                    {
                        _TEST_MODE_KEY_IN_SCHEMA: _TEST_STANDARD_API_MODE,
                    },
                ],
                (
                    "Failed to register API methods. Please follow the guide to "
                    "register the API methods: "
                    "https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/develop/custom#custom-methods. "
                    "Error: {Operation schema {'api_mode': ''} does not "
                    "contain a `name` field.}"
                ),
            ),
            (
                "Unknown API mode in operation schema",
                [
                    {
                        _TEST_MODE_KEY_IN_SCHEMA: "UNKNOWN_API_MODE",
                        _TEST_METHOD_NAME_KEY_IN_SCHEMA: _TEST_DEFAULT_METHOD_NAME,
                    },
                ],
                (
                    "Failed to register API methods. Please follow the guide to "
                    "register the API methods: "
                    "https://cloud.google.com/vertex-ai/generative-ai/docs/agent-engine/develop/custom#custom-methods. "
                    "Error: {Unsupported api mode: `UNKNOWN_API_MODE`, "
                    "Supported modes are: ``, `async`, `async_stream`, `stream`.}"
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("caplog")
    @mock.patch.object(_genai_types.AgentEngine, "operation_schemas")
    @mock.patch.object(agent_engines.AgentEngines, "_get")
    def test_invalid_operation_schema(
        self,
        mock_get,
        mock_operation_schemas,
        test_case_name,
        test_operation_schemas,
        want_log_output,
        caplog,
    ):
        mock_get.return_value = _genai_types.AgentEngine()  # just to avoid an API call
        mock_operation_schemas.return_value = test_operation_schemas
        self.client.agent_engines.get(name=_TEST_AGENT_ENGINE_RESOURCE_NAME)
        assert want_log_output in caplog.text


@pytest.mark.usefixtures("google_auth_mock")
class TestAsyncAgentEngine:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(vertexai)
        importlib.reload(os)
        os.environ[_TEST_AGENT_ENGINE_ENV_KEY] = _TEST_AGENT_ENGINE_ENV_VALUE
        self.client = vertexai.Client(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        self.test_agent = CapitalizeEngine()

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_delete_agent_engine(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "async_request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            asyncio.run(
                self.client.aio.agent_engines.delete(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME
                )
            )
            request_mock.assert_called_with(
                "delete",
                _TEST_AGENT_ENGINE_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME}},
                None,
            )

    def test_delete_agent_engine_force(self):
        with mock.patch.object(
            self.client.agent_engines._api_client, "async_request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            asyncio.run(
                self.client.aio.agent_engines.delete(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    force=True,
                )
            )
            request_mock.assert_called_with(
                "delete",
                _TEST_AGENT_ENGINE_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME}, "force": True},
                None,
            )
