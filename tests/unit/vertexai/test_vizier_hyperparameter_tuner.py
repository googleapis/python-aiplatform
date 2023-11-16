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
"""Tests for hyperparameter_tuning/vizier_hyperparameter_tuner.py.
"""

import concurrent
from importlib import reload
from unittest import mock

from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform_v1.services.vizier_service import (
    VizierServiceClient,
)
from google.cloud.aiplatform_v1.types.study import Measurement
from google.cloud.aiplatform_v1.types.study import Trial
from google.cloud.aiplatform_v1.types.vizier_service import (
    SuggestTrialsResponse,
)
from vertexai.preview._workflow.driver import remote
from vertexai.preview._workflow.driver import (
    VertexRemoteFunctor,
)
from vertexai.preview._workflow.executor import training
from vertexai.preview._workflow.shared import configs
from vertexai.preview.developer import remote_specs
from vertexai.preview.hyperparameter_tuning import (
    VizierHyperparameterTuner,
)
import numpy as np
import pandas as pd
import pytest
from sklearn.linear_model import _logistic
import sklearn.metrics
import tensorflow as tf


_TEST_PARAMETER_SPEC = {
    "parameter_id": "x",
    "double_value_spec": {"min_value": -10.0, "max_value": 10.0},
}
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_STUDY_NAME_PREFIX = "test_study"

_TRAIN_COL_0 = np.array([0.1] * 100)
_TRAIN_COL_1 = np.array([0.2] * 100)
_TEST_COL_0 = np.array([0.3] * 100)
_TEST_COL_1 = np.array([0.4] * 100)
_TRAIN_TARGET = np.array([1] * 100)
_TEST_TARGET = np.array([1] * 100)
_TEST_X_TRAIN = pd.DataFrame({"col_0": _TRAIN_COL_0, "col_1": _TRAIN_COL_1})
_TEST_Y_TRAIN = pd.DataFrame(
    {
        "target": _TRAIN_TARGET,
    }
)
_TEST_TRAINING_DATA = pd.DataFrame(
    {"col_0": _TRAIN_COL_0, "col_1": _TRAIN_COL_0, "target": _TRAIN_TARGET}
)
_TEST_X_TEST = pd.DataFrame({"col_0": _TEST_COL_0, "col_1": _TEST_COL_1})
_TEST_Y_TEST_CLASSIFICATION_BINARY = pd.DataFrame(
    {
        "target": np.array([0] * 50 + [1] * 50),
    }
)
_TEST_Y_PRED_CLASSIFICATION_BINARY = pd.DataFrame(
    {
        "target": np.array([0] * 30 + [1] * 70),
    }
)
_TEST_Y_TEST_CLASSIFICATION_MULTI_CLASS = pd.DataFrame(
    {
        "target": np.array([1] * 25 + [2] * 25 + [3] * 25 + [4] * 25),
    }
)
_TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS = pd.DataFrame(
    {
        "target": np.array([1] * 25 + [2] * 25 + [4] * 25 + [8] * 25),
    }
)
_TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS = pd.DataFrame(
    {"target": np.array([0, 1, 0, 1, 0])}
)
_TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS = pd.DataFrame(
    {"target": np.array([0.01, 0.56, 0.03, 0.65, 0.74])}
)
_TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS_TRANSFORMED = pd.DataFrame(
    {"target": np.array([0, 1, 0, 1, 1])}
)
_TEST_Y_TEST_CLASSIFICATION_MULTI_CLASS_KERAS = pd.DataFrame(
    {"target": np.array([0, 1, 2, 1, 2])}
)
_TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS_KERAS = pd.DataFrame(
    {
        "target_0": [0.98, 0.02, 0.01, 0.02, 0.02],
        "target_1": [0.01, 0.97, 0.34, 0.96, 0.95],
        "target_2": [0.01, 0.01, 0.65, 0.02, 0.03],
    }
)
_TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS_KERAS_TRANSFORMED = pd.DataFrame(
    {"target": np.array([0, 1, 2, 1, 1])}
)
_TEST_Y_TEST_REGRESSION = pd.DataFrame(
    {
        "target": np.array([0.6] * 100),
    }
)
_TEST_Y_PRED_REGRESSION = pd.DataFrame(
    {
        "target": np.array([0.8] * 100),
    }
)
_TEST_CUSTOM_METRIC_VALUE = 0.5
_TEST_VALIDATION_DATA = pd.DataFrame(
    {
        "col_0": _TEST_COL_0,
        "col_1": _TEST_COL_1,
        "target": _TEST_Y_TEST_CLASSIFICATION_BINARY["target"],
    }
)

_TEST_DISPLAY_NAME = "test_display_name"
_TEST_STAGING_BUCKET = "gs://test-staging-bucket"
_TEST_CONTAINER_URI = "gcr.io/test-image"
_TEST_CONTAINER_URI = "gcr.io/test-image"
_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_SERVICE_ACCOUNT = "test-service-account"
_TEST_TRAINING_CONFIG = configs.RemoteConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    container_uri=_TEST_CONTAINER_URI,
    machine_type=_TEST_MACHINE_TYPE,
    service_account=_TEST_SERVICE_ACCOUNT,
)
_TEST_REMOTE_CONTAINER_TRAINING_CONFIG = configs.DistributedTrainingConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
)
_TEST_TRIAL_NAME = "projects/123/locations/us/central1/studies/123/trials/1"
_TEST_TRIAL_STAGING_BUCKET = (
    _TEST_STAGING_BUCKET + "/projects-123-locations-us-central1-studies-123-trials/1"
)


@pytest.fixture
def mock_create_study():
    with mock.patch.object(VizierServiceClient, "create_study") as create_study_mock:
        create_study_mock.return_value.name = "test_study"
        yield create_study_mock


@pytest.fixture
def mock_suggest_trials():
    with mock.patch.object(
        VizierServiceClient, "suggest_trials"
    ) as suggest_trials_mock:
        yield suggest_trials_mock


