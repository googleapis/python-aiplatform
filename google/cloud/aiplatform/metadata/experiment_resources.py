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

from typing import Dict, List, NamedTuple, Optional, Set, Union

from google.api_core import exceptions
from google.auth import credentials as auth_credentials
from google.protobuf import timestamp_pb2

from google.cloud.aiplatform.compat.types import artifact as gca_artifact
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform.compat.types import tensorboard_time_series as gca_tensorboard_time_series
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
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform.tensorboard import tensorboard_resource
from google.cloud.aiplatform import utils


class VertexResourceWithMetadata(NamedTuple):
    resource: base.VertexAiResourceNoun
    metadata: _Artifact

def _format_experiment_run_name(experiment_name: str, run_name: str) -> str:
    return f'{experiment_name}-{run_name}'

def _execution_to_column_named_metadata(
        metadata_type: str, metadata: Dict, filter_prefix: Optional[str] = None
    ) -> Dict[str, Union[int, float, str]]:
    """Returns a dict of the Execution/Artifact metadata with column names.

    Args:
      metadata_type: The type of this execution properties (param, metric).
      metadata: Either an Execution or Artifact metadata field.
      filter_prefix:
        Remove this prefix from the key of metadata field. Mainly used for removing
        "input:" from PipelineJob parameter keys

    Returns:
      Dict of custom properties with keys mapped to column names
    """
    column_key_to_value = {}
    for key, value in metadata.items():
        if filter_prefix and key.startswith(filter_prefix):
            key = key[len(filter_prefix):]
        column_key_to_value[".".join([metadata_type, key])] = value

    return column_key_to_value

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

    def get_dataframe(self) -> "pd.DataFrame":  # noqa: F821
        """Get metrics and parameters all Runs in this Experiment as Dataframe.

        Returns:
            pd.Dataframe: Pandas Dataframe of Experiment Runs.

        Raises:
            ImportError: If pandas is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is not installed and is required to get dataframe as the return format. "
                'Please install the SDK using "pip install python-aiplatform[metadata]"'
            )

        experiment_runs = ExperimentRun.list(experiment=self)
        df = pd.DataFrame(row for run in experiment_runs for row in run._get_pandas_row_dicts())

        column_name_sort_map = {
            'experiment_name': -1,
            'run_name': 1,
            'pipeline_run_name': 2,
            'execution_name': 3,
            'output_name': 4
        }

        def column_sort_key(key: str) -> int:
            """Helper method to reorder columns."""
            order = column_name_sort_map.get(key)
            if order:
                return order
            elif key.startswith('param'):
                return 5
            elif key.startswith('metric'):
                return 6
            else:
                return 7

        columns = df.columns
        columns = sorted(columns, key=column_sort_key) 
        df = df.reindex(columns, axis=1)

        return df


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
    def _get_experiment(
        experiment: Union[Experiment, str, None] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials]=None) -> Experiment:

        #TODO(retrieve Experiment instance when tracked in global config)
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
    def list(
        cls,
        experiment: Union[Experiment, str, None]=None,
        project: Optional[str]=None,
        location: Optional[str]=None,
        credentials: Optional[auth_credentials.Credentials]=None) -> List['ExperimentRun']:

        experiment = cls._get_experiment(experiment=experiment, project=project, location=location, credentials=credentials)

        metadata_args = dict(
            project=experiment._metadata_context.project,
            location=experiment._metadata_context.location,
            credentials=experiment._metadata_context.credentials
        )

        filter_str = f'schema_title="{constants.SYSTEM_EXPERIMENT_RUN}" AND parent_contexts:"{experiment.resource_name}"'
        run_contexts = _Context.list(filter=filter_str, **metadata_args)

        in_context_query = " OR ".join([f'in_context("{c.resource_name}")' for c in run_contexts])
        filter_str = f'schema_title="{constants.SYSTEM_RUN}" AND ({in_context_query})'

        run_executions = _Execution.list(filter=filter_str, **metadata_args)
        experiment_run_execution_map = {e.name: e for e in run_executions}

        experiment_runs = []

        for context in  run_contexts:
            this_experiment_run = cls.__new__(cls)
            this_experiment_run._experiment = experiment
            this_experiment_run._run_name = context.display_name
            this_experiment_run._metadata_context = context
            this_experiment_run._metadata_execution = experiment_run_execution_map[context.name]
            this_experiment_run._metadata_metric = _Artifact(resource_name=context.name+'-metrics', **metadata_args)

            tb_run_artifact = _Artifact(resource_name=context.name+'-tbrun', **metadata_args)
            if tb_run_artifact:
                tb_run = tensorboard_resource.TensorboardRun(tb_run_artifact.metadata['resourceName'], **metadata_args)
                this_experiment_run._backing_tensorboard_run = VertexResourceWithMetadata(metadata=tb_run_artifact, resource=tb_run)
            else:
                this_experiment_run._backing_tensorboard_run = None
            experiment_runs.append(this_experiment_run)

        return experiment_runs

    def _get_pandas_row_dicts(self) -> List[Dict[str, Union[float, int, str]]]:

        run_dict = {
            "experiment_name": self._experiment.name,
            "run_name": self._run_name,
        }
        run_dict.update(_execution_to_column_named_metadata("param", self._metadata_execution.metadata))
        run_dict.update(_execution_to_column_named_metadata("metric", self._metadata_metric.metadata))
        run_dict.update(self._get_latest_time_series_metric_columns())

        rows = [run_dict]

        rows += self._get_logged_pipeline_runs_as_pandas_row_dicts()

        return rows


    def _get_logged_pipeline_runs(self) -> List[_Context]:
        """Returns Pipeline Run contexts logged to this Experiment Run."""

        service_request_args = dict(
            project=self._metadata_context.project,
            location=self._metadata_context.location,
            credentials=self._metadata_context.credentials
        )

        filter_str = f'schema_title="{constants.SYSTEM_PIPELINE_RUN}" AND parent_contexts:"{self._metadata_context.resource_name}"'

        return _Context.list(filter=filter_str, **service_request_args)

    def _get_logged_pipeline_runs_as_pandas_row_dicts(self) -> List[Dict[str, Union[float, int, str]]]:
        """Returns Pipeline Runs as Pandas row dictionaries."""

        pipeline_run_contexts = self._get_logged_pipeline_runs()

        row_dicts = []

        for pipeline_run_context in pipeline_run_contexts:
            pipeline_run_dict = {
                "experiment_name": self._experiment.name,
                "pipeline_run_name": pipeline_run_context.name,
                "run_name": self._run_name
            }

            context_lineage_subgraph = pipeline_run_context.query_lineage_subgraph()
            artifact_map = {artifact.name:artifact for artifact in context_lineage_subgraph.artifacts}
            output_execution_map = defaultdict(list)
            for event in context_lineage_subgraph.events:
                if event.type_ == gca_event.Event.Type.OUTPUT:
                    output_execution_map[event.execution].append(event.artifact)

            execution_dicts = []
            for execution in context_lineage_subgraph.executions:
                if execution.schema_title == constants.SYSTEM_RUN:
                    pipeline_params = _execution_to_column_named_metadata(
                        metadata_type="param", metadata=execution.metadata, filter_prefix=constants.PIPELINE_PARAM_PREFIX) 
                else:
                    execution_dict = pipeline_run_dict.copy()
                    execution_dict['execution_name'] = execution.display_name
                    artifact_dicts = []
                    for artifact_name in output_execution_map[execution.name]:
                        artifact = artifact_map.get(artifact_name)
                        if artifact and artifact.schema_title == constants.SYSTEM_METRICS and artifact.metadata:
                            execution_with_metric_dict = execution_dict.copy()
                            execution_with_metric_dict['output_name'] = artifact.display_name
                            execution_with_metric_dict.update(_execution_to_column_named_metadata("metric", artifact.metadata))
                            artifact_dicts.append(execution_with_metric_dict)
                    
                    # if this is the only artifact then we only need one row for this execution
                    # otherwise we need to create a row per metric artifact
                    # ignore all executions that didn't create metrics to remove noise
                    if len(artifact_dicts) == 1:
                        execution_dict.update(artifact_dicts[0])
                        execution_dicts.append(execution_dict)
                    elif len(artifact_dicts) >= 1:
                        execution_dicts.extend(artifact_dicts)

            # if there is only one execution/artifact combo then only need one row for this pipeline
            # otherwise we need one row be execution/artifact combo
            if len(execution_dicts) == 1:
                pipeline_run_dict.update(execution_dicts[0])
                pipeline_run_dict.update(pipeline_params)
                row_dicts.append(pipeline_run_dict)
            elif len(execution_dicts) > 1:
                # pipeline params on their own row when there are multiple output metrics
                pipeline_run_row = pipeline_run_dict.copy()
                pipeline_run_row.update(pipeline_params)
                row_dicts.append(pipeline_run_row)
                for execution_dict in execution_dicts:
                    execution_dict.update(pipeline_run_row)
                    row_dicts.append(execution_dict)

        return row_dicts


    def _get_latest_time_series_metric_columns(self) -> Dict[str, Union[float, int]]:
        if self._backing_tensorboard_run:
            time_series_metrics = self._backing_tensorboard_run.resource.read_time_series_data()

            return {
                f'time_series_metric.{display_name}': data.values[-1].scalar.value
                for display_name, data in time_series_metrics.items()
                if data.value_type == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
            }
        return {}

    def _log_pipeline_job(self, pipeline_job: pipeline_jobs.PipelineJob):
        """Associated this PipelineJob's Context to the current ExperimentRun Context as a child context.

        Args:
            pipeline_job (pipeline_jobs.PipelineJob):
                Required. The PipelineJob to associated.
        """
        
        try:
            pipeline_job.wait_for_resource_creation()
        except Exception as e:
            raise RuntimeError("Could not log PipelineJob to Experiment Run") from e

        resource_name_fields = pipeline_jobs.PipelineJob._parse_resource_name(pipeline_job.resource_name)

        pipeline_job_context = None
        pipeline_job_context_getter = functools.partial(
            _Context._get,
            resource_name=resource_name_fields['pipeline_job'],
            project=resource_name_fields['project'],
            location=resource_name_fields['location']
            )

        # PipelineJob context is created asynchronously so we need to poll until it exists.
        while not pipeline_job_context:
            pipeline_job_context = pipeline_job_context_getter()

            if not pipeline_job_context:
                if pipeline_job.done():
                    pipeline_job_context = pipeline_job_context_getter()
                    if not pipeline_job_context:
                        if pipeline_job.has_failed():
                            raise RuntimeError(f"Cannot associate PipelineJob to Experiment Run: {pipeline_job.gca_resource.error}")
                        else:
                            raise RuntimeError(f"Cannot associate PipelineJob to Experiment Run because PipelineJob context could not be found.")
                else:
                    time.sleep(1)

        self._metadata_context.add_context_children([pipeline_job_context])        


    def log(self, *, pipeline_job: Optional[pipeline_jobs.PipelineJob]=None):
        if pipeline_job:
            self._log_pipeline_job(pipeline_job=pipeline_job)


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
        """Registers TensorboardRun Metadata schema is not populated."""
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

    #TODO(get latest time series step)
    def _get_latest_time_series_step(self, time_series_keys):
        pass

    def log_time_series_metrics(
        self,
        metrics: Dict[str, Union[float, int]],
        step: Optional[int]=None,
        wall_time: Optional[timestamp_pb2.Timestamp]=None):
        """Logs time series metrics to backing TensorboardRun."""

        if not self._backing_tensorboard_run:
            raise RuntimeError("Please set this experiment run with backing tensorboard resource.")

        self._soft_create_time_series(metric_keys=set(metrics.keys()))

        self._backing_tensorboard_run.resource.write_tensorboard_scalar_data(
                time_series_data=metrics,
                step=step,
                wall_time=wall_time
            )

    def _soft_create_time_series(self, metric_keys: Set[str]):
        """Creates TensorboardTimeSeries for the metric keys if one currently does not exist."""

        if any(key not in self._backing_tensorboard_run.resource._time_series_display_name_to_id_mapping for key in metric_keys):
            self._backing_tensorboard_run.resource._sync_time_series_display_name_to_id_mapping()

        for key in metric_keys:
            if key not in self._backing_tensorboard_run.resource._time_series_display_name_to_id_mapping:
                self._backing_tensorboard_run.resource.create_tensorboard_time_series(display_name=key)







