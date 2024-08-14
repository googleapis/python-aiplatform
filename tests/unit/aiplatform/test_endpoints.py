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

import copy
from datetime import datetime, timedelta
from importlib import reload
import json
from unittest import mock

from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import explain
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.services import (
    deployment_resource_pool_service_client_v1,
    deployment_resource_pool_service_client_v1beta1,
    endpoint_service_client,
    endpoint_service_client_v1beta1,
    model_service_client,
    prediction_service_async_client,
    prediction_service_async_client_v1beta1,
    prediction_service_client,
    prediction_service_client_v1beta1,
)
from google.cloud.aiplatform.compat.types import (
    deployment_resource_pool_v1 as gca_deployment_resource_pool_v1,
    deployment_resource_pool_v1beta1 as gca_deployment_resource_pool_v1beta1,
    encryption_spec as gca_encryption_spec,
    endpoint_service_v1beta1 as gca_endpoint_service_v1beta1,
    endpoint_service as gca_endpoint_service,
    endpoint_v1beta1 as gca_endpoint_v1beta1,
    endpoint as gca_endpoint,
    io as gca_io,
    machine_resources_v1beta1 as gca_machine_resources_v1beta1,
    machine_resources as gca_machine_resources,
    model as gca_model,
    prediction_service_v1beta1 as gca_prediction_service_v1beta1,
    prediction_service as gca_prediction_service,
    service_networking as gca_service_networking,
)
from google.cloud.aiplatform.preview import models as preview_models
import constants as test_constants
import pytest
import urllib3

from google.protobuf import field_mask_pb2


_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_LOCATION_2 = "europe-west4"

_TEST_DISPLAY_NAME = test_constants.EndpointConstants._TEST_DISPLAY_NAME
_TEST_DISPLAY_NAME_2 = test_constants.EndpointConstants._TEST_DISPLAY_NAME_2
_TEST_DISPLAY_NAME_3 = test_constants.EndpointConstants._TEST_DISPLAY_NAME_3
_TEST_ID = test_constants.EndpointConstants._TEST_ID
_TEST_ID_2 = test_constants.EndpointConstants._TEST_ID_2
_TEST_ID_3 = test_constants.EndpointConstants._TEST_ID_3
_TEST_DESCRIPTION = "test-description"
_TEST_REQUEST_METADATA = ()
_TEST_TIMEOUT = None

_TEST_ENDPOINT_NAME = test_constants.EndpointConstants._TEST_ENDPOINT_NAME
_TEST_ENDPOINT_NAME_2 = test_constants.EndpointConstants._TEST_ENDPOINT_NAME_2
_TEST_ENDPOINT_NAME_ALT_LOCATION = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION_2}/endpoints/{_TEST_ID}"
)
_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT
_TEST_MODEL_NAME = test_constants.EndpointConstants._TEST_MODEL_NAME
_TEST_DRP_NAME = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/deploymentResourcePools/{_TEST_ID}"
_TEST_VERSION_ID = test_constants.EndpointConstants._TEST_VERSION_ID

_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_ID}"
_TEST_PROJECT_ALLOWLIST = [_TEST_PROJECT]
_TEST_ENDPOINT_OVERRIDE = "endpoint-override.aiplatform.vertex.goog"

_TEST_MODEL_ID = test_constants.EndpointConstants._TEST_MODEL_ID
_TEST_METADATA = {"foo": "bar"}
_TEST_PREDICTION = test_constants.EndpointConstants._TEST_PREDICTION
_TEST_INSTANCES = [[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]]
_TEST_RAW_INPUTS = b"input bytes"
_TEST_RAW_OUTPUTS = b"output bytes"
_TEST_INPUTS = [{"dtype": "BOOL"}]
_TEST_OUTPUTS = [{"dtype": "STRING"}]
_TEST_METHOD_NAME = "test-method-name"
_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT

_TEST_DEPLOYED_MODELS = test_constants.EndpointConstants._TEST_DEPLOYED_MODELS

_TEST_TRAFFIC_SPLIT = test_constants.EndpointConstants._TEST_TRAFFIC_SPLIT

_TEST_LONG_TRAFFIC_SPLIT = {
    "m1": 40,
    "m2": 10,
    "m3": 30,
    "m4": 0,
    "m5": 20,
}
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

_TEST_EXPLANATIONS = [gca_prediction_service.explanation.Explanation(attributions=[])]
_TEST_V1BETA1_EXPLANATIONS = [
    gca_prediction_service_v1beta1.explanation.Explanation(attributions=[])
]

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

_TEST_V1BETA1_ATTRIBUTIONS = [
    gca_prediction_service_v1beta1.explanation.Attribution(
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

_TEST_SHAPLEY_EXPLANATION_SPEC_OVERRIDE = {
    "parameters": {"sampled_shapley_attribution": {"path_count": 10}}
}

_TEST_XRAI_EXPLANATION_SPEC_OVERRIDE = {
    "parameters": {"xrai_attribution": {"step_count": 50}}
}

_TEST_CONCURRENT_EXPLANATION_SPEC_OVERRIDE = {
    "shapley": _TEST_SHAPLEY_EXPLANATION_SPEC_OVERRIDE,
    "xrai": _TEST_XRAI_EXPLANATION_SPEC_OVERRIDE,
}

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

_TEST_PRIVATE_ENDPOINT_LIST = [
    gca_endpoint.Endpoint(
        name=_TEST_ENDPOINT_NAME,
        display_name="aac",
        create_time=datetime.now() - timedelta(minutes=15),
        network=_TEST_NETWORK,
    ),
    gca_endpoint.Endpoint(
        name=_TEST_ENDPOINT_NAME_2,
        display_name="psc",
        create_time=datetime.now() - timedelta(minutes=15),
        private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
            enable_private_service_connect=True,
            project_allowlist=_TEST_PROJECT_ALLOWLIST,
        ),
    ),
]

_TEST_LIST_FILTER = 'display_name="abc"'
_TEST_LIST_ORDER_BY_CREATE_TIME = "create_time desc"
_TEST_LIST_ORDER_BY_DISPLAY_NAME = "display_name"

_TEST_LABELS = {"my_key": "my_value"}

_TEST_REQUEST_RESPONSE_LOGGING_SAMPLING_RATE = 0.1
_TEST_REQUEST_RESPONSE_LOGGING_BQ_DEST = (
    output_uri
) = f"bq://{_TEST_PROJECT}/test_dataset/test_table"
_TEST_REQUEST_RESPONSE_LOGGING_CONFIG = (
    gca_endpoint.PredictRequestResponseLoggingConfig(
        enabled=True,
        sampling_rate=_TEST_REQUEST_RESPONSE_LOGGING_SAMPLING_RATE,
        bigquery_destination=gca_io.BigQueryDestination(
            output_uri=_TEST_REQUEST_RESPONSE_LOGGING_BQ_DEST
        ),
    )
)

"""
----------------------------------------------------------------------------
Endpoint Fixtures
----------------------------------------------------------------------------
"""


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
def get_empty_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(name=_TEST_ENDPOINT_NAME)
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
            traffic_split=_TEST_TRAFFIC_SPLIT,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_endpoint_with_many_models_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            deployed_models=_TEST_LONG_DEPLOYED_MODELS,
            traffic_split=_TEST_LONG_TRAFFIC_SPLIT,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_MODEL_NAME,
        )
        yield get_model_mock


