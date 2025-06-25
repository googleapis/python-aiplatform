# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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
from google import auth
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.services import example_store_service
from vertexai import generative_models
from vertexai.preview import example_stores
from vertexai.example_stores._example_stores import (
    _coerce_to_dict,
)
from google.protobuf import json_format

import mock
import pytest

TEST_PROJECT = "test-project"
TEST_LOCATION = "us-central1"
TEST_RESOURCE_ID = "456"
TEST_RESOURCE_NAME = f"projects/{TEST_PROJECT}/locations/{TEST_LOCATION}/exampleStores/{TEST_RESOURCE_ID}"
TEST_EMBEDDING_MODEL = "text-embedding-004"
TEST_EXAMPLE_STORE_DISPLAY_NAME = "Test Example Store"
TEST_EXAMPLE_STORE_CONFIG = types.ExampleStoreConfig(
    vertex_embedding_model=TEST_EMBEDDING_MODEL,
)
TEST_EXAMPLE_STORE_OBJ = types.ExampleStore(
    name=TEST_RESOURCE_NAME,
    display_name=TEST_EXAMPLE_STORE_DISPLAY_NAME,
    example_store_config=TEST_EXAMPLE_STORE_CONFIG,
)
TEST_SEARCH_KEY = "What's 212 degrees in celsius?"
TEST_SEARCH_KEY_GENERATION_METHOD = (
    types.StoredContentsExample.SearchKeyGenerationMethod(
        last_entry=types.StoredContentsExample.SearchKeyGenerationMethod.LastEntry(),
    )
)
TEST_SEARCH_KEY_GENERATION_METHOD_DICT = json.loads(
    json_format.MessageToJson(
        TEST_SEARCH_KEY_GENERATION_METHOD._pb,
        preserving_proto_field_name=True,
    )
)
TEST_CONTENT = types.Content(
    role="user",
    parts=[types.Part(text=TEST_SEARCH_KEY)],
)
TEST_CONTENT_DICT = json.loads(
    json_format.MessageToJson(
        TEST_CONTENT._pb,
        preserving_proto_field_name=True,
    )
)
TEST_CONTENT_2 = types.Content(
    role="model",
    parts=[types.Part(function_call=types.FunctionCall(name="convert_temp"))],
)
TEST_CONTENT_2_DICT = json.loads(
    json_format.MessageToJson(
        TEST_CONTENT_2._pb,
        preserving_proto_field_name=True,
    )
)
TEST_EXPECTED_CONTENT = types.ContentsExample.ExpectedContent(
    content=TEST_CONTENT_2,
)
TEST_EXPECTED_CONTENT_DICT = json.loads(
    json_format.MessageToJson(
        TEST_EXPECTED_CONTENT._pb,
        preserving_proto_field_name=True,
    )
)
TEST_CONTENTS_EXAMPLE = types.ContentsExample(
    contents=[TEST_CONTENT],
    expected_contents=[TEST_EXPECTED_CONTENT],
)
TEST_CONTENTS_EXAMPLE_DICT = json.loads(
    json_format.MessageToJson(
        TEST_CONTENTS_EXAMPLE._pb,
        preserving_proto_field_name=True,
    )
)
TEST_CAMEL_CASE_CONTENTS_EXAMPLE_DICT = json.loads(
    json_format.MessageToJson(TEST_CONTENTS_EXAMPLE._pb)
)
TEST_STORED_CONTENTS_EXAMPLE = types.StoredContentsExample(
    contents_example=TEST_CONTENTS_EXAMPLE,
    search_key_generation_method=TEST_SEARCH_KEY_GENERATION_METHOD,
)
TEST_STORED_CONTENTS_EXAMPLE_DICT = json.loads(
    json_format.MessageToJson(
        TEST_STORED_CONTENTS_EXAMPLE._pb,
        preserving_proto_field_name=True,
    )
)
TEST_CAMEL_CASE_STORED_CONTENTS_EXAMPLE_DICT = json.loads(
    json_format.MessageToJson(TEST_STORED_CONTENTS_EXAMPLE._pb)
)
TEST_EXAMPLE = types.Example(stored_contents_example=TEST_STORED_CONTENTS_EXAMPLE)
TEST_EXAMPLE_DICT = json.loads(
    json_format.MessageToJson(
        TEST_EXAMPLE._pb,
        preserving_proto_field_name=True,
    )
)
TEST_CAMEL_CASE_EXAMPLE_DICT = json.loads(json_format.MessageToJson(TEST_EXAMPLE._pb))
TEST_GENERATIVE_CONTENT_DICT = generative_models.Content.from_dict(TEST_CONTENT_DICT)
TEST_GENERATIVE_CONTENT_2_DICT = generative_models.Content.from_dict(
    TEST_CONTENT_2_DICT
)
TEST_GENERATIVE_EXPECTED_CONTENT_DICT = example_stores.ExpectedContent(
    content=generative_models.Content.from_dict(TEST_CONTENT_2_DICT),
)
TEST_GENERATIVE_CONTENTS_EXAMPLE_DICT = example_stores.ContentsExample(
    contents=[TEST_GENERATIVE_CONTENT_DICT],
    expected_contents=[TEST_GENERATIVE_EXPECTED_CONTENT_DICT],
)
TEST_GENERATIVE_STORED_CONTENTS_EXAMPLE_DICT = example_stores.StoredContentsExample(
    contents_example=TEST_GENERATIVE_CONTENTS_EXAMPLE_DICT,
    search_key_generation_method=TEST_SEARCH_KEY_GENERATION_METHOD_DICT,
)
TEST_GENERATIVE_EXAMPLE_DICT = example_stores.Example(
    stored_contents_example=TEST_GENERATIVE_STORED_CONTENTS_EXAMPLE_DICT,
)
TEST_STORED_CONTENTS_EXAMPLE_PARAMETERS_1 = (
    example_stores.StoredContentsExampleParameters(
        stored_contents_example_key=TEST_SEARCH_KEY,
        function_names=example_stores.ExamplesArrayFilter(
            values=[],
            array_operator=example_stores.ArrayOperator.CONTAINS_ANY,
        ),
    )
)
TEST_STORED_CONTENTS_EXAMPLE_PARAMETERS_2 = (
    example_stores.StoredContentsExampleParameters(
        stored_contents_example_key=example_stores.ContentSearchKey(
            contents=[TEST_CONTENT_2_DICT],
            search_key_generation_method=TEST_SEARCH_KEY_GENERATION_METHOD_DICT,
        ),
        function_names=example_stores.ExamplesArrayFilter(
            values=["convert_temp"],
            array_operator=example_stores.ArrayOperator.CONTAINS_ALL,
        ),
    )
)


