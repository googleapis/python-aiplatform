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


from google.cloud.aiplatform.private_preview.vertex_ai import initializer
from google.cloud.aiplatform.private_preview.vertex_ai._workflow.driver import remote
from google.cloud.aiplatform.private_preview.vertex_ai._workflow.launcher import (
    training,
)


global_config = initializer.global_config
init = global_config.init
remote = remote.remote
TrainingConfig = training.TrainingConfig


# TODO(b/271612103) Implement import hook


__all__ = (
    "init",
    "remote",
    "TrainingConfig",
)