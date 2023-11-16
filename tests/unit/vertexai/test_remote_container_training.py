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
"""Tests for _workflow/executor/remote_container_training.py.
"""

from importlib import reload
import inspect
import os
import re
import tempfile

import cloudpickle
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform.compat.types import (
    custom_job as gca_custom_job_compat,
)
from google.cloud.aiplatform.compat.types import io as gca_io_compat
from vertexai.preview._workflow.driver import remote
from vertexai.preview._workflow.executor import (
    remote_container_training,
)
from vertexai.preview._workflow.shared import configs
from vertexai.preview.developer import remote_specs
import pandas as pd
import pytest


# Custom job constants.
_TEST_INPUTS = [
    "--arg_0=string_val_0",
    "--arg_1=string_val_1",
    "--arg_2=int_val_0",
    "--arg_3=int_val_1",
]
_TEST_IMAGE_URI = "test_image_uri"
_TEST_MACHINE_TYPE = "n1-standard-4"

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"

_TEST_BUCKET_NAME = "gs://test_bucket"
_TEST_BASE_OUTPUT_DIR = f"{_TEST_BUCKET_NAME}/test_base_output_dir"

_TEST_DISPLAY_NAME = "test_display_name"
_TEST_STAGING_BUCKET = "gs://test-staging-bucket"
_TEST_CONTAINER_URI = "gcr.io/test-image"
_TEST_REPLICA_COUNT = 1
_TEST_ACCELERATOR_COUNT = 8
_TEST_ACCELERATOR_TYPE = "NVIDIA_TESLA_K80"
_TEST_BOOT_DISK_TYPE = "test_boot_disk_type"
_TEST_BOOT_DISK_SIZE_GB = 10
_TEST_REMOTE_CONTAINER_TRAINING_CONFIG = configs.DistributedTrainingConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    machine_type=_TEST_MACHINE_TYPE,
    replica_count=_TEST_REPLICA_COUNT,
    accelerator_count=_TEST_ACCELERATOR_COUNT,
    accelerator_type=_TEST_ACCELERATOR_TYPE,
    boot_disk_type=_TEST_BOOT_DISK_TYPE,
    boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
)

_TEST_WORKER_POOL_SPECS = remote_specs.WorkerPoolSpecs(
    chief=remote_specs.WorkerPoolSpec(
        machine_type=_TEST_MACHINE_TYPE,
        replica_count=_TEST_REPLICA_COUNT,
        accelerator_count=_TEST_ACCELERATOR_COUNT,
        accelerator_type=_TEST_ACCELERATOR_TYPE,
        boot_disk_type=_TEST_BOOT_DISK_TYPE,
        boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
    )
)

_TEST_REMOTE_CONTAINER_TRAINING_CONFIG_WORKER_POOL = configs.DistributedTrainingConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    worker_pool_specs=_TEST_WORKER_POOL_SPECS,
)

_TEST_REMOTE_CONTAINER_TRAINING_CONFIG_INVALID = configs.DistributedTrainingConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    machine_type=_TEST_MACHINE_TYPE,
    replica_count=_TEST_REPLICA_COUNT,
    accelerator_count=_TEST_ACCELERATOR_COUNT,
    accelerator_type=_TEST_ACCELERATOR_TYPE,
    boot_disk_type=_TEST_BOOT_DISK_TYPE,
    boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
    worker_pool_specs=_TEST_WORKER_POOL_SPECS,
)


