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
import base64
import importlib
import io
import json
import logging
import os
import sys
import tarfile
import tempfile
from typing import Any, AsyncIterable, Dict, Iterable, List
from unittest import mock
from urllib.parse import urlencode

from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform import initializer
from vertexai.agent_engines.templates import adk
from vertexai._genai import _agent_engines_utils
from vertexai._genai import agent_engines
from vertexai._genai import types as _genai_types
from google.genai import client as genai_client
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
_TEST_OPERATION_ID = "4589432830794137600"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_AGENT_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_AGENT_ENGINE_OPERATION_NAME = f"{_TEST_PARENT}/operations/{_TEST_OPERATION_ID}"
_TEST_AGENT_ENGINE_DISPLAY_NAME = "Agent Engine Display Name"
_TEST_AGENT_ENGINE_DESCRIPTION = "Agent Engine Description"
_TEST_AGENT_ENGINE_LIST_FILTER = f'display_name="{_TEST_AGENT_ENGINE_DISPLAY_NAME}"'
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
    service_account=_TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
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

    @mock.patch.object(_agent_engines_utils, "_prepare")
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

    @mock.patch.object(_agent_engines_utils, "_prepare")
    @pytest.mark.parametrize(
        "env_vars,expected_env_vars",
        [
            ({}, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (None, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (
                {"some_env": "some_val"},
                {
                    "some_env": "some_val",
                    GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified",
                },
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
            ),
        ],
    )
    def test_agent_engine_adk_telemetry_enablement(
        self,
        mock_prepare: mock.Mock,
        env_vars: dict[str, str],
        expected_env_vars: dict[str, str],
    ):
        agent = mock.Mock(spec=adk.AdkApp)
        agent.clone = lambda: agent
        agent.register_operations = lambda: {}

        config = self.client.agent_engines._create_config(
            mode="create",
            agent=agent,
            staging_bucket=_TEST_STAGING_BUCKET,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
            env_vars=env_vars,
        )
        assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
        assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
        assert config["spec"]["deployment_spec"]["env"] == [
            {"name": key, "value": value} for key, value in expected_env_vars.items()
        ]

    @mock.patch.object(_agent_engines_utils, "_prepare")
    @pytest.mark.parametrize(
        "env_vars,expected_env_vars",
        [
            ({}, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (None, {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified"}),
            (
                {"some_env": "some_val"},
                {
                    "some_env": "some_val",
                    GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "unspecified",
                },
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "true"},
            ),
            (
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
                {GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY: "false"},
            ),
        ],
    )
    def test_agent_engine_adk_telemetry_enablement_through_source_packages(
        self,
        mock_prepare: mock.Mock,
        env_vars: dict[str, str],
        expected_env_vars: dict[str, str],
    ):
        config = self.client.agent_engines._create_config(
            mode="create",
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
            source_packages=[],
            class_methods=[],
            entrypoint_module=".",
            entrypoint_object=".",
            env_vars=env_vars,
            agent_framework="google-adk",
        )
        assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
        assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
        assert config["spec"]["deployment_spec"]["env"] == [
            {"name": key, "value": value} for key, value in expected_env_vars.items()
        ]

    @mock.patch.object(_agent_engines_utils, "_prepare")
    def test_create_agent_engine_config_full(self, mock_prepare):
        config = self.client.agent_engines._create_config(
            mode="create",
            agent=self.test_agent,
            staging_bucket=_TEST_STAGING_BUCKET,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
            gcs_dir_name=_TEST_GCS_DIR_NAME,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
            service_account=_TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
            identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
            psc_interface_config=_TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG,
            min_instances=_TEST_AGENT_ENGINE_MIN_INSTANCES,
            max_instances=_TEST_AGENT_ENGINE_MAX_INSTANCES,
            resource_limits=_TEST_AGENT_ENGINE_RESOURCE_LIMITS,
            container_concurrency=_TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY,
            encryption_spec=_TEST_AGENT_ENGINE_ENCRYPTION_SPEC,
            python_version=_TEST_PYTHON_VERSION_OVERRIDE,
        )
        assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
        assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
        assert config["spec"]["agent_framework"] == "custom"
        assert config["spec"]["package_spec"] == {
            "python_version": _TEST_PYTHON_VERSION_OVERRIDE,
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
            "psc_interface_config": _TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG,
            "min_instances": _TEST_AGENT_ENGINE_MIN_INSTANCES,
            "max_instances": _TEST_AGENT_ENGINE_MAX_INSTANCES,
            "resource_limits": _TEST_AGENT_ENGINE_RESOURCE_LIMITS,
            "container_concurrency": _TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY,
        }
        assert config["encryption_spec"] == _TEST_AGENT_ENGINE_ENCRYPTION_SPEC
        assert config["spec"]["class_methods"] == [_TEST_AGENT_ENGINE_CLASS_METHOD_1]
        assert (
            config["spec"]["service_account"]
            == _TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT
        )
        assert (
            config["spec"]["identity_type"]
            == _TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT
        )

    @mock.patch.object(
        _agent_engines_utils,
        "_create_base64_encoded_tarball",
        return_value="test_tarball",
    )
    def test_create_agent_engine_config_with_source_packages(
        self, mock_create_base64_encoded_tarball
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file_path = os.path.join(tmpdir, "test_file.txt")
            with open(test_file_path, "w") as f:
                f.write("test content")
            requirements_file_path = os.path.join(tmpdir, "requirements.txt")
            with open(requirements_file_path, "w") as f:
                f.write("requests==2.0.0")

            config = self.client.agent_engines._create_config(
                mode="create",
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=_TEST_AGENT_ENGINE_DESCRIPTION,
                source_packages=[test_file_path],
                entrypoint_module="main",
                entrypoint_object="app",
                requirements_file=requirements_file_path,
                class_methods=_TEST_AGENT_ENGINE_CLASS_METHODS,
                agent_framework=_TEST_AGENT_FRAMEWORK,
                identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
                python_version=_TEST_PYTHON_VERSION_OVERRIDE,
            )
            assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
            assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
            assert config["spec"]["agent_framework"] == _TEST_AGENT_FRAMEWORK
            assert config["spec"]["source_code_spec"] == {
                "inline_source": {"source_archive": "test_tarball"},
                "python_spec": {
                    "version": _TEST_PYTHON_VERSION_OVERRIDE,
                    "entrypoint_module": "main",
                    "entrypoint_object": "app",
                    "requirements_file": requirements_file_path,
                },
            }
            assert config["spec"]["class_methods"] == _TEST_AGENT_ENGINE_CLASS_METHODS
            mock_create_base64_encoded_tarball.assert_called_once_with(
                source_packages=[test_file_path]
            )
            assert (
                config["spec"]["identity_type"]
                == _TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT
            )

    @mock.patch.object(
        _agent_engines_utils,
        "_create_base64_encoded_tarball",
        return_value="test_tarball",
    )
    @mock.patch.object(_agent_engines_utils, "_validate_packages_or_raise")
    def test_create_agent_engine_config_with_source_packages_and_build_options(
        self, mock_validate_packages, mock_create_base64_encoded_tarball
    ):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file_path = os.path.join(tmpdir, "main.py")
            with open(test_file_path, "w") as f:
                f.write("app = None")
            build_options = {
                "installation_scripts": ["installation_scripts/install.sh"]
            }
            source_packages = [test_file_path, "installation_scripts/install.sh"]
            mock_validate_packages.return_value = source_packages

            self.client.agent_engines._create_config(
                mode="create",
                source_packages=source_packages,
                entrypoint_module="main",
                entrypoint_object="app",
                build_options=build_options,
                class_methods=_TEST_AGENT_ENGINE_CLASS_METHODS,
            )
            mock_validate_packages.assert_called_once_with(
                packages=source_packages,
                build_options=build_options,
            )

    @mock.patch.object(_agent_engines_utils, "_prepare")
    @mock.patch.object(_agent_engines_utils, "_validate_packages_or_raise")
    def test_create_agent_engine_config_with_build_options(
        self, mock_validate_packages, mock_prepare
    ):
        build_options = {"installation_scripts": ["install.sh"]}
        extra_packages = ["install.sh"]

        self.client.agent_engines._create_config(
            mode="create",
            agent=self.test_agent,
            staging_bucket=_TEST_STAGING_BUCKET,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            extra_packages=extra_packages,
            build_options=build_options,
        )

        mock_validate_packages.assert_called_once_with(
            packages=extra_packages,
            build_options=build_options,
        )

    @mock.patch.object(_agent_engines_utils, "_prepare")
    def test_update_agent_engine_config_full(self, mock_prepare):
        config = self.client.agent_engines._create_config(
            mode="update",
            agent=self.test_agent,
            staging_bucket=_TEST_STAGING_BUCKET,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
            gcs_dir_name=_TEST_GCS_DIR_NAME,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
            service_account=_TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
            identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
            python_version=_TEST_PYTHON_VERSION_OVERRIDE,
        )
        assert config["display_name"] == _TEST_AGENT_ENGINE_DISPLAY_NAME
        assert config["description"] == _TEST_AGENT_ENGINE_DESCRIPTION
        assert config["spec"]["agent_framework"] == "custom"
        assert config["spec"]["package_spec"] == {
            "python_version": _TEST_PYTHON_VERSION_OVERRIDE,
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
        assert (
            config["spec"]["service_account"]
            == _TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT
        )
        assert (
            config["spec"]["identity_type"]
            == _TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT
        )
        assert config["update_mask"] == ",".join(
            [
                "display_name",
                "description",
                "spec.package_spec.pickle_object_gcs_uri",
                "spec.package_spec.dependency_files_gcs_uri",
                "spec.package_spec.requirements_gcs_uri",
                "spec.class_methods",
                "spec.deployment_spec.env",
                "spec.deployment_spec.secret_env",
                "spec.agent_framework",
                "spec.identity_type",
                "spec.service_account",
            ]
        )

    @mock.patch.object(_agent_engines_utils, "_prepare")
    def test_update_agent_engine_clear_service_account(self, mock_prepare):
        config = self.client.agent_engines._create_config(
            mode="update",
            service_account="",
            identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
        )
        assert "service_account" not in config["spec"].keys()
        assert (
            config["spec"]["identity_type"]
            == _TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT
        )
        assert config["update_mask"] == ",".join(
            [
                "spec.identity_type",
                "spec.service_account",
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
            operation = _agent_engines_utils._await_operation(
                operation_name=_TEST_AGENT_ENGINE_OPERATION_NAME,
                get_operation_fn=self.client.agent_engines._get_agent_operation,
            )
            request_mock.assert_called_with(
                "get",
                _TEST_AGENT_ENGINE_OPERATION_NAME,
                {"_url": {"operationName": _TEST_AGENT_ENGINE_OPERATION_NAME}},
                None,
            )
            assert isinstance(operation, _genai_types.AgentEngineOperation)

    def test_register_api_methods(self):
        agent = self.client.agent_engines._register_api_methods(
            agent_engine=_genai_types.AgentEngine(
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

    @pytest.mark.usefixtures("caplog")
    def test_invalid_requirement_warning(self, caplog):
        _agent_engines_utils._parse_constraints(
            constraints=["invalid requirement line"],
        )
        assert "Failed to parse constraint" in caplog.text

    def test_requirements_with_whl_files(self):
        whl_files = [
            "wxPython-4.2.4-cp39-cp39-macosx_12_0_x86_64.whl",
            "/content/wxPython-4.2.3-cp39-cp39-macosx_12_0_x86_64.whl",
            "https://wxpython.org/Phoenix/snapshot-builds/wxPython-4.2.2-cp38-cp38-macosx_12_0_x86_64.whl",
        ]
        result = _agent_engines_utils._parse_constraints(
            constraints=whl_files,
        )
        assert result == {
            "wxPython-4.2.2-cp38-cp38-macosx_12_0_x86_64.whl": None,
            "wxPython-4.2.3-cp39-cp39-macosx_12_0_x86_64.whl": None,
            "wxPython-4.2.4-cp39-cp39-macosx_12_0_x86_64.whl": None,
        }

    def test_compare_requirements_with_required_packages(self):
        requirements = {"requests": "2.0.0"}
        constraints = ["requests==1.0.0"]
        result = _agent_engines_utils._compare_requirements(
            requirements=requirements,
            constraints=constraints,
        )
        assert result == {
            "actions": {"append": set()},
            "warnings": {
                "incompatible": {"requests==2.0.0 (required: ==1.0.0)"},
                "missing": set(),
            },
        }

    @pytest.mark.usefixtures("importlib_metadata_version_mock")
    def test_scan_simple_object(self):
        """Test scanning an object importing a known third-party package."""
        fake_obj = _create_fake_object_with_module("requests")
        requirements = _agent_engines_utils._scan_requirements(
            obj=fake_obj,
            package_distributions=_TEST_PACKAGE_DISTRIBUTIONS,
        )
        assert requirements == {
            "cloudpickle": "3.0.0",
            "pydantic": "1.11.1",
            "requests": "2.0.0",
        }

    @pytest.mark.usefixtures("importlib_metadata_version_mock")
    def test_scan_object_with_stdlib_module(self):
        """Test that stdlib modules are ignored by default."""
        fake_obj_stdlib = _create_fake_object_with_module("json")
        requirements = _agent_engines_utils._scan_requirements(
            obj=fake_obj_stdlib,
            package_distributions=_TEST_PACKAGE_DISTRIBUTIONS,
        )
        # Requirements should not contain 'json',
        # because 'json' is a stdlib module.
        assert requirements == {
            "cloudpickle": "3.0.0",
            "pydantic": "1.11.1",
        }

    @pytest.mark.usefixtures("importlib_metadata_version_mock")
    def test_scan_with_default_ignore_modules(self, monkeypatch):
        """Test implicitly ignoring a module."""
        fake_obj = _create_fake_object_with_module("requests")
        original_base = _agent_engines_utils._BASE_MODULES
        monkeypatch.setattr(
            _agent_engines_utils,
            "_BASE_MODULES",
            set(original_base) | {"requests"},
        )
        requirements = _agent_engines_utils._scan_requirements(
            obj=fake_obj,
            package_distributions=_TEST_PACKAGE_DISTRIBUTIONS,
        )
        # Requirements should not contain 'requests',
        # because 'requests' is implicitly ignored in `_BASE_MODULES`.
        assert requirements == {
            "cloudpickle": "3.0.0",
            "pydantic": "1.11.1",
        }

    @pytest.mark.usefixtures("importlib_metadata_version_mock")
    def test_scan_with_explicit_ignore_modules(self):
        """Test explicitly ignoring a module."""
        fake_obj = _create_fake_object_with_module("requests")
        requirements = _agent_engines_utils._scan_requirements(
            obj=fake_obj,
            ignore_modules=["requests"],
            package_distributions=_TEST_PACKAGE_DISTRIBUTIONS,
        )
        # Requirements should not contain 'requests',
        # because 'requests' is explicitly ignored in `ignore_modules`.
        assert requirements == {
            "cloudpickle": "3.0.0",
            "pydantic": "1.11.1",
        }

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "obj, expected",
        [
            (
                # "valid_json",
                genai_types.HttpResponse(body='{"a": 1, "b": "hello"}'),
                [{"a": 1, "b": "hello"}],
            ),
            (
                # "invalid_json",
                genai_types.HttpResponse(body='{"a": 1, "b": "hello"'),
                ['{"a": 1, "b": "hello"'],  # returns the unparsed string
            ),
            (
                # "nil_body",
                genai_types.HttpResponse(body=None),
                [None],
            ),
            (
                # "empty_data",
                genai_types.HttpResponse(body=""),
                [None],
            ),
            (
                # "nested_json",
                genai_types.HttpResponse(body='{"a": {"b": 1}}'),
                [{"a": {"b": 1}}],
            ),
            (
                # "multiline_json",
                genai_types.HttpResponse(body='{"a": {"b": 1}}\n{"a": {"b": 2}}'),
                [{"a": {"b": 1}}, {"a": {"b": 2}}],
            ),
        ],
    )
    def test_to_parsed_json(self, obj, expected):
        for got, want in zip(_agent_engines_utils._yield_parsed_json(obj), expected):
            assert got == want

    def test_create_base64_encoded_tarball(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file_path = os.path.join(tmpdir, "test_file.txt")
            with open(test_file_path, "w") as f:
                f.write("test content")

            origin_dir = os.getcwd()
            try:
                os.chdir(tmpdir)
                encoded_tarball = _agent_engines_utils._create_base64_encoded_tarball(
                    source_packages=["test_file.txt"]
                )
            finally:
                os.chdir(origin_dir)

            decoded_tarball = base64.b64decode(encoded_tarball)
            with tarfile.open(fileobj=io.BytesIO(decoded_tarball), mode="r:gz") as tar:
                names = tar.getnames()
                assert "test_file.txt" in names

    def test_create_base64_encoded_tarball_outside_project_dir_raises(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_dir = os.path.join(tmpdir, "project")
            os.makedirs(project_dir)
            sibling_path = os.path.join(tmpdir, "sibling.txt")
            with open(sibling_path, "w") as f:
                f.write("test content")

            origin_dir = os.getcwd()
            try:
                os.chdir(project_dir)
                with pytest.raises(ValueError) as excinfo:
                    _agent_engines_utils._create_base64_encoded_tarball(
                        source_packages=["../sibling.txt"]
                    )
                assert "is outside the project directory" in str(excinfo.value)
            finally:
                os.chdir(origin_dir)


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

    @pytest.mark.usefixtures("caplog")
    @mock.patch.object(_agent_engines_utils, "_prepare")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine(self, mock_await_operation, mock_prepare, caplog):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        caplog.set_level(logging.INFO, logger="vertexai_genai.agentengines")
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent=self.test_agent,
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
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "class_methods": mock.ANY,  # dict ordering was too flakey
                        "deployment_spec": _TEST_AGENT_ENGINE_SPEC.get(
                            "deployment_spec"
                        ),
                        "package_spec": _TEST_AGENT_ENGINE_SPEC.get("package_spec"),
                    },
                },
                None,
            )
            assert "View progress and logs at" in caplog.text
            assert "Agent Engine created. To use it in another session:" in caplog.text
            assert (
                f"agent_engine=client.agent_engines.get(name="
                f"'{_TEST_AGENT_ENGINE_RESOURCE_NAME}')" in caplog.text
            )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_lightweight(
        self,
        mock_await_operation,
        mock_create_config,
    ):
        mock_create_config.return_value = _genai_types.CreateAgentEngineConfig(
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
        )
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
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
    @mock.patch.object(_agent_engines_utils, "_await_operation")
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
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent=self.test_agent,
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
                agent=self.test_agent,
                staging_bucket=_TEST_STAGING_BUCKET,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=None,
                gcs_dir_name=None,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                env_vars=_TEST_AGENT_ENGINE_ENV_VARS_INPUT,
                service_account=None,
                identity_type=None,
                context_spec=None,
                psc_interface_config=None,
                min_instances=None,
                max_instances=None,
                resource_limits=None,
                container_concurrency=None,
                encryption_spec=None,
                agent_server_mode=None,
                labels=None,
                class_methods=None,
                source_packages=None,
                entrypoint_module=None,
                entrypoint_object=None,
                requirements_file=None,
                agent_framework=None,
                python_version=None,
                build_options=None,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "class_methods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
                        "package_spec": {
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "python_version": _TEST_PYTHON_VERSION,
                            "requirements_gcs_uri": (
                                _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI
                            ),
                        },
                    },
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_with_custom_service_account(
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
                "service_account": _TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
                "identity_type": _TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
                "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
            },
        }
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                    staging_bucket=_TEST_STAGING_BUCKET,
                    service_account=_TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
                    identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
                ),
            )
            mock_create_config.assert_called_with(
                mode="create",
                agent=self.test_agent,
                staging_bucket=_TEST_STAGING_BUCKET,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=None,
                gcs_dir_name=None,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                env_vars=None,
                service_account=_TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
                identity_type=_TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
                context_spec=None,
                psc_interface_config=None,
                min_instances=None,
                max_instances=None,
                resource_limits=None,
                container_concurrency=None,
                encryption_spec=None,
                labels=None,
                agent_server_mode=None,
                class_methods=None,
                source_packages=None,
                entrypoint_module=None,
                entrypoint_object=None,
                requirements_file=None,
                agent_framework=None,
                python_version=None,
                build_options=None,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "class_methods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
                        "package_spec": {
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "python_version": _TEST_PYTHON_VERSION,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                        "service_account": _TEST_AGENT_ENGINE_CUSTOM_SERVICE_ACCOUNT,
                        "identity_type": _TEST_AGENT_ENGINE_IDENTITY_TYPE_SERVICE_ACCOUNT,
                    },
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_with_experimental_mode(
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
                "deployment_spec": {
                    "agent_server_mode": _genai_types.AgentServerMode.EXPERIMENTAL,
                },
                "class_methods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
            },
        }
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                    staging_bucket=_TEST_STAGING_BUCKET,
                    agent_server_mode=_genai_types.AgentServerMode.EXPERIMENTAL,
                ),
            )
            mock_create_config.assert_called_with(
                mode="create",
                agent=self.test_agent,
                staging_bucket=_TEST_STAGING_BUCKET,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=None,
                gcs_dir_name=None,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                env_vars=None,
                service_account=None,
                identity_type=None,
                context_spec=None,
                psc_interface_config=None,
                min_instances=None,
                max_instances=None,
                resource_limits=None,
                container_concurrency=None,
                encryption_spec=None,
                labels=None,
                agent_server_mode=_genai_types.AgentServerMode.EXPERIMENTAL,
                class_methods=None,
                source_packages=None,
                entrypoint_module=None,
                entrypoint_object=None,
                requirements_file=None,
                agent_framework=None,
                python_version=None,
                build_options=None,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "class_methods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
                        "deployment_spec": {
                            "agent_server_mode": _genai_types.AgentServerMode.EXPERIMENTAL,
                        },
                        "package_spec": {
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "python_version": _TEST_PYTHON_VERSION,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                },
                None,
            )

    @mock.patch.object(
        _agent_engines_utils,
        "_create_base64_encoded_tarball",
        return_value="test_tarball",
    )
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_with_source_packages(
        self,
        mock_await_operation,
        mock_create_base64_encoded_tarball,
    ):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file_path = os.path.join(tmpdir, "test_file.txt")
            with open(test_file_path, "w") as f:
                f.write("test content")
            requirements_file_path = os.path.join(tmpdir, "requirements.txt")
            with open(requirements_file_path, "w") as f:
                f.write("requests==2.0.0")

            with mock.patch.object(
                self.client.agent_engines._api_client, "request"
            ) as request_mock:
                request_mock.return_value = genai_types.HttpResponse(body="")
                self.client.agent_engines.create(
                    config=_genai_types.AgentEngineConfig(
                        display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                        description=_TEST_AGENT_ENGINE_DESCRIPTION,
                        source_packages=[test_file_path],
                        entrypoint_module="main",
                        entrypoint_object="app",
                        requirements_file=requirements_file_path,
                        class_methods=_TEST_AGENT_ENGINE_CLASS_METHODS,
                    ),
                )
                request_mock.assert_called_with(
                    "post",
                    "reasoningEngines",
                    {
                        "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                        "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                        "spec": {
                            "agent_framework": "custom",
                            "source_code_spec": {
                                "inline_source": {"source_archive": "test_tarball"},
                                "python_spec": {
                                    "version": _TEST_PYTHON_VERSION,
                                    "entrypoint_module": "main",
                                    "entrypoint_object": "app",
                                    "requirements_file": requirements_file_path,
                                },
                            },
                            "class_methods": _TEST_AGENT_ENGINE_CLASS_METHODS,
                        },
                    },
                    None,
                )
                mock_create_base64_encoded_tarball.assert_called_once_with(
                    source_packages=[test_file_path]
                )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_with_class_methods(
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
                "class_methods": _TEST_AGENT_ENGINE_CLASS_METHODS,
            },
        }
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                    staging_bucket=_TEST_STAGING_BUCKET,
                    class_methods=_TEST_AGENT_ENGINE_CLASS_METHODS,
                ),
            )
            mock_create_config.assert_called_with(
                mode="create",
                agent=self.test_agent,
                staging_bucket=_TEST_STAGING_BUCKET,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=None,
                gcs_dir_name=None,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                env_vars=None,
                service_account=None,
                identity_type=None,
                context_spec=None,
                psc_interface_config=None,
                min_instances=None,
                max_instances=None,
                resource_limits=None,
                container_concurrency=None,
                encryption_spec=None,
                labels=None,
                agent_server_mode=None,
                class_methods=_TEST_AGENT_ENGINE_CLASS_METHODS,
                source_packages=None,
                entrypoint_module=None,
                entrypoint_object=None,
                requirements_file=None,
                agent_framework=None,
                python_version=None,
                build_options=None,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "class_methods": _TEST_AGENT_ENGINE_CLASS_METHODS,
                        "package_spec": {
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "python_version": _TEST_PYTHON_VERSION,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                },
                None,
            )

    @mock.patch.object(agent_engines.AgentEngines, "_create_config")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_with_agent_framework(
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
                "agent_framework": _TEST_AGENT_FRAMEWORK,
            },
        }
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.create(
                agent=self.test_agent,
                config=_genai_types.AgentEngineConfig(
                    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                    extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                    staging_bucket=_TEST_STAGING_BUCKET,
                    agent_framework=_TEST_AGENT_FRAMEWORK,
                ),
            )
            mock_create_config.assert_called_with(
                mode="create",
                agent=self.test_agent,
                staging_bucket=_TEST_STAGING_BUCKET,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                description=None,
                gcs_dir_name=None,
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
                env_vars=None,
                service_account=None,
                context_spec=None,
                psc_interface_config=None,
                min_instances=None,
                max_instances=None,
                resource_limits=None,
                container_concurrency=None,
                encryption_spec=None,
                labels=None,
                agent_server_mode=None,
                class_methods=None,
                source_packages=None,
                entrypoint_module=None,
                entrypoint_object=None,
                requirements_file=None,
                agent_framework=_TEST_AGENT_FRAMEWORK,
                identity_type=None,
                python_version=None,
                build_options=None,
            )
            request_mock.assert_called_with(
                "post",
                "reasoningEngines",
                {
                    "displayName": _TEST_AGENT_ENGINE_DISPLAY_NAME,
                    "description": _TEST_AGENT_ENGINE_DESCRIPTION,
                    "spec": {
                        "agent_framework": _TEST_AGENT_FRAMEWORK,
                        "class_methods": [_TEST_AGENT_ENGINE_CLASS_METHOD_1],
                        "package_spec": {
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "python_version": _TEST_PYTHON_VERSION,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                },
                None,
            )

    @pytest.mark.usefixtures("caplog")
    @mock.patch.object(_agent_engines_utils, "_prepare")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_update_agent_engine_requirements(
        self, mock_await_operation, mock_prepare, caplog
    ):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        caplog.set_level(logging.INFO, logger="vertexai_genai.agentengines")
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                agent=self.test_agent,
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
                        "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "class_methods": mock.ANY,
                        "package_spec": {
                            "python_version": _TEST_PYTHON_VERSION,
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                    },
                    "_query": {"updateMask": update_mask},
                },
                None,
            )
            assert "Agent Engine updated. To use it in another session:" in caplog.text
            assert (
                f"agent_engine=client.agent_engines.get("
                f"name='{_TEST_AGENT_ENGINE_RESOURCE_NAME}')" in caplog.text
            )

    @mock.patch.object(_agent_engines_utils, "_prepare")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_update_agent_engine_extra_packages(
        self, mock_await_operation, mock_prepare
    ):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                agent=self.test_agent,
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
                        "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "class_methods": mock.ANY,
                        "package_spec": {
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

    @mock.patch.object(_agent_engines_utils, "_prepare")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_update_agent_engine_env_vars(
        self, mock_await_operation, mock_prepare, caplog
    ):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            self.client.agent_engines.update(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                agent=self.test_agent,
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
                    "spec.class_methods",
                    "spec.deployment_spec.env",
                    "spec.deployment_spec.secret_env",
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
                        "agent_framework": _TEST_AGENT_ENGINE_FRAMEWORK,
                        "class_methods": mock.ANY,
                        "package_spec": {
                            "python_version": _TEST_PYTHON_VERSION,
                            "pickle_object_gcs_uri": _TEST_AGENT_ENGINE_GCS_URI,
                            "requirements_gcs_uri": _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI,
                        },
                        "deployment_spec": _TEST_AGENT_ENGINE_SPEC.get(
                            "deployment_spec"
                        ),
                    },
                    "_query": {"updateMask": update_mask},
                },
                None,
            )

    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_update_agent_engine_display_name(self, mock_await_operation):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
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

    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_update_agent_engine_description(self, mock_await_operation):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            response=_genai_types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=_TEST_AGENT_ENGINE_SPEC,
            )
        )
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
                agent_engine=_genai_types.AgentEngine(
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
            agent_engine=_genai_types.AgentEngine(
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
                agent_engine=_genai_types.AgentEngine(
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
        async def mock_async_generator():
            yield genai_types.HttpResponse(body=b"")

        with mock.patch.object(
            self.client.agent_engines._api_client, "async_request_streamed"
        ) as request_mock:
            request_mock.return_value = mock_async_generator()
            agent = self.client.agent_engines._register_api_methods(
                agent_engine=_genai_types.AgentEngine(
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
                        _agent_engines_utils._generate_schema(
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
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().query,
                            schema_name=_TEST_DEFAULT_METHOD_NAME,
                        ),
                        _TEST_STANDARD_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().custom_method,
                            schema_name=_TEST_CUSTOM_METHOD_NAME,
                        ),
                        _TEST_STANDARD_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().async_query,
                            schema_name=_TEST_DEFAULT_ASYNC_METHOD_NAME,
                        ),
                        _TEST_ASYNC_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().custom_async_method,
                            schema_name=_TEST_CUSTOM_ASYNC_METHOD_NAME,
                        ),
                        _TEST_ASYNC_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().stream_query,
                            schema_name=_TEST_DEFAULT_STREAM_METHOD_NAME,
                        ),
                        _TEST_STREAM_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().custom_stream_method,
                            schema_name=_TEST_CUSTOM_STREAM_METHOD_NAME,
                        ),
                        _TEST_STREAM_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().async_stream_query,
                            schema_name=_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
                        ),
                        _TEST_ASYNC_STREAM_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().custom_async_stream_method,
                            schema_name=_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
                        ),
                        _TEST_ASYNC_STREAM_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().bidi_stream_query,
                            schema_name=_TEST_DEFAULT_BIDI_STREAM_METHOD_NAME,
                        ),
                        _TEST_BIDI_STREAM_API_MODE,
                    ),
                    (
                        _agent_engines_utils._generate_schema(
                            OperationRegistrableEngine().custom_bidi_stream_method,
                            schema_name=_TEST_CUSTOM_BIDI_STREAM_METHOD_NAME,
                        ),
                        _TEST_BIDI_STREAM_API_MODE,
                    ),
                ],
            ),
            (
                "Operation Not Registered Engine",
                _TEST_OPERATION_NOT_REGISTERED_SCHEMAS,
                [
                    (
                        _agent_engines_utils._generate_schema(
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

    @mock.patch.object(_agent_engines_utils, "_prepare")
    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_create_agent_engine_error(self, mock_await_operation, mock_prepare):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            error=_TEST_AGENT_ENGINE_ERROR,
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            with pytest.raises(RuntimeError) as excinfo:
                self.client.agent_engines.create(
                    agent=self.test_agent,
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
                assert "Failed to create agent engine" in str(excinfo.value)

    @mock.patch.object(_agent_engines_utils, "_await_operation")
    def test_update_agent_engine_description(self, mock_await_operation):
        mock_await_operation.return_value = _genai_types.AgentEngineOperation(
            error=_TEST_AGENT_ENGINE_ERROR,
        )
        with mock.patch.object(
            self.client.agent_engines._api_client, "request"
        ) as request_mock:
            request_mock.return_value = genai_types.HttpResponse(body="")
            with pytest.raises(RuntimeError) as excinfo:
                self.client.agent_engines.update(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    config=_genai_types.AgentEngineConfig(
                        description=_TEST_AGENT_ENGINE_DESCRIPTION,
                    ),
                )
                assert "Failed to update agent engine" in str(excinfo.value)

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
                    "Supported modes are: ``, `a2a_extension`, `async`, `async_stream`, `stream`.}"
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("caplog")
    @mock.patch.object(agent_engines.AgentEngines, "_get")
    def test_invalid_operation_schema(
        self,
        mock_get,
        test_case_name,
        test_operation_schemas,
        want_log_output,
        caplog,
    ):
        mock_get.return_value = _genai_types.ReasoningEngine(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            spec=_genai_types.ReasoningEngineSpec(class_methods=test_operation_schemas),
        )
        self.client.agent_engines.get(name=_TEST_AGENT_ENGINE_RESOURCE_NAME)
        assert want_log_output in caplog.text

    @pytest.mark.parametrize(
        "resource_limits, expected_exception, expected_message",
        [
            (
                "Not a dict",
                TypeError,
                "resource_limits must be a dict",
            ),
            (
                {"cpu": "1"},
                KeyError,
                "resource_limits must contain 'cpu' and 'memory' keys.",
            ),
            (
                {"memory": "1Gi"},
                KeyError,
                "resource_limits must contain 'cpu' and 'memory' keys.",
            ),
            (
                {"cpu": "3", "memory": "1Gi"},
                ValueError,
                "resource_limits['cpu'] must be one of 1, 2, 4, 6, 8.",
            ),
            (
                {"cpu": "1", "memory": "1G"},
                ValueError,
                "resource_limits['memory'] must be a string ending with 'Gi'.",
            ),
            (
                {"cpu": "1", "memory": "XGi"},
                ValueError,
                "Invalid memory value: XGi.",
            ),
            (
                {"cpu": "1", "memory": "33Gi"},
                ValueError,
                "Memory size of 33Gi is too large. Must be smaller than 32Gi.",
            ),
            (
                {"cpu": "1", "memory": "8Gi"},
                ValueError,
                "Memory size of 8Gi requires at least 2 CPUs.",
            ),
            (
                {"cpu": "2", "memory": "16Gi"},
                ValueError,
                "Memory size of 16Gi requires at least 4 CPUs.",
            ),
            (
                {"cpu": "4", "memory": "24Gi"},
                ValueError,
                "Memory size of 24Gi requires at least 6 CPUs.",
            ),
            (
                {"cpu": "6", "memory": "32Gi"},
                ValueError,
                "Memory size of 32Gi requires at least 8 CPUs.",
            ),
        ],
    )
    def test_validate_resource_limits_or_raise(
        self, resource_limits, expected_exception, expected_message
    ):
        with pytest.raises(expected_exception) as excinfo:
            _agent_engines_utils._validate_resource_limits_or_raise(resource_limits)
        assert expected_message in str(excinfo.value)


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
            self.client.aio.agent_engines._api_client, "async_request"
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
            self.client.aio.agent_engines._api_client, "async_request"
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
