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
from typing import Optional

from google.auth import credentials as auth_credentials


from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import _Execution
from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore
from google.cloud.tensorboard import tensorboard_resource

_VERTEX_EXPERIMENT_TRACKING_LABEL = 'vertex_experiment_tracking'

_TensorboardRunArtifact = gca_artifact.Artifact(
	schema_title='google.VertexTensorboardRun',
	schema_version=0.0.1,
	metadata={_VERTEX_EXPERIMENT_TRACKING_LABEL: True},
)

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

		self._backing_tensorboard_run: Optional[tensorboard_resource.TensorboardRun] = self._lookup_tensorboard_run_artifact()

	def _get_experiment(self, experiment: Union[Experiment, str, None] = None) -> Experiment:
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
		if artifact.schema_title != _TensorboardRunArtifact:
			return False
		if not artifact.metadata.get(_VERTEX_EXPERIMENT_TRACKING_LABEL):
			return False
		
		run_parts = tensorboard_resource.TensorboardRun.parse_resource_name(artifact.uri)

		if (run_parts['experiment'], run_parts['run']) == (self._experiment.name, self._run_name):
			return True

		return False

	def _lookup_tensorboard_run_artifact(self) -> Optonal[TensorboardRun]:
		metadata_artifacts = self._metadata_execution.query_input_output_artifacts()

		for artifact in metadata_artifacts:
			if self._is_backing_tensorboard_run_artifact(artifact):
				return tensorboard_resource.TensorboardRun(artifact.uri)

	@classmethod
	def create(
		cls,
		run_name: str,
		experiment: Union[Experiment, str, None] = None,
		tensorboard_resource: Union[tensorboard_resource.TensorboardRun, str, None] = None,
		project: Optional[str] =  None,
		location: Optional[str] = None,
		credentials: Optional[auth_credentials.Credentials] = None) -> "ExperimentRun":

		experiment = self._get_experiment(experiment)

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

        metadata_execution = _Execution.create(
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

        return cls(
        		run_name=run_name,
        		experiment=experiment,
        		project=project,
        		location=location,
        		credentials=credentials
        	)

    def assign_backing_tensorboard(self, tensorboard_resource: Union[tensorboard_resource.Tensorboard, str]):
    	"""Assigns tensorboard as backing tensorboard for to support timeseries metrics logging."""

    	backing_tensorboard = self._lookup_tensorboard_run_artifact():
    	if backing_tensorboard:
    		raise ValueError(f'Experiment run {self._run_name} already associated to tensorboard resource {backing_tensorboard.resource_name}')

    	if isinstance(tensorboard_resource, str):
    		tensorboard_resource = tensorboard_resource.Tensorboard(tensorboard_resource)

    	tensorboard_experiment = tensorboard_resource.TensorboardExperiment.create(
    			tensorboard_experiment_id=self._experiment.name,
    			tensorboard_resource=tensorboard_resource.resource_name,
    			credentials=tensorboard_resource.credentials  			
    		)

    	tensorboard_run = tensorboard_resource.TensorboardRun.create(
    			tensorboard_run_id=self._run_name,
    			tensorboard_experiment_name=tensorboard_experiment.resource_name,
    			credentials=tensorboard_resource.credentials
    		)



