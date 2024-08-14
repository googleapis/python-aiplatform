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

import copy
from importlib import reload
from unittest import mock
from unittest.mock import patch

from google.cloud import aiplatform
from google.cloud.aiplatform.compat.services import (
    job_service_client_v1,
)
from google.cloud.aiplatform import hyperparameter_tuning as hpt
from google.cloud.aiplatform.compat.types import (
    custom_job_v1,
    encryption_spec_v1,
    hyperparameter_tuning_job_v1,
    io_v1,
    job_state_v1 as gca_job_state_compat,
    study_v1 as gca_study_compat,
)
from google.cloud.aiplatform import jobs
import constants as test_constants
import pytest

from google.protobuf import duration_pb2

_TEST_PROJECT = test_constants.ProjectConstants._TEST_PROJECT
_TEST_LOCATION = test_constants.ProjectConstants._TEST_LOCATION
_TEST_ID = "1028944691210842416"
_TEST_DISPLAY_NAME = test_constants.TrainingJobConstants._TEST_DISPLAY_NAME

_TEST_PARENT = test_constants.ProjectConstants._TEST_PARENT

_TEST_HYPERPARAMETERTUNING_JOB_NAME = (
    f"{_TEST_PARENT}/hyperparameterTuningJobs/{_TEST_ID}"
)

_TEST_PREBUILT_CONTAINER_IMAGE = "gcr.io/cloud-aiplatform/container:image"

_TEST_RUN_ARGS = test_constants.TrainingJobConstants._TEST_RUN_ARGS
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXPERIMENT_RUN = "test-experiment-run"

_TEST_STAGING_BUCKET = test_constants.TrainingJobConstants._TEST_STAGING_BUCKET

# CMEK encryption
_TEST_DEFAULT_ENCRYPTION_KEY_NAME = "key_1234"
_TEST_DEFAULT_ENCRYPTION_SPEC = encryption_spec_v1.EncryptionSpec(
    kms_key_name=_TEST_DEFAULT_ENCRYPTION_KEY_NAME
)

_TEST_SERVICE_ACCOUNT = test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT

_TEST_METRIC_SPEC_KEY = "test-metric"
_TEST_METRIC_SPEC_VALUE = "maximize"

_TEST_PARALLEL_TRIAL_COUNT = 8
_TEST_MAX_TRIAL_COUNT = 64
_TEST_MAX_FAILED_TRIAL_COUNT = 4
_TEST_SEARCH_ALGORITHM = "random"
_TEST_MEASUREMENT_SELECTION = "best"

_TEST_NETWORK = test_constants.TrainingJobConstants._TEST_NETWORK

_TEST_TIMEOUT = test_constants.TrainingJobConstants._TEST_TIMEOUT
_TEST_RESTART_JOB_ON_WORKER_RESTART = (
    test_constants.TrainingJobConstants._TEST_RESTART_JOB_ON_WORKER_RESTART
)
_TEST_DISABLE_RETRIES = test_constants.TrainingJobConstants._TEST_DISABLE_RETRIES

_TEST_LABELS = test_constants.ProjectConstants._TEST_LABELS

_TEST_CONDITIONAL_PARAMETER_DECAY = hpt.DoubleParameterSpec(
    min=1e-07, max=1, scale="linear", parent_values=[32, 64]
)
_TEST_CONDITIONAL_PARAMETER_LR = hpt.DoubleParameterSpec(
    min=1e-07, max=1, scale="linear", parent_values=[4, 8, 16]
)


# Persistent Resource
_TEST_PERSISTENT_RESOURCE_ID = "test-persistent-resource-1"

_TEST_TRIAL_JOB_SPEC = custom_job_v1.CustomJobSpec(
    worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
    base_output_directory=io_v1.GcsDestination(
        output_uri_prefix=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR
    ),
    scheduling=custom_job_v1.Scheduling(
        timeout=duration_pb2.Duration(seconds=_TEST_TIMEOUT),
        restart_job_on_worker_restart=_TEST_RESTART_JOB_ON_WORKER_RESTART,
        disable_retries=_TEST_DISABLE_RETRIES,
    ),
    service_account=test_constants.ProjectConstants._TEST_SERVICE_ACCOUNT,
    network=_TEST_NETWORK,
    persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
)

_TEST_BASE_HYPERPARAMETER_TUNING_JOB_WITH_PERSISTENT_RESOURCE_PROTO = hyperparameter_tuning_job_v1.HyperparameterTuningJob(
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
    trial_job_spec=_TEST_TRIAL_JOB_SPEC,
    labels=_TEST_LABELS,
    encryption_spec=_TEST_DEFAULT_ENCRYPTION_SPEC,
)


def _get_hyperparameter_tuning_job_proto(state=None, name=None, error=None):
    hyperparameter_tuning_job_proto = copy.deepcopy(
        _TEST_BASE_HYPERPARAMETER_TUNING_JOB_WITH_PERSISTENT_RESOURCE_PROTO
    )
    hyperparameter_tuning_job_proto.name = name
    hyperparameter_tuning_job_proto.state = state
    hyperparameter_tuning_job_proto.error = error

    return hyperparameter_tuning_job_proto


@pytest.fixture
def create_hyperparameter_tuning_job_mock():
    with mock.patch.object(
        job_service_client_v1.JobServiceClient, "create_hyperparameter_tuning_job"
    ) as create_hyperparameter_tuning_job_mock:
        create_hyperparameter_tuning_job_mock.return_value = (
            _get_hyperparameter_tuning_job_proto(
                name=_TEST_HYPERPARAMETERTUNING_JOB_NAME,
                state=gca_job_state_compat.JobState.JOB_STATE_PENDING,
            )
        )
        yield create_hyperparameter_tuning_job_mock


@pytest.fixture
def get_hyperparameter_tuning_job_mock():
    with patch.object(
        job_service_client_v1.JobServiceClient, "get_hyperparameter_tuning_job"
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


@pytest.mark.usefixtures("google_auth_mock")
class TestHyperparameterTuningJobPersistentResource:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.parametrize("sync", [True, False])
    def test_create_hyperparameter_tuning_job_with_persistent_resource(
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

        custom_job = jobs.CustomJob(
            display_name=test_constants.TrainingJobConstants._TEST_DISPLAY_NAME,
            worker_pool_specs=test_constants.TrainingJobConstants._TEST_WORKER_POOL_SPEC,
            base_output_dir=test_constants.TrainingJobConstants._TEST_BASE_OUTPUT_DIR,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )

        job = jobs.HyperparameterTuningJob(
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
