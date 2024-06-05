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
import importlib
import json
from unittest import mock

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils as aip_utils
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.services import extension_execution_service
from google.cloud.aiplatform_v1beta1.services import extension_registry_service
from vertexai.preview import extensions
from vertexai.reasoning_engines import _utils
import pytest


_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_AUTH_CONFIG = types.AuthConfig(auth_type="GOOGLE_SERVICE_ACCOUNT_AUTH")
_TEST_RESOURCE_ID = "1028944691210842416"
_TEST_OPEN_API_GCS_URI = "gs://vertex-extension-experiment/code_interpreter.yaml"
_TEST_OPEN_API_YAML = """
      openapi: 3.0.0
      info:
        title: SomeApi
        version: 1.0.0
      servers:
        - url: https://www.someapi.com
      paths:
        /path1:
          get:
            summary: Request description
            operationId: requestSomething
            parameters:
              - name: request_parameter
                in: query
                required: true
                schema:
                  type: string
            responses:
              '200':
                description: Response description
                content:
                  application/json:
                    schema:
                      type: object
                      properties:
                        response_parameter:
                          type: string"""
_TEST_EXTENSION_MANIFEST_NAME = "code_interpreter_tool"
_TEST_EXTENSION_MANIFEST_DESCRIPTION = "Google Code Interpreter Extension"
_TEST_EXTENSION_MANIFEST_WITH_GCS_URI_OBJ = types.ExtensionManifest(
    name=_TEST_EXTENSION_MANIFEST_NAME,
    description=_TEST_EXTENSION_MANIFEST_DESCRIPTION,
    api_spec=types.ExtensionManifest.ApiSpec(
        open_api_gcs_uri=_TEST_OPEN_API_GCS_URI,
    ),
    auth_config=_TEST_AUTH_CONFIG,
)
_TEST_EXTENSION_MANIFEST_WITH_YAML_OBJ = types.ExtensionManifest(
    name=_TEST_EXTENSION_MANIFEST_NAME,
    description=_TEST_EXTENSION_MANIFEST_DESCRIPTION,
    api_spec=types.ExtensionManifest.ApiSpec(
        open_api_yaml=_TEST_OPEN_API_YAML,
    ),
    auth_config=_TEST_AUTH_CONFIG,
)
_TEST_EXTENSION_MANIFEST_WITH_NO_API_SPEC = types.ExtensionManifest(
    name=_TEST_EXTENSION_MANIFEST_NAME,
    description=_TEST_EXTENSION_MANIFEST_DESCRIPTION,
    auth_config=_TEST_AUTH_CONFIG,
)
_TEST_LOCATION = "us-central1"
_TEST_PROJECT = "test-project"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_EXTENSION_RESOURCE_NAME = f"{_TEST_PARENT}/extensions/{_TEST_RESOURCE_ID}"
_TEST_EXTENSION_DISPLAY_NAME = "Extension Display Name"
_TEST_EXTENSION_OBJ = types.Extension(
    name=_TEST_EXTENSION_RESOURCE_NAME,
    display_name=_TEST_EXTENSION_DISPLAY_NAME,
    manifest=_TEST_EXTENSION_MANIFEST_WITH_GCS_URI_OBJ,
)
_TEST_EXTENSION_WITH_YAML_API_SPEC_OBJ = types.Extension(
    name=_TEST_EXTENSION_RESOURCE_NAME,
    display_name=_TEST_EXTENSION_DISPLAY_NAME,
    manifest=_TEST_EXTENSION_MANIFEST_WITH_YAML_OBJ,
)
_TEST_EXTENSION_WITH_NO_API_SPEC_OBJ = types.Extension(
    name=_TEST_EXTENSION_RESOURCE_NAME,
    display_name=_TEST_EXTENSION_DISPLAY_NAME,
    manifest=_TEST_EXTENSION_MANIFEST_WITH_NO_API_SPEC,
)
_TEST_EXTENSION_OPERATION_ID = "search"
_TEST_QUERY_PROMPT = "Find the first fibonacci number greater than 999"
_TEST_EXTENSION_OPERATION_PARAMS = {"query": _TEST_QUERY_PROMPT}
_TEST_RESPONSE_CONTENT = json.dumps(
    {
        "execution_error": "",
        "execution_result": "The first fibonacci number greater than 999 is 1597\n",
        "generated_code": "```python\n"
        "def fibonacci(n):\n"
        "    a, b = 0, 1\n"
        "    for _ in range(n):\n"
        "        a, b = b, a + b\n"
        "    return a\n"
        "\n"
        "# Find the first fibonacci number greater than 999\n"
        "n = 1\n"
        "while fibonacci(n) <= 999:\n"
        "    n += 1\n"
        "\n"
        'print(f"The first fibonacci number greater than 999 is '
        '{fibonacci(n)}")\n'
        "```",
        "output_files": [],
    }
)
_TEST_EXECUTE_EXTENSION_RESPONSE = types.ExecuteExtensionResponse(
    content=_TEST_RESPONSE_CONTENT,
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.fixture
def get_extension_mock():
    with mock.patch.object(
        extension_registry_service.ExtensionRegistryServiceClient,
        "get_extension",
    ) as get_extension_mock:
        api_client_mock = mock.Mock(
            spec=extension_registry_service.ExtensionRegistryServiceClient,
        )
        api_client_mock.get_extension.return_value = _TEST_EXTENSION_OBJ
        get_extension_mock.return_value = api_client_mock
        yield get_extension_mock


@pytest.fixture
def create_extension_mock():
    with mock.patch.object(
        extension_registry_service.ExtensionRegistryServiceClient,
        "import_extension",
    ) as create_extension_mock:
        create_extension_lro_mock = mock.Mock(ga_operation.Operation)
        create_extension_lro_mock.result.return_value = _TEST_EXTENSION_OBJ
        create_extension_mock.return_value = create_extension_lro_mock
        yield create_extension_mock


@pytest.fixture
def execute_extension_mock():
    with mock.patch.object(
        extension_execution_service.ExtensionExecutionServiceClient, "execute_extension"
    ) as execute_extension_mock:
        execute_extension_mock.return_value.content = _TEST_RESPONSE_CONTENT
        yield execute_extension_mock


@pytest.fixture
def delete_extension_mock():
    with mock.patch.object(
        extension_registry_service.ExtensionRegistryServiceClient,
        "delete_extension",
    ) as delete_extension_mock:
        delete_extension_lro_mock = mock.Mock(ga_operation.Operation)
        delete_extension_lro_mock.result.return_value = None
        delete_extension_mock.return_value = delete_extension_lro_mock
        yield delete_extension_mock


@pytest.fixture
def to_dict_mock():
    with mock.patch.object(_utils, "to_dict") as to_dict_mock:
        to_dict_mock.return_value = {}
        yield to_dict_mock


@pytest.fixture
def load_yaml_mock():
    with mock.patch.object(
        aip_utils.yaml_utils,
        "load_yaml",
        autospec=True,
    ) as load_yaml_mock:
        load_yaml_mock.return_value = lambda x: x
        yield load_yaml_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestExtension:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_get_extension(self, get_extension_mock):
        extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )

    def test_create_extension(
        self,
        create_extension_mock,
        get_extension_mock,
        load_yaml_mock,
    ):
        extensions.Extension.create(
            extension_name=_TEST_EXTENSION_RESOURCE_NAME,
            display_name=_TEST_EXTENSION_DISPLAY_NAME,
            manifest=_TEST_EXTENSION_MANIFEST_WITH_GCS_URI_OBJ,
        )
        create_extension_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            extension=_TEST_EXTENSION_OBJ,
        )
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )

    def test_delete_after_create_extension(
        self,
        create_extension_mock,
        get_extension_mock,
        delete_extension_mock,
        load_yaml_mock,
    ):
        test_extension = extensions.Extension.create(
            extension_name=_TEST_EXTENSION_RESOURCE_NAME,
            display_name=_TEST_EXTENSION_DISPLAY_NAME,
            manifest=_TEST_EXTENSION_MANIFEST_WITH_GCS_URI_OBJ,
        )
        create_extension_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            extension=_TEST_EXTENSION_OBJ,
        )
        get_extension_mock.assert_any_call(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_OBJ
        test_extension.delete()
        delete_extension_mock.assert_called_once_with(
            name=test_extension.resource_name,
        )

    def test_delete_after_get_extension(
        self,
        get_extension_mock,
        delete_extension_mock,
        load_yaml_mock,
    ):
        test_extension = extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_any_call(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_OBJ
        test_extension.delete()
        delete_extension_mock.assert_called_once_with(
            name=test_extension.resource_name,
        )

    def test_execute_extension(
        self,
        get_extension_mock,
        execute_extension_mock,
        load_yaml_mock,
    ):
        test_extension = extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_OBJ
        test_extension.execute(
            operation_id=_TEST_EXTENSION_OPERATION_ID,
            operation_params=_TEST_EXTENSION_OPERATION_PARAMS,
            runtime_auth_config=_TEST_AUTH_CONFIG,
        )
        execute_extension_mock.assert_called_once_with(
            types.ExecuteExtensionRequest(
                name=_TEST_EXTENSION_RESOURCE_NAME,
                operation_id=_TEST_EXTENSION_OPERATION_ID,
                operation_params=_utils.to_proto(
                    _TEST_EXTENSION_OPERATION_PARAMS,
                ),
                runtime_auth_config=_TEST_AUTH_CONFIG,
            ),
        )

    def test_api_spec_from_yaml(self, get_extension_mock, load_yaml_mock):
        test_extension = extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_WITH_YAML_API_SPEC_OBJ
        test_extension.api_spec() == {}

    def test_no_api_spec(self, get_extension_mock, load_yaml_mock):
        test_extension = extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_WITH_NO_API_SPEC_OBJ
        test_extension.api_spec() == {}

    def test_api_spec_from_gcs_uri(
        self,
        get_extension_mock,
        load_yaml_mock,
    ):
        test_extension = extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_OBJ
        test_extension.api_spec()
        load_yaml_mock.assert_called_once_with(_TEST_OPEN_API_GCS_URI)

    def test_operation_schemas(self, get_extension_mock):
        test_extension = extensions.Extension(_TEST_RESOURCE_ID)
        get_extension_mock.assert_called_once_with(
            name=_TEST_EXTENSION_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        test_extension._gca_resource = _TEST_EXTENSION_OBJ
        test_extension.operation_schemas()
