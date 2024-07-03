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

from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models

from google.cloud.aiplatform.compat.services import (
    deployment_resource_pool_service_client,
)

from google.cloud.aiplatform.compat.types import (
    deployed_model_ref as gca_deployed_model_ref,
    deployment_resource_pool as gca_deployment_resource_pool,
    deployment_resource_pool_service as gca_deployment_resource_pool_service,
    endpoint as gca_endpoint,
    machine_resources as gca_machine_resources,
)


_TEST_PROJECT = "test-project"
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"

_TEST_DISPLAY_NAME = "test-display-name"
_TEST_DISPLAY_NAME_2 = "test-display-name-2"
_TEST_DISPLAY_NAME_3 = "test-display-name-3"
_TEST_ID = "1028944691210842416"
_TEST_ID_2 = "4366591682456584192"
_TEST_ID_3 = "5820582938582924817"
_TEST_DESCRIPTION = "test-description"
_TEST_REQUEST_METADATA = ()
_TEST_TIMEOUT = None

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

_TEST_DRP_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/deploymentResourcePools/{_TEST_ID}"
_TEST_VERSION_ID = "1"

_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_ID}"

_TEST_MODEL_ID = "1028944691210842416"
_TEST_PREDICTION = [[1.0, 2.0, 3.0], [3.0, 3.0, 1.0]]
_TEST_INSTANCES = [[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]]
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"

_TEST_DEPLOYED_MODELS = [
    gca_endpoint.DeployedModel(id=_TEST_ID, display_name=_TEST_DISPLAY_NAME),
    gca_endpoint.DeployedModel(id=_TEST_ID_2, display_name=_TEST_DISPLAY_NAME_2),
    gca_endpoint.DeployedModel(id=_TEST_ID_3, display_name=_TEST_DISPLAY_NAME_3),
]

_TEST_LONG_TRAFFIC_SPLIT_SORTED_IDS = ["m4", "m2", "m5", "m3", "m1"]
_TEST_LONG_DEPLOYED_MODELS = [
    gca_endpoint.DeployedModel(id=id, display_name=f"{id}_display_name")
    for id in ["m1", "m2", "m3", "m4", "m5", "m6", "m7"]
]

_TEST_MACHINE_TYPE = "n1-standard-32"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2

_TEST_METRIC_NAME_CPU_UTILIZATION = (
    "aiplatform.googleapis.com/prediction/online/cpu/utilization"
)
_TEST_METRIC_NAME_GPU_UTILIZATION = (
    "aiplatform.googleapis.com/prediction/online/accelerator/duty_cycle"
)

_TEST_MACHINE_SPEC = gca_machine_resources.MachineSpec(
    machine_type=_TEST_MACHINE_TYPE,
    accelerator_type=_TEST_ACCELERATOR_TYPE,
    accelerator_count=_TEST_ACCELERATOR_COUNT,
)

_TEST_AUTOSCALING_METRIC_SPECS = [
    gca_machine_resources.AutoscalingMetricSpec(
        metric_name=_TEST_METRIC_NAME_CPU_UTILIZATION, target=70
    ),
    gca_machine_resources.AutoscalingMetricSpec(
        metric_name=_TEST_METRIC_NAME_GPU_UTILIZATION, target=70
    ),
]

_TEST_DEDICATED_RESOURCES = gca_machine_resources.DedicatedResources(
    machine_spec=_TEST_MACHINE_SPEC,
    min_replica_count=10,
    max_replica_count=20,
    autoscaling_metric_specs=_TEST_AUTOSCALING_METRIC_SPECS,
)


@pytest.fixture
def get_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client.DeploymentResourcePoolServiceClient,
        "get_deployment_resource_pool",
    ) as get_drp_mock:
        get_drp_mock.return_value = gca_deployment_resource_pool.DeploymentResourcePool(
            name=_TEST_DRP_NAME,
            dedicated_resources=_TEST_DEDICATED_RESOURCES,
        )
        yield get_drp_mock


@pytest.fixture
def create_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client.DeploymentResourcePoolServiceClient,
        "create_deployment_resource_pool",
    ) as create_drp_mock:
        create_drp_lro_mock = mock.Mock(ga_operation.Operation)
        create_drp_lro_mock.result.return_value = (
            gca_deployment_resource_pool.DeploymentResourcePool(
                name=_TEST_DRP_NAME,
                dedicated_resources=_TEST_DEDICATED_RESOURCES,
            )
        )
        create_drp_mock.return_value = create_drp_lro_mock
        yield create_drp_mock


@pytest.fixture
def list_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client.DeploymentResourcePoolServiceClient,
        "list_deployment_resource_pools",
    ) as list_drp_mock:
        list_drp_mock.return_value = [
            gca_deployment_resource_pool.DeploymentResourcePool(
                name=_TEST_DRP_NAME,
                dedicated_resources=_TEST_DEDICATED_RESOURCES,
            )
        ]
        yield list_drp_mock


