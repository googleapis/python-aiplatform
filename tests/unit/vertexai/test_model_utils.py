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

from importlib import reload
from unittest import mock

from google.cloud import aiplatform
from google.cloud.aiplatform import utils
import vertexai
from vertexai.preview._workflow.serialization_engine import (
    any_serializer,
    serializers_base,
)
from google.cloud.aiplatform.compat.services import job_service_client
from google.cloud.aiplatform.compat.types import (
    job_state as gca_job_state,
    custom_job as gca_custom_job,
    io as gca_io,
)
from google.cloud.aiplatform.compat.services import (
    model_garden_service_client,
    model_service_client,
)
from google.cloud.aiplatform.compat.types import (
    deployed_model_ref_v1,
    model as gca_model,
    publisher_model as gca_publisher_model,
)
from vertexai.preview import language_models
import pytest

import cloudpickle
import numpy as np
import sklearn
from sklearn.linear_model import _logistic
import tensorflow
import torch


# project constants
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_BUCKET = "gs://test-bucket"
_TEST_UNIQUE_NAME = "test-unique-name"


# framework-specific constants
_SKLEARN_MODEL = _logistic.LogisticRegression()
_TF_MODEL = tensorflow.keras.models.Model()
_PYTORCH_MODEL = torch.nn.Module()
_TEST_MODEL_GCS_URI = "gs://test_model_dir"
_MODEL_RESOURCE_NAME = "projects/123/locations/us-central1/models/456"
_REWRAPPER = "rewrapper"

# customJob constants
_TEST_CUSTOM_JOB_RESOURCE_NAME = "projects/123/locations/us-central1/customJobs/456"

# Tuned model constants
_TEST_ID = "123456789"
_TEST_TUNED_MODEL_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/models/{_TEST_ID}"
)
_TEST_TUNED_MODEL_ENDPOINT_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/endpoints/{_TEST_ID}"
)

_TEXT_BISON_PUBLISHER_MODEL_DICT = {
    "name": "publishers/google/models/text-bison",
    "version_id": "001",
    "open_source_category": "PROPRIETARY",
    "launch_stage": gca_publisher_model.PublisherModel.LaunchStage.GA,
    "publisher_model_template": "projects/{user-project}/locations/{location}/publishers/google/models/text-bison@001",
    "predict_schemata": {
        "instance_schema_uri": "gs://google-cloud-aiplatform/schema/predict/instance/text_generation_1.0.0.yaml",
        "parameters_schema_uri": "gs://google-cloud-aiplatfrom/schema/predict/params/text_generation_1.0.0.yaml",
        "prediction_schema_uri": "gs://google-cloud-aiplatform/schema/predict/prediction/text_generation_1.0.0.yaml",
    },
}


@pytest.fixture
def mock_serialize_model():
    with mock.patch.object(
        any_serializer.AnySerializer, "serialize"
    ) as mock_serialize_model:
        yield mock_serialize_model


@pytest.fixture
def mock_vertex_model():
    model = mock.MagicMock(aiplatform.Model)
    model.uri = _TEST_MODEL_GCS_URI
    model.container_spec.image_uri = "us-docker.xxx/sklearn-cpu.1-0:latest"
    model.labels = {"registered_by_vertex_ai": "true"}
    yield model


@pytest.fixture
def mock_vertex_model_invalid():
    model = mock.MagicMock(aiplatform.Model)
    model.uri = _TEST_MODEL_GCS_URI
    model.container_spec.image_uri = "us-docker.xxx/sklearn-cpu.1-0:latest"
    model.labels = {}
    yield model


@pytest.fixture
def mock_timestamped_unique_name():
    with mock.patch.object(
        utils, "timestamped_unique_name"
    ) as mock_timestamped_unique_name:
        mock_timestamped_unique_name.return_value = _TEST_UNIQUE_NAME
        yield mock_timestamped_unique_name


@pytest.fixture
def mock_model_upload(mock_vertex_model):
    with mock.patch.object(aiplatform.Model, "upload") as mock_model_upload:
        mock_model_upload.return_value = mock_vertex_model
        yield mock_model_upload


@pytest.fixture
def mock_get_vertex_model(mock_vertex_model):
    with mock.patch.object(aiplatform, "Model") as mock_get_vertex_model:
        mock_get_vertex_model.return_value = mock_vertex_model
        yield mock_get_vertex_model


@pytest.fixture
def mock_get_vertex_model_invalid(mock_vertex_model_invalid):
    with mock.patch.object(aiplatform, "Model") as mock_get_vertex_model:
        mock_get_vertex_model.return_value = mock_vertex_model_invalid
        yield mock_get_vertex_model


