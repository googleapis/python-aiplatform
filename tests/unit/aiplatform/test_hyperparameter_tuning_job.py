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

import pytest

import copy
from importlib import reload
from unittest import mock
from unittest.mock import patch

import logging
from google.rpc import status_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import hyperparameter_tuning as hpt
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec_compat,
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job_compat,
    job_state as gca_job_state_compat,
    study as gca_study_compat,
)
from google.cloud.aiplatform.compat.services import job_service_client

import constants as test_constants

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = test_constants.TrainingJobConstants._TEST_ID
_TEST_DISPLAY_NAME = "my_hp_job_1234"

_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_STAGING_BUCKET = test_constants.TrainingJobConstants._TEST_STAGING_BUCKET
_TEST_BASE_OUTPUT_DIR = test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR

_TEST_HYPERPARAMETERTUNING_JOB_NAME = (
    f"{_TEST_PARENT}/hyperparameterTuningJobs/{_TEST_ID}"
)

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec_compat.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT


_TEST_NETWORK = test_constants.TrainingJobConstants._TEST_NETWORK

_TEST_TIMEOUT = test_constants.TrainingJobConstants._TEST_TIMEOUT
_TEST_RESTART_JOB_ON_WORKER_RESTART = (
    test_constants.TrainingJobConstants._TEST_RESTART_JOB_ON_WORKER_RESTART
)
_TEST_DISABLE_RETRIES = test_constants.TrainingJobConstants._TEST_DISABLE_RETRIES
_TEST_MAX_WAIT_DURATION = test_constants.TrainingJobConstants._TEST_MAX_WAIT_DURATION

_TEST_METRIC_SPEC_KEY = "test-metric"
_TEST_METRIC_SPEC_VALUE = "maximize"

_TEST_PARALLEL_TRIAL_COUNT = 8
_TEST_MAX_TRIAL_COUNT = 64
_TEST_MAX_FAILED_TRIAL_COUNT = 4
_TEST_SEARCH_ALGORITHM = "random"
_TEST_MEASUREMENT_SELECTION = "best"

_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS

_TEST_CONDITIONAL_PARAMETER_DECAY = hpt.DoubleParameterSpec(
    min=1e-07, max=1, scale="linear", parent_values=[32, 64]
)
_TEST_CONDITIONAL_PARAMETER_LR = hpt.DoubleParameterSpec(
    min=1e-07, max=1, scale="linear", parent_values=[4, 8, 16]
)