@pytest.fixture
def mock_list_trials():
    with mock.patch.object(VizierServiceClient, "list_trials") as list_trials_mock:
        list_trials_mock.return_value.trials = [
            Trial(
                name="trial_0",
                final_measurement=Measurement(
                    metrics=[Measurement.Metric(metric_id="accuracy", value=0.5)]
                ),
                state=Trial.State.SUCCEEDED,
            ),
            Trial(
                name="trial_1",
                final_measurement=Measurement(
                    metrics=[Measurement.Metric(metric_id="accuracy", value=0.34)]
                ),
                state=Trial.State.SUCCEEDED,
            ),
            Trial(
                name="trial_2",
                final_measurement=Measurement(
                    metrics=[Measurement.Metric(metric_id="accuracy", value=0.99)]
                ),
                state=Trial.State.SUCCEEDED,
            ),
            Trial(
                name="trial_3",
                final_measurement=Measurement(
                    metrics=[Measurement.Metric(metric_id="accuracy", value=1.0)]
                ),
                state=Trial.State.STOPPING,
            ),
        ]
        yield list_trials_mock


@pytest.fixture
def mock_complete_trial():
    with mock.patch.object(
        VizierServiceClient, "complete_trial"
    ) as complete_trial_mock:
        yield complete_trial_mock


@pytest.fixture
def mock_binary_classifier():
    model = mock.Mock()
    model.predict.return_value = _TEST_Y_PRED_CLASSIFICATION_BINARY
    yield model


@pytest.fixture
def mock_multi_class_classifier():
    model = mock.Mock()
    model.predict.return_value = _TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS
    yield model


@pytest.fixture
def mock_regressor():
    model = mock.Mock()
    model.predict.return_value = _TEST_Y_PRED_REGRESSION
    return model


@pytest.fixture
def mock_model_custom_metric():
    model = mock.Mock()
    model.score.return_value = _TEST_CUSTOM_METRIC_VALUE
    yield model


@pytest.fixture
def mock_executor_map():
    with mock.patch.object(
        concurrent.futures.ThreadPoolExecutor, "map"
    ) as executor_map_mock:
        yield executor_map_mock


@pytest.fixture
def mock_keras_classifier():
    with mock.patch("tensorflow.keras.Sequential", autospec=True) as keras_mock:
        yield keras_mock


class TestTrainerA(remote.VertexModel):
    def predict(self, x_test):
        return

    @vertexai.preview.developer.mark.train(
        remote_config=_TEST_TRAINING_CONFIG,
    )
    def train(self, x, y):
        return


def get_test_trainer_a():
    model = TestTrainerA()
    model.predict = mock.Mock()
    model.predict.return_value = _TEST_Y_PRED_CLASSIFICATION_BINARY
    return model


class TestTrainerB(remote.VertexModel):
    def predict(self, x_test):
        return

    @vertexai.preview.developer.mark.train(
        remote_config=_TEST_TRAINING_CONFIG,
    )
    def train(self, x_train, y_train, x_test, y_test):
        return


def get_test_trainer_b():
    model = TestTrainerB()
    model.predict = mock.Mock()
    model.predict.return_value = _TEST_Y_PRED_CLASSIFICATION_BINARY
    return model


class TestRemoteContainerTrainer(remote.VertexModel):
    def __init__(self):
        super().__init__()
        self._binding = {}

    def predict(self, x_test):
        return

    # pylint: disable=invalid-name,missing-function-docstring
    @vertexai.preview.developer.mark._remote_container_train(
        image_uri=_TEST_CONTAINER_URI,
        additional_data=[
            remote_specs._InputParameterSpec(
                "training_data",
                argument_name="training_data_path",
                serializer="parquet",
            ),
            remote_specs._InputParameterSpec(
                "validation_data",
                argument_name="validation_data_path",
                serializer="parquet",
            ),
        ],
        remote_config=_TEST_REMOTE_CONTAINER_TRAINING_CONFIG,
    )
    def fit(self, training_data, validation_data):
        return


def get_test_remote_container_trainer():
    model = TestRemoteContainerTrainer()
    model.predict = mock.Mock()
    model.predict.return_value = _TEST_Y_PRED_CLASSIFICATION_BINARY
    return model


