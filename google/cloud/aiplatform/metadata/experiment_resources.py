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

from typing import Dict, NamedTuple, Optional, Set, Union

from google.api_core import exceptions
from google.auth import credentials as auth_credentials
from google.protobuf import timestamp_pb2

from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import _Execution
from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore
from google.cloud.aiplatform.metadata.schema import _MetadataSchema
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform.tensorboard import tensorboard_resource
from google.cloud.aiplatform import utils


class VertexResourceWithMetadata(NamedTuple):
    resource: base.VertexAiResourceNoun
    metadata: _Artifact

def _format_experiment_run_name(experiment_name: str, run_name: str) -> str:
    return f'{experiment_name}-{run_name}'


"""Backing TensorboardRun Artifact
schema_title: google.VertexTensorboardRun
schema_version: 0.0.1
labels: {vertex_experiment_tracking: True}
uri: projects/.../locations/.../tensorboards/.../experiment/{experiment}/runs/{run}
"""

class Experiment():

    def __init__(
            self,
            experiment_name: Optional[str] = None,
            project: Optional[str] =  None,
            location: Optional[str] = None,
            credentials: Optional[auth_credentials.Credentials] = None
        ):

        metadata_args = dict(
            resource_name=experiment_name,
            project=project,
            location=location,
            credentials=credentials
        )

        self._metadata_context = _Context(**metadata_args)

    @classmethod
    def create(
        cls,
        experiment_name:str,
        description: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None) -> 'Experiment':

        context = _Context._create(
            resource_id=experiment_name,
            display_name=experiment_name,
            description=description,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=metadata._get_experiment_schema_version(),
            metadata=constants.EXPERIMENT_METADATA,
            project=project,
            location=location,
            credentials=credentials
        )

        return cls(experiment_name=context.resource_name, credentials=credentials)

    @property
    def name(self):
        return self._metadata_context.name

    @property
    def resource_name(self):
        return self._metadata_context.resource_name


