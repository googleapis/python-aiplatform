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
#

import abc
from dataclasses import dataclass
import logging
from typing import Dict, List, NamedTuple, Optional, Union, Tuple, Type

from google.auth import credentials as auth_credentials

from google.cloud.aiplatform import base
from google.cloud.aiplatform.metadata import metadata, metadata_store
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata.artifact import _Artifact
from google.cloud.aiplatform.metadata.context import _Context
from google.cloud.aiplatform.metadata.execution import Execution
from google.cloud.aiplatform.metadata import resource
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform.tensorboard import tensorboard_resource

_LOGGER = base.Logger(__name__)


@dataclass
class ExperimentRow:
    """Class for representing a row in an Experiments Dataframe."""

    params: Optional[Dict[str, Union[float, int, str]]] = None
    metrics: Optional[Dict[str, Union[float, int, str]]] = None
    time_series_metrics: Optional[Dict[str, float]] = None
    experiment_run_type: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None

    def to_dict(self):
        result = {
            "run_type": self.experiment_run_type,
            "run_name": self.name,
            "state": self.state,
        }
        for prefix, field in [
            ("param", self.params),
            ("metric", self.metrics),
            ("time_series_metric", self.time_series_metrics),
        ]:
            if field:
                result.update(
                    {f"{prefix}.{key}": value for key, value in field.items()}
                )
        return result


