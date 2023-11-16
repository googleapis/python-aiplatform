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
import os
import re
import sys
from unittest import mock
from unittest.mock import patch

import cloudpickle
from google.api_core import exceptions
from google.cloud import aiplatform
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.services import (
    job_service_client_v1beta1 as job_service_client,
)
from google.cloud.aiplatform.compat.types import (
    custom_job_v1beta1 as gca_custom_job_compat,
)
from google.cloud.aiplatform.compat.types import (
    execution_v1beta1 as gca_execution,
)
from google.cloud.aiplatform.compat.types import io_v1beta1 as gca_io_compat
from google.cloud.aiplatform.compat.types import (
    job_state_v1beta1 as gca_job_state_compat,
)
from google.cloud.aiplatform.compat.types import (
    tensorboard as gca_tensorboard,
)
from google.cloud.aiplatform.metadata import constants as metadata_constants
from google.cloud.aiplatform.preview import resource_pool_utils
from google.cloud.aiplatform_v1 import (
    Context as GapicContext,
    MetadataServiceClient,
    MetadataStore as GapicMetadataStore,
    TensorboardServiceClient,
)
import vertexai
from vertexai.preview._workflow.executor import (
    training,
)
from vertexai.preview._workflow.serialization_engine import (
    any_serializer,
    serializers_base,
)
from vertexai.preview._workflow.shared import configs
from vertexai.preview._workflow.shared import (
    supported_frameworks,
)
from vertexai.preview.developer import remote_specs
import numpy as np
import pytest
import sklearn
from sklearn.datasets import load_iris
from sklearn.linear_model import _logistic
from sklearn.model_selection import train_test_split
import tensorflow as tf
import tensorflow.keras


# Manually set tensorflow version for b/295580335
tf.__version__ = "2.12.0"


# vertexai constants
_TEST_PROJECT = "test-project"
_TEST_PROJECT_NUMBER = 12345678
_TEST_LOCATION = "us-central1"
_TEST_PARENT = f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}"
_TEST_BUCKET_NAME = "gs://test-bucket"
_TEST_UNIQUE_NAME = "test-unique-name"
_TEST_REMOTE_JOB_NAME = f"remote-job-{_TEST_UNIQUE_NAME}"
_TEST_REMOTE_JOB_BASE_PATH = os.path.join(_TEST_BUCKET_NAME, _TEST_REMOTE_JOB_NAME)
_TEST_EXPERIMENT = "test-experiment"
_TEST_EXPERIMENT_RUN = "test-experiment-run"
_TEST_SERVICE_ACCOUNT = f"{_TEST_PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# dataset constants
dataset = load_iris()
_X_TRAIN, _X_TEST, _Y_TRAIN, _Y_TEST = train_test_split(
    dataset.data, dataset.target, test_size=0.2, random_state=42
)

# custom job constants
_TEST_CUSTOM_JOB_NAME = f"{_TEST_PARENT}/customJobs/12345"
_TEST_UPGRADE_PIP_COMMAND = (
    "export PIP_ROOT_USER_ACTION=ignore && " "pip install --upgrade pip && "
)
_TEST_BASE_DEPS = f"'{training.VERTEX_AI_DEPENDENCY_PATH}' 'absl-py==1.4.0' "
_TEST_CUSTOM_COMMAND = "apt-get update && " "apt-get install -y git && "
_TEST_DEPS = (
    f"'scikit-learn=={sklearn.__version__}' "
    f"'numpy=={np.__version__}' "
    f"'cloudpickle=={cloudpickle.__version__}' "
)
_TEST_USER_DEPS = (
    f"'torch_cv' "
    f"'xgboost==1.6.0' "
    f"'numpy' "
    f"'scikit-learn=={sklearn.__version__}' "
    f"'cloudpickle=={cloudpickle.__version__}' "
)
_TEST_TRAINING_COMMAND = (
    "python3 -m vertexai.preview._workflow.executor.training_script "
    "--pass_through_int_args= "
    "--pass_through_float_args= "
    "--pass_through_str_args= "
    "--pass_through_bool_args= "
    f"--input_path={os.path.join(_TEST_REMOTE_JOB_BASE_PATH, 'input').replace('gs://', '/gcs/', 1)} "
    f"--output_path={os.path.join(_TEST_REMOTE_JOB_BASE_PATH, 'output').replace('gs://', '/gcs/', 1)} "
    "--method_name=fit "
    f"--arg_names=X,y "
    "--enable_cuda=False "
    "--enable_distributed=False "
    "--accelerator_count=0"
)

_TEST_AUTOLOG_COMMAND = (
    _TEST_UPGRADE_PIP_COMMAND
    + "pip install "
    + _TEST_BASE_DEPS.replace(
        training.VERTEX_AI_DEPENDENCY_PATH,
        training.VERTEX_AI_DEPENDENCY_PATH_AUTOLOGGING,
    )
    + _TEST_DEPS
    + "&& "
    + _TEST_TRAINING_COMMAND
    + " --enable_autolog"
)
_TEST_REPLICA_COUNT = 1
_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
_TEST_ACCELERATOR_COUNT = 2
_TEST_WORKER_POOL_SPEC = [
    {
        "machine_spec": {
            "machine_type": _TEST_MACHINE_TYPE,
        },
        "replica_count": _TEST_REPLICA_COUNT,
        "container_spec": {
            "image_uri": f"python:{supported_frameworks._get_python_minor_version()}",
            "command": ["sh", "-c"]
            + [
                _TEST_UPGRADE_PIP_COMMAND
                + "pip install "
                + _TEST_BASE_DEPS
                + _TEST_DEPS
                + "&& "
                + _TEST_TRAINING_COMMAND
            ],
            "args": [],
        },
    }
]
_TEST_CUSTOM_JOB_PROTO = gca_custom_job_compat.CustomJob(
    display_name=_TEST_REMOTE_JOB_NAME,
    job_spec={
        "worker_pool_specs": _TEST_WORKER_POOL_SPEC,
        "base_output_directory": gca_io_compat.GcsDestination(
            output_uri_prefix=_TEST_REMOTE_JOB_BASE_PATH
        ),
    },
)

