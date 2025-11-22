# Copyright 2023 Google LLC
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
import cloudpickle
import difflib
import importlib
import os
import pytest
import sys
import tarfile
import tempfile
from typing import Any, AsyncIterable, Dict, Iterable, List, Optional
from unittest import mock

import proto

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1 import types
from google.cloud.aiplatform_v1.services import (
    reasoning_engine_execution_service,
)
from google.cloud.aiplatform_v1.services import reasoning_engine_service
from vertexai import agent_engines
from vertexai.agent_engines import _agent_engines
from vertexai.agent_engines import _utils
from google.api import httpbody_pb2
from google.protobuf import field_mask_pb2
from google.protobuf import struct_pb2


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


class BidiStreamQueryEngine:
    """A sample Agent Engine that implements `bidi_stream_query`."""

    def set_up(self):
        pass

    async def bidi_stream_query(self, unused_request_queue) -> AsyncIterable[Any]:
        """Runs the bidi stream engine."""
        raise NotImplementedError()

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

    async def bidi_stream_query(self, unused_request_queue) -> AsyncIterable[Any]:
        """Runs the bidi stream engine."""
        raise NotImplementedError()

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

    async def custom_bidi_stream_method(
        self, unused_request_queue
    ) -> AsyncIterable[Any]:
        """Runs the bidi stream engine."""
        raise NotImplementedError()

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


_TEST_RETRY = base._DEFAULT_RETRY
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
_TEST_INPUT_AGENT_ENGINE_OBJ = types.ReasoningEngine(
    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
        agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
    ),
)
_TEST_INPUT_AGENT_ENGINE_OBJ.spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
_TEST_AGENT_ENGINE_OBJ = types.ReasoningEngine(
    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
    display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
        agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
    ),
)
_TEST_AGENT_ENGINE_OBJ.spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
_TEST_UPDATE_AGENT_ENGINE_OBJ = types.ReasoningEngine(
    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=types.ReasoningEngineSpec.PackageSpec(
            pickle_object_gcs_uri=_TEST_AGENT_ENGINE_GCS_URI,
        ),
        agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
    ),
)
_TEST_UPDATE_AGENT_ENGINE_OBJ.spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
_TEST_AGENT_ENGINE_QUERY_REQUEST = types.QueryReasoningEngineRequest(
    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
    input={_TEST_DEFAULT_METHOD_NAME: _TEST_QUERY_PROMPT},
    class_method=_TEST_DEFAULT_METHOD_NAME,
)
_TEST_AGENT_ENGINE_QUERY_RESPONSE = types.QueryReasoningEngineResponse(
    output=_utils.to_proto({"output": "hey there"}),
)
_TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE = [
    httpbody_pb2.HttpBody(content_type="application/json", data=b'{"output": "hello"}'),
    httpbody_pb2.HttpBody(content_type="application/json", data=b'{"output": "world"}'),
]
_TEST_AGENT_ENGINE_OPERATION_SCHEMAS = []
_TEST_AGENT_ENGINE_EXTRA_PACKAGE = "fake.py"
_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        AsyncQueryEngine().async_query,
        schema_name=_TEST_DEFAULT_ASYNC_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_ASYNC_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_ASYNC_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        OperationRegistrableEngine().custom_method,
        schema_name=_TEST_CUSTOM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STANDARD_API_MODE
)
_TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        OperationRegistrableEngine().custom_async_method,
        schema_name=_TEST_CUSTOM_ASYNC_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_ASYNC_CUSTOM_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_ASYNC_API_MODE
)
_TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        StreamQueryEngine().stream_query,
        schema_name=_TEST_DEFAULT_STREAM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STREAM_API_MODE
_TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        OperationRegistrableEngine().custom_stream_method,
        schema_name=_TEST_CUSTOM_STREAM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STREAM_API_MODE
)
_TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        AsyncStreamQueryEngine().async_stream_query,
        schema_name=_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_ASYNC_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_ASYNC_STREAM_API_MODE
)
_TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        OperationRegistrableEngine().custom_async_stream_method,
        schema_name=_TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
    )
)
_TEST_AGENT_ENGINE_CUSTOM_ASYNC_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_ASYNC_STREAM_API_MODE
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
]
_TEST_OPERATION_NOT_REGISTRED_SCHEMAS = [
    _TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA,
]
_TEST_REGISTERED_OPERATION_NOT_EXIST_SCHEMAS = [
    _TEST_AGENT_ENGINE_QUERY_SCHEMA,
    _TEST_AGENT_ENGINE_CUSTOM_METHOD_SCHEMA,
]
_TEST_NO_OPERATION_REGISTRABLE_SCHEMAS = [
    _TEST_AGENT_ENGINE_QUERY_SCHEMA,
]
_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        MethodToBeUnregisteredEngine().method_to_be_unregistered,
        schema_name=_TEST_METHOD_TO_BE_UNREGISTERED_NAME,
    )
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

_TEST_BUILD_OPTIONS_INSTALLATION = _agent_engines._BUILD_OPTIONS_INSTALLATION
_TEST_INSTALLATION_SUBDIR = _utils._INSTALLATION_SUBDIR
_TEST_INSTALLATION_SCRIPT_PATH = f"{_TEST_INSTALLATION_SUBDIR}/install_package.sh"

_TEST_CUSTOM_SERVICE_ACCOUNT = "test-custom-service-account"
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
_TEST_ENCRYPTION_SPEC = types.EncryptionSpec(
    kms_key_name="projects/my-project/locations/my-region/keyRings/my-kr/cryptoKeys/my-key"
)


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


def _generate_agent_engine_with_class_methods_and_agent_framework(
    class_methods: List[proto.Message],
    agent_framework: str,
) -> types.ReasoningEngine:
    test_agent_engine = types.ReasoningEngine(
        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
        spec=types.ReasoningEngineSpec(
            package_spec=types.ReasoningEngineSpec.PackageSpec(
                pickle_object_gcs_uri=_TEST_AGENT_ENGINE_GCS_URI,
            ),
        ),
    )
    test_agent_engine.spec.class_methods.extend(class_methods)
    test_agent_engine.spec.agent_framework = agent_framework
    return test_agent_engine


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.fixture(scope="module")
def cloud_storage_get_bucket_mock():
    with mock.patch.object(storage, "Client") as cloud_storage_mock:
        bucket_mock = mock.Mock(spec=storage.Bucket)
        bucket_mock.blob.return_value.open.return_value = "blob_file"
        bucket_mock.blob.return_value.upload_from_filename.return_value = None
        bucket_mock.blob.return_value.upload_from_string.return_value = None

        cloud_storage_mock.get_bucket.return_value = bucket_mock

        yield cloud_storage_mock


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
def tarfile_open_mock():
    with mock.patch.object(tarfile, "open") as tarfile_open_mock:
        tarfile_mock = mock.Mock()
        tarfile_mock.add.return_value = None
        tarfile_open_mock().__enter__().return_value = tarfile_mock
        yield tarfile_open_mock


@pytest.fixture(scope="module")
def cloudpickle_dump_mock():
    with mock.patch.object(cloudpickle, "dump") as cloudpickle_dump_mock:
        yield cloudpickle_dump_mock


@pytest.fixture(scope="module")
def cloudpickle_load_mock():
    with mock.patch.object(cloudpickle, "load") as cloudpickle_load_mock:
        yield cloudpickle_load_mock


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


