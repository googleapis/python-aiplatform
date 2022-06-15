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
from typing import Optional, Dict, List
from google.cloud.aiplatform.metadata import execution
from google.cloud.aiplatform.metadata.types import base
from google.cloud.aiplatform.metadata.types import utils
from itertools import zip_longest


class Model(base.BaseArtifactSchema):
    """Schemaless Artifact Type to store Markdown file."""

    SCHEMA_TITLE = "system.Model"

    def __init__(
        self,
        model_name: Optional[str] = None,
        uri: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        **kwargs,
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
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
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
            kwargs=kwargs,
        )


class Dataset(base.BaseArtifactSchema):
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
        **kwargs,
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
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
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
            kwargs=kwargs,
        )


class Metrics(base.BaseArtifactSchema):
    """Artifact type for scalar metrics."""

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
        **kwargs,
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
            Optional. Contains the metadata information that will be stored in the base.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Artifact base method for backward compatibility.
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
            kwargs=kwargs,
        )


class ContainerExecution(base.BaseExecutionSchema):
    """Execution type for a container execution."""

    SCHEMA_TITLE = "system.ContainerExecution"

    def __init__(
        self,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        execution_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Args:
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        execution_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = execution_name
        super(ContainerExecution, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=execution_name,
            state=state,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            kwargs=kwargs,
        )


class ImporterExecution(base.BaseExecutionSchema):
    """Execution type for a importer execution."""

    SCHEMA_TITLE = "system.ImporterExecution"

    def __init__(
        self,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        execution_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Args:
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        execution_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = execution_name
        super(ImporterExecution, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=execution_name,
            state=state,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            kwargs=kwargs,
        )


class ResolverExecution(base.BaseExecutionSchema):
    """Execution type for a resolver execution."""

    SCHEMA_TITLE = "system.ResolverExecution"

    def __init__(
        self,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        execution_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Args:
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        execution_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = execution_name
        super(ResolverExecution, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=execution_name,
            state=state,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            kwargs=kwargs,
        )


class DagExecution(base.BaseExecutionSchema):
    """Execution type for a dag execution."""

    SCHEMA_TITLE = "system.DagExecution"

    def __init__(
        self,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        execution_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Args:
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        execution_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = execution_name
        super(DagExecution, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=execution_name,
            state=state,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            kwargs=kwargs,
        )


class CustomJobExecution(base.BaseExecutionSchema):
    """Execution type for a custom job execution."""

    SCHEMA_TITLE = "system.CustomJobExecution"

    def __init__(
        self,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        execution_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Args:
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        execution_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = execution_name
        super(CustomJobExecution, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=execution_name,
            state=state,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            kwargs=kwargs,
        )


class RunExecution(base.BaseExecutionSchema):
    """Execution type for root run execution."""

    SCHEMA_TITLE = "system.Run"

    def __init__(
        self,
        state: execution.Execution.State = execution.Execution.State.RUNNING,
        execution_name: Optional[str] = None,
        display_name: Optional[str] = None,
        schema_version: Optional[str] = None,
        metadata: Optional[Dict] = None,
        description: Optional[str] = None,
        **kwargs,
    ):
        """Args:
        state (gca_execution.Execution.State.RUNNING):
            Optional. State of this Execution. Defaults to RUNNING.
        execution_name (str):
            Optional. The resource name of the Execution following the format as follows.
            This is globally unique in a metadataStore:
            projects/123/locations/us-central1/metadataStores/<metadata_store_id>/executions/<resource_id>.
        display_name (str):
            Optional. The user-defined name of the Execution.
        schema_version (str):
            Optional. schema_version specifies the version used by the Execution.
            If not set, defaults to use the latest version.
        metadata (Dict):
            Optional. Contains the metadata information that will be stored in the Execution.
        description (str):
            Optional. Describes the purpose of the Execution to be created.
        **kwargs:
            Optional. Additional Args that will be passed directly to the Execution base method for backward compatibility.
        """
        extended_metadata = metadata or {}
        extended_metadata["resourceName"] = execution_name
        super(RunExecution, self).__init__(
            schema_title=self.SCHEMA_TITLE,
            resource_name=execution_name,
            state=state,
            display_name=display_name,
            schema_version=schema_version,
            description=description,
            metadata=extended_metadata,
            kwargs=kwargs,
        )
