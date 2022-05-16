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
import collections
import concurrent.futures
import functools
from typing import Callable, Dict, List, Optional, Set, Union, Any

from google.api_core import exceptions
from google.auth import credentials as auth_credentials
from google.protobuf import timestamp_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series as gca_tensorboard_time_series,
)
from google.cloud.aiplatform import initializer, gapic
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import experiment_resources
from google.cloud.aiplatform.metadata.artifact import Artifact, VertexResourceArtifactResolver
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import Execution
from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore
from google.cloud.aiplatform.metadata import resource
from google.cloud.aiplatform.metadata.schema import _MetadataSchema
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform.tensorboard import tensorboard_resource


_LOGGER = base.Logger(__name__)

def _format_experiment_run_name(experiment_name: str, run_name: str) -> str:
    return f"{experiment_name}-{run_name}"

def _v1_not_supported(method: Callable) -> Callable:
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if isinstance(self._metadata_node, Execution):
            raise NotImplementedError(
                f'{self._run_name} is an Execution run created during Vertex Experiment Preview and does not support'
                f' {method.__name__}. Please create a new Experiment run to use this method.')
        else:
            return method(self, *args, **kwargs)
    return wrapper


class ExperimentRun(experiment_resources.ExperimentLoggable,
                    experiment_loggable_schemas=(
                        experiment_resources.ExperimentLoggableSchema(
                            title=constants.SYSTEM_EXPERIMENT_RUN,
                            type=_Context),
                        # backwards compatibility with Preview Experiment runs
                        experiment_resources.ExperimentLoggableSchema(
                            title=constants.SYSTEM_RUN,
                            type=Execution
                        )
                    )):
    def __init__(
        self,
        run_name: str,
        experiment: Union[experiment_resources.Experiment, str],
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):

        self._experiment = self._get_experiment(experiment=experiment)
        self._run_name = run_name

        run_id = _format_experiment_run_name(
            experiment_name=self._experiment.name, run_name=run_name
        )

        metadata_args = dict(
            resource_name=run_id,
            project=project,
            location=location,
            credentials=credentials,
        )

        def _get_context():
            with experiment_resources._SetLoggerLevel(resource):
                # TODO: Add schema validation on these metadata nodes
                return _Context(**metadata_args)

        try:
            self._metadata_node = _get_context()
        except exceptions.NotFound as context_not_found:
            try:
                # backward compatibility
                self._v1_resolve_experiment_run(metadata_args)
            except exceptions.NotFound:
                raise context_not_found
        else:
            self._backing_tensorboard_run: Optional[
                experiment_resources.VertexResourceWithMetadata
            ] = self._lookup_tensorboard_run_artifact()

            # initially set to None. Will initially update from resource then track locally.
            self._largest_step: Optional[int] = None

    def _v1_resolve_experiment_run(self, metadata_args: Dict[str, Any]):
        def _get_execution():
            with experiment_resources._SetLoggerLevel(resource):
                # TODO: Add schema validation on these metadata nodes
                return Execution(**metadata_args)
        self._metadata_node = _get_execution()
        self._metadata_metric_artifact = self._v1_get_metric_artifact()

    def _v1_get_metric_artifact(self) -> _Artifact:
        metadata_args = dict(
            resource_name=self._v1_format_artifact_name(self._metadata_node.name),
            project=self.project,
            location=self.location,
            credentials=self.credentials
        )

        with experiment_resources._SetLoggerLevel(resource):
            return _Artifact(**metadata_args)

    @staticmethod
    def _v1_format_artifact_name(run_id: str) -> str:
        return f'{run_id}-metrics'

    def _get_context(self) -> _Context:
        return self._metadata_node

    @property
    def resource_id(self) -> str:
        return self._metadata_node.name

    @property
    def name(self) -> str:
        return self._run_name

    @property
    def resource_name(self) -> str:
        return self._metadata_node.resource_name

    @property
    def project(self) -> str:
        return self._metadata_node.project

    @property
    def location(self) -> str:
        return self._metadata_node.location

    @property
    def credentials(self) -> auth_credentials.Credentials:
        return self._metadata_node.credentials

    @property
    def state(self) -> gapic.Execution.State:
        if self._is_v1_experiment_run():
            return self._metadata_node.state
        else:
            return getattr(gapic.Execution.State, self._metadata_node.metadata[constants._STATE_KEY])

    @staticmethod
    def _get_experiment(
        experiment: Union[experiment_resources.Experiment, str, None] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> experiment_resources.Experiment:

        # TODO(retrieve Experiment instance when tracked in global config)
        experiment = experiment or initializer.global_config.experiment_name

        if not experiment:
            raise ValueError(
                "experiment must be provided or experiment should be set using aiplatform.init"
            )

        if not isinstance(experiment, experiment_resources.Experiment):
            experiment = experiment_resources.Experiment(
                experiment_name=experiment,
                project=project,
                location=location,
                credentials=credentials,
            )
        return experiment

    def _is_backing_tensorboard_run_artifact(self, artifact: _Artifact) -> bool:
        if not artifact.metadata.get(metadata_utils._VERTEX_EXPERIMENT_TRACKING_LABEL):
            return False

        if artifact.name != self._tensorboard_run_id(self._metadata_node.name):
            return False

        return True

    def _is_v1_experiment_run(self) -> bool:
        return isinstance(self._metadata_node, Execution)

    def update_state(self, state: gapic.Execution.State):
        if self._is_v1_experiment_run():
            self._metadata_node.update(state=state)
        else:
            self._metadata_node.update(metadata={constants._STATE_KEY:state.name})

    def _lookup_tensorboard_run_artifact(self) -> Optional[experiment_resources.VertexResourceWithMetadata]:
        with experiment_resources._SetLoggerLevel(resource):
            artifact = _Artifact._get(
                resource_name=self._tensorboard_run_id(self._metadata_node.name),
                project=self._metadata_node.project,
                location=self._metadata_node.location,
                credentials=self._metadata_node.credentials
            )

        if artifact and self._is_backing_tensorboard_run_artifact(artifact):
            return experiment_resources.VertexResourceWithMetadata(
                resource=tensorboard_resource.TensorboardRun(
                    artifact.metadata["resourceName"]
                ),
                metadata=artifact,
            )

    @classmethod
    def list(
        cls,
        experiment: Union[experiment_resources.Experiment, str, None] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["ExperimentRun"]:

        experiment = cls._get_experiment(
            experiment=experiment,
            project=project,
            location=location,
            credentials=credentials,
        )

        metadata_args = dict(
            project=experiment._metadata_context.project,
            location=experiment._metadata_context.location,
            credentials=experiment._metadata_context.credentials,
        )

        filter_str = metadata_utils.make_filter_string(
            schema_title=constants.SYSTEM_EXPERIMENT_RUN,
            parent_contexts=[experiment.resource_name])

        run_contexts = _Context.list(filter=filter_str, **metadata_args)

        filter_str = metadata_utils.make_filter_string(
            schema_title=constants.SYSTEM_RUN,
            in_context=[experiment.resource_name]
        )

        run_executions = Execution.list(filter=filter_str, **metadata_args)


        def _initialize_experiment_run(context: _Context) -> ExperimentRun:
            this_experiment_run = cls.__new__(cls)
            this_experiment_run._experiment = experiment
            this_experiment_run._run_name = context.display_name
            this_experiment_run._metadata_node = context

            with experiment_resources._SetLoggerLevel(resource):
                tb_run = this_experiment_run._lookup_tensorboard_run_artifact()
            if tb_run:
                this_experiment_run._backing_tensorboard_run = tb_run
            else:
                this_experiment_run._backing_tensorboard_run = None

            this_experiment_run._largest_step = None

            return this_experiment_run

        def _initialize_v1_experiment_run(execution: Execution) -> ExperimentRun:
            this_experiment_run = cls.__new__(cls)
            this_experiment_run._experiment = experiment
            this_experiment_run._run_name = execution.display_name
            this_experiment_run._metadata_node = execution
            this_experiment_run._metadata_metric_artifact = this_experiment_run._v1_get_metric_artifact()

            return this_experiment_run

        if run_contexts or run_executions:
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=max([len(run_contexts), len(run_executions)])
            ) as executor:
                submissions = [
                    executor.submit(_initialize_experiment_run, context)
                    for context in run_contexts
                ]
                experiment_runs = [submission.result() for submission in submissions]

                submissions = [
                    executor.submit(_initialize_v1_experiment_run, execution)
                    for execution in run_executions
                ]

                for submission in submissions:
                    experiment_runs.append(submission.result())

            return experiment_runs
        else:
            return []

    @classmethod
    def _query_experiment_row(cls, node: Union[_Context, Execution]) -> experiment_resources.ExperimentRow:
        this_experiment_run = cls.__new__(cls)
        this_experiment_run._metadata_node = node

        row = experiment_resources.ExperimentRow(
            experiment_run_type=node.schema_title,
            name=node.display_name,
        )

        if isinstance(node, _Context):
            this_experiment_run._backing_tensorboard_run = this_experiment_run._lookup_tensorboard_run_artifact()
            row.params = node.metadata[constants._PARAM_KEY]
            row.metrics = node.metadata[constants._METRIC_KEY]
            row.time_series_metrics = this_experiment_run._get_latest_time_series_metric_columns()
            row.state = node.metadata[constants._STATE_KEY]
        else:
            this_experiment_run._metadata_metric_artifact = this_experiment_run._v1_get_metric_artifact()
            row.params = node.metadata
            row.metrics = this_experiment_run._metadata_metric_artifact.metadata
            row.state = node.state.name
        return row

    def _get_logged_pipeline_runs(self) -> List[_Context]:
        """Returns Pipeline Run contexts logged to this Experiment Run."""

        service_request_args = dict(
            project=self._metadata_node.project,
            location=self._metadata_node.location,
            credentials=self._metadata_node.credentials,
        )

        filter_str = metadata_utils.make_filter_string(
            schema_title=constants.SYSTEM_PIPELINE_RUN,
            parent_contexts=[self._metadata_node.resource_name]
        )

        return _Context.list(filter=filter_str, **service_request_args)


    def _get_latest_time_series_metric_columns(self) -> Dict[str, Union[float, int]]:
        if self._backing_tensorboard_run:
            time_series_metrics = (
                self._backing_tensorboard_run.resource.read_time_series_data()
            )

            return {
                display_name: data.values[-1].scalar.value
                for display_name, data in time_series_metrics.items()
                if data.value_type
                == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
            }
        return {}

    def _log_pipeline_job(self, pipeline_job: pipeline_jobs.PipelineJob):
        """Associated this PipelineJob's Context to the current ExperimentRun Context as a child context.

        Args:
            pipeline_job (pipeline_jobs.PipelineJob):
                Required. The PipelineJob to associate.
        """

        pipeline_job_context = pipeline_job._get_context()
        self._metadata_node.add_context_children([pipeline_job_context])

    def _log_artifact(self, artifact: Artifact):
        self._metadata_execution._add_artifact(
            artifact_resource_names=[artifact.resource_name], input=False
        )

    def _consume_artifact(self, artifact: Artifact):
        self._metadata_execution._add_artifact(
            artifact_resource_names=[artifact.resource_name], input=True
        )

    @_v1_not_supported
    def log(
        self,
        *,
        pipeline_job: Optional[pipeline_jobs.PipelineJob] = None,
    ):
        if pipeline_job:
            self._log_pipeline_job(pipeline_job=pipeline_job)

    @classmethod
    def create(
        cls,
        run_name: str,
        experiment: Union[experiment_resources.Experiment, str, None] = None,
        tensorboard: Union[tensorboard_resource.Tensorboard, str, None] = None,
        state: gapic.Execution.State = gapic.Execution.State.RUNNING,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "ExperimentRun":

        experiment = cls._get_experiment(experiment)

        run_id = _format_experiment_run_name(
            experiment_name=experiment.name, run_name=run_name
        )

        def _create_context():
            with experiment_resources._SetLoggerLevel(resource):
                return _Context._create(
                    resource_id=run_id,
                    display_name=run_name,
                    schema_title=constants.SYSTEM_EXPERIMENT_RUN,
                    schema_version=constants.SCHEMA_VERSIONS[
                        constants.SYSTEM_EXPERIMENT_RUN
                    ],
                    metadata={
                        constants._PARAM_KEY:{},
                        constants._METRIC_KEY:{},
                        constants._STATE_KEY:state.name
                    },
                    project=project,
                    location=location,
                    credentials=credentials,
                )

        metadata_context = _create_context()

        if metadata_context is None:
            raise RuntimeError(
                f"Experiment Run with name {run_name} in {experiment.name} already exists."
            )

        experiment_run = cls.__new__(cls)
        experiment_run._experiment = experiment
        experiment_run._run_name = metadata_context.display_name
        experiment_run._metadata_node = metadata_context
        experiment_run._largest_step = None

        if tensorboard:
            cls._assign_backing_tensorboard(self=experiment_run, tensorboard=tensorboard)
        else:
            cls._assign_to_experiment_backing_tensorboard(self=experiment_run)

        experiment_run._associate_to_experiment(experiment)
        return experiment_run

    def _assign_to_experiment_backing_tensorboard(self):
        """Assigns parent Experiment backing tensorboard resource to this Experiment Run."""
        backing_tensorboard_resource = (
            self._experiment.get_backing_tensorboard_resource()
        )

        if backing_tensorboard_resource:
            self.assign_backing_tensorboard(tensorboard=backing_tensorboard_resource)

    def _format_tensorboard_experiment_display_name(self, experiment_name: str) -> str:
        return f'{experiment_name} Backing Tensorboard Experiment'

    def _assign_backing_tensorboard(
        self, tensorboard: Union[tensorboard_resource.Tensorboard, str]
    ):
        if isinstance(tensorboard, str):
            tensorboard = tensorboard_resource.Tensorboard(
                tensorboard,
                credentials=self._metadata_node.credentials)

        tensorboard_resource_name_parts = tensorboard._parse_resource_name(
            tensorboard.resource_name
        )
        tensorboard_experiment_resource_name = (
            tensorboard_resource.TensorboardExperiment._format_resource_name(
                experiment=self._experiment.name,
                **tensorboard_resource_name_parts
            )
        )
        try:
            tensorboard_experiment = tensorboard_resource.TensorboardExperiment(
                tensorboard_experiment_resource_name,
                credentials=tensorboard.credentials
            )
        except exceptions.NotFound:
            with experiment_resources._SetLoggerLevel(tensorboard_resource):
                tensorboard_experiment = (
                    tensorboard_resource.TensorboardExperiment.create(
                        tensorboard_experiment_id=self._experiment.name,
                        display_name=self._format_tensorboard_experiment_display_name(self._experiment.name),
                        tensorboard_name=tensorboard.resource_name,
                        credentials=tensorboard.credentials,
                    )
                )

        tensorboard_experiment_name_parts = tensorboard_experiment._parse_resource_name(
            tensorboard_experiment.resource_name
        )
        tensorboard_run_resource_name = (
            tensorboard_resource.TensorboardRun._format_resource_name(
                run=self._run_name, **tensorboard_experiment_name_parts
            )
        )
        try:
            tensorboard_run = tensorboard_resource.TensorboardRun(
                tensorboard_run_resource_name
            )
        except exceptions.NotFound:
            with experiment_resources._SetLoggerLevel(tensorboard_resource):
                tensorboard_run = tensorboard_resource.TensorboardRun.create(
                    tensorboard_run_id=self._run_name,
                    tensorboard_experiment_name=tensorboard_experiment.resource_name,
                    credentials=tensorboard.credentials,
                )

        gcp_resource_url = metadata_utils.make_gcp_resource_url(tensorboard_run)

        # TODO: remove tensorboard run schema as it should be seeded
        self._soft_register_tensorboard_run_schema()

        with experiment_resources._SetLoggerLevel(resource):
            tensorboard_run_metadata_artifact = _Artifact._create(
                uri=gcp_resource_url,
                resource_id=self._tensorboard_run_id(self._metadata_node.name),
                metadata={
                    "resourceName": tensorboard_run.resource_name,
                    metadata_utils._VERTEX_EXPERIMENT_TRACKING_LABEL: True,
                },
                schema_title=metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title,
                schema_version=metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_version,
            )

        self._metadata_node.add_artifacts_and_executions(
            artifact_resource_names=[tensorboard_run_metadata_artifact.resource_name])

        self._backing_tensorboard_run = experiment_resources.VertexResourceWithMetadata(
            resource=tensorboard_run, metadata=tensorboard_run_metadata_artifact
        )

    @staticmethod
    def _tensorboard_run_id(run_id: str) -> str:
        return f'{run_id}-tb-run'

    @_v1_not_supported
    def assign_backing_tensorboard(
        self, tensorboard: Union[tensorboard_resource.Tensorboard, str]
    ):
        """Assigns tensorboard as backing tensorboard to support timeseries metrics logging."""

        backing_tensorboard = self._lookup_tensorboard_run_artifact()
        if backing_tensorboard:
            # TODO: consider warning if tensorboard_resource matches backing tensorboard uri
            raise ValueError(
                f"Experiment run {self._run_name} already associated to tensorboard resource {backing_tensorboard.resource.resource_name}"
            )

        self._assign_backing_tensorboard(tensorboard=tensorboard)

    def _soft_register_tensorboard_run_schema(self):
        """Registers TensorboardRun Metadata schema is not populated."""
        resource_name_parts = self._metadata_node._parse_resource_name(
            self._metadata_node.resource_name
        )
        resource_name_parts.pop("context")
        parent = _MetadataStore._format_resource_name(**resource_name_parts)
        schema_id, schema = metadata_utils.get_tensorboard_board_run_metadata_schema()
        resource_name_parts["metadata_schema"] = schema_id
        metadata_schema_name = _MetadataSchema._format_resource_name(
            **resource_name_parts
        )

        try:
            _MetadataSchema(
                metadata_schema_name, credentials=self._metadata_node.credentials
            )
        except exceptions.NotFound as e:
            _MetadataSchema.create(
                metadata_schema=schema,
                metadata_schema_id=schema_id,
                metadata_store_name=parent,
            )

    def _get_latest_time_series_step(self) -> int:
        """Gets latest time series step of all time series from Tensorboard resource."""
        data = self._backing_tensorboard_run.resource.read_time_series_data()
        return max(ts.values[-1].step if ts.values else 0 for ts in data.values())

    def _assign_experiment_default_backing_tensorboard(self):
        """Assigns backing tensorboard resource to default of Experiment parent."""
        pass

    @_v1_not_supported
    def log_time_series_metrics(
        self,
        metrics: Dict[str, Union[float]],
        step: Optional[int] = None,
        wall_time: Optional[timestamp_pb2.Timestamp] = None,
    ):
        """Logs time series metrics to backing TensorboardRun of this Experiment Run.

        Usage:
            run.log_time_series_metrics({'accuracy': 0.9}, step=10)

        Args:
            metrics (Dict[str, Union[str, float]]):
                Required. Dictionary of where keys are metric names and values are metric values.
            step (int):
                Optional. Step index of this data point within the run.

                If not provided, the latest
                step amongst all time series metrics already logged will be used.
            wall_time (timestamp_pb2.Timestamp):
                Optional. Wall clock timestamp when this data point is
                generated by the end user.

                If not provided, this will be generated based on the value from time.time()
        Raises:
            RuntimeError: If current experiment run doesn't have a backing Tensorboard resource.
        """

        if not self._backing_tensorboard_run:
            self._assign_experiment_default_backing_tensorboard()
            if not self._backing_tensorboard_run:
                raise RuntimeError(
                    "Please set this experiment run with backing tensorboard resource to use log_time_series_metrics."
                )

        self._soft_create_time_series(metric_keys=set(metrics.keys()))

        if not step:
            step = self._largest_step or self._get_latest_time_series_step()
            step += 1
            self._largest_step = step

        self._backing_tensorboard_run.resource.write_tensorboard_scalar_data(
            time_series_data=metrics, step=step, wall_time=wall_time
        )

    def _soft_create_time_series(self, metric_keys: Set[str]):
        """Creates TensorboardTimeSeries for the metric keys if one currently does not exist."""

        if any(
            key
            not in self._backing_tensorboard_run.resource._time_series_display_name_to_id_mapping
            for key in metric_keys
        ):
            self._backing_tensorboard_run.resource._sync_time_series_display_name_to_id_mapping()

        for key in metric_keys:
            if (
                key
                not in self._backing_tensorboard_run.resource._time_series_display_name_to_id_mapping
            ):
                with experiment_resources._SetLoggerLevel(tensorboard_resource):
                    self._backing_tensorboard_run.resource.create_tensorboard_time_series(
                        display_name=key
                    )

    def log_params(self, params: Dict[str, Union[float, int, str]]):
        """Log single or multiple parameters with specified key and value pairs.

        Args:
            params (Dict):
                Required. Parameter key/value pairs.
        """
        # query the latest run execution resource before logging.
        for key, value in params.items():
            if not isinstance(key, str):
                raise ValueError(f'{key} is of type {type(key).__name__} must of type str')
            if not isinstance(value, (float, int, str)):
                raise ValueError(
                    f'Value for key {key} is of type {type(value).__name__} but must be one of float, int, str')

        if self._is_v1_experiment_run():
            self._metadata_node.update(metadata=params)
        else:
            self._metadata_node.update(metadata={constants._PARAM_KEY:params})

    def log_metrics(self, metrics: Dict[str, Union[float, int]]):
        """Log single or multiple Metrics with specified key and value pairs.

        Args:
            metrics (Dict):
                Required. Metrics key/value pairs. Only flot and int are supported format for value.
        Raises:
            TypeError: If value contains unsupported types.
            ValueError: If Experiment or Run is not set.
        """
        for key, value in metrics.items():
            if not isinstance(key, str):
                raise ValueError(f'{key} is of type {type(key).__name__} must of type str')
            if not isinstance(value, (float, int, str)):
                raise ValueError(
                    f'Value for key {key} is of type {type(value).__name__} but must be one of float, int, str')

        if self._is_v1_experiment_run():
            self._metadata_metric_artifact.update(metadata=metrics)
        else:
            # TODO: query the latest metrics artifact resource before logging.
            self._metadata_node.update(metadata={constants._METRIC_KEY:metrics})

    @_v1_not_supported
    def get_time_series_dataframe(self) -> "pd.DataFrame":
        """Returns all time series in this Run as a Dataframe.


        Returns:
            pd.DataFrame: Time series in this Run as a Dataframe.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is not installed and is required to get dataframe as the return format. "
                'Please install the SDK using "pip install python-aiplatform[metadata]"'
            )

        if not self._backing_tensorboard_run:
            return pd.DataFrame({})
        data = self._backing_tensorboard_run.resource.read_time_series_data()

        if not data:
            return pd.DataFrame({})

        return (
            pd.DataFrame(
                {
                    name: entry.scalar.value,
                    "step": entry.step,
                    "wall_time": entry.wall_time,
                }
                for name, ts in data.items()
                for entry in ts.values
            )
            .groupby(["step", "wall_time"])
            .first()
            .reset_index()
        )

    @_v1_not_supported
    def get_logged_pipeline_jobs(self) -> List[pipeline_jobs.PipelineJob]:

        pipeline_job_contexts = self._get_logged_pipeline_runs()

        return [
            pipeline_jobs.PipelineJob.get(
                c.display_name,
                project=c.project,
                location=c.location,
                credentials=c.credentials,
            )
            for c in pipeline_job_contexts
        ]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        state = gapic.Execution.State.FAILED if exc_type else gapic.Execution.State.COMPLETE

        if metadata.experiment_tracker.experiment_run is self:
            metadata.experiment_tracker.end_run(state=state)
        else:
            self.end_run(state)

    def end_run(self, state: gapic.Execution.State = gapic.Execution.State.COMPLETE):
        self.update_state(state)

    def delete(self, *, delete_backing_tensorboard_run: bool=False):
        if delete_backing_tensorboard_run:
            if not self._is_v1_experiment_run():
                if not self._backing_tensorboard_run:
                    self._backing_tensorboard_run=self._lookup_tensorboard_run_artifact()
                if self._backing_tensorboard_run:
                    self._backing_tensorboard_run.resource.delete()
                    self._backing_tensorboard_run.metadata.delete()
                else:
                    _LOGGER.warn(f'Experiment run {self.name} does not have a backing tensorboard run.'
                                 " Skipping deletion.")
            else:
                _LOGGER.warn(f'Experiment run {self.name} does not have a backing tensorboard run.'
                             " Skipping deletion.")

        self._metadata_node.delete()

        if self._is_v1_experiment_run():
            self._metadata_metric_artifact.delete()

    @_v1_not_supported
    def get_artifacts(self) -> List[Artifact]:
        return self._metadata_node.get_artifacts()

    @_v1_not_supported
    def get_executions(self) -> List[Execution]:
        return self._metadata_node.get_executions()

    def get_params(self) -> Dict[str, Union[int, float, str]]:
        if self._is_v1_experiment_run():
            return self._metadata_node.metadata
        else:
            return self._metadata_node.metadata[constants._PARAM_KEY]

    def get_metrics(self) -> Dict[str, Union[int, float]]:
        if self._is_v1_experiment_run():
            return self._metadata_metric_artifact.metadata
        else:
            return self._metadata_node.metadata[constants._METRIC_KEY]

    @_v1_not_supported
    def associate_execution(self, execution: Execution):
        self._metadata_node.add_artifacts_and_executions(
            execution_resource_names=[execution.resource_name])

    def _association_wrapper(self, f: Callable[..., Any]) -> Callable[..., Any]:
        """Wraps methods and automatically associates all passed in Artifacts or Executions to this
        ExperimentRun.

        TODO: Also associate outputs of the method.
        """

        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            artifacts = []
            executions = []
            for value in [*args, *kwargs.values()]:
                value = value if isinstance(value, collections.Iterable) else [value]
                for item in value:
                    if isinstance(item, Execution):
                        executions.append(item)
                    elif isinstance(item, Artifact):
                        artifacts.append(item)
                    elif VertexResourceArtifactResolver.supports_metadata(item):
                        artifacts.append(
                            VertexResourceArtifactResolver.resolve_or_create_resource_artifact(item))

            if artifacts or executions:
                self._metadata_node.add_artifacts_and_executions(
                    artifact_resource_names=[a.resource_name for a in artifacts],
                    execution_resource_names=[e.resource_name for e in executions]
                )

            result = f(*args, **kwargs)
            return result
        return wrapper