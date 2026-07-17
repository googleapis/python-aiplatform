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
