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

import abc
from collections import defaultdict
import concurrent.futures
import functools
import logging
import time
from typing import Dict, List, NamedTuple, Optional, Set, Union

from google.api_core import exceptions
from google.auth import credentials as auth_credentials
from google.protobuf import timestamp_pb2

from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series as gca_tensorboard_time_series,
)
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import experiment_resources
from google.cloud.aiplatform.metadata.artifact import Artifact
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import _Execution
from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore
from google.cloud.aiplatform.metadata import resource
from google.cloud.aiplatform.metadata.schema import _MetadataSchema
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform.tensorboard import tensorboard_resource


def _format_experiment_run_name(experiment_name: str, run_name: str) -> str:
    return f"{experiment_name}-{run_name}"


class ExperimentRun:
    def __init__(
        self,
        run_name: str,
        experiment: Union[experiment_resources.Experiment, str, None] = None,
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

        def _get_execution():
            with experiment_resources._SetLoggerLevel(resource):
                # TODO: Add schema validation on these metadata nodes
                return _Execution(**metadata_args)

        def _get_metric():
            with experiment_resources._SetLoggerLevel(resource):
                metadata_args_copy = dict(**metadata_args)
                metadata_args_copy["resource_name"] += "-metrics"
                return _Artifact(**metadata_args_copy)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            _metadata_context = executor.submit(_get_context)
            _metadata_execution = executor.submit(_get_execution)
            _metadata_metric = executor.submit(_get_metric)

            self._metadata_context = _metadata_context.result()
            self._metadata_execution = _metadata_execution.result()
            self._metadata_metric = _metadata_metric.result()

        self._backing_tensorboard_run: Optional[
            experiment_resources.VertexResourceWithMetadata
        ] = self._lookup_tensorboard_run_artifact()

        # initially set to None. Will initially update from resource then track locally.
        self._largest_step: Optional[int] = None

    @property
    def name(self) -> str:
        return self._metadata_context.name

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
        if (
            artifact.schema_title
            != metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title
        ):
            return False
        if not artifact.metadata.get(metadata_utils._VERTEX_EXPERIMENT_TRACKING_LABEL):
            return False

        run_parts = tensorboard_resource.TensorboardRun._parse_resource_name(
            artifact.metadata["resourceName"]
        )

        if (run_parts["experiment"], run_parts["run"]) == (
            self._experiment.name,
            self._run_name,
        ):
            return True

        return False

    def _lookup_tensorboard_run_artifact(
        self,
    ) -> Optional[experiment_resources.VertexResourceWithMetadata]:
        metadata_artifacts = self._metadata_execution.query_input_and_output_artifacts()

        for artifact in metadata_artifacts:
            if self._is_backing_tensorboard_run_artifact(artifact):
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

        filter_str = f'schema_title="{constants.SYSTEM_EXPERIMENT_RUN}" AND parent_contexts:"{experiment.resource_name}"'
        run_contexts = _Context.list(filter=filter_str, **metadata_args)

        def _initialize_experiment_run(context):
            this_experiment_run = cls.__new__(cls)
            this_experiment_run._experiment = experiment
            this_experiment_run._run_name = context.display_name
            this_experiment_run._metadata_context = context

            with experiment_resources._SetLoggerLevel(resource):
                this_experiment_run._metadata_execution = _Execution(
                    resource_name=context.name, **metadata_args
                )
                this_experiment_run._metadata_metric = _Artifact(
                    resource_name=context.name + "-metrics", **metadata_args
                )
                tb_run_artifact = _Artifact._get(
                    resource_name=context.name + "-tbrun", **metadata_args
                )
            if tb_run_artifact:
                tb_run = tensorboard_resource.TensorboardRun(
                    tb_run_artifact.metadata["resourceName"], **metadata_args
                )
                this_experiment_run._backing_tensorboard_run = (
                    experiment_resources.VertexResourceWithMetadata(
                        metadata=tb_run_artifact, resource=tb_run
                    )
                )
            else:
                this_experiment_run._backing_tensorboard_run = None

            this_experiment_run._largest_step = None

            return this_experiment_run

        with concurrent.futures.ThreadPoolExecutor(
            max_workers=len(run_contexts)
        ) as executor:
            submissions = [
                executor.submit(_initialize_experiment_run, context)
                for context in run_contexts
            ]
            experiment_runs = [submission.result() for submission in submissions]

        return experiment_runs

    def _get_pandas_row_dicts(self) -> List[Dict[str, Union[float, int, str]]]:
        """Returns the run as a Pandas row Dict."""

        run_dict = {
            "experiment_name": self._experiment.name,
            "run_name": self._run_name,
        }

        run_dict.update(
            experiment_resources._execution_to_column_named_metadata(
                "param", self.get_params()
            )
        )
        run_dict.update(
            experiment_resources._execution_to_column_named_metadata(
                "metric", self._metadata_metric.metadata
            )
        )
        run_dict.update(self._get_latest_time_series_metric_columns())

        rows = [run_dict]

        pipeline_jobs = self._get_logged_pipeline_runs_as_pandas_row_dicts()

        if len(run_dict) == 2:
            rows = pipeline_jobs
        else:
            rows += pipeline_jobs

        return rows

    def _get_logged_pipeline_runs(self) -> List[_Context]:
        """Returns Pipeline Run contexts logged to this Experiment Run."""

        service_request_args = dict(
            project=self._metadata_context.project,
            location=self._metadata_context.location,
            credentials=self._metadata_context.credentials,
        )

        filter_str = f'schema_title="{constants.SYSTEM_PIPELINE_RUN}" AND parent_contexts:"{self._metadata_context.resource_name}"'

        return _Context.list(filter=filter_str, **service_request_args)

    def _get_logged_pipeline_runs_as_pandas_row_dicts(
        self,
    ) -> List[Dict[str, Union[float, int, str]]]:
        """Returns Pipeline Runs as Pandas row dictionaries."""

        pipeline_run_contexts = self._get_logged_pipeline_runs()

        row_dicts = []

        for pipeline_run_context in pipeline_run_contexts:
            pipeline_run_dict = {
                "experiment_name": self._experiment.name,
                "pipeline_run_name": pipeline_run_context.name,
                "run_name": self._run_name,
            }

            context_lineage_subgraph = pipeline_run_context.query_lineage_subgraph()
            artifact_map = {
                artifact.name: artifact
                for artifact in context_lineage_subgraph.artifacts
            }
            output_execution_map = defaultdict(list)
            for event in context_lineage_subgraph.events:
                if event.type_ == gca_event.Event.Type.OUTPUT:
                    output_execution_map[event.execution].append(event.artifact)

            execution_dicts = []
            for execution in context_lineage_subgraph.executions:
                if execution.schema_title == constants.SYSTEM_RUN:
                    pipeline_params = (
                        experiment_resources._execution_to_column_named_metadata(
                            metadata_type="param",
                            metadata=execution.metadata,
                            filter_prefix=constants.PIPELINE_PARAM_PREFIX,
                        )
                    )
                elif execution.schema_title == "system.DagExecution":
                    # ignore for loop and condition control flow executions
                    continue
                else:
                    execution_dict = pipeline_run_dict.copy()
                    execution_dict["execution_name"] = execution.display_name
                    execution_dict.update(
                        experiment_resources._execution_to_column_named_metadata(
                            metadata_type="param",
                            metadata=execution.metadata,
                            filter_prefix=constants.PIPELINE_PARAM_PREFIX,
                        )
                    )
                    artifact_dicts = []
                    for artifact_name in output_execution_map[execution.name]:
                        artifact = artifact_map.get(artifact_name)
                        if (
                            artifact
                            and artifact.schema_title == constants.SYSTEM_METRICS
                            and artifact.metadata
                        ):
                            execution_with_metric_dict = execution_dict.copy()
                            execution_with_metric_dict[
                                "output_name"
                            ] = artifact.display_name
                            execution_with_metric_dict.update(
                                experiment_resources._execution_to_column_named_metadata(
                                    "metric", artifact.metadata
                                )
                            )
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
                pipeline_run_dict.update(pipeline_params)
                row_dicts.append(pipeline_run_dict)
                for execution_dict in execution_dicts:
                    execution_dict.update(pipeline_run_row)
                    row_dicts.append(execution_dict)

        return row_dicts

    def _get_latest_time_series_metric_columns(self) -> Dict[str, Union[float, int]]:
        if self._backing_tensorboard_run:
            time_series_metrics = (
                self._backing_tensorboard_run.resource.read_time_series_data()
            )

            return {
                f"time_series_metric.{display_name}": data.values[-1].scalar.value
                for display_name, data in time_series_metrics.items()
                if data.value_type
                == gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR
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

        resource_name_fields = pipeline_jobs.PipelineJob._parse_resource_name(
            pipeline_job.resource_name
        )

        pipeline_job_context = None
        pipeline_job_context_getter = functools.partial(
            _Context._get,
            resource_name=resource_name_fields["pipeline_job"],
            project=resource_name_fields["project"],
            location=resource_name_fields["location"],
        )

        # PipelineJob context is created asynchronously so we need to poll until it exists.
        while not pipeline_job_context:
            with experiment_resources._SetLoggerLevel(resource):
                pipeline_job_context = pipeline_job_context_getter()

            if not pipeline_job_context:
                if pipeline_job.done():
                    with experiment_resources._SetLoggerLevel(resource):
                        pipeline_job_context = pipeline_job_context_getter()
                    if not pipeline_job_context:
                        if pipeline_job.has_failed:
                            raise RuntimeError(
                                f"Cannot associate PipelineJob to Experiment Run: {pipeline_job.gca_resource.error}"
                            )
                        else:
                            raise RuntimeError(
                                f"Cannot associate PipelineJob to Experiment Run because PipelineJob context could not be found."
                            )
                else:
                    time.sleep(1)

        self._metadata_context.add_context_children([pipeline_job_context])

    def _log_artifact(self, artifact: Artifact):
        self._metadata_execution.add_artifact(
            artifact_resource_name=artifact.resource_name, input=False
        )

    def _consume_artifact(self, artifact: Artifact):
        self._metadata_execution.add_artifact(
            artifact_resource_name=artifact.resource_name, input=True
        )

    def log(
        self,
        *,
        pipeline_job: Optional[pipeline_jobs.PipelineJob] = None,
        artifact: Optional[Artifact] = None,
    ):
        if pipeline_job:
            self._log_pipeline_job(pipeline_job=pipeline_job)
        if artifact:
            self._log_artifact(artifact=artifact)

    @classmethod
    def create(
        cls,
        run_name: str,
        experiment: Union[experiment_resources.Experiment, str, None] = None,
        tensorboard: Union[tensorboard_resource.Tensorboard, str, None] = None,
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
                    metadata=constants.EXPERIMENT_METADATA,
                    project=project,
                    location=location,
                    credentials=credentials,
                )

        def _create_execution():
            with experiment_resources._SetLoggerLevel(resource):
                cls._soft_register_system_run_schema(experiment._metadata_context)

                return _Execution._create(
                    resource_id=run_id,
                    display_name=run_name,
                    schema_title=constants._EXPERIMENTS_V2_SYSTEM_RUN,
                    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                    project=project,
                    location=location,
                    credentials=credentials,
                )

        def _create_artifact():
            metrics_artifact_id = f"{run_id}-metrics"

            with experiment_resources._SetLoggerLevel(resource):
                return _Artifact._create(
                    resource_id=metrics_artifact_id,
                    display_name=metrics_artifact_id,
                    schema_title=constants.SYSTEM_METRICS,
                    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
                    project=project,
                    location=location,
                    credentials=credentials,
                )

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            metadata_context = executor.submit(_create_context)
            metadata_execution = executor.submit(_create_execution)
            metrics_artifact = executor.submit(_create_artifact)

            metadata_context = metadata_context.result()
            metadata_execution = metadata_execution.result()
            metrics_artifact = metrics_artifact.result()

        if metadata_context is None:
            raise RuntimeError(
                f"Experiment Run with name {run_name} in {experiment.name} already exists."
            )

        experiment_run = cls.__new__(cls)
        experiment_run._experiment = experiment
        experiment_run._run_name = metadata_context.display_name
        experiment_run._metadata_context = metadata_context
        experiment_run._metadata_execution = metadata_execution
        experiment_run._metadata_metric = metrics_artifact
        experiment_run._largest_step = None

        def _add_experiment_run_to_experiment():
            experiment._metadata_context.add_context_children([metadata_context])

        def _add_execution_to_context():
            metadata_context.add_artifacts_and_executions(
                execution_resource_names=[metadata_execution.resource_name]
            )

        def _add_metrics_to_execution():
            metadata_execution.add_artifact(
                artifact_resource_name=metrics_artifact.resource_name, input=False
            )

        def _add_tensorboard_to_run():
            if tensorboard:
                cls._assign_backing_tensorboard(
                    self=experiment_run, tensorboard=tensorboard
                )
            else:
                cls._assign_to_experiment_backing_tensorboard(self=experiment_run)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            submissions = [
                executor.submit(fn)
                for fn in [
                    _add_tensorboard_to_run,
                    _add_experiment_run_to_experiment,
                    _add_execution_to_context,
                    _add_metrics_to_execution,
                ]
            ]

            for submission in submissions:
                submission.result()

        return experiment_run

    def _assign_to_experiment_backing_tensorboard(self):
        """Assings parent Experiment backing tensorboard resource to this Experiment Run."""
        backing_tensorboard_resource = (
            self._experiment.get_backing_tensorboard_resource()
        )
        if backing_tensorboard_resource:
            self.assign_backing_tensorboard(tensorboard=backing_tensorboard_resource)

    def _assign_backing_tensorboard(
        self, tensorboard: Union[tensorboard_resource.Tensorboard, str]
    ):
        if isinstance(tensorboard, str):
            tensorboard = tensorboard_resource.Tensorboard(tensorboard)

        tensorboard_resource_name_parts = tensorboard._parse_resource_name(
            tensorboard.resource_name
        )
        tensorboard_experiment_resource_name = (
            tensorboard_resource.TensorboardExperiment._format_resource_name(
                experiment=self._experiment.name, **tensorboard_resource_name_parts
            )
        )
        try:
            tensorboard_experiment = tensorboard_resource.TensorboardExperiment(
                tensorboard_experiment_resource_name
            )
        except exceptions.NotFound:
            with experiment_resources._SetLoggerLevel(tensorboard_resource):
                tensorboard_experiment = (
                    tensorboard_resource.TensorboardExperiment.create(
                        tensorboard_experiment_id=self._experiment.name,
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

        self._soft_register_tensorboard_run_schema()

        metadata_resource_id = f"{self._metadata_context.name}-tbrun"

        with experiment_resources._SetLoggerLevel(resource):
            tensorboard_run_metadata_artifact = _Artifact._create(
                resource_id=metadata_resource_id,
                uri=gcp_resource_url,
                metadata={
                    "resourceName": tensorboard_run.resource_name,
                    metadata_utils._VERTEX_EXPERIMENT_TRACKING_LABEL: True,
                },
                schema_title=metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title,
                schema_version=metadata_utils._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_version,
            )

        self._metadata_execution.add_artifact(
            artifact_resource_name=tensorboard_run_metadata_artifact.resource_name,
            input=False,
        )

        self._backing_tensorboard_run = experiment_resources.VertexResourceWithMetadata(
            resource=tensorboard_run, metadata=tensorboard_run_metadata_artifact
        )

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
        resource_name_parts = self._metadata_context._parse_resource_name(
            self._metadata_context.resource_name
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
                metadata_schema_name, credentials=self._metadata_context.credentials
            )
        except exceptions.NotFound as e:
            _MetadataSchema.create(
                metadata_schema=schema,
                metadata_schema_id=schema_id,
                metadata_store_name=parent,
            )

    @classmethod
    def _soft_register_system_run_schema(cls, metadata_context: _Context):
        """Registers SystemRun Metadata schema is not populated."""
        resource_name_parts = metadata_context._parse_resource_name(
            metadata_context.resource_name
        )
        resource_name_parts.pop("context")
        parent = _MetadataStore._format_resource_name(**resource_name_parts)
        schema = metadata_utils.make_experiment_v2_metadata_schema()
        schema_id = constants._EXPERIMENTS_V2_SYSTEM_RUN_SCHEMA_TITLE
        resource_name_parts["metadata_schema"] = schema_id
        metadata_schema_name = _MetadataSchema._format_resource_name(
            **resource_name_parts
        )

        try:
            _MetadataSchema(
                metadata_schema_name, credentials=metadata_context.credentials
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
        self._metadata_execution.sync_resource()
        self._metadata_execution.update(metadata=params)

    def log_metrics(self, metrics: Dict[str, Union[float, int]]):
        """Log single or multiple Metrics with specified key and value pairs.

        Args:
            metrics (Dict):
                Required. Metrics key/value pairs. Only flot and int are supported format for value.
        Raises:
            TypeError: If value contains unsupported types.
            ValueError: If Experiment or Run is not set.
        """

        # query the latest metrics artifact resource before logging.
        self._metadata_metric.sync_resource()
        self._metadata_metric.update(metadata=metrics)

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

    def get_logged_pipeline_jobs(self) -> List[pipeline_jobs.PipelineJob]:

        pipeline_job_contexts = self._get_logged_pipeline_runs()

        return [
            pipeline_jobs.PipelineJob.get(
                c.name,
                project=c.project,
                location=c.location,
                credentials=c.credentials,
            )
            for c in pipeline_job_contexts
        ]

    def assign_artifact_as_input(self, artifact: Artifact):
        self._consume_artifact(artifact)

    def with_input_artifacts(self, *artifacts: Artifact) -> "ExperimentRun":
        for artifact in artifacts:
            self._consume_artifact(artifact)
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if metadata.experiment_tracker._experiment_run is self:
            metadata.experiment_tracker.end_run()

    # @TODO(add delete API)
    def delete(self, delete_backing_tensorboard_run=False):
        raise NotImplemented("delete not implemented")

    def get_input_artifacts(self) -> List[Artifact]:
        return self._metadata_execution.get_input_artifacts()

    def get_output_artifacts(self) -> List[Artifact]:
        return self._metadata_execution.get_output_artifacts()

    def get_params(self) -> Dict[str, Union[int, float, str]]:
        execution_metadata = self._metadata_execution.metadata
        return {
            key: int(value)
            if isinstance(value, float) and int(value) == value
            else value
            for key, value in execution_metadata.items()
        }