# RemoteConfig constants
_TEST_TRAINING_CONFIG_DISPLAY_NAME = "test-training-config-display-name"
_TEST_TRAINING_CONFIG_STAGING_BUCKET = "gs://test-training-config-staging-bucket"
_TEST_TRAINING_CONFIG_CONTAINER_URI = "gcr.io/custom-image"
_TEST_TRAINING_CONFIG_MACHINE_TYPE = "n1-highmem-4"
_TEST_TRAINING_CONFIG_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
_TEST_TRAINING_CONFIG_ACCELERATOR_COUNT = 4
_TEST_REQUIREMENTS = ["torch_cv", "xgboost==1.6.0", "numpy"]
_TEST_CUSTOM_COMMANDS = ["apt-get update", "apt-get install -y git"]

_TEST_BOOT_DISK_TYPE = "test_boot_disk_type"
_TEST_BOOT_DISK_SIZE_GB = 10
_TEST_TRAINING_CONFIG_WORKER_POOL_SPECS = remote_specs.WorkerPoolSpecs(
    chief=remote_specs.WorkerPoolSpec(
        machine_type=_TEST_TRAINING_CONFIG_MACHINE_TYPE,
        replica_count=1,
        boot_disk_type=_TEST_BOOT_DISK_TYPE,
        boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
    )
)
_TEST_TRAINING_CONFIG_WORKER_POOL_SPECS_GPU = remote_specs.WorkerPoolSpecs(
    chief=remote_specs.WorkerPoolSpec(
        machine_type=_TEST_TRAINING_CONFIG_MACHINE_TYPE,
        accelerator_count=_TEST_TRAINING_CONFIG_ACCELERATOR_COUNT,
        accelerator_type=_TEST_TRAINING_CONFIG_ACCELERATOR_TYPE,
        replica_count=1,
        boot_disk_type=_TEST_BOOT_DISK_TYPE,
        boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
    )
)

_TEST_CONTEXT_ID = _TEST_EXPERIMENT
_TEST_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_CONTEXT_ID}"
_TEST_EXPERIMENT_DESCRIPTION = "test-experiment-description"
_TEST_ID = "1028944691210842416"
_TEST_TENSORBOARD_NAME = f"{_TEST_PARENT}/tensorboards/{_TEST_ID}"
_TEST_EXECUTION_ID = f"{_TEST_EXPERIMENT}-{_TEST_EXPERIMENT_RUN}"
_TEST_EXPERIMENT_RUN_CONTEXT_NAME = f"{_TEST_PARENT}/contexts/{_TEST_EXECUTION_ID}"
_TEST_METADATASTORE = (
    f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}/metadataStores/default"
)

_EXPERIMENT_MOCK = GapicContext(
    name=_TEST_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT,
    description=_TEST_EXPERIMENT_DESCRIPTION,
    schema_title=metadata_constants.SYSTEM_EXPERIMENT,
    schema_version=metadata_constants.SCHEMA_VERSIONS[
        metadata_constants.SYSTEM_EXPERIMENT
    ],
    metadata={**metadata_constants.EXPERIMENT_METADATA},
)

_EXPERIMENT_MOCK.metadata[
    metadata_constants._BACKING_TENSORBOARD_RESOURCE_KEY
] = _TEST_TENSORBOARD_NAME

_EXPERIMENT_RUN_MOCK = GapicContext(
    name=_TEST_EXPERIMENT_RUN_CONTEXT_NAME,
    display_name=_TEST_EXPERIMENT_RUN,
    schema_title=metadata_constants.SYSTEM_EXPERIMENT_RUN,
    schema_version=metadata_constants.SCHEMA_VERSIONS[
        metadata_constants.SYSTEM_EXPERIMENT_RUN
    ],
    metadata={
        metadata_constants._PARAM_KEY: {},
        metadata_constants._METRIC_KEY: {},
        metadata_constants._STATE_KEY: gca_execution.Execution.State.RUNNING.name,
    },
)


_TEST_DEFAULT_TENSORBOARD_NAME = "test-tensorboard-default-name"

_TEST_DEFAULT_TENSORBOARD_GCA = gca_tensorboard.Tensorboard(
    name=_TEST_DEFAULT_TENSORBOARD_NAME,
    is_default=True,
)

_TEST_PERSISTENT_RESOURCE_ID = "test-cluster"
_TEST_PERSISTENT_RESOURCE_CONFIG = configs.PersistentResourceConfig(
    name=_TEST_PERSISTENT_RESOURCE_ID,
    resource_pools=[
        remote_specs.ResourcePool(
            replica_count=_TEST_REPLICA_COUNT,
        ),
        remote_specs.ResourcePool(
            machine_type="n1-standard-8",
            replica_count=2,
        ),
    ],
)

_TEST_PERSISTENT_RESOURCE_CONFIG_SERVICE_ACCOUNT = configs.PersistentResourceConfig(
    name=_TEST_PERSISTENT_RESOURCE_ID,
    resource_pools=[
        remote_specs.ResourcePool(
            replica_count=_TEST_REPLICA_COUNT,
        ),
        remote_specs.ResourcePool(
            machine_type="n1-standard-8",
            replica_count=2,
        ),
    ],
    service_account=_TEST_SERVICE_ACCOUNT,
)

