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

import pytest


from unittest import mock
from importlib import reload
from unittest.mock import patch
from unittest.mock import ANY

from google.api_core import exceptions
from google.api_core import operation

from google.cloud import aiplatform
from google.cloud.aiplatform.vizier import Study
from google.cloud.aiplatform.vizier import Trial
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.vizier import pyvizier

from google.cloud.aiplatform.compat.services import vizier_service_client
from google.cloud.aiplatform.compat.types import (
    study as gca_study,
    vizier_service as gca_vizier_service,
)
from google.protobuf import duration_pb2


# project
_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

# study
_TEST_STUDY_ID = "12345"
_TEST_STUDY_NAME = f"{_TEST_PARENT}/studies/{_TEST_STUDY_ID}"

# trial
_TEST_TRIAL_ID = "1"
_TEST_TRIAL_NAME = f"{_TEST_STUDY_NAME}/trials/{_TEST_TRIAL_ID}"

_TEST_METRIC_ID = "pr-auc"
_TEST_DISPLAY_NAME = "test_study_python_aiplatform"

_TEST_PARAMETER_ID_1 = "learning_rate"
_TEST_PARAMETER_ID_MIN_VALUE_1 = 1e-05
_TEST_PARAMETER_ID_MAX_VALUE_1 = 1.0

_TEST_PARAMETER_ID_2 = "optimizer"
_TEST_PARAMETER_VALUE_2 = ["adagrad", "adam", "experimental"]

_TEST_STUDY = gca_study.Study(
    display_name=_TEST_DISPLAY_NAME,
    study_spec=gca_study.StudySpec(
        algorithm=gca_study.StudySpec.Algorithm.RANDOM_SEARCH,
        metrics=[
            gca_study.StudySpec.MetricSpec(
                metric_id=_TEST_METRIC_ID,
                goal=gca_study.StudySpec.MetricSpec.GoalType.MAXIMIZE,
            )
        ],
        parameters=[
            gca_study.StudySpec.ParameterSpec(
                parameter_id=_TEST_PARAMETER_ID_1,
                scale_type=gca_study.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
                double_value_spec=gca_study.StudySpec.ParameterSpec.DoubleValueSpec(
                    min_value=_TEST_PARAMETER_ID_MIN_VALUE_1,
                    max_value=_TEST_PARAMETER_ID_MAX_VALUE_1,
                ),
            ),
            gca_study.StudySpec.ParameterSpec(
                parameter_id=_TEST_PARAMETER_ID_2,
                categorical_value_spec=gca_study.StudySpec.ParameterSpec.CategoricalValueSpec(
                    values=_TEST_PARAMETER_VALUE_2
                ),
            ),
        ],
    ),
)


@pytest.fixture
def get_study_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "get_study"
    ) as get_study_mock:
        get_study_mock.return_value = gca_study.Study(name=_TEST_STUDY_NAME)
        yield get_study_mock


@pytest.fixture
def get_trial_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "get_trial"
    ) as get_trial_mock:
        get_trial_mock.return_value = gca_study.Trial(
            name=_TEST_TRIAL_NAME,
            state=gca_study.Trial.State.ACTIVE,
            parameters=[
                gca_study.Trial.Parameter(
                    parameter_id=_TEST_PARAMETER_ID_1,
                    value=_TEST_PARAMETER_ID_MIN_VALUE_1,
                )
            ],
        )
        yield get_trial_mock


@pytest.fixture
def create_study_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "create_study"
    ) as create_study_mock:
        create_study_mock.return_value = gca_study.Study(
            name=_TEST_STUDY_NAME,
        )
        yield create_study_mock


@pytest.fixture
def lookup_study_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "lookup_study"
    ) as lookup_study_mock:
        lookup_study_mock.return_value = gca_study.Study(
            name=_TEST_STUDY_NAME,
        )
        yield lookup_study_mock


@pytest.fixture
def suggest_trials_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "suggest_trials"
    ) as suggest_trials_mock:
        suggest_trials_lro_mock = mock.Mock(operation.Operation)
        suggest_trials_lro_mock.result.return_value = (
            gca_vizier_service.SuggestTrialsResponse(
                trials=[gca_study.Trial(name=_TEST_TRIAL_NAME)]
            )
        )
        suggest_trials_mock.return_value = suggest_trials_lro_mock
        yield suggest_trials_mock


@pytest.fixture
def list_optimal_trials_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "list_optimal_trials"
    ) as list_optimal_trials_mock:
        list_optimal_trials_mock.return_value = (
            gca_vizier_service.ListOptimalTrialsResponse(
                optimal_trials=[gca_study.Trial(name=_TEST_TRIAL_NAME)]
            )
        )
        yield list_optimal_trials_mock


@pytest.fixture
def list_trials_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "list_trials"
    ) as list_trials_mock:
        list_trials_mock.return_value = gca_vizier_service.ListTrialsResponse(
            trials=[gca_study.Trial(name=_TEST_TRIAL_NAME)]
        )
        yield list_trials_mock


