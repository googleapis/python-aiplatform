# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

SYSTEM_RUN = "system.Run"
SYSTEM_EXPERIMENT = "system.Experiment"
SYSTEM_EXPERIMENT_RUN = "system.ExperimentRun"
SYSTEM_PIPELINE = "system.Pipeline"
SYSTEM_PIPELINE_RUN = "system.PipelineRun"
SYSTEM_METRICS = "system.Metrics"

_EXPERIMENTS_V2_TENSORBOARD_RUN = "google.VertexTensorboardRun"

_DEFAULT_SCHEMA_VERSION = "0.0.1"

SCHEMA_VERSIONS = {
    SYSTEM_RUN: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_EXPERIMENT: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_EXPERIMENT_RUN: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_PIPELINE: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_METRICS: _DEFAULT_SCHEMA_VERSION,
}

_BACKING_TENSORBOARD_RESOURCE_KEY = "backing_tensorboard_resource"


_PARAM_KEY = "_params"
_METRIC_KEY = "_metrics"
_STATE_KEY = "_state"

_PARAM_PREFIX = "param"
_METRIC_PREFIX = "metric"
_TIME_SERIES_METRIC_PREFIX = "time_series_metric"

# This is currently used to filter in the Console.
EXPERIMENT_METADATA = {"experiment_deleted": False}

PIPELINE_PARAM_PREFIX = "input:"

TENSORBOARD_CUSTOM_JOB_EXPERIMENT_FIELD = "tensorboard_link"


GCP_ARTIFACT_RESOURCE_NAME_KEY = "resourceName"