@pytest.fixture
def create_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "create_endpoint"
    ) as create_endpoint_mock:
        create_endpoint_lro_mock = mock.Mock(ga_operation.Operation)
        create_endpoint_lro_mock.result.return_value = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        create_endpoint_mock.return_value = create_endpoint_lro_mock
        yield create_endpoint_mock


@pytest.fixture
def update_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "update_endpoint"
    ) as update_endpoint_mock:
        update_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield update_endpoint_mock


@pytest.fixture
def deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = gca_endpoint.DeployedModel(
            model=_TEST_MODEL_NAME,
            display_name=_TEST_DISPLAY_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = (
            gca_endpoint_service.DeployModelResponse(
                deployed_model=deployed_model,
            )
        )
        deploy_model_mock.return_value = deploy_model_lro_mock
        yield deploy_model_mock


@pytest.fixture
def preview_deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client_v1beta1.EndpointServiceClient, "deploy_model"
    ) as preview_deploy_model_mock:
        deployed_model = gca_endpoint_v1beta1.DeployedModel(
            model=_TEST_MODEL_NAME,
            display_name=_TEST_DISPLAY_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = (
            gca_endpoint_service_v1beta1.DeployModelResponse(
                deployed_model=deployed_model,
            )
        )
        preview_deploy_model_mock.return_value = deploy_model_lro_mock
        yield preview_deploy_model_mock


@pytest.fixture
def deploy_model_with_explanations_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = gca_endpoint.DeployedModel(
            model=_TEST_MODEL_NAME,
            display_name=_TEST_DISPLAY_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = (
            gca_endpoint_service.DeployModelResponse(
                deployed_model=deployed_model,
            )
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
        initializer.global_config,
        "create_client",
        autospec=True,
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
            deployed_model_id=_TEST_MODEL_ID,
            metadata=_TEST_METADATA,
            model_version_id=_TEST_VERSION_ID,
            model=_TEST_MODEL_NAME,
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        yield predict_mock


@pytest.fixture
def predict_async_client_predict_mock():
    response = gca_prediction_service.PredictResponse(
        deployed_model_id=_TEST_MODEL_ID,
        metadata=_TEST_METADATA,
        model_version_id=_TEST_VERSION_ID,
        model=_TEST_MODEL_NAME,
    )
    response.predictions.extend(_TEST_PREDICTION)
    with mock.patch.object(
        target=prediction_service_async_client.PredictionServiceAsyncClient,
        attribute="predict",
        return_value=response,
    ) as predict_mock:
        yield predict_mock


@pytest.fixture
def predict_client_direct_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "direct_predict"
    ) as direct_predict_mock:
        direct_predict_mock.return_value = gca_prediction_service.DirectPredictResponse(
            outputs=_TEST_OUTPUTS
        )
        yield direct_predict_mock


@pytest.fixture
def predict_client_direct_predict_async_mock():
    response = gca_prediction_service.DirectPredictResponse(outputs=_TEST_OUTPUTS)
    with mock.patch.object(
        target=prediction_service_async_client.PredictionServiceAsyncClient,
        attribute="direct_predict",
        return_value=response,
    ) as direct_predict_mock:
        yield direct_predict_mock


@pytest.fixture
def predict_client_direct_raw_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "direct_raw_predict"
    ) as direct_raw_predict_mock:
        direct_raw_predict_mock.return_value = (
            gca_prediction_service.DirectRawPredictResponse(output=_TEST_RAW_OUTPUTS)
        )
        yield direct_raw_predict_mock


@pytest.fixture
def predict_client_direct_raw_predict_async_mock():
    response = gca_prediction_service.DirectRawPredictResponse(output=_TEST_RAW_OUTPUTS)
    with mock.patch.object(
        target=prediction_service_async_client.PredictionServiceAsyncClient,
        attribute="direct_raw_predict",
        return_value=response,
    ) as direct_raw_predict_mock:
        yield direct_raw_predict_mock


@pytest.fixture
def predict_client_stream_direct_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "stream_direct_predict"
    ) as stream_direct_predict_mock:
        stream_direct_predict_mock.return_value = (
            gca_prediction_service.StreamDirectPredictResponse(outputs=_TEST_OUTPUTS),
            gca_prediction_service.StreamDirectPredictResponse(outputs=_TEST_OUTPUTS),
        )
        yield stream_direct_predict_mock


@pytest.fixture
def predict_client_stream_direct_raw_predict_mock():
    with mock.patch.object(
        prediction_service_client.PredictionServiceClient, "stream_direct_raw_predict"
    ) as stream_direct_raw_predict_mock:
        stream_direct_raw_predict_mock.return_value = (
            gca_prediction_service.StreamDirectRawPredictResponse(
                output=_TEST_RAW_OUTPUTS
            ),
            gca_prediction_service.StreamDirectRawPredictResponse(
                output=_TEST_RAW_OUTPUTS
            ),
        )
        yield stream_direct_raw_predict_mock


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


@pytest.fixture
def predict_client_v1beta1_explain_mock():
    with mock.patch.object(
        prediction_service_client_v1beta1.PredictionServiceClient, "explain"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service_v1beta1.ExplainResponse(
            deployed_model_id=_TEST_MODEL_ID,
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        predict_mock.return_value.explanations.extend(_TEST_V1BETA1_EXPLANATIONS)
        predict_mock.return_value.explanations[0].attributions.extend(
            _TEST_V1BETA1_ATTRIBUTIONS
        )
        predict_mock.return_value.concurrent_explanations = {
            "shapley": gca_prediction_service_v1beta1.ExplainResponse.ConcurrentExplanation(
                explanations=_TEST_V1BETA1_EXPLANATIONS,
            )
        }
        yield predict_mock


@pytest.fixture
def predict_async_client_v1beta1_explain_mock():
    with mock.patch.object(
        prediction_service_async_client_v1beta1.PredictionServiceAsyncClient, "explain"
    ) as predict_mock:
        predict_mock.return_value = gca_prediction_service_v1beta1.ExplainResponse(
            deployed_model_id=_TEST_MODEL_ID,
        )
        predict_mock.return_value.predictions.extend(_TEST_PREDICTION)
        predict_mock.return_value.explanations.extend(_TEST_V1BETA1_EXPLANATIONS)
        predict_mock.return_value.explanations[0].attributions.extend(
            _TEST_V1BETA1_ATTRIBUTIONS
        )
        yield predict_mock


@pytest.fixture
def predict_async_client_explain_mock():
    response = gca_prediction_service.ExplainResponse(
        deployed_model_id=_TEST_MODEL_ID,
    )
    response.predictions.extend(_TEST_PREDICTION)
    response.explanations.extend(_TEST_EXPLANATIONS)
    response.explanations[0].attributions.extend(_TEST_ATTRIBUTIONS)

    with mock.patch.object(
        target=prediction_service_async_client.PredictionServiceAsyncClient,
        attribute="explain",
        return_value=response,
    ) as explain_mock:
        yield explain_mock


@pytest.fixture
def preview_get_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client_v1beta1.DeploymentResourcePoolServiceClient,
        "get_deployment_resource_pool",
    ) as get_drp_mock:
        machine_spec = gca_machine_resources_v1beta1.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )

        autoscaling_metric_specs = [
            gca_machine_resources_v1beta1.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_CPU_UTILIZATION, target=70
            ),
            gca_machine_resources_v1beta1.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_GPU_UTILIZATION, target=70
            ),
        ]

        dedicated_resources = gca_machine_resources_v1beta1.DedicatedResources(
            machine_spec=machine_spec,
            min_replica_count=10,
            max_replica_count=20,
            autoscaling_metric_specs=autoscaling_metric_specs,
        )

        get_drp_mock.return_value = (
            gca_deployment_resource_pool_v1beta1.DeploymentResourcePool(
                name=_TEST_DRP_NAME,
                dedicated_resources=dedicated_resources,
            )
        )
        yield get_drp_mock


