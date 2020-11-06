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

from unittest import mock
from importlib import reload

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
from google.cloud.aiplatform_v1beta1.services.prediction_service import client as prediction_service_client
from google.cloud.aiplatform_v1beta1.types import endpoint as gca_endpoint
from google.cloud.aiplatform_v1beta1.types import model as gca_model
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.cloud.aiplatform_v1beta1.types import prediction_service
from google.cloud.aiplatform_v1beta1.types import endpoint_service

_TEST_PROJECT = "test-project"
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"

_TEST_ENDPOINT_NAME = "test-endpoint"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_ID = "1028944691210842416"
_TEST_DESCRIPTION = "test-description"

_TEST_ENDPOINT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}"
)
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ID}"
)
_TEST_MODEL_ID = "1028944691210842416"
_TEST_PREDICTION = [['1', '2', '3'], ['3', '3', '1']]


class TestEndpoints:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    @pytest.fixture
    def get_endpoint_mock(self):
        with mock.patch.object(
            EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME, name=_TEST_ENDPOINT_NAME,

            )
            yield get_endpoint_mock

    @pytest.fixture
    def get_model_mock(self):
        with mock.patch.object(ModelServiceClient, "get_model") as get_model_mock:
            get_model_mock.return_value = gca_model.Model(
                display_name=_TEST_DISPLAY_NAME, name=_TEST_MODEL_NAME,
            )
            yield get_model_mock

    @pytest.fixture
    def create_endpoint_mock(self):
        with mock.patch.object(
            EndpointServiceClient, "create_endpoint"
        ) as create_endpoint_mock:
            create_endpoint_lro_mock = mock.Mock(ga_operation.Operation)
            create_endpoint_lro_mock.result.return_value = gca_endpoint.Endpoint(
                name=_TEST_ENDPOINT_NAME, display_name=_TEST_DISPLAY_NAME
            )
            create_endpoint_mock.return_value = create_endpoint_lro_mock
            yield create_endpoint_mock

    @pytest.fixture
    def deploy_model_mock(self):
        with mock.patch.object(
            EndpointServiceClient, "deploy_model"
        ) as deploy_model_mock:
            deployed_model = gca_endpoint.DeployedModel(
                model=_TEST_MODEL_NAME, display_name=_TEST_DISPLAY_NAME,
            )
            deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
            deploy_model_lro_mock.result.return_value = endpoint_service.DeployModelResponse(
                deployed_model=deployed_model,

            )
            deploy_model_mock.return_value = deploy_model_lro_mock
            yield deploy_model_mock

    @pytest.fixture
    def undeploy_model_mock(self):
        with mock.patch.object(
            EndpointServiceClient, "undeploy_model"
        ) as undeploy_model_mock:
            undeploy_model_lro_mock = mock.Mock(ga_operation.Operation)
            undeploy_model_lro_mock.result.return_value = (
                endpoint_service.UndeployModelResponse()
            )
            undeploy_model_mock.return_value = undeploy_model_lro_mock
            yield undeploy_model_mock

    @pytest.fixture
    def create_client_mock(self):
        with mock.patch.object(
            initializer.global_config, "create_client"
        ) as create_client_mock:
            create_client_mock.return_value = mock.Mock(spec=EndpointServiceClient)
            yield create_client_mock

    @pytest.fixture
    def predict_client_predict_mock(self):
        with mock.patch.object(prediction_service_client.PredictionClient, 'predict'
            ) as predict_mock:
            predict_mock.return_value = prediction_service.PredictResponse(
                    predictions=_TEST_PREDICTION,
                    deployed_model_id=_TEST_MODEL_ID
                )
            yield predict_mock


    def test_constructor(self, create_client_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint(_TEST_ENDPOINT_NAME)
        create_client_mock.assert_called_once_with(
            client_class=EndpointServiceClient,
            credentials=None,
            location_override=_TEST_LOCATION,
            prediction_client=False,
        )

    def test_constructor_with_endpoint_id(self, get_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint(_TEST_ID)
        get_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    def test_constructor_with_endpoint_name(self, get_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint(_TEST_ENDPOINT_NAME)
        get_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    def test_constructor_with_custom_project(self, get_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint(endpoint_name=_TEST_ID, project=_TEST_PROJECT_2)
        test_endpoint_resource_name = EndpointServiceClient.endpoint_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )
        get_endpoint_mock.assert_called_once_with(name=test_endpoint_resource_name)

    def test_constructor_with_custom_location(self, get_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint(endpoint_name=_TEST_ID, location=_TEST_LOCATION_2)
        test_endpoint_resource_name = EndpointServiceClient.endpoint_path(
            _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
        )
        get_endpoint_mock.assert_called_once_with(name=test_endpoint_resource_name)

    def test_constructor_with_custom_credentials(self, create_client_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        creds = auth_credentials.AnonymousCredentials()

        models.Endpoint(_TEST_ENDPOINT_NAME)
        create_client_mock.assert_called_once_with(
            client_class=EndpointServiceClient,
            credentials=creds,
            location_override=_TEST_LOCATION,
            prediction_client=False,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_create(self, create_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint.create(display_name=_TEST_DISPLAY_NAME)
        expected_endpoint = gca_endpoint.Endpoint(display_name=_TEST_DISPLAY_NAME)
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT, endpoint=expected_endpoint, metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_create_with_description(self, create_endpoint_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME, description=_TEST_DESCRIPTION,
        )
        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, description=_TEST_DESCRIPTION,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT, endpoint=expected_endpoint, metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(test_model)
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

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_with_display_name(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(
            model=test_model, deployed_model_display_name=_TEST_DISPLAY_NAME
        )
        automatic_resources = machine_resources.AutomaticResources(
            min_replica_count=1, max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=_TEST_DISPLAY_NAME,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_raise_error_traffic_80(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=80)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_raise_error_traffic_120(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=120)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_raise_error_traffic_negative(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=-18)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_raise_error_min_replica(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, min_replica_count=-1)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_raise_error_max_replica(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, max_replica_count=-2)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_raise_error_traffic_split(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_split={"a": 99})

    @pytest.mark.usefixtures("get_model_mock")
    def test_deploy_with_traffic_percent(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"alpaca": 100},
            )

            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=70)
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
                traffic_split={"alpaca": 30, "0": 70},
                metadata=(),
            )

    @pytest.mark.usefixtures("get_model_mock")
    def test_deploy_with_traffic_split(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"alpaca": 100},
            )

            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(
                model=test_model, traffic_split={"alpaca": 30, "0": 70}
            )
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
                traffic_split={"alpaca": 30, "0": 70},
                metadata=(),
            )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_with_machine_type(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(model=test_model, machine_type="n1-standard-32")
        machine_spec = machine_resources.MachineSpec(machine_type="n1-standard-32")
        dedicated_resources = machine_resources.DedicatedResources(
            machine_spec=machine_spec, min_replica_count=1, max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_with_min_replica_count(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(model=test_model, min_replica_count=2)
        automatic_resources = machine_resources.AutomaticResources(
            min_replica_count=2, max_replica_count=2,
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

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    def test_deploy_with_max_replica_count(self, deploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(model=test_model, max_replica_count=2)
        automatic_resources = machine_resources.AutomaticResources(
            min_replica_count=1, max_replica_count=2,
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

    @pytest.mark.parametrize(
        "old_split, percent",
        [
            ({"alpaca": 100}, 70),
            ({"alpaca": 50, "llama": 50}, 70),
            ({"alpaca": 40, "llama": 60}, 75),
            ({"alpaca": 40, "llama": 60}, 88),
            ({"baby": 88, "shark": 12}, 36),
            ({"baby": 11, "shark": 89}, 18),
            ({"baby": 1, "shark": 99}, 80),
            ({"a": 1, "b": 2, "c": 97}, 68),
            ({"a": 99, "b": 1, "c": 0}, 22),
            ({"a": 0, "b": 0, "c": 100}, 18),
            ({"a": 7, "b": 87, "c": 6}, 46),
        ],
    )
    def test_allocate_traffic(self, old_split, percent):
        new_split = models.Endpoint._allocate_traffic(old_split, percent)
        new_split_sum = 0
        for model in new_split:
            new_split_sum += new_split[model]

        assert new_split_sum == 100
        assert new_split["0"] == percent

    @pytest.mark.parametrize(
        "old_split, deployed_model",
        [
            ({"alpaca": 100}, "alpaca"),
            ({"alpaca": 50, "llama": 50}, "alpaca"),
            ({"alpaca": 40, "llama": 60}, "llama"),
            ({"alpaca": 40, "llama": 60}, "alpaca"),
            ({"baby": 88, "shark": 12}, "baby"),
            ({"baby": 11, "shark": 89}, "baby"),
            ({"baby": 1, "shark": 99}, "shark"),
            ({"a": 1, "b": 2, "c": 97}, "a"),
            ({"a": 99, "b": 1, "c": 0}, "b"),
            ({"a": 0, "b": 0, "c": 100}, "c"),
            ({"a": 7, "b": 87, "c": 6}, "b"),
        ],
    )
    def test_unallocate_traffic(self, old_split, deployed_model):
        new_split = models.Endpoint._unallocate_traffic(old_split, deployed_model)
        new_split_sum = 0
        for model in new_split:
            new_split_sum += new_split[model]

        assert new_split_sum == 100
        assert new_split[deployed_model] == 0

    def test_undeploy(self, undeploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"alpaca": 100},
            )
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy("alpaca")
            undeploy_model_mock.assert_called_once_with(
                endpoint=test_endpoint.resource_name,
                deployed_model_id="alpaca",
                traffic_split={"alpaca": 0},
                metadata=(),
            )

    def test_undeploy_with_traffic_split(self, undeploy_model_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with mock.patch.object(
            EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"alpaca": 40, "llama": 60},
            )
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="alpaca", traffic_split={"alpaca": 0, "llama": 100},
            )
            undeploy_model_mock.assert_called_once_with(
                endpoint=test_endpoint.resource_name,
                deployed_model_id="alpaca",
                traffic_split={"alpaca": 0, "llama": 100},
                metadata=(),
            )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_undeploy_raise_error_traffic_split_total(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="alpaca", traffic_split={"llama": 99},
            )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_undeploy_raise_error_undeployed_model_traffic(self):
        with pytest.raises(ValueError):
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="alpaca", traffic_split={"alpaca": 50, "llama": 50},
            )

    def test_predict(self, get_endpoint_mock, endpoint_predict_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.predict(
                instances=[[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]],
                parameters={'param': 3.0}
            )

        true_prediction = models.Prediction(
                predictions=_TEST_PREDICTION,
                deployed_model_id=_TEST_MODEL_ID
            )

        assert true_prediction == test_prediction
