# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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
import importlib

import google.auth
from google.auth import credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import constants
from google.cloud.aiplatform_v1beta1.services.model_service.client import (
    ModelServiceClient,
)

_TEST_PROJECT = "test-project"
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"
_TEST_INVALID_LOCATION = "test-invalid-location"
_TEST_EXPERIMENT = "test-experiment"
_TEST_STAGING_BUCKET = "test-bucket"


class TestInit:
    def setup_method(self):
        importlib.reload(initializer)

    def test_init_project_sets_project(self):
        initializer.global_config.init(project=_TEST_PROJECT)
        assert initializer.global_config.project == _TEST_PROJECT

    def test_not_init_project_gets_default_project(self, monkeypatch):
        def mock_auth_default():
            return None, _TEST_PROJECT

        monkeypatch.setattr(google.auth, "default", mock_auth_default)
        assert initializer.global_config.project == _TEST_PROJECT

    def test_init_location_sets_location(self):
        initializer.global_config.init(location=_TEST_LOCATION)
        assert initializer.global_config.location == _TEST_LOCATION

    def test_not_init_location_gets_default_location(self):
        assert initializer.global_config.location == constants.DEFAULT_REGION

    def test_init_location_with_invalid_location_raises(self):
        with pytest.raises(ValueError):
            initializer.global_config.init(location=_TEST_INVALID_LOCATION)

    def test_init_experiment_sets_experiment(self):
        initializer.global_config.init(experiment=_TEST_EXPERIMENT)
        assert initializer.global_config.experiment == _TEST_EXPERIMENT

    def test_init_staging_bucket_sets_staging_bucket(self):
        initializer.global_config.init(staging_bucket=_TEST_STAGING_BUCKET)
        assert initializer.global_config.staging_bucket == _TEST_STAGING_BUCKET

    def test_init_credentials_sets_credentials(self):
        creds = credentials.AnonymousCredentials()
        initializer.global_config.init(credentials=creds)
        assert initializer.global_config.credentials is creds

    def test_common_location_path_returns_parent(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        true_resource_parent = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
        assert true_resource_parent == initializer.global_config.common_location_path()

    def test_common_location_path_overrides(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        true_resource_parent = (
            f"projects/{_TEST_PROJECT_2}/locations/{_TEST_LOCATION_2}"
        )
        assert true_resource_parent == initializer.global_config.common_location_path(
            project=_TEST_PROJECT_2, location=_TEST_LOCATION_2
        )

    def test_create_client_returns_client(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        client = initializer.global_config.create_client(ModelServiceClient)
        assert isinstance(client, ModelServiceClient)
        assert (
            client._transport._host == f"{_TEST_LOCATION}-{constants.API_BASE_PATH}:443"
        )

    def test_create_client_overrides(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        creds = credentials.AnonymousCredentials()
        client = initializer.global_config.create_client(
            ModelServiceClient,
            credentials=creds,
            location_override=_TEST_LOCATION_2,
            prediction_client=True,
        )
        assert isinstance(client, ModelServiceClient)
        assert (
            client._transport._host
            == f"{_TEST_LOCATION_2}-prediction-{constants.API_BASE_PATH}:443"
        )
        assert client._transport._credentials == creds

    def test_create_client_user_agent(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        client = initializer.global_config.create_client(ModelServiceClient)

        for wrapped_method in client._transport._wrapped_methods.values():
            # wrapped_method._metadata looks like:
            # [('x-goog-api-client', 'model-builder/0.3.1 gl-python/3.7.6 grpc/1.30.0 gax/1.22.2 gapic/0.3.1')]
            user_agent = wrapped_method._metadata[0][1]
            assert user_agent.startswith("model-builder/")

    @pytest.mark.parametrize(
        "init_location, location_override, prediction, expected_endpoint",
        [
            ("us-central1", None, False, "us-central1-aiplatform.googleapis.com"),
            (
                "us-central1",
                "europe-west4",
                False,
                "europe-west4-aiplatform.googleapis.com",
            ),
            ("asia-east1", None, False, "asia-east1-aiplatform.googleapis.com"),
            (
                "asia-east1",
                None,
                True,
                "asia-east1-prediction-aiplatform.googleapis.com",
            ),
        ],
    )
    def test_get_client_options(
        self,
        init_location: str,
        location_override: str,
        prediction: bool,
        expected_endpoint: str,
    ):
        initializer.global_config.init(location=init_location)

        assert (
            initializer.global_config.get_client_options(
                location_override=location_override, prediction_client=prediction
            ).api_endpoint
            == expected_endpoint
        )
