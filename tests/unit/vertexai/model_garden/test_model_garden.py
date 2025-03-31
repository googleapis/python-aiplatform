# Copyright 2025 Google LLC
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
"""Unit tests for ModelGarden class."""

import importlib
from unittest import mock

from google import auth
from google.api_core import operation as ga_operation
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform_v1beta1 import types
from google.cloud.aiplatform_v1beta1.services import model_garden_service
from vertexai.preview import model_garden
import pytest

from google.protobuf import duration_pb2

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEST_MODEL_FULL_RESOURCE_NAME = (
    "publishers/google/models/paligemma@paligemma-224-float32"
)
_TEST_HUGGING_FACE_MODEL_FULL_RESOURCE_NAME = (
    "publishers/meta-llama/models/llama-3.3-70b-instruct"
)
_TEST_PUBLISHER_MODEL_NAME = "publishers/google/models/paligemma"
_TEST_HUGGING_FACE_PUBLISHER_MODEL_NAME = "publishers/hf-google/models/gemma-2-2b"
_TEST_MODEL_SIMPLIFIED_RESOURCE_NAME = "google/paligemma@paligemma-224-float32"
_TEST_MODEL_HUGGING_FACE_ID = "meta-llama/Llama-3.3-70B-Instruct"
_TEST_MODEL_HUGGING_FACE_RESOURCE_NAME = (
    "publishers/hf-meta-llama/models/llama-3.3-70b-instruct"
)
# Note: The full resource name is in lower case.
_TEST_MODEL_HUGGING_FACE_FULL_RESOURCE_NAME = (
    "publishers/hf-meta-llama/models/llama-3.3-70b-instruct@001"
)
_TEST_HUGGING_FACE_ACCESS_TOKEN = "test-access-token"
_TEST_GCS_URI = "gs://some-bucket/some-model"
_TEST_ENDPOINT_NAME = "projects/test-project/locations/us-central1/endpoints/1234567890"
_TEST_MODEL_NAME = "projects/test-project/locations/us-central1/models/9876543210"
_TEST_MODEL_CONTAINER_SPEC = types.ModelContainerSpec(
    image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
    command=["python", "main.py"],
    args=["--model-id=gemma-2b"],
    env=[types.EnvVar(name="MODEL_ID", value="gemma-2b")],
    ports=[types.Port(container_port=7080)],
    grpc_ports=[types.Port(container_port=7081)],
    predict_route="/predictions/v1/predict",
    health_route="/ping",
    deployment_timeout=duration_pb2.Duration(seconds=1800),
    shared_memory_size_mb=256,
    startup_probe=types.Probe(
        exec_=types.Probe.ExecAction(command=["python", "main.py"]),
        period_seconds=10,
        timeout_seconds=10,
    ),
    health_probe=types.Probe(
        exec_=types.Probe.ExecAction(command=["python", "health_check.py"]),
        period_seconds=10,
        timeout_seconds=10,
    ),
)


@pytest.fixture(scope="module")
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_mock:
        google_auth_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_mock


@pytest.fixture
def export_publisher_model_mock():
    """Mocks the export_publisher_model method."""
    with mock.patch.object(
        model_garden_service.ModelGardenServiceClient,
        "export_publisher_model",
    ) as export_publisher_model:
        mock_export_lro = mock.Mock(ga_operation.Operation)
        mock_export_lro.result.return_value = types.ExportPublisherModelResponse(
            publisher_model=_TEST_MODEL_FULL_RESOURCE_NAME,
            destination_uri=_TEST_GCS_URI,
        )
        export_publisher_model.return_value = mock_export_lro
        yield export_publisher_model


@pytest.fixture
def deploy_mock():
    """Mocks the deploy method."""
    with mock.patch.object(
        model_garden_service.ModelGardenServiceClient,
        "deploy",
    ) as deploy:
        mock_lro = mock.Mock(ga_operation.Operation)
        mock_lro.result.return_value = types.DeployResponse(
            endpoint=_TEST_ENDPOINT_NAME,
            model=_TEST_MODEL_FULL_RESOURCE_NAME,
        )
        deploy.return_value = mock_lro
        yield deploy


