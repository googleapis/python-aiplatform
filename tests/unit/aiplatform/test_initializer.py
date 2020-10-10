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


from google.api_core import client_options
import google.auth
from google.auth import credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

_TEST_PROJECT='test-project'
_TEST_LOCATION='us-central1'
_TEST_INVALIED_LOCATION='test-invalid-location'
_TEST_EXPERIMENT='test-experiment'
_TEST_STAGING_BUCKET='test-bucket'


class TestInit:

    def setup_method(self):
        importlib.reload(initializer)

    def test_init_project_sets_project(self):
        initializer.global_config.init(project=_TEST_PROJECT)
        assert initializer.global_config.project == _TEST_PROJECT

    def test_not_init_project_gets_default_project(self, monkeypatch):
        def mock_auth_default():
            return None, _TEST_PROJECT

        monkeypatch.setattr(google.auth, 'default', mock_auth_default)
        assert initializer.global_config.project == _TEST_PROJECT

    def test_init_location_sets_location(self):
        initializer.global_config.init(location=_TEST_LOCATION)
        assert initializer.global_config.location == _TEST_LOCATION

    def test_not_init_location_gets_default_location(self):
        assert initializer.global_config.location == utils.DEFAULT_REGION

    def test_init_location_with_invalid_location_raises(self):
        with pytest.raises(ValueError):
            initializer.global_config.init(location=_TEST_INVALIED_LOCATION)

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

    @pytest.mark.parametrize(
        "init_location, location_override, prediction, expected_endpoint",
        [
            (
                "us-central1",
                None,
                False,
                "us-central1-aiplatform.googleapis.com"),
            (
                "us-central1",
                "europe-west4",
                False,
                "europe-west4-aiplatform.googleapis.com",
            ),
            (
                "asia-east1",
                None,
                False,
                "asia-east1-aiplatform.googleapis.com"),
            (
                "asia-east1",
                None,
                True,
                "asia-east1-prediction-aiplatform.googleapis.com"),
        ],
    )
    def test_get_client_options(
        self, init_location: str, location_override: str, prediction: bool,
        expected_endpoint: str
    ):
        initializer.global_config.init(location=init_location)

        assert initializer.global_config.get_client_options(
            location_override=location_override, prediction_client=prediction
        ).api_endpoint == expected_endpoint
