# -*- coding: utf-8 -*-

# Copyright 2023 Google LLC
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

import os
import copy
from importlib import reload
from unittest import TestCase, mock
from unittest.mock import patch, call

import numpy as np
from sklearn.linear_model import LinearRegression

import pytest
from google.api_core import exceptions
from google.api_core import operation
from google.auth import credentials

import google.cloud.aiplatform.metadata.constants
from google.cloud.aiplatform.metadata.schema.google import (
    artifact_schema as google_artifact_schema,
)
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform_v1 import (
    AddContextArtifactsAndExecutionsResponse,
    LineageSubgraph,
    Artifact as GapicArtifact,
    Context as GapicContext,
    Execution as GapicExecution,
    JobServiceClient,
    MetadataServiceClient,
    AddExecutionEventsResponse,
    MetadataStore as GapicMetadataStore,
    TensorboardServiceClient,
)
from google.cloud.aiplatform.compat.types import event as gca_event
from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.compat.types import (
    tensorboard_data as gca_tensorboard_data,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard as gca_tensorboard,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_experiment as gca_tensorboard_experiment,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_run as gca_tensorboard_run,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series as gca_tensorboard_time_series,
)
from google.cloud.aiplatform.metadata import constants
from google.cloud.aiplatform.metadata import experiment_resources
from google.cloud.aiplatform.metadata import experiment_run_resource
from google.cloud.aiplatform.metadata import metadata
from google.cloud.aiplatform.metadata import metadata_store
from google.cloud.aiplatform.metadata import utils as metadata_utils
from google.cloud.aiplatform.tensorboard import tensorboard_resource

from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import _ipython_utils

import constants as test_constants

_TEST_PROJECT = "test-project"
_TEST_OTHER_PROJECT = "test-project-1"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXPERIMENT_DESCRIPTION = "test-experiment-description"
_TEST_OTHER_EXPERIMENT_DESCRIPTION = "test-other-experiment-description"
_TEST_PIPELINE = _TEST_EXPERIMENT
_TEST_RUN = "run-1"
_TEST_OTHER_RUN = "run-2"
_TEST_DISPLAY_NAME = "test-display-name"
_TEST_CREDENTIALS = mock.Mock(
    spec=credentials.AnonymousCredentials(),
    universe_domain="googleapis.com",
)
_TEST_BUCKET_NAME = "gs://test-bucket"

# resource attributes
_TEST_METADATA = {"test-param1": 1, "test-param2": "test-value", "test-param3": True}

# metadataStore
_TEST_METADATASTORE = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)

# context
_TEST_CONTEXT_ID = _TEST_EXPERIMENT
_TEST_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_CONTEXT_ID}"

# execution
_TEST_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}"
_TEST_EXECUTION_NAME = f"{_TEST_PARENT}/executions/{_TEST_EXECUTION_ID}"
_TEST_OTHER_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_OTHER_RUN}"
_TEST_OTHER_EXECUTION_NAME = f"{_TEST_PARENT}/executions/{_TEST_OTHER_EXECUTION_ID}"
_TEST_SCHEMA_TITLE = "test.Schema"

_TEST_EXECUTION = GapicExecution(
    name=_TEST_EXECUTION_NAME,
    schema_title=_TEST_SCHEMA_TITLE,
    display_name=_TEST_DISPLAY_NAME,
    metadata=_TEST_METADATA,
    state=GapicExecution.State.RUNNING,
)

# artifact
_TEST_ARTIFACT_ID = f"{_TEST_EXPERIMENT}-{_TEST_RUN}-metrics"
_TEST_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_ARTIFACT_ID}"
_TEST_OTHER_ARTIFACT_ID = f"{_TEST_EXPERIMENT}-{_TEST_OTHER_RUN}-metrics"
_TEST_OTHER_ARTIFACT_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_OTHER_ARTIFACT_ID}"
_TEST_MODEL_ID = "test-model"
_TEST_MODEL_NAME = f"{_TEST_PARENT}/artifacts/{_TEST_MODEL_ID}"

# parameters
_TEST_PARAM_KEY_1 = "learning_rate"
_TEST_PARAM_KEY_2 = "dropout"
_TEST_PARAMS = {_TEST_PARAM_KEY_1: 0.01, _TEST_PARAM_KEY_2: 0.2}
_TEST_OTHER_PARAMS = {_TEST_PARAM_KEY_1: 0.02, _TEST_PARAM_KEY_2: 0.3}

# metrics
_TEST_METRIC_KEY_1 = "rmse"
_TEST_METRIC_KEY_2 = "accuracy"
_TEST_METRICS = {_TEST_METRIC_KEY_1: 222, _TEST_METRIC_KEY_2: 1}
_TEST_OTHER_METRICS = {_TEST_METRIC_KEY_2: 0.9}

# classification_metrics
_TEST_CLASSIFICATION_METRICS = {
    "display_name": "my-classification-metrics",
    "labels": ["cat", "dog"],
    "matrix": [[9, 1], [1, 9]],
    "fpr": [0.1, 0.5, 0.9],
    "tpr": [0.1, 0.7, 0.9],
    "threshold": [0.9, 0.5, 0.1],
}

# schema
_TEST_WRONG_SCHEMA_TITLE = "system.WrongSchema"

# tensorboard
_TEST_DEFAULT_TENSORBOARD_NAME = "test-tensorboard-default-name"
_TEST_DEFAULT_TENSORBOARD_GCA = gca_tensorboard.Tensorboard(
    name=_TEST_DEFAULT_TENSORBOARD_NAME,
    is_default=True,
)


@pytest.fixture
def get_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.return_value = GapicMetadataStore(
            name=_TEST_METADATASTORE,
        )
        yield get_metadata_store_mock


@pytest.fixture
def get_metadata_store_mock_raise_not_found_exception():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as get_metadata_store_mock:
        get_metadata_store_mock.side_effect = [
            exceptions.NotFound("Test store not found."),
            GapicMetadataStore(
                name=_TEST_METADATASTORE,
            ),
        ]

        yield get_metadata_store_mock


@pytest.fixture
def ipython_is_available_mock():
    with patch.object(_ipython_utils, "is_ipython_available") as ipython_available_mock:
        ipython_available_mock.return_value = True
        yield ipython_available_mock


@pytest.fixture
def ipython_is_not_available_mock():
    with patch.object(
        _ipython_utils, "is_ipython_available"
    ) as ipython_not_available_mock:
        ipython_not_available_mock.return_value = False
        yield ipython_not_available_mock


@pytest.fixture
def create_metadata_store_mock():
    with patch.object(
        MetadataServiceClient, "create_metadata_store"
    ) as create_metadata_store_mock:
        create_metadata_store_lro_mock = mock.Mock(operation.Operation)
        create_metadata_store_lro_mock.result.return_value = GapicMetadataStore(
            name=_TEST_METADATASTORE,
        )
        create_metadata_store_mock.return_value = create_metadata_store_lro_mock
        yield create_metadata_store_mock


@pytest.fixture
def get_context_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            description=_TEST_EXPERIMENT_DESCRIPTION,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield get_context_mock


@pytest.fixture
def get_context_wrong_schema_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_context_wrong_schema_mock:
        get_context_wrong_schema_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            schema_title=_TEST_WRONG_SCHEMA_TITLE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield get_context_wrong_schema_mock


@pytest.fixture
def get_pipeline_context_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_pipeline_context_mock:
        get_pipeline_context_mock.return_value = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            schema_title=constants.SYSTEM_PIPELINE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_PIPELINE],
            metadata=constants.EXPERIMENT_METADATA,
        )
        yield get_pipeline_context_mock


@pytest.fixture
def get_context_not_found_mock():
    with patch.object(
        MetadataServiceClient, "get_context"
    ) as get_context_not_found_mock:
        get_context_not_found_mock.side_effect = exceptions.NotFound("test: not found")
        yield get_context_not_found_mock


_TEST_EXPERIMENT_CONTEXT = GapicContext(
    name=_TEST_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT,
    description=_TEST_EXPERIMENT_DESCRIPTION,
    schema_title=constants.SYSTEM_EXPERIMENT,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
    metadata={
        **constants.EXPERIMENT_METADATA,
        constants._BACKING_TENSORBOARD_RESOURCE_KEY: test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME,
    },
)