@pytest.fixture(scope="module")
def packaging_requirements_mock():
    with mock.patch.object(
        _utils,
        "_import_packaging_requirements_or_raise",
    ) as packaging_requirements_mock:
        yield packaging_requirements_mock


@pytest.fixture(scope="module")
def packaging_versions_mock():
    with mock.patch.object(
        _utils,
        "_import_packaging_versions_or_raise",
    ) as packaging_versions_mock:
        yield packaging_versions_mock


@pytest.fixture(scope="module")
def get_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "get_reasoning_engine",
    ) as get_agent_engine_mock:
        api_client_mock = mock.Mock()
        api_client_mock.get_reasoning_engine.return_value = _TEST_AGENT_ENGINE_OBJ
        get_agent_engine_mock.return_value = api_client_mock
        yield get_agent_engine_mock


@pytest.fixture(scope="module")
def list_agent_engines_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "list_reasoning_engines",
    ) as list_agent_engines_mock:
        yield list_agent_engines_mock


@pytest.fixture(scope="module")
def create_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "create_reasoning_engine",
    ) as create_agent_engine_mock:
        create_agent_engine_lro_mock = mock.Mock(ga_operation.Operation)
        create_agent_engine_lro_mock.result.return_value = _TEST_AGENT_ENGINE_OBJ
        create_agent_engine_mock.return_value = create_agent_engine_lro_mock
        yield create_agent_engine_mock


# Function scope is required for the pytest parameterized tests.
@pytest.fixture(scope="function")
def update_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "update_reasoning_engine",
    ) as update_agent_engine_mock:
        yield update_agent_engine_mock


@pytest.fixture(scope="module")
def delete_agent_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "delete_reasoning_engine",
    ) as delete_agent_engine_mock:
        delete_agent_engine_lro_mock = mock.Mock(ga_operation.Operation)
        delete_agent_engine_lro_mock.result.return_value = None
        delete_agent_engine_mock.return_value = delete_agent_engine_lro_mock
        yield delete_agent_engine_mock


@pytest.fixture(scope="function")
def stream_query_agent_engine_mock():
    def mock_streamer():
        for chunk in _TEST_AGENT_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    with mock.patch.object(
        reasoning_engine_execution_service.ReasoningEngineExecutionServiceClient,
        "stream_query_reasoning_engine",
        side_effect=lambda *args, **kwargs: mock_streamer(),
    ) as stream_query_agent_engine_mock:
        yield stream_query_agent_engine_mock


@pytest.fixture(scope="function")
def get_gca_resource_mock():
    with mock.patch.object(
        base.VertexAiResourceNoun,
        "_get_gca_resource",
    ) as get_gca_resource_mock:
        get_gca_resource_mock.return_value = _TEST_AGENT_ENGINE_OBJ
        yield get_gca_resource_mock


@pytest.fixture(scope="function")
def unregister_api_methods_mock():
    with mock.patch.object(
        _agent_engines,
        "_unregister_api_methods",
    ) as unregister_api_methods_mock:
        yield unregister_api_methods_mock


def create_fake_object_with_module(module_name):
    class FakeObject:
        pass

    FakeObject.__module__ = module_name
    return FakeObject()


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


