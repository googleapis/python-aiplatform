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
from google.api_core import exceptions
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

    # TODO(nachocano) Error handling this way is not very readable. Find a better way.
    def set_experiment(self, experiment_name):
        if not experiment_name:
            raise ValueError(f"Invalid experiment_name {experiment_name}.")
        try:
            _MetadataStore()
        except exceptions.NotFound:
            logging.info(
                f"Creating a default MetadataStore for experiment {experiment_name}"
            )
            _MetadataStore.create()

        try:
            context = _Context(context_name=experiment_name)
        except exceptions.NotFound:
            logging.info(
                f"Creating a Context for experiment {experiment_name}"
            )
            context = _Context.create(
                context_id=experiment_name,
                schema_title="system.Experiment",
                schema_version="0.0.1",
            )
        self._experiment = context.name

    def set_run(self, run_name):
        if not self._experiment:
            raise ValueError(
                "No experiment found for this run. Make sure to call aiplatform.init with an experiment name or aiplatform.set_experiment before trying to set a run."
            )
        if not run_name:
            raise ValueError(f"Invalid run_name {run_name}.")
        try:
            execution = _Execution(execution_name=run_name)
        except exceptions.NotFound:
            logging.info(
                f"Creating an Execution for run {run_name}"
            )
            execution = _Execution.create(
                execution_id=run_name,
                schema_title="system.Run",
                schema_version="0.0.1",
            )
        self._run = execution.name

    def log_params(self, params):
        if not self._experiment:
            raise ValueError(
                "No experiment found for logging parameters. Make sure to call aiplatform.init with an experiment name or aiplatform.set_experiment before trying to log params."
            )
        if not self._run:
            raise ValueError(
                "No run found for logging parameters. Make sure to call aiplatform.init with a run name or aiplatform.set_run before trying to log params."
            )
        # Given that we do not support deletion, if we reach this point it means that it should exist an Execution.
        run = _Execution.update(execution_name=self._run, metadata=params)
        self._run = run.name

    def log_metrics(self, metrics):
        if not self._experiment:
            raise ValueError(
                "No experiment found for logging metrics. Make sure to call aiplatform.init with an experiment name or aiplatform.set_experiment before trying to log metrics."
            )
        if not self._run:
            raise ValueError(
                "No run found for logging metrics. Make sure to call aiplatform.init with a run name or aiplatform.set_run before trying to log metrics."
            )
        # Only one metrics artifact for the (experiment, run) tuple.
        artifact_id = f"{self._experiment}-{self._run}"
        try:
            _Artifact(artifact_name=artifact_id)
        except exceptions.NotFound:
            logging.info(
                f"Creating an Artifact for run {self._run}"
            )
            artifact = _Artifact.create(
                artifact_id=artifact_id,
                schema_title="system.Metrics",
                schema_version="0.0.1",
                metadata=metrics,
            )
        else:
            artifact = _Artifact.update(artifact_name=artifact_id, metadata=metrics)
        self._metrics = artifact.name

    def get_experiment(self, experiment_name):
        raise NotImplementedError("get_experiment not implemented")

    def get_pipeline(self, pipeline_name):
        raise NotImplementedError("get_pipeline not implemented")


metadata_service = _MetadataService()