@pytest.fixture
def update_context_mock():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.return_value = _TEST_EXPERIMENT_CONTEXT
        yield update_context_mock


@pytest.fixture
def add_context_artifacts_and_executions_mock():
    with patch.object(
        MetadataServiceClient, "add_context_artifacts_and_executions"
    ) as add_context_artifacts_and_executions_mock:
        add_context_artifacts_and_executions_mock.return_value = (
            AddContextArtifactsAndExecutionsResponse()
        )
        yield add_context_artifacts_and_executions_mock


@pytest.fixture
def get_execution_mock():
    with patch.object(MetadataServiceClient, "get_execution") as get_execution_mock:
        get_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
        )
        yield get_execution_mock


@pytest.fixture
def get_execution_not_found_mock():
    with patch.object(
        MetadataServiceClient, "get_execution"
    ) as get_execution_not_found_mock:
        get_execution_not_found_mock.side_effect = exceptions.NotFound(
            "test: not found"
        )
        yield get_execution_not_found_mock


@pytest.fixture
def get_execution_wrong_schema_mock():
    with patch.object(
        MetadataServiceClient, "get_execution"
    ) as get_execution_wrong_schema_mock:
        get_execution_wrong_schema_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=_TEST_WRONG_SCHEMA_TITLE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
        )
        yield get_execution_wrong_schema_mock


@pytest.fixture
def update_execution_mock():
    with patch.object(
        MetadataServiceClient, "update_execution"
    ) as update_execution_mock:
        update_execution_mock.return_value = GapicExecution(
            name=_TEST_EXECUTION_NAME,
            display_name=_TEST_RUN,
            schema_title=constants.SYSTEM_RUN,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
            metadata=_TEST_PARAMS,
        )
        yield update_execution_mock


@pytest.fixture
def add_execution_events_mock():
    with patch.object(
        MetadataServiceClient, "add_execution_events"
    ) as add_execution_events_mock:
        add_execution_events_mock.return_value = AddExecutionEventsResponse()
        yield add_execution_events_mock


@pytest.fixture
def list_executions_mock():
    with patch.object(MetadataServiceClient, "list_executions") as list_executions_mock:
        list_executions_mock.return_value = [
            GapicExecution(
                name=_TEST_EXECUTION_NAME,
                display_name=_TEST_RUN,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=_TEST_PARAMS,
            ),
            GapicExecution(
                name=_TEST_OTHER_EXECUTION_NAME,
                display_name=_TEST_OTHER_RUN,
                schema_title=constants.SYSTEM_RUN,
                schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
                metadata=_TEST_OTHER_PARAMS,
            ),
        ]
        yield list_executions_mock


@pytest.fixture
def get_tensorboard_run_not_found_mock():
    with patch.object(
        TensorboardServiceClient, "get_tensorboard_run"
    ) as get_tensorboard_run_mock:
        get_tensorboard_run_mock.side_effect = [
            exceptions.NotFound(""),
            test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN,
        ]
        yield get_tensorboard_run_mock


@pytest.fixture
def list_default_tensorboard_mock():
    with patch.object(
        TensorboardServiceClient, "list_tensorboards"
    ) as list_default_tensorboard_mock:
        list_default_tensorboard_mock.side_effect = [
            [_TEST_DEFAULT_TENSORBOARD_GCA],
            [_TEST_DEFAULT_TENSORBOARD_GCA],
        ]
        yield list_default_tensorboard_mock


@pytest.fixture
def list_default_tensorboard_empty_mock():
    with patch.object(
        TensorboardServiceClient, "list_tensorboards"
    ) as list_default_tensorboard_empty_mock:
        list_default_tensorboard_empty_mock.return_value = []
        yield list_default_tensorboard_empty_mock


@pytest.fixture
def create_default_tensorboard_mock():
    with patch.object(
        tensorboard_resource.Tensorboard, "create"
    ) as create_default_tensorboard_mock:
        create_default_tensorboard_mock.return_value = _TEST_DEFAULT_TENSORBOARD_GCA
        yield create_default_tensorboard_mock


@pytest.fixture
def assign_backing_tensorboard_mock():
    with patch.object(
        experiment_resources.Experiment, "assign_backing_tensorboard"
    ) as assign_backing_tensorboard_mock:
        yield assign_backing_tensorboard_mock


@pytest.fixture
def get_or_create_default_tb_none_mock():
    with patch.object(
        metadata, "_get_or_create_default_tensorboard"
    ) as get_or_create_default_tb_none_mock:
        get_or_create_default_tb_none_mock.return_value = None
        yield get_or_create_default_tb_none_mock


@pytest.fixture
def get_tensorboard_experiment_not_found_mock():
    with patch.object(
        TensorboardServiceClient, "get_tensorboard_experiment"
    ) as get_tensorboard_experiment_mock:
        get_tensorboard_experiment_mock.side_effect = [
            exceptions.NotFound(""),
            test_constants.TensorboardConstants._TEST_TENSORBOARD_EXPERIMENT,
        ]
        yield get_tensorboard_experiment_mock


@pytest.fixture
def get_tensorboard_time_series_not_found_mock():
    with patch.object(
        TensorboardServiceClient, "get_tensorboard_time_series"
    ) as get_tensorboard_time_series_mock:
        get_tensorboard_time_series_mock.side_effect = [
            exceptions.NotFound(""),
            # test_tensorboard._TEST_TENSORBOARD_TIME_SERIES # change to time series
        ]
        yield get_tensorboard_time_series_mock


@pytest.fixture
def query_execution_inputs_and_outputs_mock():
    with patch.object(
        MetadataServiceClient, "query_execution_inputs_and_outputs"
    ) as query_execution_inputs_and_outputs_mock:
        query_execution_inputs_and_outputs_mock.side_effect = [
            LineageSubgraph(
                artifacts=[
                    GapicArtifact(
                        name=_TEST_ARTIFACT_NAME,
                        display_name=_TEST_ARTIFACT_ID,
                        schema_title=constants.SYSTEM_METRICS,
                        schema_version=constants.SCHEMA_VERSIONS[
                            constants.SYSTEM_METRICS
                        ],
                        metadata=_TEST_METRICS,
                    )
                ],
                events=[
                    gca_event.Event(
                        artifact=_TEST_ARTIFACT_NAME,
                        execution=_TEST_EXECUTION_NAME,
                        type_=gca_event.Event.Type.OUTPUT,
                    )
                ],
            ),
            LineageSubgraph(
                artifacts=[
                    GapicArtifact(
                        name=_TEST_OTHER_ARTIFACT_NAME,
                        display_name=_TEST_OTHER_ARTIFACT_ID,
                        schema_title=constants.SYSTEM_METRICS,
                        schema_version=constants.SCHEMA_VERSIONS[
                            constants.SYSTEM_METRICS
                        ],
                        metadata=_TEST_OTHER_METRICS,
                    ),
                ],
                events=[
                    gca_event.Event(
                        artifact=_TEST_OTHER_ARTIFACT_NAME,
                        execution=_TEST_OTHER_EXECUTION_NAME,
                        type_=gca_event.Event.Type.OUTPUT,
                    )
                ],
            ),
        ]
        yield query_execution_inputs_and_outputs_mock


_TEST_CLASSIFICATION_METRICS_METADATA = {
    "confusionMatrix": {
        "annotationSpecs": [{"displayName": "cat"}, {"displayName": "dog"}],
        "rows": [[9, 1], [1, 9]],
    },
    "confidenceMetrics": [
        {"confidenceThreshold": 0.9, "recall": 0.1, "falsePositiveRate": 0.1},
        {"confidenceThreshold": 0.5, "recall": 0.7, "falsePositiveRate": 0.5},
        {"confidenceThreshold": 0.1, "recall": 0.9, "falsePositiveRate": 0.9},
    ],
}

_TEST_CLASSIFICATION_METRICS_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    display_name=_TEST_CLASSIFICATION_METRICS["display_name"],
    schema_title=constants.GOOGLE_CLASSIFICATION_METRICS,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    metadata=_TEST_CLASSIFICATION_METRICS_METADATA,
    state=GapicArtifact.State.LIVE,
)


