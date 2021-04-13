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

from google.cloud.aiplatform.metadata.metadata_store import _MetadataStore
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import _Execution
from google.cloud.aiplatform.metadata.artifact import _Artifact


class _MetadataService:
    """Contains the exposed APIs to interact with the Managed Metadata Service."""

    def __init__(self):
        self._experiment = None
        self._run = None

    def set_experiment(self, experiment: str):
        store = _MetadataStore.get()
        if not store:
            _MetadataStore.create()

        context = _Context.get(resource_name=experiment)
        if not context:
            logging.info(f"Creating Experiment {experiment}")
            context = _Context.create(
                resource_id=experiment,
                schema_title=constants.SYSTEM_EXPERIMENT,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            )
        self._experiment = context.name

    def set_run(self, run: str):
        if not self._experiment:
            raise ValueError(
                "No experiment set for this run. Make sure to call aiplatform.init(experiment='my-experiment') or "
                "aiplatform.set_experiment(experiment='my-experiment') before trying to set_run. "
            )
        execution = _Execution.get(resource_name=run)
        if not execution:
            logging.info(f"Creating Run {run}")
            execution = _Execution.create(
                resource_id=run,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
            )
        self._run = execution.name

    def log_param(self, name: str, value: Union[float, int, str]):
        return self.log_params({name: value})

    def log_params(self, params: Dict[str, Union[float, int, str]]):
        self._validate_experiment_and_run(method_name="log_params")
        execution = _Execution.get(resource_name=self._run)
        if not execution:
            logging.info(f"Creating Run {self._run}")
            execution = _Execution.create(
                resource_id=self._run,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=params,
            )
        else:
            logging.info(f"Updating Run {self._run}")
            execution.update(metadata=params)
        self._run = execution.name

    def log_metric(self, name: str, value: Union[str, float, int]):
        return self.log_metrics({name: value})

    def log_metrics(self, metrics: Dict[str, Union[str, float, int]]):
        self._validate_experiment_and_run(method_name="log_metrics")
        # Only one metrics artifact for the (experiment, run) tuple.
        artifact_id = f"{self._experiment}-{self._run}"
        artifact = _Artifact.get(resource_name=artifact_id)
        if not artifact:
            logging.info(f"Creating Metrics for Run {self._run}")
            _Artifact.create(
                resource_id=artifact_id,
                schema_title=constants.SYSTEM_METRICS,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
                metadata=metrics,
            )
        else:
            logging.info(f"Updating Metrics for Run {self._run}")
            artifact.update(metadata=metrics)

    def get_experiment(self, experiment: str):
        raise NotImplementedError("get_experiment not implemented")

    def _validate_experiment_and_run(self, method_name: str):
        if not self._experiment:
            raise ValueError(
                f"No experiment set. Make sure to call aiplatform.init(experiment='my-experiment') "
                f"or aiplatform.set_experiment(experiment='my-experiment') before trying to {method_name}. "
            )
        if not self._run:
            raise ValueError(
                f"No run set. Make sure to call aiplatform.init(experiment='my-experiment', "
                f"run='my-run') or aiplatform.set_run('my-run') before trying to {method_name}. "
            )


metadata_service = _MetadataService()