_TEST_BASE_HYPERPARAMETER_TUNING_JOB_PROTO = gca_hyperparameter_tuning_job_compat.HyperparameterTuningJob(
    display_name=_TEST_DISPLAY_NAME,
    study_spec=gca_study_compat.StudySpec(
        metrics=[
            gca_study_compat.StudySpec.MetricSpec(
                metric_id=_TEST_METRIC_SPEC_KEY, goal=_TEST_METRIC_SPEC_VALUE.upper()
            )
        ],
        parameters=[
            gca_study_compat.StudySpec.ParameterSpec(
                parameter_id="lr",
                scale_type=gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LOG_SCALE,
                double_value_spec=gca_study_compat.StudySpec.ParameterSpec.DoubleValueSpec(
                    min_value=0.001, max_value=0.1
                ),
            ),
            gca_study_compat.StudySpec.ParameterSpec(
                parameter_id="units",
                scale_type=gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
                integer_value_spec=gca_study_compat.StudySpec.ParameterSpec.IntegerValueSpec(
                    min_value=4, max_value=1028
                ),
            ),
            gca_study_compat.StudySpec.ParameterSpec(
                parameter_id="activation",
                categorical_value_spec=gca_study_compat.StudySpec.ParameterSpec.CategoricalValueSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
            ),
            gca_study_compat.StudySpec.ParameterSpec(
                parameter_id="batch_size",
                scale_type=gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
                discrete_value_spec=gca_study_compat.StudySpec.ParameterSpec.DiscreteValueSpec(
                    values=[4, 8, 16, 32, 64]
                ),
                conditional_parameter_specs=[
                    gca_study_compat.StudySpec.ParameterSpec.ConditionalParameterSpec(
                        parent_discrete_values=gca_study_compat.StudySpec.ParameterSpec.ConditionalParameterSpec.DiscreteValueCondition(
                            values=[32, 64]
                        ),
                        parameter_spec=gca_study_compat.StudySpec.ParameterSpec(
                            double_value_spec=gca_study_compat.StudySpec.ParameterSpec.DoubleValueSpec(
                                min_value=1e-07, max_value=1
                            ),
                            scale_type=gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
                            parameter_id="decay",
                        ),
                    ),
                    gca_study_compat.StudySpec.ParameterSpec.ConditionalParameterSpec(
                        parent_discrete_values=gca_study_compat.StudySpec.ParameterSpec.ConditionalParameterSpec.DiscreteValueCondition(
                            values=[4, 8, 16]
                        ),
                        parameter_spec=gca_study_compat.StudySpec.ParameterSpec(
                            double_value_spec=gca_study_compat.StudySpec.ParameterSpec.DoubleValueSpec(
                                min_value=1e-07, max_value=1
                            ),
                            scale_type=gca_study_compat.StudySpec.ParameterSpec.ScaleType.UNIT_LINEAR_SCALE,
                            parameter_id="learning_rate",
                        ),
                    ),
                ],
            ),
        ],
        algorithm=gca_study_compat.StudySpec.Algorithm.RANDOM_SEARCH,
        measurement_selection_type=gca_study_compat.StudySpec.MeasurementSelectionType.BEST_MEASUREMENT,
    ),
    parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
    max_trial_count=_TEST_MAX_TRIAL_COUNT,
    max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
    trial_job_spec=test_constants.TrainingJobConstants._TEST_BASE_CUSTOM_JOB_PROTO.job_spec,
    labels=_TEST_LABELS,
    encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
)

_TEST_BASE_TRIAL_PROTO = gca_study_compat.Trial()


def _get_hyperparameter_tuning_job_proto(state=None, name=None, error=None):
    hyperparameter_tuning_job_proto = copy.deepcopy(
        _TEST_BASE_HYPERPARAMETER_TUNING_JOB_PROTO
    )
    hyperparameter_tuning_job_proto.name = name
    hyperparameter_tuning_job_proto.state = state
    hyperparameter_tuning_job_proto.error = error

    return hyperparameter_tuning_job_proto


def _get_trial_proto(id=None, state=None):
    trial_proto = copy.deepcopy(_TEST_BASE_TRIAL_PROTO)
    trial_proto.id = id
    trial_proto.state = state
    if state == gca_study_compat.Trial.State.ACTIVE:
        trial_proto.web_access_uris = (
            test_constants.TrainingJobConstants._TEST_WEB_ACCESS_URIS
        )
    return trial_proto


def _get_hyperparameter_tuning_job_proto_with_enable_web_access(
    state=None, name=None, error=None, trials=[]
):
    hyperparameter_tuning_job_proto = _get_hyperparameter_tuning_job_proto(
        state=state,
        name=name,
        error=error,
    )
    hyperparameter_tuning_job_proto.trial_job_spec.enable_web_access = (
        test_constants.TrainingJobConstants._TEST_ENABLE_WEB_ACCESS
    )
    if state == gca_job_state_compat.JobState.JOB_STATE_RUNNING:
        hyperparameter_tuning_job_proto.trials = trials
    return hyperparameter_tuning_job_proto


def _get_hyperparameter_tuning_job_proto_with_spot_strategy(
    state=None, name=None, error=None, trials=[]
):
    hyperparameter_tuning_job_proto = _get_hyperparameter_tuning_job_proto(
        state=state,
        name=name,
        error=error,
    )
    hyperparameter_tuning_job_proto.trial_job_spec.scheduling.strategy = (
        test_constants.TrainingJobConstants._TEST_SPOT_STRATEGY
    )
    if state == gca_job_state_compat.JobState.JOB_STATE_RUNNING:
        hyperparameter_tuning_job_proto.trials = trials
    return hyperparameter_tuning_job_proto