@pytest.fixture
def create_classification_metrics_artifact_mock():
    with patch.object(
        MetadataServiceClient, "create_artifact"
    ) as create_classification_metrics_artifact_mock:
        create_classification_metrics_artifact_mock.return_value = (
            _TEST_CLASSIFICATION_METRICS_ARTIFACT
        )
        yield create_classification_metrics_artifact_mock


@pytest.fixture
def get_classification_metrics_artifact_mock():
    with patch.object(
        MetadataServiceClient, "get_artifact"
    ) as get_classification_metrics_artifact_mock:
        get_classification_metrics_artifact_mock.return_value = (
            _TEST_CLASSIFICATION_METRICS_ARTIFACT
        )
        yield get_classification_metrics_artifact_mock


@pytest.fixture
def get_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        yield get_artifact_mock


@pytest.fixture
def get_artifact_mock_with_metadata():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
            metadata={
                google.cloud.aiplatform.metadata.constants._VERTEX_EXPERIMENT_TRACKING_LABEL: True,
                constants.GCP_ARTIFACT_RESOURCE_NAME_KEY: test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN_NAME,
                constants._STATE_KEY: gca_execution.Execution.State.RUNNING,
            },
        )
        yield get_artifact_mock


@pytest.fixture
def get_artifact_not_found_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.side_effect = exceptions.NotFound("")
        yield get_artifact_mock


@pytest.fixture
def get_artifact_wrong_schema_mock():
    with patch.object(
        MetadataServiceClient, "get_artifact"
    ) as get_artifact_wrong_schema_mock:
        get_artifact_wrong_schema_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=_TEST_WRONG_SCHEMA_TITLE,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
        )
        yield get_artifact_wrong_schema_mock


@pytest.fixture
def update_artifact_mock():
    with patch.object(MetadataServiceClient, "update_artifact") as update_artifact_mock:
        update_artifact_mock.return_value = GapicArtifact(
            name=_TEST_ARTIFACT_NAME,
            display_name=_TEST_ARTIFACT_ID,
            schema_title=constants.SYSTEM_METRICS,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_METRICS],
            metadata=_TEST_METRICS,
        )
        yield update_artifact_mock


def _assert_frame_equal_with_sorted_columns(dataframe_1, dataframe_2):
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "Pandas is not installed and is required to test the get_experiment_df/pipeline_df method. "
            'Please install the SDK using "pip install google-cloud-aiplatform[full]"'
        )

    pd.testing.assert_frame_equal(
        dataframe_1.sort_index(axis=1), dataframe_2.sort_index(axis=1), check_names=True
    )


@pytest.fixture
def mock_storage_blob_upload_from_filename():
    with patch(
        "google.cloud.storage.Blob.upload_from_filename"
    ) as mock_blob_upload_from_filename, patch(
        "google.cloud.storage.Bucket.exists", return_value=True
    ):
        yield mock_blob_upload_from_filename


_TEST_EXPERIMENT_MODEL_ARTIFACT = GapicArtifact(
    name=_TEST_MODEL_NAME,
    display_name=_TEST_DISPLAY_NAME,
    schema_title=constants.GOOGLE_EXPERIMENT_MODEL,
    schema_version=constants._DEFAULT_SCHEMA_VERSION,
    state=GapicArtifact.State.LIVE,
)


@pytest.fixture
def create_experiment_model_artifact_mock():
    with patch.object(
        MetadataServiceClient, "create_artifact"
    ) as create_experiment_model_artifact_mock:
        create_experiment_model_artifact_mock.return_value = (
            _TEST_EXPERIMENT_MODEL_ARTIFACT
        )
        yield create_experiment_model_artifact_mock


@pytest.fixture
def get_experiment_model_artifact_mock():
    with patch.object(
        MetadataServiceClient, "get_artifact"
    ) as get_experiment_model_artifact_mock:
        get_experiment_model_artifact_mock.return_value = (
            _TEST_EXPERIMENT_MODEL_ARTIFACT
        )
        yield get_experiment_model_artifact_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestMetadata:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("get_pipeline_context_mock")
    def test_get_pipeline_df(
        self, list_executions_mock, query_execution_inputs_and_outputs_mock
    ):
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "Pandas is not installed and is required to test the get_pipeline_df method. "
                'Please install the SDK using "pip install google-cloud-aiplatform[full]"'
            )
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        pipeline_df = aiplatform.get_pipeline_df(_TEST_PIPELINE)

        expected_filter = metadata_utils._make_filter_string(
            schema_title=constants.SYSTEM_RUN, in_context=[_TEST_CONTEXT_NAME]
        )

        list_executions_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "filter": expected_filter}
        )
        query_execution_inputs_and_outputs_mock.assert_has_calls(
            [
                call(execution=_TEST_EXECUTION_NAME),
                call(execution=_TEST_OTHER_EXECUTION_NAME),
            ]
        )
        pipeline_df_truth = pd.DataFrame(
            [
                {
                    "pipeline_name": _TEST_PIPELINE,
                    "run_name": _TEST_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: 0.01,
                    "param.%s" % _TEST_PARAM_KEY_2: 0.2,
                    "metric.%s" % _TEST_METRIC_KEY_1: 222,
                    "metric.%s" % _TEST_METRIC_KEY_2: 1,
                },
                {
                    "pipeline_name": _TEST_PIPELINE,
                    "run_name": _TEST_OTHER_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: 0.02,
                    "param.%s" % _TEST_PARAM_KEY_2: 0.3,
                    "metric.%s" % _TEST_METRIC_KEY_2: 0.9,
                },
            ]
        )

        _assert_frame_equal_with_sorted_columns(pipeline_df, pipeline_df_truth)

    @pytest.mark.usefixtures("get_context_not_found_mock")
    def test_get_pipeline_df_not_exist(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(exceptions.NotFound):
            aiplatform.get_pipeline_df(_TEST_PIPELINE)

    @pytest.mark.usefixtures("get_context_mock")
    def test_get_pipeline_df_wrong_schema(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(ValueError):
            aiplatform.get_pipeline_df(_TEST_PIPELINE)


_TEST_EXPERIMENT_RUN_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_EXECUTION_ID}"
_TEST_OTHER_EXPERIMENT_RUN_CONTEXT_NAME = (
    f"{_TEST_PARENT}/contexts/{_TEST_OTHER_EXECUTION_ID}"
)

_EXPERIMENT_MOCK = GapicContext(
    name=_TEST_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT,
    description=_TEST_EXPERIMENT_DESCRIPTION,
    schema_title=constants.SYSTEM_EXPERIMENT,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
    metadata={**constants.EXPERIMENT_METADATA},
)

_EXPERIMENT_RUN_MOCK = GapicContext(
    name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
    display_name=_TEST_RUN,
    schema_title=constants.SYSTEM_EXPERIMENT_RUN,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT_RUN],
    metadata={
        constants._PARAM_KEY: {},
        constants._METRIC_KEY: {},
        constants._STATE_KEY: gca_execution.Execution.State.RUNNING.name,
    },
)

_EXPERIMENT_RUN_EMPTY_METADATA_MOCK = GapicContext(
    name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
    display_name=_TEST_RUN,
    schema_title=constants.SYSTEM_EXPERIMENT_RUN,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT_RUN],
    metadata={},
)

_EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
_EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT.parent_contexts = [_TEST_CONTEXT_NAME]
_EXPERIMENT_RUN_EMPTY_METADATA_MOCK_WITH_PARENT_EXPERIMENT = copy.deepcopy(
    _EXPERIMENT_RUN_EMPTY_METADATA_MOCK
)
_EXPERIMENT_RUN_EMPTY_METADATA_MOCK_WITH_PARENT_EXPERIMENT.parent_contexts = [
    _TEST_CONTEXT_NAME
]

_TEST_CUSTOM_JOB_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/customJobs/12345"
)
_TEST_CUSTOM_JOB_CONSOLE_URI = "test-custom-job-console-uri"

