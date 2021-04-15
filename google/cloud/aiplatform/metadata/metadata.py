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
import logging
from typing import Dict, Union

import pandas as pd
from google.api_core import exceptions

from google.cloud.aiplatform import utils
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

    def set_experiment(self, experiment: str):
        _MetadataStore.get_or_create()
        context = _Context.get_or_create(
            resource_id=experiment,
            display_name=experiment,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        self._experiment = context

    def set_run(self, run: str):
        """Setup a run to current session.

        Args:
            run (str):
                Required. Name of the run to assign current session with.
        """

        if not self._experiment:
            raise ValueError(
                "No experiment set for this run. Make sure to call aiplatform.init(experiment='my-experiment') "
                "before trying to set_run. "
            )
        run_execution_id = f"{self._experiment.name}-{run}"
        run_execution = _Execution.get_or_create(
            resource_id=run_execution_id,
            display_name=run,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
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

    def log_metrics(self, metrics: Dict[str, Union[str, float, int]]):
        """Log single or multiple Metrics with specified key and value pairs.

        Args:
            metrics (Dict):
                Required. Metrics key/value pairs.
        """

        self._validate_experiment_and_run(method_name="log_metrics")
        # query the latest metrics artifact resource before logging.
        artifact = _Artifact.get_or_create(
            resource_id=self._metrics.name,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        artifact.update(metadata=metrics)

    def get_experiment(self, experiment: str) -> pd.DataFrame:
        """Returns a Pandas DataFrame of the parameters and metrics associated with one experiment.

            Example:

            aiplatform.init(experiment='exp-1')
            aiplatform.set_run(run='run-1')
            aiplatform.log_params({'learning_rate': 0.1})
            aiplatform.log_metrics({'accuracy': 0.9})

            aiplatform.set_run(run='run-2')
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
              experiment: Name of the Experiment to filter results.

            Returns:
              Pandas Dataframe of Experiment with metrics and parameters.
            """

        # TODO remove this extra API call once our BE can support project ID in filters.
        try:
            experiment_context = _Context(resource_name=experiment)
        except exceptions.NotFound:
            logging.error(f"Experiment {experiment} not found.")
            return
        if experiment_context.schema_title != constants.SYSTEM_EXPERIMENT:
            raise ValueError(
                f"Please provide a valid experiment name. {experiment} is not a experiment."
            )

        filter = f'schema_title="{constants.SYSTEM_RUN}" AND in_context("{experiment_context.resource_name}")'
        run_executions = _Execution.list(filter=filter)

        experiment_dict = []
        for run_execution in run_executions:
            run_dict = {
                "experiment_name": experiment,
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

            experiment_dict.append(run_dict)

        return pd.DataFrame(experiment_dict)

    def get_pipeline(self, pipeline: str) -> pd.DataFrame:
        """Returns a Pandas DataFrame of the parameters and metrics associated with one pipeline.

                    Args:
                      pipeline: Name of the Pipeline to filter results.

                    Returns:
                      Pandas Dataframe of Pipeline with metrics and parameters.
                    """

        # TODO remove this extra API call once our BE can support project ID in filters.
        try:
            pipeline_context = _Context(resource_name=pipeline)
        except exceptions.NotFound:
            logging.error(f"Pipeline {pipeline} not found.")
            return
        if pipeline_context.schema_title != constants.SYSTEM_PIPELINE:
            raise ValueError(
                f"Please provide a valid pipeline name. {pipeline} is not a pipeline."
            )

        filter = f'schema_title="{constants.SYSTEM_RUN}" AND in_context("{pipeline_context.resource_name}")'
        run_executions = _Execution.list(filter=filter)

        pipeline_dict = []
        for run_execution in run_executions:
            run_dict = {
                "pipeline_name": pipeline,
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

            pipeline_dict.append(run_dict)

        return pd.DataFrame(pipeline_dict)

    def _validate_experiment_and_run(self, method_name: str):
        if not self._experiment:
            raise ValueError(
                f"No experiment set. Make sure to call aiplatform.init(experiment='my-experiment') "
                f"before trying to {method_name}. "
            )
        if not self._run:
            raise ValueError(
                f"No run set. Make sure to call aiplatform.set_run('my-run') before trying to {method_name}. "
            )

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

        return {".".join([metadata_type, key]): value for key, value in metadata}


metadata_service = _MetadataService()