@pytest.fixture
def get_publisher_model_mock():
    with mock.patch.object(
        model_garden_service.ModelGardenServiceClient, "get_publisher_model"
    ) as get_publisher_model_mock:
        get_publisher_model_mock.side_effect = [
            types.PublisherModel(name=_TEST_PUBLISHER_MODEL_NAME),
            types.PublisherModel(
                name=_TEST_PUBLISHER_MODEL_NAME,
                supported_actions=types.PublisherModel.CallToAction(
                    multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                        multi_deploy_vertex=[
                            types.PublisherModel.CallToAction.Deploy(
                                dedicated_resources=types.DedicatedResources(
                                    machine_spec=types.MachineSpec(
                                        machine_type="g2-standard-16",
                                        accelerator_type="NVIDIA_L4",
                                        accelerator_count=1,
                                    )
                                )
                            )
                        ]
                    )
                ),
            ),
            types.PublisherModel(
                name=_TEST_MODEL_HUGGING_FACE_RESOURCE_NAME,
                supported_actions=types.PublisherModel.CallToAction(
                    multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                        multi_deploy_vertex=[
                            types.PublisherModel.CallToAction.Deploy(
                                dedicated_resources=types.DedicatedResources(
                                    machine_spec=types.MachineSpec(
                                        machine_type="g2-standard-16",
                                        accelerator_type="NVIDIA_L4",
                                        accelerator_count=1,
                                    )
                                )
                            )
                        ]
                    )
                ),
            ),
        ]
        yield get_publisher_model_mock


