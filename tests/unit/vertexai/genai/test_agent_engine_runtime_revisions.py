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
from vertexai._genai import _agent_engines_utils
from vertexai._genai import runtime_revisions
from vertexai._genai import types as _genai_types
from google.genai import types as genai_types
import pytest


_TEST_AGENT_FRAMEWORK = "google-adk"
GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY = (
    "GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY"
)


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

    async def bidi_stream_query(self, input_queue: asyncio.Queue) -> AsyncIterable[Any]:
        """Runs the bidi stream engine."""
        while True:
            chunk = await input_queue.get()
            yield chunk

    async def custom_bidi_stream_method(
        self, input_queue: asyncio.Queue
    ) -> AsyncIterable[Any]:
        """Runs the async bidi stream engine."""
        while True:
            chunk = await input_queue.get()
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
            _TEST_BIDI_STREAM_API_MODE: [
                _TEST_DEFAULT_BIDI_STREAM_METHOD_NAME,
                _TEST_CUSTOM_BIDI_STREAM_METHOD_NAME,
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
_TEST_RUNTIME_REVISION_ID = "1234567890"
_TEST_OPERATION_ID = "4589432830794137600"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME = (
    f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}/runtimeRevisions/{_TEST_RUNTIME_REVISION_ID}"
)
_TEST_AGENT_ENGINE_REVISION_OPERATION_NAME = (
    f"{_TEST_PARENT}/operations/{_TEST_OPERATION_ID}"
)
_TEST_AGENT_ENGINE_DISPLAY_NAME = "Agent Engine Display Name"
_TEST_AGENT_ENGINE_DESCRIPTION = "Agent Engine Description"
_TEST_LIST_FILTER = f'name="{_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}"'
_TEST_GCS_DIR_NAME = _agent_engines_utils._DEFAULT_GCS_DIR_NAME
_TEST_BLOB_FILENAME = _agent_engines_utils._BLOB_FILENAME
_TEST_REQUIREMENTS_FILE = _agent_engines_utils._REQUIREMENTS_FILE
_TEST_EXTRA_PACKAGES_FILE = _agent_engines_utils._EXTRA_PACKAGES_FILE
_TEST_STANDARD_API_MODE = _agent_engines_utils._STANDARD_API_MODE
_TEST_ASYNC_API_MODE = _agent_engines_utils._ASYNC_API_MODE
_TEST_STREAM_API_MODE = _agent_engines_utils._STREAM_API_MODE
_TEST_ASYNC_STREAM_API_MODE = _agent_engines_utils._ASYNC_STREAM_API_MODE
_TEST_BIDI_STREAM_API_MODE = _agent_engines_utils._BIDI_STREAM_API_MODE
_TEST_DEFAULT_METHOD_NAME = _agent_engines_utils._DEFAULT_METHOD_NAME
_TEST_DEFAULT_ASYNC_METHOD_NAME = _agent_engines_utils._DEFAULT_ASYNC_METHOD_NAME
_TEST_DEFAULT_STREAM_METHOD_NAME = _agent_engines_utils._DEFAULT_STREAM_METHOD_NAME
_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME = (
    _agent_engines_utils._DEFAULT_ASYNC_STREAM_METHOD_NAME
)
_TEST_DEFAULT_BIDI_STREAM_METHOD_NAME = (
    _agent_engines_utils._DEFAULT_BIDI_STREAM_METHOD_NAME
)
_TEST_CAPITALIZE_ENGINE_METHOD_DOCSTRING = "Runs the engine."
_TEST_STREAM_METHOD_DOCSTRING = "Runs the stream engine."
_TEST_ASYNC_STREAM_METHOD_DOCSTRING = "Runs the async stream engine."
_TEST_BIDI_STREAM_METHOD_DOCSTRING = "Runs the bidi stream engine."
_TEST_MODE_KEY_IN_SCHEMA = _agent_engines_utils._MODE_KEY_IN_SCHEMA
_TEST_METHOD_NAME_KEY_IN_SCHEMA = _agent_engines_utils._METHOD_NAME_KEY_IN_SCHEMA
_TEST_CUSTOM_METHOD_NAME = "custom_method"
_TEST_CUSTOM_ASYNC_METHOD_NAME = "custom_async_method"
_TEST_CUSTOM_STREAM_METHOD_NAME = "custom_stream_method"
_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME = "custom_async_stream_method"
_TEST_CUSTOM_BIDI_STREAM_METHOD_NAME = "custom_bidi_stream_method"
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
_TEST_AGENT_ENGINE_QUERY_SCHEMA = _agent_engines_utils._generate_schema(
    CapitalizeEngine().query,
    schema_name=_TEST_DEFAULT_METHOD_NAME,
)
_TEST_AGENT_ENGINE_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STANDARD_API_MODE
_TEST_PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
_TEST_PYTHON_VERSION_OVERRIDE = "3.11"
_TEST_AGENT_ENGINE_FRAMEWORK = _agent_engines_utils._DEFAULT_AGENT_FRAMEWORK
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
_TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG = {
    "network_attachment": "test-network-attachment",
    "dns_peering_configs": [
        {
            "domain": "test-domain",
            "target_project": "test-target-project",
            "target_network": "test-target-network",
        }
    ],
}
_TEST_AGENT_ENGINE_MIN_INSTANCES = 2
_TEST_AGENT_ENGINE_MAX_INSTANCES = 4
_TEST_AGENT_ENGINE_RESOURCE_LIMITS = {
    "cpu": "2",
    "memory": "4Gi",
}
_TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY = 4
_TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT = "test-custom-service-account"
_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT = (
    _genai_types.IdentityType.SERVICE_ACCOUNT
)
_TEST_AGENT_ENGINE_ENCRYPTION_SPEC = {"kms_key_name": "test-kms-key"}
_TEST_AGENT_ENGINE_REVISION_SPEC = _genai_types.ReasoningEngineSpecDict(
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
    identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
)
_TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE = [{"output": "hello"}, {"output": "world"}]
_TEST_AGENT_ENGINE_OPERATION_SCHEMAS = []
_TEST_AGENT_ENGINE_EXTRA_PACKAGE = "fake.py"
_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA = _agent_engines_utils._generate_schema(
    AsyncQueryEngine().async_query,
    schema_name=_TEST_DEFAULT_ASYNC_METHOD_NAME,
)
_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_ASYNC_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA = _agent_engines_utils._generate_schema(
    OperationRegistrableEngine().custom_method,
    schema_name=_TEST_CUSTOM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STANDARD_API_MODE
)
_TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA = _agent_engines_utils._generate_schema(
    OperationRegistrableEngine().custom_async_method,
    schema_name=_TEST_CUSTOM_ASYNC_METHOD_NAME,
)
_TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_ASYNC_API_MODE
)
_TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA = _agent_engines_utils._generate_schema(
    StreamQueryEngine().stream_query,
    schema_name=_TEST_DEFAULT_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STREAM_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA = _agent_engines_utils._generate_schema(
    OperationRegistrableEngine().custom_stream_method,
    schema_name=_TEST_CUSTOM_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STREAM_API_MODE
)
_TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA = _agent_engines_utils._generate_schema(
    AsyncStreamQueryEngine().async_stream_query,
    schema_name=_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_ASYNC_STREAM_API_MODE
)
_TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA = (
    _agent_engines_utils._generate_schema(
        OperationRegistrableEngine().custom_async_stream_method,
        schema_name=_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_ASYNC_STREAM_API_MODE
)
_TEST_AGENT_ENGINE_BIDI_STREAM_QUERY_SCHEMA = _agent_engines_utils._generate_schema(
    OperationRegistrableEngine().bidi_stream_query,
    schema_name=_TEST_DEFAULT_BIDI_STREAM_METHOD_NAME,
)
_TEST_AGENT_ENGINE_BIDI_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_BIDI_STREAM_API_MODE
)
_TEST_AGENT_ENGINE_CUSTOM_BIDI_STREAM_QUERY_SCHEMA = (
    _agent_engines_utils._generate_schema(
        OperationRegistrableEngine().custom_bidi_stream_method,
        schema_name=_TEST_CUSTOM_BIDI_STREAM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_CUSTOM_BIDI_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_BIDI_STREAM_API_MODE
)
_TEST_OPERATION_REGISTRABLE_SCHEMAS = [
    _TEST_AGENT_ENGINE_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA,
    _TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA,
    _TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA,
    _TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_BIDI_STREAM_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_BIDI_STREAM_QUERY_SCHEMA,
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
_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA = _agent_engines_utils._generate_schema(
    MethodToBeUnregisteredEngine().method_to_be_unregistered,
    schema_name=_TEST_METHOD_TO_BE_UNREGISTERED_NAME,
)
_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STANDARD_API_MODE
)
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
_TEST_AGENT_ENGINE_ERROR = {
    "message": "The following quotas are exceeded",
    "code": 8,
}


_TEST_AGENT_ENGINE_CLASS_METHODS = [
    {
        "name": "query",
        "description": "Simple query method",
        "parameters": {"type": "object", "properties": {"input": {"type": "string"}}},
        "api_mode": "",
    }
]


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


def _create_fake_object_with_module(module_name):
    class FakeObject:
        pass

    FakeObject.__module__ = module_name
    return FakeObject()


@pytest.mark.usefixtures("google_auth_mock")
class TestRuntimeRevisionsHelpers:
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

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_get_delete_runtime_revision_operation(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(
                    {
                        "name": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                        "done": True,
                    }
                ),
            )
            operation = self.client.agent_engines.runtimes.revisions._get_delete_runtime_revision_operation(
                operation_name=_TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
            )
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME}},
                None,
            )
            assert isinstance(
                operation, _genai_types.DeleteAgentEngineRuntimeRevisionOperation
            )
            assert operation.done

    def test_await_operation(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(
                body=json.dumps(
                    {
                        "name": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                        "done": True,
                    }
                ),
            )
            operation = _agent_engines_utils._await_operation(
                operation_name=_TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                get_operation_fn=self.client.agent_engines.runtimes.revisions._get_delete_runtime_revision_operation,
            )
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME}},
                None,
            )
            assert isinstance(
                operation, _genai_types.DeleteAgentEngineRuntimeRevisionOperation
            )

    def test_register_api_methods(self):
        agent = self.client.agent_engines.runtimes.revisions._register_api_methods(
            agent_engine_runtime_revision=_genai_types.AgentEngineRuntimeRevision(
                api_client=self.client.agent_engines.runtimes.revisions._api_client,
                api_resource=_genai_types.ReasoningEngineRuntimeRevision(
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
class TestRuntimeRevisions:
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

    def test_get_runtime_revision(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.runtimes.revisions.get(
                name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME
            )
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}},
                None,
            )

    def test_list_runtime_revisions(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            expected_query_params = {"filter": _TEST_LIST_FILTER}
            list(
                self.client.agent_engines.runtimes.revisions.list(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME, config=expected_query_params
                )
            )
            request_mock.assert_called_with(
                "get",
                f"{_TEST_AGENT_ENGINE_RESOURCE_NAME}/runtimeRevisions?{urlencode(expected_query_params)}",
                {
                    "_query": expected_query_params,
                    "_url": {"name": _TEST_AGENT_ENGINE_RESOURCE_NAME},
                },
                None,
            )

    def test_delete_runtime_revision(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request"
        ) as request_mock:
            request_mock.side_effect = [
                # First call: response to delete.
                genai_types.HttpResponse(body=""),
                # Second call: response to GET operation.
                genai_types.HttpResponse(
                    body=json.dumps(
                        {
                            "name": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                            "done": True,
                        }
                    ),
                ),
            ]

            self.client.agent_engines.runtimes.revisions.delete(
                name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME
            )
            request_mock.call_args_list[0].assert_called_with(
                "delete",
                _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}},
                None,
            )

            request_mock.call_args_list[1].assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME}},
                None,
            )

    def test_query_runtime_revision(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            agent = self.client.agent_engines.runtimes.revisions._register_api_methods(
                agent_engine_runtime_revision=_genai_types.AgentEngineRuntimeRevision(
                    api_client=self.client.agent_engines.runtimes.revisions,
                    api_resource=_genai_types.ReasoningEngineRuntimeRevision(
                        name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
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
                f"{_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}:query",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME},
                    "classMethod": "query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    def test_query_agent_engine_async(self):
        agent = self.client.agent_engines.runtimes.revisions._register_api_methods(
            agent_engine_runtime_revision=_genai_types.AgentEngineRuntimeRevision(
                api_async_client=runtime_revisions.AsyncRuntimeRevisions(
                    api_client_=self.client.agent_engines.runtimes.revisions._api_client
                ),
                api_resource=_genai_types.ReasoningEngineRuntimeRevision(
                    name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
                    spec=_genai_types.ReasoningEngineSpec(
                        class_methods=[
                            _TEST_AGENT_ENGINE_CLASS_METHOD_ASYNC_QUERY,
                        ]
                    ),
                ),
            )
        )
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "async_request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            asyncio.run(agent.async_query(query=_TEST_QUERY_PROMPT))
            request_mock.assert_called_with(
                "post",
                f"{_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}:query",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME},
                    "classMethod": "async_query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    def test_query_agent_engine_stream(self):
        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client, "request_streamed"
        ) as request_mock:
            agent = self.client.agent_engines.runtimes.revisions._register_api_methods(
                agent_engine_runtime_revision=_genai_types.AgentEngineRuntimeRevision(
                    api_client=self.client.agent_engines.runtimes.revisions,
                    api_resource=_genai_types.ReasoningEngineRuntimeRevision(
                        name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
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
                f"{_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}:streamQuery?alt=sse",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME},
                    "classMethod": "stream_query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )

    def test_query_agent_engine_async_stream(self):
        async def mock_async_generator():
            yield genai_types.HttpResponse(body=b"")

        with mock.patch.object(
            self.client.agent_engines.runtimes.revisions._api_client,
            "async_request_streamed",
        ) as request_mock:
            request_mock.return_value = mock_async_generator()
            agent = self.client.agent_engines.runtimes.revisions._register_api_methods(
                agent_engine_runtime_revision=_genai_types.AgentEngineRuntimeRevision(
                    api_client=self.client.agent_engines.runtimes.revisions,
                    api_resource=_genai_types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
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
                    assert isinstance(response, genai_types.HttpResponse)

            asyncio.run(consume())
            request_mock.assert_called_with(
                "post",
                f"{_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}:streamQuery?alt=sse",
                {
                    "_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME},
                    "classMethod": "async_stream_query",
                    "input": {"query": _TEST_QUERY_PROMPT},
                },
                None,
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestAsyncRuntimeRevisions:
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

    def test_delete_runtime_revision(self):
        with mock.patch.object(
            self.client.aio.agent_engines.runtimes.revisions._api_client,
            "async_request",
        ) as request_mock:
            request_mock.side_effect = [
                # First call: response to delete.
                genai_types.HttpResponse(body=""),
                # Second call: response to GET operation.
                genai_types.HttpResponse(
                    body=json.dumps(
                        {
                            "name": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                            "done": True,
                        }
                    ),
                ),
            ]
            asyncio.run(
                self.client.aio.agent_engines.runtimes.revisions.delete(
                    name=_TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME
                )
            )
            request_mock.call_args_list[0].assert_called_with(
                "delete",
                _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME,
                {"_url": {"name": _TEST_AGENT_ENGINE_RUNTIME_REVISION_RESOURCE_NAME}},
                None,
            )

            request_mock.call_args_list[1].assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_REVISION_OPERATION_NAME}},
                None,
            )