@pytest.fixture
def mock_deserialize_model():
    with mock.patch.object(
        any_serializer.AnySerializer, "deserialize"
    ) as mock_deserialize_model:

        mock_deserialize_model.side_effect = [
            _SKLEARN_MODEL,
            mock.Mock(return_value=None),
        ]
        yield mock_deserialize_model


@pytest.fixture
def mock_deserialize_model_exception():
    with mock.patch.object(
        any_serializer.AnySerializer, "deserialize"
    ) as mock_deserialize_model_exception:
        mock_deserialize_model_exception.side_effect = Exception
        yield mock_deserialize_model_exception


@pytest.fixture
def mock_any_serializer_serialize_sklearn():
    with mock.patch.object(
        any_serializer.AnySerializer,
        "serialize",
        side_effect=[
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"scikit-learn=={sklearn.__version__}"
                ]
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ]
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ]
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ]
            },
        ],
    ) as mock_any_serializer_serialize:
        yield mock_any_serializer_serialize


_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_DISPLAY_NAME = f"{_TEST_PARENT}/customJobs/12345"
_TEST_BUCKET_NAME = "gs://test_bucket"
_TEST_BASE_OUTPUT_DIR = f"{_TEST_BUCKET_NAME}/test_base_output_dir"

_TEST_INPUTS = [
    "--arg_0=string_val_0",
    "--arg_1=string_val_1",
    "--arg_2=int_val_0",
    "--arg_3=int_val_1",
]
_TEST_IMAGE_URI = "test_image_uri"
_TEST_MACHINE_TYPE = "test_machine_type"
_TEST_WORKER_POOL_SPEC = [
    {
        "machine_spec": {
            "machine_type": _TEST_MACHINE_TYPE,
        },
        "replica_count": 1,
        "container_spec": {
            "image_uri": _TEST_IMAGE_URI,
            "args": _TEST_INPUTS,
        },
    }
]
_TEST_CUSTOM_JOB_PROTO = gca_custom_job.CustomJob(
    display_name=_TEST_DISPLAY_NAME,
    job_spec={
        "worker_pool_specs": _TEST_WORKER_POOL_SPEC,
        "base_output_directory": gca_io.GcsDestination(
            output_uri_prefix=_TEST_BASE_OUTPUT_DIR
        ),
    },
    labels={"trained_by_vertex_ai": "true"},
)


@pytest.fixture
def mock_get_custom_job_pending():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as mock_get_custom_job:

        mock_get_custom_job.side_effect = [
            gca_custom_job.CustomJob(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_RUNNING,
                display_name=_TEST_DISPLAY_NAME,
                job_spec={
                    "worker_pool_specs": _TEST_WORKER_POOL_SPEC,
                    "base_output_directory": gca_io.GcsDestination(
                        output_uri_prefix=_TEST_BASE_OUTPUT_DIR
                    ),
                },
                labels={"trained_by_vertex_ai": "true"},
            ),
            gca_custom_job.CustomJob(
                name=_TEST_CUSTOM_JOB_RESOURCE_NAME,
                state=gca_job_state.JobState.JOB_STATE_SUCCEEDED,
                display_name=_TEST_DISPLAY_NAME,
                job_spec={
                    "worker_pool_specs": _TEST_WORKER_POOL_SPEC,
                    "base_output_directory": gca_io.GcsDestination(
                        output_uri_prefix=_TEST_BASE_OUTPUT_DIR
                    ),
                },
                labels={"trained_by_vertex_ai": "true"},
            ),
        ]
        yield mock_get_custom_job


@pytest.fixture
def mock_get_custom_job_failed():
    with mock.patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as mock_get_custom_job:
        custom_job_proto = _TEST_CUSTOM_JOB_PROTO
        custom_job_proto.name = _TEST_CUSTOM_JOB_RESOURCE_NAME
        custom_job_proto.state = gca_job_state.JobState.JOB_STATE_FAILED
        mock_get_custom_job.return_value = custom_job_proto
        yield mock_get_custom_job


@pytest.fixture
def get_model_with_tuned_version_label_mock():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name="test-display-name",
            name=_TEST_TUNED_MODEL_NAME,
            labels={"google-vertex-llm-tuning-base-model-id": "text-bison-001"},
            deployed_models=[
                deployed_model_ref_v1.DeployedModelRef(
                    endpoint=_TEST_TUNED_MODEL_ENDPOINT_NAME,
                    deployed_model_id=_TEST_TUNED_MODEL_NAME,
                )
            ],
        )
        yield get_model_mock


