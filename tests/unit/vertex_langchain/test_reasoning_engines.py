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
import importlib
import sys
import tarfile
from absl.testing import parameterized
from typing import Optional
from unittest import mock

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import storage
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.services import reasoning_engine_execution_service
from google.cloud.aiplatform_v1beta1.services import reasoning_engine_service
from vertexai.preview import reasoning_engines
from vertexai.reasoning_engines import _utils
from vertexai.reasoning_engines import _reasoning_engines
import pytest


class CapitalizeEngine:
    """A sample Reasoning Engine."""

    def set_up(self):
        pass

    def query(self, unused_arbitrary_string_name: str) -> str:
        """Runs the engine."""
        return unused_arbitrary_string_name.upper()

    def clone(self):
        return self


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
_TEST_GCS_DIR_NAME = _reasoning_engines._DEFAULT_GCS_DIR_NAME
_TEST_BLOB_FILENAME = _reasoning_engines._BLOB_FILENAME
_TEST_REQUIREMENTS_FILE = _reasoning_engines._REQUIREMENTS_FILE
_TEST_EXTRA_PACKAGES_FILE = _reasoning_engines._EXTRA_PACKAGES_FILE
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
        schema_name="CapitalizeEngine_query",
    )
)
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
_TEST_REASONING_ENGINE_QUERY_REQUEST = types.QueryReasoningEngineRequest(
    name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
    input={"query": _TEST_QUERY_PROMPT},
)
_TEST_REASONING_ENGINE_QUERY_RESPONSE = {}
_TEST_REASONING_ENGINE_OPERATION_SCHEMAS = []
_TEST_REASONING_ENGINE_SYS_VERSION = "3.10"


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


@pytest.fixture(scope="module")
def to_dict_mock():
    with mock.patch.object(_utils, "to_dict") as to_dict_mock:
        to_dict_mock.return_value = {}
        yield to_dict_mock


class InvalidCapitalizeEngineWithoutQuerySelf:
    """A sample Reasoning Engine with an invalid query method."""

    def set_up(self):
        pass

    def query() -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithoutQueryMethod:
    """A sample Reasoning Engine without a query method."""

    def set_up(self):
        pass

    def invoke(self) -> str:
        """Runs the engine."""
        return "RESPONSE"


class InvalidCapitalizeEngineWithNoncallableQuery:
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

    def test_get_reasoning_engine(self, get_reasoning_engine_mock):
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
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
            self.test_app,
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_reasoning_engine._gca_resource = _TEST_REASONING_ENGINE_OBJ
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
        assert "does not support user-defined resource IDs" in caplog.text

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
        assert f"is inconsistent with {sys.version_info=}" in caplog.text

    def test_create_reasoning_engine_requirements_from_file(
        self,
        create_reasoning_engine_mock,
        cloud_storage_create_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
    ):
        with mock.patch(
            "builtins.open",
            mock.mock_open(read_data="google-cloud-aiplatform==1.29.0"),
        ) as mock_file:
            test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
                self.test_app,
                display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
                requirements="requirements.txt",
            )
        mock_file.assert_called_with("requirements.txt")
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_reasoning_engine._gca_resource = _TEST_REASONING_ENGINE_OBJ
        create_reasoning_engine_mock.assert_called_with(
            parent=_TEST_PARENT,
            reasoning_engine=_TEST_INPUT_REASONING_ENGINE_OBJ,
        )
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )

    def test_delete_after_create_reasoning_engine(
        self,
        create_reasoning_engine_mock,
        cloud_storage_get_bucket_mock,
        tarfile_open_mock,
        cloudpickle_dump_mock,
        get_reasoning_engine_mock,
        delete_reasoning_engine_mock,
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine.create(
            self.test_app,
            display_name=_TEST_REASONING_ENGINE_DISPLAY_NAME,
            requirements=_TEST_REASONING_ENGINE_REQUIREMENTS,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_reasoning_engine._gca_resource = _TEST_REASONING_ENGINE_OBJ
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
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_reasoning_engine._gca_resource = _TEST_REASONING_ENGINE_OBJ
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        test_reasoning_engine.delete()
        delete_reasoning_engine_mock.assert_called_with(
            name=test_reasoning_engine.resource_name,
        )

    def test_query_reasoning_engine(
        self,
        get_reasoning_engine_mock,
        query_reasoning_engine_mock,
        to_dict_mock,
    ):
        test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_reasoning_engine._gca_resource = _TEST_REASONING_ENGINE_OBJ
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        test_reasoning_engine.query(query=_TEST_QUERY_PROMPT)
        query_reasoning_engine_mock.assert_called_with(
            request=_TEST_REASONING_ENGINE_QUERY_REQUEST
        )
        to_dict_mock.assert_called_once()

    def test_operation_schemas(self, get_reasoning_engine_mock):
        test_reasoning_engine = reasoning_engines.ReasoningEngine(_TEST_RESOURCE_ID)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_reasoning_engine._gca_resource = _TEST_REASONING_ENGINE_OBJ
        test_reasoning_engine._operation_schemas = (
            _TEST_REASONING_ENGINE_OPERATION_SCHEMAS
        )
        get_reasoning_engine_mock.assert_called_with(
            name=_TEST_REASONING_ENGINE_RESOURCE_NAME,
            retry=_TEST_RETRY,
        )
        assert test_reasoning_engine.operation_schemas() == (
            _TEST_REASONING_ENGINE_OPERATION_SCHEMAS
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
            match="does not have a callable method named `query`",
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
            match="does not have a callable method named `query`",
        ):
            reasoning_engines.ReasoningEngine.create(
                InvalidCapitalizeEngineWithNoncallableQuery(),
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


class TestGenerateSchema(parameterized.TestCase):
    @parameterized.named_parameters(
        dict(
            testcase_name="place_tool_query",
            func=place_tool_query,
            required=["city", "activity"],
            expected_operation={
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
        dict(
            testcase_name="place_photo_query",
            func=place_photo_query,
            required=["photo_reference"],
            expected_operation={
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
    )
    def test_generate_schemas(self, func, required, expected_operation):
        result = _utils.generate_schema(func, required=required)
        self.assertDictEqual(result, expected_operation)
