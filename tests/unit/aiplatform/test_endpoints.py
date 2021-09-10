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
from datetime import datetime, timedelta

from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils

from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform_v1.services.endpoint_service import (
    client as endpoint_service_client,
)
from google.cloud.aiplatform_v1.services.prediction_service import (
    client as prediction_service_client,
)
from google.cloud.aiplatform.compat.types import (
    endpoint as gca_endpoint,
    model as gca_model,
    machine_resources as gca_machine_resources,
    prediction_service as gca_prediction_service,
    endpoint_service as gca_endpoint_service,
    encryption_spec as gca_encryption_spec,
)

_TEST_PROJECT = "test-project"
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"

_TEST_DISPLAY_NAME = "test-display-name"
_TEST_DISPLAY_NAME_2 = "test-display-name-2"
_TEST_ID = "1028944691210842416"
_TEST_ID_2 = "4366591682456584192"
_TEST_DESCRIPTION = "test-description"

_TEST_ENDPOINT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}"
)
_TEST_ENDPOINT_NAME_ALT_LOCATION = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION_2}/endpoints/{_TEST_ID}"
)
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ID}"
)

_TEST_MODEL_ID = "1028944691210842416"
_TEST_PREDICTION = [[1.0, 2.0, 3.0], [3.0, 3.0, 1.0]]
_TEST_INSTANCES = [[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]]
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"

_TEST_DEPLOYED_MODELS = [
    gca_endpoint.DeployedModel(id=_TEST_ID, display_name=_TEST_DISPLAY_NAME),
    gca_endpoint.DeployedModel(id=_TEST_ID_2, display_name=_TEST_DISPLAY_NAME_2),
]

_TEST_MACHINE_TYPE = "n1-standard-32"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2

_TEST_EXPLANATIONS = [gca_prediction_service.explanation.Explanation(attributions=[])]

_TEST_ATTRIBUTIONS = [
    gca_prediction_service.explanation.Attribution(
        baseline_output_value=1.0,
        instance_output_value=2.0,
        feature_attributions=3.0,
        output_index=[1, 2, 3],
        output_display_name="abc",
        approximation_error=6.0,
        output_name="xyz",
    )
]

_TEST_EXPLANATION_METADATA = explain.ExplanationMetadata(
    inputs={
        "features": explain.ExplanationMetadata.InputMetadata(
            {
                "input_tensor_name": "dense_input",
                "encoding": "BAG_OF_FEATURES",
                "modality": "numeric",
                "index_feature_mapping": ["abc", "def", "ghj"],
            }
        )
    },
    outputs={
        "medv": explain.ExplanationMetadata.OutputMetadata(
            {"output_tensor_name": "dense_2"}
        )
    },
)
_TEST_EXPLANATION_PARAMETERS = explain.ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 10}}
)

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

_TEST_ENDPOINT_GAPIC = gca_endpoint.Endpoint(
    display_name=_TEST_DISPLAY_NAME, name=_TEST_ENDPOINT_NAME
)

_TEST_ENDPOINT_LIST = [
    gca_endpoint.Endpoint(
        name=_TEST_ENDPOINT_NAME,
        display_name="aac",
        create_time=datetime.now() - timedelta(minutes=15),
    ),
    gca_endpoint.Endpoint(
        name=_TEST_ENDPOINT_NAME,
        display_name="aab",
        create_time=datetime.now() - timedelta(minutes=5),
    ),
    gca_endpoint.Endpoint(
        name=_TEST_ENDPOINT_NAME,
        display_name="aaa",
        create_time=datetime.now() - timedelta(minutes=10),
    ),
]

_TEST_LIST_FILTER = 'display_name="abc"'
_TEST_LIST_ORDER_BY_CREATE_TIME = "create_time desc"
_TEST_LIST_ORDER_BY_DISPLAY_NAME = "display_name"

_TEST_LABELS = {"my_key": "my_value"}


@pytest.fixture
def get_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_endpoint_alt_location_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME_ALT_LOCATION,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_endpoint_with_models_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            deployed_models=_TEST_DEPLOYED_MODELS,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME, name=_TEST_MODEL_NAME,
        )
        yield get_model_mock


@pytest.fixture
def create_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "create_endpoint"
    ) as create_endpoint_mock:
        create_endpoint_lro_mock = mock.Mock(ga_operation.Operation)
        create_endpoint_lro_mock.result.return_value = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME, display_name=_TEST_DISPLAY_NAME
        )
        create_endpoint_mock.return_value = create_endpoint_lro_mock
        yield create_endpoint_mock