class InvalidCapitalizeEngineWithoutBidiStreamQuerySelf:
    """A sample Agent Engine with an invalid bidi_stream_query method."""

    def set_up(self):
        pass

    async def bidi_stream_query() -> AsyncIterable[Any]:
        """Runs the engine."""
        raise NotImplementedError()


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
class TestAgentEngine:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        importlib.reload(os)
        os.environ[_TEST_AGENT_ENGINE_ENV_KEY] = _TEST_AGENT_ENGINE_ENV_VALUE
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )
        self.test_agent = CapitalizeEngine()

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_prepare_with_unspecified_extra_packages(
        self,
        cloud_storage_create_bucket_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
    ):
        with mock.patch.object(
            _agent_engines,
            "_upload_extra_packages",
        ) as upload_extra_packages_mock:
            _agent_engines._prepare(
                agent_engine=self.test_agent,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                extra_packages=None,
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                staging_bucket=_TEST_STAGING_BUCKET,
                gcs_dir_name=_TEST_GCS_DIR_NAME,
            )
            upload_extra_packages_mock.assert_not_called()

    def test_prepare_with_empty_extra_packages(
        self,
        cloud_storage_create_bucket_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
    ):
        with mock.patch.object(
            _agent_engines,
            "_upload_extra_packages",
        ) as upload_extra_packages_mock:
            _agent_engines._prepare(
                agent_engine=self.test_agent,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                extra_packages=[],
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                staging_bucket=_TEST_STAGING_BUCKET,
                gcs_dir_name=_TEST_GCS_DIR_NAME,
            )
            upload_extra_packages_mock.assert_called()  # user wants to override

    def test_get_agent_engine(self, get_agent_engine_mock):
        agent_engines.get(_TEST_RESOURCE_ID)
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_list_agent_engines(self, list_agent_engines_mock):
        list(agent_engines.list(filter=_TEST_AGENT_ENGINE_LIST_FILTER))
        list_agent_engines_mock.assert_called_with(
            request=types.reasoning_engine_service.ListReasoningEnginesRequest(
                parent=_TEST_PARENT,
                filter=_TEST_AGENT_ENGINE_LIST_FILTER,
            ),
        )

    def test_create_agent_engine(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
        )
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_AGENT_ENGINE_OBJ,
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_requirements_from_file(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="google-cloud-aiplatform==1.29.0"),
        ) as mock_file:
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements="requirements.txt",
                extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            )
        mock_file.assert_called_with("requirements.txt")
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_AGENT_ENGINE_OBJ,
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_env_vars_dict(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            env_vars={
                "TEST_ENV_VAR": "TEST_ENV_VAR_VALUE",
                "TEST_ENV_VAR_2": "TEST_ENV_VAR_VALUE_2",
                "TEST_SECRET_ENV_VAR": {
                    "secret": "TEST_SECRET_NAME_1",
                    "version": "TEST_SECRET_VERSION_1",
                },
                "TEST_SECRET_ENV_VAR_2": types.SecretRef(
                    secret="TEST_SECRET_NAME_2",
                    version="TEST_SECRET_VERSION_2",
                ),
            },
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                env=[
                    types.EnvVar(name="TEST_ENV_VAR", value="TEST_ENV_VAR_VALUE"),
                    types.EnvVar(name="TEST_ENV_VAR_2", value="TEST_ENV_VAR_VALUE_2"),
                ],
                secret_env=[
                    types.SecretEnvVar(
                        name="TEST_SECRET_ENV_VAR",
                        secret_ref={
                            "secret": "TEST_SECRET_NAME_1",
                            "version": "TEST_SECRET_VERSION_1",
                        },
                    ),
                    types.SecretEnvVar(
                        name="TEST_SECRET_ENV_VAR_2",
                        secret_ref=types.SecretRef(
                            secret="TEST_SECRET_NAME_2",
                            version="TEST_SECRET_VERSION_2",
                        ),
                    ),
                ],
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_env_vars_list(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            env_vars=[_TEST_AGENT_ENGINE_ENV_KEY, _TEST_AGENT_ENGINE_ENV_KEY],
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                env=[
                    types.EnvVar(
                        name=_TEST_AGENT_ENGINE_ENV_KEY,
                        value=_TEST_AGENT_ENGINE_ENV_VALUE,
                    ),
                    types.EnvVar(
                        name=_TEST_AGENT_ENGINE_ENV_KEY,
                        value=_TEST_AGENT_ENGINE_ENV_VALUE,
                    ),
                ],
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_build_options(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):

        with mock.patch("os.path.exists", return_value=True):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                extra_packages=[
                    _TEST_INSTALLATION_SCRIPT_PATH,
                ],
                build_options={
                    _TEST_BUILD_OPTIONS_INSTALLATION: [_TEST_INSTALLATION_SCRIPT_PATH]
                },
            )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )

        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_service_account(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            service_account=_TEST_CUSTOM_SERVICE_ACCOUNT,
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
            service_account=_TEST_CUSTOM_SERVICE_ACCOUNT,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_psc_interface_config(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            psc_interface_config=_TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG,
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                psc_interface_config=_TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG,
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_resource_limits(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            resource_limits=_TEST_AGENT_ENGINE_RESOURCE_LIMITS,
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                resource_limits=_TEST_AGENT_ENGINE_RESOURCE_LIMITS,
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_min_instances(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            min_instances=_TEST_AGENT_ENGINE_MIN_INSTANCES,
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                min_instances=_TEST_AGENT_ENGINE_MIN_INSTANCES,
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_max_instances(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            max_instances=_TEST_AGENT_ENGINE_MAX_INSTANCES,
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                max_instances=_TEST_AGENT_ENGINE_MAX_INSTANCES,
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_container_concurrency(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            container_concurrency=_TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY,
        )
        test_spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                container_concurrency=_TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY,
            ),
            agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
        )
        test_spec.class_methods.append(_TEST_AGENT_ENGINE_QUERY_SCHEMA)
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=test_spec,
            ),
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_agent_engine_with_encryption_spec(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        test_input_agent_engine_obj = types.ReasoningEngine(
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            spec=types.ReasoningEngineSpec(
                package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
                agent_framework=_agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        test_input_agent_engine_obj.spec.class_methods.append(
            _TEST_AGENT_ENGINE_QUERY_SCHEMA
        )
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=test_input_agent_engine_obj,
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    @pytest.mark.parametrize(
        "test_case_name, test_engine_instance, expected_framework",
        [
            (
                "Engine without agent_framework attribute",
                CapitalizeEngine(),
                _agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
            (
                "Engine with agent_framework attribute set to None",
                type(
                    "NoneFrameworkEngine",
                    (object,),
                    {"agent_framework": None, "clone": lambda self: self},
                )(),
                _agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
            (
                "Engine with agent_framework attribute set to a specific string",
                OperationRegistrableEngine(),
                _TEST_AGENT_FRAMEWORK,
            ),
            (
                "Engine with a different agent_framework string",
                type(
                    "CustomFrameworkEngine",
                    (object,),
                    {
                        "agent_framework": "MyCustomFramework",
                        "clone": lambda self: self,
                    },
                )(),
                "MyCustomFramework",
            ),
        ],
    )
    def test_get_agent_framework(
        self, test_case_name, test_engine_instance, expected_framework
    ):
        framework = _agent_engines._get_agent_framework(test_engine_instance)
        assert framework == expected_framework

    @pytest.mark.parametrize(
        "test_case_name, test_kwargs, want_request",
        [
            (
                "Update the requirements",
                {"requirements": _TEST_AGENT_ENGINE_REQUIREMENTS},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            package_spec=types.ReasoningEngineSpec.PackageSpec(
                                requirements_gcs_uri=(
                                    _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI
                                ),
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=["spec.package_spec.requirements_gcs_uri"]
                    ),
                ),
            ),
            (
                "Update the extra_packages",
                {"extra_packages": [_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH]},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            package_spec=types.ReasoningEngineSpec.PackageSpec(
                                dependency_files_gcs_uri=(
                                    _TEST_AGENT_ENGINE_DEPENDENCY_FILES_GCS_URI
                                ),
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=["spec.package_spec.dependency_files_gcs_uri"]
                    ),
                ),
            ),
            (
                "Update the agent_engine",
                {"agent_engine": CapitalizeEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_TEST_UPDATE_AGENT_ENGINE_OBJ,
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the async query engine",
                {"agent_engine": AsyncQueryEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        _TEST_ASYNC_QUERY_SCHEMAS,
                        _agent_engines._DEFAULT_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the stream query engine",
                {"agent_engine": StreamQueryEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        _TEST_STREAM_QUERY_SCHEMAS,
                        _agent_engines._DEFAULT_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the async stream query engine",
                {"agent_engine": AsyncStreamQueryEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        _TEST_ASYNC_STREAM_QUERY_SCHEMAS,
                        _agent_engines._DEFAULT_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the bidi stream query engine",
                {"agent_engine": BidiStreamQueryEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        [],
                        _agent_engines._DEFAULT_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the operation registrable engine",
                {"agent_engine": OperationRegistrableEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        _TEST_OPERATION_REGISTRABLE_SCHEMAS,
                        _TEST_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the operation not registered engine",
                {"agent_engine": OperationNotRegisteredEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
                        _agent_engines._DEFAULT_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the display_name",
                {"display_name": _TEST_AGENT_ENGINE_DISPLAY_NAME},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                    ),
                    update_mask=field_mask_pb2.FieldMask(paths=["display_name"]),
                ),
            ),
            (
                "Update the description",
                {"description": _TEST_AGENT_ENGINE_DESCRIPTION},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        description=_TEST_AGENT_ENGINE_DESCRIPTION,
                    ),
                    update_mask=field_mask_pb2.FieldMask(paths=["description"]),
                ),
            ),
            (
                "Update the environment variables",
                {
                    "env_vars": {
                        _TEST_AGENT_ENGINE_ENV_KEY: _TEST_AGENT_ENGINE_ENV_VALUE,
                        "TEST_SECRET_ENV_VAR": {
                            "secret": "TEST_SECRET_NAME",
                            "version": "TEST_SECRET_VERSION",
                        },
                    },
                },
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                                env=[
                                    types.EnvVar(
                                        name=_TEST_AGENT_ENGINE_ENV_KEY,
                                        value=_TEST_AGENT_ENGINE_ENV_VALUE,
                                    ),
                                ],
                                secret_env=[
                                    types.SecretEnvVar(
                                        name="TEST_SECRET_ENV_VAR",
                                        secret_ref=types.SecretRef(
                                            secret="TEST_SECRET_NAME",
                                            version="TEST_SECRET_VERSION",
                                        ),
                                    ),
                                ],
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.deployment_spec.env",
                            "spec.deployment_spec.secret_env",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with agent_framework attribute",
                {"agent_engine": OperationRegistrableEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_generate_agent_engine_with_class_methods_and_agent_framework(
                        _TEST_OPERATION_REGISTRABLE_SCHEMAS,
                        _TEST_AGENT_FRAMEWORK,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                            "spec.agent_framework",
                        ]
                    ),
                ),
            ),
            (
                "Update the agent_engine with service_account attribute",
                {"service_account": _TEST_CUSTOM_SERVICE_ACCOUNT},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            service_account=_TEST_CUSTOM_SERVICE_ACCOUNT,
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.service_account",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with psc_interface_config attribute",
                {"psc_interface_config": _TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                                psc_interface_config=_TEST_AGENT_ENGINE_PSC_INTERFACE_CONFIG,
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.deployment_spec.psc_interface_config",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with min_instances attribute",
                {"min_instances": _TEST_AGENT_ENGINE_MIN_INSTANCES},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                                min_instances=_TEST_AGENT_ENGINE_MIN_INSTANCES,
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.deployment_spec.min_instances",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with max_instances attribute",
                {"max_instances": _TEST_AGENT_ENGINE_MAX_INSTANCES},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                                max_instances=_TEST_AGENT_ENGINE_MAX_INSTANCES,
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.deployment_spec.max_instances",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with resource_limits attribute",
                {"resource_limits": _TEST_AGENT_ENGINE_RESOURCE_LIMITS},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                                resource_limits=_TEST_AGENT_ENGINE_RESOURCE_LIMITS,
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.deployment_spec.resource_limits",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with container_concurrency attribute",
                {"container_concurrency": _TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            deployment_spec=types.ReasoningEngineSpec.DeploymentSpec(
                                container_concurrency=_TEST_AGENT_ENGINE_CONTAINER_CONCURRENCY,
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.deployment_spec.container_concurrency",
                        ],
                    ),
                ),
            ),
            (
                "Update the agent_engine with encryption_spec attribute",
                {"encryption_spec": _TEST_ENCRYPTION_SPEC},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        encryption_spec=_TEST_ENCRYPTION_SPEC,
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "encryption_spec",
                        ],
                    ),
                ),
            ),
        ],
    )
    def test_update_agent_engine(
        self,
        test_case_name,
        test_kwargs,
        want_request,
        update_agent_engine_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_gca_resource_mock,
    ):
        test_agent_engine = _generate_agent_engine_to_update()
        with mock.patch.object(
            reasoning_engine_service.ReasoningEngineServiceClient,
            "update_reasoning_engine",
        ) as update_mock_1:
            test_agent_engine.update(**test_kwargs)
            assert_called_with_diff(update_mock_1, {"request": want_request})

        with mock.patch.object(
            reasoning_engine_service.ReasoningEngineServiceClient,
            "update_reasoning_engine",
        ) as update_mock_2:
            agent_engines.update(
                resource_name=test_agent_engine.resource_name,
                **test_kwargs,
            )
            assert_called_with_diff(update_mock_2, {"request": want_request})

    def test_update_agent_engine_requirements_from_file(
        self,
        update_agent_engine_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_gca_resource_mock,
        unregister_api_methods_mock,
    ):
        test_agent_engine = _generate_agent_engine_to_update()
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="google-cloud-aiplatform==1.29.0"),
        ) as mock_file:
            test_agent_engine.update(requirements="requirements.txt")
            mock_file.assert_called_with("requirements.txt")
        assert_called_with_diff(
            update_agent_engine_mock,
            {
                "request": types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            package_spec=types.ReasoningEngineSpec.PackageSpec(
                                requirements_gcs_uri=(
                                    _TEST_AGENT_ENGINE_REQUIREMENTS_GCS_URI
                                ),
                            ),
                        ),
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=["spec.package_spec.requirements_gcs_uri"]
                    ),
                )
            },
        )
        unregister_api_methods_mock.assert_not_called()

    def test_delete_agent_engine(
        self,
        delete_agent_engine_mock,
    ):
        agent_engines.delete(_TEST_AGENT_ENGINE_RESOURCE_NAME)
        delete_agent_engine_mock.assert_called_with(
            request=types.DeleteReasoningEngineRequest(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            ),
        )

    def test_delete_agent_engine_force(
        self,
        delete_agent_engine_mock,
    ):
        agent_engines.delete(_TEST_AGENT_ENGINE_RESOURCE_NAME, force=True)
        delete_agent_engine_mock.assert_called_with(
            request=types.DeleteReasoningEngineRequest(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                force=True,
            ),
        )

    def test_delete_after_create_agent_engine(
        self,
        create_agent_engine_mock,
        cloud_storage_get_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
        delete_agent_engine_mock,
        get_gca_resource_mock,
    ):
        test_agent_engine = agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
        )
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_AGENT_ENGINE_OBJ,
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        test_agent_engine.delete()
        delete_agent_engine_mock.assert_called_with(
            request=types.DeleteReasoningEngineRequest(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                force=False,
            ),
        )

    def test_delete_after_get_agent_engine(
        self,
        get_agent_engine_mock,
        delete_agent_engine_mock,
        get_gca_resource_mock,
    ):
        test_agent_engine = agent_engines.get(_TEST_RESOURCE_ID)
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        test_agent_engine.delete()
        delete_agent_engine_mock.assert_called_with(
            request=types.DeleteReasoningEngineRequest(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                force=False,
            ),
        )

    def test_query_after_create_agent_engine(
        self,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        test_agent_engine = agent_engines.create(
            self.test_agent,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
        )
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        with mock.patch.object(
            test_agent_engine.execution_api_client,
            "query_reasoning_engine",
        ) as query_mock:
            query_mock.return_value = _TEST_AGENT_ENGINE_QUERY_RESPONSE
            test_agent_engine.query(query=_TEST_QUERY_PROMPT)
            assert test_agent_engine.query.__doc__ == CapitalizeEngine().query.__doc__
            query_mock.assert_called_with(request=_TEST_AGENT_ENGINE_QUERY_REQUEST)

    def test_query_agent_engine(
        self,
        get_agent_engine_mock,
        get_gca_resource_mock,
    ):
        test_agent_engine = agent_engines.get(_TEST_RESOURCE_ID)
        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        with mock.patch.object(
            test_agent_engine.execution_api_client,
            "query_reasoning_engine",
        ) as query_mock:
            query_mock.return_value = _TEST_AGENT_ENGINE_QUERY_RESPONSE
            test_agent_engine.query(query=_TEST_QUERY_PROMPT)
            query_mock.assert_called_with(request=_TEST_AGENT_ENGINE_QUERY_REQUEST)

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
                _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
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
    def test_operation_schemas(
        self,
        test_case_name,
        test_class_methods_spec,
        want_operation_schema_api_modes,
        get_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.get(_TEST_RESOURCE_ID)

        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        want_operation_schemas = []
        for want_operation_schema, api_mode in want_operation_schema_api_modes:
            want_operation_schema[_TEST_MODE_KEY_IN_SCHEMA] = api_mode
            want_operation_schemas.append(want_operation_schema)
        assert test_agent_engine.operation_schemas() == want_operation_schemas

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, want_class_methods, want_agent_framework",
        [
            (
                "Default (Not Operation Registrable) Engine",
                CapitalizeEngine(),
                _TEST_NO_OPERATION_REGISTRABLE_SCHEMAS,
                _agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
                _TEST_AGENT_FRAMEWORK,
            ),
            (
                "Operation Not Registered Engine",
                OperationNotRegisteredEngine(),
                _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
                _agent_engines._DEFAULT_AGENT_FRAMEWORK,
            ),
        ],
    )
    def test_create_class_methods_spec_with_registered_operations(
        self,
        test_case_name,
        test_engine,
        want_class_methods,
        want_agent_framework,
        create_agent_engine_mock,
    ):
        agent_engines.create(
            test_engine,
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_AGENT_ENGINE_EXTRA_PACKAGE_PATH],
        )
        spec = types.ReasoningEngineSpec(
            package_spec=_TEST_AGENT_ENGINE_PACKAGE_SPEC,
            agent_framework=want_agent_framework,
        )
        spec.class_methods.extend(want_class_methods)
        spec.agent_framework = want_agent_framework
        create_agent_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=types.ReasoningEngine(
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                spec=spec,
            ),
        )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_method_docs, test_class_methods_spec",
        [
            (
                "Default (Not Operation Registrable) Engine",
                CapitalizeEngine(),
                {
                    _TEST_DEFAULT_METHOD_NAME: _TEST_CAPITALIZE_ENGINE_METHOD_DOCSTRING,
                },
                _TEST_NO_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                {
                    _TEST_DEFAULT_METHOD_NAME: _TEST_CAPITALIZE_ENGINE_METHOD_DOCSTRING,
                    _TEST_CUSTOM_METHOD_NAME: _TEST_CUSTOM_METHOD_DEFAULT_DOCSTRING,
                },
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Not Registered Engine",
                OperationNotRegisteredEngine(),
                {
                    _TEST_CUSTOM_METHOD_NAME: _TEST_CUSTOM_METHOD_DEFAULT_DOCSTRING,
                },
                _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
            ),
        ],
    )
    def test_query_after_create_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_method_docs,
        test_class_methods_spec,
        get_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.create(test_engine)

        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

        for method_name, test_doc in test_class_method_docs.items():
            with mock.patch.object(
                test_agent_engine.execution_api_client,
                "query_reasoning_engine",
            ) as query_mock:
                query_mock.return_value = _TEST_AGENT_ENGINE_QUERY_RESPONSE
                invoked_method = getattr(test_agent_engine, method_name)
                invoked_method(query=_TEST_QUERY_PROMPT)
                query_mock.assert_called_with(
                    request=types.QueryReasoningEngineRequest(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        input={_TEST_DEFAULT_METHOD_NAME: _TEST_QUERY_PROMPT},
                        class_method=method_name,
                    )
                )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default (Not Operation Registrable) Engine",
                CapitalizeEngine(),
                [_TEST_DEFAULT_METHOD_NAME],
                _TEST_NO_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [_TEST_DEFAULT_METHOD_NAME, _TEST_CUSTOM_METHOD_NAME],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Not Registered Engine",
                OperationNotRegisteredEngine(),
                [_TEST_CUSTOM_METHOD_NAME],
                _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
            ),
        ],
    )
    def test_query_after_update_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        get_agent_engine_mock,
        update_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.append(_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME, spec=test_spec
            )
            test_agent_engine = agent_engines.create(MethodToBeUnregisteredEngine())
            assert hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)

        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine.update(agent_engine=test_engine)

        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

        assert not hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)
        for method_name in test_class_methods:
            with mock.patch.object(
                test_agent_engine.execution_api_client,
                "query_reasoning_engine",
            ) as query_mock:
                getattr(test_agent_engine, method_name)(query=_TEST_QUERY_PROMPT)
                query_mock.assert_called_with(
                    request=types.QueryReasoningEngineRequest(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        input={_TEST_DEFAULT_METHOD_NAME: _TEST_QUERY_PROMPT},
                        class_method=method_name,
                    )
                )

    def test_query_after_update_agent_engine_with_same_operation_schema(
        self,
        update_agent_engine_mock,
        unregister_api_methods_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(_TEST_OPERATION_REGISTRABLE_SCHEMAS)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.create(OperationRegistrableEngine())
            test_agent_engine.update(agent_engine=SameRegisteredOperationsEngine())
            unregister_api_methods_mock.assert_not_called()

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default (Not Operation Registrable) Engine",
                CapitalizeEngine(),
                [_TEST_DEFAULT_METHOD_NAME],
                _TEST_NO_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [_TEST_DEFAULT_METHOD_NAME, _TEST_CUSTOM_METHOD_NAME],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Not Registered Engine",
                OperationNotRegisteredEngine(),
                [_TEST_CUSTOM_METHOD_NAME],
                _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
            ),
        ],
    )
    def test_query_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        get_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.get(_TEST_RESOURCE_ID)

        get_agent_engine_mock.assert_called_with(
            name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

        for method_name in test_class_methods:
            with mock.patch.object(
                test_agent_engine.execution_api_client,
                "query_reasoning_engine",
            ) as query_mock:
                getattr(test_agent_engine, method_name)(query=_TEST_QUERY_PROMPT)
                query_mock.assert_called_with(
                    request=types.QueryReasoningEngineRequest(
                        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                        input={_TEST_DEFAULT_METHOD_NAME: _TEST_QUERY_PROMPT},
                        class_method=method_name,
                    )
                )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_method_docs, test_class_methods_spec",
        [
            (
                "Default Stream Queryable (Not Operation Registrable) Engine",
                StreamQueryEngine(),
                {
                    _TEST_DEFAULT_STREAM_METHOD_NAME: _TEST_STREAM_METHOD_DOCSTRING,
                },
                _TEST_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                {
                    _TEST_DEFAULT_STREAM_METHOD_NAME: _TEST_STREAM_METHOD_DOCSTRING,
                    _TEST_CUSTOM_STREAM_METHOD_NAME: _TEST_CUSTOM_STREAM_METHOD_DEFAULT_DOCSTRING,
                },
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    def test_stream_query_after_create_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_method_docs,
        test_class_methods_spec,
        stream_query_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.create(test_engine)

        for method_name, test_doc in test_class_method_docs.items():
            invoked_method = getattr(test_agent_engine, method_name)
            list(invoked_method(input=_TEST_QUERY_PROMPT))

            stream_query_agent_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default Stream Queryable (Not Operation Registrable) Engine",
                StreamQueryEngine(),
                [_TEST_DEFAULT_STREAM_METHOD_NAME],
                _TEST_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [_TEST_DEFAULT_STREAM_METHOD_NAME, _TEST_CUSTOM_STREAM_METHOD_NAME],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    def test_stream_query_after_update_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        update_agent_engine_mock,
        stream_query_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.append(_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME, spec=test_spec
            )
            test_agent_engine = agent_engines.create(MethodToBeUnregisteredEngine())
            assert hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)

        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine.update(agent_engine=test_engine)

        assert not hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)
        for method_name in test_class_methods:
            invoked_method = getattr(test_agent_engine, method_name)
            list(invoked_method(input=_TEST_QUERY_PROMPT))

            stream_query_agent_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default Stream Queryable (Not Operation Registrable) Engine",
                StreamQueryEngine(),
                [_TEST_DEFAULT_STREAM_METHOD_NAME],
                _TEST_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [_TEST_DEFAULT_STREAM_METHOD_NAME, _TEST_CUSTOM_STREAM_METHOD_NAME],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    def test_stream_query_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        stream_query_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.get(_TEST_RESOURCE_ID)

        for method_name in test_class_methods:
            invoked_method = getattr(test_agent_engine, method_name)
            list(invoked_method(input=_TEST_QUERY_PROMPT))

            stream_query_agent_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_method_docs, test_class_methods_spec",
        [
            (
                "Default Async Stream Queryable (Not Operation Registrable) Engine",
                AsyncStreamQueryEngine(),
                {
                    _TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME: (
                        _TEST_ASYNC_STREAM_METHOD_DOCSTRING
                    ),
                },
                _TEST_ASYNC_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                {
                    _TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME: (
                        _TEST_ASYNC_STREAM_METHOD_DOCSTRING
                    ),
                    _TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME: (
                        _TEST_CUSTOM_ASYNC_STREAM_METHOD_DEFAULT_DOCSTRING
                    ),
                },
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_async_stream_query_after_create_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_method_docs,
        test_class_methods_spec,
        stream_query_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.create(test_engine)

        for method_name, test_doc in test_class_method_docs.items():
            invoked_method = getattr(test_agent_engine, method_name)
            results = []
            async for chunk in invoked_method(input=_TEST_QUERY_PROMPT):
                results.append(chunk)

            assert len(results) == 2  # Matches the length of mocked response

            stream_query_agent_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default Async Stream Queryable (Not Operation Registrable) Engine",
                AsyncStreamQueryEngine(),
                [_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME],
                _TEST_ASYNC_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [
                    _TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
                    _TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
                ],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_async_stream_query_after_update_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        update_agent_engine_mock,
        stream_query_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.append(_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME, spec=test_spec
            )
            test_agent_engine = agent_engines.create(MethodToBeUnregisteredEngine())
            assert hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)

        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine.update(agent_engine=test_engine)

        assert not hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)
        for method_name in test_class_methods:
            invoked_method = getattr(test_agent_engine, method_name)
            results = []
            async for chunk in invoked_method(input=_TEST_QUERY_PROMPT):
                results.append(chunk)

            assert len(results) == 2  # Matches the length of mocked response

            stream_query_agent_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default Async Stream Queryable (Not Operation Registrable) Engine",
                AsyncStreamQueryEngine(),
                [_TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME],
                _TEST_ASYNC_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [
                    _TEST_DEFAULT_ASYNC_STREAM_METHOD_NAME,
                    _TEST_CUSTOM_ASYNC_STREAM_METHOD_NAME,
                ],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_async_stream_query_agent_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        stream_query_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine = agent_engines.get(_TEST_RESOURCE_ID)

        for method_name in test_class_methods:
            invoked_method = getattr(test_agent_engine, method_name)
            results = []
            async for chunk in invoked_method(input=_TEST_QUERY_PROMPT):
                results.append(chunk)

            assert len(results) == 2  # Matches the length of mocked response

            stream_query_agent_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_method_docs, test_class_methods_spec",
        [
            (
                "Default Bidi Stream Queryable (Not Operation Registrable) Engine",
                BidiStreamQueryEngine(),
                {},
                _TEST_ASYNC_STREAM_QUERY_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                {},
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_create_agent_engine_with_bidi_stream_query_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_method_docs,
        test_class_methods_spec,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            agent_engines.create(test_engine)

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, test_class_methods, test_class_methods_spec",
        [
            (
                "Default Bidi Stream Queryable (Not Operation Registrable) Engine",
                BidiStreamQueryEngine(),
                [],
                [],
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                [],
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
        ],
    )
    @pytest.mark.asyncio
    async def test_update_agent_engine_with_bidi_stream_query_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        update_agent_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.append(_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME, spec=test_spec
            )
            test_agent_engine = agent_engines.create(MethodToBeUnregisteredEngine())
            assert hasattr(test_agent_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)

        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_agent_engine.update(agent_engine=test_engine)


@pytest.mark.usefixtures("google_auth_mock")
class TestAgentEngineErrors:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )
        self.test_agent = CapitalizeEngine()

    def test_create_agent_engine_unspecified_staging_bucket(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(
            ValueError,
            match="Please provide a `staging_bucket`",
        ):
            importlib.reload(initializer)
            importlib.reload(aiplatform)
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
            )
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
                staging_bucket=_TEST_STAGING_BUCKET,
            )

    def test_create_agent_engine_no_query_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "agent_engine has none of the following callable methods: "
                "`query`, `async_query`, `stream_query`, `async_stream_query`, "
                "`bidi_stream_query` or `register_operations`."
            ),
        ):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutQueryMethod(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_noncallable_query_attribute(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "agent_engine has none of the following callable methods: "
                "`query`, `async_query`, `stream_query`, `async_stream_query`, "
                "`bidi_stream_query` or `register_operations`."
            ),
        ):
            agent_engines.create(
                InvalidCapitalizeEngineWithNoncallableQueryStreamQuery(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_requirements_ioerror(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(IOError, match="Failed to read requirements"):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements="nonexistent_requirements.txt",
            )

    def test_create_agent_engine_nonexistent_extra_packages(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(FileNotFoundError, match="not found"):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                extra_packages=_TEST_AGENT_ENGINE_INVALID_EXTRA_PACKAGES,
            )

    def test_create_agent_engine_with_invalid_query_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid query signature"):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutQuerySelf(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_with_invalid_async_query_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid async_query signature"):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutAsyncQuerySelf(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_with_invalid_stream_query_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid stream_query signature"):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutStreamQuerySelf(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_with_invalid_async_stream_query_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid async_stream_query signature"):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutAsyncStreamQuerySelf(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_with_invalid_bidi_stream_query_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid bidi_stream_query signature"):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutBidiStreamQuerySelf(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_with_invalid_register_operations_method(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid register_operations signature"):
            agent_engines.create(
                InvalidCapitalizeEngineWithoutRegisterOperationsSelf(),
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
            )

    def test_create_agent_engine_with_invalid_secret_ref_env_var(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Failed to convert to secret ref"):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                env_vars={
                    "TEST_ENV_VAR": {
                        "name": "TEST_SECRET_NAME",  # "name" should be "secret"
                        "version": "TEST_SECRET_VERSION",
                    },
                },
            )

    def test_create_agent_engine_with_unknown_env_var(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Env var not found in os.environ"):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                # Assumption: "UNKNOWN_TEST_ENV_VAR" not in os.environ
                env_vars=["UNKNOWN_TEST_ENV_VAR"],
            )

    def test_create_agent_engine_with_invalid_type_env_var(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(TypeError, match="Unknown value type in env_vars"):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                env_vars={
                    "TEST_ENV_VAR": 0.01,  # should be a string or dict or SecretRef
                },
            )
        with pytest.raises(TypeError, match="env_vars must be a list, tuple or a dict"):
            agent_engines.create(
                self.test_agent,
                display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
                requirements=_TEST_AGENT_ENGINE_REQUIREMENTS,
                env_vars=types.SecretRef(  # should be a list or dict
                    secret="TEST_SECRET_NAME",
                    version="TEST_SECRET_VERSION",
                ),
            )

    def test_update_agent_engine_unspecified_staging_bucket(
        self,
        update_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
    ):
        with pytest.raises(
            ValueError,
            match="Please provide a `staging_bucket`",
        ):
            test_agent_engine = _generate_agent_engine_to_update()
            importlib.reload(initializer)
            importlib.reload(aiplatform)
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
            )
            test_agent_engine.update(
                agent_engine=InvalidCapitalizeEngineWithoutQueryMethod(),
            )
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
                staging_bucket=_TEST_STAGING_BUCKET,
            )

    def test_update_agent_engine_no_query_method(
        self,
        update_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "agent_engine has none of the following callable methods: "
                "`query`, `async_query`, `stream_query`, `async_stream_query`, "
                "`bidi_stream_query` or `register_operations`."
            ),
        ):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update(
                agent_engine=InvalidCapitalizeEngineWithoutQueryMethod(),
            )

    def test_update_agent_engine_noncallable_query_attribute(
        self,
        update_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "agent_engine has none of the following callable methods: "
                "`query`, `async_query`, `stream_query`, `async_stream_query`, "
                "`bidi_stream_query` or `register_operations`."
            ),
        ):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update(
                agent_engine=InvalidCapitalizeEngineWithNoncallableQueryStreamQuery(),
            )

    def test_update_agent_engine_requirements_ioerror(
        self,
        update_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(IOError, match="Failed to read requirements"):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update(
                requirements="nonexistent_requirements.txt",
            )

    def test_update_agent_engine_nonexistent_extra_packages(
        self,
        update_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(FileNotFoundError, match="not found"):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update(
                extra_packages=_TEST_AGENT_ENGINE_INVALID_EXTRA_PACKAGES,
            )

    def test_update_agent_engine_with_invalid_query_method(
        self,
        update_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid query signature"):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update(
                agent_engine=InvalidCapitalizeEngineWithoutQuerySelf(),
            )

    def test_update_agent_engine_with_no_updates(
        self,
        update_agent_engine_mock,
    ):
        with pytest.raises(
            ValueError,
            match=(
                "At least one of `agent_engine`, `requirements`, "
                "`extra_packages`, `display_name`, `description`, "
                "`env_vars`, `build_options`, `service_account`, "
                "`psc_interface_config`, `min_instances`, `max_instances`, "
                "`resource_limits`, `container_concurrency`, or "
                "`encryption_spec` must be specified."
            ),
        ):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update()

    def test_create_class_methods_spec_with_registered_operation_not_found(self):
        with pytest.raises(
            ValueError,
            match=(
                "Method `missing_method` defined in `register_operations`"
                " not found on AgentEngine."
            ),
        ):
            agent_engines.create(RegisteredOperationNotExistEngine())

    def test_update_class_methods_spec_with_registered_operation_not_found(self):
        with pytest.raises(
            ValueError,
            match=(
                "Method `missing_method` defined in `register_operations`"
                " not found on AgentEngine."
            ),
        ):
            test_agent_engine = _generate_agent_engine_to_update()
            test_agent_engine.update(agent_engine=RegisteredOperationNotExistEngine())

    # pytest does not allow absl.testing.parameterized.named_parameters.
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
                    "Supported modes are: ``, `a2a_extension`, `async`, `async_stream`, "
                    "`bidi_stream`, `stream`.}"
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("caplog")
    def test_invalid_operation_schema(
        self,
        test_case_name,
        test_operation_schemas,
        want_log_output,
        caplog,
    ):
        with mock.patch.object(
            _agent_engines.AgentEngine,
            "operation_schemas",
        ) as mock_operation_schemas:
            mock_operation_schemas.return_value = test_operation_schemas
            agent_engines.get(_TEST_AGENT_ENGINE_RESOURCE_NAME)

        assert want_log_output in caplog.text


@pytest.mark.usefixtures("google_auth_mock")
class TestLightweightAgentEngine:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        self.test_agent = CapitalizeEngine()

    def test_create_agent_engine_with_no_spec(
        self,
        create_agent_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        cloudpickle_load_mock,
        importlib_metadata_version_mock,
        get_agent_engine_mock,
    ):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        agent_engines.create(
            display_name=_TEST_AGENT_ENGINE_DISPLAY_NAME,
            description=_TEST_AGENT_ENGINE_DESCRIPTION,
        )
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )


def _generate_agent_engine_to_update() -> "agent_engines.AgentEngine":
    test_agent_engine = agent_engines.create(CapitalizeEngine())
    # Resource name is required for the update method.
    test_agent_engine._gca_resource = types.ReasoningEngine(
        name=_TEST_AGENT_ENGINE_RESOURCE_NAME,
    )
    return test_agent_engine


def place_tool_query(
    city: str,
    activity: Optional[str] = None,
    page_size: int = 3,
):
    """Searches the city for recommendations on the activity."""
    pass


def place_photo_query(
    photo_reference: str,
    maxwidth: int = 400,
    maxheight: Optional[int] = None,
):
    """Returns the photo for a given reference."""
    pass


def assert_called_with_diff(mock_obj, expected_kwargs=None):
    """Asserts that the mock object was called with the expected arguments,
    using difflib to show any differences.

    Args:
        mock_obj: The mock object to check.
        expected_kwargs: Expected keyword arguments, or None if not checking.
    """
    assert mock_obj.called, (
        f"Expected '{mock_obj._extract_mock_name()}' to be called, ",
        "but it was not.",
    )

    _, call_kwargs = mock_obj.call_args_list[0]
    diff = "\n".join(
        difflib.ndiff(
            str(call_kwargs or "").splitlines(), str(expected_kwargs or "").splitlines()
        )
    )
    assert call_kwargs == expected_kwargs, (
        "Unexpected keyword arguments for "
        f"'{mock_obj._extract_mock_name()}'.\n"
        f"Diff (-got +want):\n{diff}"
    )


class TestGenerateSchema:
    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "func, required, expected_operation",
        [
            (
                # "place_tool_query",
                place_tool_query,
                ["city", "activity"],
                {
                    "name": "place_tool_query",
                    "description": (
                        "Searches the city for recommendations on the activity."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {"type": "string"},
                            "activity": {"type": "string", "nullable": True},
                            "page_size": {"type": "integer"},
                        },
                        "required": ["city", "activity"],
                    },
                },
            ),
            (
                # "place_photo_query",
                place_photo_query,
                ["photo_reference"],
                {
                    "name": "place_photo_query",
                    "description": "Returns the photo for a given reference.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "photo_reference": {"type": "string"},
                            "maxwidth": {"type": "integer"},
                            "maxheight": {"type": "integer", "nullable": True},
                        },
                        "required": ["photo_reference"],
                    },
                },
            ),
        ],
    )
    def test_generate_schemas(self, func, required, expected_operation):
        result = _utils.generate_schema(func, required=required)
        assert result == expected_operation


