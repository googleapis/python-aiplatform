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

from typing import Optional, Dict

from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.metadata.schema import base_artifact


class Model(base_artifact.BaseArtifactSchema):
    """Schemaless Artifact to store Markdown file."""

    SCHEMA_TITLE = "system.Model"

    def __init__(
        self,
        model_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        model_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        uri (str):
            Optional. The uniform resource identifier of the artifact file. May be empty if there is no actual
            artifact file.
        display_name (str):
            Optional. The user-defined name of the base.
        schema_version (str):
            Optional. schema_version specifies the version used by the base.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = model_name
        super(Model, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=model_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class Dataset(base_artifact.BaseArtifactSchema):
    """An artifact representing a system Dataset."""

    SCHEMA_TITLE = "system.Dataset"

    def __init__(
        self,
        dataset_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        dataset_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        uri (str):
            Optional. The uniform resource identifier of the artifact file. May be empty if there is no actual
            artifact file.
        display_name (str):
            Optional. The user-defined name of the base.
        schema_version (str):
            Optional. schema_version specifies the version used by the base.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = dataset_name
        super(Dataset, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=dataset_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )


class Metrics(base_artifact.BaseArtifactSchema):
    """Artifact schema for scalar metrics."""

    SCHEMA_TITLE = "system.Metrics"

    def __init__(
        self,
        metrics_name: Optional[str] = None,
        accuracy: Optional[float] = 0,
        precision: Optional[float] = 0,
        recall: Optional[float] = 0,
        f1score: Optional[float] = 0,
        mean_absolute_error: Optional[float] = 0,
        mean_squared_error: Optional[float] = 0,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        state: gca_artifact.Artifact.State = gca_artifact.Artifact.State.LIVE,
    ):
        """Args:
        metrics_name (str):
            Optional. The resource name of the Artifact following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/artifacts/<resource_id>.
        accuracy (float):
            Optional. Defaults to zero.
        precision (float):
            Optional. Defaults to zero.
        recall (float):
            Optional. Defaults to zero.
        f1score (float):
            Optional. Defaults to zero.
        mean_absolute_error (float):
            Optional. Defaults to zero.
        mean_squared_error (float):
            Optional. Defaults to zero.
        uri (str):
            Optional. The uniform resource identifier of the artifact file. May be empty if there is no actual
            artifact file.
        display_name (str):
            Optional. The user-defined name of the base.
        schema_version (str):
            Optional. schema_version specifies the version used by the base.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        state (google.cloud.gapic.types.Artifact.State):
            Optional. The state of this Artifact. This is a
            property of the Artifact, and does not imply or
            capture any ongoing process. This property is
            managed by clients (such as Vertex AI
            Pipelines), and the system does not prescribe or
            check the validity of state transitions.
        """
        extended_metadata = metadata or {}
        extended_metadata["accuracy"] = accuracy
        extended_metadata["precision"] = precision
        extended_metadata["recall"] = recall
        extended_metadata["f1score"] = f1score
        extended_metadata["mean_absolute_error"] = mean_absolute_error
        extended_metadata["mean_squared_error"] = mean_squared_error
        extended_metadata["resourceName"] = metrics_name

        super(Metrics, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=metrics_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            state=state,
        )
