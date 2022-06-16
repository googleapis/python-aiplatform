# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from google.cloud.aiplatform.metadata.types import google_types
from google.cloud.aiplatform.metadata.types import system_types
from google.cloud.aiplatform.metadata.types import base_artifact
import json


PARAMS = {"sdk-param-test-1": 0.1, "sdk-param-test-2": 0.2}

METRICS = {"sdk-metric-test-1": 0.8, "sdk-metric-test-2": 100}


@pytest.mark.usefixtures("tear_down_resources")
class TestMetadata(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-e2e-test"

    def test_experiment_logging(self, shared_state):

        # Truncating the name because of resource id constraints from the service
        experiment_name = self._make_display_name("experiment")[:56]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            experiment=experiment_name,
        )

        shared_state["resources"] = [aiplatform.metadata.metadata_service._experiment]

        # Truncating the name because of resource id constraints from the service
        run_name = self._make_display_name("run")[:56]

        aiplatform.start_run(run_name)

        shared_state["resources"].extend(
            [
                aiplatform.metadata.metadata_service._run,
                aiplatform.metadata.metadata_service._metrics,
            ]
        )

        aiplatform.log_params(PARAMS)

        aiplatform.log_metrics(METRICS)

        df = aiplatform.get_experiment_df()

        true_df_dict = {f"metric.{key}": value for key, value in METRICS.items()}
        for key, value in PARAMS.items():
            true_df_dict[f"param.{key}"] = value

        true_df_dict["experiment_name"] = experiment_name
        true_df_dict["run_name"] = run_name

        assert true_df_dict == df.to_dict("records")[0]

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
        assert artifact.resource_name.startswith(
            f"projects/{e2e_base._PROJECT}/locations/{e2e_base._LOCATION}/metadataStores/default/artifacts/"
        )

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

        artifact = system_types.Dataset(
            display_name=artifact_display_name,
            uri=artifact_uri,
            metadata=artifact_metadata,
            description=artifact_description,
        ).create()

        assert artifact.display_name == artifact_display_name
        assert json.dumps(artifact.metadata) == json.dumps(artifact_metadata)
        assert artifact.schema_title == "system.Dataset"
        assert artifact.description == artifact_description
        assert artifact.resource_name.startswith(
            f"projects/{e2e_base._PROJECT}/locations/{e2e_base._LOCATION}/metadataStores/default/artifacts/"
        )

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

        artifact = google_types.VertexDataset(
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
        assert artifact.resource_name == dataset_name
