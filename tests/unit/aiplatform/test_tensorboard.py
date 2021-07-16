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
from unittest.mock import patch
from importlib import reload

from google.api_core import operation
from google.auth.exceptions import GoogleAuthError
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import tensorboard

from google.cloud.aiplatform_v1beta1.services.tensorboard_service import (
    client as tensorboard_service_client,
)

from google.cloud.aiplatform_v1beta1.types import (
    tensorboard as gca_tensorboard,
    tensorboard_service as gca_tensorboard_service,
    encryption_spec as gca_encryption_spec,
)

from google.protobuf import field_mask_pb2

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_ALT_PROJECT = "test-project_alt"

_TEST_ALT_LOCATION = "europe-west4"
_TEST_INVALID_LOCATION = "us-central2"

# tensorboard
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "my_tensorboard_1234"
_TEST_DISPLAY_NAME_UPDATE = "my_tensorboard_1234_update"

_TEST_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/tensorboards/{_TEST_ID}"
)
_TEST_ALT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_ALT_LOCATION}/tensorboards/{_TEST_ID}"
)
_TEST_INVALID_NAME = f"prj/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/{_TEST_ID}"

# request_metadata
_TEST_REQUEST_METADATA = ()

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)


@pytest.fixture
def get_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "get_tensorboard"
    ) as get_tensorboard_mock:
        get_tensorboard_mock.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_tensorboard_mock


@pytest.fixture
def create_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "create_tensorboard"
    ) as create_tensorboard_mock:
        create_tensorboard_lro_mock = mock.Mock(operation.Operation)
        create_tensorboard_lro_mock.result.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_tensorboard_mock.return_value = create_tensorboard_lro_mock
        yield create_tensorboard_mock


@pytest.fixture
def update_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "update_tensorboard"
    ) as update_tensorboard_mock:
        update_tensorboard_lro_mock = mock.Mock(operation.Operation)
        update_tensorboard_lro_mock.result.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_NAME,
            display_name=_TEST_DISPLAY_NAME_UPDATE,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        update_tensorboard_mock.return_value = update_tensorboard_lro_mock
        yield update_tensorboard_mock


@pytest.fixture
def delete_tensorboard_mock():
    with mock.patch.object(
        tensorboard_service_client.TensorboardServiceClient, "delete_tensorboard"
    ) as delete_tensorboard_mock:
        delete_tensorboard_lro_mock = mock.Mock(operation.Operation)
        delete_tensorboard_lro_mock.result.return_value = gca_tensorboard_service.DeleteTensorboardRequest(
            name=_TEST_NAME,
        )
        delete_tensorboard_mock.return_value = delete_tensorboard_lro_mock
        yield delete_tensorboard_mock


class TestTensorboard:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_tensorboard(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        get_tensorboard_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_tensorboard_with_id_only_with_project_and_location(
        self, get_tensorboard_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_ID, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_tensorboard_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_tensorboard_with_project_and_location(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_NAME, project=_TEST_PROJECT, location=_TEST_LOCATION
        )
        get_tensorboard_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_tensorboard_with_alt_project_and_location(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)
        tensorboard.Tensorboard(
            tensorboard_name=_TEST_NAME,
            project=_TEST_ALT_PROJECT,
            location=_TEST_LOCATION,
        )
        get_tensorboard_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_tensorboard_with_alt_location(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_ALT_LOCATION)
        tensorboard.Tensorboard(tensorboard_name=_TEST_NAME,)
        get_tensorboard_mock.assert_called_once_with(name=_TEST_NAME)

    def test_init_tensorboard_with_project_and_alt_location(self):
        aiplatform.init(project=_TEST_PROJECT)
        with pytest.raises(RuntimeError):
            tensorboard.Tensorboard(
                tensorboard_name=_TEST_NAME,
                project=_TEST_PROJECT,
                location=_TEST_ALT_LOCATION,
            )

    @patch.dict(
        os.environ, {"GOOGLE_CLOUD_PROJECT": "", "GOOGLE_APPLICATION_CREDENTIALS": ""}
    )
    def test_init_tensorboard_with_id_only_without_project_or_location(self):
        with pytest.raises(GoogleAuthError):
            tensorboard.Tensorboard(
                tensorboard_name=_TEST_ID,
                credentials=auth_credentials.AnonymousCredentials(),
            )

    def test_init_tensorboard_with_location_override(self, get_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        tensorboard.Tensorboard(tensorboard_name=_TEST_ID, location=_TEST_ALT_LOCATION)
        get_tensorboard_mock.assert_called_once_with(name=_TEST_ALT_NAME)

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_init_tensorboard_with_invalid_name(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            tensorboard.Tensorboard(tensorboard_name=_TEST_INVALID_NAME)

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard_with_default_encryption_key(
        self, create_tensorboard_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT, encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        tensorboard.Tensorboard.create(display_name=_TEST_DISPLAY_NAME,)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_create_tensorboard(self, create_tensorboard_mock):

        aiplatform.init(project=_TEST_PROJECT,)

        tensorboard.Tensorboard.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )

        expected_tensorboard = gca_tensorboard.Tensorboard(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_tensorboard_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_delete_tensorboard(self, delete_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)

        my_tensorboard.delete()

        delete_tensorboard_mock.assert_called_once_with(
            name=my_tensorboard.resource_name
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_update_tensorboard_display_name(self, update_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        my_tensorboard.update(display_name=_TEST_DISPLAY_NAME_UPDATE)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            name=_TEST_NAME, display_name=_TEST_DISPLAY_NAME_UPDATE,
        )
        update_tensorboard_mock.assert_called_once_with(
            update_mask=field_mask_pb2.FieldMask(paths=["display_name"]),
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )

    @pytest.mark.usefixtures("get_tensorboard_mock")
    def test_update_tensorboard_encryption_spec(self, update_tensorboard_mock):
        aiplatform.init(project=_TEST_PROJECT)

        my_tensorboard = tensorboard.Tensorboard(tensorboard_name=_TEST_NAME)
        my_tensorboard.update(encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME)

        expected_tensorboard = gca_tensorboard.Tensorboard(
            name=_TEST_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        update_tensorboard_mock.assert_called_once_with(
            update_mask=field_mask_pb2.FieldMask(paths=["encryption_spec"]),
            tensorboard=expected_tensorboard,
            metadata=_TEST_REQUEST_METADATA,
        )