@pytest.fixture
def get_drp_mock():
    with mock.patch.object(
        deployment_resource_pool_service_client_v1.DeploymentResourcePoolServiceClient,
        "get_deployment_resource_pool",
    ) as get_drp_mock:
        machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )

        autoscaling_metric_specs = [
            gca_machine_resources.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_CPU_UTILIZATION, target=70
            ),
            gca_machine_resources.AutoscalingMetricSpec(
                metric_name=_TEST_METRIC_NAME_GPU_UTILIZATION, target=70
            ),
        ]

        dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=machine_spec,
            min_replica_count=10,
            max_replica_count=20,
            autoscaling_metric_specs=autoscaling_metric_specs,
        )

        get_drp_mock.return_value = (
            gca_deployment_resource_pool_v1.DeploymentResourcePool(
                name=_TEST_DRP_NAME,
                dedicated_resources=dedicated_resources,
            )
        )
        yield get_drp_mock


"""
----------------------------------------------------------------------------
Private Endpoint Fixtures
----------------------------------------------------------------------------
"""


@pytest.fixture
def create_psa_private_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "create_endpoint"
    ) as create_private_endpoint_mock:
        create_private_endpoint_lro_mock = mock.Mock(ga_operation.Operation)
        create_private_endpoint_lro_mock.result.return_value = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            network=_TEST_NETWORK,
        )
        create_private_endpoint_mock.return_value = create_private_endpoint_lro_mock
        yield create_private_endpoint_mock


@pytest.fixture
def get_psa_private_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            network=_TEST_NETWORK,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_psa_private_endpoint_with_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            network=_TEST_NETWORK,
            deployed_models=[_TEST_DEPLOYED_MODELS[0]],
        )
        yield get_endpoint_mock


@pytest.fixture
def create_psc_private_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "create_endpoint"
    ) as create_private_endpoint_mock:
        create_private_endpoint_lro_mock = mock.Mock(ga_operation.Operation)
        create_private_endpoint_lro_mock.result.return_value = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
            ),
        )
        create_private_endpoint_mock.return_value = create_private_endpoint_lro_mock
        yield create_private_endpoint_mock


@pytest.fixture
def get_psc_private_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
            ),
        )
        yield get_endpoint_mock


@pytest.fixture
def get_psc_private_endpoint_with_many_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
            ),
            deployed_models=_TEST_LONG_DEPLOYED_MODELS,
            traffic_split=_TEST_LONG_TRAFFIC_SPLIT,
        )
        yield get_endpoint_mock


@pytest.fixture
def predict_private_endpoint_mock():
    with mock.patch.object(urllib3.PoolManager, "request") as predict_mock:
        predict_mock.return_value = urllib3.response.HTTPResponse(
            status=200,
            body=json.dumps(
                {
                    "predictions": _TEST_PREDICTION,
                    "metadata": _TEST_METADATA,
                    "deployedModelId": _TEST_DEPLOYED_MODELS[0].id,
                    "model": _TEST_MODEL_NAME,
                    "modelVersionId": "1",
                }
            ),
        )
        yield predict_mock


@pytest.fixture
def health_check_private_endpoint_mock():
    with mock.patch.object(urllib3.PoolManager, "request") as health_check_mock:
        health_check_mock.return_value = urllib3.response.HTTPResponse(status=200)
        yield health_check_mock


@pytest.fixture
def list_private_endpoints_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "list_endpoints"
    ) as list_endpoints_mock:
        list_endpoints_mock.return_value = _TEST_PRIVATE_ENDPOINT_LIST
        yield list_endpoints_mock


@pytest.fixture
def sdk_undeploy_mock():
    """Mocks the high-level PrivateEndpoint.undeploy() SDK method"""
    with mock.patch.object(aiplatform.PrivateEndpoint, "undeploy") as sdk_undeploy_mock:
        sdk_undeploy_mock.return_value = None
        yield sdk_undeploy_mock


