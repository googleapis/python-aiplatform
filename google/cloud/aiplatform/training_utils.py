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

import os


class EnvironmentVariables:
    """Stores OS' environment variables"""

    def __init__(self):
        self.training_data_uri = os.environ["AIP_TRAINING_DATA_URI"]
        self.validation_data_uri = os.environ["AIP_VALIDATION_DATA_URI"]
        self.test_data_uri = os.environ["AIP_TEST_DATA_URI"]
        self.model_dir = os.environ["AIP_MODEL_DIR"]
        self.checkpoint_dir = os.environ["AIP_CHECKPOINT_DIR"]
        self.tensorboard_log_dir = os.environ["AIP_TENSORBOARD_LOG_DIR"]
        self.cluster_spec = os.environ["CLUSTER_SPEC"]

    @property
    def training_data_uri(self) -> str:
        """
        Returns: Cloud Storage URI of a directory intended for training data
        """
        return self.training_data_uri

    @property
    def validation_data_uri(self) -> str:
        """
        Returns: Cloud Storage URI of a directory intended for validation data
        """
        return self.validation_data_uri

    @property
    def test_data_uri(self) -> str:
        """
        Returns: Cloud Storage URI of a directory intended for test data
        """
        return self.test_data_uri

    @property
    def model_dir(self) -> str:
        """
        Returns: Cloud Storage URI of a directory intended for saving model artefacts
        """
        return self.model_dir

    @property
    def checkpoint_dir(self) -> str:
        """
        Returns: Cloud Storage URI of a directory intended for saving checkpoints
        """
        return self.checkpoint_dir

    @property
    def tensorboard_log_dir(self) -> str:
        """
        Returns: Cloud Storage URI of a directory intended for saving TensorBoard logs
        """
        return self.tensorboard_log_dir

    @property
    def cluster_spec(self) -> str:
        """
        Returns: json string as described in https://cloud.google.com/ai-platform-unified/docs/training/distributed-training#cluster-variables
        """
        return self.cluster_spec
