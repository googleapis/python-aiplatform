# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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
SYSTEM_PIPELINE = "system.Pipeline"
SYSTEM_METRICS = "system.Metrics"

_DEFAULT_SCHEMA_VERSION = "0.0.1"

SCHEMA_VERSIONS = {
    SYSTEM_RUN: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_EXPERIMENT: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_PIPELINE: _DEFAULT_SCHEMA_VERSION,
    SYSTEM_METRICS: _DEFAULT_SCHEMA_VERSION,
}

# The EXPERIMENT_METADATA is needed until we support context deletion in backend service.
# TODO: delete EXPERIMENT_METADATA once backend supports context deletion.
EXPERIMENT_METADATA = {"experiment_deleted": False}