class TestVizierHyperparameterTuner:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)
        reload(vertexai.preview.initializer)
        reload(vertexai)

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid")
    def test_vizier_hyper_parameter_tuner(self, mock_create_study):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        test_model_name = "test_model"
        test_max_trial_count = 16
        test_parallel_trial_count = 4
        test_hparam_space = [_TEST_PARAMETER_SPEC]
        test_metric_id = "rmse"
        test_metric_goal = "MINIMIZE"
        test_max_failed_trial_count = 12
        test_search_algorithm = "RANDOM_SEARCH"
        test_project = "custom-project"
        test_location = "custom-location"

        def get_model_func():
            model = mock.Mock()
            model.name = test_model_name
            return model

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=test_max_trial_count,
            parallel_trial_count=test_parallel_trial_count,
            hparam_space=test_hparam_space,
            metric_id=test_metric_id,
            metric_goal=test_metric_goal,
            max_failed_trial_count=test_max_failed_trial_count,
            search_algorithm=test_search_algorithm,
            project=test_project,
            location=test_location,
            study_display_name_prefix=_TEST_STUDY_NAME_PREFIX,
        )
        assert test_tuner.get_model_func().name == test_model_name
        assert test_tuner.max_trial_count == test_max_trial_count
        assert test_tuner.parallel_trial_count == test_parallel_trial_count
        assert test_tuner.hparam_space == test_hparam_space
        assert test_tuner.metric_id == test_metric_id
        assert test_tuner.metric_goal == test_metric_goal
        assert test_tuner.max_failed_trial_count == test_max_failed_trial_count
        assert test_tuner.search_algorithm == test_search_algorithm
        assert test_tuner.vertex == configs.VertexConfig()

        expected_study_name = f"{_TEST_STUDY_NAME_PREFIX}_0"
        expected_study_config = {
            "display_name": expected_study_name,
            "study_spec": {
                "algorithm": test_search_algorithm,
                "parameters": test_hparam_space,
                "metrics": [{"metric_id": test_metric_id, "goal": test_metric_goal}],
            },
        }
        expected_parent = f"projects/{test_project}/locations/{test_location}"
        mock_create_study.assert_called_once_with(
            parent=expected_parent, study=expected_study_config
        )
        assert isinstance(test_tuner.vizier_client, VizierServiceClient)
        assert test_tuner.study == mock_create_study.return_value

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid")
    def test_vizier_hyper_parameter_tuner_default(self, mock_create_study):
        test_model_name = "test_model"
        test_max_trial_count = 16
        test_parallel_trial_count = 4
        test_hparam_space = [_TEST_PARAMETER_SPEC]

        def get_model_func():
            model = mock.Mock()
            model.name = test_model_name
            return model

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=test_max_trial_count,
            parallel_trial_count=test_parallel_trial_count,
            hparam_space=test_hparam_space,
        )
        assert test_tuner.get_model_func().name == test_model_name
        assert test_tuner.max_trial_count == test_max_trial_count
        assert test_tuner.parallel_trial_count == test_parallel_trial_count
        assert test_tuner.hparam_space == test_hparam_space
        assert test_tuner.metric_id == "accuracy"
        assert test_tuner.metric_goal == "MAXIMIZE"
        assert test_tuner.max_failed_trial_count == 0
        assert test_tuner.search_algorithm == "ALGORITHM_UNSPECIFIED"
        assert test_tuner.vertex == configs.VertexConfig()

        expected_study_name = "vizier_hyperparameter_tuner_study_0"
        expected_study_config = {
            "display_name": expected_study_name,
            "study_spec": {
                "algorithm": "ALGORITHM_UNSPECIFIED",
                "parameters": test_hparam_space,
                "metrics": [{"metric_id": "accuracy", "goal": "MAXIMIZE"}],
            },
        }
        expected_parent = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
        mock_create_study.assert_called_once_with(
            parent=expected_parent, study=expected_study_config
        )
        assert isinstance(test_tuner.vizier_client, VizierServiceClient)
        assert test_tuner.study == mock_create_study.return_value

    def test_vizier_hyper_parameter_tuner_error(self):
        def get_model_func():
            return

        test_invalid_metric_id = "invalid_metric_id"
        with pytest.raises(ValueError, match="Unsupported metric_id"):
            VizierHyperparameterTuner(
                get_model_func=get_model_func,
                max_trial_count=16,
                parallel_trial_count=4,
                hparam_space=[_TEST_PARAMETER_SPEC],
                metric_id=test_invalid_metric_id,
            )

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_best_models(self, mock_list_trials):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        test_max_trial_count = 16
        test_parallel_trial_count = 4
        test_hparam_space = [_TEST_PARAMETER_SPEC]

        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=test_max_trial_count,
            parallel_trial_count=test_parallel_trial_count,
            hparam_space=test_hparam_space,
        )
        test_tuner.models["trial_0"] = get_model_func()
        test_tuner.models["trial_1"] = get_model_func()
        test_tuner.models["trial_2"] = get_model_func()
        test_tuner.models["trial_3"] = get_model_func()
        assert test_tuner.get_best_models(2) == [
            test_tuner.models["trial_2"],
            test_tuner.models["trial_0"],
        ]
        mock_list_trials.assert_called_once_with({"parent": "test_study"})

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_create_train_and_test_split_x_and_y(self):
        x = pd.DataFrame(
            {
                "col_0": np.array([0.1] * 100),
                "col_1": np.array([0.2] * 100),
            }
        )
        y = pd.DataFrame(
            {
                "target": np.array([0.3] * 100),
            }
        )

        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
        )
        x_train, x_test, y_train, y_test = test_tuner._create_train_and_test_splits(
            x, y
        )
        assert x_train.shape == (75, 2)
        assert list(x_train.columns) == ["col_0", "col_1"]
        assert x_test.shape == (25, 2)
        assert list(x_test.columns) == ["col_0", "col_1"]
        assert y_train.shape == (75, 1)
        assert list(y_train.columns) == ["target"]
        assert y_test.shape == (25, 1)
        assert list(y_test.columns) == ["target"]

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_create_train_and_test_split_only_x(self):
        x = pd.DataFrame(
            {
                "col_0": np.array([0.1] * 100),
                "col_1": np.array([0.2] * 100),
                "target": np.array([0.3] * 100),
            }
        )

        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
        )
        x_train, x_test, y_train, y_test = test_tuner._create_train_and_test_splits(
            x, "target", test_fraction=0.2
        )
        assert x_train.shape == (80, 3)
        assert list(x_train.columns) == ["col_0", "col_1", "target"]
        assert x_test.shape == (20, 2)
        assert list(x_test.columns) == ["col_0", "col_1"]
        assert not y_train
        assert y_test.shape == (20, 1)
        assert list(y_test.columns) == ["target"]

    @pytest.mark.parametrize(
        "test_fraction",
        [-0.2, 0, 1, 1.2],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_create_train_and_test_split_invalid_test_fraction(self, test_fraction):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
        )

        err_msg = f"test_fraction must be greater than 0 and less than 1 but was {test_fraction}"
        with pytest.raises(ValueError, match=err_msg):
            test_tuner._create_train_and_test_splits(
                pd.DataFrame(), pd.DataFrame(), test_fraction=test_fraction
            )

    @pytest.mark.parametrize(
        "metric_id,expected_value",
        [
            (
                "roc_auc",
                sklearn.metrics.roc_auc_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY,
                ),
            ),
            (
                "f1",
                sklearn.metrics.f1_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY,
                ),
            ),
            (
                "precision",
                sklearn.metrics.precision_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY,
                ),
            ),
            (
                "recall",
                sklearn.metrics.recall_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY,
                ),
            ),
            (
                "accuracy",
                sklearn.metrics.accuracy_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY,
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_model_binary_classification(
        self,
        metric_id,
        expected_value,
        mock_binary_classifier,
    ):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
            metric_id=metric_id,
            metric_goal="MAXIMIZE",
        )
        test_model, test_value = test_tuner._evaluate_model(
            mock_binary_classifier,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
        )
        assert test_value == expected_value
        assert test_model == mock_binary_classifier

    @pytest.mark.parametrize(
        "metric_id,expected_value",
        [
            (
                "accuracy",
                sklearn.metrics.accuracy_score(
                    _TEST_Y_TEST_CLASSIFICATION_MULTI_CLASS,
                    _TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS,
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_model_multi_class_classification(
        self,
        metric_id,
        expected_value,
        mock_multi_class_classifier,
    ):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
            metric_id=metric_id,
            metric_goal="MAXIMIZE",
        )
        test_model, test_value = test_tuner._evaluate_model(
            mock_multi_class_classifier,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_MULTI_CLASS,
        )
        assert test_value == expected_value
        assert test_model == mock_multi_class_classifier

    @pytest.mark.parametrize(
        "metric_id,metric_goal,expected_value",
        [
            (
                "mae",
                "MINIMIZE",
                sklearn.metrics.mean_absolute_error(
                    _TEST_Y_TEST_REGRESSION, _TEST_Y_PRED_REGRESSION
                ),
            ),
            (
                "mape",
                "MINIMIZE",
                sklearn.metrics.mean_absolute_percentage_error(
                    _TEST_Y_TEST_REGRESSION, _TEST_Y_PRED_REGRESSION
                ),
            ),
            (
                "r2",
                "MAXIMIZE",
                sklearn.metrics.r2_score(
                    _TEST_Y_TEST_REGRESSION, _TEST_Y_PRED_REGRESSION
                ),
            ),
            (
                "rmse",
                "MINIMIZE",
                sklearn.metrics.mean_squared_error(
                    _TEST_Y_TEST_REGRESSION, _TEST_Y_PRED_REGRESSION, squared=False
                ),
            ),
            (
                "rmsle",
                "MINIMIZE",
                sklearn.metrics.mean_squared_log_error(
                    _TEST_Y_TEST_REGRESSION, _TEST_Y_PRED_REGRESSION, squared=False
                ),
            ),
            (
                "mse",
                "MINIMIZE",
                sklearn.metrics.mean_squared_error(
                    _TEST_Y_TEST_REGRESSION, _TEST_Y_PRED_REGRESSION
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_model_regression(
        self,
        metric_id,
        metric_goal,
        expected_value,
        mock_regressor,
    ):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
            metric_id=metric_id,
            metric_goal=metric_goal,
        )
        test_model, test_value = test_tuner._evaluate_model(
            mock_regressor, _TEST_X_TEST, _TEST_Y_TEST_REGRESSION
        )
        assert test_value == expected_value
        assert test_model == mock_regressor

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_model_custom_metric(
        self,
        mock_model_custom_metric,
    ):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
            metric_id="custom",
        )
        test_model, test_value = test_tuner._evaluate_model(
            mock_model_custom_metric,
            _TEST_X_TEST,
            _TEST_Y_TEST_REGRESSION,
        )
        assert test_value == _TEST_CUSTOM_METRIC_VALUE
        assert test_model == mock_model_custom_metric

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_model_invalid(self):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
        )
        test_tuner.metric_id = "invalid_metric_id"
        with pytest.raises(ValueError, match="Unsupported metric_id"):
            test_tuner._evaluate_model(
                "model",
                pd.DataFrame(),
                pd.DataFrame(),
            )

    @pytest.mark.parametrize(
        "metric_id,expected_value",
        [
            (
                "roc_auc",
                sklearn.metrics.roc_auc_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS_TRANSFORMED,
                ),
            ),
            (
                "f1",
                sklearn.metrics.f1_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS_TRANSFORMED,
                ),
            ),
            (
                "precision",
                sklearn.metrics.precision_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS_TRANSFORMED,
                ),
            ),
            (
                "recall",
                sklearn.metrics.recall_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS_TRANSFORMED,
                ),
            ),
            (
                "accuracy",
                sklearn.metrics.accuracy_score(
                    _TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS,
                    _TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS_TRANSFORMED,
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_keras_model_binary_classification(
        self, metric_id, expected_value, mock_keras_classifier
    ):
        def get_model_func():
            return mock.Mock

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
            metric_id=metric_id,
            metric_goal="MAXIMIZE",
        )
        mock_keras_classifier.predict.return_value = (
            _TEST_Y_PRED_CLASSIFICATION_BINARY_KERAS
        )

        test_model, test_value = test_tuner._evaluate_model(
            mock_keras_classifier,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_BINARY_KERAS,
        )
        assert test_value == expected_value
        assert test_model == mock_keras_classifier

    @pytest.mark.parametrize(
        "metric_id,expected_value",
        [
            (
                "accuracy",
                sklearn.metrics.accuracy_score(
                    _TEST_Y_TEST_CLASSIFICATION_MULTI_CLASS_KERAS,
                    _TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS_KERAS_TRANSFORMED,
                ),
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_evaluate_keras_model_multi_class_classification(
        self,
        metric_id,
        expected_value,
        mock_keras_classifier,
    ):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
            metric_id=metric_id,
            metric_goal="MAXIMIZE",
        )
        mock_keras_classifier.predict.return_value = (
            _TEST_Y_PRED_CLASSIFICATION_MULTI_CLASS_KERAS
        )
        test_model, test_value = test_tuner._evaluate_model(
            mock_keras_classifier,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_MULTI_CLASS_KERAS,
        )
        assert test_value == expected_value
        assert test_model == mock_keras_classifier

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_add_model_and_report_trial_metrics_feasible(
        self, mock_binary_classifier, mock_complete_trial
    ):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
        )
        test_trial_name = "trial_0"
        test_model = mock_binary_classifier
        test_metric_value = 1.0
        test_tuner._add_model_and_report_trial_metrics(
            test_trial_name,
            (test_model, test_metric_value),
        )
        mock_complete_trial.assert_called_once_with(
            {
                "name": test_trial_name,
                "final_measurement": {
                    "metrics": [{"metric_id": "accuracy", "value": test_metric_value}]
                },
            }
        )
        assert test_tuner.models == {test_trial_name: mock_binary_classifier}

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_add_model_and_report_trial_metrics_infeasible(self, mock_complete_trial):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=1,
            parallel_trial_count=1,
            hparam_space=[],
        )
        test_trial_name = "trial_0"
        test_tuner._add_model_and_report_trial_metrics(
            test_trial_name,
            None,
        )
        mock_complete_trial.assert_called_once_with(
            {"name": test_trial_name, "trial_infeasible": True}
        )
        assert test_tuner.models == {}

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_suggest_trials(self, mock_suggest_trials):
        test_parallel_trial_count = 4

        def get_model_func():
            return

        mock_suggest_trials.return_value.result.return_value.trials = [
            Trial(name="trial_0"),
            Trial(name="trial_1"),
            Trial(name="trial_2"),
            Trial(name="trial_3"),
        ]

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=test_parallel_trial_count,
            hparam_space=[_TEST_PARAMETER_SPEC],
        )
        test_suggested_trials = test_tuner._suggest_trials(test_parallel_trial_count)

        expected_suggest_trials_request = {
            "parent": "test_study",
            "suggestion_count": test_parallel_trial_count,
            "client_id": "client",
        }
        mock_suggest_trials.assert_called_once_with(expected_suggest_trials_request)
        assert test_suggested_trials == mock_suggest_trials().result().trials

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_set_model_parameters(self):
        def get_model_func(penalty: str, C: float, dual=True):
            return _logistic.LogisticRegression(penalty=penalty, C=C, dual=dual)

        hparam_space = [
            {
                "parameter_id": "penalty",
                "categorical_value_spec": {"values": ["l1", "l2"]},
            },
            {
                "parameter_id": "C",
                "discrete_value_spec": {"values": [0.002, 0.01, 0.03]},
            },
            {"parameter_id": "extra_1", "discrete_value_spec": {"values": [1, 2, 3]}},
        ]
        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=hparam_space,
        )
        trial = Trial(
            name="trial_1",
            parameters=[
                Trial.Parameter(parameter_id="penalty", value="elasticnet"),
                Trial.Parameter(parameter_id="C", value=0.05),
                Trial.Parameter(parameter_id="extra_1", value=1.0),
            ],
        )
        model, model_runtime_parameters = test_tuner._set_model_parameters(
            trial, fixed_runtime_params={"extra_2": 5}
        )

        assert model.C == 0.05
        assert model.dual
        assert model.penalty == "elasticnet"
        assert model_runtime_parameters == {"extra_1": 1, "extra_2": 5}

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_set_model_parameters_no_runtime_params(self):
        def get_model_func(penalty: str, C: float, dual=True):
            return _logistic.LogisticRegression(penalty=penalty, C=C, dual=dual)

        hparam_space = [
            {
                "parameter_id": "penalty",
                "categorical_value_spec": {"values": ["l1", "l2"]},
            },
            {
                "parameter_id": "C",
                "discrete_value_spec": {"values": [0.002, 0.01, 0.03]},
            },
            {"parameter_id": "extra_1", "discrete_value_spec": {"values": [1, 2, 3]}},
        ]

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=hparam_space,
        )
        trial = Trial(
            name="trial_1",
            parameters=[
                Trial.Parameter(parameter_id="penalty", value="elasticnet"),
                Trial.Parameter(parameter_id="C", value=0.05),
                Trial.Parameter(parameter_id="dual", value=False),
            ],
        )
        model, model_runtime_parameters = test_tuner._set_model_parameters(trial)

        assert model.C == 0.05
        assert not model.dual
        assert model.penalty == "elasticnet"
        assert not model_runtime_parameters

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_vertex_model_train_method_and_params(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        vertexai.preview.init(remote=False)

        class TestVertexModel(remote.VertexModel):
            @vertexai.preview.developer.mark.train(
                remote_config=_TEST_TRAINING_CONFIG,
            )
            def train(
                self,
                x,
                y,
                x_train,
                y_train,
                x_test,
                y_test,
                training_data,
                validation_data,
                X,
                X_train,
                X_test,
            ):
                return

        def get_model_func():
            return TestVertexModel()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_model = get_model_func()
        (
            test_train_method,
            test_data_params,
        ) = test_tuner._get_vertex_model_train_method_and_params(
            test_model,
            _TEST_X_TRAIN,
            _TEST_Y_TRAIN,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
            _TEST_TRIAL_NAME,
        )
        assert test_train_method == test_model.train
        assert set(test_data_params.keys()) == set(
            [
                "x",
                "y",
                "x_train",
                "y_train",
                "x_test",
                "y_test",
                "training_data",
                "validation_data",
                "X",
                "X_train",
                "X_test",
            ]
        )
        assert test_data_params["x"].equals(_TEST_X_TRAIN)
        assert test_data_params["y"].equals(_TEST_Y_TRAIN)
        assert test_data_params["x_train"].equals(_TEST_X_TRAIN)
        assert test_data_params["y_train"].equals(_TEST_Y_TRAIN)
        assert test_data_params["x_test"].equals(_TEST_X_TEST)
        assert test_data_params["y_test"].equals(_TEST_Y_TEST_CLASSIFICATION_BINARY)
        assert test_data_params["training_data"].equals(_TEST_X_TRAIN)
        assert test_data_params["validation_data"].equals(_TEST_VALIDATION_DATA)
        assert test_data_params["X"].equals(_TEST_X_TRAIN)
        assert test_data_params["X_train"].equals(_TEST_X_TRAIN)
        assert test_data_params["X_test"].equals(_TEST_X_TEST)

        # staging_bucket is not overriden in local mode.
        assert (
            test_train_method.vertex.remote_config.staging_bucket
            == _TEST_STAGING_BUCKET
        )

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_vertex_model_train_method_and_params_no_y_train(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        class TestVertexModel(remote.VertexModel):
            @vertexai.preview.developer.mark.train(
                remote_config=_TEST_TRAINING_CONFIG,
            )
            def train(self, training_data, validation_data):
                return

        def get_model_func():
            return TestVertexModel()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_model = get_model_func()
        (
            test_train_method,
            test_data_params,
        ) = test_tuner._get_vertex_model_train_method_and_params(
            test_model,
            _TEST_TRAINING_DATA,
            None,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
            _TEST_TRIAL_NAME,
        )
        assert test_train_method == test_model.train
        assert set(test_data_params.keys()) == set(["training_data", "validation_data"])
        assert test_data_params["training_data"].equals(_TEST_TRAINING_DATA)
        assert test_data_params["validation_data"].equals(_TEST_VALIDATION_DATA)

    @pytest.mark.parametrize(
        "get_model_func", [get_test_trainer_a, get_test_remote_container_trainer]
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_vertex_model_train_method_and_params_remote_staging_bucket(
        self, get_model_func
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
        )
        vertexai.preview.init(remote=True)
        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_model = get_model_func()
        test_train_method, _ = test_tuner._get_vertex_model_train_method_and_params(
            test_model,
            _TEST_X_TRAIN,
            _TEST_Y_TRAIN,
            _TEST_X_TEST,
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
            _TEST_TRIAL_NAME,
        )
        assert (
            test_train_method.vertex.remote_config.staging_bucket
            == _TEST_TRIAL_STAGING_BUCKET
        )

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_vertex_model_train_method_and_params_no_remote_executable(self):
        class TestVertexModel(remote.VertexModel):
            def train(self, x, y):
                return

            @vertexai.preview.developer.mark.predict()
            def predict(self, x):
                return

        def get_model_func():
            return TestVertexModel()

        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_model = get_model_func()
        with pytest.raises(ValueError, match="No remote executable train method"):
            test_tuner._get_vertex_model_train_method_and_params(
                test_model,
                _TEST_X_TRAIN,
                _TEST_Y_TRAIN,
                _TEST_X_TEST,
                _TEST_Y_TEST_CLASSIFICATION_BINARY,
                _TEST_TRIAL_NAME,
            )

    @pytest.mark.parametrize(
        "get_model_func,x_train,y_train,x_test,y_test",
        [
            (
                get_test_trainer_a,
                _TEST_X_TRAIN,
                None,
                _TEST_Y_TRAIN,
                _TEST_Y_TEST_CLASSIFICATION_BINARY,
            ),
            (
                get_test_trainer_b,
                _TEST_X_TRAIN,
                _TEST_X_TEST,
                _TEST_Y_TRAIN,
                _TEST_Y_TEST_CLASSIFICATION_BINARY,
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_run_trial_vertex_model_train(
        self,
        get_model_func,
        x_train,
        y_train,
        x_test,
        y_test,
    ):
        # For unit tests only test local mode.
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        vertexai.preview.init(remote=False)

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_trial = Trial(name="trial_0", parameters=[])
        test_model, test_metric_value = test_tuner._run_trial(
            x_train=x_train,
            y_train=y_train,
            x_test=x_test,
            y_test=y_test,
            trial=test_trial,
        )
        assert isinstance(test_model, type(get_model_func()))
        test_model.predict.assert_called_once_with(x_test)
        assert test_metric_value == sklearn.metrics.accuracy_score(
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
            _TEST_Y_PRED_CLASSIFICATION_BINARY,
        )

    @pytest.mark.usefixtures(
        "google_auth_mock",
        "mock_create_study",
        "mock_blob_upload_from_filename",
        "mock_create_custom_job",
        "mock_get_custom_job_succeeded",
    )
    def test_run_trial_vertex_model_remote_container_train(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        vertexai.preview.init(remote=True)

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_test_remote_container_trainer,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_trial = Trial(name="trial_0", parameters=[])
        test_model, test_metric_value = test_tuner._run_trial(
            x_train=_TEST_TRAINING_DATA,
            y_train=None,
            x_test=_TEST_X_TEST,
            y_test=_TEST_Y_TEST_CLASSIFICATION_BINARY,
            trial=test_trial,
        )
        assert isinstance(test_model, TestRemoteContainerTrainer)
        test_model.predict.assert_called_once_with(_TEST_X_TEST)
        assert test_metric_value == sklearn.metrics.accuracy_score(
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
            _TEST_Y_PRED_CLASSIFICATION_BINARY,
        )

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_run_trial_infeasible(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        vertexai.preview.init(remote=True)

        class TestTrainer(remote.VertexModel):
            @vertexai.preview.developer.mark.train(
                remote_config=_TEST_TRAINING_CONFIG,
            )
            def train(self, x_train, y_train, x_test, y_test):
                raise RuntimeError()

        def get_model_func():
            return TestTrainer()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_trial = Trial(name="trial_0", parameters=[])
        trial_output = test_tuner._run_trial(
            x_train=_TEST_X_TRAIN,
            y_train=_TEST_Y_TRAIN,
            x_test=_TEST_X_TEST,
            y_test=_TEST_Y_TEST_REGRESSION,
            trial=test_trial,
        )
        assert not trial_output

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_run_trial_unsupported_model_type(self):
        def get_model_func():
            return mock.Mock()

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_trial = Trial(name="trial_0", parameters=[])
        with pytest.raises(ValueError, match="Unsupported model type"):
            test_tuner._run_trial(
                x_train=_TEST_X_TRAIN,
                y_train=_TEST_Y_TRAIN,
                x_test=_TEST_X_TEST,
                y_test=_TEST_Y_TEST_REGRESSION,
                trial=test_trial,
            )

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid", "mock_create_study")
    def test_fit(
        self,
        mock_executor_map,
        mock_suggest_trials,
        mock_complete_trial,
    ):
        def get_model_func():
            return

        mock_suggest_trials.return_value.result.side_effect = [
            SuggestTrialsResponse(
                trials=[Trial(name="trial_1"), Trial(name="trial_2")]
            ),
            SuggestTrialsResponse(
                trials=[
                    Trial(name="trial_3"),
                    Trial(name="trial_4"),
                ]
            ),
        ]
        model_1, model_2, model_3, model_4 = (mock.Mock() for _ in range(4))
        mock_executor_map.side_effect = [
            [(model_1, 0.01), (model_2, 0.03)],
            [(model_3, 0.02), (model_4, 0.05)],
        ]
        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=4,
            parallel_trial_count=2,
            hparam_space=[],
        )
        test_tuner.fit(x=_TEST_X_TEST, y=_TEST_Y_TEST_CLASSIFICATION_BINARY)

        assert mock_suggest_trials.call_count == 2
        assert mock_executor_map.call_count == 2
        # check fixed_runtime_params in first executor.map call is empty
        assert not mock_executor_map.call_args_list[0][0][1][0][6]
        assert mock_complete_trial.call_count == 4
        assert test_tuner.models == {
            "trial_1": model_1,
            "trial_2": model_2,
            "trial_3": model_3,
            "trial_4": model_4,
        }

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid", "mock_create_study")
    def test_fit_varying_parallel_trial_count_and_fixed_runtime_params(
        self,
        mock_executor_map,
        mock_suggest_trials,
        mock_complete_trial,
    ):
        def get_model_func():
            return

        mock_suggest_trials.return_value.result.side_effect = [
            SuggestTrialsResponse(
                trials=[Trial(name="trial_1"), Trial(name="trial_2")]
            ),
            SuggestTrialsResponse(
                trials=[
                    Trial(name="trial_3"),
                    Trial(name="trial_4"),
                ]
            ),
            SuggestTrialsResponse(
                trials=[
                    Trial(name="trial_5"),
                ]
            ),
        ]
        model_1, model_2, model_3, model_4, model_5 = (mock.Mock() for _ in range(5))
        mock_executor_map.side_effect = [
            [(model_1, 0.01), (model_2, 0.03)],
            [(model_3, 0.02), (model_4, 0.05)],
            [(model_5, 0.06)],
        ]
        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=5,
            parallel_trial_count=2,
            hparam_space=[],
        )
        test_tuner.fit(
            x=_TEST_X_TEST,
            y=_TEST_Y_TEST_CLASSIFICATION_BINARY,
            x_test=_TEST_X_TEST,
            y_test=_TEST_Y_TEST_CLASSIFICATION_BINARY,
            num_epochs=5,
        )

        assert mock_suggest_trials.call_count == 3
        assert mock_executor_map.call_count == 3
        # check fixed_runtime_params in first executor.map call is non-empty
        assert mock_executor_map.call_args_list[0][0][1][0][6] == {"num_epochs": 5}
        assert mock_complete_trial.call_count == 5
        assert test_tuner.models == {
            "trial_1": model_1,
            "trial_2": model_2,
            "trial_3": model_3,
            "trial_4": model_4,
            "trial_5": model_5,
        }

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid", "mock_create_study")
    def test_fit_max_failed_trial_count(
        self,
        mock_executor_map,
        mock_suggest_trials,
        mock_complete_trial,
    ):
        def get_model_func():
            return

        mock_suggest_trials.return_value.result.return_value = SuggestTrialsResponse(
            trials=[Trial(name="trial_1")]
        )

        mock_executor_map.return_value = [None]

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=2,
            parallel_trial_count=1,
            hparam_space=[],
            max_failed_trial_count=1,
        )

        with pytest.raises(
            ValueError, match="Maximum number of failed trials reached."
        ):
            test_tuner.fit(
                x=_TEST_X_TEST,
                y=_TEST_Y_TEST_CLASSIFICATION_BINARY,
                num_epochs=5,
            )

        assert mock_suggest_trials.call_count == 1
        assert mock_executor_map.call_count == 1
        # check fixed_runtime_params in first executor.map call is non-empty
        assert mock_executor_map.call_args_list[0][0][1][0][6] == {"num_epochs": 5}
        assert mock_complete_trial.call_count == 1
        assert not test_tuner.models

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid", "mock_create_study")
    def test_fit_all_trials_failed(
        self,
        mock_executor_map,
        mock_suggest_trials,
        mock_complete_trial,
    ):
        def get_model_func():
            return

        mock_suggest_trials.return_value.result.side_effect = [
            SuggestTrialsResponse(trials=[Trial(name="trial_1")]),
            SuggestTrialsResponse(trials=[Trial(name="trial_2")]),
        ]

        mock_executor_map.return_value = [None]

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=2,
            parallel_trial_count=1,
            hparam_space=[],
            max_failed_trial_count=0,
        )

        with pytest.raises(ValueError, match="All trials failed."):
            test_tuner.fit(
                x=_TEST_X_TEST,
                y=_TEST_Y_TEST_CLASSIFICATION_BINARY,
            )

        assert mock_suggest_trials.call_count == 2
        assert mock_executor_map.call_count == 2
        assert mock_complete_trial.call_count == 2
        assert not test_tuner.models

    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid", "mock_create_study")
    def test_get_model_param_type_mapping(self):
        hparam_space = [
            {
                "parameter_id": "penalty",
                "categorical_value_spec": {"values": ["l1", "l2"]},
            },
            {
                "parameter_id": "C",
                "discrete_value_spec": {"values": [0.002, 0.01, 0.03]},
            },
            {
                "parameter_id": "epochs",
                "integer_value_spec": {"min_value": 1, "max_value": 5.0},
            },
            {
                "parameter_id": "learning_rate",
                "double_value_spec": {"min_value": 1, "max_value": 5},
            },
        ]
        test_tuner = VizierHyperparameterTuner(
            get_model_func=None,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=hparam_space,
        )
        expected_mapping = {
            "penalty": str,
            "C": float,
            "epochs": int,
            "learning_rate": float,
        }

        assert expected_mapping == test_tuner._get_model_param_type_mapping()

    @pytest.mark.parametrize(
        "test_get_model_func,expected_fixed_init_params",
        [
            (lambda x, y: None, {"x": _TEST_X_TRAIN, "y": _TEST_Y_TRAIN}),
            (lambda X, y: None, {"X": _TEST_X_TRAIN, "y": _TEST_Y_TRAIN}),
            (
                lambda x_train, y_train: None,
                {"x_train": _TEST_X_TRAIN, "y_train": _TEST_Y_TRAIN},
            ),
            (
                lambda X_train, y_train: None,
                {"X_train": _TEST_X_TRAIN, "y_train": _TEST_Y_TRAIN},
            ),
        ],
    )
    @pytest.mark.usefixtures("google_auth_mock", "mock_uuid", "mock_create_study")
    def test_fit_get_model_func_params(
        self,
        test_get_model_func,
        expected_fixed_init_params,
        mock_executor_map,
        mock_suggest_trials,
        mock_complete_trial,
    ):
        mock_suggest_trials.return_value.result.side_effect = [
            SuggestTrialsResponse(trials=[Trial(name="trial_1")]),
            SuggestTrialsResponse(trials=[Trial(name="trial_2")]),
            SuggestTrialsResponse(trials=[Trial(name="trial_3")]),
            SuggestTrialsResponse(trials=[Trial(name="trial_4")]),
        ]
        model_1, model_2, model_3, model_4 = (mock.Mock() for _ in range(4))
        mock_executor_map.side_effect = [
            [(model_1, 0.01)],
            [(model_2, 0.03)],
            [(model_3, 0.02)],
            [(model_4, 0.05)],
        ]
        test_tuner = VizierHyperparameterTuner(
            get_model_func=test_get_model_func,
            max_trial_count=4,
            parallel_trial_count=1,
            hparam_space=[],
        )
        test_tuner.fit(
            x=_TEST_X_TRAIN,
            y=_TEST_Y_TRAIN,
            x_test=_TEST_X_TEST,
            y_test=_TEST_Y_TEST_CLASSIFICATION_BINARY,
        )

        assert mock_suggest_trials.call_count == 4
        assert mock_executor_map.call_count == 4
        # check fixed_runtime_params in first executor.map call is empty
        assert not mock_executor_map.call_args_list[0][0][1][0][6]
        assert mock_complete_trial.call_count == 4
        assert test_tuner.models == {
            "trial_1": model_1,
            "trial_2": model_2,
            "trial_3": model_3,
            "trial_4": model_4,
        }

        test_map_args = [call_args[0] for call_args in mock_executor_map.call_args_list]
        test_fixed_init_params = []
        for map_args in test_map_args:
            test_fixed_init_params.append(
                [trial_inputs[5] for trial_inputs in map_args[1]]
            )
        assert test_fixed_init_params == [
            [expected_fixed_init_params],
            [expected_fixed_init_params],
            [expected_fixed_init_params],
            [expected_fixed_init_params],
        ]

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_lightning_train_method_and_params_local(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        def get_model_func():
            return

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=4,
            parallel_trial_count=2,
            hparam_space=[],
        )
        test_model = {
            "model": mock.Mock(),
            "trainer": mock.Mock(),
            "train_dataloaders": mock.Mock(),
        }
        (
            test_train_method,
            test_params,
        ) = test_tuner._get_lightning_train_method_and_params(test_model, "")
        assert test_train_method == test_model["trainer"].fit
        assert test_params == {
            "model": test_model["model"],
            "train_dataloaders": test_model["train_dataloaders"],
        }

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_lightning_train_method_and_params_remote(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
        )
        vertexai.preview.init(remote=True)

        def get_model_func():
            return

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=4,
            parallel_trial_count=2,
            hparam_space=[],
        )

        class TestTrainer:
            def fit(self, model, train_dataloaders):
                pass

        test_model = {
            "model": mock.Mock(),
            "trainer": mock.Mock(),
            "train_dataloaders": mock.Mock(),
        }

        test_model["trainer"].fit = VertexRemoteFunctor(
            TestTrainer().fit, remote_executor=training.remote_training
        )
        (
            test_train_method,
            test_params,
        ) = test_tuner._get_lightning_train_method_and_params(
            test_model, _TEST_TRIAL_NAME
        )
        assert test_params == {
            "model": test_model["model"],
            "train_dataloaders": test_model["train_dataloaders"],
        }
        assert test_train_method == test_model["trainer"].fit
        assert (
            test_train_method.vertex.remote_config.staging_bucket
            == _TEST_TRIAL_STAGING_BUCKET
        )

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_run_trial_lightning(
        self,
    ):
        # For unit tests only test local mode.
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        test_lightning_model = {
            "model": mock.Mock(),
            "trainer": mock.Mock(),
            "train_dataloaders": mock.Mock(),
        }
        test_lightning_model[
            "model"
        ].predict.return_value = _TEST_Y_PRED_CLASSIFICATION_BINARY

        def get_model_func():
            return test_lightning_model

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_trial = Trial(name="trial_0", parameters=[])
        test_trained_model, test_metric_value = test_tuner._run_trial(
            x_train=_TEST_X_TRAIN,
            y_train=_TEST_Y_TRAIN,
            x_test=_TEST_X_TEST,
            y_test=_TEST_Y_TEST_CLASSIFICATION_BINARY,
            trial=test_trial,
            fixed_runtime_params={"ckpt_path": "test_ckpt_path"},
        )
        assert test_trained_model == test_lightning_model
        test_lightning_model["trainer"].fit.assert_called_once_with(
            model=test_lightning_model["model"],
            train_dataloaders=test_lightning_model["train_dataloaders"],
            ckpt_path="test_ckpt_path",
        )
        test_lightning_model["model"].predict.assert_called_once_with(_TEST_X_TEST)
        assert test_metric_value == sklearn.metrics.accuracy_score(
            _TEST_Y_TEST_CLASSIFICATION_BINARY,
            _TEST_Y_PRED_CLASSIFICATION_BINARY,
        )

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_keras_train_method_and_params(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        vertexai.preview.init(remote=True)

        def get_model_func():
            tf.keras.Sequential = vertexai.preview.remote(tf.keras.Sequential)
            model = tf.keras.Sequential(
                [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
            )
            model.compile(optimizer="adam", loss="mean_squared_error")
            model.fit.vertex.remote_config.staging_bucket = _TEST_STAGING_BUCKET
            return model

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_model = get_model_func()
        test_train_method, data_params = test_tuner._get_train_method_and_params(
            test_model,
            _TEST_X_TRAIN,
            _TEST_Y_TRAIN,
            _TEST_TRIAL_NAME,
            params=["x", "y"],
        )
        assert test_train_method._remote_executor == training.remote_training
        assert (
            test_train_method.vertex.remote_config.staging_bucket
            == _TEST_TRIAL_STAGING_BUCKET
        )
        assert data_params == {"x": _TEST_X_TRAIN, "y": _TEST_Y_TRAIN}

    @pytest.mark.usefixtures("google_auth_mock", "mock_create_study")
    def test_get_sklearn_train_method_and_params(self):
        vertexai.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
        vertexai.preview.init(remote=True)

        def get_model_func():
            LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
            model = LogisticRegression(penalty="l1")
            model.fit.vertex.remote_config.staging_bucket = _TEST_STAGING_BUCKET
            return model

        test_tuner = VizierHyperparameterTuner(
            get_model_func=get_model_func,
            max_trial_count=16,
            parallel_trial_count=4,
            hparam_space=[],
        )
        test_model = get_model_func()
        (test_train_method, data_params,) = test_tuner._get_train_method_and_params(
            test_model,
            _TEST_X_TRAIN,
            _TEST_Y_TRAIN,
            _TEST_TRIAL_NAME,
            params=["X", "y"],
        )
        assert test_train_method._remote_executor == training.remote_training
        assert (
            test_train_method.vertex.remote_config.staging_bucket
            == _TEST_TRIAL_STAGING_BUCKET
        )
        assert data_params == {"X": _TEST_X_TRAIN, "y": _TEST_Y_TRAIN}
