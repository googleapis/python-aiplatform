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
from google.cloud.aiplatform.metadata.schema.google import (
    artifact_schema as google_artifact_schema,
)
from google.cloud.aiplatform.metadata.schema.system import (
    artifact_schema as system_artifact_schema,
)
from google.cloud.aiplatform.metadata.schema.system import (
    execution_schema as system_execution_schema,
)
from tests.system.aiplatform import e2e_base


@pytest.mark.usefixtures("tear_down_resources")
class TestMetadataSchema(e2e_base.TestEndToEnd):

    _temp_prefix = "tmpvrtxmlmdsdk-e2e"

    def setup_class(cls):
        # Truncating the name because of resource id constraints from the service
        cls.artifact_display_name = cls._make_display_name("base-artifact")[:30]
        cls.artifact_id = cls._make_display_name("base-artifact-id")[:30]
        cls.artifact_uri = cls._make_display_name("base-uri")
        cls.artifact_metadata = {"test_property": "test_value"}
        cls.artifact_description = cls._make_display_name("base-description")
        cls.execution_display_name = cls._make_display_name("base-execution")[:30]
        cls.execution_description = cls._make_display_name("base-description")

    def test_artifact_creation_using_schema_base_class(self):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        artifact = base_artifact.BaseArtifactSchema(
            display_name=self.artifact_display_name,
            uri=self.artifact_uri,
            metadata=self.artifact_metadata,
            description=self.artifact_description,
        ).create()

        assert artifact.display_name == self.artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(self.artifact_metadata)
        assert artifact.schema_title == "system.Artifact"
        assert artifact.description == self.artifact_description
        assert "/metadataStores/default/artifacts/" in artifact.resource_name

    def test_system_dataset_artifact_create(self):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        artifact = system_artifact_schema.Dataset(
            display_name=self.artifact_display_name,
            uri=self.artifact_uri,
            metadata=self.artifact_metadata,
            description=self.artifact_description,
        ).create()

        assert artifact.display_name == self.artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(self.artifact_metadata)
        assert artifact.schema_title == "system.Dataset"
        assert artifact.description == self.artifact_description
        assert "/metadataStores/default/artifacts/" in artifact.resource_name

    def test_google_dataset_artifact_create(self):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        artifact = google_artifact_schema.VertexDataset(
            dataset_name=self.artifact_id,
            display_name=self.artifact_display_name,
            uri=self.artifact_uri,
            metadata=self.artifact_metadata,
            description=self.artifact_description,
        ).create()
        expected_metadata = self.artifact_metadata

        assert artifact.display_name == self.artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(expected_metadata)
        assert artifact.schema_title == "google.VertexDataset"
        assert artifact.description == self.artifact_description
        assert "/metadataStores/default/artifacts/" in artifact.resource_name

    def test_execution_create_using_schema_base_class(self):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        execution = base_execution.BaseExecutionSchema(
            display_name=self.execution_display_name,
            description=self.execution_description,
        ).create()

        assert execution.display_name == self.execution_display_name
        assert execution.schema_title == "system.ContainerExecution"
        assert execution.description == self.execution_description
        assert "/metadataStores/default/executions/" in execution.resource_name

    def test_execution_create_using_system_schema_class(self):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        execution = system_execution_schema.CustomJobExecution(
            display_name=self.execution_display_name,
            description=self.execution_description,
        ).create()

        assert execution.display_name == self.execution_display_name
        assert execution.schema_title == "system.CustomJobExecution"
        assert execution.description == self.execution_description
        assert "/metadataStores/default/executions/" in execution.resource_name

    def test_execution_start_execution_using_system_schema_class(self):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        execution = system_execution_schema.ContainerExecution(
            display_name=self.execution_display_name,
            description=self.execution_description,
        ).start_execution()

        assert execution.display_name == self.execution_display_name
        assert execution.schema_title == "system.ContainerExecution"
        assert execution.description == self.execution_description
        assert "/metadataStores/default/executions/" in execution.resource_name
