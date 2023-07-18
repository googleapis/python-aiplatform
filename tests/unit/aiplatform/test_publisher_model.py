# -*- coding: utf-8 -*-

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

import pytest

from unittest import mock
from importlib import reload

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import _publisher_models

from google.cloud.aiplatform.compat.services import (
    model_garden_service_client_v1,
)


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEST_RESOURCE_NAME = "publishers/google/models/chat-bison@001"
_TEST_MODEL_GARDEN_ID = "google/chat-bison@001"
_TEST_INVALID_RESOURCE_NAME = "google.chat-bison@001"


@pytest.fixture
def mock_get_publisher_model():
    with mock.patch.object(
        model_garden_service_client_v1.ModelGardenServiceClient,
        "get_publisher_model",
    ) as mock_get_publisher_model:
        yield mock_get_publisher_model


@pytest.mark.usefixtures("google_auth_mock")
class TestPublisherModel:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_publisher_model_with_resource_name(self, mock_get_publisher_model):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        _ = _publisher_models._PublisherModel(_TEST_RESOURCE_NAME)
        mock_get_publisher_model.assert_called_once_with(
            name=_TEST_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_publisher_model_with_model_garden_id(self, mock_get_publisher_model):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        _ = _publisher_models._PublisherModel(_TEST_MODEL_GARDEN_ID)
        mock_get_publisher_model.assert_called_once_with(
            name=_TEST_RESOURCE_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_publisher_model_with_invalid_resource_name(
        self, mock_get_publisher_model
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        with pytest.raises(
            ValueError,
            match=(
                f"`{_TEST_INVALID_RESOURCE_NAME}` is not a valid PublisherModel "
                "resource name or model garden id."
            ),
        ):
            _ = _publisher_models._PublisherModel(_TEST_INVALID_RESOURCE_NAME)