# TODO: Move to conftest.py when publishing
@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            "test-project",
        )
        yield google_auth_mock


@pytest.fixture
def create_example_store_mock():
    with mock.patch.object(
        example_store_service.ExampleStoreServiceClient,
        "create_example_store",
    ) as create_example_store_mock:
        yield create_example_store_mock


@pytest.fixture
def get_example_store_mock():
    with mock.patch.object(
        example_store_service.ExampleStoreServiceClient,
        "get_example_store",
    ) as get_example_store_mock:
        yield get_example_store_mock


@pytest.fixture
def upsert_examples_mock():
    with mock.patch.object(
        example_store_service.ExampleStoreServiceClient,
        "upsert_examples",
    ) as upsert_examples_mock:
        yield upsert_examples_mock


@pytest.fixture
def search_examples_mock():
    with mock.patch.object(
        example_store_service.ExampleStoreServiceClient,
        "search_examples",
    ) as search_examples_mock:
        yield search_examples_mock


@pytest.fixture
def fetch_examples_mock():
    with mock.patch.object(
        example_store_service.ExampleStoreServiceClient,
        "fetch_examples",
    ) as fetch_examples_mock:
        yield fetch_examples_mock


@pytest.fixture
def remove_examples_mock():
    with mock.patch.object(
        example_store_service.ExampleStoreServiceClient,
        "remove_examples",
    ) as remove_examples_mock:
        yield remove_examples_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestExampleStores:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=TEST_PROJECT)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    def test_create_example_store_success(self, create_example_store_mock):
        example_stores.ExampleStore.create(
            example_store_name=TEST_RESOURCE_NAME,
            example_store_config=TEST_EXAMPLE_STORE_CONFIG,
            display_name=TEST_EXAMPLE_STORE_DISPLAY_NAME,
        )
        create_example_store_mock.assert_called_once_with(
            parent=aiplatform.initializer.global_config.common_location_path(),
            example_store=TEST_EXAMPLE_STORE_OBJ,
        )

    def test_get_example_store_success(self, get_example_store_mock):
        example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
        get_example_store_mock.assert_called_with(
            name=TEST_RESOURCE_NAME,
            retry=aiplatform.base._DEFAULT_RETRY,
        )
        # Manually set _gca_resource here to prevent the mocks from propagating.
        example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
        assert example_store.resource_name == TEST_RESOURCE_NAME

    @pytest.mark.usefixtures("get_example_store_mock")
    def test_upsert_examples_success(self, upsert_examples_mock):
        example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
        example_store.upsert_examples(
            [
                TEST_CONTENTS_EXAMPLE_DICT,
                TEST_STORED_CONTENTS_EXAMPLE_DICT,
                TEST_EXAMPLE_DICT,
                TEST_CAMEL_CASE_CONTENTS_EXAMPLE_DICT,
                TEST_CAMEL_CASE_STORED_CONTENTS_EXAMPLE_DICT,
                TEST_CAMEL_CASE_EXAMPLE_DICT,
                TEST_CONTENTS_EXAMPLE,
                TEST_STORED_CONTENTS_EXAMPLE,
                TEST_EXAMPLE,
            ]
        )
        upsert_examples_mock.assert_called_once_with(
            types.UpsertExamplesRequest(
                example_store=TEST_RESOURCE_NAME,
                examples=[
                    TEST_EXAMPLE,  # from TEST_CONTENTS_EXAMPLE_DICT
                    TEST_EXAMPLE,  # from TEST_STORED_CONTENTS_EXAMPLE_DICT
                    TEST_EXAMPLE,  # from TEST_EXAMPLE_DICT
                    TEST_EXAMPLE,  # from TEST_CAMEL_CASE_CONTENTS_EXAMPLE_DICT
                    TEST_EXAMPLE,  # from TEST_CAMEL_CASE_STORED_CONTENTS_EXAMPLE_DICT
                    TEST_EXAMPLE,  # from TEST_CAMEL_CASE_EXAMPLE_DICT
                    TEST_EXAMPLE,  # from TEST_CONTENTS_EXAMPLE
                    TEST_EXAMPLE,  # from TEST_STORED_CONTENTS_EXAMPLE
                    TEST_EXAMPLE,  # from TEST_EXAMPLE
                ],
            ),
        )

    @pytest.mark.usefixtures("get_example_store_mock")
    def test_search_examples_search_key_success(self, search_examples_mock):
        example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
        example_store.search_examples(
            TEST_STORED_CONTENTS_EXAMPLE_PARAMETERS_1,
            top_k=5,
        )
        search_examples_mock.assert_called_once_with(
            types.SearchExamplesRequest(
                example_store=TEST_RESOURCE_NAME,
                stored_contents_example_parameters={
                    "search_key": TEST_SEARCH_KEY,
                    "function_names": example_stores.ExamplesArrayFilter(
                        values=[],
                        array_operator=example_stores.ArrayOperator.CONTAINS_ANY,
                    ),
                },
                top_k=5,
            ),
        )

    @pytest.mark.usefixtures("get_example_store_mock")
    def test_search_examples_search_content_key_success(self, search_examples_mock):
        example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
        example_store.search_examples(
            TEST_STORED_CONTENTS_EXAMPLE_PARAMETERS_2,
            top_k=10,
        )
        search_examples_mock.assert_called_once_with(
            types.SearchExamplesRequest(
                example_store=TEST_RESOURCE_NAME,
                stored_contents_example_parameters={
                    "content_search_key": example_stores.ContentSearchKey(
                        contents=[TEST_CONTENT_2_DICT],
                        search_key_generation_method=TEST_SEARCH_KEY_GENERATION_METHOD_DICT,
                    ),
                    "function_names": example_stores.ExamplesArrayFilter(
                        values=["convert_temp"],
                        array_operator=example_stores.ArrayOperator.CONTAINS_ALL,
                    ),
                },
                top_k=10,
            )
        )

    @pytest.mark.usefixtures("get_example_store_mock")
    def test_fetch_examples_success(self, fetch_examples_mock):
        example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
        example_store.fetch_examples(
            filter=example_stores.StoredContentsExampleFilter(
                search_keys=[TEST_SEARCH_KEY],
                function_names=example_stores.ExamplesArrayFilter(
                    values=["convert_temp"],
                    array_operator=example_stores.ArrayOperator.CONTAINS_ALL,
                ),
            ),
        )
        fetch_examples_mock.assert_called_once_with(
            types.FetchExamplesRequest(
                example_store=TEST_RESOURCE_NAME,
                stored_contents_example_filter=types.StoredContentsExampleFilter(
                    search_keys=[TEST_SEARCH_KEY],
                    function_names=types.ExamplesArrayFilter(
                        values=["convert_temp"],
                        array_operator=types.ExamplesArrayFilter.ArrayOperator.CONTAINS_ALL,
                    ),
                ),
            )
        )

    @pytest.mark.usefixtures("get_example_store_mock")
    def test_remove_examples_success(self, remove_examples_mock):
        example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
        # Manually set _gca_resource here to prevent the mocks from propagating.
        example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
        example_store.remove_examples(
            filter=example_stores.StoredContentsExampleFilter(
                search_keys=[TEST_SEARCH_KEY],
                function_names=example_stores.ExamplesArrayFilter(
                    values=["convert_temp"],
                    array_operator=example_stores.ArrayOperator.CONTAINS_ALL,
                ),
            ),
        )
        remove_examples_mock.assert_called_once_with(
            types.RemoveExamplesRequest(
                example_store=TEST_RESOURCE_NAME,
                stored_contents_example_filter=types.StoredContentsExampleFilter(
                    search_keys=[TEST_SEARCH_KEY],
                    function_names=types.ExamplesArrayFilter(
                        values=["convert_temp"],
                        array_operator=types.ExamplesArrayFilter.ArrayOperator.CONTAINS_ALL,
                    ),
                ),
            )
        )


