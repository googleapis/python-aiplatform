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


def training_data_uri() -> str:
    """
    Returns: Cloud Storage URI of a directory intended for training data
    """
    return os.environ["AIP_TRAINING_DATA_URI"]


def validation_data_uri() -> str:
    """
    Returns: Cloud Storage URI of a directory intended for validation data
    """
    return os.environ["AIP_VALIDATION_DATA_URI"]


def test_data_uri() -> str:
    """
    Returns: Cloud Storage URI of a directory intended for test data
    """
    return os.environ["AIP_TEST_DATA_URI"]


def model_dir() -> str:
    """
    Returns: Cloud Storage URI of a directory intended for saving model artefacts
    """
    return os.environ["AIP_MODEL_DIR"]


def checkpoint_dir() -> str:
    """
    Returns: Cloud Storage URI of a directory intended for saving checkpoints
    """
    return os.environ["AIP_CHECKPOINT_DIR"]


def tensorboard_log_dir() -> str:
    """
    Returns: Cloud Storage URI of a directory intended for saving TensorBoard logs
    """
    return os.environ["AIP_TENSORBOARD_LOG_DIR"]


def cluster_spec() -> str:
    """
    Returns: json string as described in https://cloud.google.com/ai-platform-unified/docs/training/distributed-training#cluster-variables
    """
    return os.environ["CLUSTER_SPEC"]
