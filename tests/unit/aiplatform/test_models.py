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
from concurrent import futures
import pytest
from unittest import mock
from unittest.mock import patch

from google.api_core import operation as ga_operation
from google.api_core import exceptions as api_exceptions
from google.auth import credentials as auth_credentials

from google.cloud import aiplatform

from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import models
from google.cloud.aiplatform import utils

from google.cloud.aiplatform_v1.services.endpoint_service import (
    client as endpoint_service_client,
)
from google.cloud.aiplatform_v1.services.job_service import client as job_service_client
from google.cloud.aiplatform_v1.services.model_service import (
    client as model_service_client,
)
from google.cloud.aiplatform.compat.services import pipeline_service_client
from google.cloud.aiplatform.compat.types import (
    batch_prediction_job as gca_batch_prediction_job,
    io as gca_io,
    job_state as gca_job_state,
    model as gca_model,
    endpoint as gca_endpoint,
    env_var as gca_env_var,
    explanation as gca_explanation,
    machine_resources as gca_machine_resources,
    model_service as gca_model_service,
    endpoint_service as gca_endpoint_service,
    encryption_spec as gca_encryption_spec,
)


from test_endpoints import create_endpoint_mock  # noqa: F401

_TEST_PROJECT = "test-project"
_TEST_PROJECT_2 = "test-project-2"
_TEST_LOCATION = "us-central1"
_TEST_LOCATION_2 = "europe-west4"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
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
_TEST_LABEL = {"team": "experimentation", "trial_id": "x435"}

_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_P100"
_TEST_ACCELERATOR_COUNT = 2
_TEST_STARTING_REPLICA_COUNT = 2
_TEST_MAX_REPLICA_COUNT = 12

_TEST_PIPELINE_RESOURCE_NAME = (
    "projects/my-project/locations/us-central1/trainingPipeline/12345"
)

_TEST_BATCH_PREDICTION_GCS_SOURCE = "gs://example-bucket/folder/instance.jsonl"
_TEST_BATCH_PREDICTION_GCS_SOURCE_LIST = [
    "gs://example-bucket/folder/instance1.jsonl",
    "gs://example-bucket/folder/instance2.jsonl",
]
_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX = "gs://example-bucket/folder/output"
_TEST_BATCH_PREDICTION_BQ_PREFIX = "ucaip-sample-tests"
_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL = (
    f"bq://{_TEST_BATCH_PREDICTION_BQ_PREFIX}"
)
_TEST_BATCH_PREDICTION_DISPLAY_NAME = "test-batch-prediction-job"
_TEST_BATCH_PREDICTION_JOB_NAME = job_service_client.JobServiceClient.batch_prediction_job_path(
    project=_TEST_PROJECT, location=_TEST_LOCATION, batch_prediction_job=_TEST_ID
)

_TEST_INSTANCE_SCHEMA_URI = "gs://test/schema/instance.yaml"
_TEST_PARAMETERS_SCHEMA_URI = "gs://test/schema/parameters.yaml"
_TEST_PREDICTION_SCHEMA_URI = "gs://test/schema/predictions.yaml"

_TEST_CREDENTIALS = mock.Mock(spec=auth_credentials.AnonymousCredentials())
_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"

_TEST_EXPLANATION_METADATA = aiplatform.explain.ExplanationMetadata(
    inputs={
        "features": {
            "input_tensor_name": "dense_input",
            "encoding": "BAG_OF_FEATURES",
            "modality": "numeric",
            "index_feature_mapping": ["abc", "def", "ghj"],
        }
    },
    outputs={"medv": {"output_tensor_name": "dense_2"}},
)
_TEST_EXPLANATION_PARAMETERS = aiplatform.explain.ExplanationParameters(
    {"sampled_shapley_attribution": {"path_count": 10}}
)

# CMEK encryption
_TEST_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_ENCRYPTION_SPEC = gca_encryption_spec.EncryptionSpec(
    kms_key_name=_TEST_ENCRYPTION_KEY_NAME
)

_TEST_MODEL_RESOURCE_NAME = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
)
_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
)
_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION = model_service_client.ModelServiceClient.model_path(
    _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
)