@pytest.fixture
def list_publisher_models_mock():
    """Mocks the list_publisher_models method."""
    with mock.patch.object(
        model_garden_service.ModelGardenServiceClient,
        "list_publisher_models",
    ) as list_publisher_models:
        pager_mg = mock.Mock()
        pager_mg.pages = [
            types.ListPublisherModelsResponse(
                publisher_models=[
                    types.PublisherModel(
                        name=_TEST_PUBLISHER_MODEL_NAME,
                        version_id="001",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                    types.PublisherModel(
                        name=_TEST_PUBLISHER_MODEL_NAME,
                        version_id="002",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                ],
            ),
            types.ListPublisherModelsResponse(
                publisher_models=[
                    types.PublisherModel(
                        name=_TEST_PUBLISHER_MODEL_NAME,
                        version_id="003",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                    types.PublisherModel(
                        name=_TEST_PUBLISHER_MODEL_NAME,
                        version_id="004",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                ],
            ),
        ]
        pager_hf = mock.Mock()
        pager_hf.pages = [
            types.ListPublisherModelsResponse(
                publisher_models=[
                    types.PublisherModel(
                        name=_TEST_HUGGING_FACE_PUBLISHER_MODEL_NAME,
                        version_id="001",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                    types.PublisherModel(
                        name=_TEST_HUGGING_FACE_PUBLISHER_MODEL_NAME,
                        version_id="002",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                ],
            ),
            types.ListPublisherModelsResponse(
                publisher_models=[
                    types.PublisherModel(
                        name=_TEST_HUGGING_FACE_PUBLISHER_MODEL_NAME,
                        version_id="003",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                    types.PublisherModel(
                        name=_TEST_HUGGING_FACE_PUBLISHER_MODEL_NAME,
                        version_id="004",
                        supported_actions=types.PublisherModel.CallToAction(
                            multi_deploy_vertex=types.PublisherModel.CallToAction.DeployVertex(
                                multi_deploy_vertex=[
                                    types.PublisherModel.CallToAction.Deploy(
                                        dedicated_resources=types.DedicatedResources(
                                            machine_spec=types.MachineSpec(
                                                machine_type="g2-standard-16",
                                                accelerator_type="NVIDIA_L4",
                                                accelerator_count=1,
                                            )
                                        )
                                    )
                                ]
                            )
                        ),
                    ),
                ],
            ),
        ]
        list_publisher_models.side_effect = [pager_mg, pager_hf]
        yield list_publisher_models


@pytest.mark.usefixtures(
    "google_auth_mock",
    "deploy_mock",
    "get_publisher_model_mock",
    "list_publisher_models_mock",
    "export_publisher_model_mock",
)
class TestModelGarden:
    """Test cases for ModelGarden class."""

    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)
        aiplatform.init(project=_TEST_PROJECT)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    def test_export_full_resource_name_success(self, export_publisher_model_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.export(_TEST_GCS_URI)
        export_publisher_model_mock.assert_called_once_with(
            types.ExportPublisherModelRequest(
                parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=types.GcsDestination(output_uri_prefix=_TEST_GCS_URI),
            ),
            metadata=[("x-goog-user-project", "test-project")],
        )

    def test_export_simplified_resource_name_success(self, export_publisher_model_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_SIMPLIFIED_RESOURCE_NAME)
        model.export(_TEST_GCS_URI)
        export_publisher_model_mock.assert_called_once_with(
            types.ExportPublisherModelRequest(
                parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=types.GcsDestination(output_uri_prefix=_TEST_GCS_URI),
            ),
            metadata=[("x-goog-user-project", "test-project")],
        )

    def test_export_hugging_face_id_success(self, export_publisher_model_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_HUGGING_FACE_ID)
        model.export(_TEST_GCS_URI)
        export_publisher_model_mock.assert_called_once_with(
            types.ExportPublisherModelRequest(
                parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                name=_TEST_HUGGING_FACE_MODEL_FULL_RESOURCE_NAME,
                destination=types.GcsDestination(output_uri_prefix=_TEST_GCS_URI),
            ),
            metadata=[("x-goog-user-project", "test-project")],
        )

    def test_deploy_full_resource_name_success(self, deploy_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy()
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            )
        )

    def test_deploy_simplified_resource_name_success(self, deploy_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_SIMPLIFIED_RESOURCE_NAME)
        model.deploy()
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            )
        )

    def test_deploy_hugging_face_id_success(self, deploy_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_HUGGING_FACE_ID)
        model.deploy()
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                hugging_face_model_id=_TEST_MODEL_HUGGING_FACE_ID.lower(),
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            )
        )

    def test_deploy_specify_machine_spec_success(self, deploy_mock):
        """Tests deploying a model with specified machine spec."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(
            machine_type="n1-standard-4",
            accelerator_type="NVIDIA_TESLA_T4",
            accelerator_count=1,
            min_replica_count=1,
            max_replica_count=1,
        )
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                deploy_config=types.DeployRequest.DeployConfig(
                    dedicated_resources=types.DedicatedResources(
                        machine_spec=types.MachineSpec(
                            machine_type="n1-standard-4",
                            accelerator_type="NVIDIA_TESLA_T4",
                            accelerator_count=1,
                        ),
                        min_replica_count=1,
                        max_replica_count=1,
                    )
                ),
            )
        )

    def test_deploy_specify_partial_machine_spec_success(self, deploy_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(
            accelerator_type="NVIDIA_TESLA_T4",
        )
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                deploy_config=types.DeployRequest.DeployConfig(
                    dedicated_resources=types.DedicatedResources(
                        machine_spec=types.MachineSpec(
                            accelerator_type="NVIDIA_TESLA_T4",
                        ),
                        min_replica_count=1,
                        max_replica_count=1,
                    )
                ),
            )
        )

    def test_deploy_with_timeout_success(self, deploy_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(deploy_request_timeout=10)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            ),
        )

    def test_deploy_with_display_names_success(self, deploy_mock):
        """Tests deploying a model with display names."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(
            endpoint_display_name="test-endpoint",
            model_display_name="test-model",
        )
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                model_config=types.DeployRequest.ModelConfig(
                    model_display_name="test-model",
                ),
                endpoint_config=types.DeployRequest.EndpointConfig(
                    endpoint_display_name="test-endpoint",
                ),
            )
        )

    def test_deploy_with_eula_success(self, deploy_mock):
        """Tests deploying a model with EULA."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(accept_eula=True)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                model_config=types.DeployRequest.ModelConfig(
                    accept_eula=True,
                ),
            )
        )

    def test_deploy_with_hugging_face_access_token_success(self, deploy_mock):
        """Tests deploying a model with Hugging Face access token."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_HUGGING_FACE_ID)
        model.deploy(hugging_face_access_token=_TEST_HUGGING_FACE_ACCESS_TOKEN)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                hugging_face_model_id=_TEST_MODEL_HUGGING_FACE_ID.lower(),
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                model_config=types.DeployRequest.ModelConfig(
                    hugging_face_access_token=_TEST_HUGGING_FACE_ACCESS_TOKEN,
                ),
            )
        )

    def test_deploy_with_spot_vm_success(self, deploy_mock):
        """Tests deploying a model with spot VM."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(spot=True)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                deploy_config=types.DeployRequest.DeployConfig(
                    dedicated_resources=types.DedicatedResources(spot=True),
                ),
            )
        )

    def test_deploy_with_reservation_success(self, deploy_mock):
        """Tests deploying a model with spot VM."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(
            reservation_affinity_type="SPECIFIC_RESERVATION",
            reservation_affinity_key="compute.googleapis.com/reservation-name",
            reservation_affinity_values=[
                "projects/test-project/zones/us-central1-a/reservations/test-reservation"
            ],
        )
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                deploy_config=types.DeployRequest.DeployConfig(
                    dedicated_resources=types.DedicatedResources(
                        machine_spec=types.MachineSpec(
                            reservation_affinity=types.ReservationAffinity(
                                reservation_affinity_type="SPECIFIC_RESERVATION",
                                key="compute.googleapis.com/reservation-name",
                                values=[
                                    "projects/test-project/zones/us-central1-a/reservations/test-reservation"
                                ],
                            )
                        )
                    )
                ),
            )
        )

    def test_deploy_with_dedicated_endpoint_success(self, deploy_mock):
        """Tests deploying a model with dedicated endpoint."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(use_dedicated_endpoint=True)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                endpoint_config=types.DeployRequest.EndpointConfig(
                    dedicated_endpoint_enabled=True
                ),
            )
        )

    def test_deploy_with_fast_tryout_enabled_success(self, deploy_mock):
        """Tests deploying a model with fast tryout enabled."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(fast_tryout_enabled=True)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                deploy_config=types.DeployRequest.DeployConfig(
                    fast_tryout_enabled=True
                ),
            )
        )

    def test_deploy_with_serving_container_image_success(self, deploy_mock):
        """Tests deploying a model with serving container spec."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
        )
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                model_config=types.DeployRequest.ModelConfig(
                    container_spec=types.ModelContainerSpec(
                        image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
                    )
                ),
            )
        )

    def test_deploy_with_serving_container_spec_success(self, deploy_mock):
        """Tests deploying a model with serving container spec."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(serving_container_spec=_TEST_MODEL_CONTAINER_SPEC)
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                model_config=types.DeployRequest.ModelConfig(
                    container_spec=_TEST_MODEL_CONTAINER_SPEC
                ),
            )
        )

    def test_deploy_with_serving_container_spec_no_image_uri_raises_error(self):
        """Tests getting the supported deploy options for a model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        expected_message = (
            "Serving container image uri is required for the serving container" " spec."
        )
        with pytest.raises(ValueError) as exception:
            model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
            model.deploy(
                serving_container_spec=types.ModelContainerSpec(
                    predict_route="/predictions/v1/predict",
                    health_route="/ping",
                )
            )
        assert str(exception.value) == expected_message

    def test_deploy_with_serving_container_spec_with_both_image_uri_raises_error(
        self,
    ):
        """Tests getting the supported deploy options for a model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        expected_message = (
            "Serving container image uri is already set in the serving container"
            " spec."
        )
        with pytest.raises(ValueError) as exception:
            model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
            model.deploy(
                serving_container_spec=types.ModelContainerSpec(
                    image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
                    predict_route="/predictions/v1/predict",
                    health_route="/ping",
                ),
                serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
            )
        assert str(exception.value) == expected_message

    def test_deploy_with_serving_container_spec_individual_fields_success(
        self, deploy_mock
    ):
        """Tests deploying a model with serving container spec."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )
        model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
        model.deploy(
            serving_container_image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
            serving_container_predict_route="/predictions/v1/predict",
            serving_container_health_route="/ping",
            serving_container_command=["python", "main.py"],
            serving_container_args=["--model-id=gemma-2b"],
            serving_container_environment_variables={"MODEL_ID": "gemma-2b"},
            serving_container_ports=[7080],
            serving_container_grpc_ports=[7081],
            serving_container_deployment_timeout=1800,
            serving_container_shared_memory_size_mb=256,
            serving_container_startup_probe_exec=["python", "main.py"],
            serving_container_startup_probe_period_seconds=10,
            serving_container_startup_probe_timeout_seconds=10,
            serving_container_health_probe_exec=["python", "health_check.py"],
            serving_container_health_probe_period_seconds=10,
            serving_container_health_probe_timeout_seconds=10,
        )
        deploy_mock.assert_called_once_with(
            types.DeployRequest(
                publisher_model_name=_TEST_MODEL_FULL_RESOURCE_NAME,
                destination=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                model_config=types.DeployRequest.ModelConfig(
                    container_spec=types.ModelContainerSpec(
                        image_uri="us-docker.pkg.dev/vertex-ai/vertex-vision-model-garden-dockers/pytorch-vllm-serve:20241202_0916_RC00",
                        command=["python", "main.py"],
                        args=["--model-id=gemma-2b"],
                        env=[types.EnvVar(name="MODEL_ID", value="gemma-2b")],
                        ports=[types.Port(container_port=7080)],
                        grpc_ports=[types.Port(container_port=7081)],
                        predict_route="/predictions/v1/predict",
                        health_route="/ping",
                        deployment_timeout=duration_pb2.Duration(seconds=1800),
                        shared_memory_size_mb=256,
                        startup_probe=types.Probe(
                            exec_=types.Probe.ExecAction(command=["python", "main.py"]),
                            period_seconds=10,
                            timeout_seconds=10,
                        ),
                        health_probe=types.Probe(
                            exec_=types.Probe.ExecAction(
                                command=["python", "health_check.py"]
                            ),
                            period_seconds=10,
                            timeout_seconds=10,
                        ),
                    )
                ),
            )
        )

    def test_list_deploy_options(self, get_publisher_model_mock):
        """Tests getting the supported deploy options for a model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        expected_message = (
            "Model does not support deployment, please use a deploy-able model"
            " instead. You can use the list_deployable_models() method to find out"
            " which ones currently support deployment."
        )
        with pytest.raises(ValueError) as exception:
            model = model_garden.OpenModel(model_name=_TEST_MODEL_FULL_RESOURCE_NAME)
            _ = model.list_deploy_options()
        assert str(exception.value) == expected_message

        model.list_deploy_options()
        get_publisher_model_mock.assert_called_with(
            types.GetPublisherModelRequest(
                name=_TEST_MODEL_FULL_RESOURCE_NAME,
                is_hugging_face_model=False,
                include_equivalent_model_garden_model_deployment_configs=True,
            )
        )

        hf_model = model_garden.OpenModel(_TEST_MODEL_HUGGING_FACE_ID)
        hf_model.list_deploy_options()
        get_publisher_model_mock.assert_called_with(
            types.GetPublisherModelRequest(
                name=_TEST_HUGGING_FACE_MODEL_FULL_RESOURCE_NAME,
                is_hugging_face_model=True,
                include_equivalent_model_garden_model_deployment_configs=True,
            )
        )

    def test_list_deployable_models(self, list_publisher_models_mock):
        """Tests getting the supported deploy options for a model."""
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        mg_models = model_garden.list_deployable_models()
        list_publisher_models_mock.assert_called_with(
            types.ListPublisherModelsRequest(
                parent="publishers/*",
                list_all_versions=True,
                filter="is_hf_wildcard(false)",
            )
        )

        assert mg_models == [
            "google/paligemma@001",
            "google/paligemma@002",
            "google/paligemma@003",
            "google/paligemma@004",
        ]

        hf_models = model_garden.list_deployable_models(list_hf_models=True)
        list_publisher_models_mock.assert_called_with(
            types.ListPublisherModelsRequest(
                parent="publishers/*",
                list_all_versions=True,
                filter=(
                    "is_hf_wildcard(true) AND "
                    "labels.VERIFIED_DEPLOYMENT_CONFIG=VERIFIED_DEPLOYMENT_SUCCEED"
                ),
            )
        )
        assert hf_models == [
            "google/gemma-2-2b",
            "google/gemma-2-2b",
            "google/gemma-2-2b",
            "google/gemma-2-2b",
        ]
