# -*- coding: utf-8 -*-
# Copyright 2024 Google LLC
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

from google.cloud.aiplatform_v1beta1.types import content
from google.cloud.aiplatform_v1beta1.types import tool
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "CachedContent",
    },
)


class CachedContent(proto.Message):
    r"""A resource used in LLM queries for users to explicitly
    specify what to cache and how to cache.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        expire_time (google.protobuf.timestamp_pb2.Timestamp):
            Timestamp of when this resource is considered expired. This
            is *always* provided on output, regardless of what was sent
            on input.

            This field is a member of `oneof`_ ``expiration``.
        ttl (google.protobuf.duration_pb2.Duration):
            Input only. The TTL for this resource. The
            expiration time is computed: now + TTL.

            This field is a member of `oneof`_ ``expiration``.
        name (str):
            Immutable. Identifier. The resource name of the cached
            content Format:
            projects/{project}/locations/{location}/cachedContents/{cached_content}
        model (str):
            Immutable. The name of the publisher model to
            use for cached content. Format:

            projects/{project}/locations/{location}/publishers/{publisher}/models/{model}
        system_instruction (google.cloud.aiplatform_v1beta1.types.Content):
            Optional. Input only. Immutable. Developer
            set system instruction. Currently, text only
        contents (MutableSequence[google.cloud.aiplatform_v1beta1.types.Content]):
            Optional. Input only. Immutable. The content
            to cache
        tools (MutableSequence[google.cloud.aiplatform_v1beta1.types.Tool]):
            Optional. Input only. Immutable. A list of ``Tools`` the
            model may use to generate the next response
        tool_config (google.cloud.aiplatform_v1beta1.types.ToolConfig):
            Optional. Input only. Immutable. Tool config.
            This config is shared for all tools
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Creatation time of the cache
            entry.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. When the cache entry was last
            updated in UTC time.
    """

    expire_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=9,
        oneof="expiration",
        message=timestamp_pb2.Timestamp,
    )
    ttl: duration_pb2.Duration = proto.Field(
        proto.MESSAGE,
        number=10,
        oneof="expiration",
        message=duration_pb2.Duration,
    )
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    model: str = proto.Field(
        proto.STRING,
        number=2,
    )
    system_instruction: content.Content = proto.Field(
        proto.MESSAGE,
        number=3,
        message=content.Content,
    )
    contents: MutableSequence[content.Content] = proto.RepeatedField(
        proto.MESSAGE,
        number=4,
        message=content.Content,
    )
    tools: MutableSequence[tool.Tool] = proto.RepeatedField(
        proto.MESSAGE,
        number=5,
        message=tool.Tool,
    )
    tool_config: tool.ToolConfig = proto.Field(
        proto.MESSAGE,
        number=6,
        message=tool.ToolConfig,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=7,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=8,
        message=timestamp_pb2.Timestamp,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
