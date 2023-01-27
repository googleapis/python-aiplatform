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

from google import auth
from google.auth import credentials as auth_credentials
from unittest import mock

from google.cloud.aiplatform.utils import source_utils
import constants as test_constants


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            "test-project",
        )
        yield google_auth_mock


@pytest.fixture
def mock_python_package_to_gcs():
    with mock.patch.object(
        source_utils._TrainingScriptPythonPackager, "package_and_copy_to_gcs"
    ) as mock_package_to_copy_gcs:
        mock_package_to_copy_gcs.return_value = (
            test_constants.TrainingJobConstants._TEST_OUTPUT_PYTHON_PACKAGE_PATH
        )
        yield mock_package_to_copy_gcs
