# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

import json
from importlib import reload
from unittest import mock
from unittest.mock import patch, call

import pytest
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata.types import base
from google.cloud.aiplatform.metadata.types import google_types
from google.cloud.aiplatform.metadata.types import system_types
from google.cloud.aiplatform.metadata.types import utils

from google.cloud.aiplatform_v1 import MetadataServiceClient
from google.cloud.aiplatform_v1 import Artifact as GapicArtifact

# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METADATA_STORE = "test-metadata-store"
_TEST_ALT_LOCATION = "europe-west4"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/{_TEST_METADATA_STORE}"

# resource attributes
_TEST_URI = "test-uri"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_SCHEMA_TITLE = "test.Example"
_TEST_SCHEMA_VERSION = "0.0.1"
_TEST_DESCRIPTION = "test description"
_TEST_METADATA = {"test-param1": 1, "test-param2": "test-value", "test-param3": True}
_TEST_UPDATED_METADATA = {
    "test-param1": 2,
    "test-param2": "test-value-1",
    "test-param3": False,
}

# context
_TEST_CONTEXT_ID = "test-context-id"
_TEST_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_CONTEXT_ID}"

# artifact
_TEST_ARTIFACT_ID = "test-artifact-id"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"


@pytest.fixture
def create_artifact_mock():
    with patch.object(MetadataServiceClient, "create_artifact") as create_artifact_mock:
        create_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            state=GapicArtifact.State.STATE_UNSPECIFIED,
        )
        yield create_artifact_mock


class TestMetadataBaseSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_base_class_overrides_default_schema_title(self):
        artifact = base.BaseArtifactSchema(schema_title=_TEST_SCHEMA_TITLE)
        assert artifact.schema_title == _TEST_SCHEMA_TITLE

    def test_base_class_overrides_resouce_id_from_resouce_name(self):
        artifact = base.BaseArtifactSchema(resource_name=_TEST_ARTIFACT_NAME)
        assert artifact.resource_id == _TEST_ARTIFACT_ID

    def test_base_class_overrides_default_version(self):
        artifact = base.BaseArtifactSchema(schema_version=_TEST_SCHEMA_VERSION)
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_base_class_init_remaining_parameters_are_assigned_correctly(self):
        artifact = base.BaseArtifactSchema(
            schema_title=_TEST_SCHEMA_TITLE,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.schema_title == _TEST_SCHEMA_TITLE
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA

    @pytest.mark.usefixtures("create_artifact_mock")
    def test_create_is_called_with_default_parameters(self, create_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT)
        base_artifact = base.BaseArtifactSchema(
            schema_title=_TEST_SCHEMA_TITLE,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        base_artifact.create(metadata_store_id=_TEST_METADATA_STORE)
        create_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT, artifact=mock.ANY, artifact_id=None
        )
        _, _, kwargs = create_artifact_mock.mock_calls[0]
        assert kwargs['artifact'].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs['artifact'].uri == _TEST_URI
        assert kwargs['artifact'].display_name == _TEST_DISPLAY_NAME
        assert kwargs['artifact'].description == _TEST_DESCRIPTION
        assert kwargs['artifact'].metadata == _TEST_UPDATED_METADATA

class TestMetadataGoogleTypes:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_vertex_dataset_schema_title_is_set_correctly(self):
        artifact = google_types.VertexDataset()
        assert artifact.schema_title == "google.VertexDataset"

    def test_vertex_dataset_resouce_name_is_set_in_metadata(self):
        artifact = google_types.VertexDataset(dataset_name=_TEST_ARTIFACT_NAME)
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_vertex_dataset_constructor_parameters_are_set_correctly(self):
        artifact = google_types.VertexDataset(
            dataset_name=_TEST_ARTIFACT_NAME,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_vertex_model_schema_title_is_set_correctly(self):
        artifact = google_types.VertexModel()
        assert artifact.schema_title == "google.VertexModel"

    def test_vertex_model_resouce_name_is_set_in_metadata(self):
        artifact = google_types.VertexModel(vertex_model_name=_TEST_ARTIFACT_NAME)
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_vertex_model_constructor_parameters_are_set_correctly(self):
        artifact = google_types.VertexModel(
            vertex_model_name=_TEST_ARTIFACT_NAME,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_vertex_endpoint_schema_title_is_set_correctly(self):
        artifact = google_types.VertexEndpoint()
        assert artifact.schema_title == "google.VertexEndpoint"

    def test_vertex_endpoint_resouce_name_is_set_in_metadata(self):
        artifact = google_types.VertexEndpoint(vertex_endpoint_name=_TEST_ARTIFACT_NAME)
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_vertex_endpoint_constructor_parameters_are_set_correctly(self):
        artifact = google_types.VertexEndpoint(
            vertex_endpoint_name=_TEST_ARTIFACT_NAME,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_unmanaged_container_model_title_is_set_correctly(self):
        predict_schema_ta = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/test_container_image_uri"
        )
        artifact = google_types.UnmanagedContainerModel(
            predict_schema_ta=predict_schema_ta,
            container_spec=container_spec,
        )
        assert artifact.schema_title == "google.UnmanagedContainerModel"

    def test_unmanaged_container_model_resouce_name_is_set_in_metadata(self):
        predict_schema_ta = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/test_container_image_uri"
        )
        artifact = google_types.UnmanagedContainerModel(
            predict_schema_ta=predict_schema_ta,
            container_spec=container_spec,
            unmanaged_container_model_name=_TEST_ARTIFACT_NAME,
        )
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_unmanaged_container_model_constructor_parameters_are_set_correctly(self):
        predict_schema_ta = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/test_container_image_uri"
        )

        artifact = google_types.UnmanagedContainerModel(
            predict_schema_ta=predict_schema_ta,
            container_spec=container_spec,
            unmanaged_container_model_name=_TEST_ARTIFACT_NAME,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION


class TestMetadataSystemTypes:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_system_dataset_schema_title_is_set_correctly(self):
        artifact = system_types.Dataset()
        assert artifact.schema_title == "system.Dataset"

    def test_system_dataset_resouce_name_is_set_in_metadata(self):
        artifact = system_types.Dataset(dataset_name=_TEST_ARTIFACT_NAME)
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_system_dataset_constructor_parameters_are_set_correctly(self):
        artifact = system_types.Dataset(
            dataset_name=_TEST_ARTIFACT_NAME,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_system_model_schema_title_is_set_correctly(self):
        artifact = system_types.Model()
        assert artifact.schema_title == "system.Model"

    def test_system_model_resouce_name_is_set_in_metadata(self):
        artifact = system_types.Model(model_name=_TEST_ARTIFACT_NAME)
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_system_model_constructor_parameters_are_set_correctly(self):
        artifact = system_types.Model(
            model_name=_TEST_ARTIFACT_NAME,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_system_metrics_schema_title_is_set_correctly(self):
        artifact = system_types.Metrics()
        assert artifact.schema_title == "system.Metrics"

    def test_system_metrics_resouce_name_is_set_in_metadata(self):
        artifact = system_types.Metrics(metrics_name=_TEST_ARTIFACT_NAME)
        assert artifact.metadata["resourceName"] == _TEST_ARTIFACT_NAME

    def test_system_metrics_constructor_parameters_are_set_correctly(self):
        artifact = system_types.Metrics(
            metrics_name=_TEST_ARTIFACT_NAME,
            accuracy=0.1,
            precision=0.2,
            recall=0.3,
            f1score=0.4,
            mean_absolute_error=0.5,
            mean_squared_error=0.6,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.schema_version == _TEST_SCHEMA_VERSION
        assert artifact.metadata["accuracy"] == 0.1
        assert artifact.metadata["precision"] == 0.2
        assert artifact.metadata["recall"] == 0.3
        assert artifact.metadata["f1score"] == 0.4
        assert artifact.metadata["mean_absolute_error"] == 0.5
        assert artifact.metadata["mean_squared_error"] == 0.6


class TestMetadataUtils:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_predict_schemata_to_dict_method_returns_correct_schema(self):
        predict_schema_ta = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )
        expected_results = {
            "instanceSchemaUri": "instance_uri",
            "parametersSchemaUri": "parameters_uri",
            "predictionSchemaUri": "prediction_uri",
        }

        assert json.dumps(predict_schema_ta.to_dict()) == json.dumps(expected_results)

    def test_container_spec_to_dict_method_returns_correct_schema(self):
        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/some_container_image_uri",
            command=["test_command"],
            args=["test_args"],
            env=[{"env_var_name": "env_var_value"}],
            ports=[1],
            predict_route="test_prediction_rout",
            health_route="test_health_rout",
        )

        expected_results = {
            "imageUri": "gcr.io/some_container_image_uri",
            "command": ["test_command"],
            "args": ["test_args"],
            "env": [{"env_var_name": "env_var_value"}],
            "ports": [1],
            "predictRoute": "test_prediction_rout",
            "healthRoute": "test_health_rout",
        }

        assert json.dumps(container_spec.to_dict()) == json.dumps(expected_results)

    def test_container_spec_to_dict_method_returns_correct_schema(self):
        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/some_container_image_uri",
            command=["test_command"],
            args=["test_args"],
            env=[{"env_var_name": "env_var_value"}],
            ports=[1],
            predict_route="test_prediction_rout",
            health_route="test_health_rout",
        )

        expected_results = {
            "imageUri": "gcr.io/some_container_image_uri",
            "command": ["test_command"],
            "args": ["test_args"],
            "env": [{"env_var_name": "env_var_value"}],
            "ports": [1],
            "predictRoute": "test_prediction_rout",
            "healthRoute": "test_health_rout",
        }

        assert json.dumps(container_spec.to_dict()) == json.dumps(expected_results) 