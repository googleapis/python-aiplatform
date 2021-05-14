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

from typing import Dict, Union, Optional

from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import _Execution
from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore


class _MetadataService:
    """Contains the exposed APIs to interact with the Managed Metadata Service."""

    def __init__(self):
        self._experiment = None
        self._run = None
        self._metrics = None

    def reset(self):
        """Reset all _MetadataService fields to None"""
        self._experiment = None
        self._run = None
        self._metrics = None

    @property
    def experiment_name(self) -> Optional[str]:
        """Return the experiment name of the _MetadataService, if experiment is not set, return None"""
        if self._experiment:
            return self._experiment.display_name
        return None

    @property
    def run_name(self) -> Optional[str]:
        """Return the run name of the _MetadataService, if run is not set, return None"""
        if self._run:
            return self._run.display_name
        return None

    def set_experiment(self, experiment: str, description: Optional[str] = None):
        """Setup a experiment to current session.

        Args:
            experiment (str):
                Required. Name of the experiment to assign current session with.
            description (str):
                Optional. Description of an experiment.
        """

        _MetadataStore.get_or_create()
        context = _Context.get_or_create(
            resource_id=experiment,
            display_name=experiment,
            description=description,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        if context.schema_title != constants.SYSTEM_EXPERIMENT:
            raise ValueError(
                f"Experiment name {experiment} has been used to create other type of resources "
                f"({context.schema_title}) in this MetadataStore, please choose a different experiment name."
            )

        if description and context.description != description:
            context.update(metadata=context.metadata, description=description)

        self._experiment = context

    def start_run(self, run: str):
        """Setup a run to current session.

        Args:
            run (str):
                Required. Name of the run to assign current session with.
        Raise:
            ValueError if experiment is not set. Or if run execution or metrics artifact
            is already created but with a different schema.
        """

        if not self._experiment:
            raise ValueError(
                "No experiment set for this run. Make sure to call aiplatform.init(experiment='my-experiment') "
                "before trying to start_run. "
            )
        run_execution_id = f"{self._experiment.name}-{run}"
        run_execution = _Execution.get_or_create(
            resource_id=run_execution_id,
            display_name=run,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
        )
        if run_execution.schema_title != constants.SYSTEM_RUN:
            raise ValueError(
                f"Run name {run} has been used to create other type of resources ({run_execution.schema_title}) "
                "in this MetadataStore, please choose a different run name."
            )
        self._experiment.add_artifacts_and_executions(
            execution_resource_names=[run_execution.resource_name]
        )

        metrics_artifact_id = f"{self._experiment.name}-{run}-metrics"
        metrics_artifact = _Artifact.get_or_create(
            resource_id=metrics_artifact_id,
            display_name=metrics_artifact_id,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        if metrics_artifact.schema_title != constants.SYSTEM_METRICS:
            raise ValueError(
                f"Run name {run} has been used to create other type of resources ({metrics_artifact.schema_title}) "
                "in this MetadataStore, please choose a different run name."
            )
        run_execution.add_artifact(
            artifact_resource_name=metrics_artifact.resource_name, input=False
        )

        self._run = run_execution
        self._metrics = metrics_artifact

    def log_params(self, params: Dict[str, Union[float, int, str]]):
        """Log single or multiple parameters with specified key and value pairs.

        Args:
            params (Dict):
                Required. Parameter key/value pairs.
        """

        self._validate_experiment_and_run(method_name="log_params")
        # query the latest run execution resource before logging.
        execution = _Execution.get_or_create(
            resource_id=self._run.name,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
        )
        execution.update(metadata=params)

    def log_metrics(self, metrics: Dict[str, Union[float, int]]):
        """Log single or multiple Metrics with specified key and value pairs.

        Args:
            metrics (Dict):
                Required. Metrics key/value pairs. Only flot and int are supported format for value.
        Raises:
            TypeError if value contains unsupported types.
            ValueError if Experiment or Run is not set.
        """

        self._validate_experiment_and_run(method_name="log_metrics")
        self._validate_metrics_value_type(metrics)
        # query the latest metrics artifact resource before logging.
        artifact = _Artifact.get_or_create(
            resource_id=self._metrics.name,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        artifact.update(metadata=metrics)

    def get_experiment_df(
        self, experiment: Optional[str] = None
    ) -> "pd.DataFrame":  # noqa: F821
        """Returns a Pandas DataFrame of the parameters and metrics associated with one experiment.

            Example:

            aiplatform.init(experiment='exp-1')
            aiplatform.start_run(run='run-1')
            aiplatform.log_params({'learning_rate': 0.1})
            aiplatform.log_metrics({'accuracy': 0.9})

            aiplatform.start_run(run='run-2')
            aiplatform.log_params({'learning_rate': 0.2})
            aiplatform.log_metrics({'accuracy': 0.95})

            Will result in the following DataFrame
            ___________________________________________________________________________
            | experiment_name | run_name      | param.learning_rate | metric.accuracy |
            ---------------------------------------------------------------------------
            | exp-1           | run-1         | 0.1                 | 0.9             |
            | exp-1           | run-2         | 0.2                 | 0.95            |
            ---------------------------------------------------------------------------

            Args:
                experiment (str):
                Name of the Experiment to filter results. If not set, return results of current active experiment.

            Returns:
                Pandas Dataframe of Experiment with metrics and parameters.

            Raise:
                NotFound exception if experiment does not exist.
                ValueError if given experiment is not associated with a wrong schema.
            """

        if not experiment:
            experiment = self._experiment.name

        source = "experiment"
        experiment_resource_name = self._get_experiment_or_pipeline_resource_name(
            name=experiment, source=source, expected_schema=constants.SYSTEM_EXPERIMENT,
        )

        return self._query_runs_to_data_frame(
            context_id=experiment,
            context_resource_name=experiment_resource_name,
            source=source,
        )

    def get_pipeline_df(self, pipeline: str) -> "pd.DataFrame":  # noqa: F821
        """Returns a Pandas DataFrame of the parameters and metrics associated with one pipeline.

        Args:
            pipeline: Name of the Pipeline to filter results.

        Returns:
            Pandas Dataframe of Pipeline with metrics and parameters.

        Raise:
            NotFound exception if experiment does not exist.
            ValueError if given experiment is not associated with a wrong schema.
        """

        source = "pipeline"
        pipeline_resource_name = self._get_experiment_or_pipeline_resource_name(
            name=pipeline, source=source, expected_schema=constants.SYSTEM_PIPELINE
        )

        return self._query_runs_to_data_frame(
            context_id=pipeline,
            context_resource_name=pipeline_resource_name,
            source=source,
        )

    def _validate_experiment_and_run(self, method_name: str):
        if not self._experiment:
            raise ValueError(
                f"No experiment set. Make sure to call aiplatform.init(experiment='my-experiment') "
                f"before trying to {method_name}. "
            )
        if not self._run:
            raise ValueError(
                f"No run set. Make sure to call aiplatform.start_run('my-run') before trying to {method_name}. "
            )

    @staticmethod
    def _validate_metrics_value_type(metrics: Dict[str, Union[float, int]]):
        """Verify that metrics value are with supported types.

        Args:
            metrics (Dict):
                Required. Metrics key/value pairs. Only flot and int are supported format for value.
        Raises:
            TypeError if value contains unsupported types.
        """

        for key, value in metrics.items():
            if isinstance(value, int) or isinstance(value, float):
                continue
            raise TypeError(
                f"metrics contain unsupported value types. key: {key}; value: {value}; type: {type(value)}"
            )

    @staticmethod
    def _get_experiment_or_pipeline_resource_name(
        name: str, source: str, expected_schema: str
    ) -> str:
        """Get the full resource name of the Context representing an Experiment or Pipeline.

        Args:
            name (str):
                Name of the Experiment or Pipeline.
            source (str):
                Identify whether the this is an Experiment or a Pipeline.
            expected_schema (str):
                expected_schema identifies the expected schema used for Experiment or Pipeline.

        Returns:
            The full resource name of the Experiment or Pipeline Context.

        Raise:
            NotFound exception if experiment or pipeline does not exist.
        """

        context = _Context(resource_name=name)

        if context.schema_title != expected_schema:
            raise ValueError(
                f"Please provide a valid {source} name. {name} is not a {source}."
            )
        return context.resource_name

    def _query_runs_to_data_frame(
        self, context_id: str, context_resource_name: str, source: str
    ) -> "pd.DataFrame":  # noqa: F821
        """Get metrics and parameters associated with a given Context into a Dataframe.

        Args:
            context_id (str):
                Name of the Experiment or Pipeline.
            context_resource_name (str):
                Full resource name of the Context associated with an Experiment or Pipeline.
            source (str):
                Identify whether the this is an Experiment or a Pipeline.

        Returns:
            The full resource name of the Experiment or Pipeline Context.
        """

        filter = f'schema_title="{constants.SYSTEM_RUN}" AND in_context("{context_resource_name}")'
        run_executions = _Execution.list(filter=filter)

        context_summary = []
        for run_execution in run_executions:
            run_dict = {
                f"{source}_name": context_id,
                "run_name": run_execution.display_name,
            }
            run_dict.update(
                self._execution_to_column_named_metadata(
                    "param", run_execution.metadata
                )
            )

            for metric_artifact in run_execution.query_input_and_output_artifacts():
                run_dict.update(
                    self._execution_to_column_named_metadata(
                        "metric", metric_artifact.metadata
                    )
                )

            context_summary.append(run_dict)

        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is not installed and is required to get dataframe as the return format. "
                'Please install the SDK using "pip install python-aiplatform[full]"'
            )

        return pd.DataFrame(context_summary)

    @staticmethod
    def _execution_to_column_named_metadata(
        metadata_type: str, metadata: Dict,
    ) -> Dict[str, Union[int, float, str]]:
        """Returns a dict of the Execution/Artifact metadata with column names.

        Args:
          metadata_type: The type of this execution properties (param, metric).
          metadata: Either an Execution or Artifact metadata field.

        Returns:
          Dict of custom properties with keys mapped to column names
        """

        return {
            ".".join([metadata_type, key]): value for key, value in metadata.items()
        }


metadata_service = _MetadataService()