_TEST_PERSISTENT_RESOURCE_CONFIG_DISABLE = configs.PersistentResourceConfig(
    name=_TEST_PERSISTENT_RESOURCE_ID,
    resource_pools=[
        remote_specs.ResourcePool(
            replica_count=_TEST_REPLICA_COUNT,
        ),
        remote_specs.ResourcePool(
            machine_type="n1-standard-8",
            replica_count=2,
        ),
    ],
    disable=True,
)


@pytest.fixture
def list_default_tensorboard_mock():
    with patch.object(
        TensorboardServiceClient, "list_tensorboards"
    ) as list_default_tensorboard_mock:
        list_default_tensorboard_mock.side_effect = [
            [_TEST_DEFAULT_TENSORBOARD_GCA],
        ]
        yield list_default_tensorboard_mock


def _get_custom_job_proto(
    display_name=None,
    staging_bucket=None,
    container_uri=None,
    machine_type=None,
    accelerator_type=None,
    accelerator_count=None,
    replica_count=None,
    boot_disk_type=None,
    boot_disk_size_gb=None,
    service_account=None,
    experiment=None,
    experiment_run=None,
    autolog_enabled=False,
    cuda_enabled=False,
    distributed_enabled=False,
    model=None,
    user_requirements=False,
    custom_commands=False,
    persistent_resource_id=None,
):
    job = copy.deepcopy(_TEST_CUSTOM_JOB_PROTO)
    if display_name:
        job.display_name = display_name
    if container_uri:
        job.job_spec.worker_pool_specs[0].container_spec.image_uri = container_uri
        job.job_spec.worker_pool_specs[0].container_spec.command[-1] = (
            _TEST_UPGRADE_PIP_COMMAND
            + "pip install "
            + _TEST_BASE_DEPS
            + "&& "
            + _TEST_TRAINING_COMMAND
        )
    if user_requirements:
        job.job_spec.worker_pool_specs[0].container_spec.command[-1] = (
            _TEST_UPGRADE_PIP_COMMAND
            + "pip install "
            + _TEST_BASE_DEPS
            + _TEST_USER_DEPS
            + "&& "
            + _TEST_TRAINING_COMMAND
        )
    if custom_commands:
        job.job_spec.worker_pool_specs[0].container_spec.command[-1] = (
            _TEST_UPGRADE_PIP_COMMAND.replace("&& ", f"&& {_TEST_CUSTOM_COMMAND}", 1)
            + "pip install "
            + _TEST_BASE_DEPS
            + _TEST_DEPS
            + "&& "
            + _TEST_TRAINING_COMMAND
        )
    if autolog_enabled:
        job.job_spec.worker_pool_specs[0].container_spec.command[
            -1
        ] = _TEST_AUTOLOG_COMMAND
    if isinstance(model, tf.Module):
        command = job.job_spec.worker_pool_specs[0].container_spec.command
        for i, s in enumerate(command):
            s = s.replace(
                f"scikit-learn=={sklearn.__version__}", f"tensorflow=={tf.__version__}"
            )
            s = s.replace("--arg_names=X,y", "--arg_names=x,y")
            command[i] = s
        job.job_spec.worker_pool_specs[0].container_spec.command = command
    if cuda_enabled:
        if not container_uri:
            job.job_spec.worker_pool_specs[
                0
            ].container_spec.image_uri = supported_frameworks._get_gpu_container_uri(
                model
            )
        job.job_spec.worker_pool_specs[0].machine_spec.machine_type = "n1-standard-16"
        job.job_spec.worker_pool_specs[
            0
        ].machine_spec.accelerator_type = "NVIDIA_TESLA_P100"
        job.job_spec.worker_pool_specs[0].machine_spec.accelerator_count = 1
        command = job.job_spec.worker_pool_specs[0].container_spec.command
        job.job_spec.worker_pool_specs[0].container_spec.command = [
            s.replace("--enable_cuda=False", "--enable_cuda=True") for s in command
        ]
    if distributed_enabled:
        command = job.job_spec.worker_pool_specs[0].container_spec.command
        job.job_spec.worker_pool_specs[0].container_spec.command = [
            s.replace("--enable_distributed=False", "--enable_distributed=True")
            for s in command
        ]
    if machine_type:
        job.job_spec.worker_pool_specs[0].machine_spec.machine_type = machine_type
    if accelerator_type:
        job.job_spec.worker_pool_specs[
            0
        ].machine_spec.accelerator_type = accelerator_type
    if accelerator_count:
        job.job_spec.worker_pool_specs[
            0
        ].machine_spec.accelerator_count = accelerator_count
        if not distributed_enabled:
            command = job.job_spec.worker_pool_specs[0].container_spec.command
            job.job_spec.worker_pool_specs[0].container_spec.command = [
                s.replace(
                    "--accelerator_count=0",
                    f"--accelerator_count={accelerator_count}",
                )
                for s in command
            ]
    if replica_count:
        job.job_spec.worker_pool_specs[0].replica_count = replica_count
    if boot_disk_type:
        job.job_spec.worker_pool_specs[0].disk_spec.boot_disk_type = boot_disk_type
    if boot_disk_size_gb:
        job.job_spec.worker_pool_specs[
            0
        ].disk_spec.boot_disk_size_gb = boot_disk_size_gb
    if staging_bucket:
        job.job_spec.base_output_directory = gca_io_compat.GcsDestination(
            output_uri_prefix=os.path.join(staging_bucket, _TEST_REMOTE_JOB_NAME)
        )
        command = job.job_spec.worker_pool_specs[0].container_spec.command
        job.job_spec.worker_pool_specs[0].container_spec.command = [
            s.replace(_TEST_BUCKET_NAME[5:], staging_bucket[5:]) for s in command
        ]
    if service_account:
        job.job_spec.service_account = service_account
    if experiment:
        env = job.job_spec.worker_pool_specs[0].container_spec.env
        env.append({"name": metadata_constants.ENV_EXPERIMENT_KEY, "value": experiment})
    if experiment_run:
        env = job.job_spec.worker_pool_specs[0].container_spec.env
        env.append(
            {"name": metadata_constants.ENV_EXPERIMENT_RUN_KEY, "value": experiment_run}
        )
    if persistent_resource_id:
        job.job_spec.persistent_resource_id = persistent_resource_id
    job.labels = ({"trained_by_vertex_ai": "true"},)
    return job


