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

import pytest

from google.cloud import aiplatform
from google.cloud.aiplatform.metadata.schema import base_artifact
from google.cloud.aiplatform.metadata.schema import base_execution
from google.cloud.aiplatform.metadata.schema import google_artifact_schema
from google.cloud.aiplatform.metadata.schema import system_artifact_schema
from google.cloud.aiplatform.metadata.schema import system_execution_schema

from tests.system.aiplatform import e2e_base


@pytest.mark.usefixtures("tear_down_resources")
class TestMetadataSchema(e2e_base.TestEndToEnd):
    def test_artifact_creation_using_schema_base_class(self):

        # Truncating the name because of resource id constraints from the service
        artifact_display_name = self._make_display_name("base-artifact")[:30]
        artifact_uri = self._make_display_name("base-uri")
        artifact_metadata = {"test_property": "test_value"}
        artifact_description = self._make_display_name("base-description")

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        artifact = base_artifact.BaseArtifactSchema(
            display_name=artifact_display_name,
            uri=artifact_uri,
            metadata=artifact_metadata,
            description=artifact_description,
        ).create()

        assert artifact.display_name == artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(artifact_metadata)
        assert artifact.schema_title == "system.Artifact"
        assert artifact.description == artifact_description
        assert "/metadataStores/default/artifacts/" in artifact.resource_name

    def test_system_dataset_artifact_create(self):

        # Truncating the name because of resource id constraints from the service
        artifact_display_name = self._make_display_name("dataset-artifact")[:30]
        artifact_uri = self._make_display_name("dataset-uri")
        artifact_metadata = {"test_property": "test_value"}
        artifact_description = self._make_display_name("dataset-description")

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        artifact = system_artifact_schema.Dataset(
            display_name=artifact_display_name,
            uri=artifact_uri,
            metadata=artifact_metadata,
            description=artifact_description,
        ).create()

        assert artifact.display_name == artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(artifact_metadata)
        assert artifact.schema_title == "system.Dataset"
        assert artifact.description == artifact_description
        assert "/metadataStores/default/artifacts/" in artifact.resource_name

    def test_google_dataset_artifact_create(self):

        # Truncating the name because of resource id constraints from the service
        artifact_display_name = self._make_display_name("ds-artifact")[:30]
        artifact_uri = self._make_display_name("vertex-dataset-uri")
        artifact_metadata = {"test_property": "test_value"}
        artifact_description = self._make_display_name("vertex-dataset-description")
        dataset_name = f"projects/{e2e_base._PROJECT}/locations/{e2e_base._LOCATION}/datasets/{artifact_display_name}"

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        artifact = google_artifact_schema.VertexDataset(
            dataset_name=dataset_name,
            display_name=artifact_display_name,
            uri=artifact_uri,
            metadata=artifact_metadata,
            description=artifact_description,
        ).create()
        expected_metadata = artifact_metadata
        expected_metadata["resourceName"] = dataset_name

        assert artifact.display_name == artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(expected_metadata)
        assert artifact.schema_title == "google.VertexDataset"
        assert artifact.description == artifact_description
        assert "/metadataStores/default/artifacts/" in artifact.resource_name

    def test_execution_create_using_schema_base_class(self):

        # Truncating the name because of resource id constraints from the service
        execution_display_name = self._make_display_name("base-execution")[:30]
        execution_description = self._make_display_name("base-description")

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        execution = base_execution.BaseExecutionSchema(
            display_name=execution_display_name,
            description=execution_description,
        ).create()

        assert execution.display_name == execution_display_name
        assert execution.schema_title == "system.ContainerExecution"
        assert execution.description == execution_description
        assert "/metadataStores/default/executions/" in execution.resource_name

    def test_execution_create_using_system_schema_class(self):
        # Truncating the name because of resource id constraints from the service
        execution_display_name = self._make_display_name("base-execution")[:30]
        execution_description = self._make_display_name("base-description")

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        execution = system_execution_schema.CustomJobExecution(
            display_name=execution_display_name,
            description=execution_description,
        ).create()

        assert execution.display_name == execution_display_name
        assert execution.schema_title == "system.CustomJobExecution"
        assert execution.description == execution_description
        assert "/metadataStores/default/executions/" in execution.resource_name

    def test_execution_start_execution_using_system_schema_class(self):
        # Truncating the name because of resource id constraints from the service
        execution_display_name = self._make_display_name("base-execution")[:30]
        execution_description = self._make_display_name("base-description")

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        execution = system_execution_schema.ContainerExecution(
            display_name=execution_display_name,
            description=execution_description,
        ).start_execution()

        assert execution.display_name == execution_display_name
        assert execution.schema_title == "system.ContainerExecution"
        assert execution.description == execution_description
        assert "/metadataStores/default/executions/" in execution.resource_name
