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
import dataclasses
import datetime
import difflib
import importlib
import os
import pytest
import sys
import tarfile
import tempfile
from typing import Any, Dict, Iterable, List, Optional
from unittest import mock

import proto

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.services import (
    reasoning_engine_execution_service,
)
from google.cloud.aiplatform_v1beta1.services import reasoning_engine_service
from vertexai.preview import reasoning_engines
from vertexai.reasoning_engines import _reasoning_engines
from vertexai.reasoning_engines import _utils
from google.api import httpbody_pb2
from google.protobuf import field_mask_pb2
from google.protobuf import struct_pb2


class CapitalizeEngine:
    """A sample Reasoning Engine."""

    def set_up(self):
        pass

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    def clone(self):
        return self


class StreamQueryEngine:
    """A sample stream queryReasoning Engine."""

    def set_up(self):
        pass

    def stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self


class OperationRegistrableEngine:
    """Add a test class that implements OperationRegistrable."""

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    # Add a custom method to test the custom method registration.
    def custom_method(self, x: str) -> str:
        return x.upper()

    def stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    # Add a custom method to test the custom stream method registration.
    def custom_stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    # Add a custom method to test the custom stream method registration.
    def custom_stream_method(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self

    def register_operations(self) -> Dict[str, List[str]]:
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_DEFAULT_METHOD_NAME,
                _TEST_CUSTOM_METHOD_NAME,
            ],
            _TEST_STREAM_API_MODE: [
                _TEST_DEFAULT_STREAM_METHOD_NAME,
                _TEST_CUSTOM_STREAM_METHOD_NAME,
            ],
        }


class SameRegisteredOperationsEngine:
    """Add a test class that is different from `OperationRegistrableEngine` but has the same registered operations."""

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    # Add a custom method to test the custom method registration
    def custom_method(self, x: str) -> str:
        return x.upper()

    # Add a custom method that is not registered.ration
    def custom_method_2(self, x: str) -> str:
        return x.upper()

    def stream_query(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        """Runs the stream engine."""
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    # Add a custom method to test the custom stream method registration.
    def custom_stream_method(self, unused_arbitrary_string_name: str) -> Iterable[Any]:
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    def clone(self):
        return self

    def register_operations(self) -> Dict[str, List[str]]:
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_DEFAULT_METHOD_NAME,
                _TEST_CUSTOM_METHOD_NAME,
            ],
            _TEST_STREAM_API_MODE: [
                _TEST_DEFAULT_STREAM_METHOD_NAME,
                _TEST_CUSTOM_STREAM_METHOD_NAME,
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
        # Registered method `missing_method` is not a method of the
        # ReasoningEngine.
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_DEFAULT_METHOD_NAME,
                _TEST_CUSTOM_METHOD_NAME,
                "missing_method",
            ]
        }


class MethodToBeUnregisteredEngine:
    """A Reasoning Engine that has a method to be unregistered."""

    def method_to_be_unregistered(self, unused_arbitrary_string_name: str) -> str:
        """Method to be unregistered."""
        return unused_arbitrary_string_name.upper()

    def register_operations(self) -> Dict[str, List[str]]:
        # Registered method `missing_method` is not a method of the
        # ReasoningEngine.
        return {
            _TEST_STANDARD_API_MODE: [
                _TEST_METHOD_TO_BE_UNREGISTERED_NAME,
            ]
        }


@dataclasses.dataclass
class NonSerializableClass:
    name: str
    date: datetime  # Not JSON serializable by default


@dataclasses.dataclass
class SerializableClass:
    name: str
    value: int


@dataclasses.dataclass
class NestedClass:
    name: str
    inner: SerializableClass


@dataclasses.dataclass
class ListClass:
    name: str
    items: List[Any]