@pytest.mark.usefixtures("google_auth_mock")
class TestExampleStoreErrors:
    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=TEST_PROJECT)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("get_example_store_mock", "upsert_examples_mock")
    def test_upsert_examples_example_type_error(self):
        with pytest.raises(TypeError, match="Unsupported example type:"):
            example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
            # Manually set _gca_resource here to prevent the mocks from propagating.
            example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
            example_store.upsert_examples(["invalid example type"])

    @pytest.mark.usefixtures("get_example_store_mock", "upsert_examples_mock")
    def test_upsert_examples_example_error(self):
        with pytest.raises(TypeError, match="Unsupported example:"):
            example_store = example_stores.ExampleStore(TEST_RESOURCE_NAME)
            # Manually set _gca_resource here to prevent the mocks from propagating.
            example_store._gca_resource = TEST_EXAMPLE_STORE_OBJ
            example_store.upsert_examples([{"invalid": "dictionary"}])


class TestCoerceToDict:
    def test_coerce_to_dict_content(self):
        assert _coerce_to_dict(TEST_GENERATIVE_CONTENT_DICT) == TEST_CONTENT_DICT

    def test_coerce_to_dict_expected_content_dict(self):
        assert (
            _coerce_to_dict(TEST_GENERATIVE_EXPECTED_CONTENT_DICT)
            == TEST_EXPECTED_CONTENT_DICT
        )

    def test_coerce_to_dict_contents_example_dict(self):
        assert (
            _coerce_to_dict(TEST_GENERATIVE_CONTENTS_EXAMPLE_DICT)
            == TEST_CONTENTS_EXAMPLE_DICT
        )

    def test_coerce_to_dict_stored_contents_example_dict(self):
        assert (
            _coerce_to_dict(TEST_GENERATIVE_STORED_CONTENTS_EXAMPLE_DICT)
            == TEST_STORED_CONTENTS_EXAMPLE_DICT
        )

    def test_coerce_to_dict_example_dict(self):
        assert _coerce_to_dict(TEST_GENERATIVE_EXAMPLE_DICT) == TEST_EXAMPLE_DICT

    def test_coerce_to_dict_example_type_error(self):
        with pytest.raises(TypeError, match="Unsupported example type:"):
            _coerce_to_dict("invalid example type")