@pytest.fixture
def get_model_with_invalid_tuned_version_labels():
    with mock.patch.object(
        model_service_client.ModelServiceClient, "get_model"
    ) as get_model_mock:
        get_model_mock.return_value = gca_model.Model(
            display_name="test-display-name",
            name=_TEST_TUNED_MODEL_NAME,
            labels={
                "google-vertex-llm-tuning-base-model-id": "invalidlabel",
                "another": "label",
            },
            deployed_models=[
                deployed_model_ref_v1.DeployedModelRef(
                    endpoint=_TEST_TUNED_MODEL_ENDPOINT_NAME,
                    deployed_model_id=_TEST_TUNED_MODEL_NAME,
                )
            ],
        )
        yield get_model_mock


@pytest.fixture
def mock_get_publisher_model():
    with mock.patch.object(
        model_garden_service_client.ModelGardenServiceClient,
        "get_publisher_model",
        return_value=gca_publisher_model.PublisherModel(
            _TEXT_BISON_PUBLISHER_MODEL_DICT
        ),
    ) as mock_get_publisher_model:
        yield mock_get_publisher_model


@pytest.mark.usefixtures("google_auth_mock")
class TestModelUtils:
    def setup_method(self):
        reload(aiplatform)
        reload(vertexai)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("mock_timestamped_unique_name")
    def test_register_sklearn_model(self, mock_model_upload, mock_serialize_model):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )
        vertex_model = vertexai.preview.register(_SKLEARN_MODEL)

        expected_display_name = (
            f"vertex-ai-registered-sklearn-model-{_TEST_UNIQUE_NAME}"
        )
        expected_uri = f"{_TEST_BUCKET}/{expected_display_name}"
        expected_container_uri = (
            aiplatform.helpers.get_prebuilt_prediction_container_uri(
                framework="sklearn",
                framework_version="1.0",
            )
        )

        assert vertex_model.uri == _TEST_MODEL_GCS_URI
        mock_model_upload.assert_called_once_with(
            display_name=expected_display_name,
            artifact_uri=expected_uri,
            serving_container_image_uri=expected_container_uri,
            labels={"registered_by_vertex_ai": "true"},
            sync=True,
        )
        assert 2 == mock_serialize_model.call_count
        mock_serialize_model.assert_has_calls(
            calls=[
                mock.call(
                    _SKLEARN_MODEL,
                    f"{expected_uri}/model.pkl",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.parametrize("use_gpu", [True, False])
    @pytest.mark.usefixtures("mock_timestamped_unique_name")
    def test_register_tf_model(self, mock_model_upload, mock_serialize_model, use_gpu):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )
        vertex_model = vertexai.preview.register(_TF_MODEL, use_gpu=use_gpu)

        expected_display_name = (
            f"vertex-ai-registered-tensorflow-model-{_TEST_UNIQUE_NAME}"
        )
        expected_uri = f"{_TEST_BUCKET}/{expected_display_name}/saved_model"
        expected_container_uri = (
            aiplatform.helpers.get_prebuilt_prediction_container_uri(
                framework="tensorflow",
                framework_version="2.11",
                accelerator="gpu" if use_gpu else "cpu",
            )
        )

        assert vertex_model.uri == _TEST_MODEL_GCS_URI
        mock_model_upload.assert_called_once_with(
            display_name=expected_display_name,
            artifact_uri=expected_uri,
            serving_container_image_uri=expected_container_uri,
            labels={"registered_by_vertex_ai": "true"},
            sync=True,
        )
        assert 2 == mock_serialize_model.call_count
        mock_serialize_model.assert_has_calls(
            calls=[
                mock.call(
                    _TF_MODEL,
                    f"{expected_uri}",
                    save_format="tf",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.parametrize("use_gpu", [True, False])
    @pytest.mark.usefixtures("mock_timestamped_unique_name")
    def test_register_pytorch_model(
        self, mock_model_upload, mock_serialize_model, use_gpu
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )
        vertex_model = vertexai.preview.register(_PYTORCH_MODEL, use_gpu=use_gpu)

        expected_display_name = (
            f"vertex-ai-registered-pytorch-model-{_TEST_UNIQUE_NAME}"
        )
        expected_uri = f"{_TEST_BUCKET}/{expected_display_name}"
        expected_container_uri = (
            aiplatform.helpers.get_prebuilt_prediction_container_uri(
                framework="pytorch",
                framework_version="1.12",
                accelerator="gpu" if use_gpu else "cpu",
            )
        )

        assert vertex_model.uri == _TEST_MODEL_GCS_URI
        mock_model_upload.assert_called_once_with(
            display_name=expected_display_name,
            artifact_uri=expected_uri,
            serving_container_image_uri=expected_container_uri,
            labels={"registered_by_vertex_ai": "true"},
            sync=True,
        )

        assert 2 == mock_serialize_model.call_count
        mock_serialize_model.assert_has_calls(
            calls=[
                mock.call(
                    _PYTORCH_MODEL,
                    f"{expected_uri}/model.mar",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("mock_get_vertex_model")
    def test_local_model_from_pretrained_succeed(self, mock_deserialize_model):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        local_model = vertexai.preview.from_pretrained(model_name=_MODEL_RESOURCE_NAME)
        assert local_model == _SKLEARN_MODEL
        assert 2 == mock_deserialize_model.call_count
        mock_deserialize_model.assert_has_calls(
            calls=[
                mock.call(
                    f"{_TEST_MODEL_GCS_URI}/model.pkl",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures(
        "mock_get_vertex_model_invalid",
    )
    def test_local_model_from_pretrained_fail(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        with pytest.raises(ValueError):
            vertexai.preview.from_pretrained(model_name=_MODEL_RESOURCE_NAME)

    @pytest.mark.usefixtures(
        "mock_get_vertex_model",
        "mock_get_custom_job_succeeded",
    )
    def test_custom_job_from_pretrained_succeed(self, mock_deserialize_model):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        local_model = vertexai.preview.from_pretrained(
            custom_job_name=_TEST_CUSTOM_JOB_RESOURCE_NAME
        )
        assert local_model == _SKLEARN_MODEL
        assert 2 == mock_deserialize_model.call_count

        mock_deserialize_model.assert_has_calls(
            calls=[
                mock.call(
                    f"{_TEST_BASE_OUTPUT_DIR}/output/output_estimator",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures(
        "mock_get_vertex_model",
        "mock_get_custom_job_pending",
        "mock_cloud_logging_list_entries",
    )
    def test_custom_job_from_pretrained_logs_and_blocks_until_complete_on_pending_job(
        self, mock_deserialize_model
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        local_model = vertexai.preview.from_pretrained(
            custom_job_name=_TEST_CUSTOM_JOB_RESOURCE_NAME
        )
        assert local_model == _SKLEARN_MODEL
        assert 2 == mock_deserialize_model.call_count

        mock_deserialize_model.assert_has_calls(
            calls=[
                mock.call(
                    f"{_TEST_BASE_OUTPUT_DIR}/output/output_estimator",
                ),
            ],
            any_order=True,
        )

    @pytest.mark.usefixtures("mock_get_vertex_model", "mock_get_custom_job_failed")
    def test_custom_job_from_pretrained_fails_on_errored_job(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        with pytest.raises(ValueError) as err_msg:
            vertexai.preview.from_pretrained(
                custom_job_name=_TEST_CUSTOM_JOB_RESOURCE_NAME
            )
            assert "did not complete" in err_msg

    @pytest.mark.usefixtures(
        "mock_get_publisher_model",
    )
    def test_from_pretrained_with_preview_foundation_model(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        foundation_model = vertexai.preview.from_pretrained(
            foundation_model_name="text-bison@001"
        )
        assert isinstance(foundation_model, language_models._PreviewTextGenerationModel)

    @pytest.mark.usefixtures(
        "get_model_with_tuned_version_label_mock",
    )
    def test_from_pretrained_with_preview_tuned_mg_model(
        self, mock_get_publisher_model
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        tuned_model = vertexai.preview.from_pretrained(model_name=_TEST_ID)
        assert mock_get_publisher_model.call_count == 1
        assert isinstance(tuned_model, language_models._PreviewTextGenerationModel)
        assert tuned_model._endpoint_name == _TEST_TUNED_MODEL_ENDPOINT_NAME
        assert tuned_model._model_id == "publishers/google/models/text-bison@001"

    @pytest.mark.usefixtures(
        "mock_get_publisher_model",
        "get_model_with_invalid_tuned_version_labels",
    )
    def test_from_pretrained_raises_on_invalid_model_registry_model(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        with pytest.raises(ValueError):
            vertexai.preview.from_pretrained(model_name=_TEST_ID)

    def test_from_pretrained_raises_with_more_than_one_arg(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        with pytest.raises(ValueError):
            vertexai.preview.from_pretrained(
                model_name=_TEST_ID, foundation_model_name="text-bison@001"
            )

    def test_from_pretrained_raises_with_no_args_passed(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET,
        )

        with pytest.raises(ValueError):
            vertexai.preview.from_pretrained()