class TestToProto:
    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "obj, expected_proto",
        [
            (
                # "empty_dict",
                {},
                struct_pb2.Struct(fields={}),
            ),
            (
                # "nonempty_dict",
                {"snake_case": 1, "camelCase": 2},
                struct_pb2.Struct(
                    fields={
                        "snake_case": struct_pb2.Value(number_value=1),
                        "camelCase": struct_pb2.Value(number_value=2),
                    },
                ),
            ),
            (
                # "empty_proto_message",
                struct_pb2.Struct(fields={}),
                struct_pb2.Struct(fields={}),
            ),
            (
                # "nonempty_proto_message",
                struct_pb2.Struct(
                    fields={
                        "snake_case": struct_pb2.Value(number_value=1),
                        "camelCase": struct_pb2.Value(number_value=2),
                    },
                ),
                struct_pb2.Struct(
                    fields={
                        "snake_case": struct_pb2.Value(number_value=1),
                        "camelCase": struct_pb2.Value(number_value=2),
                    },
                ),
            ),
        ],
    )
    def test_to_proto(self, obj, expected_proto):
        result = _utils.to_proto(obj)
        assert _utils.to_dict(result) == _utils.to_dict(expected_proto)


class ToParsedJsonTest:
    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "obj, expected",
        [
            (
                # "valid_json",
                httpbody_pb2.HttpBody(
                    content_type="application/json", data=b'{"a": 1, "b": "hello"}'
                ),
                [{"a": 1, "b": "hello"}],
            ),
            (
                # "invalid_json",
                httpbody_pb2.HttpBody(
                    content_type="application/json", data=b'{"a": 1, "b": "hello"'
                ),
                ['{"a": 1, "b": "hello"'],  # returns the unparsed string
            ),
            (
                # "missing_content_type",
                httpbody_pb2.HttpBody(data=b'{"a": 1}'),
                [httpbody_pb2.HttpBody(data=b'{"a": 1}')],
            ),
            (
                # "missing_data",
                httpbody_pb2.HttpBody(content_type="application/json"),
                [None],
            ),
            (
                # "wrong_content_type",
                httpbody_pb2.HttpBody(content_type="text/plain", data=b"hello"),
                [httpbody_pb2.HttpBody(content_type="text/plain", data=b"hello")],
            ),
            (
                # "empty_data",
                httpbody_pb2.HttpBody(content_type="application/json", data=b""),
                [None],
            ),
            (
                # "unicode_data",
                httpbody_pb2.HttpBody(
                    content_type="application/json",
                    data='{"a": "你好"}'.encode("utf-8"),
                ),
                [{"a": "你好"}],
            ),
            (
                # "nested_json",
                httpbody_pb2.HttpBody(
                    content_type="application/json", data=b'{"a": {"b": 1}}'
                ),
                [{"a": {"b": 1}}],
            ),
            (
                # "multiline_json",
                httpbody_pb2.HttpBody(
                    content_type="application/json",
                    data=b'{"a": {"b": 1}}\n{"a": {"b": 2}}',
                ),
                [{"a": {"b": 1}}, {"a": {"b": 2}}],
            ),
        ],
    )
    def test_to_parsed_json(self, obj, expected):
        for got, want in zip(_utils.yield_parsed_json(obj), expected):
            assert got == want