_TEST_RETRY = base._DEFAULT_RETRY
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_STAGING_BUCKET = "gs://test-bucket"
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_REASONING_ENGINE_RESOURCE_NAME = (
    f"{_TEST_PARENT}/reasoningEngines/{_TEST_RESOURCE_ID}"
)
_TEST_REASONING_ENGINE_DISPLAY_NAME = "Reasoning Engine Display Name"
_TEST_REASONING_ENGINE_DESCRIPTION = "Reasoning Engine Description"
_TEST_GCS_DIR_NAME = _reasoning_engines._DEFAULT_GCS_DIR_NAME
_TEST_BLOB_FILENAME = _reasoning_engines._BLOB_FILENAME
_TEST_REQUIREMENTS_FILE = _reasoning_engines._REQUIREMENTS_FILE
_TEST_EXTRA_PACKAGES_FILE = _reasoning_engines._EXTRA_PACKAGES_FILE
_TEST_STANDARD_API_MODE = _reasoning_engines._STANDARD_API_MODE
_TEST_STREAM_API_MODE = _reasoning_engines._STREAM_API_MODE
_TEST_DEFAULT_METHOD_NAME = _reasoning_engines._DEFAULT_METHOD_NAME
_TEST_DEFAULT_STREAM_METHOD_NAME = _reasoning_engines._DEFAULT_STREAM_METHOD_NAME
_TEST_CAPITALIZE_ENGINE_METHOD_DOCSTRING = "Runs the engine."
_TEST_STREAM_METHOD_DOCSTRING = "Runs the stream engine."
_TEST_MODE_KEY_IN_SCHEMA = _reasoning_engines._MODE_KEY_IN_SCHEMA
_TEST_METHOD_NAME_KEY_IN_SCHEMA = _reasoning_engines._METHOD_NAME_KEY_IN_SCHEMA
_TEST_CUSTOM_METHOD_NAME = "custom_method"
_TEST_CUSTOM_STREAM_METHOD_NAME = "custom_stream_method"
_TEST_CUSTOM_METHOD_DEFAULT_DOCSTRING = """
    Runs the Reasoning Engine to serve the user request.

    This will be based on the `.custom_method(...)` of the python object that
    was passed in when creating the Reasoning Engine. The method will invoke the
    `query` API client of the python object.

    Args:
        **kwargs:
            Optional. The arguments of the `.custom_method(...)` method.

    Returns:
        dict[str, Any]: The response from serving the user request.
"""
_TEST_CUSTOM_STREAM_METHOD_DEFAULT_DOCSTRING = """
    Runs the Reasoning Engine to serve the user request.

    This will be based on the `.custom_stream_method(...)` of the python object that
    was passed in when creating the Reasoning Engine. The method will invoke the
    `stream_query` API client of the python object.

    Args:
        **kwargs:
            Optional. The arguments of the `.custom_stream_method(...)` method.

    Returns:
        Iterable[Any]: The response from serving the user request.
"""
_TEST_METHOD_TO_BE_UNREGISTERED_NAME = "method_to_be_unregistered"
_TEST_QUERY_PROMPT = "Find the first fibonacci number greater than 999"
_TEST_REASONING_ENGINE_GCS_URI = "{}/{}/{}".format(
    _TEST_STAGING_BUCKET,
    _TEST_GCS_DIR_NAME,
    _TEST_BLOB_FILENAME,
)
_TEST_REASONING_ENGINE_DEPENDENCY_FILES_GCS_URI = "{}/{}/{}".format(
    _TEST_STAGING_BUCKET,
    _TEST_GCS_DIR_NAME,
    _TEST_EXTRA_PACKAGES_FILE,
)
_TEST_REASONING_ENGINE_REQUIREMENTS_GCS_URI = "{}/{}/{}".format(
    _TEST_STAGING_BUCKET,
    _TEST_GCS_DIR_NAME,
    _TEST_REQUIREMENTS_FILE,
)
_TEST_REASONING_ENGINE_REQUIREMENTS = [
    "google-cloud-aiplatform==1.29.0",
    "langchain",
]
_TEST_REASONING_ENGINE_INVALID_EXTRA_PACKAGES = [
    "lib",
    "main.py",
]
_TEST_REASONING_ENGINE_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        CapitalizeEngine().query,
        schema_name=_TEST_DEFAULT_METHOD_NAME,
    )
)
_TEST_REASONING_ENGINE_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = _TEST_STANDARD_API_MODE
_TEST_INPUT_REASONING_ENGINE_OBJ = types.ReasoningEngine(
    display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=types.ReasoningEngineSpec.PackageSpec(
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            pickle_object_gcs_uri=_TEST_REASONING_ENGINE_GCS_URI,
            dependency_files_gcs_uri=_TEST_REASONING_ENGINE_DEPENDENCY_FILES_GCS_URI,
            requirements_gcs_uri=_TEST_REASONING_ENGINE_REQUIREMENTS_GCS_URI,
        ),
    ),
)
_TEST_INPUT_REASONING_ENGINE_OBJ.spec.class_methods.append(
    _TEST_REASONING_ENGINE_QUERY_SCHEMA
)
_TEST_REASONING_ENGINE_OBJ = types.ReasoningEngine(
    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
    display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=types.ReasoningEngineSpec.PackageSpec(
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}",
            pickle_object_gcs_uri=_TEST_REASONING_ENGINE_GCS_URI,
            dependency_files_gcs_uri=_TEST_REASONING_ENGINE_DEPENDENCY_FILES_GCS_URI,
            requirements_gcs_uri=_TEST_REASONING_ENGINE_REQUIREMENTS_GCS_URI,
        ),
    ),
)
_TEST_REASONING_ENGINE_OBJ.spec.class_methods.append(
    _TEST_REASONING_ENGINE_QUERY_SCHEMA
)
_TEST_UPDATE_REASONING_ENGINE_OBJ = types.ReasoningEngine(
    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
    spec=types.ReasoningEngineSpec(
        package_spec=types.ReasoningEngineSpec.PackageSpec(
            pickle_object_gcs_uri=_TEST_REASONING_ENGINE_GCS_URI,
        ),
    ),
)
_TEST_UPDATE_REASONING_ENGINE_OBJ.spec.class_methods.append(
    _TEST_REASONING_ENGINE_QUERY_SCHEMA
)
_TEST_REASONING_ENGINE_QUERY_REQUEST = types.QueryReasoningEngineRequest(
    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
    input={_TEST_DEFAULT_METHOD_NAME: _TEST_QUERY_PROMPT},
    class_method=_TEST_DEFAULT_METHOD_NAME,
)
_TEST_REASONING_ENGINE_QUERY_RESPONSE = {}
_TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE = [
    httpbody_pb2.HttpBody(content_type="application/json", data=b'{"output": "hello"}'),
    httpbody_pb2.HttpBody(content_type="application/json", data=b'{"output": "world"}'),
]
_TEST_REASONING_ENGINE_OPERATION_SCHEMAS = []
_TEST_REASONING_ENGINE_SYS_VERSION = "3.10"
_TEST_REASONING_ENGINE_EXTRA_PACKAGE = "fake.py"
_TEST_REASONING_ENGINE_CUSTOM_METHOD_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        OperationRegistrableEngine().custom_method,
        schema_name=_TEST_CUSTOM_METHOD_NAME,
    )
)
_TEST_REASONING_ENGINE_CUSTOM_METHOD_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STANDARD_API_MODE
)
_TEST_REASONING_ENGINE_STREAM_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        StreamQueryEngine().stream_query,
        schema_name=_TEST_DEFAULT_STREAM_METHOD_NAME,
    )
)
_TEST_REASONING_ENGINE_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STREAM_API_MODE
)
_TEST_REASONING_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA = _utils.to_proto(
    _utils.generate_schema(
        OperationRegistrableEngine().custom_stream_method,
        schema_name=_TEST_CUSTOM_STREAM_METHOD_NAME,
    )
)
_TEST_REASONING_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA[_TEST_MODE_KEY_IN_SCHEMA] = (
    _TEST_STREAM_API_MODE
)
_TEST_OPERATION_REGISTRABLE_SCHEMAS = [
    _TEST_REASONING_ENGINE_QUERY_SCHEMA,
    _TEST_REASONING_ENGINE_CUSTOM_METHOD_SCHEMA,
    _TEST_REASONING_ENGINE_STREAM_QUERY_SCHEMA,
    _TEST_REASONING_ENGINE_CUSTOM_STREAM_QUERY_SCHEMA,
]
_TEST_OPERATION_NOT_REGISTRED_SCHEMAS = [
    _TEST_REASONING_ENGINE_CUSTOM_METHOD_SCHEMA,
]
_TEST_REGISTERED_OPERATION_NOT_EXIST_SCHEMAS = [
    _TEST_REASONING_ENGINE_QUERY_SCHEMA,
    _TEST_REASONING_ENGINE_CUSTOM_METHOD_SCHEMA,
]
_TEST_NO_OPERATION_REGISTRABLE_SCHEMAS = [
    _TEST_REASONING_ENGINE_QUERY_SCHEMA,
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
_TEST_STREAM_QUERY_SCHEMAS = [
    _TEST_REASONING_ENGINE_STREAM_QUERY_SCHEMA,
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


_TEST_REASONING_ENGINE_EXTRA_PACKAGE_PATH = _create_empty_fake_package(
    _TEST_REASONING_ENGINE_EXTRA_PACKAGE
)


def _generate_reasoning_engine_with_class_methods(
    class_methods: List[proto.Message],
) -> types.ReasoningEngine:
    test_reasoning_engine = types.ReasoningEngine(
        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
        spec=types.ReasoningEngineSpec(
            package_spec=types.ReasoningEngineSpec.PackageSpec(
                pickle_object_gcs_uri=_TEST_REASONING_ENGINE_GCS_URI,
            ),
        ),
    )
    test_reasoning_engine.spec.class_methods.extend(class_methods)
    return test_reasoning_engine


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
        cloudpickle_dump_mock.return_value = None
        yield cloudpickle_dump_mock


@pytest.fixture(scope="module")
def get_reasoning_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "get_reasoning_engine",
    ) as get_reasoning_engine_mock:
        api_client_mock = mock.Mock(
            spec=reasoning_engine_service.ReasoningEngineServiceClient,
        )
        api_client_mock.get_reasoning_engine.return_value = _TEST_REASONING_ENGINE_OBJ
        get_reasoning_engine_mock.return_value = api_client_mock
        yield get_reasoning_engine_mock


@pytest.fixture(scope="module")
def create_reasoning_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "create_reasoning_engine",
    ) as create_reasoning_engine_mock:
        create_reasoning_engine_lro_mock = mock.Mock(ga_operation.Operation)
        create_reasoning_engine_lro_mock.result.return_value = (
            _TEST_REASONING_ENGINE_OBJ
        )
        create_reasoning_engine_mock.return_value = create_reasoning_engine_lro_mock
        yield create_reasoning_engine_mock