@pytest.fixture
def delete_study_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "delete_study"
    ) as delete_study_mock:
        yield delete_study_mock


@pytest.fixture
def delete_trial_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "delete_trial"
    ) as delete_trial_mock:
        yield delete_trial_mock


@pytest.fixture
def complete_trial_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "complete_trial"
    ) as complete_trial_mock:
        complete_trial_mock.return_value = gca_study.Trial(
            name=_TEST_TRIAL_NAME,
            final_measurement=gca_study.Measurement(
                step_count=3,
                metrics=[gca_study.Measurement.Metric(metric_id="y", value=5)],
            ),
        )
        yield complete_trial_mock


@pytest.fixture
def complete_trial_empty_measurement_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "complete_trial"
    ) as complete_trial_empty_measurement_mock:
        complete_trial_empty_measurement_mock.return_value = gca_study.Trial(
            name=_TEST_TRIAL_NAME
        )
        yield complete_trial_empty_measurement_mock


@pytest.fixture
def should_stop_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "check_trial_early_stopping_state"
    ) as should_stop_mock:
        should_stop_lro_mock = mock.Mock(operation.Operation)
        should_stop_lro_mock.result.return_value = (
            gca_vizier_service.CheckTrialEarlyStoppingStateResponse(should_stop=True)
        )
        should_stop_mock.return_value = should_stop_lro_mock
        yield should_stop_mock


@pytest.fixture
def create_study_mock_already_exists():
    with patch.object(
        vizier_service_client.VizierServiceClient, "create_study"
    ) as create_study_mock:
        create_study_mock.side_effect = [
            exceptions.AlreadyExists("Study already exists."),
            gca_study.Study(
                name=_TEST_STUDY_NAME,
            ),
        ]
        yield create_study_mock


@pytest.fixture
def add_measurement_mock():
    with patch.object(
        vizier_service_client.VizierServiceClient, "add_trial_measurement"
    ) as add_measurement_mock:
        yield add_measurement_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestStudy:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("get_study_mock")
    def test_create_study(self, create_study_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)

        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        create_study_mock.assert_called_once_with(
            parent=_TEST_PARENT, study=_TEST_STUDY
        )
        assert type(study) == Study

    @pytest.mark.usefixtures("get_study_mock")
    def test_create_study_already_exists(
        self, create_study_mock_already_exists, lookup_study_mock
    ):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)

        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        lookup_study_mock.assert_called_once_with(
            request={"parent": _TEST_PARENT, "display_name": _TEST_DISPLAY_NAME}
        )
        assert type(study) == Study

    @pytest.mark.usefixtures("get_study_mock")
    def test_materialize_study_config(self, create_study_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)
        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        study_config = study.materialize_study_config()

        create_study_mock.assert_called_once_with(
            parent=_TEST_PARENT, study=_TEST_STUDY
        )
        assert type(study_config) == pyvizier.StudyConfig

    @pytest.mark.usefixtures("get_study_mock", "get_trial_mock")
    def test_suggest(self, create_study_mock, suggest_trials_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)
        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        trials = study.suggest(count=5, worker="test_worker")

        suggest_trials_mock.assert_called_once_with(
            request={
                "parent": _TEST_STUDY_NAME,
                "suggestion_count": 5,
                "client_id": "test_worker",
            }
        )
        assert type(trials[0]) == Trial

    @pytest.mark.usefixtures("get_study_mock")
    def test_from_uid(self):
        aiplatform.init(project=_TEST_PROJECT)

        study = Study.from_uid(uid=_TEST_STUDY_ID)

        assert type(study) == Study
        assert study.name == _TEST_STUDY_ID

    @pytest.mark.usefixtures("get_study_mock")
    def test_delete(self, create_study_mock, delete_study_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)
        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        study.delete()

        delete_study_mock.assert_called_once_with(name=_TEST_STUDY_NAME)

    @pytest.mark.usefixtures("get_study_mock", "create_study_mock", "get_trial_mock")
    def test_optimal_trials(self, list_optimal_trials_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)
        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        trials = study.optimal_trials()

        list_optimal_trials_mock.assert_called_once_with(
            request={"parent": _TEST_STUDY_NAME}
        )
        assert type(trials[0]) == Trial

    @pytest.mark.usefixtures("get_study_mock", "create_study_mock", "get_trial_mock")
    def test_list_trials(self, list_trials_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)
        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        trials = study.trials()

        list_trials_mock.assert_called_once_with(request={"parent": _TEST_STUDY_NAME})
        assert type(trials[0]) == Trial

    @pytest.mark.usefixtures("get_study_mock", "create_study_mock")
    def test_get_trial(self, get_trial_mock):
        aiplatform.init(project=_TEST_PROJECT)
        sc = pyvizier.StudyConfig()
        sc.algorithm = pyvizier.Algorithm.RANDOM_SEARCH
        sc.metric_information.append(
            pyvizier.MetricInformation(
                name=_TEST_METRIC_ID, goal=pyvizier.ObjectiveMetricGoal.MAXIMIZE
            )
        )
        root = sc.search_space.select_root()
        root.add_float_param(
            _TEST_PARAMETER_ID_1,
            _TEST_PARAMETER_ID_MIN_VALUE_1,
            _TEST_PARAMETER_ID_MAX_VALUE_1,
            scale_type=pyvizier.ScaleType.LINEAR,
        )
        root.add_categorical_param(_TEST_PARAMETER_ID_2, _TEST_PARAMETER_VALUE_2)
        study = Study.create_or_load(display_name=_TEST_DISPLAY_NAME, problem=sc)

        trial = study.get_trial(1)

        get_trial_mock.assert_called_once_with(name=_TEST_TRIAL_NAME, retry=ANY)
        assert type(trial) == Trial


