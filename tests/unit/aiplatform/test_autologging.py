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

import copy
import datetime
from importlib import reload
import os
from unittest import mock
from unittest.mock import patch


from mlflow import entities as mlflow_entities
from google.cloud.aiplatform._mlflow_plugin import _vertex_mlflow_tracking
from google.cloud.aiplatform.utils import autologging_utils

import pytest
from google.api_core import exceptions


from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import base
from google.cloud.aiplatform_v1 import (
    Artifact as GapicArtifact,
    Context as GapicContext,
    Execution as GapicExecution,
    MetadataServiceClient,
    MetadataStore as GapicMetadataStore,
    TensorboardServiceClient,
)
from google.cloud.aiplatform.compat.types import execution as gca_execution
from google.cloud.aiplatform.compat.types import (
    tensorboard_run as gca_tensorboard_run,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard_time_series as gca_tensorboard_time_series,
)
from google.cloud.aiplatform.metadata import constants
import constants as test_constants

from google.cloud.aiplatform.compat.services import (
    tensorboard_service_client,
)

from google.cloud.aiplatform.compat.types import (
    tensorboard as gca_tensorboard,
)
from google.cloud.aiplatform.metadata import metadata


import test_tensorboard
import test_metadata

import numpy as np

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_OTHER_PROJECT = "test-project-1"
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_PARENT = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)
_TEST_EXPERIMENT = "test-experiment"
_TEST_OTHER_EXPERIMENT = "test-other-experiment"
_TEST_EXPERIMENT_DESCRIPTION = "test-experiment-description"
_TEST_OTHER_EXPERIMENT_DESCRIPTION = "test-other-experiment-description"
_TEST_PIPELINE = _TEST_EXPERIMENT
_TEST_RUN = "run-1"
_TEST_OTHER_RUN = "run-2"
_TEST_DISPLAY_NAME = "test-display-name"

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

# tf model autologging
_TEST_TF_EXPERIMENT_RUN_PARAMS = {
    "batch_size": "None",
    "class_weight": "None",
    "epochs": "5",
    "initial_epoch": "0",
    "max_queue_size": "10",
    "sample_weight": "None",
    "shuffle": "True",
    "steps_per_epoch": "None",
    "use_multiprocessing": "False",
    "validation_batch_size": "None",
    "validation_freq": "1",
    "validation_split": "0.0",
    "validation_steps": "None",
    "workers": "1",
}
_TEST_TF_EXPERIMENT_RUN_METRICS = {
    "accuracy": 0.0,
    "loss": 1.013,
}

# tensorboard
_TEST_TB_ID = "1028944691210842416"
_TEST_TENSORBOARD_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/tensorboards/{_TEST_TB_ID}"
)
_TEST_TB_DISPLAY_NAME = "my_tensorboard_1234"
_TEST_ENCRYPTION_KEY_NAME = test_constants.ProjectConstants._TEST_ENCRYPTION_KEY_NAME
_TEST_ENCRYPTION_SPEC = test_constants.ProjectConstants._TEST_ENCRYPTION_SPEC
_TEST_TB_NAME = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/tensorboards/{_TEST_TB_ID}"
)
_TEST_TENSORBOARD_EXPERIMENT_ID = "test-experiment"
_TEST_TENSORBOARD_EXPERIMENT_NAME = (
    f"{_TEST_TB_NAME}/experiments/{_TEST_TENSORBOARD_EXPERIMENT_ID}"
)

_TEST_TENSORBOARD_RUN_ID = "run-1"
_TEST_TENSORBOARD_RUN_NAME = (
    f"{_TEST_TENSORBOARD_EXPERIMENT_NAME}/runs/{_TEST_TENSORBOARD_RUN_ID}"
)

_TEST_TENSORBOARD_RUN = gca_tensorboard_run.TensorboardRun(
    name=_TEST_TENSORBOARD_RUN_NAME,
    display_name=_TEST_DISPLAY_NAME,
)
_TEST_TIME_SERIES_DISPLAY_NAME = "loss"
_TEST_TIME_SERIES_DISPLAY_NAME_2 = "accuracy"
_TEST_TENSORBOARD_TIME_SERIES_ID = "test-time-series"
_TEST_TENSORBOARD_TIME_SERIES_NAME = (
    f"{_TEST_TENSORBOARD_RUN_NAME}/timeSeries/{_TEST_TENSORBOARD_TIME_SERIES_ID}"
)

