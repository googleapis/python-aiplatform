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
from unittest.mock import patch
import pytest

from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata.schema import base_artifact
from google.cloud.aiplatform.metadata.schema import base_execution
from google.cloud.aiplatform.metadata.schema import google_artifact_schema
from google.cloud.aiplatform.metadata.schema import system_artifact_schema
from google.cloud.aiplatform.metadata.schema import system_execution_schema
from google.cloud.aiplatform.metadata.schema import utils
from google.cloud.aiplatform_v1 import MetadataServiceClient
from google.cloud.aiplatform_v1 import Artifact as GapicArtifact
from google.cloud.aiplatform_v1 import Execution as GapicExecution


# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_METADATA_STORE = "test-metadata-store"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/{_TEST_METADATA_STORE}"

# resource attributes
_TEST_ARTIFACT_STATE = gca_artifact.Artifact.State.STATE_UNSPECIFIED
_TEST_EXECUTION_STATE = gca_execution.Execution.State.STATE_UNSPECIFIED
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

# artifact
_TEST_ARTIFACT_ID = "test-artifact-id"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"

# execution
_TEST_EXECUTION_ID = "test-execution-id"
_TEST_EXECUTION_NAME = f"{_TEST_PARENT}/executions/{_TEST_EXECUTION_ID}"


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


@pytest.fixture
def create_execution_mock():
    with patch.object(
        MetadataServiceClient, "create_execution"
    ) as create_execution_mock:
        create_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_DISPLAY_NAME,
            schema_title=_TEST_SCHEMA_TITLE,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_METADATA,
            state=GapicExecution.State.RUNNING,
        )
        yield create_execution_mock


class TestMetadataBaseArtifactSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_base_class_overrides_default_schema_title(self):
        artifact = base_artifact.BaseArtifactSchema(schema_title=_TEST_SCHEMA_TITLE)
        assert artifact.schema_title == _TEST_SCHEMA_TITLE

    def test_base_class_overrides_default_state(self):
        artifact = base_artifact.BaseArtifactSchema(state=_TEST_ARTIFACT_STATE)
        assert artifact.state == _TEST_ARTIFACT_STATE

    def test_base_class_default_schema_title(self):
        artifact = base_artifact.BaseArtifactSchema()
        assert artifact.schema_title == "system.Artifact"

    def test_base_class_default_state(self):
        artifact = base_artifact.BaseArtifactSchema()
        assert artifact.state == gca_artifact.Artifact.State.LIVE

    def test_base_class_overrides_default_version(self):
        artifact = base_artifact.BaseArtifactSchema(schema_version=_TEST_SCHEMA_VERSION)
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_base_class_init_remaining_parameters_are_assigned_correctly(self):
        artifact = base_artifact.BaseArtifactSchema(
            resource_id=_TEST_ARTIFACT_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.resource_id == _TEST_ARTIFACT_ID
        assert artifact.schema_title == _TEST_SCHEMA_TITLE
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA

    @pytest.mark.usefixtures("create_artifact_mock")
    def test_create_is_called_with_default_parameters(self, create_artifact_mock):
        aiplatform.init(project=_TEST_PROJECT)
        artifact = base_artifact.BaseArtifactSchema(
            schema_title=_TEST_SCHEMA_TITLE,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
            state=_TEST_ARTIFACT_STATE,
        )
        artifact.create(metadata_store_id=_TEST_METADATA_STORE)
        create_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT, artifact=mock.ANY, artifact_id=None
        )
        _, _, kwargs = create_artifact_mock.mock_calls[0]
        assert kwargs["artifact"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["artifact"].uri == _TEST_URI
        assert kwargs["artifact"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["artifact"].description == _TEST_DESCRIPTION
        assert kwargs["artifact"].metadata == _TEST_UPDATED_METADATA
        assert kwargs["artifact"].state == _TEST_ARTIFACT_STATE


class TestMetadataBaseExecutionSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_base_class_overrides_default_schema_title(self):
        execution = base_execution.BaseExecutionSchema(schema_title=_TEST_SCHEMA_TITLE)
        assert execution.schema_title == _TEST_SCHEMA_TITLE

    def test_base_class_overrides_default_state(self):
        execution = base_execution.BaseExecutionSchema(state=_TEST_EXECUTION_STATE)
        assert execution.state == _TEST_EXECUTION_STATE

    def test_base_class_default_schema_title(self):
        execution = base_execution.BaseExecutionSchema()
        assert execution.schema_title == "system.ContainerExecution"

    def test_base_class_default_state(self):
        execution = base_execution.BaseExecutionSchema()
        assert execution.state == gca_execution.Execution.State.RUNNING

    def test_base_class_overrides_default_version(self):
        execution = base_execution.BaseExecutionSchema(
            schema_version=_TEST_SCHEMA_VERSION
        )
        assert execution.schema_version == _TEST_SCHEMA_VERSION

    def test_base_class_init_remaining_parameters_are_assigned_correctly(self):
        execution = base_execution.BaseExecutionSchema(
            resource_id=_TEST_EXECUTION_ID,
            schema_title=_TEST_SCHEMA_TITLE,
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert execution.resource_id == _TEST_EXECUTION_ID
        assert execution.schema_title == _TEST_SCHEMA_TITLE
        assert execution.state == _TEST_EXECUTION_STATE
        assert execution.display_name == _TEST_DISPLAY_NAME
        assert execution.description == _TEST_DESCRIPTION
        assert execution.metadata == _TEST_UPDATED_METADATA

    @pytest.mark.usefixtures("create_execution_mock")
    def test_create_method_calls_gapic_library_with_correct_parameters(
        self, create_execution_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        execution = base_execution.BaseExecutionSchema(
            schema_title=_TEST_SCHEMA_TITLE,
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution.create(metadata_store_id=_TEST_METADATA_STORE)
        create_execution_mock.assert_called_once_with(
            parent=_TEST_PARENT, execution=mock.ANY, execution_id=None
        )
        _, _, kwargs = create_execution_mock.mock_calls[0]
        assert kwargs["execution"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["execution"].state == _TEST_EXECUTION_STATE
        assert kwargs["execution"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["execution"].description == _TEST_DESCRIPTION
        assert kwargs["execution"].metadata == _TEST_UPDATED_METADATA

    @pytest.mark.usefixtures("create_execution_mock")
    def test_start_execution_method_calls_gapic_library_with_correct_parameters(
        self, create_execution_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        execution = base_execution.BaseExecutionSchema(
            schema_title=_TEST_SCHEMA_TITLE,
            state=_TEST_EXECUTION_STATE,
            display_name=_TEST_DISPLAY_NAME,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        execution.start_execution(metadata_store_id=_TEST_METADATA_STORE)
        create_execution_mock.assert_called_once_with(
            parent=_TEST_PARENT, execution=mock.ANY, execution_id=None
        )
        _, _, kwargs = create_execution_mock.mock_calls[0]
        assert kwargs["execution"].schema_title == _TEST_SCHEMA_TITLE
        assert kwargs["execution"].state == _TEST_EXECUTION_STATE
        assert kwargs["execution"].display_name == _TEST_DISPLAY_NAME
        assert kwargs["execution"].description == _TEST_DESCRIPTION
        assert kwargs["execution"].metadata == _TEST_UPDATED_METADATA


class TestMetadataGoogleArtifactSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_vertex_dataset_schema_title_is_set_correctly(self):
        artifact = google_artifact_schema.VertexDataset()
        assert artifact.schema_title == "google.VertexDataset"

    def test_vertex_dataset_constructor_parameters_are_set_correctly(self):
        artifact = google_artifact_schema.VertexDataset(
            dataset_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.resource_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_vertex_model_schema_title_is_set_correctly(self):
        artifact = google_artifact_schema.VertexModel()
        assert artifact.schema_title == "google.VertexModel"

    def test_vertex_model_constructor_parameters_are_set_correctly(self):
        artifact = google_artifact_schema.VertexModel(
            vertex_model_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.resource_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION

    def test_vertex_endpoint_schema_title_is_set_correctly(self):
        artifact = google_artifact_schema.VertexEndpoint()
        assert artifact.schema_title == "google.VertexEndpoint"

    def test_vertex_endpoint_constructor_parameters_are_set_correctly(self):
        artifact = google_artifact_schema.VertexEndpoint(
            vertex_endpoint_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.resource_id == _TEST_ARTIFACT_ID
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
        artifact = google_artifact_schema.UnmanagedContainerModel(
            predict_schema_ta=predict_schema_ta,
            container_spec=container_spec,
        )
        assert artifact.schema_title == "google.UnmanagedContainerModel"

    def test_unmanaged_container_model_constructor_parameters_are_set_correctly(self):
        predict_schema_ta = utils.PredictSchemata(
            instance_schema_uri="instance_uri",
            prediction_schema_uri="prediction_uri",
            parameters_schema_uri="parameters_uri",
        )

        container_spec = utils.ContainerSpec(
            image_uri="gcr.io/test_container_image_uri"
        )

        artifact = google_artifact_schema.UnmanagedContainerModel(
            predict_schema_ta=predict_schema_ta,
            container_spec=container_spec,
            unmanaged_container_model_id=_TEST_ARTIFACT_ID,
            uri=_TEST_URI,
            display_name=_TEST_DISPLAY_NAME,
            schema_version=_TEST_SCHEMA_VERSION,
            description=_TEST_DESCRIPTION,
            metadata=_TEST_UPDATED_METADATA,
        )
        assert artifact.resource_id == _TEST_ARTIFACT_ID
        assert artifact.uri == _TEST_URI
        assert artifact.display_name == _TEST_DISPLAY_NAME
        assert artifact.description == _TEST_DESCRIPTION
        assert artifact.metadata == _TEST_UPDATED_METADATA
        assert artifact.schema_version == _TEST_SCHEMA_VERSION


class TestMetadataSystemArtifactSchema:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    def test_system_dataset_schema_title_is_set_correctly(self):
        artifact = system_artifact_schema.Dataset()
        assert artifact.schema_title == "system.Dataset"

    def test_system_dataset_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Dataset(
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
        artifact = system_artifact_schema.Model()
        assert artifact.schema_title == "system.Model"

    def test_system_model_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Model(
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
        artifact = system_artifact_schema.Metrics()
        assert artifact.schema_title == "system.Metrics"

    def test_system_metrics_values_default_to_none(self):
        artifact = system_artifact_schema.Metrics()
        assert artifact.metadata == {}

    def test_system_metrics_constructor_parameters_are_set_correctly(self):
        artifact = system_artifact_schema.Metrics(
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


class TestMetadataSystemSchemaExecution:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    # Test system.Execution Schemas
    def test_system_container_execution_schema_title_is_set_correctly(self):
        execution = system_execution_schema.ContainerExecution()
        assert execution.schema_title == "system.ContainerExecution"

    def test_system_custom_job_execution_schema_title_is_set_correctly(self):
        execution = system_execution_schema.CustomJobExecution()
        assert execution.schema_title == "system.CustomJobExecution"

    def test_system_run_execution_schema_title_is_set_correctly(self):
        execution = system_execution_schema.Run()
        assert execution.schema_title == "system.Run"


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
