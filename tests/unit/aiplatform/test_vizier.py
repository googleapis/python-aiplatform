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

from importlib import reload
from unittest import mock
from unittest.mock import ANY
from unittest.mock import patch

import attr
from google.api_core import exceptions
from google.api_core import operation
from google.cloud import aiplatform
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform.compat.services import vizier_service_client
from google.cloud.aiplatform.compat.types import study as study_pb2
from google.cloud.aiplatform.compat.types import study as gca_study
from google.cloud.aiplatform.compat.types import (
    vizier_service as gca_vizier_service,
)
from google.cloud.aiplatform.vizier import pyvizier
from google.cloud.aiplatform.vizier import Study
from google.cloud.aiplatform.vizier import Trial
from google.cloud.aiplatform.vizier.pyvizier import proto_converters
import pytest

from google.protobuf import duration_pb2
from google.protobuf import struct_pb2
from google.protobuf import timestamp_pb2


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
        assert isinstance(study, Study)

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
        assert isinstance(study, Study)

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
        assert isinstance(study_config, pyvizier.StudyConfig)

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
        assert isinstance(trials[0], Trial)

    @pytest.mark.usefixtures("get_study_mock")
    def test_from_uid(self):
        aiplatform.init(project=_TEST_PROJECT)

        study = Study.from_uid(uid=_TEST_STUDY_ID)

        assert isinstance(study, Study)
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
        assert isinstance(trials[0], Trial)

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
        assert isinstance(trials[0], Trial)

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
        assert isinstance(trial, Trial)


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
        assert isinstance(trial, Trial)

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
        assert isinstance(measurement, pyvizier.Measurement)

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


class TestMeasurementConverter:
    def test_measurement_proto_with_empty_named_metric(self):
        proto = study_pb2.Measurement()
        proto.metrics.append(study_pb2.Measurement.Metric(metric_id="", value=0.8))

        measurement = proto_converters.MeasurementConverter.from_proto(proto)
        assert measurement.metrics[""] == pyvizier.Metric(value=0.8)

    def test_measurement_creation(self):
        measurement = pyvizier.Measurement(
            metrics={
                "": pyvizier.Metric(value=0),
                # The empty metric always exists in Measurement.
                "pr-auc:": pyvizier.Metric(value=0.8),
                "latency": pyvizier.Metric(value=32),
            },
            elapsed_secs=12,
            steps=12,
        )
        proto = proto_converters.MeasurementConverter.to_proto(measurement)
        assert attr.asdict(
            proto_converters.MeasurementConverter.from_proto(proto)
        ) == attr.asdict(measurement)


class TestParameterValueConverter:
    def test_to_double_proto(self):
        value = pyvizier.ParameterValue(True)
        assert proto_converters.ParameterValueConverter.to_proto(
            value, "aa"
        ) == study_pb2.Trial.Parameter(
            parameter_id="aa", value=struct_pb2.Value(number_value=1.0)
        )

    def test_to_discrete_proto(self):
        value = pyvizier.ParameterValue(True)
        assert proto_converters.ParameterValueConverter.to_proto(
            value, "aa"
        ) == study_pb2.Trial.Parameter(
            parameter_id="aa", value=struct_pb2.Value(number_value=1.0)
        )

    def testto_string_proto(self):
        value = pyvizier.ParameterValue("category")
        assert proto_converters.ParameterValueConverter.to_proto(
            value, "aa"
        ) == study_pb2.Trial.Parameter(
            parameter_id="aa", value=struct_pb2.Value(string_value="category")
        )

    def test_to_integer_proto(self):
        value = pyvizier.ParameterValue(True)
        assert proto_converters.ParameterValueConverter.to_proto(
            value, "aa"
        ) == study_pb2.Trial.Parameter(
            parameter_id="aa", value=struct_pb2.Value(number_value=1.0)
        )


