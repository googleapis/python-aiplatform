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

from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform_v1beta1.services import prediction_service
from tests.system.aiplatform import e2e_base


class TestInitializer(e2e_base.TestEndToEnd):
    """Tests the _set_google_auth_default() functionality in initializer._Config."""

    _temp_prefix = "test_initializer_"

    def test_init_calls_set_google_auth_default(self):
        aiplatform.init(project=e2e_base._PROJECT)

        # init() with only creds shouldn't overwrite the project
        creds = auth_credentials.AnonymousCredentials()
        aiplatform.init(credentials=creds)

        assert aiplatform.initializer.global_config.project == e2e_base._PROJECT
        assert aiplatform.initializer.global_config.credentials == creds

        # init() with only project shouldn't overwrite creds
        aiplatform.init(project=e2e_base._PROJECT)
        assert aiplatform.initializer.global_config.credentials == creds

    def test_init_rest_async_incorrect_credentials(self):
        # Sync credentials should not be used for async REST transport.
        creds = auth_credentials.AnonymousCredentials()
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            api_transport="rest",
            credentials=creds
        )

        with pytest.raises(ValueError):
            aiplatform_initializer.global_config.create_client(
                client_class=prediction_service.PredictionServiceAsyncClient,
                prediction_client=True,
            )