class Experiment:
    def __init__(
        self,
        experiment_name: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):

        metadata_args = dict(
            resource_name=experiment_name,
            project=project,
            location=location,
            credentials=credentials,
        )

        with _SetLoggerLevel(resource):
            context = _Context(**metadata_args)

        if context.schema_title != constants.SYSTEM_EXPERIMENT:
            raise ValueError(
                f"Experiment name {experiment_name} has been used to create other type of resources "
                f"({context.schema_title}) in this MetadataStore, please choose a different experiment name."
            )

        self._metadata_context = context

    @property
    def name(self):
        return self._metadata_context.name

    @classmethod
    def create(
        cls,
        experiment_name: str,
        description: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Experiment":

        metadata_store._MetadataStore.ensure_default_metadata_store_exists(
            project=project,
            location=location,
            credentials=credentials
        )

        with _SetLoggerLevel(resource):
            context = _Context._create(
                resource_id=experiment_name,
                display_name=experiment_name,
                description=description,
                schema_title=constants.SYSTEM_EXPERIMENT,
                schema_version=metadata._get_experiment_schema_version(),
                metadata=constants.EXPERIMENT_METADATA,
                project=project,
                location=location,
                credentials=credentials,
            )

        return cls(experiment_name=context.resource_name, credentials=credentials)

    @classmethod
    def get_or_create(
        cls,
        experiment_name: str,
        description: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> "Experiment":

        metadata_store._MetadataStore.ensure_default_metadata_store_exists(
            project=project,
            location=location,
            credentials=credentials
        )

        with _SetLoggerLevel(resource):
            context = _Context.get_or_create(
                resource_id=experiment_name,
                display_name=experiment_name,
                description=description,
                schema_title=constants.SYSTEM_EXPERIMENT,
                schema_version=metadata._get_experiment_schema_version(),
                metadata=constants.EXPERIMENT_METADATA,
                project=project,
                location=location,
                credentials=credentials,
            )

        if context.schema_title != constants.SYSTEM_EXPERIMENT:
            raise ValueError(
                f"Experiment name {experiment_name} has been used to create other type of resources "
                f"({context.schema_title}) in this MetadataStore, please choose a different experiment name."
            )

        return cls(experiment_name=context.resource_name, credentials=credentials)

    @classmethod
    def list(
        cls,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["Experiment"]:

        filter_str = metadata_utils.make_filter_string(schema_title=constants.SYSTEM_EXPERIMENT)

        with _SetLoggerLevel(resource):
            experiment_contexts = _Context.list(
                filter=filter_str,
                project=project,
                location=location,
                credentials=credentials,
            )

        experiments = []
        for experiment_context in experiment_contexts:
            # Removes Tensorboard Experiments
            if not is_tensorboard_experiment(experiment_context):
                experiment = cls.__new__(cls)
                experiment._metadata_context = experiment_context
                experiments.append(experiment)
        return experiments

    @property
    def resource_name(self):
        return self._metadata_context.resource_name

    def delete(self, *, delete_backing_tensorboard_runs: bool=False):

        experiment_runs =_SUPPORTED_LOGGABLE_RESOURCES[_Context][constants.SYSTEM_EXPERIMENT_RUN].list(
            experiment=self)
        for experiment_run in experiment_runs:
            experiment_run.delete(delete_backing_tensorboard_run=delete_backing_tensorboard_runs)
        self._metadata_context.delete()

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

        service_request_args = dict(
            project=self._metadata_context.project,
            location=self._metadata_context.location,
            credentials=self._metadata_context.credentials,
        )

        filter_str = metadata_utils.make_filter_string(
            schema_title=list(_SUPPORTED_LOGGABLE_RESOURCES[_Context].keys()),
            parent_contexts=[self._metadata_context.resource_name]
        )
        contexts = _Context.list(filter_str, **service_request_args)

        filter_str = metadata_utils.make_filter_string(
            schema_title=list(_SUPPORTED_LOGGABLE_RESOURCES[Execution].keys()),
            in_context=[self._metadata_context.resource_name]
        )

        executions = Execution.list(filter_str, **service_request_args)

        rows = []
        for context in contexts:
            row_dict = (
                _SUPPORTED_LOGGABLE_RESOURCES[_Context][context.schema_title]
                ._query_experiment_row(context)
                .to_dict()
            )
            row_dict.update({"experiment_name": self.name})
            rows.append(row_dict)

        for execution in executions:
            row_dict = (
                _SUPPORTED_LOGGABLE_RESOURCES[Execution][execution.schema_title]
                    ._query_experiment_row(execution)
                    .to_dict()
            )
            row_dict.update({"experiment_name": self.name})
            rows.append(row_dict)

        df = pd.DataFrame(rows)

        column_name_sort_map = {
            "experiment_name": -1,
            "run_name": 1,
            "run_type": 2,
            "state": 3,
        }

        def column_sort_key(key: str) -> int:
            """Helper method to reorder columns."""
            order = column_name_sort_map.get(key)
            if order:
                return order
            elif key.startswith("param"):
                return 5
            elif key.startswith("metric"):
                return 6
            else:
                return 7

        columns = df.columns
        columns = sorted(columns, key=column_sort_key)
        df = df.reindex(columns, axis=1)

        return df

        # experiment_runs = ExperimentRun.list(experiment=self)

        # with concurrent.futures.ThreadPoolExecutor(max_workers = len(experiment_runs)) as executor:
        #     submissions = [executor.submit(run._get_pandas_row_dicts) for run in experiment_runs]
        #     experiment_runs = [submission.result() for submission in submissions]

        # df = pd.DataFrame(row for run in experiment_runs for row in run)

    def _lookup_backing_tensorboard(self) -> Optional[tensorboard_resource.Tensorboard]:
        """Returns backing tensorboard if one is set."""
        tensorboard_resource_name = self._metadata_context.metadata.get(
            "backing_tensorboard_resource"
        )

        if not tensorboard_resource_name:
            with _SetLoggerLevel(resource):
                self._metadata_context.sync_resource()
            tensorboard_resource_name = self._metadata_context.metadata.get(
                "backing_tensorboard_resource"
            )

        if tensorboard_resource_name:
            return tensorboard_resource.Tensorboard(
                tensorboard_resource_name,
                credentials=self._metadata_context.credentials,
            )

    def get_backing_tensorboard_resource(
        self,
    ) -> Optional[tensorboard_resource.Tensorboard]:
        return self._lookup_backing_tensorboard()

    def assign_backing_tensorboard(
        self, tensorboard: Union[tensorboard_resource.Tensorboard, str]
    ):
        """Assigns tensorboard as backing tensorboard to support timeseries metrics logging."""

        backing_tensorboard = self._lookup_backing_tensorboard()
        if backing_tensorboard:
            tensorboard_resource_name = tensorboard if isinstance(tensorboard, str) else tensorboard.resource_name
            if tensorboard_resource_name != backing_tensorboard.resource_name:
                raise ValueError(
                    f"Experiment {self._metadata_context.name} already associated '"
                    f"to tensorboard resource {backing_tensorboard.resource_name}"
                )

        if isinstance(tensorboard, str):
            tensorboard = tensorboard_resource.Tensorboard(
                tensorboard,
                project=self._metadata_context.project,
                location=self._metadata_context.location,
                credentials=self._metadata_context.credentials,
            )

        self._metadata_context.update(
            metadata={"backing_tensorboard_resource": tensorboard.resource_name}
        )

    def _log_experiment_loggable(self, experiment_loggable: "ExperimentLoggable"):
        """Associates a Vertex resource that can be logged to an Experiment as an Experiment Run.

        Args:
            experiment_loggable: A Vertex Resource that can be logged to an Experiment directly.
        """
        context = experiment_loggable._get_context()
        self._metadata_context.add_context_children([context])


# maps context names to their resources classes
_SUPPORTED_LOGGABLE_RESOURCES: Dict[Union[Type[_Context], Type[Execution]], Dict[str, base.VertexAiResourceNoun]] = {
    Execution: dict(), _Context: dict()
}


class _SetLoggerLevel:
    def __init__(self, module):
        self._module = module

    def __enter__(self):
        logging.getLogger(self._module.__name__).setLevel(logging.WARNING)

    def __exit__(self, exc_type, exc_value, traceback):
        logging.getLogger(self._module.__name__).setLevel(logging.INFO)


class VertexResourceWithMetadata(NamedTuple):
    resource: base.VertexAiResourceNoun
    metadata: _Artifact


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
            key = key[len(filter_prefix) :]
        column_key_to_value[".".join([metadata_type, key])] = value

    return column_key_to_value


def is_tensorboard_experiment(context: _Context) -> bool:
    """Returns True is Experiment is a Tensorboard Experiment created by CustomJob."""
    return constants.TENSORBOARD_CUSTOM_JOB_EXPERIMENT_FIELD in context.metadata


class ExperimentLoggableSchema(NamedTuple):
    title: str
    type: Union[Type[_Context], Type[Execution]] = _Context

class ExperimentLoggable(abc.ABC):
    def __init_subclass__(cls,
                          *,
                          experiment_loggable_schemas: Tuple[ExperimentLoggableSchema],
                          **kwargs):
        """Register the metadata_schema for the subclass so Experiment can use it to retrieve the associated types.

        usage:

        class PipelineJob(ExperimentLoggable(metadata_schema_title='system.PipelineRun'))

        Args:
            metadata_schema_title: The metadata scheam title for the metadata node that represents this resource.

        """
        super().__init_subclass__(**kwargs)

        for schema in experiment_loggable_schemas:
            _SUPPORTED_LOGGABLE_RESOURCES[schema.type][schema.title] = cls

    @abc.abstractmethod
    def _get_context(self) -> _Context:
        """Should return the  metadata context that represents this resource.

        The subclass should enforce this context exists.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def _query_experiment_row(cls, context: _Context) -> ExperimentRow:
        """Should returns parameters and metrics for this resource as an ExperimentRun row."""
        pass

    def _validate_experiment(self, experiment: Union[str, Experiment]):
        """Validates experiment is accessible. Can be used by subclass to throw before creating the intended resource."""

        if isinstance(experiment, str):
            try:
                Experiment.get_or_create(
                    experiment,
                    project=self.project,
                    location=self.location,
                    credentials=self.credentials,
                )
            except Exception as e:
                raise RuntimeError(
                    f"Experiment {experiment} could not be found or created. {self.__class__.__name__} not created"
                ) from e

        # TODO(confirm project and location match in the case of Experiment)

    def _associate_to_experiment(self, experiment: Union[str, Experiment]):
        """Associates this resource to the provided Experiment."""
        experiment_name = experiment if isinstance(experiment, str) else experiment.name
        _LOGGER.info(
            "Associating %s to Experiment: %s" % (self.resource_name, experiment_name)
        )

        try:
            if isinstance(experiment, str):
                experiment = Experiment.get_or_create(
                    experiment,
                    project=self.project,
                    location=self.location,
                    credentials=self.credentials,
                )
            experiment._log_experiment_loggable(self)
        except Exception as e:
            raise RuntimeError(
                f"{self.resource_name} could not be associated with Experiment {experiment.name}"
            ) from e