@pytest.mark.usefixtures("google_auth_mock")
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
                    appended_user_agent=None,
                ),
            ]
        )

    def test_lazy_constructor_with_endpoint_id(self, get_endpoint_mock):
        ep = models.Endpoint(_TEST_ID)
        assert ep._gca_resource.name == _TEST_ENDPOINT_NAME
        assert ep._skipped_getter_call()
        assert not get_endpoint_mock.called

    def test_lazy_constructor_with_endpoint_name(self, get_endpoint_mock):
        ep = models.Endpoint(_TEST_ENDPOINT_NAME)
        assert ep._gca_resource.name == _TEST_ENDPOINT_NAME
        assert ep._skipped_getter_call()
        assert not get_endpoint_mock.called

    def test_lazy_constructor_calls_get_on_property_access(self, get_endpoint_mock):
        ep = models.Endpoint(_TEST_ENDPOINT_NAME)
        assert ep._gca_resource.name == _TEST_ENDPOINT_NAME
        assert ep._skipped_getter_call()
        assert not get_endpoint_mock.called

        ep.display_name  # Retrieve a property that requires a call to Endpoint getter
        get_endpoint_mock.assert_called_with(
            name=_TEST_ENDPOINT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_lazy_constructor_with_custom_project(self, get_endpoint_mock):
        ep = models.Endpoint(endpoint_name=_TEST_ID, project=_TEST_PROJECT_2)
        test_endpoint_resource_name = (
            endpoint_service_client.EndpointServiceClient.endpoint_path(
                _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
            )
        )
        assert not get_endpoint_mock.called

        ep.name  # Retrieve a property that requires a call to Endpoint getter
        get_endpoint_mock.assert_called_with(
            name=test_endpoint_resource_name, retry=base._DEFAULT_RETRY
        )

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

    def test_lazy_constructor_with_custom_location(
        self, get_endpoint_alt_location_mock
    ):
        ep = models.Endpoint(endpoint_name=_TEST_ID, location=_TEST_LOCATION_2)
        test_endpoint_resource_name = (
            endpoint_service_client.EndpointServiceClient.endpoint_path(
                _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
            )
        )

        # Get Endpoint not called due to lazy loading
        assert not get_endpoint_alt_location_mock.called

        ep.network  # Accessing a property that requires calling getter

        get_endpoint_alt_location_mock.assert_called_with(
            name=test_endpoint_resource_name, retry=base._DEFAULT_RETRY
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
                    appended_user_agent=None,
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
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            sync=sync,
            create_request_timeout=None,
        )

        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=None,
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
            create_request_timeout=None,
        )

        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=None,
        )

        expected_endpoint.name = _TEST_ENDPOINT_NAME
        assert my_endpoint._gca_resource == expected_endpoint

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_endpoint_id(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            endpoint_id=_TEST_ID,
            description=_TEST_DESCRIPTION,
            sync=sync,
            create_request_timeout=None,
        )
        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=_TEST_ID,
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_timeout(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
            create_request_timeout=180.0,
        )

        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, encryption_spec=_TEST_ENCRYPTION_SPEC
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=180.0,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_timeout_not_explicitly_set(self, create_endpoint_mock, sync):
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
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_empty_endpoint_mock")
    def test_accessing_properties_with_no_resource_raises(
        self,
    ):
        """Ensure a descriptive RuntimeError is raised when the
        GAPIC object has not been populated"""

        my_endpoint = aiplatform.Endpoint(_TEST_ENDPOINT_NAME)

        # Create a gca_resource without `name` being populated
        my_endpoint._gca_resource = gca_endpoint.Endpoint(create_time=datetime.now())

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
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            sync=sync,
            create_request_timeout=None,
        )
        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_labels(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
            sync=sync,
            create_request_timeout=None,
        )
        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            labels=_TEST_LABELS,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_create_with_request_response_logging(self, create_endpoint_mock, sync):
        my_endpoint = models.Endpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            enable_request_response_logging=True,
            request_response_logging_sampling_rate=_TEST_REQUEST_RESPONSE_LOGGING_SAMPLING_RATE,
            request_response_logging_bq_destination_table=_TEST_REQUEST_RESPONSE_LOGGING_BQ_DEST,
            sync=sync,
            create_request_timeout=None,
        )
        if not sync:
            my_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            predict_request_response_logging_config=_TEST_REQUEST_RESPONSE_LOGGING_CONFIG,
        )
        create_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            endpoint_id=None,
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_update_endpoint(self, update_endpoint_mock):
        endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        endpoint.update(
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
        )

        expected_endpoint = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        expected_update_mask = field_mask_pb2.FieldMask(
            paths=["display_name", "description", "labels"]
        )

        update_endpoint_mock.assert_called_once_with(
            endpoint=expected_endpoint,
            update_mask=expected_update_mask,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        update_endpoint_mock.return_value = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            labels=_TEST_LABELS,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

    @pytest.mark.usefixtures("get_endpoint_with_models_mock")
    def test_update_traffic_split(self, update_endpoint_mock):
        endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)

        endpoint.update(traffic_split={_TEST_ID: 10, _TEST_ID_2: 80, _TEST_ID_3: 10})

        expected_endpoint = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            deployed_models=_TEST_DEPLOYED_MODELS,
            traffic_split={_TEST_ID: 10, _TEST_ID_2: 80, _TEST_ID_3: 10},
        )
        expected_update_mask = field_mask_pb2.FieldMask(paths=["traffic_split"])

        update_endpoint_mock.assert_called_once_with(
            endpoint=expected_endpoint,
            update_mask=expected_update_mask,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        update_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            traffic_split={_TEST_ID: 10, _TEST_ID_2: 80, _TEST_ID_3: 10},
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            test_model,
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_timeout(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            test_model,
            sync=sync,
            deploy_request_timeout=180.0,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
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
            timeout=180.0,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_timeout_not_explicitly_set(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            test_model,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_display_name(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            deployed_model_display_name=_TEST_DISPLAY_NAME,
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_80(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
            test_endpoint.deploy(model=test_model, traffic_percentage=80, sync=sync)

            if not sync:
                test_endpoint.wait()

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_120(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
            test_endpoint.deploy(model=test_model, traffic_percentage=120, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_negative(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
            test_endpoint.deploy(model=test_model, traffic_percentage=-18, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_min_replica(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
            test_endpoint.deploy(model=test_model, min_replica_count=-1, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_max_replica(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
            test_endpoint.deploy(model=test_model, max_replica_count=-2, sync=sync)

    @pytest.mark.usefixtures("get_endpoint_with_models_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_raise_error_traffic_split(self, sync):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
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
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
            )
            test_endpoint.deploy(
                model=test_model,
                traffic_percentage=70,
                sync=sync,
                deploy_request_timeout=None,
            )
            if not sync:
                test_endpoint.wait()
            automatic_resources = gca_machine_resources.AutomaticResources(
                min_replica_count=1,
                max_replica_count=1,
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
                timeout=None,
            )

    @pytest.mark.usefixtures("get_endpoint_with_models_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_traffic_split(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            traffic_split={_TEST_ID: 10, _TEST_ID_2: 40, _TEST_ID_3: 10, "0": 40},
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()
        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={_TEST_ID: 10, _TEST_ID_2: 40, _TEST_ID_3: 10, "0": 40},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_dedicated_resources(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_autoscaling_target_cpu_utilization(
        self, deploy_model_mock, sync
    ):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            machine_type=_TEST_MACHINE_TYPE,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
            autoscaling_target_cpu_utilization=70,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
        )

        expected_autoscaling_metric_spec = gca_machine_resources.AutoscalingMetricSpec(
            metric_name=_TEST_METRIC_NAME_CPU_UTILIZATION,
            target=70,
        )

        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
        )
        expected_dedicated_resources.autoscaling_metric_specs.extend(
            [expected_autoscaling_metric_spec]
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_autoscaling_target_accelerator_duty_cycle(
        self, deploy_model_mock, sync
    ):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            service_account=_TEST_SERVICE_ACCOUNT,
            sync=sync,
            deploy_request_timeout=None,
            autoscaling_target_accelerator_duty_cycle=70,
        )

        if not sync:
            test_endpoint.wait()

        expected_machine_spec = gca_machine_resources.MachineSpec(
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
        )

        expected_autoscaling_metric_spec = gca_machine_resources.AutoscalingMetricSpec(
            metric_name=_TEST_METRIC_NAME_GPU_UTILIZATION,
            target=70,
        )

        expected_dedicated_resources = gca_machine_resources.DedicatedResources(
            machine_spec=expected_machine_spec,
            min_replica_count=1,
            max_replica_count=1,
        )
        expected_dedicated_resources.autoscaling_metric_specs.extend(
            [expected_autoscaling_metric_spec]
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_autoscaling_target_accelerator_duty_cycle_and_no_accelerator_type_or_count_raises(
        self, sync
    ):
        with pytest.raises(ValueError):
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_model = models.Model(_TEST_ID)
            test_model._gca_resource.supported_deployment_resources_types.append(
                aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
            )
            test_endpoint.deploy(
                model=test_model,
                sync=sync,
                autoscaling_target_accelerator_duty_cycle=70,
            )

            if not sync:
                test_endpoint.wait()

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_explanations(self, deploy_model_with_explanations_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.DEDICATED_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            sync=sync,
            deploy_request_timeout=None,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_min_replica_count(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            min_replica_count=2,
            sync=sync,
            deploy_request_timeout=None,
        )

        if not sync:
            test_endpoint.wait()
        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=2,
            max_replica_count=2,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_max_replica_count(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model,
            max_replica_count=2,
            sync=sync,
            deploy_request_timeout=None,
        )
        if not sync:
            test_endpoint.wait()
        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=2,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_disable_container_logging(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            test_model,
            sync=sync,
            deploy_request_timeout=None,
            disable_container_logging=True,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )
        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
            disable_container_logging=True,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "preview_get_drp_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_preview_deploy_with_deployment_resource_pool(
        self, preview_deploy_model_mock, sync
    ):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME).preview
        test_model = models.Model(_TEST_ID).preview
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.SHARED_RESOURCES,
        )
        test_drp = preview_models.DeploymentResourcePool(_TEST_DRP_NAME)

        test_endpoint.deploy(
            model=test_model,
            deployment_resource_pool=test_drp,
            sync=sync,
            deploy_request_timeout=None,
        )
        if not sync:
            test_endpoint.wait()

        deployed_model = gca_endpoint_v1beta1.DeployedModel(
            shared_resources=_TEST_DRP_NAME,
            model=test_model.resource_name,
            display_name=None,
            enable_container_logging=True,
        )
        preview_deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock", "get_drp_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_with_deployment_resource_pool(self, deploy_model_mock, sync):
        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.SHARED_RESOURCES,
        )
        test_drp = models.DeploymentResourcePool(_TEST_DRP_NAME)

        test_endpoint.deploy(
            model=test_model,
            deployment_resource_pool=test_drp,
            sync=sync,
            deploy_request_timeout=None,
        )
        if not sync:
            test_endpoint.wait()

        deployed_model = gca_endpoint.DeployedModel(
            shared_resources=_TEST_DRP_NAME,
            model=test_model.resource_name,
            display_name=None,
        )
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            traffic_split={"0": 100},
            metadata=(),
            timeout=None,
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
            assert dict(test_endpoint.traffic_split) == {"model1": 100}
            test_endpoint.undeploy("model1", sync=sync)
            if not sync:
                test_endpoint.wait()
            undeploy_model_mock.assert_called_once_with(
                endpoint=test_endpoint.resource_name,
                deployed_model_id="model1",
                traffic_split={},
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
        with pytest.raises(ValueError) as e:
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="model1", traffic_split={"model2": 99}, sync=sync
            )

        assert e.match("Sum of all traffic within traffic split needs to be 100.")

    @pytest.mark.usefixtures("get_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_raise_error_undeployed_model_traffic(self, sync):
        with pytest.raises(ValueError) as e:
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id="model1",
                traffic_split={"model1": 50, "model2": 50},
                sync=sync,
            )

        assert e.match("Model being undeployed should have 0 traffic.")

    @pytest.mark.usefixtures("get_endpoint_with_models_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_raises_error_on_zero_leftover_traffic(self, sync):
        """
        Attempting to undeploy model with 100% traffic on an Endpoint with
        multiple models deployed without an updated traffic_split should
        raise an informative error.
        """

        traffic_remaining = _TEST_TRAFFIC_SPLIT[_TEST_ID_2]

        assert traffic_remaining == 100  # Confirm this model has all traffic
        assert sum(_TEST_TRAFFIC_SPLIT.values()) == 100  # Mock traffic sums to 100%

        with pytest.raises(ValueError) as e:
            test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
            test_endpoint.undeploy(
                deployed_model_id=_TEST_ID_2,
                sync=sync,
            )

        assert e.match(
            f"Undeploying deployed model '{_TEST_ID_2}' would leave the remaining "
            f"traffic split at 0%."
        )

    @pytest.mark.usefixtures("get_endpoint_with_models_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_zero_traffic_model_without_new_traffic_split(
        self, undeploy_model_mock, sync
    ):
        """
        Attempting to undeploy model with zero traffic without providing
        a new traffic split should not raise any errors.
        """

        traffic_remaining = _TEST_TRAFFIC_SPLIT[_TEST_ID_3]

        assert not traffic_remaining  # Confirm there is zero traffic

        test_endpoint = models.Endpoint(_TEST_ENDPOINT_NAME)
        test_endpoint.undeploy(
            deployed_model_id=_TEST_ID_3,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        expected_new_traffic_split = copy.deepcopy(_TEST_TRAFFIC_SPLIT)
        expected_new_traffic_split.pop(_TEST_ID_3)

        undeploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model_id=_TEST_ID_3,
            traffic_split=expected_new_traffic_split,
            metadata=(),
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_predict(self, predict_client_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.predict(
            instances=_TEST_INSTANCES, parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_ID,
            metadata=_TEST_METADATA,
            model_version_id=_TEST_VERSION_ID,
            model_resource_name=_TEST_MODEL_NAME,
        )

        assert true_prediction == test_prediction
        predict_client_predict_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            timeout=None,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_predict_async(self, predict_async_client_predict_mock):
        """Tests the Endpoint.predict_async method."""
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = await test_endpoint.predict_async(
            instances=_TEST_INSTANCES, parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_ID,
            metadata=_TEST_METADATA,
            model_version_id=_TEST_VERSION_ID,
            model_resource_name=_TEST_MODEL_NAME,
        )

        assert true_prediction == test_prediction
        predict_async_client_predict_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_explain(self, predict_client_explain_mock):
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
            timeout=None,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_explain_async(self, predict_async_client_explain_mock):
        """Tests the Endpoint.explain_async method."""
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = await test_endpoint.explain_async(
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
        predict_async_client_explain_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_predict_with_timeout(self, predict_client_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)

        test_endpoint.predict(
            instances=_TEST_INSTANCES, parameters={"param": 3.0}, timeout=10.0
        )

        predict_client_predict_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            timeout=10.0,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_predict_with_timeout_not_explicitly_set(self, predict_client_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)

        test_endpoint.predict(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
        )

        predict_client_predict_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_direct_predict(self, predict_client_direct_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.direct_predict(inputs=_TEST_INPUTS)

        true_prediction = models.Prediction(
            predictions=_TEST_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_predict_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "inputs": _TEST_INPUTS,
                "parameters": None,
            },
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_direct_predict_with_parameters(self, predict_client_direct_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.direct_predict(
            inputs=_TEST_INPUTS, parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=_TEST_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_predict_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "inputs": _TEST_INPUTS,
                "parameters": {"param": 3.0},
            },
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_direct_predict_with_timeout(self, predict_client_direct_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.direct_predict(
            inputs=_TEST_INPUTS, timeout=10.0
        )

        true_prediction = models.Prediction(
            predictions=_TEST_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_predict_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "inputs": _TEST_INPUTS,
                "parameters": None,
            },
            timeout=10.0,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_direct_predict_async(self, predict_client_direct_predict_async_mock):
        """Tests the Endpoint.predict_async method."""
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = await test_endpoint.direct_predict_async(
            inputs=_TEST_INPUTS, parameters=None
        )

        true_prediction = models.Prediction(
            predictions=_TEST_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_predict_async_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "inputs": _TEST_INPUTS,
                "parameters": None,
            },
            timeout=None,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_direct_predict_async_with_parameters(
        self, predict_client_direct_predict_async_mock
    ):
        """Tests the Endpoint.predict_async method."""
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = await test_endpoint.direct_predict_async(
            inputs=_TEST_INPUTS, parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=_TEST_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_predict_async_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "inputs": _TEST_INPUTS,
                "parameters": {"param": 3.0},
            },
            timeout=None,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_direct_predict_async_with_timeout(
        self, predict_client_direct_predict_async_mock
    ):
        """Tests the Endpoint.predict_async method."""
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = await test_endpoint.direct_predict_async(
            inputs=_TEST_INPUTS, timeout=10.0
        )

        true_prediction = models.Prediction(
            predictions=_TEST_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_predict_async_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "inputs": _TEST_INPUTS,
                "parameters": None,
            },
            timeout=10.0,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_direct_raw_predict(self, predict_client_direct_raw_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.direct_raw_predict(
            method_name=_TEST_METHOD_NAME, request=_TEST_RAW_INPUTS
        )

        true_prediction = models.Prediction(
            predictions=_TEST_RAW_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_raw_predict_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "method_name": _TEST_METHOD_NAME,
                "input": _TEST_RAW_INPUTS,
            },
            timeout=None,
        )

    @pytest.mark.asyncio
    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_direct_raw_predict_async(
        self, predict_client_direct_raw_predict_async_mock
    ):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = await test_endpoint.direct_raw_predict_async(
            method_name=_TEST_METHOD_NAME, request=_TEST_RAW_INPUTS
        )

        true_prediction = models.Prediction(
            predictions=_TEST_RAW_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_raw_predict_async_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "method_name": _TEST_METHOD_NAME,
                "input": _TEST_RAW_INPUTS,
            },
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_direct_raw_predict_with_timeout(
        self, predict_client_direct_raw_predict_mock
    ):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction = test_endpoint.direct_raw_predict(
            method_name=_TEST_METHOD_NAME, request=_TEST_RAW_INPUTS, timeout=10.0
        )

        true_prediction = models.Prediction(
            predictions=_TEST_RAW_OUTPUTS,
            deployed_model_id=None,
            metadata=None,
            model_version_id=None,
            model_resource_name=None,
        )

        assert true_prediction == test_prediction
        predict_client_direct_raw_predict_mock.assert_called_once_with(
            request={
                "endpoint": _TEST_ENDPOINT_NAME,
                "method_name": _TEST_METHOD_NAME,
                "input": _TEST_RAW_INPUTS,
            },
            timeout=10.0,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_stream_direct_predict(self, predict_client_stream_direct_predict_mock):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction_iterator = test_endpoint.stream_direct_predict(
            inputs_iterator=iter([_TEST_INPUTS]), parameters=None
        )
        test_prediction = list(test_prediction_iterator)

        true_prediction = [
            models.Prediction(
                predictions=_TEST_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
            models.Prediction(
                predictions=_TEST_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
        ]

        assert true_prediction == test_prediction
        predict_client_stream_direct_predict_mock.assert_called_once()

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_stream_direct_predict_with_parameters(
        self, predict_client_stream_direct_predict_mock
    ):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction_iterator = test_endpoint.stream_direct_predict(
            inputs_iterator=iter([_TEST_INPUTS]), parameters={"param": 3.0}
        )
        test_prediction = list(test_prediction_iterator)

        true_prediction = [
            models.Prediction(
                predictions=_TEST_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
            models.Prediction(
                predictions=_TEST_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
        ]

        assert true_prediction == test_prediction
        predict_client_stream_direct_predict_mock.assert_called_once()

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_stream_direct_predict_with_timeout(
        self, predict_client_stream_direct_predict_mock
    ):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction_iterator = test_endpoint.stream_direct_predict(
            inputs_iterator=iter([_TEST_INPUTS]), parameters=None, timeout=10.0
        )
        test_prediction = list(test_prediction_iterator)

        true_prediction = [
            models.Prediction(
                predictions=_TEST_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
            models.Prediction(
                predictions=_TEST_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
        ]

        assert true_prediction == test_prediction
        predict_client_stream_direct_predict_mock.assert_called_once()

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_stream_direct_raw_predict(
        self, predict_client_stream_direct_raw_predict_mock
    ):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction_iterator = test_endpoint.stream_direct_raw_predict(
            method_name=_TEST_METHOD_NAME, requests=iter([_TEST_RAW_INPUTS])
        )
        test_prediction = list(test_prediction_iterator)

        true_prediction = [
            models.Prediction(
                predictions=_TEST_RAW_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
            models.Prediction(
                predictions=_TEST_RAW_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
        ]

        assert true_prediction == test_prediction
        predict_client_stream_direct_raw_predict_mock.assert_called_once()

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_stream_direct_raw_predict_with_timeout(
        self, predict_client_stream_direct_raw_predict_mock
    ):
        test_endpoint = models.Endpoint(_TEST_ID)
        test_prediction_iterator = test_endpoint.stream_direct_raw_predict(
            method_name=_TEST_METHOD_NAME,
            requests=iter([_TEST_RAW_INPUTS]),
            timeout=10.0,
        )
        test_prediction = list(test_prediction_iterator)

        true_prediction = [
            models.Prediction(
                predictions=_TEST_RAW_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
            models.Prediction(
                predictions=_TEST_RAW_OUTPUTS,
                deployed_model_id=None,
                metadata=None,
                model_version_id=None,
                model_resource_name=None,
            ),
        ]

        assert true_prediction == test_prediction
        predict_client_stream_direct_raw_predict_mock.assert_called_once()

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_explain_with_timeout(self, predict_client_explain_mock):
        test_endpoint = models.Endpoint(_TEST_ID)

        test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            timeout=10.0,
        )

        predict_client_explain_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            timeout=10.0,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_explain_with_timeout_not_explicitly_set(self, predict_client_explain_mock):
        test_endpoint = models.Endpoint(_TEST_ID)

        test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
        )

        predict_client_explain_mock.assert_called_once_with(
            endpoint=_TEST_ENDPOINT_NAME,
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_explain_with_explaination_spec_override(
        self, predict_client_v1beta1_explain_mock
    ):
        test_endpoint = aiplatform.Endpoint(_TEST_ID).preview

        test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            explanation_spec_override=_TEST_SHAPLEY_EXPLANATION_SPEC_OVERRIDE,
        )

        predict_client_v1beta1_explain_mock.assert_called_once_with(
            mock.ANY,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    def test_explain_with_concurrent_explaination_spec_override(
        self, predict_client_v1beta1_explain_mock
    ):
        test_endpoint = aiplatform.Endpoint(_TEST_ID).preview

        test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            concurrent_explanation_spec_override=_TEST_CONCURRENT_EXPLANATION_SPEC_OVERRIDE,
        )

        predict_client_v1beta1_explain_mock.assert_called_once_with(
            mock.ANY,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_explain_async_with_explaination_spec_override(
        self, predict_async_client_v1beta1_explain_mock
    ):
        test_endpoint = aiplatform.Endpoint(_TEST_ID).preview

        await test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            explanation_spec_override=_TEST_SHAPLEY_EXPLANATION_SPEC_OVERRIDE,
        )

        predict_async_client_v1beta1_explain_mock.assert_called_once_with(
            mock.ANY,
            timeout=None,
        )

    @pytest.mark.usefixtures("get_endpoint_mock")
    async def test_explain_async_with_concurrent_explaination_spec_override(
        self, predict_async_client_v1beta1_explain_mock
    ):
        test_endpoint = aiplatform.Endpoint(_TEST_ID).preview

        await test_endpoint.explain(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            deployed_model_id=_TEST_MODEL_ID,
            concurrent_explanation_spec_override=_TEST_CONCURRENT_EXPLANATION_SPEC_OVERRIDE,
        )

        predict_async_client_v1beta1_explain_mock.assert_called_once_with(
            mock.ANY,
            timeout=None,
        )

    def test_list_models(self, get_endpoint_with_models_mock):
        ept = aiplatform.Endpoint(_TEST_ID)
        my_models = ept.list_models()

        assert my_models == _TEST_DEPLOYED_MODELS

    @pytest.mark.usefixtures("get_endpoint_with_many_models_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_all(self, sdk_private_undeploy_mock, sync):
        ept = aiplatform.Endpoint(_TEST_ID)
        ept.undeploy_all(sync=sync)

        if not sync:
            ept.wait()

        # undeploy_all() results in an undeploy() call for each deployed_model
        # Models are undeployed in ascending order of traffic percentage
        expected_models_to_undeploy = ["m6", "m7"] + _TEST_LONG_TRAFFIC_SPLIT_SORTED_IDS
        sdk_private_undeploy_mock.assert_has_calls(
            [
                mock.call(deployed_model_id=deployed_model_id, sync=sync)
                for deployed_model_id in expected_models_to_undeploy
            ],
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
            assert isinstance(ep, aiplatform.Endpoint)

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
            assert isinstance(ep, aiplatform.Endpoint)

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


class TestPrivateEndpoint:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_psa(self, create_psa_private_endpoint_mock, sync):
        test_endpoint = models.PrivateEndpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            network=_TEST_NETWORK,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME, network=_TEST_NETWORK
        )

        create_psa_private_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            metadata=(),
            timeout=None,
            endpoint_id=None,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_psc(self, create_psc_private_endpoint_mock, sync):
        test_endpoint = models.PrivateEndpoint.create(
            display_name=_TEST_DISPLAY_NAME,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            private_service_connect_config=models.PrivateEndpoint.PrivateServiceConnectConfig(
                project_allowlist=_TEST_PROJECT_ALLOWLIST
            ),
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        expected_endpoint = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
            ),
        )

        create_psc_private_endpoint_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            endpoint=expected_endpoint,
            metadata=(),
            timeout=None,
            endpoint_id=None,
        )

    @pytest.mark.usefixtures("get_psa_private_endpoint_with_model_mock")
    def test_psa_predict(self, predict_private_endpoint_mock):
        test_endpoint = models.PrivateEndpoint(_TEST_ID)
        test_prediction = test_endpoint.predict(
            instances=_TEST_INSTANCES, parameters={"param": 3.0}
        )

        true_prediction = models.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_ID,
            metadata=_TEST_METADATA,
        )

        assert true_prediction == test_prediction
        predict_private_endpoint_mock.assert_called_once_with(
            method="POST",
            url="",
            body='{"instances": [[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]]}',
            headers={"Content-Type": "application/json"},
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    def test_psc_predict(self, predict_private_endpoint_mock):
        test_endpoint = models.PrivateEndpoint(
            project=_TEST_PROJECT, location=_TEST_LOCATION, endpoint_name=_TEST_ID
        )
        test_prediction = test_endpoint.predict(
            instances=_TEST_INSTANCES,
            parameters={"param": 3.0},
            endpoint_override=_TEST_ENDPOINT_OVERRIDE,
        )

        true_prediction = models.Prediction(
            predictions=_TEST_PREDICTION,
            deployed_model_id=_TEST_DEPLOYED_MODELS[0].id,
            metadata=_TEST_METADATA,
            model_version_id="1",
            model_resource_name=_TEST_MODEL_NAME,
        )

        assert true_prediction == test_prediction
        predict_private_endpoint_mock.assert_called_once_with(
            method="POST",
            url=f"https://{_TEST_ENDPOINT_OVERRIDE}/v1/projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}:predict",
            body='{"instances": [[1.0, 2.0, 3.0], [1.0, 3.0, 4.0]]}',
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer None",
            },
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    def test_psc_predict_without_endpoint_override(self):
        test_endpoint = models.PrivateEndpoint(
            project=_TEST_PROJECT, location=_TEST_LOCATION, endpoint_name=_TEST_ID
        )

        with pytest.raises(ValueError) as err:
            test_endpoint.predict(
                instances=_TEST_INSTANCES,
                parameters={"param": 3.0},
            )
        assert err.match(
            regexp=r"Cannot make a predict request because endpoint override is"
            "not provided. Please ensure an endpoint override is"
            "provided."
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    def test_psc_predict_with_invalid_endpoint_override(self):
        test_endpoint = models.PrivateEndpoint(
            project=_TEST_PROJECT, location=_TEST_LOCATION, endpoint_name=_TEST_ID
        )

        with pytest.raises(ValueError) as err:
            test_endpoint.predict(
                instances=_TEST_INSTANCES,
                parameters={"param": 3.0},
                endpoint_override="invalid@endpoint.override",
            )
        assert err.match(
            regexp=r"Invalid endpoint override provided. Please only use IP"
            "address or DNS."
        )

    @pytest.mark.usefixtures("get_psa_private_endpoint_with_model_mock")
    def test_psa_health_check(self, health_check_private_endpoint_mock):
        test_endpoint = models.PrivateEndpoint(_TEST_ID)
        test_health_check = test_endpoint.health_check()

        true_health_check = True

        assert true_health_check == test_health_check
        health_check_private_endpoint_mock.assert_called_once_with(
            method="GET", url="", body=None, headers=None
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    def test_psc_health_check(self):
        test_endpoint = models.PrivateEndpoint(
            project=_TEST_PROJECT, location=_TEST_LOCATION, endpoint_name=_TEST_ID
        )

        with pytest.raises(RuntimeError) as err:
            test_endpoint.health_check()
        assert err.match(
            regexp=r"Health check request is not supported on PSC based Private Endpoint."
        )

    @pytest.mark.usefixtures("get_psa_private_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psa_deploy(self, deploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            test_model,
            sync=sync,
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )

        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )

        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            metadata=(),
            timeout=None,
            traffic_split=None,
        )

    @pytest.mark.usefixtures("get_psa_private_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psa_deploy_traffic_split_not_supported(self, deploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        with pytest.raises(ValueError) as err:
            test_endpoint.deploy(
                test_model, sync=sync, traffic_split=_TEST_TRAFFIC_SPLIT
            )
        assert err.match(
            regexp=r"Traffic split is not supported for PSA based PrivateEndpoint."
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psc_deploy_traffic_split(self, deploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )
        test_endpoint.deploy(
            model=test_model, sync=sync, traffic_split=_TEST_TRAFFIC_SPLIT
        )

        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
        )

        deployed_model = gca_endpoint.DeployedModel(
            automatic_resources=automatic_resources,
            model=test_model.resource_name,
            display_name=None,
        )

        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=deployed_model,
            metadata=(),
            timeout=None,
            traffic_split=_TEST_TRAFFIC_SPLIT,
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psc_deploy_with_traffic_percentage(self, deploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_model = models.Model(_TEST_ID)
        test_endpoint._gca_resource.traffic_split = {"model1": 100}
        test_model._gca_resource.supported_deployment_resources_types.append(
            aiplatform.gapic.Model.DeploymentResourcesType.AUTOMATIC_RESOURCES
        )

        test_endpoint.deploy(
            model=test_model,
            traffic_percentage=70,
            sync=sync,
        )
        if not sync:
            test_endpoint.wait()

        automatic_resources = gca_machine_resources.AutomaticResources(
            min_replica_count=1,
            max_replica_count=1,
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
            timeout=None,
        )

    @pytest.mark.usefixtures("get_psa_private_endpoint_with_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psa_undeploy(self, undeploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_endpoint.undeploy("model1", sync=sync)

        if not sync:
            test_endpoint.wait()

        undeploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model_id="model1",
            metadata=(),
            traffic_split={},
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psc_undeploy(self, undeploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_endpoint.undeploy("model1", sync=sync)

        if not sync:
            test_endpoint.wait()

        undeploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model_id="model1",
            metadata=(),
            traffic_split={},
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psc_undeploy_with_traffic_split(self, undeploy_model_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_endpoint._gca_resource.traffic_split = {"model1": 40, "model2": 60}
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

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    def test_psc_update_traffic_split(self, update_endpoint_mock):
        endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)

        endpoint.update(traffic_split={_TEST_ID: 10, _TEST_ID_2: 80, _TEST_ID_3: 10})

        expected_endpoint = gca_endpoint.Endpoint(
            name=_TEST_ENDPOINT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
            ),
            traffic_split={_TEST_ID: 10, _TEST_ID_2: 80, _TEST_ID_3: 10},
        )
        expected_update_mask = field_mask_pb2.FieldMask(paths=["traffic_split"])

        update_endpoint_mock.assert_called_once_with(
            endpoint=expected_endpoint,
            update_mask=expected_update_mask,
            metadata=_TEST_REQUEST_METADATA,
            timeout=_TEST_TIMEOUT,
        )

        update_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_DISPLAY_NAME,
            name=_TEST_ENDPOINT_NAME,
            private_service_connect_config=gca_service_networking.PrivateServiceConnectConfig(
                enable_private_service_connect=True,
                project_allowlist=_TEST_PROJECT_ALLOWLIST,
            ),
            traffic_split={_TEST_ID: 10, _TEST_ID_2: 80, _TEST_ID_3: 10},
        )

    @pytest.mark.usefixtures("get_psc_private_endpoint_with_many_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_undeploy_all(self, sdk_private_undeploy_mock, sync):
        test_endpoint = aiplatform.Endpoint(_TEST_ID)
        test_endpoint.undeploy_all(sync=sync)

        if not sync:
            test_endpoint.wait()

        # undeploy_all() results in an undeploy() call for each deployed_model
        # Models are undeployed in ascending order of traffic percentage
        expected_models_to_undeploy = ["m6", "m7"] + _TEST_LONG_TRAFFIC_SPLIT_SORTED_IDS
        sdk_private_undeploy_mock.assert_has_calls(
            [
                mock.call(deployed_model_id=deployed_model_id, sync=sync)
                for deployed_model_id in expected_models_to_undeploy
            ],
        )

    @pytest.mark.usefixtures("get_psa_private_endpoint_with_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psa_delete_without_force(
        self, sdk_undeploy_mock, delete_endpoint_mock, sync
    ):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_endpoint.delete(sync=sync)

        if not sync:
            test_endpoint.wait()

        # undeploy() should not be called unless force is set to True
        sdk_undeploy_mock.assert_not_called()

        delete_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    @pytest.mark.usefixtures("get_psa_private_endpoint_with_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psa_delete_with_force(self, sdk_undeploy_mock, delete_endpoint_mock, sync):
        test_endpoint = models.PrivateEndpoint(_TEST_ENDPOINT_NAME)
        test_endpoint._gca_resource.deployed_models = [_TEST_DEPLOYED_MODELS[0]]
        test_endpoint.delete(sync=sync)

        if not sync:
            test_endpoint.wait()

        # undeploy() should not be called unless force is set to True
        sdk_undeploy_mock.called_once_with(deployed_model_id=_TEST_ID, sync=sync)

        delete_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psc_delete_with_force(
        self, sdk_undeploy_all_mock, delete_endpoint_mock, sync
    ):
        test_endpoint = aiplatform.Endpoint(_TEST_ID)
        test_endpoint.delete(force=True, sync=sync)

        if not sync:
            test_endpoint.wait()

        # undeploy_all() should be called if force is set to True
        sdk_undeploy_all_mock.assert_called_once()

        delete_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    @pytest.mark.usefixtures("get_psc_private_endpoint_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_psc_delete_without_force(
        self, sdk_undeploy_all_mock, delete_endpoint_mock, sync
    ):
        test_endpoint = aiplatform.Endpoint(_TEST_ID)
        test_endpoint.delete(sync=sync)

        if not sync:
            test_endpoint.wait()

        # undeploy_all() should not be called unless force is set to True
        sdk_undeploy_all_mock.assert_not_called()

        delete_endpoint_mock.assert_called_once_with(name=_TEST_ENDPOINT_NAME)

    @pytest.mark.usefixtures("list_private_endpoints_mock")
    def test_list(self):
        ep_list = aiplatform.PrivateEndpoint.list()
        assert len(ep_list) == 2  # Ensure list include both PSA and PSC endpoints

    def test_construct_sdk_resource_from_gapic_uses_resource_project(self):
        PROJECT = "my-project"
        LOCATION = "me-west1"
        endpoint_name = f"projects/{PROJECT}/locations/{LOCATION}/endpoints/123"
        endpoint = aiplatform.Endpoint._construct_sdk_resource_from_gapic(
            models.gca_endpoint_compat.Endpoint(name=endpoint_name)
        )
        assert endpoint.project == PROJECT
        assert endpoint.location == LOCATION
        assert endpoint.project != _TEST_PROJECT
        assert endpoint.location != _TEST_LOCATION

        endpoint2 = aiplatform.Endpoint._construct_sdk_resource_from_gapic(
            models.gca_endpoint_compat.Endpoint(name=endpoint_name),
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        assert endpoint2.project != _TEST_PROJECT
        assert endpoint2.location != _TEST_LOCATION
