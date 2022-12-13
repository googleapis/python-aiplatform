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
from typing import MutableMapping, MutableSequence

import proto  # type: ignore


__protobuf__ = proto.module(
    package='google.cloud.aiplatform.v1',
    manifest={
        'PipelineState',
    },
)


class PipelineState(proto.Enum):
    r"""Describes the state of a pipeline."""
    PIPELINE_STATE_UNSPECIFIED = 0
    PIPELINE_STATE_QUEUED = 1
    PIPELINE_STATE_PENDING = 2
    PIPELINE_STATE_RUNNING = 3
    PIPELINE_STATE_SUCCEEDED = 4
    PIPELINE_STATE_FAILED = 5
    PIPELINE_STATE_CANCELLING = 6
    PIPELINE_STATE_CANCELLED = 7
    PIPELINE_STATE_PAUSED = 8


__all__ = tuple(sorted(__protobuf__.manifest))