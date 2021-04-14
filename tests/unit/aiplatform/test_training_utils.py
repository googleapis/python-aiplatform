# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

import json
import os
import pytest

from google.cloud.aiplatform import training_utils
from unittest import mock

_TEST_TRAINING_DATA_URI = "gs://training-data-uri"
_TEST_VALIDATION_DATA_URI = "gs://test-validation-data-uri"
_TEST_TEST_DATA_URI = "gs://test-data-uri"
_TEST_MODEL_DIR = "gs://test-model-dir"
_TEST_CHECKPOINT_DIR = "gs://test-checkpoint-dir"
_TEST_TENSORBOARD_LOG_DIR = "gs://test-tensorboard-log-dir"
_TEST_CLUSTER_SPEC = """{
    "cluster": {
        "worker_pools":[
            {
                "index":0,
                "replicas":[
                    "training-workerpool0-ab-0:2222"
                ]
            },
            {
                "index":1,
                "replicas":[
                    "training-workerpool1-ab-0:2222",
                    "training-workerpool1-ab-1:2222"
                ]
            }
        ]
    },
    "environment": "cloud",
    "task": {
        "worker_pool_index":0,
        "replica_index":0,
        "trial":"TRIAL_ID"
    }
}"""


class TestTrainingUtils:
    @pytest.fixture
    def mock_environment(self):
        env_vars = {
            "AIP_TRAINING_DATA_URI": _TEST_TRAINING_DATA_URI,
            "AIP_VALIDATION_DATA_URI": _TEST_VALIDATION_DATA_URI,
            "AIP_TEST_DATA_URI": _TEST_TEST_DATA_URI,
            "AIP_MODEL_DIR": _TEST_MODEL_DIR,
            "AIP_CHECKPOINT_DIR": _TEST_CHECKPOINT_DIR,
            "AIP_TENSORBOARD_LOG_DIR": _TEST_TENSORBOARD_LOG_DIR,
            "CLUSTER_SPEC": _TEST_CLUSTER_SPEC,
            "TF_CONFIG": _TEST_CLUSTER_SPEC,
        }
        with mock.patch.dict(os.environ, env_vars):
            yield

    @pytest.mark.usefixtures("mock_environment")
    def test_training_data_uri(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.training_data_uri == _TEST_TRAINING_DATA_URI

    def test_training_data_uri_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.training_data_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_validation_data_uri(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.validation_data_uri == _TEST_VALIDATION_DATA_URI

    def test_validation_data_uri_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.validation_data_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_test_data_uri(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.test_data_uri == _TEST_TEST_DATA_URI

    def test_test_data_uri_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.test_data_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_model_dir(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.model_dir == _TEST_MODEL_DIR

    def test_model_dir_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.model_dir is None

    @pytest.mark.usefixtures("mock_environment")
    def test_checkpoint_dir(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.checkpoint_dir == _TEST_CHECKPOINT_DIR

    def test_checkpoint_dir_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.checkpoint_dir is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tensorboard_log_dir(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.tensorboard_log_dir == _TEST_TENSORBOARD_LOG_DIR

    def test_tensorboard_log_dir_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.tensorboard_log_dir is None

    @pytest.mark.usefixtures("mock_environment")
    def test_cluster_spec(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.cluster_spec == json.loads(_TEST_CLUSTER_SPEC)

    def test_cluster_spec_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.cluster_spec is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tf_config(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.tf_config == json.loads(_TEST_CLUSTER_SPEC)

    def test_tf_config_none(self):
        env_vars = training_utils.EnvironmentVariables()
        assert env_vars.tf_config is None