_TEST_TENSORBOARD_TIME_SERIES_LIST = [
    gca_tensorboard_time_series.TensorboardTimeSeries(
        name=_TEST_TENSORBOARD_TIME_SERIES_NAME,
        display_name=_TEST_TIME_SERIES_DISPLAY_NAME,
        value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
    ),
    gca_tensorboard_time_series.TensorboardTimeSeries(
        name=_TEST_TENSORBOARD_TIME_SERIES_NAME,
        display_name=_TEST_TIME_SERIES_DISPLAY_NAME_2,
        value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
    ),
]

# mlflow
_TEST_MLFLOW_TRACKING_URI = "file://my-test-tracking-uri"
_TEST_MLFLOW_CREATE_RUN_TIMESTAMP = int(datetime.datetime.now().timestamp())
_TEST_MLFLOW_RUN_ID = f"tensorflow-{_TEST_MLFLOW_CREATE_RUN_TIMESTAMP}"

_MOCK_MLFLOW_RUN_INFO = mlflow_entities.RunInfo(
    run_uuid=_TEST_MLFLOW_RUN_ID,
    run_id=_TEST_MLFLOW_RUN_ID,
    experiment_id=_TEST_EXPERIMENT,
    user_id="",
    status=gca_execution.Execution.State.RUNNING,
    start_time=1,
    end_time=2,
    lifecycle_stage=mlflow_entities.LifecycleStage.ACTIVE,
    artifact_uri="file:///tmp/",
)

_MOCK_MLFLOW_RUN_INFO_COMPLETE = mlflow_entities.RunInfo(
    run_uuid=_TEST_MLFLOW_RUN_ID,
    run_id=_TEST_MLFLOW_RUN_ID,
    experiment_id=_TEST_EXPERIMENT,
    user_id="",
    status=gca_execution.Execution.State.COMPLETE,
    start_time=1,
    end_time=2,
    lifecycle_stage=mlflow_entities.LifecycleStage.ACTIVE,
    artifact_uri="file:///tmp/",
)


_MOCK_MLFLOW_RUN_DATA = mlflow_entities.RunData(
    metrics=[
        mlflow_entities.Metric(key=k, value=v, step=0, timestamp=0)
        for k, v in _TEST_TF_EXPERIMENT_RUN_METRICS.items()
    ],
    params=[
        mlflow_entities.Param(key=k, value=v)
        for k, v in _TEST_TF_EXPERIMENT_RUN_PARAMS.items()
    ],
    tags={},
)


@pytest.fixture
def mlflow_plugin_create_run_mock():
    with patch.object(
        _vertex_mlflow_tracking._VertexMlflowTracking, "create_run"
    ) as create_vertex_run_mock:
        create_vertex_run_mock.return_value = mlflow_entities.Run(
            run_info=_MOCK_MLFLOW_RUN_INFO, run_data=_MOCK_MLFLOW_RUN_DATA
        )
        yield create_vertex_run_mock


@pytest.fixture
def mlflow_plugin_get_run_mock():
    with patch.object(
        _vertex_mlflow_tracking._VertexMlflowTracking, "get_run"
    ) as get_vertex_run_mock:
        get_vertex_run_mock.return_value = mlflow_entities.Run(
            run_info=_MOCK_MLFLOW_RUN_INFO, run_data=_MOCK_MLFLOW_RUN_DATA
        )
        yield get_vertex_run_mock


@pytest.fixture
def mlflow_plugin_update_run_info_mock():
    with patch.object(
        _vertex_mlflow_tracking._VertexMlflowTracking, "update_run_info"
    ) as update_run_mock:
        update_run_mock.return_value = _MOCK_MLFLOW_RUN_INFO_COMPLETE
        yield update_run_mock


@pytest.fixture
def mock_experiment_run():
    exp_run_mock = mock.MagicMock(aiplatform.ExperimentRun)
    exp_run_mock.run_name = _TEST_MLFLOW_RUN_ID
    exp_run_mock.experiment = _EXPERIMENT_MOCK
    return exp_run_mock


@pytest.fixture
def mlflow_plugin_run_map_mock(mock_experiment_run):
    with patch.object(
        _vertex_mlflow_tracking._VertexMlflowTracking,
        "run_map",
        new_callable=mock.PropertyMock,
    ) as run_map_mock:
        run_map_mock.return_value = {
            _TEST_MLFLOW_RUN_ID: _vertex_mlflow_tracking._RunTracker(
                autocreate=True, experiment_run=mock_experiment_run
            )
        }
        yield run_map_mock


