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

import importlib
import pytest
from unittest import mock

from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform_v1beta1.services.model_service.client import (
    ModelServiceClient,
)
from google.cloud.aiplatform_v1beta1.services.endpoint_service.client import (
    EndpointServiceClient,
)
from google.cloud.aiplatform_v1beta1.types import env_var
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import model_service
from google.cloud.aiplatform_v1beta1.types import endpoint_service

_TEST_PROJECT = "test-project"
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"
_TEST_MODEL_NAME = "test-model"
_TEST_ARTIFACT_URI = "gs://test/artifact/uri"
_TEST_SERVING_CONTAINER_IMAGE = "gcr.io/test-serving/container:image"
_TEST_SERVING_CONTAINER_PREDICTION_ROUTE = "predict"
_TEST_SERVING_CONTAINER_HEALTH_ROUTE = "metadata"
_TEST_DESCRIPTION = "test description"
_TEST_SERVING_CONTAINER_COMMAND = ["python3", "run_my_model.py"]
_TEST_SERVING_CONTAINER_ARGS = ["--test", "arg"]
_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES = {
    "learning_rate": 0.01,
    "loss_fn": "mse",
}
_TEST_SERVING_CONTAINER_PORTS = [8888, 10000]
_TEST_ID = "1028944691210842416"