class TestTrialConverter:
    def test_from_proto_completed(self):
        proto = study_pb2.Trial(name=str(1))
        proto.state = study_pb2.Trial.State.SUCCEEDED
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="float", value=struct_pb2.Value(number_value=1.0)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="int", value=struct_pb2.Value(number_value=2)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="str", value=struct_pb2.Value(string_value="3")
            )
        )
        proto.final_measurement.metrics.append(
            study_pb2.Measurement.Metric(metric_id="pr-auc", value=0.8)
        )
        proto.final_measurement.metrics.append(
            study_pb2.Measurement.Metric(metric_id="latency", value=32)
        )

        creation_secs = 1586649600
        start_time = timestamp_pb2.Timestamp(
            seconds=int(creation_secs),
            nanos=int(1e9 * (creation_secs - int(creation_secs))),
        )
        setattr(proto, "start_time", start_time)

        completion_secs = 1586649600 + 10
        end_time = timestamp_pb2.Timestamp(
            seconds=int(completion_secs),
            nanos=int(1e9 * (completion_secs - int(completion_secs))),
        )
        setattr(proto, "end_time", end_time)

        proto.measurements.append(
            study_pb2.Measurement(
                step_count=10, elapsed_duration=duration_pb2.Duration(seconds=15)
            )
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="pr-auc", value=0.7)
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="latency", value=42)
        )

        proto.measurements.append(
            study_pb2.Measurement(
                step_count=20, elapsed_duration=duration_pb2.Duration(seconds=30)
            )
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="pr-auc", value=0.75)
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="latency", value=37)
        )

        test = proto_converters.TrialConverter.from_proto(proto=proto)
        assert test.id == 1
        assert test.status == pyvizier.TrialStatus.COMPLETED
        assert test.is_completed
        assert not test.infeasible
        assert test.infeasibility_reason is None
        assert len(test.parameters) == 3
        assert test.parameters["float"].value == 1.0
        assert test.parameters["int"].value == 2
        assert test.parameters["str"].value == "3"

        # Final measurement
        assert len(test.final_measurement.metrics) == 2
        assert test.final_measurement.metrics["pr-auc"].value == 0.8
        assert test.final_measurement.metrics["latency"].value == 32

        # Intermediate measurement
        assert test.measurements[0] == pyvizier.Measurement(
            metrics={"pr-auc": 0.7, "latency": 42}, steps=10, elapsed_secs=15
        )

        assert test.measurements[1] == pyvizier.Measurement(
            metrics={"pr-auc": 0.75, "latency": 37}, steps=20, elapsed_secs=30
        )

        assert test.id == 1

        assert test.creation_time is not None
        assert test.creation_time.timestamp() == start_time.seconds
        assert test.completion_time is not None
        assert test.completion_time.timestamp() == end_time.seconds
        assert test.duration.total_seconds() == 10

        assert not test.infeasible

    def test_from_proto_pending(self):
        proto = study_pb2.Trial(name=str(2))
        proto.state = study_pb2.Trial.State.ACTIVE

        start_time = timestamp_pb2.Timestamp(seconds=int(1586649600))
        setattr(proto, "start_time", start_time)

        test = proto_converters.TrialConverter.from_proto(proto=proto)
        assert test.status == pyvizier.TrialStatus.ACTIVE
        assert not test.is_completed
        assert not test.infeasible
        assert test.infeasibility_reason is None
        assert test.creation_time is not None
        assert test.completion_time is None
        assert test.duration is None

    def test_from_proto_infeasible(self):
        proto = study_pb2.Trial(name=str(1))
        proto.state = study_pb2.Trial.State.INFEASIBLE
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="float", value=struct_pb2.Value(number_value=1.0)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="int", value=struct_pb2.Value(number_value=2)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="str", value=struct_pb2.Value(string_value="3")
            )
        )

        start_time = timestamp_pb2.Timestamp(seconds=int(1586649600))
        setattr(proto, "start_time", start_time)
        end_time = timestamp_pb2.Timestamp(seconds=int(1586649600 + 10))
        setattr(proto, "end_time", end_time)
        setattr(proto, "infeasible_reason", "A reason")

        test = proto_converters.TrialConverter.from_proto(proto=proto)
        assert test.status == pyvizier.TrialStatus.COMPLETED
        assert test.is_completed
        assert test.infeasible
        assert test.infeasibility_reason == "A reason"

    def test_from_proto_invalid_trial(self):
        proto = study_pb2.Trial(name=str(2))
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="float", value=struct_pb2.Value(number_value=1.0)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="float", value=struct_pb2.Value(number_value=2.0)
            )
        )
        proto.state = study_pb2.Trial.State.ACTIVE
        start_time = timestamp_pb2.Timestamp(seconds=int(1586649600))
        setattr(proto, "start_time", start_time)
        try:
            proto_converters.TrialConverter.from_proto(proto=proto)
        except ValueError as e:
            assert "Invalid trial proto" in str(e)