@pytest.fixture
def delete_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client.DeploymentResourcePoolServiceClient,
        "delete_deployment_resource_pool",
    ) as delete_drp_mock:
        delete_drp_lro_mock = mock.Mock(ga_operation.Operation)
        delete_drp_lro_mock.result.return_value = (
            gca_deployment_resource_pool_service.DeleteDeploymentResourcePoolRequest()
        )
        delete_drp_mock.return_value = delete_drp_lro_mock
        yield delete_drp_mock


@pytest.fixture()
def query_deployed_models_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client.DeploymentResourcePoolServiceClient,
        "query_deployed_models",
    ) as query_deployed_models_mock:
        pager = mock.Mock()
        pager.pages = [
            gca_deployment_resource_pool_service.QueryDeployedModelsResponse(
                deployed_model_refs=[
                    gca_deployed_model_ref.DeployedModelRef(
                        endpoint=_TEST_ID,
                        deployed_model_id=_TEST_ID_2,
                    )
                ],
                total_deployed_model_count=2,
                total_endpoint_count=1,
            ),
            gca_deployment_resource_pool_service.QueryDeployedModelsResponse(
                deployed_model_refs=[
                    gca_deployed_model_ref.DeployedModelRef(
                        endpoint=_TEST_ID,
                        deployed_model_id=_TEST_ID_3,
                    )
                ],
                total_deployed_model_count=2,
                total_endpoint_count=1,
            ),
        ]
        query_deployed_models_mock.return_value = pager
        yield query_deployed_models_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestDeploymentResourcePool:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor_gets_drp(self, get_drp_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        models.DeploymentResourcePool(_TEST_DRP_NAME)
        get_drp_mock.assert_called_once_with(
            name=_TEST_DRP_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures("get_drp_mock")
    def test_constructor_with_conflicting_location_fails(self):
        """Passing a full resource name with `_TEST_LOCATION` and providing `_TEST_LOCATION_2` as location"""

        with pytest.raises(RuntimeError) as err:
            models.DeploymentResourcePool(_TEST_DRP_NAME, location=_TEST_LOCATION_2)

        assert err.match(
            regexp=r"is provided, but different from the resource location"
        )

    @pytest.mark.usefixtures("create_drp_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create(self, create_drp_mock, sync):
        test_drp = models.DeploymentResourcePool.create(
            deployment_resource_pool_id=_TEST_ID,
            machine_type=_TEST_MACHINE_TYPE,
            min_replica_count=10,
            max_replica_count=20,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            autoscaling_target_cpu_utilization=70,
            autoscaling_target_accelerator_duty_cycle=70,
            sync=sync,
        )

        if not sync:
            test_drp.wait()

        expected_drp = gca_deployment_resource_pool.DeploymentResourcePool(
            dedicated_resources=_TEST_DEDICATED_RESOURCES
        )

        create_drp_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            deployment_resource_pool_id=_TEST_ID,
            deployment_resource_pool=expected_drp,
            metadata=(),
            timeout=None,
        )

        expected_drp.name = _TEST_DRP_NAME

        assert test_drp._gca_resource == expected_drp

    @pytest.mark.usefixtures("create_drp_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_timeout(self, create_drp_mock, sync):
        test_drp = models.DeploymentResourcePool.create(
            deployment_resource_pool_id=_TEST_ID,
            machine_type=_TEST_MACHINE_TYPE,
            min_replica_count=10,
            max_replica_count=20,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            autoscaling_target_cpu_utilization=70,
            autoscaling_target_accelerator_duty_cycle=70,
            sync=sync,
            create_request_timeout=100,
        )

        if not sync:
            test_drp.wait()

        expected_drp = gca_deployment_resource_pool.DeploymentResourcePool(
            dedicated_resources=_TEST_DEDICATED_RESOURCES
        )

        create_drp_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            deployment_resource_pool_id=_TEST_ID,
            deployment_resource_pool=expected_drp,
            metadata=(),
            timeout=100,
        )

        expected_drp.name = _TEST_DRP_NAME

        assert test_drp._gca_resource == expected_drp

    @pytest.mark.usefixtures("list_drp_mock")
    def test_list(self, list_drp_mock):
        drp_list = models.DeploymentResourcePool.list()

        list_drp_mock.assert_called_once()

        for drp in drp_list:
            assert isinstance(drp, models.DeploymentResourcePool)

    @pytest.mark.usefixtures("delete_drp_mock", "get_drp_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete(self, delete_drp_mock, get_drp_mock, sync):
        test_drp = models.DeploymentResourcePool(
            deployment_resource_pool_name=_TEST_DRP_NAME
        )
        test_drp.delete(sync=sync)

        if not sync:
            test_drp.wait()

        delete_drp_mock.assert_called_once_with(name=test_drp.resource_name)

    @pytest.mark.usefixtures("query_deployed_models_mock", "get_drp_mock")
    def test_query_deployed_models(self, query_deployed_models_mock, get_drp_mock):
        test_drp = models.DeploymentResourcePool(
            deployment_resource_pool_name=_TEST_DRP_NAME
        )
        dm_refs = test_drp.query_deployed_models()

        assert len(dm_refs) == 2
        query_deployed_models_mock.assert_called_once()