@pytest.fixture
def deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = gca_endpoint.DeployedModel(
            model=_TEST_MODEL_NAME, display_name=_TEST_DISPLAY_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = gca_endpoint_service.DeployModelResponse(
            deployed_model=deployed_model,
        )
        deploy_model_mock.return_value = deploy_model_lro_mock
        yield deploy_model_mock


@pytest.fixture
def deploy_model_with_explanations_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = gca_endpoint.DeployedModel(
            model=_TEST_MODEL_NAME, display_name=_TEST_DISPLAY_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = gca_endpoint_service.DeployModelResponse(
            deployed_model=deployed_model,
        )
        deploy_model_mock.return_value = deploy_model_lro_mock
        yield deploy_model_mock


@pytest.fixture
def undeploy_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "undeploy_model"
    ) as undeploy_model_mock:
        undeploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        undeploy_model_lro_mock.result.return_value = (
            gca_endpoint_service.UndeployModelResponse()
        )
        undeploy_model_mock.return_value = undeploy_model_lro_mock
        yield undeploy_model_mock


@pytest.fixture
def delete_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "delete_endpoint"
    ) as delete_endpoint_mock:
        delete_endpoint_lro_mock = mock.Mock(ga_operation.Operation)
        delete_endpoint_lro_mock.result.return_value = (
            gca_endpoint_service.DeleteEndpointRequest()
        )
        delete_endpoint_mock.return_value = delete_endpoint_lro_mock
        yield delete_endpoint_mock


@pytest.fixture
def sdk_private_undeploy_mock():
    """Mocks the high-level Endpoint._undeploy() SDK private method"""
    with mock.patch.object(aiplatform.Endpoint, "_undeploy") as sdk_undeploy_mock:
        sdk_undeploy_mock.return_value = None
        yield sdk_undeploy_mock


@pytest.fixture
def sdk_undeploy_all_mock():
    """Mocks the high-level Endpoint.undeploy_all() SDK method"""
    with mock.patch.object(
        aiplatform.Endpoint, "undeploy_all"
    ) as sdk_undeploy_all_mock:
        sdk_undeploy_all_mock.return_value = None
        yield sdk_undeploy_all_mock


@pytest.fixture
def list_endpoints_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "list_endpoints"
    ) as list_endpoints_mock:
        list_endpoints_mock.return_value = _TEST_ENDPOINT_LIST
        yield list_endpoints_mock


@pytest.fixture
def create_endpoint_client_mock():
    with mock.patch.object(
        initializer.global_config, "create_client", autospec=True,
    ) as create_endpoint_client_mock:
        endpoint_client_mock = mock.Mock(
            spec=endpoint_service_client.EndpointServiceClient
        )
        endpoint_client_mock.get_endpoint.return_value = _TEST_ENDPOINT_GAPIC
        create_endpoint_client_mock.return_value = endpoint_client_mock
        yield create_endpoint_client_mock