# Function scope is required for the pytest parameterized tests.
@pytest.fixture(scope="function")
def update_reasoning_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "update_reasoning_engine",
    ) as update_reasoning_engine_mock:
        yield update_reasoning_engine_mock


@pytest.fixture(scope="module")
def delete_reasoning_engine_mock():
    with mock.patch.object(
        reasoning_engine_service.ReasoningEngineServiceClient,
        "delete_reasoning_engine",
    ) as delete_reasoning_engine_mock:
        delete_reasoning_engine_lro_mock = mock.Mock(ga_operation.Operation)
        delete_reasoning_engine_lro_mock.result.return_value = None
        delete_reasoning_engine_mock.return_value = delete_reasoning_engine_lro_mock
        yield delete_reasoning_engine_mock


@pytest.fixture(scope="module")
def query_reasoning_engine_mock():
    with mock.patch.object(
        reasoning_engine_execution_service.ReasoningEngineExecutionServiceClient,
        "query_reasoning_engine",
    ) as query_reasoning_engine_mock:
        api_client_mock = mock.Mock(
            spec=reasoning_engine_execution_service.ReasoningEngineExecutionServiceClient,
        )
        api_client_mock.query_reasoning_engine.return_value = (
            _TEST_REASONING_ENGINE_QUERY_RESPONSE
        )
        query_reasoning_engine_mock.return_value = api_client_mock
        yield query_reasoning_engine_mock


