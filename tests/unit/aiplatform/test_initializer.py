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

import importlib
import os
from typing import Optional
from unittest import mock
from unittest.mock import patch

import pytest

import google.auth
from google.auth import credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata.metadata import _experiment_tracker
from google.cloud.aiplatform.constants import base as constants
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import resource_manager_utils
from google.cloud.aiplatform.compat.services import (
    model_service_client,
    prediction_service_client_v1beta1,
)
import constants as test_constants

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_LOCATION_2 = "europe-west4"
_TEST_INVALID_LOCATION = "test-invalid-location"
_TEST_EXPERIMENT = "test-experiment"
_TEST_DESCRIPTION = "test-description"
_TEST_STAGING_BUCKET = "test-bucket"
_TEST_NETWORK = "projects/12345/global/networks/myVPC"
_TEST_SERVICE_ACCOUNT = "test-service-account@test-project.iam.gserviceaccount.com"

# tensorboard
_TEST_TENSORBOARD_ID = "1028944691210842416"
_TEST_TENSORBOARD_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/tensorboards/{_TEST_TENSORBOARD_ID}"


@pytest.mark.usefixtures("google_auth_mock")
class TestInit:
    def setup_method(self):
        importlib.reload(initializer)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_init_project_sets_project(self):
        initializer.global_config.init(project=_TEST_PROJECT)
        assert initializer.global_config.project == _TEST_PROJECT

    def test_not_init_project_gets_default_project(self, monkeypatch):
        def mock_auth_default():
            return None, _TEST_PROJECT

        monkeypatch.setattr(google.auth, "default", mock_auth_default)
        assert initializer.global_config.project == _TEST_PROJECT

    def test_infer_project_id(self):
        cloud_project_number = "123"

        def mock_get_project_id(project_number: str, **_):
            assert project_number == cloud_project_number
            return _TEST_PROJECT

        with mock.patch.object(
            target=resource_manager_utils,
            attribute="get_project_id",
            new=mock_get_project_id,
        ), mock.patch.dict(
            os.environ, {"CLOUD_ML_PROJECT_ID": cloud_project_number}, clear=True
        ):
            assert initializer.global_config.project == _TEST_PROJECT

    def test_infer_project_id_with_precedence(self):
        lower_precedence_cloud_project_number = "456"
        higher_precedence_cloud_project_number = "123"

        def mock_get_project_id(project_number: str, **_):
            assert project_number == higher_precedence_cloud_project_number
            return _TEST_PROJECT

        with mock.patch.object(
            target=resource_manager_utils,
            attribute="get_project_id",
            new=mock_get_project_id,
        ), mock.patch.dict(
            os.environ,
            {
                "GOOGLE_CLOUD_PROJECT": higher_precedence_cloud_project_number,
                "CLOUD_ML_PROJECT_ID": lower_precedence_cloud_project_number,
            },
            clear=True,
        ):
            assert initializer.global_config.project == _TEST_PROJECT

    def test_init_location_sets_location(self):
        initializer.global_config.init(location=_TEST_LOCATION)
        assert initializer.global_config.location == _TEST_LOCATION

    def test_not_init_location_gets_env_location(self):
        os.environ["CLOUD_ML_REGION"] = _TEST_LOCATION_2
        assert initializer.global_config.location == _TEST_LOCATION_2
        del os.environ["CLOUD_ML_REGION"]

    def test_not_init_location_gets_default_location(self):
        assert initializer.global_config.location == constants.DEFAULT_REGION

    def test_init_location_with_invalid_location_raises(self):
        with pytest.raises(ValueError):
            initializer.global_config.init(location=_TEST_INVALID_LOCATION)

    def test_init_network_sets_network(self):
        initializer.global_config.init(network=_TEST_NETWORK)
        assert initializer.global_config.network == _TEST_NETWORK

    def test_init_service_account_sets_service_account(self):
        initializer.global_config.init(service_account=_TEST_SERVICE_ACCOUNT)
        assert initializer.global_config.service_account == _TEST_SERVICE_ACCOUNT

    @patch.object(_experiment_tracker, "set_experiment")
    def test_init_experiment_sets_experiment(self, set_experiment_mock):
        initializer.global_config.init(experiment=_TEST_EXPERIMENT)
        set_experiment_mock.assert_called_once_with(
            experiment=_TEST_EXPERIMENT,
            description=None,
            backing_tensorboard=None,
        )

    @patch.object(_experiment_tracker, "set_experiment")
    def test_init_experiment_sets_experiment_with_description(
        self, set_experiment_mock
    ):
        initializer.global_config.init(
            experiment=_TEST_EXPERIMENT, experiment_description=_TEST_DESCRIPTION
        )
        set_experiment_mock.assert_called_once_with(
            experiment=_TEST_EXPERIMENT,
            description=_TEST_DESCRIPTION,
            backing_tensorboard=None,
        )

    @patch.object(_experiment_tracker, "set_tensorboard")
    def test_init_with_experiment_tensorboard_id_sets_global_tensorboard(
        self, set_tensorboard_mock
    ):
        creds = credentials.AnonymousCredentials()
        initializer.global_config.init(
            experiment_tensorboard=_TEST_TENSORBOARD_ID,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=creds,
        )

        set_tensorboard_mock.assert_called_once_with(
            tensorboard=_TEST_TENSORBOARD_ID,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=creds,
        )

    @patch.object(_experiment_tracker, "set_tensorboard")
    def test_init_with_experiment_tensorboard_resource_sets_global_tensorboard(
        self, set_tensorboard_mock
    ):
        initializer.global_config.init(experiment_tensorboard=_TEST_TENSORBOARD_NAME)

        set_tensorboard_mock.assert_called_once_with(
            tensorboard=_TEST_TENSORBOARD_NAME,
            project=None,
            location=None,
            credentials=None,
        )

    @patch.object(_experiment_tracker, "set_experiment")
    def test_init_experiment_without_tensorboard_uses_global_tensorboard(
        self, set_experiment_mock
    ):
        initializer.global_config.tensorboard = _TEST_TENSORBOARD_NAME

        initializer.global_config.init(
            experiment=_TEST_EXPERIMENT,
        )

        set_experiment_mock.assert_called_once_with(
            experiment=_TEST_EXPERIMENT,
            description=None,
            backing_tensorboard=None,
        )

        assert initializer.global_config.tensorboard == _TEST_TENSORBOARD_NAME

    @patch.object(_experiment_tracker, "set_tensorboard")
    @patch.object(_experiment_tracker, "set_experiment")
    def test_init_experiment_tensorboard_false_does_not_set_tensorboard(
        self, set_experiment_mock, set_tensorboard_mock
    ):
        initializer.global_config.tensorboard = _TEST_TENSORBOARD_NAME

        initializer.global_config.init(
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=False,
        )

        set_tensorboard_mock.assert_not_called()

        set_experiment_mock.assert_called_once_with(
            experiment=_TEST_EXPERIMENT,
            description=None,
            backing_tensorboard=False,
        )

    def test_init_experiment_description_fail_without_experiment(self):
        with pytest.raises(ValueError):
            initializer.global_config.init(experiment_description=_TEST_DESCRIPTION)

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
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride
        )
        assert client._client_class is model_service_client.ModelServiceClient
        assert isinstance(client, utils.ModelClientWithOverride)
        assert (
            client._transport._host == f"{_TEST_LOCATION}-{constants.API_BASE_PATH}:443"
        )

    def test_create_client_with_default_api_transport(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride
        )
        assert client._client_class is model_service_client.ModelServiceClient
        assert isinstance(client, utils.ModelClientWithOverride)
        assert client._api_transport is None

    @pytest.mark.parametrize("api_transport", ["grpc", "rest", None])
    def test_create_client_with_api_transport_override(self, api_transport):
        initializer.global_config.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, api_transport=api_transport
        )
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride
        )
        assert client._client_class is model_service_client.ModelServiceClient
        assert isinstance(client, utils.ModelClientWithOverride)
        assert client._api_transport == (
            api_transport if api_transport == "rest" else None
        )

    @pytest.mark.parametrize("api_transport", ["grpc_asyncio", "unsupported"])
    def test_create_client_with_invalid_api_transport_override(self, api_transport):
        with pytest.raises(ValueError):
            initializer.global_config.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                api_transport=api_transport,
            )

    def test_create_client_overrides(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        creds = credentials.AnonymousCredentials()
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride,
            credentials=creds,
            location_override=_TEST_LOCATION_2,
            prediction_client=True,
        )
        assert isinstance(client, utils.ModelClientWithOverride)
        assert (
            client._transport._host
            == f"{_TEST_LOCATION_2}-{constants.API_BASE_PATH}:443"
        )
        assert client._transport._credentials == creds

    def test_create_client_user_agent(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride
        )

        for wrapped_method in client._transport._wrapped_methods.values():
            # wrapped_method._metadata looks like:
            # [('x-goog-api-client', 'model-builder/0.3.1 gl-python/3.7.6 grpc/1.30.0 gax/1.22.2 gapic/0.3.1')]
            user_agent = wrapped_method._metadata[0][1]
            assert "model-builder/" in user_agent
            assert "google.cloud.aiplatform" in user_agent

    def test_create_client_user_agent_top_level_method(self):
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        class SomeClass:
            # Overriding the module since the top level method code skips test namespaces.
            __module__ = "vertexai"

            def __init__(self):
                self._client = initializer.global_config.create_client(
                    client_class=utils.ModelClientWithOverride
                )

        for wrapped_method in SomeClass()._client._transport._wrapped_methods.values():
            # wrapped_method._metadata looks like:
            # [('x-goog-api-client', 'model-builder/0.3.1 gl-python/3.7.6 grpc/1.30.0 gax/1.22.2 gapic/0.3.1')]
            user_agent = wrapped_method._metadata[0][1]
            assert (
                f"+{initializer._TOP_GOOGLE_CONSTRUCTOR_METHOD_TAG}+vertexai.SomeClass.__init__"
                in user_agent
            )

    def test_create_client_appended_user_agent(self):
        appended_user_agent = ["fake_user_agent", "another_fake_user_agent"]
        initializer.global_config.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride,
            appended_user_agent=appended_user_agent,
        )

        for wrapped_method in client._transport._wrapped_methods.values():
            # wrapped_method._metadata looks like:
            # [('x-goog-api-client', 'model-builder/0.3.1 gl-python/3.7.6 grpc/1.30.0 gax/1.22.2 gapic/0.3.1')]
            user_agent = wrapped_method._metadata[0][1]
            assert " " + appended_user_agent[0] in user_agent
            assert " " + appended_user_agent[1] in user_agent

    def test_set_api_endpoint(self):
        initializer.global_config.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            api_endpoint="test.googleapis.com",
        )

        assert initializer.global_config.api_endpoint == "test.googleapis.com"

    def test_not_set_api_endpoint(self):
        initializer.global_config.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        assert initializer.global_config.api_endpoint is None

    @pytest.mark.parametrize(
        "init_location, location_override, api_endpoint, expected_endpoint",
        [
            ("us-central1", None, None, "us-central1-aiplatform.googleapis.com"),
            (
                "us-central1",
                "europe-west4",
                None,
                "europe-west4-aiplatform.googleapis.com",
            ),
            ("asia-east1", None, None, "asia-east1-aiplatform.googleapis.com"),
            (
                "asia-southeast1",
                "australia-southeast1",
                None,
                "australia-southeast1-aiplatform.googleapis.com",
            ),
            (
                "asia-east1",
                None,
                "us-central1-aiplatform.googleapis.com",
                "us-central1-aiplatform.googleapis.com",
            ),
            (
                "us-central1",
                None,
                "test.aiplatform.googleapis.com",
                "test.aiplatform.googleapis.com",
            ),
        ],
    )
    def test_get_client_options(
        self,
        init_location: str,
        location_override: Optional[str],
        api_endpoint: Optional[str],
        expected_endpoint: str,
    ):
        initializer.global_config.init(
            location=init_location, api_endpoint=api_endpoint
        )

        assert (
            initializer.global_config.get_client_options(
                location_override=location_override
            ).api_endpoint
            == expected_endpoint
        )

    def test_get_client_options_with_api_override(self):
        initializer.global_config.init(location="asia-east1")

        client_options = initializer.global_config.get_client_options(
            api_base_path_override="override.googleapis.com"
        )

        assert client_options.api_endpoint == "asia-east1-override.googleapis.com"

    def test_get_resource_type(self):
        initializer.global_config.init()
        os.environ["VERTEX_PRODUCT"] = "COLAB_ENTERPRISE"
        assert initializer.global_config.get_resource_type().value == (
            "COLAB_ENTERPRISE"
        )

        initializer.global_config.init()
        os.environ["VERTEX_PRODUCT"] = "WORKBENCH_INSTANCE"
        assert initializer.global_config.get_resource_type().value == (
            "WORKBENCH_INSTANCE"
        )

        initializer.global_config.init()
        os.environ["VERTEX_PRODUCT"] = "WORKBENCH_CUSTOM_CONTAINER"
        assert initializer.global_config.get_resource_type().value == (
            "WORKBENCH_CUSTOM_CONTAINER"
        )

    def test_init_with_only_creds_does_not_override_set_project(self):
        assert initializer.global_config.project is not _TEST_PROJECT_2
        initializer.global_config.init(project=_TEST_PROJECT_2)

        creds = credentials.AnonymousCredentials()
        initializer.global_config.init(credentials=creds)

        assert initializer.global_config.project == _TEST_PROJECT_2

    def test_init_with_only_project_does_not_override_set_creds(self):
        creds = credentials.AnonymousCredentials()
        assert initializer.global_config.credentials is not creds
        initializer.global_config.init(credentials=creds)

        initializer.global_config.init(project=_TEST_PROJECT_2)
        assert initializer.global_config.credentials is creds

    def test_create_client_with_request_metadata_model_service(self):
        global_metadata = [
            ("global_param", "value1"),
        ]
        request_metadata = [
            ("request_param", "value2"),
        ]
        initializer.global_config.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            request_metadata=global_metadata,
            api_transport="rest",
        )
        client = initializer.global_config.create_client(
            client_class=utils.ModelClientWithOverride
        )
        model_name = client.model_path(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            model="model_id",
        )
        with patch("requests.sessions.Session.get") as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.content = "{}"
            client.get_model(name=model_name, metadata=request_metadata)
            call_kwargs = mock_get.call_args_list[0][1]
            headers = call_kwargs["headers"]
            for metadata_key in ["global_param", "request_param"]:
                assert metadata_key in headers

    def test_create_client_with_request_metadata_prediction_service(self):
        global_metadata = [
            ("global_param", "value1"),
        ]
        request_metadata = [
            ("request_param", "value2"),
        ]
        initializer.global_config.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            request_metadata=global_metadata,
            api_transport="rest",
        )
        client = initializer.global_config.create_client(
            client_class=prediction_service_client_v1beta1.PredictionServiceClient
        )
        model_name = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/publishers/google/models/gemini-1.0-pro"
        with patch("requests.sessions.Session.post") as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.content = "{}"
            client.generate_content(model=model_name, metadata=request_metadata)
            call_kwargs = mock_post.call_args_list[0][1]
            headers = call_kwargs["headers"]
            for metadata_key in ["global_param", "request_param"]:
                assert metadata_key in headers


class TestThreadPool:
    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize(
        "cpu_count, expected", [(4, 20), (32, 32), (None, 4), (2, 10)]
    )
    def test_max_workers(self, cpu_count, expected):
        with mock.patch.object(os, "cpu_count") as cpu_count_mock:
            cpu_count_mock.return_value = cpu_count
            importlib.reload(initializer)
            assert initializer.global_pool._max_workers == expected
