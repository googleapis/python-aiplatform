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
import proto  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "JobState",
    },
)


class JobState(proto.Enum):
    r"""Describes the state of a job."""
    JOB_STATE_UNSPECIFIED = 0
    JOB_STATE_QUEUED = 1
    JOB_STATE_PENDING = 2
    JOB_STATE_RUNNING = 3
    JOB_STATE_SUCCEEDED = 4
    JOB_STATE_FAILED = 5
    JOB_STATE_CANCELLING = 6
    JOB_STATE_CANCELLED = 7
    JOB_STATE_PAUSED = 8
    JOB_STATE_EXPIRED = 9
    JOB_STATE_UPDATING = 10


__all__ = tuple(sorted(__protobuf__.manifest))