@pytest.fixture
def get_hyperparameter_tuning_job_mock():
    with patch.object(
        job_service_client.JobServiceClient, "get_hyperparameter_tuning_job"
    ) as get_hyperparameter_tuning_job_mock:
        get_hyperparameter_tuning_job_mock.side_effect = [
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_hyperparameter_tuning_job_mock


@pytest.fixture
def get_hyperparameter_tuning_job_mock_with_enable_web_access():
    with patch.object(
        job_service_client.JobServiceClient, "get_hyperparameter_tuning_job"
    ) as get_hyperparameter_tuning_job_mock:
        get_hyperparameter_tuning_job_mock.side_effect = [
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                trials=[
                    _get_trial_proto(
                        id="1", state=gca_study_compat.Trial.State.REQUESTED
                    ),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                trials=[
                    _get_trial_proto(id="1", state=gca_study_compat.Trial.State.ACTIVE),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                trials=[
                    _get_trial_proto(id="1", state=gca_study_compat.Trial.State.ACTIVE),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                trials=[
                    _get_trial_proto(id="1", state=gca_study_compat.Trial.State.ACTIVE),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
                trials=[
                    _get_trial_proto(
                        id="1", state=gca_study_compat.Trial.State.SUCCEEDED
                    ),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
                trials=[
                    _get_trial_proto(
                        id="1", state=gca_study_compat.Trial.State.SUCCEEDED
                    ),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
                trials=[
                    _get_trial_proto(
                        id="1", state=gca_study_compat.Trial.State.SUCCEEDED
                    ),
                ],
            ),
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
                trials=[
                    _get_trial_proto(
                        id="1", state=gca_study_compat.Trial.State.SUCCEEDED
                    ),
                ],
            ),
        ]
        yield get_hyperparameter_tuning_job_mock


@pytest.fixture
def get_hyperparameter_tuning_job_mock_with_fail():
    with patch.object(
        job_service_client.JobServiceClient, "get_hyperparameter_tuning_job"
    ) as get_hyperparameter_tuning_job_mock:
        get_hyperparameter_tuning_job_mock.side_effect = [
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_FAILED,
                error=status_pb2.Status(message="Test Error"),
            ),
        ]
        yield get_hyperparameter_tuning_job_mock


@pytest.fixture
def get_hyperparameter_tuning_job_mock_with_spot_strategy():
    with patch.object(
        job_service_client.JobServiceClient, "get_hyperparameter_tuning_job"
    ) as get_hyperparameter_tuning_job_mock:
        get_hyperparameter_tuning_job_mock.side_effect = [
            _get_hyperparameter_tuning_job_proto_with_spot_strategy(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            ),
            _get_hyperparameter_tuning_job_proto_with_spot_strategy(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_RUNNING,
            ),
            _get_hyperparameter_tuning_job_proto_with_spot_strategy(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED,
            ),
        ]
        yield get_hyperparameter_tuning_job_mock


@pytest.fixture
def create_hyperparameter_tuning_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.return_value = (
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            )
        )
        yield create_hyperparameter_tuning_job_mock


@pytest.fixture
def create_hyperparameter_tuning_job_mock_with_enable_web_access():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.return_value = (
            _get_hyperparameter_tuning_job_proto_with_enable_web_access(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            )
        )
        yield create_hyperparameter_tuning_job_mock


@pytest.fixture
def create_hyperparameter_tuning_job_mock_fail():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.side_effect = RuntimeError("Mock fail")
        yield create_hyperparameter_tuning_job_mock


@pytest.fixture
def create_hyperparameter_tuning_job_mock_with_tensorboard():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        hyperparameter_tuning_job_proto = _get_hyperparameter_tuning_job_proto(
            name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
        )
        hyperparameter_tuning_job_proto.trial_job_spec.tensorboard = (
            test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME
        )
        create_hyperparameter_tuning_job_mock.return_value = (
            hyperparameter_tuning_job_proto
        )
        yield create_hyperparameter_tuning_job_mock


@pytest.fixture
def create_hyperparameter_tuning_job_mock_with_spot_strategy():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.return_value = (
            _get_hyperparameter_tuning_job_proto_with_spot_strategy(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            )
        )
        yield create_hyperparameter_tuning_job_mock


@pytest.mark.usefixtures("google_auth_mock")
class TestHyperparameterTuningJob:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_create_hyperparameter_tuning_job(
        self,
        create_hyperparameter_tuning_job_mock,
        get_hyperparameter_tuning_job_mock,
        sync,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto()

        create_hyperparameter_tuning_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
            timeout=None,
        )

        assert job.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        assert job.network == _TEST_NETWORK
        assert job.trials == []

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_hyperparameter_tuning_job_with_timeout(
        self,
        create_hyperparameter_tuning_job_mock,
        get_hyperparameter_tuning_job_mock,
        sync,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=sync,
            create_request_timeout=180.0,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto()

        create_hyperparameter_tuning_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
            timeout=180.0,
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_run_hyperparameter_tuning_job_with_fail_raises(
        self,
        create_hyperparameter_tuning_job_mock,
        get_hyperparameter_tuning_job_mock_with_fail,
        sync,
    ):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
            labels=_TEST_LABELS,
        )

        with pytest.raises(RuntimeError):
            job.run(
                service_account=_TEST_SERVICE_ACCOUNT,
                network=_TEST_NETWORK,
                timeout=_TEST_TIMEOUT,
                restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
                sync=sync,
                create_request_timeout=None,
                disable_retries=_TEST_DISABLE_RETRIES,
                max_wait_duration=_TEST_MAX_WAIT_DURATION,
            )

            job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto()

        create_hyperparameter_tuning_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
            timeout=None,
        )

        assert job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_FAILED

    @pytest.mark.usefixtures("create_hyperparameter_tuning_job_mock_fail")
    def test_run_hyperparameter_tuning_job_with_fail_at_creation(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            sync=False,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        with pytest.raises(RuntimeError) as e:
            job.wait_for_resource_creation()
        assert e.match("Mock fail")

        with pytest.raises(RuntimeError) as e:
            job.resource_name
        assert e.match(
            "HyperparameterTuningJob resource has not been created. Resource failed with: Mock fail"
        )

        with pytest.raises(RuntimeError) as e:
            job.network
        assert e.match(
            "HyperparameterTuningJob resource has not been created. Resource failed with: Mock fail"
        )

        with pytest.raises(RuntimeError) as e:
            job.trials
        assert e.match(
            "HyperparameterTuningJob resource has not been created. Resource failed with: Mock fail"
        )

    def test_hyperparameter_tuning_job_get_state_raises_without_run(self):
        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
        )

        with pytest.raises(RuntimeError):
            print(job.state)

    def test_get_hyperparameter_tuning_job(self, get_hyperparameter_tuning_job_mock):

        job = aiplatform.HyperparameterTuningJob.get(
            _TEST_HYPERPARAMETERTUNING_JOB_NAME
        )

        get_hyperparameter_tuning_job_mock.assert_called_once_with(
            name=_TEST_HYPERPARAMETERTUNING_JOB_NAME, retry=base._DEFAULT_RETRY
        )
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_PENDING
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_hyperparameter_tuning_job_with_tensorboard(
        self,
        create_hyperparameter_tuning_job_mock_with_tensorboard,
        get_hyperparameter_tuning_job_mock,
        sync,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            tensorboard=test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto()
        expected_hyperparameter_tuning_job.trial_job_spec.tensorboard = (
            test_constants.TensorboardConstants._TEST_TENSORBOARD_NAME
        )

        create_hyperparameter_tuning_job_mock_with_tensorboard.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
            timeout=None,
        )

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )

    @pytest.mark.parametrize("sync", [True, False])
    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_create_hyperparameter_tuning_job_with_enable_web_access(
        self,
        create_hyperparameter_tuning_job_mock_with_enable_web_access,
        get_hyperparameter_tuning_job_mock_with_enable_web_access,
        sync,
        caplog,
    ):
        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            enable_web_access=test_constants.TrainingJobConstants._TEST_ENABLE_WEB_ACCESS,
            sync=sync,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait()

        assert "workerpool0-0" in caplog.text

        expected_hyperparameter_tuning_job = (
            _get_hyperparameter_tuning_job_proto_with_enable_web_access()
        )

        create_hyperparameter_tuning_job_mock_with_enable_web_access.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
            timeout=None,
        )

        assert job.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        assert job.network == _TEST_NETWORK
        assert job.trials == []

        caplog.clear()

    @mock.patch.object(jobs, "_JOB_WAIT_TIME", 1)
    @mock.patch.object(jobs, "_LOG_WAIT_TIME", 1)
    def test_log_enable_web_access_after_get_hyperparameter_tuning_job(
        self,
        get_hyperparameter_tuning_job_mock_with_enable_web_access,
    ):

        hp_job = aiplatform.HyperparameterTuningJob.get(
            _TEST_HYPERPARAMETERTUNING_JOB_NAME
        )
        hp_job._block_until_complete()
        assert hp_job._logged_web_access_uris == set(
            test_constants.TrainingJobConstants._TEST_WEB_ACCESS_URIS.values()
        )

    def test_create_hyperparameter_tuning_job_with_spot_strategy(
        self,
        create_hyperparameter_tuning_job_mock_with_spot_strategy,
        get_hyperparameter_tuning_job_mock_with_spot_strategy,
    ):

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
            encryption_spec_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME,
        )

        custom_job = aiplatform.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
        )

        job = aiplatform.HyperparameterTuningJob(
            display_name=_TEST_DISPLAY_NAME,
            custom_job=custom_job,
            metric_spec={_TEST_METRIC_SPEC_KEY: _TEST_METRIC_SPEC_VALUE},
            parameter_spec={
                "lr": hpt.DoubleParameterSpec(min=0.001, max=0.1, scale="log"),
                "units": hpt.IntegerParameterSpec(min=4, max=1028, scale="linear"),
                "activation": hpt.CategoricalParameterSpec(
                    values=["relu", "sigmoid", "elu", "selu", "tanh"]
                ),
                "batch_size": hpt.DiscreteParameterSpec(
                    values=[4, 8, 16, 32, 64],
                    scale="linear",
                    conditional_parameter_spec={
                        "decay": _TEST_CONDITIONAL_PARAMETER_DECAY,
                        "learning_rate": _TEST_CONDITIONAL_PARAMETER_LR,
                    },
                ),
            },
            parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
            max_trial_count=_TEST_MAX_TRIAL_COUNT,
            max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
            search_algorithm=_TEST_SEARCH_ALGORITHM,
            measurement_selection=_TEST_MEASUREMENT_SELECTION,
            labels=_TEST_LABELS,
        )

        job.run(
            service_account=_TEST_SERVICE_ACCOUNT,
            network=_TEST_NETWORK,
            timeout=_TEST_TIMEOUT,
            restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
            create_request_timeout=None,
            disable_retries=_TEST_DISABLE_RETRIES,
            scheduling_strategy=test_constants.TrainingJobConstants._TEST_SPOT_STRATEGY,
            max_wait_duration=_TEST_MAX_WAIT_DURATION,
        )

        job.wait()

        expected_hyperparameter_tuning_job = (
            _get_hyperparameter_tuning_job_proto_with_spot_strategy()
        )

        create_hyperparameter_tuning_job_mock_with_spot_strategy.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
            timeout=None,
        )
