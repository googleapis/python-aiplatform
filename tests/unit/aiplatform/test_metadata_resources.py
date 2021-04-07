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

import pytest

from unittest import mock
from importlib import reload
from unittest.mock import patch

from google.api_core import operation
from google.auth.exceptions import GoogleAuthError
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import metadata
from google.cloud.aiplatform import initializer

from google.cloud.aiplatform_v1beta1 import MetadataServiceClient
from google.cloud.aiplatform_v1beta1 import Context as GapicContext
from google.cloud.aiplatform_v1beta1.types import metadata_service
from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METADATA_STORE = "test-metadata-store"
_TEST_ALT_LOCATION = "europe-west4"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/{_TEST_METADATA_STORE}"

# resource attributes
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_SCHEMA_TITLE = "test.Example"
_TEST_SCHEMA_VERSION = "0.0.1"
_TEST_DESCRIPTION = "test description"
_TEST_METADATA = {"test-param1": 1, "test-param2": "test-value", "test-param3": True}

# context
_TEST_CONTEXT_ID = "test-context-id"
_TEST_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_CONTEXT_ID}"


@pytest.fixture
def get_context_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_context_mock:
        get_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield get_context_mock


@pytest.fixture
def create_context_mock():
    with patch.object(
        MetadataServiceClient, "create_context"
    ) as create_context_mock:
        create_context_mock = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )
        yield create_context_mock


class TestContext:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_context(self, get_context_mock):
        aiplatform.init(project=_TEST_PROJECT)
        metadata.Context(context_name=_TEST_CONTEXT_NAME)
        get_context_mock.assert_called_once_with(name=_TEST_CONTEXT_NAME)

    def test_init_context_with_id(self, get_metadata_store_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        metadata.Context(context_name=_TEST_CONTEXT_ID, metadata_store_id=_TEST_METADATA_STORE)
        get_metadata_store_mock.assert_called_once_with(name=_TEST_CONTEXT_NAME)

    @pytest.mark.usefixtures("get_context_mock")
    def test_create_context(self, create_context_mock):
        aiplatform.init(project=_TEST_PROJECT)

        metadata.Context.create(
            context_id=_TEST_CONTEXT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            metadata_store_id=_TEST_METADATA_STORE,
        )

        expected_context = GapicContext(
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
        )

        create_context_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            context_id=_TEST_CONTEXT_ID,
            context=expected_context,
        )