@pytest.fixture(scope="function")
def stream_query_reasoning_engine_mock():
    def mock_streamer():
        for chunk in _TEST_REASONING_ENGINE_STREAM_QUERY_RESPONSE:
            yield chunk

    with mock.patch.object(
        reasoning_engine_execution_service.ReasoningEngineExecutionServiceClient,
        "stream_query_reasoning_engine",
        return_value=mock_streamer(),
    ) as stream_query_reasoning_engine_mock:
        yield stream_query_reasoning_engine_mock


# Function scope is required for the pytest parameterized tests.
@pytest.fixture(scope="function")
def types_reasoning_engine_mock():
    with mock.patch.object(
        types,
        "ReasoningEngine",
        return_value=types.ReasoningEngine(name=_TEST_REASONING_ENGINE_RESOURCE_NAME),
    ) as types_reasoning_engine_mock:
        yield types_reasoning_engine_mock


@pytest.fixture(scope="function")
def get_gca_resource_mock():
    with mock.patch.object(
        base.VertexAiResourceNoun,
        "_get_gca_resource",
    ) as get_gca_resource_mock:
        get_gca_resource_mock.return_value = _TEST_REASONING_ENGINE_OBJ
        yield get_gca_resource_mock


@pytest.fixture(scope="function")
def unregister_api_methods_mock():
    with mock.patch.object(
        _reasoning_engines,
        "_unregister_api_methods",
    ) as unregister_api_methods_mock:
        yield unregister_api_methods_mock


class InvalidCapitalizeEngineWithoutQuerySelf:
    """A sample Reasoning Engine with an invalid query method."""

    def set_up(self):
        pass

    def query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutStreamQuerySelf:
    """A sample Reasoning Engine with an invalid query_stream_query method."""

    def set_up(self):
        pass

    def stream_query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutRegisterOperationsSelf:
    """A sample Reasoning Engine with an invalid register_operations method."""

    def set_up(self):
        pass

    def register_operations() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutQueryMethod:
    """A sample Reasoning Engine without a query method."""

    def set_up(self):
        pass

    def invoke(self) -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithNoncallableQueryStreamQuery:
    """A sample Reasoning Engine with a noncallable query attribute."""

    def __init__(self):
        self.query = "RESPONSE"

    def set_up(self):
        pass


