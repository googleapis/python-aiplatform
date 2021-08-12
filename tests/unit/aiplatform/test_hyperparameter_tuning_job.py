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

from google.rpc import status_pb2

from google.cloud import aiplatform
from google.cloud.aiplatform import hyperparameter_tuning as hpt
from google.cloud.aiplatform.compat.types import job_state as gca_job_state_compat
from google.cloud.aiplatform.compat.types import (
    encryption_spec as gca_encryption_spec_compat,
)
from google.cloud.aiplatform.compat.types import (
    hyperparameter_tuning_job as gca_hyperparameter_tuning_job_compat,
    hyperparameter_tuning_job_v1beta1 as gca_hyperparameter_tuning_job_v1beta1,
)
from google.cloud.aiplatform.compat.types import study as gca_study_compat
from google.cloud.aiplatform_v1.services.job_service import client as job_service_client
from google.cloud.aiplatform_v1beta1.services.job_service import (
    client as job_service_client_v1beta1,
)

import test_custom_job

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = "my_hp_job_1234"

_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"

_TEST_STAGING_BUCKET = test_custom_job._TEST_STAGING_BUCKET
_TEST_BASE_OUTPUT_DIR = test_custom_job._TEST_BASE_OUTPUT_DIR

_TEST_HYPERPARAMETERTUNING_JOB_NAME = (
    f"{_TEST_PARENT}/hyperparameterTuningJobs/{_TEST_ID}"
)

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_default"
_TEST_DEFAULT_ENCRYPTION_SPEC = gca_encryption_spec_compat.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = "vinnys@my-project.iam.gserviceaccount.com"


_TEST_NETWORK = f"projects/{_TEST_PROJECT}/global/networks/{_TEST_ID}"

_TEST_TIMEOUT = 8000
_TEST_RESTART_JOB_ON_WORKER_RESTART = True

_TEST_METRIC_SPEC_KEY = "test-metric"
_TEST_METRIC_SPEC_VALUE = "maximize"

_TEST_PARALLEL_TRIAL_COUNT = 8
_TEST_MAX_TRIAL_COUNT = 64
_TEST_MAX_FAILED_TRIAL_COUNT = 4
_TEST_SEARCH_ALGORITHM = "random"
_TEST_MEASUREMENT_SELECTION = "best"

_TEST_LABELS = {"my_hp_key": "my_hp_value"}

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
                    values=[16, 32]
                ),
            ),
        ],
        algorithm=gca_study_compat.StudySpec.Algorithm.RANDOM_SEARCH,
        measurement_selection_type=gca_study_compat.StudySpec.MeasurementSelectionType.BEST_MEASUREMENT,
    ),
    parallel_trial_count=_TEST_PARALLEL_TRIAL_COUNT,
    max_trial_count=_TEST_MAX_TRIAL_COUNT,
    max_failed_trial_count=_TEST_MAX_FAILED_TRIAL_COUNT,
    trial_job_spec=test_custom_job._TEST_BASE_CUSTOM_JOB_PROTO.job_spec,
    labels=_TEST_LABELS,
    encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
)


def _get_hyperparameter_tuning_job_proto(
    state=None, name=None, error=None, version="v1"
):
    hyperparameter_tuning_job_proto = copy.deepcopy(
        _TEST_BASE_HYPERPARAMETER_TUNING_JOB_PROTO
    )
    hyperparameter_tuning_job_proto.name = name
    hyperparameter_tuning_job_proto.state = state
    hyperparameter_tuning_job_proto.error = error

    if version == "v1beta1":
        v1beta1_hyperparameter_tuning_job_proto = (
            gca_hyperparameter_tuning_job_v1beta1.HyperparameterTuningJob()
        )
        v1beta1_hyperparameter_tuning_job_proto._pb.MergeFromString(
            hyperparameter_tuning_job_proto._pb.SerializeToString()
        )
        hyperparameter_tuning_job_proto = v1beta1_hyperparameter_tuning_job_proto
        hyperparameter_tuning_job_proto.trial_job_spec.tensorboard = (
            test_custom_job._TEST_TENSORBOARD_NAME
        )

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
def create_hyperparameter_tuning_job_mock():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.return_value = _get_hyperparameter_tuning_job_proto(
            name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
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
def create_hyperparameter_tuning_job_v1beta1_mock():
    with mock.patch.object(
        job_service_client_v1beta1.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.return_value = _get_hyperparameter_tuning_job_proto(
            name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
            state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            version="v1beta1",
        )
        yield create_hyperparameter_tuning_job_mock


class TestHyperparameterTuningJob:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
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
            display_name=test_custom_job._TEST_DISPLAY_NAME,
            worker_pool_specs=test_custom_job._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_custom_job._TEST_BASE_OUTPUT_DIR,
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
                    values=[16, 32], scale="linear"
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
        )

        job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto()

        create_hyperparameter_tuning_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
        )

        assert job.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        assert job.network == _TEST_NETWORK
        assert job.trials == []

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
            display_name=test_custom_job._TEST_DISPLAY_NAME,
            worker_pool_specs=test_custom_job._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_custom_job._TEST_BASE_OUTPUT_DIR,
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
                    values=[16, 32], scale="linear"
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
            )

            job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto()

        create_hyperparameter_tuning_job_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
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
            display_name=test_custom_job._TEST_DISPLAY_NAME,
            worker_pool_specs=test_custom_job._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_custom_job._TEST_BASE_OUTPUT_DIR,
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
                    values=[16, 32], scale="linear"
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
            display_name=test_custom_job._TEST_DISPLAY_NAME,
            worker_pool_specs=test_custom_job._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_custom_job._TEST_BASE_OUTPUT_DIR,
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
                    values=[16, 32, 64], scale="linear"
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
            name=_TEST_HYPERPARAMETERTUNING_JOB_NAME
        )
        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_PENDING
        )

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_hyperparameter_tuning_job_with_tensorboard(
        self,
        create_hyperparameter_tuning_job_v1beta1_mock,
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
            display_name=test_custom_job._TEST_DISPLAY_NAME,
            worker_pool_specs=test_custom_job._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_custom_job._TEST_BASE_OUTPUT_DIR,
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
                    values=[16, 32], scale="linear"
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
            tensorboard=test_custom_job._TEST_TENSORBOARD_NAME,
            sync=sync,
        )

        job.wait()

        expected_hyperparameter_tuning_job = _get_hyperparameter_tuning_job_proto(
            version="v1beta1"
        )

        create_hyperparameter_tuning_job_v1beta1_mock.assert_called_once_with(
            parent=_TEST_PARENT,
            hyperparameter_tuning_job=expected_hyperparameter_tuning_job,
        )

        assert (
            job._gca_resource.state == gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        )
