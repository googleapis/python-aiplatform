# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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
from importlib import reload
from unittest import mock
from unittest.mock import patch

import pytest
from google.api_core import operation
from google.auth import credentials as auth_credentials
from google.auth.exceptions import GoogleAuthError

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import metadata_store
from google.cloud.aiplatform_v1beta1 import MetadataServiceClient
from google.cloud.aiplatform_v1beta1 import MetadataStore as GapicMetadataStore
from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1beta1.types import metadata_service

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ALT_LOCATION = "europe-west4"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

# metadata_store
_TEST_ID = "test-id"
_TEST_DEFAULT_ID = "default"

_TEST_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/{_TEST_ID}"
)
_TEST_ALT_LOC_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_ALT_LOCATION}/metadataStores/{_TEST_ID}"
)
_TEST_DEFAULT_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/{_TEST_DEFAULT_ID}"

_TEST_INVALID_NAME = f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_ID}"

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)


@pytest.fixture
def get_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            name=_TEST_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_metadata_store_mock


@pytest.fixture
def get_default_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            name=_TEST_DEFAULT_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_metadata_store_mock


@pytest.fixture
def get_metadata_store_without_name_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_metadata_store_mock


@pytest.fixture
def create_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "create_metadata_store"
    ) as create_metadata_store_mock:
        create_metadata_store_lro_mock = mock.Mock(operation.Operation)
        create_metadata_store_lro_mock.result.return_value = GapicMetadataStore(
            name=_TEST_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_metadata_store_mock.return_value = create_metadata_store_lro_mock
        yield create_metadata_store_mock


@pytest.fixture
def create_default_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "create_metadata_store"
    ) as create_metadata_store_mock:
        create_metadata_store_lro_mock = mock.Mock(operation.Operation)
        create_metadata_store_lro_mock.result.return_value = GapicMetadataStore(
            name=_TEST_DEFAULT_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_metadata_store_mock.return_value = create_metadata_store_lro_mock
        yield create_metadata_store_mock


@pytest.fixture
def delete_metadata_store_mock():
    with mock.patch.object(
        MetadataServiceClient, "delete_metadata_store"
    ) as delete_metadata_store_mock:
        delete_metadata_store_lro_mock = mock.Mock(operation.Operation)
        delete_metadata_store_lro_mock.result.return_value = (
            metadata_service.DeleteMetadataStoreRequest()
        )
        delete_metadata_store_mock.return_value = delete_metadata_store_lro_mock
        yield delete_metadata_store_mock


class TestMetadataStore:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_metadata_store(self, get_metadata_store_mock):
        aiplatform.init(project=_TEST_PROJECT)
        metadata_store._MetadataStore(metadata_store_name=_TEST_NAME)
        get_metadata_store_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_metadata_store_with_id(self, get_metadata_store_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        metadata_store._MetadataStore(metadata_store_name=_TEST_ID)
        get_metadata_store_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_metadata_store_with_default_id(self, get_metadata_store_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        metadata_store._MetadataStore()
        get_metadata_store_mock.assert_called_once_with(name=_TEST_DEFAULT_NAME)

    @pytest.mark.usefixtures("get_metadata_store_without_name_mock")
    @patch.dict(
        os.environ, {"GOOGLE_CLOUD_PROJECT": "", "GOOGLE_APPLICATION_CREDENTIALS": ""}
    )
    def test_init_metadata_store_with_id_without_project_or_location(self):
        with pytest.raises(GoogleAuthError):
            metadata_store._MetadataStore(
                metadata_store_name=_TEST_ID,
                credentials=auth_credentials.AnonymousCredentials(),
            )

    def test_init_metadata_store_with_location_override(self, get_metadata_store_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        metadata_store._MetadataStore(
            metadata_store_name=_TEST_ID, location=_TEST_ALT_LOCATION
        )
        get_metadata_store_mock.assert_called_once_with(name=_TEST_ALT_LOC_NAME)

    @pytest.mark.usefixtures("get_metadata_store_mock")
    def test_init_metadata_store_with_invalid_name(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            metadata_store._MetadataStore(metadata_store_name=_TEST_INVALID_NAME)

    @pytest.mark.usefixtures("get_default_metadata_store_mock")
    def test_init_aiplatform_with_encryption_key_name_and_create_default_metadata_store(
        self, create_default_metadata_store_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        my_metadata_store = metadata_store._MetadataStore._create(
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        expected_metadata_store = GapicMetadataStore(
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_default_metadata_store_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            metadata_store_id=_TEST_DEFAULT_ID,
            metadata_store=expected_metadata_store,
        )

        expected_metadata_store.name = _TEST_DEFAULT_NAME
        assert my_metadata_store._gca_resource == expected_metadata_store

    @pytest.mark.usefixtures("get_metadata_store_mock")
    def test_create_non_default_metadata_store(self, create_metadata_store_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_metadata_store = metadata_store._MetadataStore._create(
            metadata_store_id=_TEST_ID,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        expected_metadata_store = GapicMetadataStore(
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_metadata_store_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            metadata_store_id=_TEST_ID,
            metadata_store=expected_metadata_store,
        )

        expected_metadata_store.name = _TEST_NAME
        assert my_metadata_store._gca_resource == expected_metadata_store