@pytest.fixture
def mock_timestamped_unique_name():
    with patch.object(utils, "timestamped_unique_name") as mock_timestamped_unique_name:
        mock_timestamped_unique_name.return_value = _TEST_UNIQUE_NAME
        yield mock_timestamped_unique_name


@pytest.fixture
def mock_autolog_enabled():
    with patch.object(
        utils.autologging_utils, "_is_autologging_enabled"
    ) as autolog_enabled:
        autolog_enabled.return_value = True
        yield autolog_enabled


@pytest.fixture
def mock_autolog_disabled():
    with patch.object(
        utils.autologging_utils, "_is_autologging_enabled"
    ) as autolog_disabled:
        autolog_disabled.return_value = False
        yield autolog_disabled


@pytest.fixture
def mock_get_project_number():
    with patch.object(
        utils.resource_manager_utils, "get_project_number"
    ) as mock_get_project_number:
        mock_get_project_number.return_value = _TEST_PROJECT_NUMBER
        yield mock_get_project_number


@pytest.fixture
def mock_get_experiment_run():
    with patch.object(MetadataServiceClient, "get_context") as mock_get_experiment_run:
        mock_get_experiment_run.side_effect = [
            _EXPERIMENT_MOCK,
            _EXPERIMENT_RUN_MOCK,
            _EXPERIMENT_RUN_MOCK,
        ]

        yield mock_get_experiment_run


@pytest.fixture
def mock_get_metadata_store():
    with patch.object(
        MetadataServiceClient, "get_metadata_store"
    ) as mock_get_metadata_store:
        mock_get_metadata_store.return_value = GapicMetadataStore(
            name=_TEST_METADATASTORE,
        )
        yield mock_get_metadata_store


@pytest.fixture
def get_artifact_not_found_mock():
    with patch.object(MetadataServiceClient, "get_artifact") as get_artifact_mock:
        get_artifact_mock.side_effect = exceptions.NotFound("")
        yield get_artifact_mock


# we've tested AnySerializer in `test_serializers.py`
# so here we mock the SDK methods directly
@pytest.fixture
def mock_any_serializer_serialize_sklearn():
    with patch.object(
        any_serializer.AnySerializer,
        "serialize",
        side_effect=[
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"scikit-learn=={sklearn.__version__}"
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
        ],
    ) as mock_any_serializer_serialize:
        yield mock_any_serializer_serialize


@pytest.fixture
def mock_any_serializer_save_global_metadata():
    with patch.object(
        any_serializer.AnySerializer,
        "save_global_metadata",
    ) as mock_any_serializer_save_global_metadata:
        yield mock_any_serializer_save_global_metadata


@pytest.fixture
def mock_any_serializer_load_global_metadata():
    with patch.object(
        any_serializer.AnySerializer,
        "load_global_metadata",
    ) as mock_any_serializer_load_global_metadata:
        yield mock_any_serializer_load_global_metadata


@pytest.fixture
def mock_any_serializer_sklearn(
    mock_any_serializer_serialize_sklearn, mock_any_serializer_deserialize_sklearn
):
    with patch.object(
        any_serializer,
        "AnySerializer",
    ) as mock_any_serializer_obj:
        model = _logistic.LogisticRegression()
        model.fit(_X_TRAIN, _Y_TRAIN)
        mock_any_serializer_obj.return_value.deserialize = (
            mock_any_serializer_deserialize_sklearn
        )
        mock_any_serializer_obj.return_value.serialize = (
            mock_any_serializer_serialize_sklearn
        )
        yield mock_any_serializer_obj


@pytest.fixture
def mock_any_serializer_deserialize_sklearn():
    with patch.object(
        any_serializer.AnySerializer, "deserialize"
    ) as mock_any_serializer_deserialize_sklearn:
        model = _logistic.LogisticRegression()
        returned_model = model.fit(_X_TRAIN, _Y_TRAIN)
        mock_any_serializer_deserialize_sklearn.side_effect = [model, returned_model]
        yield mock_any_serializer_deserialize_sklearn


@pytest.fixture
def mock_any_serializer_keras(
    mock_any_serializer_serialize_keras, mock_any_serializer_deserialize_keras
):
    with patch.object(
        any_serializer,
        "AnySerializer",
    ) as mock_any_serializer_obj:
        model = _logistic.LogisticRegression()
        model.fit(_X_TRAIN, _Y_TRAIN)
        mock_any_serializer_obj.return_value.deserialize = (
            mock_any_serializer_deserialize_keras
        )
        mock_any_serializer_obj.return_value.serialize = (
            mock_any_serializer_serialize_keras
        )
        yield mock_any_serializer_obj


@pytest.fixture
def mock_any_serializer_serialize_keras():
    with patch.object(
        any_serializer.AnySerializer,
        "serialize",
        side_effect=[
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"tensorflow=={tf.__version__}"
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
            {
                serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                    f"numpy=={np.__version__}",
                    f"cloudpickle=={cloudpickle.__version__}",
                ],
                serializers_base.SERIALIZATION_METADATA_CUSTOM_COMMANDS_KEY: [],
            },
        ],
    ) as mock_any_serializer_serialize:
        yield mock_any_serializer_serialize


