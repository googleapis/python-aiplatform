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

from typing import Dict, Optional


class EnvironmentVariables:
    """Passes on OS' environment variables."""

    @property
    def training_data_uri(self) -> Optional[str]:
        """
        Returns:
            Cloud Storage URI of a directory intended for training data. None if
            environment variable not set.
        """
        return os.environ.get("AIP_TRAINING_DATA_URI")

    @property
    def validation_data_uri(self) -> Optional[str]:
        """
        Returns:
            Cloud Storage URI of a directory intended for validation data. None
            if environment variable not set.
        """
        return os.environ.get("AIP_VALIDATION_DATA_URI")

    @property
    def test_data_uri(self) -> Optional[str]:
        """
        Returns:
            Cloud Storage URI of a directory intended for test data. None if
            environment variable not set.
        """
        return os.environ.get("AIP_TEST_DATA_URI")

    @property
    def model_dir(self) -> Optional[str]:
        """
        Returns:
            Cloud Storage URI of a directory intended for saving model artefacts.
            None if environment variable not set.
        """
        return os.environ.get("AIP_MODEL_DIR")

    @property
    def checkpoint_dir(self) -> Optional[str]:
        """
        Returns:
            Cloud Storage URI of a directory intended for saving checkpoints.
            None if environment variable not set.
        """
        return os.environ.get("AIP_CHECKPOINT_DIR")

    @property
    def tensorboard_log_dir(self) -> Optional[str]:
        """
        Returns:
            Cloud Storage URI of a directory intended for saving TensorBoard logs.
            None if environment variable not set.
        """
        return os.environ.get("AIP_TENSORBOARD_LOG_DIR")

    @property
    def cluster_spec(self) -> Optional[Dict]:
        """
        Returns:
            json string as described in https://cloud.google.com/ai-platform-unified/docs/training/distributed-training#cluster-variables
            None if environment variable not set.
        """
        cluster_spec_env = os.environ.get("CLUSTER_SPEC")
        if cluster_spec_env is not None:
            return json.loads(cluster_spec_env)
        else:
            return None

    @property
    def tf_config(self) -> Optional[Dict]:
        """
        Returns:
            json string as described in https://cloud.google.com/ai-platform-unified/docs/training/distributed-training#tf-config
            None if environment variable not set.
        """
        tf_config_env = os.environ.get("TF_CONFIG")
        if tf_config_env is not None:
            return json.loads(tf_config_env)
        else:
            return None