@pytest.fixture
def mlflow_plugin_vertex_experiment_mock(mock_experiment_run):
    with patch.object(
        _vertex_mlflow_tracking._VertexMlflowTracking,
        "vertex_experiment",
        new_callable=mock.PropertyMock,
    ) as vertex_experiment_mock:
        vertex_experiment_mock.return_value = _EXPERIMENT_MOCK
        yield vertex_experiment_mock


@pytest.fixture
def get_tensorboard_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient, "get_tensorboard"
    ) as get_tensorboard_mock:
        get_tensorboard_mock.return_value = gca_tensorboard.Tensorboard(
            name=_TEST_TENSORBOARD_NAME,
            display_name=_TEST_DISPLAY_NAME,
            encryption_spec=_TEST_ENCRYPTION_SPEC,
        )
        yield get_tensorboard_mock


@pytest.fixture
def get_tensorboard_run_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "get_tensorboard_run",
    ) as get_tensorboard_run_mock:
        get_tensorboard_run_mock.return_value = _TEST_TENSORBOARD_RUN
        yield get_tensorboard_run_mock


@pytest.fixture
def list_tensorboard_time_series_mock():
    with patch.object(
        tensorboard_service_client.TensorboardServiceClient,
        "list_tensorboard_time_series",
    ) as list_tensorboard_time_series_mock:
        list_tensorboard_time_series_mock.return_value = (
            _TEST_TENSORBOARD_TIME_SERIES_LIST
        )
        yield list_tensorboard_time_series_mock


create_tensorboard_experiment_mock = test_tensorboard.create_tensorboard_experiment_mock
write_tensorboard_run_data_mock = test_tensorboard.write_tensorboard_run_data_mock
get_tensorboard_time_series_mock = test_tensorboard.get_tensorboard_time_series_mock

create_tensorboard_run_artifact_mock = (
    test_metadata.create_tensorboard_run_artifact_mock
)
add_context_artifacts_and_executions_mock = (
    test_metadata.add_context_artifacts_and_executions_mock
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


_TEST_EXPERIMENT_CONTEXT = GapicContext(
    name=_TEST_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT,
    description=_TEST_EXPERIMENT_DESCRIPTION,
    schema_title=constants.SYSTEM_EXPERIMENT,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
    metadata={
        **constants.EXPERIMENT_METADATA,
        constants._BACKING_TENSORBOARD_RESOURCE_KEY: test_tensorboard._TEST_NAME,
    },
)


@pytest.fixture
def add_context_children_mock():
    with patch.object(
        MetadataServiceClient, "add_context_children"
    ) as add_context_children_mock:
        yield add_context_children_mock


@pytest.fixture
def get_tensorboard_run_not_found_mock():
    with patch.object(
        TensorboardServiceClient, "get_tensorboard_run"
    ) as get_tensorboard_run_mock:
        get_tensorboard_run_mock.side_effect = [
            exceptions.NotFound(""),
            test_tensorboard._TEST_TENSORBOARD_RUN,
        ]
        yield get_tensorboard_run_mock


@pytest.fixture
def get_tensorboard_experiment_not_found_mock():
    with patch.object(
        TensorboardServiceClient, "get_tensorboard_experiment"
    ) as get_tensorboard_experiment_mock:
        get_tensorboard_experiment_mock.side_effect = [
            exceptions.NotFound(""),
            test_tensorboard._TEST_TENSORBOARD_EXPERIMENT,
        ]
        yield get_tensorboard_experiment_mock


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
def get_artifact_not_found_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.side_effect = exceptions.NotFound("")
        yield get_artifact_mock


@pytest.fixture
def update_context_mock():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.return_value = _TEST_EXPERIMENT_CONTEXT
        yield update_context_mock


@pytest.fixture
def get_or_create_default_tb_none_mock():
    with patch.object(
        metadata, "_get_or_create_default_tensorboard"
    ) as get_or_create_default_tb_none_mock:
        get_or_create_default_tb_none_mock.return_value = None
        yield get_or_create_default_tb_none_mock


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
    metadata={
        **constants.EXPERIMENT_METADATA,
        constants._BACKING_TENSORBOARD_RESOURCE_KEY: _TEST_TENSORBOARD_NAME,
    },
)
_EXPERIMENT_MOCK_WITHOUT_TB_SET = GapicContext(
    name=_TEST_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT,
    description=_TEST_EXPERIMENT_DESCRIPTION,
    schema_title=constants.SYSTEM_EXPERIMENT,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT],
    metadata={
        **constants.EXPERIMENT_METADATA,
    },
)
_EXPERIMENT_RUN_MOCK = GapicContext(
    name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
    display_name=_TEST_RUN,
    schema_title=constants.SYSTEM_EXPERIMENT_RUN,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT_RUN],
    metadata={
        constants._PARAM_KEY: _TEST_TF_EXPERIMENT_RUN_PARAMS,
        constants._METRIC_KEY: _TEST_TF_EXPERIMENT_RUN_METRICS,
        constants._STATE_KEY: gca_execution.Execution.State.RUNNING.name,
    },
)
_EXPERIMENT_RUN_MOCK_WITH_BACKING_TB = GapicContext(
    name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
    display_name=_TEST_RUN,
    schema_title=constants.SYSTEM_EXPERIMENT_RUN,
    schema_version=constants.SCHEMA_VERSIONS[constants.SYSTEM_EXPERIMENT_RUN],
    metadata={
        constants._PARAM_KEY: _TEST_TF_EXPERIMENT_RUN_PARAMS,
        constants._METRIC_KEY: _TEST_TF_EXPERIMENT_RUN_METRICS,
        constants._STATE_KEY: gca_execution.Execution.State.RUNNING.name,
        **constants.EXPERIMENT_METADATA,
        constants._BACKING_TENSORBOARD_RESOURCE_KEY: _TEST_TENSORBOARD_NAME,
    },
)

_EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT = copy.deepcopy(_EXPERIMENT_RUN_MOCK)
_EXPERIMENT_RUN_MOCK_WITH_PARENT_EXPERIMENT.parent_contexts = [_TEST_CONTEXT_NAME]


@pytest.fixture
def get_experiment_mock():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = _EXPERIMENT_MOCK
        yield get_context_mock


@pytest.fixture
def get_experiment_mock_without_tensorboard():
    with patch.object(MetadataServiceClient, "get_context") as get_context_mock:
        get_context_mock.return_value = _EXPERIMENT_MOCK_WITHOUT_TB_SET
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
def create_experiment_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.side_effect = [_TEST_EXPERIMENT_CONTEXT]
        yield create_context_mock


@pytest.fixture
def create_experiment_run_context_mock():
    with patch.object(MetadataServiceClient, "create_context") as create_context_mock:
        create_context_mock.side_effect = [_EXPERIMENT_RUN_MOCK]
        yield create_context_mock


_TEST_TENSORBOARD_TIME_SERIES = gca_tensorboard_time_series.TensorboardTimeSeries(
    name=_TEST_TENSORBOARD_TIME_SERIES_NAME,
    display_name=_TEST_TIME_SERIES_DISPLAY_NAME,
    value_type=gca_tensorboard_time_series.TensorboardTimeSeries.ValueType.SCALAR,
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
            [_TEST_TENSORBOARD_TIME_SERIES],
        ]
        yield list_tensorboard_time_series_mock


def build_and_train_test_tf_model():
    import tensorflow as tf

    X = np.array(
        [
            [1, 1],
            [1, 2],
            [2, 2],
            [2, 3],
            [1, 1],
            [1, 2],
            [2, 2],
            [2, 3],
            [1, 1],
            [1, 2],
            [2, 2],
            [2, 3],
        ]
    )
    y = np.dot(X, np.array([1, 2])) + 3

    model = tf.keras.models.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(2,)),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(1),
        ]
    )

    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.CategoricalCrossentropy(),
        metrics=["accuracy"],
    )

    model.fit(X, y, epochs=5)