@pytest.mark.usefixtures("google_auth_mock")
class TestTrial:
    def setup_method(self):
        reload(initializer)
        reload(aiplatform)

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("get_trial_mock")
    def test_delete(self, delete_trial_mock):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)

        trial.delete()

        delete_trial_mock.assert_called_once_with(name=_TEST_TRIAL_NAME)
        assert type(trial) == Trial

    @pytest.mark.usefixtures("get_trial_mock")
    def test_complete(self, complete_trial_mock):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)
        measurement = pyvizier.Measurement()
        measurement.metrics["y"] = 4

        measurement = trial.complete(
            measurement=measurement, infeasible_reason="infeasible"
        )

        complete_trial_mock.assert_called_once_with(
            request={
                "name": _TEST_TRIAL_NAME,
                "infeasible_reason": "infeasible",
                "trial_infeasible": True,
                "final_measurement": gca_study.Measurement(
                    elapsed_duration=duration_pb2.Duration(),
                    metrics=[gca_study.Measurement.Metric(metric_id="y", value=4)],
                ),
            }
        )
        assert type(measurement) == pyvizier.Measurement

    @pytest.mark.usefixtures("get_trial_mock")
    def test_complete_empty_measurement(self, complete_trial_empty_measurement_mock):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)
        measurement = pyvizier.Measurement()
        measurement.metrics["y"] = 4

        measurement = trial.complete(
            measurement=measurement, infeasible_reason="infeasible"
        )

        complete_trial_empty_measurement_mock.assert_called_once_with(
            request={
                "name": _TEST_TRIAL_NAME,
                "infeasible_reason": "infeasible",
                "trial_infeasible": True,
                "final_measurement": gca_study.Measurement(
                    elapsed_duration=duration_pb2.Duration(),
                    metrics=[gca_study.Measurement.Metric(metric_id="y", value=4)],
                ),
            }
        )
        assert measurement is None

    @pytest.mark.usefixtures("get_trial_mock")
    def test_should_stop(self, should_stop_mock):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)

        should_stop = trial.should_stop()

        should_stop_mock.assert_called_once_with(
            request={"trial_name": _TEST_TRIAL_NAME}
        )
        assert should_stop is True

    @pytest.mark.usefixtures("get_trial_mock")
    def test_add_measurement(self, add_measurement_mock):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)
        measurement = pyvizier.Measurement()
        measurement.metrics["y"] = 4

        add_measurement = trial.add_measurement(measurement=measurement)

        add_measurement_mock.assert_called_once_with(
            request={
                "trial_name": _TEST_TRIAL_NAME,
                "measurement": gca_study.Measurement(
                    elapsed_duration=duration_pb2.Duration(),
                    metrics=[gca_study.Measurement.Metric(metric_id="y", value=4)],
                ),
            }
        )
        assert add_measurement is None

    @pytest.mark.usefixtures("get_trial_mock")
    def test_properties(self):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)
        measurement = pyvizier.Measurement()
        measurement.metrics["y"] = 4

        uid = trial.uid
        status = trial.status
        parameters = trial.parameters

        assert uid == 1
        assert status == pyvizier.TrialStatus.ACTIVE
        assert (
            parameters.get_value(_TEST_PARAMETER_ID_1) == _TEST_PARAMETER_ID_MIN_VALUE_1
        )

    @pytest.mark.usefixtures("get_trial_mock")
    def test_materialize(self):
        aiplatform.init(project=_TEST_PROJECT)
        trial = Trial(trial_name=_TEST_TRIAL_NAME)
        measurement = pyvizier.Measurement()
        measurement.metrics["y"] = 4

        materialize_trial = trial.materialize()

        assert materialize_trial.id == 1
        assert (
            materialize_trial.parameters.get_value(_TEST_PARAMETER_ID_1)
            == _TEST_PARAMETER_ID_MIN_VALUE_1
        )
