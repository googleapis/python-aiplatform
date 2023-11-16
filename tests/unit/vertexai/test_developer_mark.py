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

import functools

import vertexai
from vertexai.preview._workflow import driver
from vertexai.preview._workflow.driver import remote
from vertexai.preview._workflow.executor import (
    remote_container_training,
)
from vertexai.preview._workflow.shared import (
    configs,
)
from vertexai.preview.developer import remote_specs
import pytest

# RemoteConfig constants
_TEST_DISPLAY_NAME = "test_display_name"
_TEST_STAGING_BUCKET = "gs://test-staging-bucket"
_TEST_CONTAINER_URI = "gcr.io/test-image"
_TEST_MACHINE_TYPE = "n1-standard-4"
_TEST_SERVICE_ACCOUNT = "test-service-account"
_TEST_WORKER_POOL_SPECS = remote_specs.WorkerPoolSpecs(
    chief=remote_specs.WorkerPoolSpec(
        machine_type=_TEST_MACHINE_TYPE,
    )
)

_TEST_TRAINING_CONFIG = configs.RemoteConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    container_uri=_TEST_CONTAINER_URI,
    machine_type=_TEST_MACHINE_TYPE,
    service_account=_TEST_SERVICE_ACCOUNT,
)

_TEST_TRAINING_CONFIG_WORKER_POOL = configs.RemoteConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    container_uri=_TEST_CONTAINER_URI,
    worker_pool_specs=_TEST_WORKER_POOL_SPECS,
    service_account=_TEST_SERVICE_ACCOUNT,
)

# Remote training custom job constants
_TEST_IMAGE_URI = "test_image_uri"
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
_TEST_REMOTE_CONTAINER_TRAINING_CONFIG_WORKER_POOL = configs.DistributedTrainingConfig(
    display_name=_TEST_DISPLAY_NAME,
    staging_bucket=_TEST_STAGING_BUCKET,
    worker_pool_specs=_TEST_WORKER_POOL_SPECS,
)

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