_EXPERIMENT_RUN_MOCK_WITH_CUSTOM_JOBS = copy.deepcopy(
    _EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT
)
_EXPERIMENT_RUN_MOCK_WITH_CUSTOM_JOBS.metadata[constants._CUSTOM_JOB_KEY] = [
    {
        constants._CUSTOM_JOB_RESOURCE_NAME: _TEST_CUSTOM_JOB_NAME,
        constants._CUSTOM_JOB_CONSOLE_URI: _TEST_CUSTOM_JOB_CONSOLE_URI,
    },
]


@pytest.fixture
def get_experiment_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = _EXPERIMENT_MOCK
        yield get_context_mock


@pytest.fixture
def get_experiment_not_found_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = exceptions.NotFound("test: not found")
        yield get_context_mock


@pytest.fixture
def get_experiment_run_run_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK,
            _EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT,
        ]

        yield get_context_mock


@pytest.fixture
def get_experiment_run_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT,
        ]

        yield get_context_mock


@pytest.fixture
def get_empty_experiment_run_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_EMPTY_METADATA_MOCK_WITH_PARENT_EXPERIMENT,
        ]

        yield get_context_mock


@pytest.fixture
def get_experiment_run_with_custom_jobs_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK_WITH_CUSTOM_JOBS,
        ]

        yield get_context_mock


@pytest.fixture
def get_experiment_run_not_found_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.side_effect = [
            _EXPERIMENT_MOCK,
            exceptions.NotFound("test: not found"),
        ]

        yield get_context_mock


@pytest.fixture
def create_experiment_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.side_effect = [_TEST_EXPERIMENT_CONTEXT]
        yield create_context_mock


@pytest.fixture
def create_experiment_run_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.side_effect = [_EXPERIMENT_RUN_MOCK]
        yield create_context_mock


@pytest.fixture
def update_experiment_run_context_to_running():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.side_effect = [_EXPERIMENT_RUN_MOCK]
        yield update_context_mock


@pytest.fixture
def create_execution_mock():
    with patch.object(
        MetadataServiceClient, "create_execution"
    ) as create_execution_mock:
        create_execution_mock.side_effect = [_TEST_EXECUTION]
        yield create_execution_mock


@pytest.fixture
def update_context_mock_v2():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.side_effect = [
            # experiment run
            GapicContext(
                name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
                display_name=_TEST_RUN,
                schema_title=constants.SYSTEM_EXPERIMENT_RUN,
                schema_version=constants.SCHEMA_VERSIONS[
                    constants.SYSTEM_EXPERIMENT_RUN
                ],
                metadata={**constants.EXPERIMENT_METADATA},
            ),
            # experiment run
            GapicContext(
                name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
                display_name=_TEST_RUN,
                schema_title=constants.SYSTEM_EXPERIMENT_RUN,
                schema_version=constants.SCHEMA_VERSIONS[
                    constants.SYSTEM_EXPERIMENT_RUN
                ],
                metadata=constants.EXPERIMENT_METADATA,
                parent_contexts=[_TEST_CONTEXT_NAME],
            ),
        ]

        yield update_context_mock


@pytest.fixture
def list_contexts_mock():
    with patch.object(MetadataServiceClient, "list_contexts") as list_contexts_mock:
        list_contexts_mock.return_value = [
            GapicContext(
                name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
                display_name=_TEST_RUN,
                schema_title=constants.SYSTEM_EXPERIMENT_RUN,
                schema_version=constants.SCHEMA_VERSIONS[
                    constants.SYSTEM_EXPERIMENT_RUN
                ],
                metadata=constants.EXPERIMENT_METADATA,
                parent_contexts=[_TEST_CONTEXT_NAME],
            ),
            GapicContext(
                name=_TEST_OTHER_EXPERIMENT_RUN_CONTEXT_NAME,
                display_name=_TEST_OTHER_RUN,
                schema_title=constants.SYSTEM_EXPERIMENT_RUN,
                schema_version=constants.SCHEMA_VERSIONS[
                    constants.SYSTEM_EXPERIMENT_RUN
                ],
                metadata=constants.EXPERIMENT_METADATA,
                parent_contexts=[_TEST_CONTEXT_NAME],
            ),
        ]
        yield list_contexts_mock


@pytest.fixture
def add_context_children_mock():
    with patch.object(
        MetadataServiceClient, "add_context_children"
    ) as add_context_children_mock:
        yield add_context_children_mock


@pytest.fixture
def get_custom_job_mock():
    with patch.object(JobServiceClient, "get_custom_job") as get_custom_job_mock:
        yield get_custom_job_mock


_EXPERIMENT_RUN_MOCK_POPULATED_1 = copy.deepcopy(
    _EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT
)
_EXPERIMENT_RUN_MOCK_POPULATED_1.metadata[constants._PARAM_KEY].update(_TEST_PARAMS)
_EXPERIMENT_RUN_MOCK_POPULATED_1.metadata[constants._METRIC_KEY].update(_TEST_METRICS)
_EXPERIMENT_RUN_MOCK_POPULATED_2 = copy.deepcopy(
    _EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT
)
_EXPERIMENT_RUN_MOCK_POPULATED_2.display_name = _TEST_OTHER_RUN
_EXPERIMENT_RUN_MOCK_POPULATED_2.metadata[constants._PARAM_KEY].update(
    _TEST_OTHER_PARAMS
)
_EXPERIMENT_RUN_MOCK_POPULATED_2.metadata[constants._METRIC_KEY].update(
    _TEST_OTHER_METRICS
)

_TEST_PIPELINE_RUN_ID = "test-pipeline-run"
_TEST_PIPELINE_RUN_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_PIPELINE_RUN_ID}"

_TEST_PIPELINE_CONTEXT = GapicContext(
    name=_TEST_PIPELINE_RUN_CONTEXT_NAME,
    display_name=_TEST_PIPELINE_RUN_ID,
    schema_title=constants.SYSTEM_PIPELINE_RUN,
    parent_contexts=[_TEST_CONTEXT_NAME],
)


@pytest.fixture()
def list_context_mock_for_experiment_dataframe_mock():
    with patch.object(MetadataServiceClient, "list_contexts") as list_context_mock:
        list_context_mock.side_effect = [
            # experiment runs
            [
                _EXPERIMENT_RUN_MOCK_POPULATED_1,
                _EXPERIMENT_RUN_MOCK_POPULATED_2,
                _TEST_PIPELINE_CONTEXT,
            ],
            # pipeline runs
            [],
        ]
        yield list_context_mock


_TEST_LEGACY_METRIC_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    schema_title=constants.SYSTEM_METRICS,
    metadata=_TEST_METRICS,
)

_TEST_PIPELINE_METRIC_ARTIFACT = GapicArtifact(
    name=_TEST_ARTIFACT_NAME,
    schema_title=constants.SYSTEM_METRICS,
    metadata={key: value + 1 for key, value in _TEST_METRICS.items()},
)


@pytest.fixture()
def list_artifact_mock_for_experiment_dataframe():
    with patch.object(MetadataServiceClient, "list_artifacts") as list_artifacts_mock:
        list_artifacts_mock.side_effect = [
            # pipeline run metric artifact
            [_TEST_PIPELINE_METRIC_ARTIFACT],
        ]
        yield list_artifacts_mock


_TEST_PIPELINE_SYSTEM_RUN_EXECUTION = GapicExecution(
    name=_TEST_EXECUTION_NAME,
    schema_title=constants.SYSTEM_RUN,
    state=gca_execution.Execution.State.RUNNING,
    metadata={
        f"input:{_TEST_PARAM_KEY_1}": _TEST_PARAMS[_TEST_PARAM_KEY_1] + 1,
        f"input:{_TEST_PARAM_KEY_2}": _TEST_PARAMS[_TEST_PARAM_KEY_2] + 1,
        # This is automatically logged by the pipeline run but will not be
        # shown in experiment
        "vertex-ai-pipelines-artifact-argument-binding": {
            "output:trainer-metrics": ["artifact-path"]
        },
    },
)

_TEST_LEGACY_SYSTEM_RUN_EXECUTION = GapicExecution(
    name=_TEST_EXECUTION_NAME,
    display_name=_TEST_RUN,
    schema_title=constants.SYSTEM_RUN,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_RUN],
    metadata=_TEST_PARAMS,
)


