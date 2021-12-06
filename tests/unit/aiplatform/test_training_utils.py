# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from importlib import reload
import json
import os
import pytest

from google.cloud.aiplatform.training_utils import environment_variables
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
_TEST_AIP_TF_PROFILER_PORT = "1234"
_TEST_TENSORBOARD_API_URI = "http://testuri.com"
_TEST_TENSORBOARD_RESOURCE_NAME = (
    "projects/myproj/locations/us-central1/tensorboards/1234"
)
_TEST_CLOUD_ML_JOB_ID = "myjob"
_TEST_AIP_HTTP_HANDLER_PORT = "5678"


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
            "AIP_TF_PROFILER_PORT": _TEST_AIP_TF_PROFILER_PORT,
            "AIP_HTTP_HANDLER_PORT": _TEST_AIP_HTTP_HANDLER_PORT,
            "AIP_TENSORBOARD_API_URI": _TEST_TENSORBOARD_API_URI,
            "AIP_TENSORBOARD_RESOURCE_NAME": _TEST_TENSORBOARD_RESOURCE_NAME,
            "CLOUD_ML_JOB_ID": _TEST_CLOUD_ML_JOB_ID,
            "CLUSTER_SPEC": _TEST_CLUSTER_SPEC,
            "TF_CONFIG": _TEST_CLUSTER_SPEC,
        }
        with mock.patch.dict(os.environ, env_vars, clear=True):
            yield

    @pytest.mark.usefixtures("mock_environment")
    def test_training_data_uri(self):
        reload(environment_variables)
        assert environment_variables.training_data_uri == _TEST_TRAINING_DATA_URI

    def test_training_data_uri_none(self):
        reload(environment_variables)
        assert environment_variables.training_data_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_validation_data_uri(self):
        reload(environment_variables)
        assert environment_variables.validation_data_uri == _TEST_VALIDATION_DATA_URI

    def test_validation_data_uri_none(self):
        reload(environment_variables)
        assert environment_variables.validation_data_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_test_data_uri(self):
        reload(environment_variables)
        assert environment_variables.test_data_uri == _TEST_TEST_DATA_URI

    def test_test_data_uri_none(self):
        reload(environment_variables)
        assert environment_variables.test_data_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_model_dir(self):
        reload(environment_variables)
        assert environment_variables.model_dir == _TEST_MODEL_DIR

    def test_model_dir_none(self):
        reload(environment_variables)
        assert environment_variables.model_dir is None

    @pytest.mark.usefixtures("mock_environment")
    def test_checkpoint_dir(self):
        reload(environment_variables)
        assert environment_variables.checkpoint_dir == _TEST_CHECKPOINT_DIR

    def test_checkpoint_dir_none(self):
        reload(environment_variables)
        assert environment_variables.checkpoint_dir is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tensorboard_log_dir(self):
        reload(environment_variables)
        assert environment_variables.tensorboard_log_dir == _TEST_TENSORBOARD_LOG_DIR

    def test_tensorboard_log_dir_none(self):
        reload(environment_variables)
        assert environment_variables.tensorboard_log_dir is None

    @pytest.mark.usefixtures("mock_environment")
    def test_cluster_spec(self):
        reload(environment_variables)
        assert environment_variables.cluster_spec == json.loads(_TEST_CLUSTER_SPEC)

    def test_cluster_spec_none(self):
        reload(environment_variables)
        assert environment_variables.cluster_spec is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tf_config(self):
        reload(environment_variables)
        assert environment_variables.tf_config == json.loads(_TEST_CLUSTER_SPEC)

    def test_tf_config_none(self):
        reload(environment_variables)
        assert environment_variables.tf_config is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tf_profiler_port(self):
        reload(environment_variables)
        assert environment_variables.tf_profiler_port == _TEST_AIP_TF_PROFILER_PORT

    def test_tf_profiler_port_none(self):
        reload(environment_variables)
        assert environment_variables.tf_profiler_port is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tensorboard_api_uri(self):
        reload(environment_variables)
        assert environment_variables.tensorboard_api_uri == _TEST_TENSORBOARD_API_URI

    def test_tensorboard_api_uri_none(self):
        reload(environment_variables)
        assert environment_variables.tensorboard_api_uri is None

    @pytest.mark.usefixtures("mock_environment")
    def test_tensorboard_resource_name(self):
        reload(environment_variables)
        assert (
            environment_variables.tensorboard_resource_name
            == _TEST_TENSORBOARD_RESOURCE_NAME
        )

    def test_tensorboard_resource_name_none(self):
        reload(environment_variables)
        assert environment_variables.tensorboard_resource_name is None

    @pytest.mark.usefixtures("mock_environment")
    def test_cloud_ml_job_id(self):
        reload(environment_variables)
        assert environment_variables.cloud_ml_job_id == _TEST_CLOUD_ML_JOB_ID

    def test_cloud_ml_job_id_none(self):
        reload(environment_variables)
        assert environment_variables.cloud_ml_job_id is None

    @pytest.mark.usefixtures("mock_environment")
    def test_http_handler_port(self):
        reload(environment_variables)
        assert environment_variables.http_handler_port == _TEST_AIP_HTTP_HANDLER_PORT

    def test_http_handler_port_none(self):
        reload(environment_variables)
        assert environment_variables.http_handler_port is None