class TestTrialConverterToProto:
    def _get_single_objective_base_trial(self):
        proto = study_pb2.Trial(
            name="owners/my_username/studies/2", id="2", client_id="worker0"
        )

        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="activation", value=struct_pb2.Value(string_value="relu")
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="synchronus", value=struct_pb2.Value(string_value="true")
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="batch_size", value=struct_pb2.Value(number_value=32)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="floating_point_param",
                value=struct_pb2.Value(number_value=32.0),
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="learning_rate", value=struct_pb2.Value(number_value=0.5)
            )
        )
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="units", value=struct_pb2.Value(number_value=50)
            )
        )
        creation_secs = 1630505100
        start_time = timestamp_pb2.Timestamp(
            seconds=int(creation_secs),
            nanos=int(1e9 * (creation_secs - int(creation_secs))),
        )
        setattr(proto, "start_time", start_time)
        return proto

    def test_parameter_back_to_back_conversion(self):
        proto = self._get_single_objective_base_trial()
        proto.state = study_pb2.Trial.State.ACTIVE
        pytrial = proto_converters.TrialConverter.from_proto(proto)
        got = proto_converters.TrialConverter.to_proto(pytrial)
        assert proto == got

    def test_final_measurement_back_to_back_conversion(self):
        proto = study_pb2.Trial(
            name=str(1),
            id=str(1),
            state=study_pb2.Trial.State.SUCCEEDED,
            final_measurement=gca_study.Measurement(
                step_count=101, elapsed_duration=duration_pb2.Duration(seconds=67)
            ),
        )
        creation_secs = 12456
        start_time = timestamp_pb2.Timestamp(
            seconds=int(creation_secs),
            nanos=int(1e9 * (creation_secs - int(creation_secs))),
        )
        setattr(proto, "start_time", start_time)

        completion_secs = 12456 + 10
        end_time = timestamp_pb2.Timestamp(
            seconds=int(completion_secs),
            nanos=int(1e9 * (completion_secs - int(completion_secs))),
        )
        setattr(proto, "end_time", end_time)
        proto.parameters.append(
            study_pb2.Trial.Parameter(
                parameter_id="learning_rate", value=struct_pb2.Value(number_value=0.5)
            )
        )
        proto.final_measurement.metrics.append(
            study_pb2.Measurement.Metric(metric_id="loss", value=56.8)
        )
        proto.final_measurement.metrics.append(
            study_pb2.Measurement.Metric(metric_id="objective", value=77.7)
        )
        proto.final_measurement.metrics.append(
            study_pb2.Measurement.Metric(metric_id="objective2", value=-0.2)
        )

        pytrial = proto_converters.TrialConverter.from_proto(proto)
        got = proto_converters.TrialConverter.to_proto(pytrial)
        assert proto == got

    def test_measurement_back_to_back_conversion(self):
        proto = study_pb2.Trial(
            name=str(2),
            id=str(2),
            state=study_pb2.Trial.State.ACTIVE,
            client_id="worker0",
        )
        creation_secs = 1630505100
        start_time = timestamp_pb2.Timestamp(
            seconds=int(creation_secs),
            nanos=int(1e9 * (creation_secs - int(creation_secs))),
        )
        setattr(proto, "start_time", start_time)
        proto.measurements.append(
            study_pb2.Measurement(
                step_count=123, elapsed_duration=duration_pb2.Duration(seconds=22)
            )
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="objective", value=0.4321)
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="loss", value=0.001)
        )

        proto.measurements.append(
            study_pb2.Measurement(
                step_count=789, elapsed_duration=duration_pb2.Duration(seconds=55)
            )
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="objective", value=0.21)
        )
        proto.measurements[-1].metrics.append(
            study_pb2.Measurement.Metric(metric_id="loss", value=0.0001)
        )

        pytrial = proto_converters.TrialConverter.from_proto(proto)
        got = proto_converters.TrialConverter.to_proto(pytrial)
        assert proto == got