@pytest.mark.usefixtures("google_auth_mock")
class TestAutologging:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

        if autologging_utils._is_autologging_enabled():
            aiplatform.autolog(disable=True)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures(
        "update_context_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_not_found_mock",
        "get_tensorboard_experiment_not_found_mock",
        "list_tensorboard_time_series_mock",
        "list_tensorboard_time_series_mock_empty",
    )
    def test_autologging_init(
        self,
        get_experiment_mock,
        get_metadata_store_mock,
        get_tensorboard_mock,
    ):

        try:
            import mlflow  # noqa: F401
        except ImportError:
            raise ImportError(
                "MLFlow is not installed and is required to test autologging. "
                'Please install the SDK using "pip install google-cloud-aiplatform[autologging]"'
            )
        try:
            import tensorflow as tf  # noqa: F401
        except ImportError:
            raise ImportError(
                "TensorFlow is not installed and is required to test autologging."
                'Please install it before running autologging tests."'
            )
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        aiplatform.autolog()

        get_tensorboard_mock.assert_called_with(
            name=_TEST_TENSORBOARD_NAME,
            retry=base._DEFAULT_RETRY,
        )

        assert get_tensorboard_mock.call_count == 1

        get_experiment_mock.assert_called_once_with(
            name=_TEST_CONTEXT_NAME, retry=base._DEFAULT_RETRY
        )

        get_metadata_store_mock.assert_called_once_with(
            name=_TEST_METADATASTORE,
            retry=base._DEFAULT_RETRY,
        )

    @pytest.mark.usefixtures(
        "get_experiment_mock",
        "get_metadata_store_mock",
    )
    def test_autologging_raises_if_experiment_not_set(
        self,
    ):
        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        with pytest.raises(ValueError):
            aiplatform.autolog()

    @pytest.mark.usefixtures(
        "get_experiment_mock_without_tensorboard",
        "get_metadata_store_mock",
        "update_context_mock",
        "get_or_create_default_tb_none_mock",
    )
    def test_autologging_raises_if_experiment_tensorboard_not_set(
        self,
    ):

        # unset the global tensorboard
        aiplatform.metadata.metadata._experiment_tracker._global_tensorboard = None

        aiplatform.init(
            project=_TEST_PROJECT, location=_TEST_LOCATION, experiment=_TEST_EXPERIMENT
        )

        with pytest.raises(ValueError):
            aiplatform.autolog()

    @pytest.mark.usefixtures(
        "get_experiment_mock",
        "update_context_mock",
        "get_metadata_store_mock",
        "create_experiment_run_context_mock",
        "get_tensorboard_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_not_found_mock",
        "get_tensorboard_experiment_not_found_mock",
        "list_tensorboard_time_series_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock_empty",
    )
    def test_autologging_sets_and_resets_mlflow_tracking_uri(
        self,
    ):
        import mlflow  # noqa: F401

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )
        mlflow.set_tracking_uri(_TEST_MLFLOW_TRACKING_URI)

        aiplatform.autolog()

        assert mlflow.get_tracking_uri() == "vertex-mlflow-plugin://"

        aiplatform.autolog(disable=True)

        assert mlflow.get_tracking_uri() == _TEST_MLFLOW_TRACKING_URI

    @pytest.mark.usefixtures(
        "get_experiment_mock",
        "update_context_mock",
        "get_metadata_store_mock",
        "create_experiment_run_context_mock",
        "get_tensorboard_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_not_found_mock",
        "get_tensorboard_experiment_not_found_mock",
        "list_tensorboard_time_series_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock_empty",
    )
    def test_autologging_enabled_check(
        self,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        aiplatform.autolog()

        assert aiplatform.utils.autologging_utils._is_autologging_enabled()

        aiplatform.autolog(disable=True)

        assert not aiplatform.utils.autologging_utils._is_autologging_enabled()

    @pytest.mark.usefixtures(
        "get_experiment_mock",
        "update_context_mock",
        "get_metadata_store_mock",
        "create_experiment_run_context_mock",
        "get_tensorboard_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_not_found_mock",
        "get_tensorboard_experiment_not_found_mock",
        "list_tensorboard_time_series_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock_empty",
    )
    def test_calling_autolog_with_disable_raises_if_not_enabled(
        self,
    ):

        import mlflow  # noqa: F401

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        with pytest.raises(ValueError):
            aiplatform.autolog(disable=True)

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "add_context_children_mock",
        "get_experiment_mock",
        "get_experiment_run_run_mock",
        "get_tensorboard_mock",
        "create_tensorboard_experiment_mock",
        "write_tensorboard_run_data_mock",
        "get_tensorboard_experiment_not_found_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock",
        "create_tensorboard_run_artifact_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_mock",
        "update_context_mock",
        "list_tensorboard_time_series_mock_empty",
        "add_context_artifacts_and_executions_mock",
    )
    def test_autologging_plugin_autocreates_run_id(
        self,
        create_experiment_run_context_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        aiplatform.autolog()

        build_and_train_test_tf_model()

        # An ExperimentRun should be created with an auto-generated ID
        for args, kwargs in create_experiment_run_context_mock.call_args_list:
            assert kwargs["context"].display_name.startswith("tensorflow-")
            assert kwargs["context_id"].startswith(f"{_TEST_EXPERIMENT}-tensorflow-")

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "add_context_children_mock",
        "get_experiment_mock",
        "create_experiment_context_mock",
        "get_experiment_run_run_mock",
        "get_tensorboard_mock",
        "create_tensorboard_experiment_mock",
        "write_tensorboard_run_data_mock",
        "get_tensorboard_experiment_not_found_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock",
        "create_tensorboard_run_artifact_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_mock",
        "update_context_mock",
        "list_tensorboard_time_series_mock_empty",
        "add_context_artifacts_and_executions_mock",
        "mlflow_plugin_get_run_mock",
        "mlflow_plugin_run_map_mock",
        "mlflow_plugin_create_run_mock",
        "mlflow_plugin_vertex_experiment_mock",
    )
    def test_autologging_plugin_with_auto_run_creation(
        self,
        mlflow_plugin_create_run_mock,
        mlflow_plugin_get_run_mock,
        mlflow_plugin_update_run_info_mock,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        aiplatform.autolog()

        build_and_train_test_tf_model()

        assert mlflow_plugin_create_run_mock.call_count == 1

        build_and_train_test_tf_model()

        # a subsequent model.fit() call should create another ExperimentRun
        assert mlflow_plugin_create_run_mock.call_count == 2

        assert (
            mlflow_plugin_update_run_info_mock.call_args_list[0][0][0]
            == _TEST_MLFLOW_RUN_ID
        )

        # the above model.fit() calls should not result in any data being written locally
        assert not os.path.isdir("mlruns")

        # training a model after disabling autologging should not create additional ExperimentRuns
        # and the plugin should not be invoked
        aiplatform.autolog(disable=True)
        build_and_train_test_tf_model()
        assert mlflow_plugin_create_run_mock.call_count == 2

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "add_context_children_mock",
        "get_experiment_mock",
        "get_experiment_run_run_mock",
        "create_experiment_context_mock",
        "get_tensorboard_mock",
        "create_tensorboard_experiment_mock",
        "write_tensorboard_run_data_mock",
        "get_tensorboard_experiment_not_found_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock",
        "create_tensorboard_run_artifact_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_mock",
        "update_context_mock",
        "list_tensorboard_time_series_mock_empty",
        "add_context_artifacts_and_executions_mock",
    )
    def test_autologging_with_manual_run_creation(
        self,
        create_experiment_run_context_mock,
        caplog,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        aiplatform.autolog()

        aiplatform.start_run(_TEST_RUN)
        build_and_train_test_tf_model()
        assert create_experiment_run_context_mock.call_count == 1

        # metrics and params from additional training calls will not be logged
        # and no new ExperimentRun will be created
        # a warning will be logged with details
        build_and_train_test_tf_model()
        assert create_experiment_run_context_mock.call_count == 1
        assert (
            "Metrics and parameters have already been logged to this run" in caplog.text
        )

        # ending the run and training a new model should result in an auto-created run
        aiplatform.end_run()

        build_and_train_test_tf_model()
        assert create_experiment_run_context_mock.call_count == 2

        caplog.clear()

    @pytest.mark.usefixtures(
        "get_metadata_store_mock",
        "add_context_children_mock",
        "get_experiment_mock",
        "create_experiment_run_context_mock",
        "get_experiment_run_run_mock",
        "get_tensorboard_mock",
        "create_tensorboard_experiment_mock",
        "write_tensorboard_run_data_mock",
        "get_tensorboard_experiment_not_found_mock",
        "get_artifact_not_found_mock",
        "list_tensorboard_time_series_mock",
        "create_tensorboard_run_artifact_mock",
        "get_tensorboard_time_series_mock",
        "get_tensorboard_run_mock",
        "update_context_mock",
        "list_tensorboard_time_series_mock_empty",
        "add_context_artifacts_and_executions_mock",
    )
    def test_mlflow_log_filter_only_shows_framework_warning_logs(
        self,
        caplog,
    ):

        import tensorflow  # noqa: F401

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            experiment=_TEST_EXPERIMENT,
            experiment_tensorboard=_TEST_TENSORBOARD_NAME,
        )

        aiplatform.autolog()

        # Tests that no INFO logs are being surfaced from MLFlow
        # We can't test for the unsupported version warning log since
        # MLFlow changes supported versions regularly
        assert "INFO mlflow" not in caplog.text

        caplog.clear()
