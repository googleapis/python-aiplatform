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

import logging
import mlflow  # noqa: F401
import numpy as np
import os
import pytest

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base

_RUN = "run-1"
_PARAMS = {"sdk-param-test-1": 0.1, "sdk-param-test-2": 0.2}
_METRICS = {"sdk-metric-test-1": 0.8, "sdk-metric-test-2": 100.0}

_RUN_2 = "run-2"
_PARAMS_2 = {"sdk-param-test-1": 0.2, "sdk-param-test-2": 0.4}
_METRICS_2 = {"sdk-metric-test-1": 1.6, "sdk-metric-test-2": 200.0}

_TIME_SERIES_METRIC_KEY = "accuracy"

_CLASSIFICATION_METRICS = {
    "display_name": "my-classification-metrics",
    "labels": ["cat", "dog"],
    "matrix": [[9, 1], [1, 9]],
    "fpr": [0.1, 0.5, 0.9],
    "tpr": [0.1, 0.7, 0.9],
    "threshold": [0.9, 0.5, 0.1],
}


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


def build_and_train_test_scikit_model():
    from sklearn.linear_model import LinearRegression

    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3

    model = LinearRegression()
    model.fit(X, y)


def train_test_scikit_model_and_get_score():
    from sklearn.linear_model import LinearRegression

    X = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
    y = np.dot(X, np.array([1, 2])) + 3

    model = LinearRegression()
    model.fit(X, y)

    model.score(X, y)


def build_and_train_test_sklearn_gridsearch_model():
    from sklearn import svm, datasets
    from sklearn.linear_model import LinearRegression  # noqa: F401
    from sklearn.model_selection import GridSearchCV, RandomizedSearchCV  # noqa: F401

    iris = datasets.load_iris()
    parameters = {"kernel": ("linear", "rbf"), "C": [1, 10]}
    svc = svm.SVC()
    clf = GridSearchCV(svc, parameters)
    clf.fit(iris.data, iris.target)
    return clf


@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestAutologging(e2e_base.TestEndToEnd):

    _temp_prefix = "tmpvrtxsdk-e2e"

    def setup_class(cls):
        cls._experiment_autocreate_scikit = cls._make_display_name("")[:64]
        cls._experiment_autocreate_tf = cls._make_display_name("")[:64]
        cls._experiment_manual_scikit = cls._make_display_name("")[:64]
        cls._experiment_nested_run = cls._make_display_name("")[:64]
        cls._backing_tensorboard = aiplatform.Tensorboard.create(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            display_name=cls._make_display_name("")[:64],
        )

    def test_autologging_with_autorun_creation(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            experiment=self._experiment_autocreate_scikit,
            experiment_tensorboard=self._backing_tensorboard,
        )

        shared_state["resources"] = [self._backing_tensorboard]

        shared_state["resources"].append(
            aiplatform.metadata.metadata._experiment_tracker.experiment
        )

        aiplatform.autolog()

        build_and_train_test_scikit_model()

        # Confirm sklearn run, params, and metrics exist
        experiment_df_scikit = aiplatform.get_experiment_df()
        assert experiment_df_scikit["run_name"][0].startswith("sklearn-")
        assert experiment_df_scikit["param.fit_intercept"][0] == "True"
        assert experiment_df_scikit["metric.training_mae"][0] > 0

        # Write post-training metrics to a scikit-learn model
        assert "metric.LinearRegression_score_X" not in experiment_df_scikit.columns
        train_test_scikit_model_and_get_score()

        experiment_df_scikit = aiplatform.get_experiment_df()
        assert "metric.LinearRegression_score_X" in experiment_df_scikit.columns

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            experiment=self._experiment_autocreate_tf,
            experiment_tensorboard=self._backing_tensorboard,
        )

        shared_state["resources"].append(
            aiplatform.metadata.metadata._experiment_tracker.experiment
        )
        build_and_train_test_tf_model()

        experiment_df_tf = aiplatform.get_experiment_df()

        # Confirm tf run, params, metrics, and time series metrics exist
        assert experiment_df_tf["run_name"][0].startswith("tensorflow-")
        assert experiment_df_tf["param.steps_per_epoch"][0] == "None"
        assert experiment_df_tf["metric.loss"][0] > 0
        assert "time_series_metric.accuracy" in experiment_df_tf.columns

        # No data should be written locally
        assert not os.path.isdir("mlruns")

        # training a model after disabling autologging should not create additional ExperimentRuns
        assert len(experiment_df_tf) == 1
        aiplatform.autolog(disable=True)
        build_and_train_test_scikit_model()

        # No additional experiment runs should be created after disabling autologging
        experiment_df_after_disable = aiplatform.get_experiment_df()
        assert len(experiment_df_after_disable) == 1

    def test_autologging_with_manual_run_creation(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            experiment=self._experiment_manual_scikit,
            experiment_tensorboard=self._backing_tensorboard,
        )

        shared_state["resources"].append(
            aiplatform.metadata.metadata._experiment_tracker.experiment
        )

        aiplatform.autolog()
        run = aiplatform.start_run(_RUN)

        build_and_train_test_scikit_model()
        experiment_df = aiplatform.get_experiment_df()

        # The run shouldn't be ended until end_run() is called
        assert len(experiment_df) == 1
        assert experiment_df["run_name"][0] == _RUN
        assert experiment_df["param.fit_intercept"][0] == "True"
        assert run.state == aiplatform.gapic.Execution.State.RUNNING

        aiplatform.end_run()
        assert run.state == aiplatform.gapic.Execution.State.COMPLETE

        new_experiment = self._make_display_name("exp-2")

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            experiment=new_experiment,
            experiment_tensorboard=self._backing_tensorboard,
        )

        shared_state["resources"].append(
            aiplatform.metadata.metadata._experiment_tracker.experiment
        )
        # Ending the manually created run and training a new model
        # should auto-create a new ExperimentRun
        build_and_train_test_scikit_model()
        experiment_df_after_autocreate = aiplatform.get_experiment_df()

        assert len(experiment_df_after_autocreate) == 1
        assert experiment_df_after_autocreate["run_name"][0].startswith("sklearn-")

    def test_autologging_nested_run_model(self, shared_state, caplog):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            experiment=self._experiment_nested_run,
            experiment_tensorboard=self._backing_tensorboard,
        )

        shared_state["resources"].append(
            aiplatform.metadata.metadata._experiment_tracker.experiment
        )

        aiplatform.autolog()

        build_and_train_test_sklearn_gridsearch_model()
        experiment_df = aiplatform.get_experiment_df()

        assert len(experiment_df) == 1

        assert "This model creates nested runs." in caplog.text
        caplog.clear()