# backward compatibility
@pytest.fixture()
def list_executions_mock_for_experiment_dataframe():
    with patch.object(MetadataServiceClient, "list_executions") as list_executions_mock:
        list_executions_mock.side_effect = [
            # legacy system.run execution
            [_TEST_LEGACY_SYSTEM_RUN_EXECUTION],
            # pipeline system.run execution
            [_TEST_PIPELINE_SYSTEM_RUN_EXECUTION],
        ]
        yield list_executions_mock


@pytest.fixture
def get_tensorboard_run_artifact_not_found_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.side_effect = exceptions.NotFound("")
        yield get_artifact_mock


_TEST_LEGACY_METRIC_ARTIFACT

_TEST_TENSORBOARD_RUN_ARTIFACT = GapicArtifact(
    name=experiment_run_resource.ExperimentRun._tensorboard_run_id(
        _TEST_EXPERIMENT_RUN_CONTEXT_NAME
    ),
    uri="https://us-central1-aiplatform.googleapis.com/v1/projects/test-project/locations/us-central1/tensorboards/1028944691210842416/experiments/test-experiment/runs/test-run",
    schema_title=google.cloud.aiplatform.metadata.constants._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_title,
    schema_version=google.cloud.aiplatform.metadata.constants._TENSORBOARD_RUN_REFERENCE_ARTIFACT.schema_version,
    state=GapicArtifact.State.LIVE,
    metadata={
        google.cloud.aiplatform.metadata.constants._VERTEX_EXPERIMENT_TRACKING_LABEL: True,
        constants.GCP_ARTIFACT_RESOURCE_NAME_KEY: test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN_NAME,
    },
)


@pytest.fixture
def list_tensorboard_time_series_mock_empty():
    with patch.object(
        TensorboardServiceClient,
        "list_tensorboard_time_series",
    ) as list_tensorboard_time_series_mock:
        list_tensorboard_time_series_mock.side_effect = [
            [],  # initially empty
            [],
            [test_constants.TensorboardConstants._TEST_TENSORBOARD_TIME_SERIES],
        ]
        yield list_tensorboard_time_series_mock


@pytest.fixture
def create_tensorboard_run_artifact_mock():
    with patch.object(MetadataServiceClient, "create_artifact") as create_artifact_mock:
        create_artifact_mock.side_effect = [_TEST_TENSORBOARD_RUN_ARTIFACT]
        yield create_artifact_mock