class TestRequirements:
    @pytest.mark.usefixtures("caplog")
    def test_invalid_requirement_warning(self, caplog):
        _utils.parse_constraints(["invalid requirement line"])
        assert "Failed to parse constraint" in caplog.text

    def test_requirements_with_whl_files(self):
        whl_files = [
            "wxPython-4.2.4-cp39-cp39-macosx_12_0_x86_64.whl",
            "/content/wxPython-4.2.3-cp39-cp39-macosx_12_0_x86_64.whl",
            "https://wxpython.org/Phoenix/snapshot-builds/wxPython-4.2.2-cp38-cp38-macosx_12_0_x86_64.whl",
        ]
        result = _utils.parse_constraints(whl_files)
        assert result == {
            "wxPython-4.2.2-cp38-cp38-macosx_12_0_x86_64.whl": None,
            "wxPython-4.2.3-cp39-cp39-macosx_12_0_x86_64.whl": None,
            "wxPython-4.2.4-cp39-cp39-macosx_12_0_x86_64.whl": None,
        }

    def test_compare_requirements_with_required_packages(self):
        requirements = {"requests": "2.0.0"}
        constraints = ["requests==1.0.0"]
        result = _utils.compare_requirements(requirements, constraints)
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
        fake_obj = create_fake_object_with_module("requests")
        requirements = _utils.scan_requirements(
            fake_obj,
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
        fake_obj_stdlib = create_fake_object_with_module("json")
        requirements = _utils.scan_requirements(
            fake_obj_stdlib,
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
        fake_obj = create_fake_object_with_module("requests")
        original_base = _utils._BASE_MODULES
        monkeypatch.setattr(
            _utils,
            "_BASE_MODULES",
            set(original_base) | {"requests"},
        )
        requirements = _utils.scan_requirements(
            fake_obj,
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
        fake_obj = create_fake_object_with_module("requests")
        requirements = _utils.scan_requirements(
            fake_obj,
            ignore_modules=["requests"],
            package_distributions=_TEST_PACKAGE_DISTRIBUTIONS,
        )
        # Requirements should not contain 'requests',
        # because 'requests' is explicitly ignored in `ignore_modules`.
        assert requirements == {
            "cloudpickle": "3.0.0",
            "pydantic": "1.11.1",
        }


class TestValidateInstallationScripts:
    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "name, script_paths, extra_packages",
        [
            (
                "valid_script_in_subdir_and_extra_packages",
                [f"{_utils._INSTALLATION_SUBDIR}/script.sh"],
                [f"{_utils._INSTALLATION_SUBDIR}/script.sh"],
            ),
            (
                "multiple_valid_scripts",
                [
                    f"{_utils._INSTALLATION_SUBDIR}/script1.sh",
                    f"{_utils._INSTALLATION_SUBDIR}/script2.sh",
                ],
                [
                    f"{_utils._INSTALLATION_SUBDIR}/script1.sh",
                    f"{_utils._INSTALLATION_SUBDIR}/script2.sh",
                ],
            ),
            ("empty_script_paths_and_extra_packages", [], []),
        ],
    )
    def test_validate_installation_scripts(self, name, script_paths, extra_packages):
        _utils.validate_installation_scripts_or_raise(
            script_paths=script_paths, extra_packages=extra_packages
        )

    @pytest.mark.parametrize(
        "name, script_paths, extra_packages, error_message",
        [
            (
                "script_not_in_subdir",
                ["script.sh"],
                ["script.sh"],
                (
                    f"Required installation script 'script.sh' is not under"
                    f" '{_utils._INSTALLATION_SUBDIR}'"
                ),
            ),
            (
                "script_not_in_extra_packages",
                [f"{_utils._INSTALLATION_SUBDIR}/script.sh"],
                [],
                (
                    "User-defined installation script "
                    f"'{_utils._INSTALLATION_SUBDIR}/script.sh'"
                    " does not exist in `extra_packages`"
                ),
            ),
            (
                "extra_package_in_subdir_but_not_script",
                [],
                [f"{_utils._INSTALLATION_SUBDIR}/script.sh"],
                (
                    f"Extra package '{_utils._INSTALLATION_SUBDIR}/script.sh' "
                    "is in the installation scripts subdirectory, but is not "
                    "specified as an installation script."
                ),
            ),
            (
                "one_valid_one_invalid_script_not_in_subdir",
                [f"{_utils._INSTALLATION_SUBDIR}/script1.sh", "script2.sh"],
                [f"{_utils._INSTALLATION_SUBDIR}/script1.sh", "script2.sh"],
                (
                    f"Required installation script 'script2.sh' is not under"
                    f" '{_utils._INSTALLATION_SUBDIR}'"
                ),
            ),
            (
                "one_valid_one_invalid_script_not_in_extra_packages",
                [
                    f"{_utils._INSTALLATION_SUBDIR}/script1.sh",
                    f"{_utils._INSTALLATION_SUBDIR}/script2.sh",
                ],
                [f"{_utils._INSTALLATION_SUBDIR}/script1.sh"],
                (
                    "User-defined installation script "
                    f"'{_utils._INSTALLATION_SUBDIR}/script2.sh' "
                    "does not exist in `extra_packages`"
                ),
            ),
            (
                "one_valid_one_invalid_extra_package_in_subdir",
                [f"{_utils._INSTALLATION_SUBDIR}/script1.sh"],
                [
                    f"{_utils._INSTALLATION_SUBDIR}/script1.sh",
                    f"{_utils._INSTALLATION_SUBDIR}/script2.sh",
                ],
                (
                    f"Extra package '{_utils._INSTALLATION_SUBDIR}/script2.sh' "
                    "is in the installation scripts subdirectory, but is not "
                    "specified as an installation script."
                ),
            ),
        ],
    )
    def test_validate_installation_scripts_raises_error(
        self,
        name,
        script_paths,
        extra_packages,
        error_message,
    ):
        with pytest.raises(ValueError, match=error_message):
            _utils.validate_installation_scripts_or_raise(
                script_paths=script_paths, extra_packages=extra_packages
            )