class TestModel:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)

    @pytest.fixture
    def get_endpoint_mock(self):
        with mock.patch.object(
            EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            test_endpoint_resource_name = EndpointServiceClient.endpoint_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_MODEL_NAME, name=test_endpoint_resource_name,
            )
            yield get_endpoint_mock

    @pytest.fixture
    def get_model_mock(self):
        with mock.patch.object(ModelServiceClient, "get_model") as get_model_mock:
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
            get_model_mock.return_value = gca_model.Model(
                display_name=_TEST_MODEL_NAME, name=test_model_resource_name,
            )
            yield get_model_mock

    @pytest.fixture
    def deploy_model_mock(self):
        with mock.patch.object(
            EndpointServiceClient, "deploy_model"
        ) as deploy_model_mock:
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
            deployed_model = gca_endpoint.DeployedModel(
                model=test_model_resource_name, display_name=_TEST_MODEL_NAME,
            )
            deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
            deploy_model_lro_mock.result.return_value = endpoint_service.DeployModelResponse(
                deployed_model=deployed_model,
            )
            deploy_model_mock.return_value = deploy_model_lro_mock
            yield deploy_model_mock

    def test_constructor_creates_client(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            create_client_mock.return_value = api_client_mock

            models.Model(_TEST_ID)
            create_client_mock.assert_called_once_with(
                client_class=ModelServiceClient,
                credentials=None,
                location_override=_TEST_LOCATION,
                prediction_client=False,
            )

    def test_constructor_create_client_with_custom_location(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            create_client_mock.return_value = api_client_mock

            models.Model(_TEST_ID, location=_TEST_LOCATION_2)
            create_client_mock.assert_called_once_with(
                client_class=ModelServiceClient,
                credentials=None,
                location_override=_TEST_LOCATION_2,
                prediction_client=False,
            )

    def test_constructor_creates_client_with_custom_credentials(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            create_client_mock.return_value = api_client_mock
            creds = auth_credentials.AnonymousCredentials()
            models.Model(_TEST_ID, credentials=creds)
            create_client_mock.assert_called_once_with(
                client_class=ModelServiceClient,
                credentials=creds,
                location_override=_TEST_LOCATION,
                prediction_client=False,
            )

    def test_constructor_gets_model(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            create_client_mock.return_value = api_client_mock

            models.Model(_TEST_ID)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    def test_constructor_gets_model_with_custom_project(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            create_client_mock.return_value = api_client_mock

            models.Model(_TEST_ID, project=_TEST_PROJECT_2)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
            )
            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    def test_constructor_gets_model_with_custom_location(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            create_client_mock.return_value = api_client_mock

            models.Model(_TEST_ID, location=_TEST_LOCATION_2)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
            )
            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    def test_upload_uploads_and_gets_model(self):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            mock_lro = mock.Mock(ga_operation.Operation)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
            mock_lro.result.return_value = model_service.UploadModelResponse(
                model=test_model_resource_name
            )
            api_client_mock.upload_model.return_value = mock_lro
            create_client_mock.return_value = api_client_mock

            models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            )

            container_spec = gca_model.ModelContainerSpec(
                image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            )

            managed_model = gca_model.Model(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                container_spec=container_spec,
            )

            api_client_mock.upload_model.assert_called_once_with(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            )

            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    def test_upload_uploads_and_gets_model_with_all_args(self):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            mock_lro = mock.Mock(ga_operation.Operation)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            )
            mock_lro.result.return_value = model_service.UploadModelResponse(
                model=test_model_resource_name
            )
            api_client_mock.upload_model.return_value = mock_lro
            create_client_mock.return_value = api_client_mock

            models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                description=_TEST_DESCRIPTION,
                serving_container_command=_TEST_SERVING_CONTAINER_COMMAND,
                serving_container_args=_TEST_SERVING_CONTAINER_ARGS,
                serving_container_environment_variables=_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
                serving_container_ports=_TEST_SERVING_CONTAINER_PORTS,
            )

            env = [
                env_var.EnvVar(name=str(key), value=str(value))
                for key, value in _TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES.items()
            ]

            ports = [
                gca_model.Port(container_port=port)
                for port in _TEST_SERVING_CONTAINER_PORTS
            ]

            container_spec = gca_model.ModelContainerSpec(
                image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                command=_TEST_SERVING_CONTAINER_COMMAND,
                args=_TEST_SERVING_CONTAINER_ARGS,
                env=env,
                ports=ports,
            )

            managed_model = gca_model.Model(
                display_name=_TEST_MODEL_NAME,
                description=_TEST_DESCRIPTION,
                artifact_uri=_TEST_ARTIFACT_URI,
                container_spec=container_spec,
            )

            api_client_mock.upload_model.assert_called_once_with(
                parent=initializer.global_config.common_location_path(),
                model=managed_model,
            )

            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    def test_upload_uploads_and_gets_model_with_custom_project(self):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            mock_lro = mock.Mock(ga_operation.Operation)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
            )
            mock_lro.result.return_value = model_service.UploadModelResponse(
                model=test_model_resource_name
            )
            api_client_mock.upload_model.return_value = mock_lro
            create_client_mock.return_value = api_client_mock

            models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                project=_TEST_PROJECT_2,
            )

            container_spec = gca_model.ModelContainerSpec(
                image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            )

            managed_model = gca_model.Model(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                container_spec=container_spec,
            )

            api_client_mock.upload_model.assert_called_once_with(
                parent=f"projects/{_TEST_PROJECT_2}/locations/{_TEST_LOCATION}",
                model=managed_model,
            )

            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    def test_upload_uploads_and_gets_model_with_custom_location(self):

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            api_client_mock = mock.Mock(spec=ModelServiceClient)
            mock_lro = mock.Mock(ga_operation.Operation)
            test_model_resource_name = ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
            )
            mock_lro.result.return_value = model_service.UploadModelResponse(
                model=test_model_resource_name
            )
            api_client_mock.upload_model.return_value = mock_lro
            create_client_mock.return_value = api_client_mock

            models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
                location=_TEST_LOCATION_2,
            )

            container_spec = gca_model.ModelContainerSpec(
                image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
                health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            )

            managed_model = gca_model.Model(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                container_spec=container_spec,
            )

            api_client_mock.upload_model.assert_called_once_with(
                parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION_2}",
                model=managed_model,
            )

            api_client_mock.get_model.assert_called_once_with(
                name=test_model_resource_name
            )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_model = models.Model(_TEST_ID)
        test_endpoint = models.Endpoint(_TEST_ID)

        assert test_model.deploy(test_endpoint) == test_endpoint
        automatic_resources = machine_resources.AutomaticResources(
            min_replica_count=1, max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
        )