@pytest.fixture
def predict_client_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "predict"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.PredictResponse(
            deployed_model_id=_TEST_MODEL_ID
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        yield predict_mock


@pytest.fixture
def predict_client_explain_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "explain"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service.ExplainResponse(
            deployed_model_id=_TEST_MODEL_ID,
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        predict_mock.return_value.explanations.extend(_TEST_EXPLANATIONS)
        predict_mock.return_value.explanations[0].attributions.extend(
            _TEST_ATTRIBUTIONS
        )
        yield predict_mock


class TestEndpoint:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor(self, create_endpoint_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        models.Endpoint(_TEST_ENDPOINT_NAME)
        create_endpoint_client_mock.assert_has_calls(
            [
                mock.call(
                    client_class=utils.EndpointClientWithOverride,
                    credentials=initializer.global_config.credentials,
                    location_override=_TEST_LOCATION,
                    prediction_client=False,
                ),
                mock.call(
                    client_class=utils.PredictionClientWithOverride,
                    credentials=None,
                    location_override=_TEST_LOCATION,
                    prediction_client=True,
                ),
            ]
        )

    def test_constructor_with_endpoint_id(self, get_endpoint_mock):
        models.Endpoint(_TEST_ID)
        get_endpoint_mock.assert_called_with(name=_TEST_ENDPOINT_NAME)

    def test_constructor_with_endpoint_name(self, get_endpoint_mock):
        models.Endpoint(_TEST_ENDPOINT_NAME)
        get_endpoint_mock.assert_called_with(name=_TEST_ENDPOINT_NAME)

    def test_constructor_with_custom_project(self, get_endpoint_mock):
        models.Endpoint(endpoint_name=_TEST_ID, project=_TEST_PROJECT_2)
        test_endpoint_resource_name = endpoint_service_client.EndpointServiceClient.endpoint_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )
        get_endpoint_mock.assert_called_with(name=test_endpoint_resource_name)

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_constructor_with_conflicting_location(self):
        """Passing a full resource name with `_TEST_LOCATION` and providing `_TEST_LOCATION_2` as location"""

        with pytest.raises(RuntimeError) as err:
            models.Endpoint(
                endpoint_name=_TEST_ENDPOINT_NAME, location=_TEST_LOCATION_2
            )

        assert err.match(
            regexp=r"is provided, but different from the resource location"
        )

    def test_constructor_with_custom_location(self, get_endpoint_alt_location_mock):
        models.Endpoint(endpoint_name=_TEST_ID, location=_TEST_LOCATION_2)
        test_endpoint_resource_name = endpoint_service_client.EndpointServiceClient.endpoint_path(
            _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
        )
        get_endpoint_alt_location_mock.assert_called_with(
            name=test_endpoint_resource_name
        )

    def test_constructor_with_custom_credentials(self, create_endpoint_client_mock):
        creds = auth_credentials.AnonymousCredentials()

        models.Endpoint(_TEST_ENDPOINT_NAME, credentials=creds)
        create_endpoint_client_mock.assert_has_calls(
            [
                mock.call(
                    client_class=utils.EndpointClientWithOverride,
                    credentials=creds,
                    location_override=_TEST_LOCATION,
                    prediction_client=False,
                ),
                mock.call(
                    client_class=utils.PredictionClientWithOverride,
                    credentials=creds,
                    location_override=_TEST_LOCATION,
                    prediction_client=True,
                ),
            ]
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_init_aiplatform_with_encryption_key_name_and_create_endpoint(
        self, create_endpoint_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )
        my_endpoint = models.Endpoint.create(display_name=_TEST_DISPLAY_NAME, sync=sync)

        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT, endpoint=expected_endpoint, metadata=(),
        )

        expected_endpoint.name = _TEST_ENDPOINT_NAME
        assert my_endpoint._gca_resource == expected_endpoint

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT, endpoint=expected_endpoint, metadata=(),
        )

        expected_endpoint.name = _TEST_ENDPOINT_NAME
        assert my_endpoint.gca_resource == expected_endpoint
        assert my_endpoint.network is None

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_accessing_properties_with_no_resource_raises(self,):

        my_endpoint = aiplatform.Endpoint(_TEST_ENDPOINT_NAME)

        my_endpoint._gca_resource = None

        with pytest.raises(RuntimeError) as e:
            my_endpoint.gca_resource
        e.match(regexp=r"Endpoint resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_endpoint.network
        e.match(regexp=r"Endpoint resource has not been created.")

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_description(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME, description=_TEST_DESCRIPTION, sync=sync
        )
        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, description=_TEST_DESCRIPTION,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT, endpoint=expected_endpoint, metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_labels(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME, labels=_TEST_LABELS, sync=sync
        )
        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, labels=_TEST_LABELS,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT, endpoint=expected_endpoint, metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(test_model, sync=sync)

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
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
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_display_name(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(
            model=test_model, deployed_model_display_name=_TEST_DISPLAY_NAME, sync=sync
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
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
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_80(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=80, sync=sync)

            if not sync:
                test_endpoint.wait()

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_120(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=120, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_negative(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=-18, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_min_replica(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, min_replica_count=-1, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_max_replica(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, max_replica_count=-2, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_split(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_split={"a": 99}, sync=sync)

    @pytest.mark.usefixtures("get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_traffic_percent(self, deploy_model_mock, sync):
        with mock.patch.object(
            endpoint_service_client.EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"model1": 100},
            )

            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(model=test_model, traffic_percentage=70, sync=sync)
            if not sync:
                test_endpoint.wait()
            automatic_resources = gca_machine_resources.AutomaticResources(
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
                traffic_split={"model1": 30, "0": 70},
                metadata=(),
            )

    @pytest.mark.usefixtures("get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_traffic_split(self, deploy_model_mock, sync):
        with mock.patch.object(
            endpoint_service_client.EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"model1": 100},
            )

            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_endpoint.deploy(
                model=test_model, traffic_split={"model1": 30, "0": 70}, sync=sync
            )

            if not sync:
                test_endpoint.wait()
            automatic_resources = gca_machine_resources.AutomaticResources(
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
                traffic_split={"model1": 30, "0": 70},
                metadata=(),
            )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_dedicated_resources(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(
            model=test_model,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            service_account=_TEST_SERVICE_ACCOUNT,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_explanations(self, deploy_model_with_explanations_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(
            model=test_model,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )
        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
        )
        expected_deployed_model = gca_endpoint.DeployedModel(
            dedicated_resources=expected_dedicated_resources,
            model=test_model.resource_name,
            display_name=None,
            explanation_spec=gca_endpoint.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
        )
        deploy_model_with_explanations_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_min_replica_count(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(model=test_model, min_replica_count=2, sync=sync)

        if not sync:
            test_endpoint.wait()
        automatic_resources = gca_machine_resources.AutomaticResources(
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
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_max_replica_count(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint.deploy(model=test_model, max_replica_count=2, sync=sync)
        if not sync:
            test_endpoint.wait()
        automatic_resources = gca_machine_resources.AutomaticResources(
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
        "model1, model2, model3, percent",
        [
            (100, None, None, 70),
            (50, 50, None, 70),
            (40, 60, None, 75),
            (40, 60, None, 88),
            (88, 12, None, 36),
            (11, 89, None, 18),
            (1, 99, None, 80),
            (1, 2, 97, 68),
            (99, 1, 0, 22),
            (0, 0, 100, 18),
            (7, 87, 6, 46),
        ],
    )
    def test_allocate_traffic(self, model1, model2, model3, percent):
        old_split = {}
        if model1 is not None:
            old_split["model1"] = model1
        if model2 is not None:
            old_split["model2"] = model2
        if model3 is not None:
            old_split["model3"] = model3

        new_split = models.Endpoint._allocate_traffic(old_split, percent)
        new_split_sum = 0
        for model in new_split:
            new_split_sum += new_split[model]

        assert new_split_sum == 100
        assert new_split["0"] == percent

    @pytest.mark.parametrize(
        "model1, model2, model3, deployed_model",
        [
            (100, None, None, "model1"),
            (50, 50, None, "model1"),
            (40, 60, None, "model2"),
            (40, 60, None, "model1"),
            (88, 12, None, "model1"),
            (11, 89, None, "model1"),
            (1, 99, None, "model2"),
            (1, 2, 97, "model1"),
            (99, 1, 0, "model2"),
            (0, 0, 100, "model3"),
            (7, 87, 6, "model2"),
        ],
    )
    def test_unallocate_traffic(self, model1, model2, model3, deployed_model):
        old_split = {}
        if model1 is not None:
            old_split["model1"] = model1
        if model2 is not None:
            old_split["model2"] = model2
        if model3 is not None:
            old_split["model3"] = model3

        new_split = models.Endpoint._unallocate_traffic(old_split, deployed_model)
        new_split_sum = 0
        for model in new_split:
            new_split_sum += new_split[model]

        assert new_split_sum == 100 or new_split_sum == 0
        assert new_split[deployed_model] == 0

    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy(self, undeploy_model_mock, sync):
        with mock.patch.object(
            endpoint_service_client.EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"model1": 100},
            )
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            assert dict(test_endpoint._gca_resource.traffic_split) == {"model1": 100}
            test_endpoint.undeploy("model1", sync=sync)
            if not sync:
                test_endpoint.wait()
            undeploy_model_mock.assert_called_once_with(
                endpoint=test_endpoint.resource_name,
                deployed_model_id="model1",
                traffic_split={},
                # traffic_split={"model1": 0},
                metadata=(),
            )

    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_with_traffic_split(self, undeploy_model_mock, sync):
        with mock.patch.object(
            endpoint_service_client.EndpointServiceClient, "get_endpoint"
        ) as get_endpoint_mock:
            get_endpoint_mock.return_value = gca_endpoint.Endpoint(
                display_name=_TEST_DISPLAY_NAME,
                name=_TEST_ENDPOINT_NAME,
                traffic_split={"model1": 40, "model2": 60},
            )
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="model1",
                traffic_split={"model1": 0, "model2": 100},
                sync=sync,
            )

            if not sync:
                test_endpoint.wait()

            undeploy_model_mock.assert_called_once_with(
                endpoint=test_endpoint.resource_name,
                deployed_model_id="model1",
                traffic_split={"model2": 100},
                metadata=(),
            )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_raise_error_traffic_split_total(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="model1", traffic_split={"model2": 99}, sync=sync
            )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_raise_error_undeployed_model_traffic(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="model1",
                traffic_split={"model1": 50, "model2": 50},
                sync=sync,
            )

    def test_predict(self, get_endpoint_mock, predict_client_predict_mock):

        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.predict(
            instances=_TEST_INSTANCES, parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=_TEST_PREDICTION, deployed_model_id=_TEST_ID
        )

        assert true_prediction == test_prediction
        predict_client_predict_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
        )

    def test_explain(self, get_endpoint_mock, predict_client_explain_mock):

        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
        )
        expected_explanations = _TEST_EXPLANATIONS
        expected_explanations[0].attributions.extend(_TEST_ATTRIBUTIONS)

        expected_prediction = models.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_ID,
            explanations=expected_explanations,
        )

        assert expected_prediction == test_prediction
        predict_client_explain_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
        )

    def test_list_models(self, get_endpoint_with_models_mock):

        ept = aiplatform.Endpoint(_TEST_ID)
        my_models = ept.list_models()

        assert my_models == _TEST_DEPLOYED_MODELS

    @pytest.mark.usefixtures("get_endpoint_with_models_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_all(self, sdk_private_undeploy_mock, sync):

        ept = aiplatform.Endpoint(_TEST_ID)
        ept.undeploy_all(sync=sync)

        if not sync:
            ept.wait()

        # undeploy_all() results in an undeploy() call for each deployed_model
        sdk_private_undeploy_mock.assert_has_calls(
            [
                mock.call(deployed_model_id=deployed_model.id, sync=sync)
                for deployed_model in _TEST_DEPLOYED_MODELS
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("list_endpoints_mock")
    def test_list_endpoint_has_prediction_client(self):
        """Test call to Endpoint.list() and ensure Endpoints have prediction client set"""
        ep_list = aiplatform.Endpoint.list(order_by=_TEST_LIST_ORDER_BY_CREATE_TIME)

        assert ep_list  # Ensure list is not empty

        # Confirm every Endpoint object in the list has a prediction client
        assert all(
            [
                isinstance(
                    e._prediction_client, aiplatform.utils.PredictionClientWithOverride
                )
                for e in ep_list
            ]
        )

    def test_list_endpoint_order_by_time(self, list_endpoints_mock):
        """Test call to Endpoint.list() and ensure list is returned in descending order of create_time"""

        ep_list = aiplatform.Endpoint.list(
            filter=_TEST_LIST_FILTER, order_by=_TEST_LIST_ORDER_BY_CREATE_TIME
        )

        # `order_by` is not passed to API since it is not an accepted field
        list_endpoints_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": _TEST_LIST_FILTER}
        )

        assert len(ep_list) == len(_TEST_ENDPOINT_LIST)

        for ep in ep_list:
            assert type(ep) == aiplatform.Endpoint

        assert ep_list[0].create_time > ep_list[1].create_time > ep_list[2].create_time

    def test_list_endpoint_order_by_display_name(self, list_endpoints_mock):
        """Test call to Endpoint.list() and ensure list is returned in order of display_name"""

        ep_list = aiplatform.Endpoint.list(
            filter=_TEST_LIST_FILTER, order_by=_TEST_LIST_ORDER_BY_DISPLAY_NAME
        )

        # `order_by` is not passed to API since it is not an accepted field
        list_endpoints_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": _TEST_LIST_FILTER}
        )

        assert len(ep_list) == len(_TEST_ENDPOINT_LIST)

        for ep in ep_list:
            assert type(ep) == aiplatform.Endpoint

        assert (
            ep_list[0].display_name < ep_list[1].display_name < ep_list[2].display_name
        )

    @pytest.mark.usefixtures("get_endpoint_with_models_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_endpoint_without_force(
        self, sdk_undeploy_all_mock, delete_endpoint_mock, sync
    ):

        ept = aiplatform.Endpoint(_TEST_ID)
        ept.delete(sync=sync)

        if not sync:
            ept.wait()

        # undeploy_all() should not be called unless force is set to True
        sdk_undeploy_all_mock.assert_not_called()

        delete_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    @pytest.mark.usefixtures("get_endpoint_with_models_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_endpoint_with_force(
        self, sdk_undeploy_all_mock, delete_endpoint_mock, sync
    ):

        ept = aiplatform.Endpoint(_TEST_ID)
        ept.delete(force=True, sync=sync)

        if not sync:
            ept.wait()

        # undeploy_all() should be called if force is set to True
        sdk_undeploy_all_mock.assert_called_once()

        delete_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)