class TestDeveloperMark:
    def test_mark_train(self):
        class TestClass(vertexai.preview.VertexModel):
            @vertexai.preview.developer.mark.train()
            def test_method(x, y):
                return x + y

        assert isinstance(TestClass.test_method, driver.VertexRemoteFunctor)
        assert TestClass.test_method.vertex == configs.VertexConfig

        test_class = TestClass()

        assert isinstance(test_class.test_method, driver.VertexRemoteFunctor)
        assert isinstance(test_class.test_method.vertex, configs.VertexConfig)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_mark_train_with_all_args(self):
        class TestClass(vertexai.preview.VertexModel):
            @vertexai.preview.developer.mark.train(remote_config=_TEST_TRAINING_CONFIG)
            def test_method(self, x, y):
                return x + y

        test_class = TestClass()

        assert isinstance(test_class.test_method, driver.VertexRemoteFunctor)
        assert (
            test_class.test_method.vertex.remote_config.display_name
            == _TEST_DISPLAY_NAME
        )
        assert (
            test_class.test_method.vertex.remote_config.staging_bucket
            == _TEST_STAGING_BUCKET
        )
        assert (
            test_class.test_method.vertex.remote_config.container_uri
            == _TEST_CONTAINER_URI
        )
        assert (
            test_class.test_method.vertex.remote_config.machine_type
            == _TEST_MACHINE_TYPE
        )
        assert (
            test_class.test_method.vertex.remote_config.service_account
            == _TEST_SERVICE_ACCOUNT
        )

    @pytest.mark.usefixtures("google_auth_mock")
    def test_mark_train_with_worker_pool_specs(self):
        class TestClass(vertexai.preview.VertexModel):
            @vertexai.preview.developer.mark.train(
                remote_config=_TEST_TRAINING_CONFIG_WORKER_POOL
            )
            def test_method(self, x, y):
                return x + y

        test_class = TestClass()

        assert isinstance(test_class.test_method, driver.VertexRemoteFunctor)
        assert (
            test_class.test_method.vertex.remote_config.display_name
            == _TEST_DISPLAY_NAME
        )
        assert (
            test_class.test_method.vertex.remote_config.staging_bucket
            == _TEST_STAGING_BUCKET
        )
        assert (
            test_class.test_method.vertex.remote_config.container_uri
            == _TEST_CONTAINER_URI
        )
        assert (
            test_class.test_method.vertex.remote_config.worker_pool_specs
            == _TEST_WORKER_POOL_SPECS
        )

    # pylint: disable=missing-function-docstring,protected-access)
    @pytest.mark.parametrize(
        "remote_config,expected_config",
        [
            (
                _TEST_REMOTE_CONTAINER_TRAINING_CONFIG,
                _TEST_REMOTE_CONTAINER_TRAINING_CONFIG,
            ),
            (None, configs.DistributedTrainingConfig()),
            (
                _TEST_REMOTE_CONTAINER_TRAINING_CONFIG_WORKER_POOL,
                _TEST_REMOTE_CONTAINER_TRAINING_CONFIG_WORKER_POOL,
            ),
        ],
    )
    def test_mark_remote_container_train(self, remote_config, expected_config):
        test_additional_data = [remote_specs._InputParameterSpec("arg_0")]

        # pylint: disable=missing-class-docstring
        class MockTrainer(remote.VertexModel):

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=test_additional_data,
                remote_config=remote_config,
            )
            def fit(self):
                return

        assert isinstance(MockTrainer.fit, driver.VertexRemoteFunctor)
        assert isinstance(MockTrainer.fit.vertex, functools.partial)
        assert MockTrainer.fit.vertex.func == configs.VertexConfig
        assert not MockTrainer.fit.vertex.args
        assert MockTrainer.fit.vertex.keywords == {
            "remote_config": expected_config,
            "remote": True,
        }

        test_trainer = MockTrainer()
        assert isinstance(test_trainer.fit, driver.VertexRemoteFunctor)
        assert test_trainer.fit.vertex.remote_config == expected_config
        assert test_trainer.fit._remote_executor is remote_container_training.train
        assert test_trainer.fit._remote_executor_kwargs == {
            "additional_data": test_additional_data,
            "image_uri": _TEST_IMAGE_URI,
        }
        assert test_trainer.fit.vertex.remote

    # pylint: disable=missing-function-docstring,protected-access
    def test_mark_remote_container_train_override_remote_config(self):
        # pylint: disable=missing-class-docstring
        class MockTrainer(remote.VertexModel):

            # pylint: disable=invalid-name,missing-function-docstring
            @vertexai.preview.developer.mark._remote_container_train(
                image_uri=_TEST_IMAGE_URI,
                additional_data=[],
                remote_config=configs.DistributedTrainingConfig(),
            )
            def fit(self):
                return

        test_trainer = MockTrainer()
        assert isinstance(test_trainer.fit, driver.VertexRemoteFunctor)
        assert (
            test_trainer.fit.vertex.remote_config == configs.DistributedTrainingConfig()
        )
        assert test_trainer.fit._remote_executor is remote_container_training.train
        assert test_trainer.fit._remote_executor_kwargs == {
            "additional_data": [],
            "image_uri": _TEST_IMAGE_URI,
        }

        # Overrides training config
        test_remote_config = test_trainer.fit.vertex.remote_config
        test_remote_config.display_name = _TEST_DISPLAY_NAME
        test_remote_config.staging_bucket = _TEST_STAGING_BUCKET
        test_remote_config.machine_type = _TEST_MACHINE_TYPE
        test_remote_config.replica_count = _TEST_REPLICA_COUNT
        test_remote_config.accelerator_type = _TEST_ACCELERATOR_TYPE
        test_remote_config.accelerator_count = _TEST_ACCELERATOR_COUNT
        test_remote_config.boot_disk_type = _TEST_BOOT_DISK_TYPE
        test_remote_config.boot_disk_size_gb = _TEST_BOOT_DISK_SIZE_GB

        assert (
            test_trainer.fit.vertex.remote_config
            == _TEST_REMOTE_CONTAINER_TRAINING_CONFIG
        )

    def test_mark_predict(self):
        class TestClass(vertexai.preview.VertexModel):
            @vertexai.preview.developer.mark.predict()
            def test_method(x, y):
                return x + y

        assert isinstance(TestClass.test_method, driver.VertexRemoteFunctor)
        assert TestClass.test_method.vertex == configs.VertexConfig

        test_class = TestClass()

        assert isinstance(test_class.test_method, driver.VertexRemoteFunctor)
        assert isinstance(test_class.test_method.vertex, configs.VertexConfig)

    def test_mark_predict_with_all_args(self):
        class TestClass(vertexai.preview.VertexModel):
            @vertexai.preview.developer.mark.predict(
                remote_config=_TEST_TRAINING_CONFIG
            )
            def test_method(self, x, y):
                return x + y

        test_class = TestClass()

        assert isinstance(test_class.test_method, driver.VertexRemoteFunctor)
        assert (
            test_class.test_method.vertex.remote_config.display_name
            == _TEST_DISPLAY_NAME
        )
        assert (
            test_class.test_method.vertex.remote_config.staging_bucket
            == _TEST_STAGING_BUCKET
        )
        assert (
            test_class.test_method.vertex.remote_config.container_uri
            == _TEST_CONTAINER_URI
        )
        assert (
            test_class.test_method.vertex.remote_config.machine_type
            == _TEST_MACHINE_TYPE
        )
        assert (
            test_class.test_method.vertex.remote_config.service_account
            == _TEST_SERVICE_ACCOUNT
        )