_TEST_OUTPUT_DIR = "gs://my-output-bucket"
_TEST_CONTAINER_REGISTRY_DESTINATION = (
    "us-central1-docker.pkg.dev/projectId/repoName/imageName"
)

_TEST_EXPORT_FORMAT_ID_IMAGE = "custom-trained"
_TEST_EXPORT_FORMAT_ID_ARTIFACT = "tf-saved-model"

_TEST_SUPPORTED_EXPORT_FORMATS_IMAGE = [
    gca_model.Model.ExportFormat(
        id=_TEST_EXPORT_FORMAT_ID_IMAGE,
        exportable_contents=[gca_model.Model.ExportFormat.ExportableContent.IMAGE],
    )
]

_TEST_SUPPORTED_EXPORT_FORMATS_ARTIFACT = [
    gca_model.Model.ExportFormat(
        id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
        exportable_contents=[gca_model.Model.ExportFormat.ExportableContent.ARTIFACT],
    )
]

_TEST_SUPPORTED_EXPORT_FORMATS_BOTH = [
    gca_model.Model.ExportFormat(
        id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
        exportable_contents=[
            gca_model.Model.ExportFormat.ExportableContent.ARTIFACT,
            gca_model.Model.ExportFormat.ExportableContent.IMAGE,
        ],
    )
]

_TEST_SUPPORTED_EXPORT_FORMATS_UNSUPPORTED = []
_TEST_CONTAINER_REGISTRY_DESTINATION


@pytest.fixture
def get_endpoint_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "get_endpoint"
    ) as get_endpoint_mock:
        test_endpoint_resource_name = endpoint_service_client.EndpointServiceClient.endpoint_path(
            _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
        )
        get_endpoint_mock.return_value = gca_endpoint.Endpoint(
            display_name=_TEST_MODEL_NAME, name=test_endpoint_resource_name,
        )
        yield get_endpoint_mock


@pytest.fixture
def get_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME, name=_TEST_MODEL_RESOURCE_NAME,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_custom_location_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_custom_project_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT,
            artifact_uri=_TEST_ARTIFACT_URI,
            description=_TEST_DESCRIPTION,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_training_job():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT,
            training_pipeline=_TEST_PIPELINE_RESOURCE_NAME,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_supported_export_formats_image():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_IMAGE,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_supported_export_formats_artifact():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_ARTIFACT,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_both_supported_export_formats():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_BOTH,
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_unsupported_export_formats():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            name=_TEST_MODEL_RESOURCE_NAME,
            supported_export_formats=_TEST_SUPPORTED_EXPORT_FORMATS_UNSUPPORTED,
        )
        yield get_model_mock


@pytest.fixture
def upload_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def upload_model_with_custom_project_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME_CUSTOM_PROJECT
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def upload_model_with_custom_location_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "upload_model"
    ) as upload_model_mock:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = gca_model_service.UploadModelResponse(
            model=_TEST_MODEL_RESOURCE_NAME_CUSTOM_LOCATION
        )
        upload_model_mock.return_value = mock_lro
        yield upload_model_mock


@pytest.fixture
def export_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "export_model"
    ) as export_model_mock:
        export_model_lro_mock = mock.Mock(ga_operation.Operation)
        export_model_lro_mock.metadata = gca_model_service.ExportModelOperationMetadata(
            output_info=gca_model_service.ExportModelOperationMetadata.OutputInfo(
                artifact_output_uri=_TEST_OUTPUT_DIR
            )
        )
        export_model_lro_mock.result.return_value = None
        export_model_mock.return_value = export_model_lro_mock
        yield export_model_mock


@pytest.fixture
def delete_model_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "delete_model"
    ) as delete_model_mock:
        delete_model_lro_mock = mock.Mock(ga_operation.Operation)
        delete_model_lro_mock.result.return_value = (
            gca_model_service.DeleteModelRequest()
        )
        delete_model_mock.return_value = delete_model_lro_mock
        yield delete_model_mock