@pytest.fixture
def get_tensorboard_run_artifact_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.side_effect = [
            _TEST_TENSORBOARD_RUN_ARTIFACT,
            exceptions.NotFound(""),
            _TEST_LEGACY_METRIC_ARTIFACT,
        ]
        yield get_artifact_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestExperiments:
    def setup_method(self):
        reload(initializer)
        reload(metadata)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
    )
    def test_init_experiment_with_ipython_environment(
        self,
        list_default_tensorboard_mock,
        assign_backing_tensorboard_mock,
        ipython_is_available_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
    )
    def test_init_experiment_with_no_ipython_environment(
        self,
        list_default_tensorboard_mock,
        assign_backing_tensorboard_mock,
        ipython_is_not_available_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

    @pytest.mark.usefixtures("get_or_create_default_tb_none_mock")
    def test_init_experiment_with_existing_metadataStore_and_context(
        self, get_metadata_store_mock, get_experiment_run_run_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

        get_metadata_store_mock.assert_called_once_with(
            name=_TEST_METADATASTORE, retry=base._DEFAULT_RETRY
        )
        get_experiment_run_run_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
    )
    def test_init_experiment_with_default_tensorboard(
        self, list_default_tensorboard_mock, assign_backing_tensorboard_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

        list_default_tensorboard_mock.assert_called_once_with(
            request={
                "parent": f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                "filter": "is_default=true",
            }
        )
        assign_backing_tensorboard_mock.assert_called_once()

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
    )
    def test_init_experiment_tensorboard_false_doesNotSet_backing_tensorboard(
        self, list_default_tensorboard_mock, assign_backing_tensorboard_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=False,
        )

        list_default_tensorboard_mock.assert_not_called()
        assign_backing_tensorboard_mock.assert_not_called()

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
    )
    def test_init_experiment_tensorboard_true_sets_backing_tensorboard(
        self, list_default_tensorboard_mock, assign_backing_tensorboard_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=True,
        )

        list_default_tensorboard_mock.assert_called()
        assign_backing_tensorboard_mock.assert_called()

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
    )
    def test_init_experiment_tensorboard_none_sets_backing_tensorboard(
        self, list_default_tensorboard_mock, assign_backing_tensorboard_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=None,
        )

        list_default_tensorboard_mock.assert_called()
        assign_backing_tensorboard_mock.assert_called()

    @pytest.mark.usefixtures("get_metadata_store_mock")
    def test_create_experiment(self, create_experiment_context_mock):
        exp = aiplatform.Experiment.create(
            experiment_name=_TEST_EXPERIMENT,
            description=_TEST_EXPERIMENT_DESCRIPTION,
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        _TRUE_CONTEXT = copy.deepcopy(_TEST_EXPERIMENT_CONTEXT)
        _TRUE_CONTEXT.name = None
        _TRUE_CONTEXT.metadata.pop("backing_tensorboard_resource")

        create_experiment_context_mock.assert_called_once_with(
            parent=_TEST_PARENT, context=_TRUE_CONTEXT, context_id=_TEST_EXPERIMENT
        )

        assert exp._metadata_context.gca_resource == _TEST_EXPERIMENT_CONTEXT

    @pytest.mark.usefixtures(
        "get_or_create_default_tb_none_mock",
    )
    def test_init_experiment_with_credentials(
        self,
        get_metadata_store_mock,
        get_experiment_run_run_mock,
    ):
        creds = credentials.AnonymousCredentials()

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            credentials=creds,
        )

        assert (
            metadata._experiment_tracker._experiment._metadata_context.api_client._transport._credentials
            == creds
        )

        get_metadata_store_mock.assert_called_once_with(
            name=_TEST_METADATASTORE, retry=base._DEFAULT_RETRY
        )
        get_experiment_run_run_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_init_and_get_metadata_store_with_credentials(
        self, get_metadata_store_mock
    ):
        creds = credentials.AnonymousCredentials()

        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, credentials=creds
        )

        store = metadata_store._MetadataStore.get_or_create()

        assert store.api_client._transport._credentials == creds

    @pytest.mark.usefixtures(
        "get_metadata_store_mock_raise_not_found_exception",
        "create_metadata_store_mock",
    )
    def test_init_and_get_then_create_metadata_store_with_credentials(
        self,
    ):
        creds = credentials.AnonymousCredentials()

        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, credentials=creds
        )

        store = metadata_store._MetadataStore.get_or_create()

        assert store.api_client._transport._credentials == creds

    @pytest.mark.usefixtures("get_or_create_default_tb_none_mock")
    def test_init_experiment_with_existing_description(
        self, get_metadata_store_mock, get_experiment_run_run_mock
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_description=_TEST_EXPERIMENT_DESCRIPTION,
        )

        get_metadata_store_mock.assert_called_once_with(
            name=_TEST_METADATASTORE, retry=base._DEFAULT_RETRY
        )
        get_experiment_run_run_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_run_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_init_experiment_without_existing_description(
        self,
        update_context_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_description=_TEST_OTHER_EXPERIMENT_DESCRIPTION,
        )

        experiment_context = GapicContext(
            name=_TEST_CONTEXT_NAME,
            display_name=_TEST_EXPERIMENT,
            description=_TEST_OTHER_EXPERIMENT_DESCRIPTION,
            schema_title=constants.SYSTEM_EXPERIMENT,
            schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
            metadata=constants.EXPERIMENT_METADATA,
        )

        update_context_mock.assert_called_once_with(context=experiment_context)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_mock",
        "update_experiment_run_context_to_running",
        "get_tensorboard_run_artifact_not_found_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_init_experiment_reset(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN, resume=True)

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        assert metadata._experiment_tracker.experiment_name == _TEST_EXPERIMENT
        assert metadata._experiment_tracker.experiment_run.name == _TEST_RUN

        aiplatform.init(project=_TEST_OTHER_PROJECT, location=_TEST_LOCATION)

        assert metadata._experiment_tracker.experiment_name is None
        assert metadata._experiment_tracker.experiment_run is None

    @pytest.mark.usefixtures("get_metadata_store_mock", "get_context_wrong_schema_mock")
    def test_init_experiment_wrong_schema(self):
        with pytest.raises(ValueError):
            aiplatform.init(
                project=_TEST_PROJECT,
                location=_TEST_LOCATION,
                experiment=_TEST_EXPERIMENT,
            )

    @pytest.mark.usefixtures("get_metadata_store_mock", "get_experiment_mock")
    def test_init_experiment_from_env(self):
        os.environ["AIP_EXPERIMENT_NAME"] = _TEST_EXPERIMENT

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        exp = metadata._experiment_tracker.experiment
        assert exp.name == _TEST_EXPERIMENT

        del os.environ["AIP_EXPERIMENT_NAME"]

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
    )
    def test_start_run_from_env_experiment(
        self,
        get_experiment_mock,
        create_experiment_run_context_mock,
        add_context_children_mock,
    ):
        os.environ["AIP_EXPERIMENT_NAME"] = _TEST_EXPERIMENT

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        aiplatform.start_run(_TEST_RUN)

        get_experiment_mock.assert_called_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

        _TRUE_CONTEXT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
        _TRUE_CONTEXT.name = None

        create_experiment_run_context_mock.assert_called_with(
            parent=_TEST_METADATASTORE,
            context=_TRUE_CONTEXT,
            context_id=_EXPERIMENT_RUN_MOCK.name.split("/")[-1],
        )

        add_context_children_mock.assert_called_with(
            context=_EXPERIMENT_MOCK.name, child_contexts=[_EXPERIMENT_RUN_MOCK.name]
        )

        del os.environ["AIP_EXPERIMENT_NAME"]

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_mock",
        "get_tensorboard_run_artifact_not_found_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_init_experiment_run_from_env_run_name(self):
        os.environ["AIP_EXPERIMENT_RUN_NAME"] = _TEST_RUN

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

        run = metadata._experiment_tracker.experiment_run
        assert run.name == _TEST_RUN

        del os.environ["AIP_EXPERIMENT_RUN_NAME"]

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_run_mock",
        "get_tensorboard_run_artifact_not_found_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_init_experiment_run_from_env_run_resource_name(self):
        os.environ["AIP_EXPERIMENT_RUN_NAME"] = _TEST_EXPERIMENT_RUN_CONTEXT_NAME

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

        run = metadata._experiment_tracker.experiment_run
        assert run.name == _TEST_RUN

        del os.environ["AIP_EXPERIMENT_RUN_NAME"]

    def test_get_experiment(self, get_experiment_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        exp = aiplatform.Experiment.get(_TEST_EXPERIMENT)

        assert exp.name == _TEST_EXPERIMENT
        get_experiment_mock.assert_called_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    def test_get_experiment_not_found(self, get_experiment_not_found_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        exp = aiplatform.Experiment.get(_TEST_EXPERIMENT)

        assert exp is None
        get_experiment_not_found_mock.assert_called_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock", "get_tensorboard_run_artifact_not_found_mock"
    )
    def test_get_experiment_run(self, get_experiment_run_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        run = aiplatform.ExperimentRun.get(_TEST_RUN, experiment=_TEST_EXPERIMENT)

        assert run.name == _TEST_RUN
        get_experiment_run_mock.assert_called_with(
            name=f"{_TEST_CONTEXT_NAME}-{_TEST_RUN}", retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_tensorboard_run_artifact_not_found_mock",
        "get_execution_not_found_mock",
    )
    def test_get_experiment_run_not_found(self, get_experiment_run_not_found_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        run = aiplatform.ExperimentRun.get(_TEST_RUN, experiment=_TEST_EXPERIMENT)

        assert run is None
        get_experiment_run_not_found_mock.assert_called_with(
            name=f"{_TEST_CONTEXT_NAME}-{_TEST_RUN}", retry=base._DEFAULT_RETRY
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock", "get_or_create_default_tb_none_mock"
    )
    def test_start_run(
        self,
        get_experiment_mock,
        create_experiment_run_context_mock,
        add_context_children_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)

        get_experiment_mock.assert_called_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

        _TRUE_CONTEXT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
        _TRUE_CONTEXT.name = None

        create_experiment_run_context_mock.assert_called_with(
            parent=_TEST_METADATASTORE,
            context=_TRUE_CONTEXT,
            context_id=_EXPERIMENT_RUN_MOCK.name.split("/")[-1],
        )

        add_context_children_mock.assert_called_with(
            context=_EXPERIMENT_MOCK.name, child_contexts=[_EXPERIMENT_RUN_MOCK.name]
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_start_run_fails_when_run_name_too_long(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )

        run_name_too_long = "".join(
            "a"
            for _ in range(
                constants._EXPERIMENT_RUN_MAX_LENGTH + 2 - len(_TEST_EXPERIMENT)
            )
        )

        with pytest.raises(ValueError):
            aiplatform.start_run(run_name_too_long)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_params(
        self,
        update_context_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)
        aiplatform.log_params(_TEST_PARAMS)

        _TRUE_CONTEXT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
        _TRUE_CONTEXT.metadata[constants._PARAM_KEY].update(_TEST_PARAMS)

        update_context_mock.assert_called_once_with(context=_TRUE_CONTEXT)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_metrics(self, update_context_mock):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)
        aiplatform.log_metrics(_TEST_METRICS)

        _TRUE_CONTEXT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
        _TRUE_CONTEXT.metadata[constants._METRIC_KEY].update(_TEST_METRICS)

        update_context_mock.assert_called_once_with(context=_TRUE_CONTEXT)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_classification_metrics(
        self,
        create_classification_metrics_artifact_mock,
        get_classification_metrics_artifact_mock,
        add_context_artifacts_and_executions_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)
        classification_metrics = aiplatform.log_classification_metrics(
            display_name=_TEST_CLASSIFICATION_METRICS["display_name"],
            labels=_TEST_CLASSIFICATION_METRICS["labels"],
            matrix=_TEST_CLASSIFICATION_METRICS["matrix"],
            fpr=_TEST_CLASSIFICATION_METRICS["fpr"],
            tpr=_TEST_CLASSIFICATION_METRICS["tpr"],
            threshold=_TEST_CLASSIFICATION_METRICS["threshold"],
        )

        expected_artifact = GapicArtifact(
            display_name=_TEST_CLASSIFICATION_METRICS["display_name"],
            schema_title=constants.GOOGLE_CLASSIFICATION_METRICS,
            schema_version=constants._DEFAULT_SCHEMA_VERSION,
            metadata=_TEST_CLASSIFICATION_METRICS_METADATA,
            state=GapicArtifact.State.LIVE,
        )
        create_classification_metrics_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=expected_artifact,
            artifact_id=None,
        )

        get_classification_metrics_artifact_mock.assert_called_once_with(
            name=_TEST_ARTIFACT_NAME, retry=base._DEFAULT_RETRY
        )
        assert isinstance(
            classification_metrics, google_artifact_schema.ClassificationMetrics
        )

        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
            artifacts=[_TEST_ARTIFACT_NAME],
            executions=None,
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "mock_storage_blob_upload_from_filename",
        "create_experiment_model_artifact_mock",
        "get_experiment_model_artifact_mock",
        "get_metadata_store_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_model(
        self,
        add_context_artifacts_and_executions_mock,
    ):
        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        model = LinearRegression()
        model.fit(train_x, train_y)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            credentials=_TEST_CREDENTIALS,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)
        aiplatform.log_model(model, _TEST_MODEL_ID)

        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
            artifacts=[_TEST_MODEL_NAME],
            executions=None,
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_tensorboard_mock",
        "get_tensorboard_run_not_found_mock",
        "get_tensorboard_experiment_not_found_mock",
        "get_artifact_not_found_mock",
        "get_tensorboard_time_series_not_found_mock",
        "list_tensorboard_time_series_mock_empty",
    )
    def test_log_time_series_metrics(
        self,
        update_context_mock,
        create_tensorboard_experiment_mock,
        create_tensorboard_run_mock,
        create_tensorboard_run_artifact_mock,
        add_context_artifacts_and_executions_mock,
        create_tensorboard_time_series_mock,
        batch_read_tensorboard_time_series_mock,
        write_tensorboard_run_data_mock,
    ):
        tb = aiplatform.Tensorboard(
            test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME
        )

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=tb,
        )

        update_context_mock.assert_called_once_with(context=_TEST_EXPERIMENT_CONTEXT)

        aiplatform.start_run(_TEST_RUN)
        timestamp = utils.get_timestamp_proto()
        aiplatform.log_time_series_metrics(_TEST_OTHER_METRICS, wall_time=timestamp)

        create_tensorboard_experiment_mock.assert_called_once_with(
            parent=test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME,
            tensorboard_experiment_id=_TEST_CONTEXT_ID,
            tensorboard_experiment=gca_tensorboard_experiment.TensorboardExperiment(
                display_name=_TEST_CONTEXT_ID,
                labels=constants._VERTEX_EXPERIMENT_TB_EXPERIMENT_LABEL,
            ),
            metadata=(),
            timeout=None,
        )

        create_tensorboard_run_mock.assert_called_once_with(
            parent=test_constants.TensorboardConstants._TEST_TENSORBOARD_EXPERIMENT_NAME,
            tensorboard_run_id=_TEST_RUN,
            tensorboard_run=gca_tensorboard_run.TensorboardRun(
                display_name=_TEST_RUN,
            ),
            metadata=(),
            timeout=None,
        )

        true_tb_run_artifact = copy.deepcopy(_TEST_TENSORBOARD_RUN_ARTIFACT)
        true_tb_run_artifact.name = None

        create_tensorboard_run_artifact_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            artifact=true_tb_run_artifact,
            artifact_id=experiment_run_resource.ExperimentRun._tensorboard_run_id(
                _TEST_EXECUTION_ID
            ),
        )

        add_context_artifacts_and_executions_mock.assert_called_once_with(
            context=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
            artifacts=[_TEST_TENSORBOARD_RUN_ARTIFACT.name],
            executions=None,
        )

        create_tensorboard_time_series_mock.assert_called_with(
            parent=test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN_NAME,
            tensorboard_time_series=gca_tensorboard_time_series.TensorboardTimeSeries(
                display_name=list(_TEST_OTHER_METRICS.keys())[0],
                value_type="SCALAR",
                plugin_name="scalars",
            ),
        )

        ts_data = [
            gca_tensorboard_data.TimeSeriesData(
                tensorboard_time_series_id=test_constants.TensorboardConstants._TEST_TENSORBOARD_TIME_SERIES_ID,
                value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
                values=[
                    gca_tensorboard_data.TimeSeriesDataPoint(
                        scalar=gca_tensorboard_data.Scalar(value=value),
                        wall_time=timestamp,
                        step=2,
                    )
                ],
            )
            for value in _TEST_OTHER_METRICS.values()
        ]

        write_tensorboard_run_data_mock.assert_called_once_with(
            tensorboard_run=test_constants.TensorboardConstants._TEST_TENSORBOARD_RUN_NAME,
            time_series_data=ts_data,
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_metrics_nest_value_raises_error(self):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.start_run(_TEST_RUN)
        with pytest.raises(TypeError):
            aiplatform.log_metrics({"test": {"nested": "string"}})

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_params_nest_value_raises_error(self):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.start_run(_TEST_RUN)
        with pytest.raises(TypeError):
            aiplatform.log_params({"test": {"nested": "string"}})

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_artifact_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_start_execution_and_assign_artifact(
        self,
        create_execution_mock,
        add_execution_events_mock,
        add_context_artifacts_and_executions_mock,
        update_execution_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )
        aiplatform.start_run(_TEST_RUN)

        in_artifact = aiplatform.Artifact(_TEST_ARTIFACT_ID)
        out_artifact = aiplatform.Artifact(_TEST_ARTIFACT_ID)

        with aiplatform.start_execution(
            schema_title=_TEST_SCHEMA_TITLE,
            display_name=_TEST_DISPLAY_NAME,
            metadata=_TEST_METADATA,
        ) as exc:
            exc.assign_input_artifacts([in_artifact])
            exc.assign_output_artifacts([out_artifact])

        _created_execution = copy.deepcopy(_TEST_EXECUTION)
        _created_execution.name = None

        create_execution_mock.assert_called_once_with(
            parent=_TEST_PARENT, execution=_created_execution, execution_id=None
        )

        in_event = gca_event.Event(
            artifact=_TEST_ARTIFACT_NAME,
            type_=gca_event.Event.Type.INPUT,
        )

        out_event = gca_event.Event(
            artifact=_TEST_ARTIFACT_NAME,
            type_=gca_event.Event.Type.OUTPUT,
        )

        add_execution_events_mock.assert_has_calls(
            [
                call(execution=_TEST_EXECUTION.name, events=[in_event]),
                call(execution=_TEST_EXECUTION.name, events=[out_event]),
            ]
        )

        add_context_artifacts_and_executions_mock.assert_has_calls(
            [
                call(
                    context=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
                    artifacts=None,
                    executions=[_TEST_EXECUTION.name],
                ),
                call(
                    context=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
                    artifacts=[_TEST_ARTIFACT_NAME],
                    executions=[],
                ),
                call(
                    context=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
                    artifacts=[_TEST_ARTIFACT_NAME],
                    executions=[],
                ),
            ]
        )

        updated_execution = copy.deepcopy(_TEST_EXECUTION)
        updated_execution.state = GapicExecution.State.COMPLETE

        update_execution_mock.assert_called_once_with(execution=updated_execution)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "add_context_children_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_end_run(
        self,
        update_context_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)
        aiplatform.end_run()

        _TRUE_CONTEXT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
        _TRUE_CONTEXT.metadata[constants._STATE_KEY] = (
            gca_execution.Execution.State.COMPLETE.name
        )

        update_context_mock.assert_called_once_with(context=_TRUE_CONTEXT)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "get_pipeline_job_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_log_pipeline_job(
        self,
        add_context_children_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
        )
        aiplatform.start_run(_TEST_RUN)

        pipeline_job = aiplatform.PipelineJob.get(
            test_constants.PipelineJobConstants._TEST_PIPELINE_JOB_ID
        )
        pipeline_job.wait()

        aiplatform.log(pipeline_job=pipeline_job)

        add_context_children_mock.assert_called_with(
            context=_EXPERIMENT_RUN_MOCK.name,
            child_contexts=[
                pipeline_job.gca_resource.job_detail.pipeline_run_context.name
            ],
        )

    @pytest.mark.usefixtures(
        "get_experiment_mock",
    )
    def test_get_experiment_df_passes_experiment_variable(
        self,
        list_context_mock_for_experiment_dataframe_mock,
        list_artifact_mock_for_experiment_dataframe,
        list_executions_mock_for_experiment_dataframe,
        get_tensorboard_run_artifact_mock,
        get_tensorboard_run_mock,
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with patch.object(
            experiment_run_resource.ExperimentRun, "_query_experiment_row"
        ) as query_experiment_row_mock:
            row = experiment_resources._ExperimentRow(
                experiment_run_type=constants.SYSTEM_EXPERIMENT_RUN,
                name=_TEST_EXPERIMENT,
            )
            query_experiment_row_mock.return_value = row

            aiplatform.get_experiment_df(_TEST_EXPERIMENT)
            _, kwargs = query_experiment_row_mock.call_args_list[0]
            TestCase.assertTrue(self, kwargs["experiment"].name == _TEST_EXPERIMENT)

    @pytest.mark.skip(reason="flaky")
    @pytest.mark.usefixtures(
        "get_experiment_mock",
        "list_tensorboard_time_series_mock",
        "batch_read_tensorboard_time_series_mock",
    )
    def test_get_experiment_df(
        self,
        list_context_mock_for_experiment_dataframe_mock,
        list_artifact_mock_for_experiment_dataframe,
        list_executions_mock_for_experiment_dataframe,
        get_tensorboard_run_artifact_mock,
        get_tensorboard_run_mock,
    ):
        import pandas as pd

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        experiment_df = aiplatform.get_experiment_df(_TEST_EXPERIMENT)

        expected_filter = metadata_utils._make_filter_string(
            parent_contexts=[_TEST_CONTEXT_NAME],
            schema_title=[
                constants.SYSTEM_EXPERIMENT_RUN,
                constants.SYSTEM_PIPELINE_RUN,
            ],
        )

        list_context_mock_for_experiment_dataframe_mock.assert_called_once_with(
            request=dict(parent=_TEST_PARENT, filter=expected_filter)
        )

        expected_legacy_filter = metadata_utils._make_filter_string(
            in_context=[_TEST_CONTEXT_NAME], schema_title=[constants.SYSTEM_RUN]
        )
        expected_pipeline_filter = metadata_utils._make_filter_string(
            in_context=[_TEST_PIPELINE_CONTEXT.name], schema_title=constants.SYSTEM_RUN
        )

        list_executions_mock_for_experiment_dataframe.assert_has_calls(
            calls=[
                call(request=dict(parent=_TEST_PARENT, filter=expected_legacy_filter)),
                call(
                    request=dict(parent=_TEST_PARENT, filter=expected_pipeline_filter)
                ),
            ],
            any_order=False,
        )

        expected_filter = metadata_utils._make_filter_string(
            in_context=[_TEST_PIPELINE_CONTEXT.name],
            schema_title=[
                constants.SYSTEM_METRICS,
                constants.GOOGLE_CLASSIFICATION_METRICS,
                constants.GOOGLE_REGRESSION_METRICS,
                constants.GOOGLE_FORECASTING_METRICS,
            ],
        )

        list_artifact_mock_for_experiment_dataframe.assert_has_calls(
            calls=[call(request=dict(parent=_TEST_PARENT, filter=expected_filter))],
            any_order=False,
        )

        experiment_df_truth = pd.DataFrame(
            [
                {
                    "experiment_name": _TEST_EXPERIMENT,
                    "run_type": constants.SYSTEM_EXPERIMENT_RUN,
                    "state": gca_execution.Execution.State.RUNNING.name,
                    "run_name": _TEST_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: _TEST_PARAMS[_TEST_PARAM_KEY_1],
                    "param.%s" % _TEST_PARAM_KEY_2: _TEST_PARAMS[_TEST_PARAM_KEY_2],
                    "metric.%s" % _TEST_METRIC_KEY_1: _TEST_METRICS[_TEST_METRIC_KEY_1],
                    "metric.%s" % _TEST_METRIC_KEY_2: _TEST_METRICS[_TEST_METRIC_KEY_2],
                    "time_series_metric.accuracy": test_constants.TensorboardConstants._TEST_TENSORBOARD_TIME_SERIES_DATA.values[
                        0
                    ].scalar.value,
                },
                {
                    "experiment_name": _TEST_EXPERIMENT,
                    "run_type": constants.SYSTEM_EXPERIMENT_RUN,
                    "state": gca_execution.Execution.State.RUNNING.name,
                    "run_name": _TEST_OTHER_RUN,
                    "param.%s"
                    % _TEST_PARAM_KEY_1: _TEST_OTHER_PARAMS[_TEST_PARAM_KEY_1],
                    "param.%s"
                    % _TEST_PARAM_KEY_2: _TEST_OTHER_PARAMS[_TEST_PARAM_KEY_2],
                    "metric.%s"
                    % _TEST_METRIC_KEY_2: _TEST_OTHER_METRICS[_TEST_METRIC_KEY_2],
                },
                {
                    "experiment_name": _TEST_EXPERIMENT,
                    "run_type": constants.SYSTEM_PIPELINE_RUN,
                    "state": gca_execution.Execution.State.RUNNING.name,
                    "run_name": _TEST_PIPELINE_RUN_ID,
                    "param.%s" % _TEST_PARAM_KEY_1: _TEST_PARAMS[_TEST_PARAM_KEY_1] + 1,
                    "param.%s" % _TEST_PARAM_KEY_2: _TEST_PARAMS[_TEST_PARAM_KEY_2] + 1,
                    "metric.%s" % _TEST_METRIC_KEY_1: _TEST_METRICS[_TEST_METRIC_KEY_1]
                    + 1,
                    "metric.%s" % _TEST_METRIC_KEY_2: _TEST_METRICS[_TEST_METRIC_KEY_2]
                    + 1,
                },
                {
                    "experiment_name": _TEST_EXPERIMENT,
                    "run_type": constants.SYSTEM_RUN,
                    "state": gca_execution.Execution.State.STATE_UNSPECIFIED.name,
                    "run_name": _TEST_RUN,
                    "param.%s" % _TEST_PARAM_KEY_1: _TEST_PARAMS[_TEST_PARAM_KEY_1],
                    "param.%s" % _TEST_PARAM_KEY_2: _TEST_PARAMS[_TEST_PARAM_KEY_2],
                    "metric.%s" % _TEST_METRIC_KEY_1: _TEST_METRICS[_TEST_METRIC_KEY_1],
                    "metric.%s" % _TEST_METRIC_KEY_2: _TEST_METRICS[_TEST_METRIC_KEY_2],
                },
            ]
        )

        _assert_frame_equal_with_sorted_columns(experiment_df, experiment_df_truth)

    @pytest.mark.usefixtures("get_context_not_found_mock")
    def test_get_experiment_df_not_exist(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(exceptions.NotFound):
            aiplatform.get_experiment_df(_TEST_EXPERIMENT)

    @pytest.mark.usefixtures("get_pipeline_context_mock")
    def test_get_experiment_df_wrong_schema(self):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        with pytest.raises(ValueError):
            aiplatform.get_experiment_df(_TEST_EXPERIMENT)

    @pytest.mark.usefixtures(
        "get_tensorboard_run_artifact_not_found_mock", "get_metadata_store_mock"
    )
    def test_run_metadata_not_set(self, get_empty_experiment_run_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        run = aiplatform.ExperimentRun.get(_TEST_RUN, experiment=_TEST_EXPERIMENT)

        params = run.get_params()
        metrics = run.get_metrics()
        state = run.get_state()

        assert params == {}
        assert metrics == {}
        assert state == gca_execution.Execution.State.STATE_UNSPECIFIED.name

    @pytest.mark.usefixtures(
        "get_experiment_run_with_custom_jobs_mock",
        "get_metadata_store_mock",
        "get_tensorboard_run_artifact_not_found_mock",
    )
    def test_experiment_run_get_logged_custom_jobs(self, get_custom_job_mock):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        run = aiplatform.ExperimentRun(_TEST_RUN, experiment=_TEST_EXPERIMENT)
        jobs = run.get_logged_custom_jobs()

        assert len(jobs) == 1
        get_custom_job_mock.assert_called_once_with(
            name=_TEST_CUSTOM_JOB_NAME,
            retry=base._DEFAULT_RETRY,
        )

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "get_experiment_mock",
        "get_experiment_run_mock",
        "get_context_mock",
        "list_contexts_mock",
        "list_executions_mock",
        "get_artifact_mock_with_metadata",
        "update_context_mock",
    )
    def test_update_experiment_run_after_list(
        self,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

        experiment_run_list = aiplatform.ExperimentRun.list(experiment=_TEST_EXPERIMENT)
        experiment_run_list[0].update_state(gca_execution.Execution.State.FAILED)


class TestTensorboard:
    def test_get_or_create_default_tb_with_existing_default(
        self, list_default_tensorboard_mock
    ):
        tensorboard = metadata._get_or_create_default_tensorboard()

        list_default_tensorboard_mock.assert_called_once_with(
            request={
                "parent": f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                "filter": "is_default=true",
            }
        )
        assert tensorboard.name == _TEST_DEFAULT_TENSORBOARD_NAME

    def test_get_or_create_default_tb_no_existing_default(
        self,
        list_default_tensorboard_empty_mock,
        create_default_tensorboard_mock,
    ):
        tensorboard = metadata._get_or_create_default_tensorboard()

        list_default_tensorboard_empty_mock.assert_called_once_with(
            request={
                "parent": f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
                "filter": "is_default=true",
            }
        )
        create_default_tensorboard_mock.assert_called_once()
        assert tensorboard.name == _TEST_DEFAULT_TENSORBOARD_NAME