# pylint: disable=protected-access,missing-function-docstring
class TestRemoteContainerTrain:
    """Tests for remote_container_train and helper functions."""

    def setup_method(self):
        reload(aiplatform.initializer)
        reload(aiplatform)
        reload(vertexai.preview.initializer)
        reload(vertexai)

    def test_generate_worker_pool_specs_single_machine(self):
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB,
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": _TEST_INPUTS,
                },
            }
        ]

        worker_pool_specs = remote_container_training._generate_worker_pool_specs(
            image_uri=_TEST_IMAGE_URI,
            inputs=_TEST_INPUTS,
            machine_type=_TEST_MACHINE_TYPE,
            replica_count=1,
            boot_disk_type=_TEST_BOOT_DISK_TYPE,
            boot_disk_size_gb=_TEST_BOOT_DISK_SIZE_GB,
        )

        assert worker_pool_specs == expected_worker_pool_specs

    def test_generate_worker_pool_specs_distributed(self):
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                },
                "disk_spec": {
                    "boot_disk_type": "pd-ssd",
                    "boot_disk_size_gb": 100,
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": _TEST_INPUTS,
                },
            },
            {
                "replica_count": 3,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                },
                "disk_spec": {
                    "boot_disk_type": "pd-ssd",
                    "boot_disk_size_gb": 100,
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": _TEST_INPUTS,
                },
            },
        ]

        worker_pool_specs = remote_container_training._generate_worker_pool_specs(
            image_uri=_TEST_IMAGE_URI,
            inputs=_TEST_INPUTS,
            replica_count=4,
            machine_type=_TEST_MACHINE_TYPE,
        )

        assert worker_pool_specs == expected_worker_pool_specs

    def test_generate_worker_pool_specs_gpu(self):
        test_accelerator_type = "NVIDIA_TESLA_K80"
        test_accelerator_count = 8

        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": test_accelerator_type,
                    "accelerator_count": test_accelerator_count,
                },
                "disk_spec": {
                    "boot_disk_type": "pd-ssd",
                    "boot_disk_size_gb": 100,
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": _TEST_INPUTS,
                },
            }
        ]

        worker_pool_specs = remote_container_training._generate_worker_pool_specs(
            image_uri=_TEST_IMAGE_URI,
            inputs=_TEST_INPUTS,
            machine_type=_TEST_MACHINE_TYPE,
            accelerator_count=test_accelerator_count,
            accelerator_type=test_accelerator_type,
        )

        assert worker_pool_specs == expected_worker_pool_specs

    def test_generate_worker_pool_specs_invalid(self):
        with pytest.raises(ValueError) as e:
            remote_container_training._generate_worker_pool_specs(
                image_uri=_TEST_IMAGE_URI,
                inputs=_TEST_INPUTS,
                replica_count=0,
                machine_type=_TEST_MACHINE_TYPE,
            )
        expected_err_msg = "replica_count must be a positive number but is 0."
        assert str(e.value) == expected_err_msg

    # pylint: disable=missing-function-docstring,protected-access
    @pytest.mark.parametrize(
        "remote_config",
        [
            (_TEST_REMOTE_CONTAINER_TRAINING_CONFIG),
            (_TEST_REMOTE_CONTAINER_TRAINING_CONFIG_WORKER_POOL),
        ],
    )
    @pytest.mark.usefixtures(
        "google_auth_mock", "mock_uuid", "mock_get_custom_job_succeeded"
    )
    def test_remote_container_train(
        self,
        mock_blob_upload_from_filename,
        mock_create_custom_job,
        mock_named_temp_file,
        mock_blob_download_to_filename,
        remote_config: configs.DistributedTrainingConfig,
    ):
        # pylint: disable=missing-class-docstring
        class MockTrainer(remote.VertexModel):
            def __init__(self, input_0, input_1):
                super().__init__()
                sig = inspect.signature(self.__init__)
                self._binding = sig.bind(input_0, input_1).arguments
                self.output_0 = None
                self.output_1 = None

            # pylint: disable=invalid-name,unused-argument,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=[
                    remote_specs._InputParameterSpec("input_0"),
                    remote_specs._InputParameterSpec(
                        "input_1", serializer="cloudpickle"
                    ),
                    remote_specs._InputParameterSpec("X", serializer="parquet"),
                    remote_specs._OutputParameterSpec("output_0"),
                    remote_specs._OutputParameterSpec(
                        "output_1", deserializer="cloudpickle"
                    ),
                ],
                remote_config=remote_config,
            )
            def fit(self, X):
                self.output_0 = int(self.output_0)

        def test_input_1(x):
            return x

        test_trainer = MockTrainer(
            input_0="test_input_0",
            input_1=test_input_1,
        )
        test_data = pd.DataFrame(data={"col_0": [0, 1], "col_1": [2, 3]})
        test_output_0 = 10

        def test_output_1(x):
            return x + 1

        assert test_trainer.fit._remote_executor is remote_container_training.train

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Sets up file mocks
            test_input_1_path = os.path.join(tmp_dir, "input_1")
            test_input_1_handler = open(test_input_1_path, "wb")

            test_serialized_path = os.path.join(tmp_dir, "serialized")
            test_serialized_handler = open(test_serialized_path, "wb")

            test_metadata_path = os.path.join(tmp_dir, "metadata")
            test_metadata_handler = open(test_metadata_path, "wb")

            test_output_0_path = os.path.join(tmp_dir, "output_0")
            with open(test_output_0_path, "w") as f:
                f.write(f"{test_output_0}")
            test_output_0_handler = open(test_output_0_path, "r")

            test_output_1_path = os.path.join(tmp_dir, "output_1")
            with open(test_output_1_path, "wb") as f:
                f.write(cloudpickle.dumps(test_output_1))
            test_output_1_handler = open(test_output_1_path, "rb")

            (mock_named_temp_file.return_value.__enter__.side_effect) = [
                test_input_1_handler,
                test_serialized_handler,
                test_metadata_handler,
                test_output_0_handler,
                test_output_1_handler,
            ]

            # Calls the decorated function
            aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)
            test_trainer.fit(test_data)

        # Checks the created custom job and outputs
        expected_inputs = [
            "--input_0=test_input_0",
            f"--input_1={_TEST_STAGING_BUCKET}/input/input_1",
            f"--X={_TEST_STAGING_BUCKET}/input/X",
            f"--output_0={_TEST_STAGING_BUCKET}/output/output_0",
            f"--output_1={_TEST_STAGING_BUCKET}/output/output_1",
        ]

        assert mock_blob_upload_from_filename.call_count == 3
        assert mock_blob_download_to_filename.call_count == 2

        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": _TEST_MACHINE_TYPE,
                    "accelerator_type": _TEST_ACCELERATOR_TYPE,
                    "accelerator_count": _TEST_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": _TEST_BOOT_DISK_TYPE,
                    "boot_disk_size_gb": _TEST_BOOT_DISK_SIZE_GB,
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": expected_inputs,
                },
            }
        ]
        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=f"MockTrainer-{_TEST_DISPLAY_NAME}-0",
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=expected_worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=os.path.join(_TEST_STAGING_BUCKET, "custom_job"),
                ),
            ),
        )
        mock_create_custom_job.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            custom_job=expected_custom_job,
            timeout=None,
        )

        assert test_trainer.output_0 == test_output_0
        # pylint: disable=not-callable
        assert test_trainer.output_1(1) == test_output_1(1)

    # pylint: disable=missing-function-docstring,protected-access
    def test_remote_container_train_invalid_additional_data(self):
        # pylint: disable=missing-class-docstring
        class MockTrainer(remote.VertexModel):
            def __init__(self):
                super().__init__()
                self._binding = {}

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=["invalid"],
                remote_config=configs.DistributedTrainingConfig(
                    staging_bucket=_TEST_STAGING_BUCKET
                ),
            )
            def fit(self):
                return

        test_trainer = MockTrainer()
        assert test_trainer.fit._remote_executor is remote_container_training.train

        with pytest.raises(ValueError, match="Invalid data type"):
            test_trainer.fit()

    @pytest.mark.usefixtures(
        "google_auth_mock", "mock_uuid", "mock_get_custom_job_succeeded"
    )
    def test_remote_container_train_invalid_local(self):
        # pylint: disable=missing-class-docstring
        class MockTrainer(remote.VertexModel):
            def __init__(self):
                super().__init__()
                self._binding = {}

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=[],
                remote_config=configs.DistributedTrainingConfig(
                    staging_bucket=_TEST_STAGING_BUCKET
                ),
            )
            def fit(self):
                return

        test_trainer = MockTrainer()
        assert test_trainer.fit._remote_executor is remote_container_training.train
        test_trainer.fit.vertex.remote = False
        with pytest.raises(
            ValueError,
            match="Remote container train is only supported for remote mode.",
        ):
            test_trainer.fit()

    # pylint: disable=missing-function-docstring,protected-access
    @pytest.mark.usefixtures(
        "google_auth_mock", "mock_uuid", "mock_get_custom_job_succeeded"
    )
    def test_remote_container_train_default_config(self, mock_create_custom_job):
        class MockTrainer(remote.VertexModel):
            def __init__(self):
                super().__init__()
                self._binding = {}

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=[],
            )
            def fit(self):
                return

        test_trainer = MockTrainer()

        aiplatform.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
            staging_bucket=_TEST_STAGING_BUCKET,
        )

        test_trainer.fit()

        expected_display_name = "MockTrainer-remote-fit"
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": remote_container_training._DEFAULT_MACHINE_TYPE,
                    "accelerator_type": (
                        remote_container_training._DEFAULT_ACCELERATOR_TYPE
                    ),
                    "accelerator_count": (
                        remote_container_training._DEFAULT_ACCELERATOR_COUNT
                    ),
                },
                "disk_spec": {
                    "boot_disk_type": remote_container_training._DEFAULT_BOOT_DISK_TYPE,
                    "boot_disk_size_gb": (
                        remote_container_training._DEFAULT_BOOT_DISK_SIZE_GB
                    ),
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": [],
                },
            }
        ]
        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=f"{expected_display_name}-0",
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=expected_worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=os.path.join(_TEST_STAGING_BUCKET, "custom_job"),
                ),
            ),
        )
        mock_create_custom_job.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            custom_job=expected_custom_job,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "google_auth_mock", "mock_uuid", "mock_get_custom_job_succeeded"
    )
    def test_remote_container_train_job_dir(self, mock_create_custom_job):
        class MockTrainer(remote.VertexModel):
            def __init__(self):
                super().__init__()
                self._binding = {"job_dir": ""}

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=[remote_specs._InputParameterSpec("job_dir")],
                remote_config=configs.DistributedTrainingConfig(
                    staging_bucket=_TEST_STAGING_BUCKET
                ),
            )
            def fit(self):
                return

        test_trainer = MockTrainer()

        aiplatform.init(project=_TEST_PROJECT, location=_TEST_LOCATION)

        test_trainer.fit()

        expected_display_name = "MockTrainer-remote-fit"
        expected_job_dir = os.path.join(_TEST_STAGING_BUCKET, "custom_job")
        expected_worker_pool_specs = [
            {
                "replica_count": 1,
                "machine_spec": {
                    "machine_type": remote_container_training._DEFAULT_MACHINE_TYPE,
                    "accelerator_type": remote_container_training._DEFAULT_ACCELERATOR_TYPE,
                    "accelerator_count": remote_container_training._DEFAULT_ACCELERATOR_COUNT,
                },
                "disk_spec": {
                    "boot_disk_type": remote_container_training._DEFAULT_BOOT_DISK_TYPE,
                    "boot_disk_size_gb": remote_container_training._DEFAULT_BOOT_DISK_SIZE_GB,
                },
                "container_spec": {
                    "image_uri": _TEST_IMAGE_URI,
                    "args": [f"--job_dir={expected_job_dir}"],
                },
            }
        ]
        expected_custom_job = gca_custom_job_compat.CustomJob(
            display_name=f"{expected_display_name}-0",
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=expected_worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=os.path.join(_TEST_STAGING_BUCKET, "custom_job"),
                ),
            ),
        )
        mock_create_custom_job.assert_called_once_with(
            parent=f"projects/{_TEST_PROJECT}/locations/{_TEST_LOCATION}",
            custom_job=expected_custom_job,
            timeout=None,
        )

    @pytest.mark.usefixtures(
        "google_auth_mock", "mock_uuid", "mock_get_custom_job_succeeded"
    )
    def test_remote_container_train_invalid_remote_config(self):
        # pylint: disable=missing-class-docstring
        class MockTrainer(remote.VertexModel):
            def __init__(self):
                super().__init__()
                self._binding = {}

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=[],
                remote_config=_TEST_REMOTE_CONTAINER_TRAINING_CONFIG_INVALID,
            )
            def fit(self):
                return

        test_trainer = MockTrainer()
        assert test_trainer.fit._remote_executor is remote_container_training.train
        with pytest.raises(
            ValueError,
            match=re.escape(
                "Cannot specify both 'worker_pool_specs' and ['machine_type', 'accelerator_type', 'accelerator_count', 'replica_count', 'boot_disk_type', 'boot_disk_size_gb']."
            ),
        ):
            test_trainer.fit()