@pytest.fixture
def deploy_model_mock():
    with mock.patch.object(
        endpoint_service_client.EndpointServiceClient, "deploy_model"
    ) as deploy_model_mock:
        deployed_model = gca_endpoint.DeployedModel(
            model=_TEST_MODEL_RESOURCE_NAME, display_name=_TEST_MODEL_NAME,
        )
        deploy_model_lro_mock = mock.Mock(ga_operation.Operation)
        deploy_model_lro_mock.result.return_value = gca_endpoint_service.DeployModelResponse(
            deployed_model=deployed_model,
        )
        deploy_model_mock.return_value = deploy_model_lro_mock
        yield deploy_model_mock


@pytest.fixture
def get_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_batch_prediction_job"
    ) as get_batch_prediction_job_mock:
        batch_prediction_mock = mock.Mock(
            spec=gca_batch_prediction_job.BatchPredictionJob
        )
        batch_prediction_mock.state = gca_job_state.JobState.JOB_STATE_SUCCEEDED
        batch_prediction_mock.name = _TEST_BATCH_PREDICTION_JOB_NAME
        get_batch_prediction_job_mock.return_value = batch_prediction_mock
        yield get_batch_prediction_job_mock


@pytest.fixture
def create_batch_prediction_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_batch_prediction_job"
    ) as create_batch_prediction_job_mock:
        batch_prediction_job_mock = mock.Mock(
            spec=gca_batch_prediction_job.BatchPredictionJob
        )
        batch_prediction_job_mock.name = _TEST_BATCH_PREDICTION_JOB_NAME
        create_batch_prediction_job_mock.return_value = batch_prediction_job_mock
        yield create_batch_prediction_job_mock


@pytest.fixture
def get_training_job_non_existent_mock():
    with patch.object(
        pipeline_service_client.PipelineServiceClient, "get_training_pipeline"
    ) as get_training_job_non_existent_mock:
        get_training_job_non_existent_mock.side_effect = api_exceptions.NotFound("404")

        yield get_training_job_non_existent_mock


@pytest.fixture
def create_client_mock():
    with mock.patch.object(
        initializer.global_config, "create_client"
    ) as create_client_mock:
        api_client_mock = mock.Mock(spec=model_service_client.ModelServiceClient)
        create_client_mock.return_value = api_client_mock
        yield create_client_mock