class ExperimentRun:

    def __init__(
        self,
        run_name: str,
        experiment: Union[Experiment, str, None] = None,
        project: Optional[str] =  None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None):

        self._experiment = self._get_experiment(experiment=experiment)
        self._run_name = run_name

        run_id = _format_experiment_run_name(
            experiment_name=self._experiment.name,
            run_name=run_name)

        metadata_args = dict(
            resource_name=run_id,
            project=project,
            location=location,
            credentials=credentials
        )

        self._metadata_context = _Context(**metadata_args)
        self._metadata_execution = _Execution(**metadata_args)
        metadata_args['resource_name']+='-metrics'
        self._metadata_metric = _Artifact(**metadata_args)

        self._backing_tensorboard_run: Optional[VertexResourceWithMetadata] = self._lookup_tensorboard_run_artifact()

    @staticmethod
    def _get_experiment(experiment: Union[Experiment, str, None] = None) -> Experiment:
        experiment = experiment or initializer.global_config.experiment_name

        if not experiment:
            raise ValueError('experiment must be provided or experiment should be set using aiplatform.init')

        if not isinstance(experiment, Experiment):
            experiment = Experiment(
                experiment_name = experiment,
                project=project,
                location=location,
                credentials=credentials)
        return experiment

    def _is_backing_tensorboard_run_artifact(self, artifact: _Artifact) -> bool:
        if artifact.schema_title != metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title:
            return False
        if not artifact.metadata.get(metadata_utils._VERTEX_EXPERIMENT_TRACKING_LABEL):
            return False
        
        run_parts = tensorboard_resource.TensorboardRun._parse_resource_name(artifact.metadata['resourceName'])

        if (run_parts['experiment'], run_parts['run']) == (self._experiment.name, self._run_name):
            return True

        return False

    def _lookup_tensorboard_run_artifact(self) -> Optional[VertexResourceWithMetadata]:
        metadata_artifacts = self._metadata_execution.query_input_and_output_artifacts()

        for artifact in metadata_artifacts:
            if self._is_backing_tensorboard_run_artifact(artifact):
                return VertexResourceWithMetadata(
                    resource=tensorboard_resource.TensorboardRun(artifact.metadata['resourceName']),
                    metadata=_Artifact)

    @classmethod
    def create(
        cls,
        run_name: str,
        experiment: Union[Experiment, str, None] = None,
        tensorboard_resource: Union[tensorboard_resource.TensorboardRun, str, None] = None,
        project: Optional[str] =  None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None) -> "ExperimentRun":

        experiment = cls._get_experiment(experiment)

        run_id = _format_experiment_run_name(
            experiment_name=experiment.name,
            run_name=run_name)

        metadata_context = _Context._create(
            resource_id=run_id,
            display_name=run_name,
            schema_title=constants.SYSTEM_EXPERIMENT_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT_RUN],
            metadata=constants.EXPERIMENT_METADATA,
            project=project,
            location=location,
            credentials=credentials
        )

        experiment._metadata_context.add_context_children([metadata_context])

        metadata_execution = _Execution._create(
            resource_id=run_id,
            display_name=run_name,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
            project=project,
            location=location,
            credentials=credentials
        )

        metadata_context.add_artifacts_and_executions(execution_resource_names=[metadata_execution.resource_name])

        metrics_artifact_id = f'{run_id}-metrics'
        metrics_artifact = _Artifact._create(
            resource_id=metrics_artifact_id,
            display_name=metrics_artifact_id,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
            project=project,
            location=location,
            credentials=credentials
        )

        metadata_execution.add_artifact(artifact_resource_name=metrics_artifact.resource_name, input=False)

        experiment_run = cls(
            run_name=run_name,
            experiment=experiment,
            project=project,
            location=location,
            credentials=credentials
        ) 

        # TODO: default to experiment tensorboard resource if tensorboard resource not given
        if tensorboard_resource:
            experiment_run.assign_backing_tensorboard(tensorboard_resource=tensorboard_resource)

        return experiment_run

    def assign_backing_tensorboard(self, tensorboard: Union[tensorboard_resource.Tensorboard, str]):
        """Assigns tensorboard as backing tensorboard to support timeseries metrics logging."""

        backing_tensorboard = self._lookup_tensorboard_run_artifact()
        if backing_tensorboard:
            # TODO: consider warning if tensorboard_resource matches backing tensorboard uri 
            raise ValueError(
                f'Experiment run {self._run_name} already associated to tensorboard resource {backing_tensorboard.resource_name}')

        if isinstance(tensorboard, str):
            tensorboard = tensorboard_resource.Tensorboard(tensorboard)

        # TODO: get or create TB experiment
        tensorboard_experiment = tensorboard_resource.TensorboardExperiment.create(
                tensorboard_experiment_id=self._experiment.name,
                tensorboard_name=tensorboard.resource_name,
                credentials=tensorboard.credentials            
            )

        # TODO: get or create TB run
        tensorboard_run = tensorboard_resource.TensorboardRun.create(
                tensorboard_run_id=self._run_name,
                tensorboard_experiment_name=tensorboard_experiment.resource_name,
                credentials=tensorboard.credentials
            )

        gcp_resource_url = metadata_utils.make_gcp_resource_url(tensorboard_run)

        self._soft_register_tensorboard_run_schema()

        metadata_resource_id = f'{self._metadata_context.name}-tbrun'

        tensorboard_run_metadata_artifact = _Artifact._create(
            resource_id=metadata_resource_id,
            uri=gcp_resource_url,
            metadata={
                'resourceName':tensorboard_run.resource_name,
                metadata_utils._VERTEX_EXPERIMENT_TRACKING_LABEL: True,
            },
            schema_title=metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title,
            schema_version=metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_version,
        )

        self._metadata_execution.add_artifact(
            artifact_resource_name=tensorboard_run_metadata_artifact.resource_name,
            input=False)

        self._backing_tensorboard_run = VertexResourceWithMetadata(
                resource=tensorboard_run,
                metadata = tensorboard_run_metadata_artifact
            )

    def _soft_register_tensorboard_run_schema(self):
        resource_name_parts = self._metadata_context._parse_resource_name(self._metadata_context.resource_name)
        resource_name_parts.pop('context')
        parent = _MetadataStore._format_resource_name(**resource_name_parts)
        schema_id, schema = metadata_utils.get_tensorboard_board_run_metadata_schema()
        resource_name_parts['metadata_schema'] = schema_id 
        metadata_schema_name = _MetadataSchema._format_resource_name(**resource_name_parts)

        try:
            _MetadataSchema(metadata_schema_name)
        except exceptions.NotFound as e:
            _MetadataSchema.create(
                metadata_schema = schema,
                metadata_schema_id = schema_id,
                metadata_store_name= parent
            )

    def _get_latest_time_series_step(self, time_series_keys):
        pass

    def log_time_series_metrics(
        self,
        metrics: Dict[str, Union[float, int]],
        step: Optional[int]=None,
        wall_time: Optional[timestamp_pb2.Timestamp]=None):

        if not self._backing_tensorboard_run:
            raise RuntimeError("Please set this experiment run with backing tensorboard resource.")

        if not step:
            step = self._get_latest_time_series_step(time_series_keys=metrics.keys())

        self._soft_create_time_series(metric_keys=set(metrics.keys()))

        self._backing_tensorboard_run.resource.write_tensorboard_scalar_data(
                time_series_data=metrics,
                step=step,
                wall_time=wall_time
            )

    def _soft_create_time_series(self, metric_keys: Set[str]):

        current_time_series_keys = self._get_available_time_series_keys()

        for key in metric_keys:
            if key not in current_time_series_keys:
                tensorboard_resource.TensorboardTimeSeries.create(
                    tensorboard_time_series_id=key,
                    tensorboard_run_name=self._backing_tensorboard_run.resource.resource_name,
                    credentials=self._backing_tensorboard_run.resource.credentials)

    def _get_available_time_series_keys(self) -> Set[str]:
        tb_time_series_resources = tensorboard_resource.TensorboardTimeSeries.list(
            tensorboard_run_name=self._backing_tensorboard_run.resource.resource_name,
            credentials=self._backing_tensorboard_run.resource.credentials)

        return set(ts.display_name for ts in tb_time_series_resources)







