# -*- coding: utf-8 -*-
# Copyright 2026 Google LLC
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
from __future__ import annotations

from typing import MutableMapping, MutableSequence

import proto  # type: ignore

from google.cloud.aiplatform_v1beta1.types import reasoning_engine
import google.protobuf.timestamp_pb2 as timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "ReasoningEngineRuntimeRevision",
    },
)


class ReasoningEngineRuntimeRevision(proto.Message):
    r"""ReasoningEngineRuntimeRevision is a specific version of the
    runtime related part of ReasoningEngine. Contains only the
    fields that are revision specific.

    Attributes:
        name (str):
            Identifier. The resource name of the
            ReasoningEngineRuntimeRevision. Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}/runtimeRevisions/{runtime_revision}``
        spec (google.cloud.aiplatform_v1beta1.types.ReasoningEngineSpec):
            Immutable. Configurations of the
            ReasoningEngineRuntimeRevision. Contains only
            revision specific fields.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            ReasoningEngineRuntimeRevision was created.
        state (google.cloud.aiplatform_v1beta1.types.ReasoningEngineRuntimeRevision.State):
            Output only. The state of the revision.
    """

    class State(proto.Enum):
        r"""Possible values of the state of the revision.

        Values:
            STATE_UNSPECIFIED (0):
                The unspecified state.
            ACTIVE (1):
                Is deployed and ready to be used.
            DEPRECATED (2):
                Is deprecated, may not be used, only
                preserved for historical purposes.
        """

        STATE_UNSPECIFIED = 0
        ACTIVE = 1
        DEPRECATED = 2

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    spec: reasoning_engine.ReasoningEngineSpec = proto.Field(
        proto.MESSAGE,
        number=3,
        message=reasoning_engine.ReasoningEngineSpec,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=4,
        message=timestamp_pb2.Timestamp,
    )
    state: State = proto.Field(
        proto.ENUM,
        number=5,
        enum=State,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