@pytest.mark.usefixtures("google_auth_mock")
class TestReasoningEngine:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )
        self.test_app = CapitalizeEngine()

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_prepare_with_unspecified_extra_packages(
        self,
        cloud_storage_create_bucket_mock,
        cloudpickle_dump_mock,
    ):
        with mock.patch.object(
            _reasoning_engines,
            "_upload_extra_packages",
        ) as upload_extra_packages_mock:
            _reasoning_engines._prepare(
                reasoning_engine=self.test_app,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
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
    ):
        with mock.patch.object(
            _reasoning_engines,
            "_upload_extra_packages",
        ) as upload_extra_packages_mock:
            _reasoning_engines._prepare(
                reasoning_engine=self.test_app,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
                extra_packages=[],
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                staging_bucket=_TEST_STAGING_BUCKET,
                gcs_dir_name=_TEST_GCS_DIR_NAME,
            )
            upload_extra_packages_mock.assert_called()  # user wants to override

    def test_get_reasoning_engine(
        self,
        get_reasoning_engine_mock,
    ):
        reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_create_reasoning_engine(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
        get_gca_resource_mock,
    ):
        reasoning_engines.ReasoningEngine.create(
            self.test_app,
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_REASONING_ENGINE_EXTRA_PACKAGE_PATH],
        )
        create_reasoning_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_REASONING_ENGINE_OBJ,
        )
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    @pytest.mark.usefixtures("caplog")
    def test_create_reasoning_engine_warn_resource_name(
        self,
        caplog,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        reasoning_engines.ReasoningEngine.create(
            self.test_app,
            reasoning_engine_name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
        )
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "does not support user-defined resource IDs" in caplog.text

    @pytest.mark.usefixtures("caplog")
    def test_create_reasoning_engine_warn_sys_version(
        self,
        caplog,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        sys_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        reasoning_engines.ReasoningEngine.create(
            self.test_app,
            sys_version="3.10" if sys_version != "3.10" else "3.11",
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
        )
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert f"is inconsistent with {sys.version_info=}" in caplog.text

    def test_create_reasoning_engine_requirements_from_file(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
        get_gca_resource_mock,
    ):
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="google-cloud-aiplatform==1.29.0"),
        ) as mock_file:
            reasoning_engines.ReasoningEngine.create(
                self.test_app,
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements="requirements.txt",
                extra_packages=[_TEST_REASONING_ENGINE_EXTRA_PACKAGE_PATH],
            )
        mock_file.assert_called_with("requirements.txt")
        create_reasoning_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_REASONING_ENGINE_OBJ,
        )
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_kwargs, want_request",
        [
            (
                "Update the requirements",
                {"requirements": _TEST_REASONING_ENGINE_REQUIREMENTS},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            package_spec=types.ReasoningEngineSpec.PackageSpec(
                                requirements_gcs_uri=(
                                    _TEST_REASONING_ENGINE_REQUIREMENTS_GCS_URI
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
                {"extra_packages": [_TEST_REASONING_ENGINE_EXTRA_PACKAGE_PATH]},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            package_spec=types.ReasoningEngineSpec.PackageSpec(
                                dependency_files_gcs_uri=(
                                    _TEST_REASONING_ENGINE_DEPENDENCY_FILES_GCS_URI
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
                "Update the reasoning_engine",
                {"reasoning_engine": CapitalizeEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=_TEST_UPDATE_REASONING_ENGINE_OBJ,
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                        ]
                    ),
                ),
            ),
            (
                "Update the stream query engine",
                {"reasoning_engine": StreamQueryEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=(
                        _generate_reasoning_engine_with_class_methods(
                            _TEST_STREAM_QUERY_SCHEMAS
                        )
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                        ]
                    ),
                ),
            ),
            (
                "Update the operation registrable engine",
                {"reasoning_engine": OperationRegistrableEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=(
                        _generate_reasoning_engine_with_class_methods(
                            _TEST_OPERATION_REGISTRABLE_SCHEMAS
                        )
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                        ]
                    ),
                ),
            ),
            (
                "Update the operation not registered engine",
                {"reasoning_engine": OperationNotRegisteredEngine()},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=(
                        _generate_reasoning_engine_with_class_methods(
                            _TEST_OPERATION_NOT_REGISTRED_SCHEMAS
                        )
                    ),
                    update_mask=field_mask_pb2.FieldMask(
                        paths=[
                            "spec.package_spec.pickle_object_gcs_uri",
                            "spec.class_methods",
                        ]
                    ),
                ),
            ),
            (
                "Update the display_name",
                {"display_name": _TEST_REASONING_ENGINE_DISPLAY_NAME},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                        display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                    ),
                    update_mask=field_mask_pb2.FieldMask(paths=["display_name"]),
                ),
            ),
            (
                "Update the description",
                {"description": _TEST_REASONING_ENGINE_DESCRIPTION},
                types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                        description=_TEST_REASONING_ENGINE_DESCRIPTION,
                    ),
                    update_mask=field_mask_pb2.FieldMask(paths=["description"]),
                ),
            ),
        ],
    )
    def test_update_reasoning_engine(
        self,
        test_case_name,
        test_kwargs,
        want_request,
        update_reasoning_engine_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_gca_resource_mock,
    ):
        test_reasoning_engine = _generate_reasoning_engine_to_update()
        test_reasoning_engine.update(**test_kwargs)
        assert_called_with_diff(
            update_reasoning_engine_mock,
            {"request": want_request},
        )

    @pytest.mark.usefixtures("caplog")
    def test_update_reasoning_engine_warn_sys_version(
        self,
        caplog,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_gca_resource_mock,
    ):
        test_reasoning_engine = _generate_reasoning_engine_to_update()
        # Update the reasoning engine's sys_version alone will raise
        # `no updates` error, so we need to update the display_name as well.
        test_reasoning_engine.update(
            sys_version="3.10", display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME
        )
        # TODO: b/383923584: Re-enable this test once the parent issue is fixed
        # assert "Updated sys_version is not supported." in caplog.text

    def test_update_reasoning_engine_requirements_from_file(
        self,
        update_reasoning_engine_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_gca_resource_mock,
        unregister_api_methods_mock,
    ):
        test_reasoning_engine = _generate_reasoning_engine_to_update()
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="google-cloud-aiplatform==1.29.0"),
        ) as mock_file:
            test_reasoning_engine.update(
                requirements="requirements.txt",
            )
            mock_file.assert_called_with("requirements.txt")
        assert_called_with_diff(
            update_reasoning_engine_mock,
            {
                "request": types.reasoning_engine_service.UpdateReasoningEngineRequest(
                    reasoning_engine=types.ReasoningEngine(
                        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                        spec=types.ReasoningEngineSpec(
                            package_spec=types.ReasoningEngineSpec.PackageSpec(
                                requirements_gcs_uri=(
                                    _TEST_REASONING_ENGINE_REQUIREMENTS_GCS_URI
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

    def test_delete_after_create_reasoning_engine(
        self,
        create_reasoning_engine_mock,
        cloud_storage_get_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
        delete_reasoning_engine_mock,
        get_gca_resource_mock,
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
            self.test_app,
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_REASONING_ENGINE_EXTRA_PACKAGE_PATH],
        )
        create_reasoning_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_REASONING_ENGINE_OBJ,
        )
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        test_reasoning_engine.delete()
        delete_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
        )

    def test_delete_after_get_reasoning_engine(
        self,
        get_reasoning_engine_mock,
        delete_reasoning_engine_mock,
        get_gca_resource_mock,
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        test_reasoning_engine.delete()
        delete_reasoning_engine_mock.assert_called_with(
            name=test_reasoning_engine.resource_name,
        )

    def test_query_after_create_reasoning_engine(
        self,
        get_reasoning_engine_mock,
        query_reasoning_engine_mock,
        get_gca_resource_mock,
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
            self.test_app,
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            extra_packages=[_TEST_REASONING_ENGINE_EXTRA_PACKAGE_PATH],
        )
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        with mock.patch.object(_utils, "to_dict") as to_dict_mock:
            to_dict_mock.return_value = {}
            test_reasoning_engine.query(query=_TEST_QUERY_PROMPT)
            assert (
                test_reasoning_engine.query.__doc__ == CapitalizeEngine().query.__doc__
            )
            query_reasoning_engine_mock.assert_called_with(
                request=_TEST_REASONING_ENGINE_QUERY_REQUEST
            )
            to_dict_mock.assert_called_once()

    def test_query_reasoning_engine(
        self,
        get_reasoning_engine_mock,
        query_reasoning_engine_mock,
        get_gca_resource_mock,
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        with mock.patch.object(_utils, "to_dict") as to_dict_mock:
            to_dict_mock.return_value = {}
            test_reasoning_engine.query(query=_TEST_QUERY_PROMPT)
            to_dict_mock.assert_called_once()
        query_reasoning_engine_mock.assert_called_with(
            request=_TEST_REASONING_ENGINE_QUERY_REQUEST
        )

    # pytest does not allow absl.testing.parameterized.named_parameters.
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
        get_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)

        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        want_operation_schemas = []
        for want_operation_schema, api_mode in want_operation_schema_api_modes:
            want_operation_schema[_TEST_MODE_KEY_IN_SCHEMA] = api_mode
            want_operation_schemas.append(want_operation_schema)
        assert test_reasoning_engine.operation_schemas() == want_operation_schemas

    # pytest does not allow absl.testing.parameterized.named_parameters.
    @pytest.mark.parametrize(
        "test_case_name, test_engine, want_class_methods",
        [
            (
                "Default (Not Operation Registrable) Engine",
                CapitalizeEngine(),
                _TEST_NO_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Registrable Engine",
                OperationRegistrableEngine(),
                _TEST_OPERATION_REGISTRABLE_SCHEMAS,
            ),
            (
                "Operation Not Registered Engine",
                OperationNotRegisteredEngine(),
                _TEST_OPERATION_NOT_REGISTRED_SCHEMAS,
            ),
        ],
    )
    def test_create_class_methods_spec_with_registered_operations(
        self,
        test_case_name,
        test_engine,
        want_class_methods,
        types_reasoning_engine_mock,
    ):
        reasoning_engines.ReasoningEngine.create(test_engine)
        want_spec = types.ReasoningEngineSpec(
            package_spec=types.ReasoningEngineSpec.PackageSpec(
                python_version=(f"{sys.version_info.major}.{sys.version_info.minor}"),
                pickle_object_gcs_uri=_TEST_REASONING_ENGINE_GCS_URI,
            )
        )
        want_spec.class_methods.extend(want_class_methods)
        assert_called_with_diff(
            types_reasoning_engine_mock,
            {
                "name": None,
                "display_name": None,
                "description": None,
                "spec": want_spec,
            },
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
    def test_query_after_create_reasoning_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_method_docs,
        test_class_methods_spec,
        get_reasoning_engine_mock,
        query_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
                test_engine
            )

        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

        for method_name, test_doc in test_class_method_docs.items():
            with mock.patch.object(_utils, "to_dict") as to_dict_mock:
                to_dict_mock.return_value = {}
                getattr(test_reasoning_engine, method_name)(query=_TEST_QUERY_PROMPT)
                to_dict_mock.assert_called_once()

            query_reasoning_engine_mock.assert_called_with(
                request=types.QueryReasoningEngineRequest(
                    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
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
    def test_query_after_update_reasoning_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        get_reasoning_engine_mock,
        query_reasoning_engine_mock,
        update_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.append(_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME, spec=test_spec
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
                MethodToBeUnregisteredEngine()
            )
            assert hasattr(test_reasoning_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)

        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine.update(reasoning_engine=test_engine)

        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

        assert not hasattr(test_reasoning_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)
        for method_name in test_class_methods:
            with mock.patch.object(_utils, "to_dict") as to_dict_mock:
                to_dict_mock.return_value = {}
                getattr(test_reasoning_engine, method_name)(query=_TEST_QUERY_PROMPT)
                to_dict_mock.assert_called_once()

            query_reasoning_engine_mock.assert_called_with(
                request=types.QueryReasoningEngineRequest(
                    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                    input={_TEST_DEFAULT_METHOD_NAME: _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )

    def test_query_after_update_reasoning_engine_with_same_operation_schema(
        self,
        update_reasoning_engine_mock,
        unregister_api_methods_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(_TEST_OPERATION_REGISTRABLE_SCHEMAS)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
                OperationRegistrableEngine()
            )
            test_reasoning_engine.update(
                reasoning_engine=SameRegisteredOperationsEngine()
            )
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
    def test_query_reasoning_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        get_reasoning_engine_mock,
        query_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)

        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

        for method_name in test_class_methods:
            with mock.patch.object(_utils, "to_dict") as to_dict_mock:
                to_dict_mock.return_value = {}
                getattr(test_reasoning_engine, method_name)(query=_TEST_QUERY_PROMPT)
                to_dict_mock.assert_called_once()

            query_reasoning_engine_mock.assert_called_with(
                request=types.QueryReasoningEngineRequest(
                    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
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
    def test_stream_query_after_create_reasoning_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_method_docs,
        test_class_methods_spec,
        stream_query_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
                test_engine
            )

        for method_name, test_doc in test_class_method_docs.items():
            invoked_method = getattr(test_reasoning_engine, method_name)
            list(invoked_method(input=_TEST_QUERY_PROMPT))

            stream_query_reasoning_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
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
    def test_stream_query_after_update_reasoning_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        update_reasoning_engine_mock,
        stream_query_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.append(_TEST_METHOD_TO_BE_UNREGISTERED_SCHEMA)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME, spec=test_spec
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
                MethodToBeUnregisteredEngine()
            )
            assert hasattr(test_reasoning_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)

        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine.update(reasoning_engine=test_engine)

        assert not hasattr(test_reasoning_engine, _TEST_METHOD_TO_BE_UNREGISTERED_NAME)
        for method_name in test_class_methods:
            invoked_method = getattr(test_reasoning_engine, method_name)
            list(invoked_method(input=_TEST_QUERY_PROMPT))

            stream_query_reasoning_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
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
    def test_stream_query_reasoning_engine_with_operation_schema(
        self,
        test_case_name,
        test_engine,
        test_class_methods,
        test_class_methods_spec,
        stream_query_reasoning_engine_mock,
    ):
        with mock.patch.object(
            base.VertexAiResourceNoun,
            "_get_gca_resource",
        ) as get_gca_resource_mock:
            test_spec = types.ReasoningEngineSpec()
            test_spec.class_methods.extend(test_class_methods_spec)
            get_gca_resource_mock.return_value = types.ReasoningEngine(
                name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                spec=test_spec,
            )
            test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)

        for method_name in test_class_methods:
            invoked_method = getattr(test_reasoning_engine, method_name)
            list(invoked_method(input=_TEST_QUERY_PROMPT))

            stream_query_reasoning_engine_mock.assert_called_with(
                request=types.StreamQueryReasoningEngineRequest(
                    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
                    input={"input": _TEST_QUERY_PROMPT},
                    class_method=method_name,
                )
            )


@pytest.mark.usefixtures("google_auth_mock")
class TestReasoningEngineErrors:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
            staging_bucket=_TEST_STAGING_BUCKET,
        )
        self.test_app = CapitalizeEngine()

    def test_create_reasoning_engine_unspecified_staging_bucket(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
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
            reasoning_engines.ReasoningEngine.create(
                self.test_app,
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            )
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
                staging_bucket=_TEST_STAGING_BUCKET,
            )

    def test_create_reasoning_engine_no_query_method(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "reasoning_engine has neither a callable method named"
                " `query` nor a callable method named `register_operations`."
            ),
        ):
            reasoning_engines.ReasoningEngine.create(
                InvalidCapitalizeEngineWithoutQueryMethod(),
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            )

    def test_create_reasoning_engine_noncallable_query_attribute(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "reasoning_engine has neither a callable method named"
                " `query` nor a callable method named `register_operations`."
            ),
        ):
            reasoning_engines.ReasoningEngine.create(
                InvalidCapitalizeEngineWithNoncallableQueryStreamQuery(),
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            )

    def test_create_reasoning_engine_unsupported_sys_version(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(ValueError, match="Unsupported python version"):
            reasoning_engines.ReasoningEngine.create(
                self.test_app,
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
                sys_version="2.6",
            )

    def test_create_reasoning_engine_requirements_ioerror(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(IOError, match="Failed to read requirements"):
            reasoning_engines.ReasoningEngine.create(
                self.test_app,
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements="nonexistent_requirements.txt",
            )

    def test_create_reasoning_engine_nonexistent_extra_packages(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(FileNotFoundError, match="not found"):
            reasoning_engines.ReasoningEngine.create(
                self.test_app,
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
                extra_packages=_TEST_REASONING_ENGINE_INVALID_EXTRA_PACKAGES,
            )

    def test_create_reasoning_engine_with_invalid_query_method(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid query signature"):
            reasoning_engines.ReasoningEngine.create(
                InvalidCapitalizeEngineWithoutQuerySelf(),
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            )

    def test_create_reasoning_engine_with_invalid_stream_query_method(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid stream_query signature"):
            reasoning_engines.ReasoningEngine.create(
                InvalidCapitalizeEngineWithoutStreamQuerySelf(),
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            )

    def test_create_reasoning_engine_with_invalid_register_operations_method(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid register_operations signature"):
            reasoning_engines.ReasoningEngine.create(
                InvalidCapitalizeEngineWithoutRegisterOperationsSelf(),
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
            )

    def test_update_reasoning_engine_unspecified_staging_bucket(
        self,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
    ):
        with pytest.raises(
            ValueError,
            match="Please provide a `staging_bucket`",
        ):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            importlib.reload(initializer)
            importlib.reload(aiplatform)
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
            )
            test_reasoning_engine.update(
                reasoning_engine=InvalidCapitalizeEngineWithoutQueryMethod(),
            )
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                credentials=_TEST_CREDENTIALS,
                staging_bucket=_TEST_STAGING_BUCKET,
            )

    def test_update_reasoning_engine_no_query_method(
        self,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "reasoning_engine has neither a callable method named"
                " `query` nor a callable method named `register_operations`."
            ),
        ):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update(
                reasoning_engine=InvalidCapitalizeEngineWithoutQueryMethod(),
            )

    def test_update_reasoning_engine_noncallable_query_attribute(
        self,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(
            TypeError,
            match=(
                "reasoning_engine has neither a callable method named"
                " `query` nor a callable method named `register_operations`."
            ),
        ):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update(
                reasoning_engine=InvalidCapitalizeEngineWithNoncallableQueryStreamQuery(),
            )

    def test_update_reasoning_engine_requirements_ioerror(
        self,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(IOError, match="Failed to read requirements"):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update(
                requirements="nonexistent_requirements.txt",
            )

    def test_update_reasoning_engine_nonexistent_extra_packages(
        self,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(FileNotFoundError, match="not found"):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update(
                extra_packages=_TEST_REASONING_ENGINE_INVALID_EXTRA_PACKAGES,
            )

    def test_update_reasoning_engine_with_invalid_query_method(
        self,
        update_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with pytest.raises(ValueError, match="Invalid query signature"):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update(
                reasoning_engine=InvalidCapitalizeEngineWithoutQuerySelf(),
            )

    def test_update_reasoning_engine_with_no_updates(
        self,
        update_reasoning_engine_mock,
    ):
        with pytest.raises(
            ValueError,
            match=(
                "At least one of `reasoning_engine`, `requirements`, "
                "`extra_packages`, `display_name`, or `description` "
                "must be specified."
            ),
        ):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update()

    def test_create_class_methods_spec_with_registered_operation_not_found(self):
        with pytest.raises(
            ValueError,
            match=(
                "Method `missing_method` defined in `register_operations`"
                " not found on ReasoningEngine."
            ),
        ):
            reasoning_engines.ReasoningEngine.create(
                RegisteredOperationNotExistEngine()
            )

    def test_update_class_methods_spec_with_registered_operation_not_found(self):
        with pytest.raises(
            ValueError,
            match=(
                "Method `missing_method` defined in `register_operations`"
                " not found on ReasoningEngine."
            ),
        ):
            test_reasoning_engine = _generate_reasoning_engine_to_update()
            test_reasoning_engine.update(
                reasoning_engine=RegisteredOperationNotExistEngine()
            )

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
                    "Failed to register API methods: {Operation schema {'name':"
                    " 'query'} does not contain an `api_mode` field.}"
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
                    "Failed to register API methods: {Operation schema"
                    " {'api_mode': ''} does not contain a `name` field.}"
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
                    "Failed to register API methods: {Unsupported api mode:"
                    " `UNKNOWN_API_MODE`, Supported modes are:"
                    " `` and `stream`.}"
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
            _reasoning_engines.ReasoningEngine,
            "operation_schemas",
        ) as mock_operation_schemas:
            mock_operation_schemas.return_value = test_operation_schemas
            _reasoning_engines.ReasoningEngine(_TEST_REASONING_ENGINE_RESOURCE_NAME)

        assert want_log_output in caplog.text


def _generate_reasoning_engine_to_update() -> "reasoning_engines.ReasoningEngine":
    test_reasoning_engine = reasoning_engines.ReasoningEngine.create(CapitalizeEngine())
    # Resource name is required for the update method.
    test_reasoning_engine._gca_resource = types.ReasoningEngine(
        name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
    )
    return test_reasoning_engine


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
                place_photo_query,
                ["photo_reference"],
                {
                    "name": "place_photo_query",
                    "description": "Returns the photo for a given reference.",
                    "parameters": {
                        "properties": {
                            "photo_reference": {"type": "string"},
                            "maxwidth": {"type": "integer"},
                            "maxheight": {"type": "integer", "nullable": True},
                        },
                        "required": ["photo_reference"],
                        "type": "object",
                    },
                },
            ),
        ],
    )
    def test_generate_schemas(self, func, required, expected_operation):
        result = _utils.generate_schema(func, required=required)
        assert result == expected_operation


class TestToProto:
    @pytest.mark.parametrize(
        "obj, expected_proto",
        [
            (
                {},
                struct_pb2.Struct(fields={}),
            ),
            (
                {"a": 1, "b": 2},
                struct_pb2.Struct(
                    fields={
                        "a": struct_pb2.Value(number_value=1),
                        "b": struct_pb2.Value(number_value=2),
                    },
                ),
            ),
            (
                struct_pb2.Struct(fields={}),
                struct_pb2.Struct(fields={}),
            ),
            (
                struct_pb2.Struct(
                    fields={
                        "a": struct_pb2.Value(number_value=1),
                        "b": struct_pb2.Value(number_value=2),
                    },
                ),
                struct_pb2.Struct(
                    fields={
                        "a": struct_pb2.Value(number_value=1),
                        "b": struct_pb2.Value(number_value=2),
                    },
                ),
            ),
        ],
    )
    def test_to_proto(self, obj, expected_proto):
        result = _utils.to_proto(obj)
        assert _utils.to_dict(result) == _utils.to_dict(expected_proto)

    # class TestDataclassToDict(parameterized.TestCase):
    #     @parameterized.named_parameters(
    #         dict(
    #             testcase_name="serializable_dataclass",
    #             obj=SerializableClass(name="test", value=42),
    #             expected_dict={"name": "test", "value": 42},
    #         ),
    #         dict(
    #             testcase_name="nested_dataclass",
    #             obj=NestedClass(
    #                 name="outer", inner=SerializableClass(name="inner", value=10)
    #             ),
    #             expected_dict={"name": "outer", "inner": {"name": "inner", "value": 10}},
    #         ),
    #         dict(
    #             testcase_name="list_dataclass",
    #             obj=ListClass(name="list_test", items=[1, 2, 3]),
    #             expected_dict={"name": "list_test", "items": [1, 2, 3]},
    #         ),
    #         dict(
    #             testcase_name="empty_list_dataclass",
    #             obj=ListClass(name="list_test", items=[]),
    #             expected_dict={"name": "list_test", "items": []},
    #         ),
    #     )
    #     def test_dataclass_to_dict_success(self, obj, expected_dict):
    #         result = _utils.dataclass_to_dict(obj)
    #         self.assertEqual(result, expected_dict)

    @pytest.mark.parametrize(
        "obj, expected_exception",
        [
            (
                "not a dataclass",
                TypeError,
            ),
            (
                NonSerializableClass(name="test", date=datetime.datetime.now()),
                TypeError,
            ),
        ],
    )
    def test_dataclass_to_dict_failure(self, obj, expected_exception):
        with pytest.raises(expected_exception):
            _utils.dataclass_to_dict(obj)


class ToParsedJsonTest:
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