class TestParameterConfigConverterToProto:
    def test_discrete_config_to_proto(self):
        feasible_values = (-1, 3, 2)
        child_parameter_config = pyvizier.ParameterConfig.factory(
            "child", bounds=(-1.0, 1.0)
        )
        parameter_config = pyvizier.ParameterConfig.factory(
            "name",
            feasible_values=feasible_values,
            scale_type=pyvizier.ScaleType.LOG,
            default_value=2,
            children=[([-1], child_parameter_config)],
        )

        proto = proto_converters.ParameterConfigConverter.to_proto(parameter_config)
        assert proto.parameter_id == "name"
        assert proto.discrete_value_spec.values == [-1.0, 2.0, 3.0]
        assert proto.discrete_value_spec.default_value == 2
        assert (
            proto.scale_type
            == study_pb2.StudySpec.ParameterSpec.ScaleType.UNIT_LOG_SCALE
        )
        assert len(proto.conditional_parameter_specs) == 1

        spec = proto.conditional_parameter_specs[0]
        assert spec.parameter_spec.parameter_id == "child"
        assert spec.parameter_spec.double_value_spec.min_value == -1.0
        assert spec.parameter_spec.double_value_spec.max_value == 1.0
        assert len(spec.parent_discrete_values.values) == 1
        assert spec.parent_discrete_values.values[0] == -1

    def test_categorical_config_to_proto_with_children(self):
        feasible_values = ("option_a", "option_b")
        child_parameter_config = pyvizier.ParameterConfig.factory(
            "child", bounds=(-1.0, 1.0)
        )
        parameter_config = pyvizier.ParameterConfig.factory(
            "name",
            feasible_values=feasible_values,
            children=[(["option_a"], child_parameter_config)],
        )
        proto = proto_converters.ParameterConfigConverter.to_proto(parameter_config)
        assert len(proto.conditional_parameter_specs) == 1
        spec = proto.conditional_parameter_specs[0]
        assert len(spec.parent_categorical_values.values) == 1
        assert spec.parent_categorical_values.values[0] == "option_a"

    def test_integer_config_to_proto_with_children(self):
        child_parameter_config = pyvizier.ParameterConfig.factory(
            "child", bounds=(-1.0, 1.0)
        )
        parameter_config = pyvizier.ParameterConfig.factory(
            "name", bounds=(1, 10), children=[([6], child_parameter_config)]
        )
        proto = proto_converters.ParameterConfigConverter.to_proto(parameter_config)
        assert len(proto.conditional_parameter_specs) == 1
        spec = proto.conditional_parameter_specs[0]
        assert len(spec.parent_int_values.values) == 1
        assert spec.parent_int_values.values[0] == 6


class TestParameterConfigConverterFromProto:
    """Test ParameterConfigConverter.from_proto."""

    def test_from_proto_discrete(self):
        """Test from_proto."""
        proto = study_pb2.StudySpec.ParameterSpec(
            parameter_id="name",
            discrete_value_spec=study_pb2.StudySpec.ParameterSpec.DiscreteValueSpec(
                values=[1.0, 2.0, 3.0], default_value=2.0
            ),
        )

        parameter_config = proto_converters.ParameterConfigConverter.from_proto(proto)

        assert parameter_config.name == proto.parameter_id
        assert parameter_config.type == pyvizier.ParameterType.DISCRETE
        assert parameter_config.bounds == (1.0, 3.0)
        assert parameter_config.feasible_values == [1.0, 2.0, 3.0]
        assert parameter_config.default_value == 2.0
        assert parameter_config.external_type == pyvizier.ExternalType.INTERNAL

    def test_from_proto_integer(self):
        """Test from_proto."""
        proto = study_pb2.StudySpec.ParameterSpec(
            parameter_id="name",
            integer_value_spec=study_pb2.StudySpec.ParameterSpec.IntegerValueSpec(
                default_value=2, min_value=1, max_value=3
            ),
        )

        parameter_config = proto_converters.ParameterConfigConverter.from_proto(proto)

        assert parameter_config.name == proto.parameter_id
        assert parameter_config.type == pyvizier.ParameterType.INTEGER
        assert parameter_config.bounds == (1, 3)
        assert parameter_config.default_value == 2
        assert parameter_config.external_type == pyvizier.ExternalType.INTEGER

    def test_from_proto_bool(self):
        """Test from_proto."""
        proto = study_pb2.StudySpec.ParameterSpec(
            parameter_id="name",
            categorical_value_spec=study_pb2.StudySpec.ParameterSpec.CategoricalValueSpec(
                default_value="True", values=["True", "False"]
            ),
        )

        parameter_config = proto_converters.ParameterConfigConverter.from_proto(proto)

        assert parameter_config.name == proto.parameter_id
        assert parameter_config.type == pyvizier.ParameterType.CATEGORICAL
        assert parameter_config.feasible_values == ["False", "True"]
        assert parameter_config.default_value == "True"
        assert parameter_config.external_type == pyvizier.ExternalType.BOOLEAN