class TestModel:
    def setup_method(self):
        importlib.reload(initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_constructor_creates_client(self, create_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        models.Model(_TEST_ID)
        create_client_mock.assert_called_once_with(
            client_class=utils.ModelClientWithOverride,
            credentials=initializer.global_config.credentials,
            location_override=_TEST_LOCATION,
            prediction_client=False,
        )

    def test_constructor_create_client_with_custom_location(self, create_client_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            credentials=_TEST_CREDENTIALS,
        )
        models.Model(_TEST_ID, location=_TEST_LOCATION_2)
        create_client_mock.assert_called_once_with(
            client_class=utils.ModelClientWithOverride,
            credentials=initializer.global_config.credentials,
            location_override=_TEST_LOCATION_2,
            prediction_client=False,
        )

    def test_constructor_creates_client_with_custom_credentials(
        self, create_client_mock
    ):
        creds = auth_credentials.AnonymousCredentials()
        models.Model(_TEST_ID, credentials=creds)
        create_client_mock.assert_called_once_with(
            client_class=utils.ModelClientWithOverride,
            credentials=creds,
            location_override=_TEST_LOCATION,
            prediction_client=False,
        )

    def test_constructor_gets_model(self, get_model_mock):
        models.Model(_TEST_ID)
        get_model_mock.assert_called_once_with(name=_TEST_MODEL_RESOURCE_NAME)

    def test_constructor_gets_model_with_custom_project(self, get_model_mock):
        models.Model(_TEST_ID, project=_TEST_PROJECT_2)
        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )
        get_model_mock.assert_called_once_with(name=test_model_resource_name)

    def test_constructor_gets_model_with_custom_location(self, get_model_mock):
        models.Model(_TEST_ID, location=_TEST_LOCATION_2)
        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
        )
        get_model_mock.assert_called_once_with(name=test_model_resource_name)

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model(
        self, upload_model_mock, get_model_mock, sync
    ):

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME, container_spec=container_spec,
        )

        upload_model_mock.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            model=managed_model,
        )

        get_model_mock.assert_called_once_with(name=_TEST_MODEL_RESOURCE_NAME)

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_labels(
        self, upload_model_mock, get_model_mock, sync
    ):

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            labels=_TEST_LABEL,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        container_spec = gca_model.ModelContainerSpec(
            image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
        )

        managed_model = gca_model.Model(
            display_name=_TEST_MODEL_NAME,
            container_spec=container_spec,
            labels=_TEST_LABEL,
        )

        upload_model_mock.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            model=managed_model,
        )

        get_model_mock.assert_called_once_with(name=_TEST_MODEL_RESOURCE_NAME)

    def test_upload_raises_with_impartial_explanation_spec(self):

        with pytest.raises(ValueError) as e:
            models.Model.upload(
                display_name=_TEST_MODEL_NAME,
                artifact_uri=_TEST_ARTIFACT_URI,
                serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
                explanation_parameters=_TEST_EXPLANATION_PARAMETERS
                # Missing the required explanations_metadata field
            )

        assert e.match(regexp=r"`explanation_parameters` should be specified or None.")

    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_all_args(
        self, upload_model_mock, get_model_mock, sync
    ):

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            instance_schema_uri=_TEST_INSTANCE_SCHEMA_URI,
            parameters_schema_uri=_TEST_PARAMETERS_SCHEMA_URI,
            prediction_schema_uri=_TEST_PREDICTION_SCHEMA_URI,
            description=_TEST_DESCRIPTION,
            serving_container_command=_TEST_SERVING_CONTAINER_COMMAND,
            serving_container_args=_TEST_SERVING_CONTAINER_ARGS,
            serving_container_environment_variables=_TEST_SERVING_CONTAINER_ENVIRONMENT_VARIABLES,
            serving_container_ports=_TEST_SERVING_CONTAINER_PORTS,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            labels=_TEST_LABEL,
            sync=sync,
        )

        if not sync:
            my_model.wait()

        env = [
            gca_env_var.EnvVar(name=str(key), value=str(value))
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
            predict_schemata=gca_model.PredictSchemata(
                instance_schema_uri=_TEST_INSTANCE_SCHEMA_URI,
                parameters_schema_uri=_TEST_PARAMETERS_SCHEMA_URI,
                prediction_schema_uri=_TEST_PREDICTION_SCHEMA_URI,
            ),
            explanation_spec=gca_model.explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
        )

        upload_model_mock.assert_called_once_with(
            parent=initializer.global_config.common_location_path(),
            model=managed_model,
        )
        get_model_mock.assert_called_once_with(name=_TEST_MODEL_RESOURCE_NAME)

    @pytest.mark.usefixtures("get_model_with_custom_project_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_custom_project(
        self,
        upload_model_with_custom_project_mock,
        get_model_with_custom_project_mock,
        sync,
    ):

        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            project=_TEST_PROJECT_2,
            sync=sync,
        )

        if not sync:
            my_model.wait()

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

        upload_model_with_custom_project_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT_2}/locations/{_TEST_LOCATION}",
            model=managed_model,
        )

        get_model_with_custom_project_mock.assert_called_once_with(
            name=test_model_resource_name
        )

        assert my_model.uri == _TEST_ARTIFACT_URI
        assert my_model.supported_export_formats == {}
        assert my_model.supported_deployment_resources_types == []
        assert my_model.supported_input_storage_formats == []
        assert my_model.supported_output_storage_formats == []
        assert my_model.description == _TEST_DESCRIPTION

    @pytest.mark.usefixtures("get_model_with_custom_project_mock")
    def test_accessing_properties_with_no_resource_raises(self,):

        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT_2, _TEST_LOCATION, _TEST_ID
        )

        my_model = models.Model(test_model_resource_name)
        my_model._gca_resource = None

        with pytest.raises(RuntimeError) as e:
            my_model.uri
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_export_formats
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_deployment_resources_types
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_input_storage_formats
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.supported_output_storage_formats
        e.match(regexp=r"Model resource has not been created.")

        with pytest.raises(RuntimeError) as e:
            my_model.description
        e.match(regexp=r"Model resource has not been created.")

    @pytest.mark.usefixtures("get_model_with_custom_location_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_upload_uploads_and_gets_model_with_custom_location(
        self,
        upload_model_with_custom_location_mock,
        get_model_with_custom_location_mock,
        sync,
    ):
        test_model_resource_name = model_service_client.ModelServiceClient.model_path(
            _TEST_PROJECT, _TEST_LOCATION_2, _TEST_ID
        )

        my_model = models.Model.upload(
            display_name=_TEST_MODEL_NAME,
            artifact_uri=_TEST_ARTIFACT_URI,
            serving_container_image_uri=_TEST_SERVING_CONTAINER_IMAGE,
            serving_container_predict_route=_TEST_SERVING_CONTAINER_PREDICTION_ROUTE,
            serving_container_health_route=_TEST_SERVING_CONTAINER_HEALTH_ROUTE,
            location=_TEST_LOCATION_2,
            sync=sync,
        )

        if not sync:
            my_model.wait()

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

        upload_model_with_custom_location_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION_2}",
            model=managed_model,
        )

        get_model_with_custom_location_mock.assert_called_once_with(
            name=test_model_resource_name
        )

    @pytest.mark.usefixtures("get_endpoint_mock", "get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_endpoint = models.Endpoint(_TEST_ID)

        assert test_model.deploy(test_endpoint, sync=sync,) == test_endpoint

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

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_endpoint = test_model.deploy(sync=sync)

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

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_dedicated_resources(self, deploy_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_endpoint = test_model.deploy(
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
            machine_spec=expected_machine_spec, min_replica_count=1, max_replica_count=1
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

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    @pytest.mark.parametrize("sync", [True, False])
    def test_deploy_no_endpoint_with_explanations(self, deploy_model_mock, sync):
        test_model = models.Model(_TEST_ID)
        test_endpoint = test_model.deploy(
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
            machine_spec=expected_machine_spec, min_replica_count=1, max_replica_count=1
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
        deploy_model_mock.assert_called_once_with(
            endpoint=test_endpoint.resource_name,
            deployed_model=expected_deployed_model,
            traffic_split={"0": 100},
            metadata=(),
        )

    @pytest.mark.usefixtures(
        "get_endpoint_mock", "get_model_mock", "create_endpoint_mock"
    )
    def test_deploy_raises_with_impartial_explanation_spec(self):

        test_model = models.Model(_TEST_ID)

        with pytest.raises(ValueError) as e:
            test_model.deploy(
                machine_type=_TEST_MACHINE_TYPE,
                accelerator_type=_TEST_ACCELERATOR_TYPE,
                accelerator_count=_TEST_ACCELERATOR_COUNT,
                explanation_metadata=_TEST_EXPLANATION_METADATA,
                # Missing required `explanation_parameters` argument
            )

        assert e.match(regexp=r"`explanation_parameters` should be specified or None.")

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_init_aiplatform_with_encryption_key_name_and_batch_predict_gcs_source_and_dest(
        self, create_batch_prediction_job_mock, sync
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
        )
        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            model=model_service_client.ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            ),
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="jsonl",
            ),
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_and_dest(
        self, create_batch_prediction_job_mock, sync
    ):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            sync=sync,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            model=model_service_client.ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            ),
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="jsonl",
            ),
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_gcs_source_bq_dest(
        self, create_batch_prediction_job_mock, sync
    ):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            sync=sync,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            model=model_service_client.ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            ),
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                bigquery_destination=gca_io.BigQueryDestination(
                    output_uri=_TEST_BATCH_PREDICTION_BQ_DEST_PREFIX_WITH_PROTOCOL
                ),
                predictions_format="bigquery",
            ),
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            batch_prediction_job=expected_gapic_batch_prediction_job,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_with_all_args(self, create_batch_prediction_job_mock, sync):
        test_model = models.Model(_TEST_ID)
        creds = auth_credentials.AnonymousCredentials()

        # Make SDK batch_predict method call passing all arguments
        batch_prediction_job = test_model.batch_predict(
            job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            gcs_destination_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX,
            predictions_format="csv",
            model_parameters={},
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
            max_replica_count=_TEST_MAX_REPLICA_COUNT,
            generate_explanation=True,
            explanation_metadata=_TEST_EXPLANATION_METADATA,
            explanation_parameters=_TEST_EXPLANATION_PARAMETERS,
            labels=_TEST_LABEL,
            credentials=creds,
            encryption_spec_key_name=_TEST_ENCRYPTION_KEY_NAME,
            sync=sync,
        )

        if not sync:
            batch_prediction_job.wait()

        # Construct expected request
        expected_gapic_batch_prediction_job = gca_batch_prediction_job.BatchPredictionJob(
            display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
            model=model_service_client.ModelServiceClient.model_path(
                _TEST_PROJECT, _TEST_LOCATION, _TEST_ID
            ),
            input_config=gca_batch_prediction_job.BatchPredictionJob.InputConfig(
                instances_format="jsonl",
                gcs_source=gca_io.GcsSource(uris=[_TEST_BATCH_PREDICTION_GCS_SOURCE]),
            ),
            output_config=gca_batch_prediction_job.BatchPredictionJob.OutputConfig(
                gcs_destination=gca_io.GcsDestination(
                    output_uri_prefix=_TEST_BATCH_PREDICTION_GCS_DEST_PREFIX
                ),
                predictions_format="csv",
            ),
            dedicated_resources=gca_machine_resources.BatchDedicatedResources(
                machine_spec=gca_machine_resources.MachineSpec(
                    machine_type=_TEST_MACHINE_TYPE,
                    accelerator_type=_TEST_ACCELERATOR_TYPE,
                    accelerator_count=_TEST_ACCELERATOR_COUNT,
                ),
                starting_replica_count=_TEST_STARTING_REPLICA_COUNT,
                max_replica_count=_TEST_MAX_REPLICA_COUNT,
            ),
            generate_explanation=True,
            explanation_spec=gca_explanation.ExplanationSpec(
                metadata=_TEST_EXPLANATION_METADATA,
                parameters=_TEST_EXPLANATION_PARAMETERS,
            ),
            labels=_TEST_LABEL,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )

        create_batch_prediction_job_mock.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            batch_prediction_job=expected_gapic_batch_prediction_job,
        )

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_no_source(self, create_batch_prediction_job_mock):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call without source
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"source")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_two_sources(self, create_batch_prediction_job_mock):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call with two sources
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                bigquery_source=_TEST_BATCH_PREDICTION_BQ_PREFIX,
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"source")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_no_destination(self):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call without destination
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
            )

        assert e.match(regexp=r"destination")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_wrong_instance_format(self):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                instances_format="wrong",
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"accepted instances format")

    @pytest.mark.usefixtures("get_model_mock", "get_batch_prediction_job_mock")
    def test_batch_predict_wrong_prediction_format(self):

        test_model = models.Model(_TEST_ID)

        # Make SDK batch_predict method call
        with pytest.raises(ValueError) as e:
            test_model.batch_predict(
                job_display_name=_TEST_BATCH_PREDICTION_DISPLAY_NAME,
                gcs_source=_TEST_BATCH_PREDICTION_GCS_SOURCE,
                predictions_format="wrong",
                bigquery_destination_prefix=_TEST_BATCH_PREDICTION_BQ_PREFIX,
            )

        assert e.match(regexp=r"accepted prediction format")

    @pytest.mark.usefixtures("get_model_mock")
    @pytest.mark.parametrize("sync", [True, False])
    def test_delete_model(self, delete_model_mock, sync):

        test_model = models.Model(_TEST_ID)
        test_model.delete(sync=sync)

        if not sync:
            test_model.wait()

        delete_model_mock.assert_called_once_with(name=test_model.resource_name)

    @pytest.mark.usefixtures("get_model_mock")
    def test_print_model(self):
        test_model = models.Model(_TEST_ID)
        assert (
            repr(test_model)
            == f"{object.__repr__(test_model)} \nresource name: {test_model.resource_name}"
        )

    @pytest.mark.usefixtures("get_model_mock")
    def test_print_model_if_waiting(self):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource = None
        test_model._latest_future = futures.Future()
        assert (
            repr(test_model)
            == f"{object.__repr__(test_model)} is waiting for upstream dependencies to complete."
        )

    @pytest.mark.usefixtures("get_model_mock")
    def test_print_model_if_exception(self):
        test_model = models.Model(_TEST_ID)
        test_model._gca_resource = None
        mock_exception = Exception("mock exception")
        test_model._exception = mock_exception
        assert (
            repr(test_model)
            == f"{object.__repr__(test_model)} failed with {str(mock_exception)}"
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_artifact")
    def test_export_model_as_artifact(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        if not sync:
            test_model.wait()

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            artifact_destination=_TEST_OUTPUT_DIR,
        )

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            artifact_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_OUTPUT_DIR
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_image")
    def test_export_model_as_image(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
            image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
        )

        if not sync:
            test_model.wait()

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
            image_destination=gca_io.ContainerRegistryDestination(
                output_uri=_TEST_CONTAINER_REGISTRY_DESTINATION
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_both_supported_export_formats")
    def test_export_model_as_both_formats(self, export_model_mock, sync):
        """Exports a 'tf-saved-model' as both an artifact and an image"""

        test_model = models.Model(_TEST_ID)

        test_model.export_model(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
            artifact_destination=_TEST_OUTPUT_DIR,
        )

        if not sync:
            test_model.wait()

        expected_output_config = gca_model_service.ExportModelRequest.OutputConfig(
            export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
            image_destination=gca_io.ContainerRegistryDestination(
                output_uri=_TEST_CONTAINER_REGISTRY_DESTINATION
            ),
            artifact_destination=gca_io.GcsDestination(
                output_uri_prefix=_TEST_OUTPUT_DIR
            ),
        )

        export_model_mock.assert_called_once_with(
            name=f"{_TEST_PARENT}/models/{_TEST_ID}",
            output_config=expected_output_config,
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_unsupported_export_formats")
    def test_export_model_not_supported(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        with pytest.raises(ValueError) as e:
            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
                image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
            )

            if not sync:
                test_model.wait()

            assert e.match(
                regexp=f"The model `{_TEST_PARENT}/models/{_TEST_ID}` is not exportable."
            )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_image")
    def test_export_model_as_image_with_invalid_args(self, export_model_mock, sync):

        # Passing an artifact destination on an image-only Model
        with pytest.raises(ValueError) as dest_type_err:
            test_model = models.Model(_TEST_ID)

            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE,
                artifact_destination=_TEST_OUTPUT_DIR,
                sync=sync,
            )

            if not sync:
                test_model.wait()

        # Passing no destination type
        with pytest.raises(ValueError) as no_dest_err:
            test_model = models.Model(_TEST_ID)

            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_IMAGE, sync=sync,
            )

            if not sync:
                test_model.wait()

        # Passing an invalid export format ID
        with pytest.raises(ValueError) as format_err:
            test_model = models.Model(_TEST_ID)
            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
                image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
                sync=sync,
            )

            if not sync:
                test_model.wait()

        assert dest_type_err.match(
            regexp=r"This model can not be exported as an artifact."
        )
        assert no_dest_err.match(regexp=r"Please provide an")
        assert format_err.match(
            regexp=f"'{_TEST_EXPORT_FORMAT_ID_ARTIFACT}' is not a supported export format"
        )

    @pytest.mark.parametrize("sync", [True, False])
    @pytest.mark.usefixtures("get_model_with_supported_export_formats_artifact")
    def test_export_model_as_artifact_with_invalid_args(self, export_model_mock, sync):
        test_model = models.Model(_TEST_ID)

        # Passing an image destination on an artifact-only Model
        with pytest.raises(ValueError) as e:
            test_model.export_model(
                export_format_id=_TEST_EXPORT_FORMAT_ID_ARTIFACT,
                image_destination=_TEST_CONTAINER_REGISTRY_DESTINATION,
                sync=sync,
            )

            if not sync:
                test_model.wait()

            assert e.match(
                regexp=r"This model can not be exported as a container image."
            )

    @pytest.mark.usefixtures(
        "get_training_job_non_existent_mock", "get_model_with_training_job"
    )
    def test_get_and_return_subclass_not_found(self):
        test_model = models.Model(_TEST_ID)

        # Attempt to access Model's training job that no longer exists
        with pytest.raises(api_exceptions.NotFound) as e:
            test_model.training_job

        assert e.match(
            regexp=(
                r"The training job used to create this model could not be found: "
                fr"{_TEST_PIPELINE_RESOURCE_NAME}"
            )
        )