@pytest.fixture
def mock_any_serializer_deserialize_keras():
    with patch.object(
        any_serializer.AnySerializer, "deserialize"
    ) as mock_any_serializer_deserialize_keras:
        model = tf.keras.Sequential(
            [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        returned_history = model.fit(_X_TRAIN, _Y_TRAIN)
        mock_any_serializer_deserialize_keras.side_effect = [model, returned_history]
        yield mock_any_serializer_deserialize_keras


@pytest.fixture
def mock_create_custom_job():
    with mock.patch.object(
        job_service_client.JobServiceClient, "create_custom_job"
    ) as mock_create_custom_job:
        custom_job_proto = _get_custom_job_proto()
        custom_job_proto.name = _TEST_CUSTOM_JOB_NAME
        custom_job_proto.state = gca_job_state_compat.JobState.JOB_STATE_PENDING
        mock_create_custom_job.return_value = custom_job_proto
        yield mock_create_custom_job


@pytest.fixture
def mock_get_custom_job():
    with patch.object(
        job_service_client.JobServiceClient, "get_custom_job"
    ) as mock_get_custom_job:
        custom_job_proto = _get_custom_job_proto()
        custom_job_proto.name = _TEST_CUSTOM_JOB_NAME
        custom_job_proto.state = gca_job_state_compat.JobState.JOB_STATE_SUCCEEDED
        mock_get_custom_job.return_value = custom_job_proto
        yield mock_get_custom_job


@pytest.fixture
def update_context_mock():
    with patch.object(MetadataServiceClient, "update_context") as update_context_mock:
        update_context_mock.side_effect = [_EXPERIMENT_RUN_MOCK] * 4
        yield update_context_mock


@pytest.fixture
def aiplatform_autolog_mock():
    with patch.object(aiplatform, "autolog") as aiplatform_autolog_mock:
        yield aiplatform_autolog_mock


# unittest `assert_any_call` method doesn't work when arguments contain `np.ndarray`
# https://stackoverflow.com/questions/56644729/mock-assert-mock-calls-with-a-numpy-array-as-argument-raises-valueerror-and-np
# tentatively runtime patch `assert_any_call` to solve this issue
def assert_any_call_for_numpy(self, **kwargs):
    """Used by vertexai Serializer mock, only check kwargs."""
    found = False
    for call in self.call_args_list:
        equal = True
        actual_kwargs = call[1]
        for k, v in actual_kwargs.items():
            if k not in kwargs:
                equal = False
                break
            try:
                equal = v == kwargs[k]
            except ValueError:
                equal = False
            equal = equal.all() if isinstance(equal, np.ndarray) else equal
            if not equal:
                break

        if equal and len(actual_kwargs) == len(kwargs):
            found = True
            break

    if not found:
        raise AssertionError(f"{kwargs} not found.")


mock.Mock.assert_any_call = assert_any_call_for_numpy

# TODO(zhenyiqi) fix external unit test failure caused by this method
training._add_indirect_dependency_versions = lambda x: x


@pytest.mark.usefixtures("google_auth_mock", "mock_cloud_logging_list_entries")
class TestRemoteTraining:
    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)
        reload(vertexai.preview.initializer)
        reload(vertexai)
        reload(_logistic)
        reload(tf.keras)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_sklearn(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()
        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto()
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_sklearn_with_user_requirements(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()
        model.fit.vertex.remote_config.requirements = _TEST_REQUIREMENTS

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(user_requirements=True)
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_sklearn_with_custom_commands(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()
        model.fit.vertex.remote_config.custom_commands = _TEST_CUSTOM_COMMANDS

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(custom_commands=True)
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_sklearn_with_remote_configs(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        # set all training configs
        model.fit.vertex.remote_config.display_name = _TEST_TRAINING_CONFIG_DISPLAY_NAME
        model.fit.vertex.remote_config.staging_bucket = (
            _TEST_TRAINING_CONFIG_STAGING_BUCKET
        )
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )
        model.fit.vertex.remote_config.machine_type = _TEST_TRAINING_CONFIG_MACHINE_TYPE
        model.fit.vertex.remote_config.serializer_args[model] = {"extra_params": 1}
        # X_TRAIN is a numpy array that is not hashable.
        model.fit.vertex.remote_config.serializer_args[_X_TRAIN] = {"extra_params": 2}

        model.fit(_X_TRAIN, _Y_TRAIN)

        remote_job_base_path = os.path.join(
            _TEST_TRAINING_CONFIG_STAGING_BUCKET, _TEST_REMOTE_JOB_NAME
        )

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(remote_job_base_path, "input/input_estimator"),
            **{"extra_params": 1},
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(remote_job_base_path, "input/X"),
            **{"extra_params": 2},
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(remote_job_base_path, "input/y"),
            **{},
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            display_name=_TEST_TRAINING_CONFIG_DISPLAY_NAME,
            staging_bucket=_TEST_TRAINING_CONFIG_STAGING_BUCKET,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type=_TEST_TRAINING_CONFIG_MACHINE_TYPE,
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(remote_job_base_path, "output/output_estimator")
                ),
                mock.call(os.path.join(remote_job_base_path, "output/output_data")),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_sklearn_with_worker_pool_specs(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        # set all training configs
        model.fit.vertex.remote_config.display_name = _TEST_TRAINING_CONFIG_DISPLAY_NAME
        model.fit.vertex.remote_config.staging_bucket = (
            _TEST_TRAINING_CONFIG_STAGING_BUCKET
        )
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )
        model.fit.vertex.remote_config.worker_pool_specs = (
            _TEST_TRAINING_CONFIG_WORKER_POOL_SPECS
        )

        model.fit(_X_TRAIN, _Y_TRAIN)

        remote_job_base_path = os.path.join(
            _TEST_TRAINING_CONFIG_STAGING_BUCKET, _TEST_REMOTE_JOB_NAME
        )

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(remote_job_base_path, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(remote_job_base_path, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(remote_job_base_path, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            display_name=_TEST_TRAINING_CONFIG_DISPLAY_NAME,
            staging_bucket=_TEST_TRAINING_CONFIG_STAGING_BUCKET,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type="n1-standard-4",
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(remote_job_base_path, "output/output_estimator")
                ),
                mock.call(os.path.join(remote_job_base_path, "output/output_data")),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name",
        "mock_any_serializer_save_global_metadata",
        "mock_any_serializer_load_global_metadata",
        "mock_get_custom_job",
        "mock_any_serializer_deserialize_sklearn",
        "mock_autolog_disabled",
    )
    def test_remote_training_sklearn_with_set_config(
        self,
        mock_any_serializer_serialize_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        # set training config via dict
        model.fit.vertex.set_config(
            display_name=_TEST_TRAINING_CONFIG_DISPLAY_NAME,
            staging_bucket=_TEST_TRAINING_CONFIG_STAGING_BUCKET,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            worker_pool_specs=_TEST_TRAINING_CONFIG_WORKER_POOL_SPECS,
        )

        model.fit(_X_TRAIN, _Y_TRAIN)

        remote_job_base_path = os.path.join(
            _TEST_TRAINING_CONFIG_STAGING_BUCKET, _TEST_REMOTE_JOB_NAME
        )

        # check that model is serialized correctly
        mock_any_serializer_serialize_sklearn.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(remote_job_base_path, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_serialize_sklearn.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(remote_job_base_path, "input/X"),
        )
        mock_any_serializer_serialize_sklearn.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(remote_job_base_path, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            display_name=_TEST_TRAINING_CONFIG_DISPLAY_NAME,
            staging_bucket=_TEST_TRAINING_CONFIG_STAGING_BUCKET,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type="n1-standard-4",
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
        "mock_any_serializer_sklearn",
        "mock_autolog_disabled",
    )
    def test_set_config_raises_with_unsupported_arg(
        self,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        # RemoteConfig doesn't have `boot_disk_type`, only DistributedTrainingConfig
        with pytest.raises(ValueError):
            model.fit.vertex.set_config(boot_disk_type=_TEST_BOOT_DISK_TYPE)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_sklearn_with_invalid_remote_config(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        # set all training configs
        model.fit.vertex.remote_config.display_name = _TEST_TRAINING_CONFIG_DISPLAY_NAME
        model.fit.vertex.remote_config.staging_bucket = (
            _TEST_TRAINING_CONFIG_STAGING_BUCKET
        )
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )
        model.fit.vertex.remote_config.worker_pool_specs = (
            _TEST_TRAINING_CONFIG_WORKER_POOL_SPECS
        )
        model.fit.vertex.remote_config.machine_type = _TEST_TRAINING_CONFIG_MACHINE_TYPE

        with pytest.raises(
            ValueError,
            match=re.escape(
                "Cannot specify both 'worker_pool_specs' and ['machine_type', 'accelerator_type', 'accelerator_count', 'replica_count', 'boot_disk_type', 'boot_disk_size_gb']."
            ),
        ):
            model.fit(_X_TRAIN, _Y_TRAIN)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_gpu_training_keras(
        self,
        mock_any_serializer_keras,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        tf.keras.VertexSequential = vertexai.preview.remote(tf.keras.Sequential)
        model = tf.keras.VertexSequential(
            [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit.vertex.remote_config.enable_cuda = True
        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/x"),
        )
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(cuda_enabled=True, model=model)
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_keras.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data"),
                    model=model,
                ),
            ]
        )

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_gpu_training_keras_with_remote_configs(
        self,
        mock_any_serializer_keras,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        tf.keras.VertexSequential = vertexai.preview.remote(tf.keras.Sequential)
        model = tf.keras.VertexSequential(
            [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")

        model.fit.vertex.remote_config.enable_cuda = True
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )
        model.fit.vertex.remote_config.machine_type = _TEST_TRAINING_CONFIG_MACHINE_TYPE
        model.fit.vertex.remote_config.accelerator_type = (
            _TEST_TRAINING_CONFIG_ACCELERATOR_TYPE
        )
        model.fit.vertex.remote_config.accelerator_count = (
            _TEST_TRAINING_CONFIG_ACCELERATOR_COUNT
        )

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/x"),
        )
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            cuda_enabled=True,
            model=model,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type=_TEST_TRAINING_CONFIG_MACHINE_TYPE,
            accelerator_type=_TEST_TRAINING_CONFIG_ACCELERATOR_TYPE,
            accelerator_count=_TEST_TRAINING_CONFIG_ACCELERATOR_COUNT,
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_keras.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data"),
                    model=model,
                ),
            ]
        )

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_keras_with_worker_pool_specs(
        self,
        mock_any_serializer_keras,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        tf.keras.VertexSequential = vertexai.preview.remote(tf.keras.Sequential)
        model = tf.keras.VertexSequential(
            [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")

        model.fit.vertex.remote_config.enable_distributed = True
        model.fit.vertex.remote_config.enable_cuda = True
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )
        model.fit.vertex.remote_config.worker_pool_specs = (
            _TEST_TRAINING_CONFIG_WORKER_POOL_SPECS_GPU
        )

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/x"),
        )
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            cuda_enabled=True,
            model=model,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type=_TEST_TRAINING_CONFIG_MACHINE_TYPE,
            accelerator_type=_TEST_TRAINING_CONFIG_ACCELERATOR_TYPE,
            accelerator_count=_TEST_TRAINING_CONFIG_ACCELERATOR_COUNT,
            boot_disk_type=_TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
            distributed_enabled=True,
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_keras.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data"),
                    model=model,
                ),
            ]
        )

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_keras_distributed_cuda_no_worker_pool_specs(
        self,
        mock_any_serializer_keras,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        tf.keras.VertexSequential = vertexai.preview.remote(tf.keras.Sequential)
        model = tf.keras.VertexSequential(
            [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")

        model.fit.vertex.remote_config.enable_distributed = True
        model.fit.vertex.remote_config.enable_cuda = True
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/x"),
        )
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            cuda_enabled=True,
            model=model,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type="n1-standard-16",
            accelerator_type="NVIDIA_TESLA_P100",
            accelerator_count=1,
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
            distributed_enabled=True,
        )

        expected_custom_job.job_spec.worker_pool_specs = [
            expected_custom_job.job_spec.worker_pool_specs[0],
            expected_custom_job.job_spec.worker_pool_specs[0],
        ]

        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_keras.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data"),
                    model=model,
                ),
            ]
        )

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name", "mock_get_custom_job", "mock_autolog_disabled"
    )
    def test_remote_training_keras_distributed_no_cuda_no_worker_pool_specs(
        self,
        mock_any_serializer_keras,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True)

        tf.keras.VertexSequential = vertexai.preview.remote(tf.keras.Sequential)
        model = tf.keras.VertexSequential(
            [tf.keras.layers.Dense(5, input_shape=(4,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")

        model.fit.vertex.remote_config.enable_distributed = True
        model.fit.vertex.remote_config.enable_cuda = False
        model.fit.vertex.remote_config.container_uri = (
            _TEST_TRAINING_CONFIG_CONTAINER_URI
        )

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/x"),
        )
        mock_any_serializer_keras.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # check that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            model=model,
            container_uri=_TEST_TRAINING_CONFIG_CONTAINER_URI,
            machine_type="n1-standard-4",
            boot_disk_type="pd-ssd",
            boot_disk_size_gb=100,
            distributed_enabled=True,
        )
        expected_custom_job.job_spec.worker_pool_specs = [
            expected_custom_job.job_spec.worker_pool_specs[0],
            expected_custom_job.job_spec.worker_pool_specs[0],
        ]

        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_keras.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data"),
                    model=model,
                ),
            ]
        )

    # TODO(b/300116902) Remove this once we find better solution.
    @pytest.mark.xfail(
        sys.version_info.minor >= 8,
        raises=ValueError,
        reason="Flaky in python >=3.8",
    )
    @pytest.mark.usefixtures(
        "list_default_tensorboard_mock",
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
        "mock_get_project_number",
        "mock_get_experiment_run",
        "mock_get_metadata_store",
        "get_artifact_not_found_mock",
        "update_context_mock",
        "mock_autolog_disabled",
    )
    def test_remote_training_sklearn_with_experiment(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            experiment=_TEST_EXPERIMENT,
        )
        vertexai.preview.init(remote=True)

        vertexai.preview.start_run(_TEST_EXPERIMENT_RUN, resume=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.fit.vertex.remote_config.service_account = "GCE"

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            service_account=f"{_TEST_PROJECT_NUMBER}-compute@developer.gserviceaccount.com",
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    # TODO(b/300116902) Remove this once we find better solution
    @pytest.mark.xfail(
        sys.version_info.minor >= 8,
        raises=ValueError,
        reason="Flaky in python >=3.8",
    )
    @pytest.mark.usefixtures(
        "list_default_tensorboard_mock",
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
        "mock_get_experiment_run",
        "mock_get_metadata_store",
        "get_artifact_not_found_mock",
        "update_context_mock",
        "aiplatform_autolog_mock",
        "mock_autolog_enabled",
    )
    def test_remote_training_sklearn_with_experiment_autolog_enabled(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            experiment=_TEST_EXPERIMENT,
        )
        vertexai.preview.init(remote=True, autolog=True)

        vertexai.preview.start_run(_TEST_EXPERIMENT_RUN, resume=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.fit.vertex.remote_config.service_account = "custom-sa"

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            service_account="custom-sa",
            experiment=_TEST_EXPERIMENT,
            experiment_run=_TEST_EXPERIMENT_RUN,
            autolog_enabled=True,
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    def test_get_service_account_custom_service_account(self):
        config = configs.RemoteConfig()
        config.service_account = "custom-sa"

        service_account = training._get_service_account(config, autolog=True)

        assert service_account == "custom-sa"

    @pytest.mark.usefixtures(
        "mock_get_project_number",
    )
    def test_get_service_account_gce_service_account(self):
        config = configs.RemoteConfig()
        config.service_account = "GCE"

        service_account = training._get_service_account(config, autolog=True)

        assert (
            service_account
            == f"{_TEST_PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
        )

    def test_get_service_account_empty_sa_autolog_enabled(self):
        config = configs.RemoteConfig()
        # config.service_account is empty

        with pytest.raises(ValueError):
            training._get_service_account(config, autolog=True)

    def test_get_service_account_empty_sa_autolog_disabled(self):
        config = configs.RemoteConfig()
        # config.service_account is empty

        service_account = training._get_service_account(config, autolog=False)

        assert service_account is None

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
        "mock_autolog_disabled",
        "persistent_resource_running_mock",
    )
    def test_remote_training_sklearn_with_persistent_cluster(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        vertexai.preview.init(remote=True, cluster=_TEST_PERSISTENT_RESOURCE_CONFIG)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
        "mock_autolog_disabled",
        "persistent_resource_running_mock",
    )
    def test_initialize_existing_persistent_resource_service_account_mismatch(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        with pytest.raises(ValueError) as e:
            vertexai.preview.init(
                cluster=_TEST_PERSISTENT_RESOURCE_CONFIG_SERVICE_ACCOUNT
            )
        e.match(
            regexp=r"Expect the existing cluster was created with the service account "
        )

    @pytest.mark.usefixtures(
        "mock_get_project_number",
        "list_default_tensorboard_mock",
        "mock_get_experiment_run",
        "mock_get_metadata_store",
        "get_artifact_not_found_mock",
        "update_context_mock",
        "aiplatform_autolog_mock",
        "mock_autolog_enabled",
        "persistent_resource_running_mock",
    )
    def test_remote_training_sklearn_with_persistent_cluster_no_service_account_and_experiment_error(
        self,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            experiment=_TEST_EXPERIMENT,
        )
        vertexai.preview.init(
            remote=True, autolog=True, cluster=_TEST_PERSISTENT_RESOURCE_CONFIG
        )

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        with pytest.raises(ValueError) as e:
            model.fit.vertex.remote_config.service_account = "GCE"
            model.fit(_X_TRAIN, _Y_TRAIN)
        e.match(regexp=r"The service account for autologging")

    # TODO(b/300116902) Remove this once we find better solution.
    @pytest.mark.xfail(
        sys.version_info.minor >= 8,
        raises=ValueError,
        reason="Flaky in python >=3.8",
    )
    @pytest.mark.usefixtures(
        "mock_get_project_number",
        "list_default_tensorboard_mock",
        "mock_get_experiment_run",
        "mock_get_metadata_store",
        "get_artifact_not_found_mock",
        "update_context_mock",
        "aiplatform_autolog_mock",
        "mock_autolog_enabled",
        "persistent_resource_service_account_running_mock",
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
    )
    def test_remote_training_sklearn_with_persistent_cluster_and_experiment_autologging(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
            experiment=_TEST_EXPERIMENT,
        )
        vertexai.preview.init(
            remote=True,
            autolog=True,
            cluster=_TEST_PERSISTENT_RESOURCE_CONFIG_SERVICE_ACCOUNT,
        )

        vertexai.preview.start_run(_TEST_EXPERIMENT_RUN, resume=True)

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.fit.vertex.remote_config.service_account = _TEST_SERVICE_ACCOUNT

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly
        expected_custom_job = _get_custom_job_proto(
            service_account=_TEST_SERVICE_ACCOUNT,
            experiment=_TEST_EXPERIMENT,
            experiment_run=_TEST_EXPERIMENT_RUN,
            autolog_enabled=True,
            persistent_resource_id=_TEST_PERSISTENT_RESOURCE_ID,
        )
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    @pytest.mark.usefixtures(
        "mock_timestamped_unique_name",
        "mock_get_custom_job",
        "mock_autolog_disabled",
        "persistent_resource_running_mock",
    )
    def test_remote_training_sklearn_with_persistent_cluster_disabled(
        self,
        mock_any_serializer_sklearn,
        mock_create_custom_job,
    ):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_BUCKET_NAME,
        )
        # Enable persistent resource executor
        vertexai.preview.init(remote=True, cluster=_TEST_PERSISTENT_RESOURCE_CONFIG)
        # Disable persistent resource executor
        vertexai.preview.init(
            remote=True, cluster=_TEST_PERSISTENT_RESOURCE_CONFIG_DISABLE
        )

        LogisticRegression = vertexai.preview.remote(_logistic.LogisticRegression)
        model = LogisticRegression()

        model.fit(_X_TRAIN, _Y_TRAIN)

        # check that model is serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=model,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/input_estimator"),
        )

        # check that args are serialized correctly
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_X_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/X"),
        )
        mock_any_serializer_sklearn.return_value.serialize.assert_any_call(
            to_serialize=_Y_TRAIN,
            gcs_path=os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "input/y"),
        )

        # ckeck that CustomJob is created correctly without persistent_resource_id
        expected_custom_job = _get_custom_job_proto()
        mock_create_custom_job.assert_called_once_with(
            parent=_TEST_PARENT,
            custom_job=expected_custom_job,
            timeout=None,
        )

        # check that trained model is deserialized correctly
        mock_any_serializer_sklearn.return_value.deserialize.assert_has_calls(
            [
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_estimator")
                ),
                mock.call(
                    os.path.join(_TEST_REMOTE_JOB_BASE_PATH, "output/output_data")
                ),
            ]
        )

        # change to `vertexai.preview.init(remote=False)` to use local prediction
        vertexai.preview.init(remote=False)

        # check that local model is updated in place
        # `model.score` raises NotFittedError if the model is not updated
        model.score(_X_TEST, _Y_TEST)

    def test_resource_pool_return_spec_dict(self):
        test_pool = resource_pool_utils._ResourcePool(
            replica_count=_TEST_REPLICA_COUNT,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=_TEST_ACCELERATOR_COUNT,
            accelerator_type=_TEST_ACCELERATOR_TYPE,
        )
        true_spec_dict = {
            "machine_spec": {
                "machine_type": _TEST_MACHINE_TYPE,
                "accelerator_type": _TEST_ACCELERATOR_TYPE,
                "accelerator_count": _TEST_ACCELERATOR_COUNT,
            },
            "replica_count": _TEST_REPLICA_COUNT,
            "disk_spec": {
                "boot_disk_type": "pd-ssd",
                "boot_disk_size_gb": 100,
            },
        }

        assert test_pool.spec_dict == true_spec_dict
