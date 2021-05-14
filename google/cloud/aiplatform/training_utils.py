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

import collections
import json
import os
import time
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


_DEFAULT_HYPERPARAMETER_METRIC_TAG = "training/hptuning/metric"
_DEFAULT_METRIC_PATH = "/tmp/hypertune/output.metrics"
# TODO(0olwzo0): consider to make it configurable
_MAX_NUM_METRIC_ENTRIES_TO_PRESERVE = 100


class _HyperparameterTuningJobReporterSingleton:
    """Main class for HyperTune."""

    initialized = False

    @classmethod
    def initialize(cls):
        if cls.initialized:
            return

        cls.metric_path = os.environ.get(
            "CLOUD_ML_HP_METRIC_FILE", _DEFAULT_METRIC_PATH
        )
        if not os.path.exists(os.path.dirname(cls.metric_path)):
            os.makedirs(os.path.dirname(cls.metric_path))

        cls.trial_id = os.environ.get("CLOUD_ML_TRIAL_ID", 0)
        cls.metrics_queue = collections.deque(
            maxlen=_MAX_NUM_METRIC_ENTRIES_TO_PRESERVE
        )

        cls.initialized = True

    @classmethod
    def _dump_metrics_to_file(cls):
        with open(cls.metric_path, "w") as metric_file:
            for metric in cls.metrics_queue:
                metric_file.write(json.dumps(metric, sort_keys=True) + "\n")

    @classmethod
    def report_hyperparameter_tuning_metric(
        cls,
        hyperparameter_metric_tag,
        metric_value,
        global_step=None,
        checkpoint_path="",
    ):
        """Method to report hyperparameter tuning metric.
        Args:
          hyperparameter_metric_tag: The hyperparameter metric name this metric
            value is associated with. Should keep consistent with the tag
            specified in HyperparameterSpec.
          metric_value: float, the values for the hyperparameter metric to report.
          global_step: int, the global step this metric value is associated with.
          checkpoint_path: The checkpoint path which can be used to warmstart from.
        """
        metric_value = float(metric_value)
        metric_tag = _DEFAULT_HYPERPARAMETER_METRIC_TAG
        if hyperparameter_metric_tag:
            metric_tag = hyperparameter_metric_tag
        metric_body = {
            "timestamp": time.time(),
            "trial": str(cls.trial_id),
            metric_tag: str(metric_value),
            "global_step": str(int(global_step) if global_step else 0),
            "checkpoint_path": checkpoint_path,
        }
        cls.metrics_queue.append(metric_body)
        cls._dump_metrics_to_file()


def report_hyperparameter_tuning_metrics(
    metrics: Dict[str, float], global_step: Optional[int] = None, checkpoint_path=""
):
    _HyperparameterTuningJobReporterSingleton.initialize()

    for hyperparameter_metric_tag, metric_value in metrics.items():
        _HyperparameterTuningJobReporterSingleton.report_hyperparameter_tuning_metric(
            hyperparameter_metric_tag=hyperparameter_metric_tag,
            metric_value=metric_value,
            global_step=global_step,
            checkpoint_path=checkpoint_path,
        )
