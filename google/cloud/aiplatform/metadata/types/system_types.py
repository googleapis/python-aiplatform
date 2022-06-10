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
from typing import Optional, Dict
from google.cloud.aiplatform.metadata import artifact


class Dataset(artifact.BaseArtifactType):
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
    ):
        """Args:
        dataset_name (str):
            The name of the Dataset resource, in a form of
            projects/{project}/locations/{location}/datasets/{datasets_name}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.datasets/get
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = dataset_name
        super(Dataset, self).__init__(
            schema_title=Dataset.SCHEMA_TITLE,
            resource_name=dataset_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )


class Experiment(artifact.BaseArtifactType):
    """An artifact representing a system Dataset."""

    SCHEMA_TITLE = "system.Experiment"

    def __init__(
        self,
        tensorboard_link: Optional[str] = None,
        experiment_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ):
        """Args:
        tensorboard_link (str):
            Optional. A link to a Tensorboard.
        experiment_name (str):
            Optional. The name of the experiment resource, in a form of
            projects/{project}/locations/{location}/tensorboards/{tensorboard}/experiments/{experiment}. For
            more details, see
            https://cloud.google.com/vertex-ai/docs/reference/rest/v1/projects.locations.tensorboards.experiments/get
        display_name (str):
            Optional. The user-defined name of the Artifact.
        schema_version (str):
            Optional. schema_version specifies the version used by the Artifact.
            If not set, defaults to use the latest version.
        description (str):
            Optional. Describes the purpose of the Artifact to be created.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Artifact.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = experiment_name

        if tensorboard_link:
            extended_metadata["tensorboard_link"] = tensorboard_link

        super(Dataset, self).__init__(
            schema_title=Experiment.SCHEMA_TITLE,
            resource_name=experiment_name,
            uri=uri,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
        )
