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
from typing import Dict

from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import _Execution
from google.cloud.aiplatform.metadata.artifact import _Artifact


class _MetadataService:
    """Contains the exposed APIs to interact with the Managed Metadata Service."""

    def __init__(self):
        self._experiment = None
        self._run = None
        self._metrics = None

    def set_experiment(self, experiment: str):
        if not experiment:
            raise ValueError(f"Invalid experiment {experiment}.")

        store = _MetadataStore.get()
        if not store:
            logging.info(
                f"Creating a default MetadataStore for experiment {experiment}"
            )
            _MetadataStore.create()

        context = _Context.get(context_name=experiment)
        if not context:
            logging.info(f"Creating a Context for experiment {experiment}")
            context = _Context.create(
                context_id=experiment,
                schema_title="system.Experiment",
                schema_version="0.0.1",
            )
        self._experiment = context.name

    def set_run(self, run: str):
        if not self._experiment:
            raise ValueError(
                "No experiment set for this run. Make sure to call aiplatform.init(experiment='my-experiment') or "
                "aiplatform.set_experiment(experiment='my-experiment') before trying to set_run. "
            )
        if not run:
            raise ValueError(f"Invalid run {run}.")

        execution = _Execution.get(execution_name=run)
        if not execution:
            logging.info(f"Creating an Execution for run {run}")
            execution = _Execution.create(
                execution_id=run, schema_title="system.Run", schema_version="0.0.1",
            )
        self._run = execution.name

    def log_params(self, params: Dict):
        if not self._experiment:
            raise ValueError(
                "No experiment set for logging parameters. Make sure to call aiplatform.init("
                "experiment='my-experiment') or aiplatform.set_experiment(experiment='my-experiment') before trying "
                "to log_params. "
            )
        if not self._run:
            raise ValueError(
                "No run set for logging parameters. Make sure to call aiplatform.init(experiment='my-experiment', "
                "run='my-run') or aiplatform.set_run('my-run') before trying to log_params. "
            )
        execution = _Execution.get(execution_name=self._run)
        if not execution:
            logging.info(f"Creating an Execution for run {self._run}")
            execution = _Execution.create(
                execution_id=self._run,
                schema_title="system.Run",
                schema_version="0.0.1",
                metadata=params,
            )
        else:
            logging.info(f"Updating Execution for run {self._run}")
            execution = execution.update(metadata=params)
        self._run = execution.name

    def log_metrics(self, metrics: Dict):
        if not self._experiment:
            raise ValueError(
                "No experiment set for logging metrics. Make sure to call aiplatform.init(experiment='my-experiment') "
                "or aiplatform.set_experiment(experiment='my-experiment') before trying to log_metrics. "
            )
        if not self._run:
            raise ValueError(
                "No run set for logging metrics. Make sure to call aiplatform.init(experiment='my-experiment', "
                "run='my-run') or aiplatform.set_run('my-run') before trying to log_metrics. "
            )
        # Only one metrics artifact for the (experiment, run) tuple.
        artifact_id = f"{self._experiment}-{self._run}"
        artifact = _Artifact.get(artifact_name=artifact_id)
        if not artifact:
            logging.info(f"Creating an Artifact for run {self._run}")
            artifact = _Artifact.create(
                artifact_id=artifact_id,
                schema_title="system.Metrics",
                schema_version="0.0.1",
                metadata=metrics,
            )
        else:
            logging.info(f"Updating Artifact for run {self._run}")
            artifact = artifact.update(metadata=metrics)
        self._metrics = artifact.name

    def get_experiment(self, experiment: str):
        raise NotImplementedError("get_experiment not implemented")

    def get_run(self, run: str):
        raise NotImplementedError("get_run not implemented")

    def get_pipeline(self, pipeline: str):
        raise NotImplementedError("get_pipeline not implemented")


metadata_service = _MetadataService()
