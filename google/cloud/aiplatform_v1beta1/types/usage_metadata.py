# -*- coding: utf-8 -*-
# Copyright 2025 Google LLC
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


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "UsageMetadata",
    },
)


class UsageMetadata(proto.Message):
    r"""Usage metadata about the content generation request and
    response. This message provides a detailed breakdown of token
    usage and other relevant metrics.

    Attributes:
        prompt_token_count (int):
            The total number of tokens in the prompt. This includes any
            text, images, or other media provided in the request. When
            ``cached_content`` is set, this also includes the number of
            tokens in the cached content.
        candidates_token_count (int):
            The total number of tokens in the generated
            candidates.
        total_token_count (int):
            The total number of tokens for the entire request. This is
            the sum of ``prompt_token_count``,
            ``candidates_token_count``, ``tool_use_prompt_token_count``,
            and ``thoughts_token_count``.
        tool_use_prompt_token_count (int):
            Output only. The number of tokens in the
            results from tool executions, which are provided
            back to the model as input, if applicable.
        thoughts_token_count (int):
            Output only. The number of tokens that were
            part of the model's generated "thoughts" output,
            if applicable.
        cached_content_token_count (int):
            Output only. The number of tokens in the
            cached content that was used for this request.
        prompt_tokens_details (MutableSequence[google.cloud.aiplatform_v1beta1.types.ModalityTokenCount]):
            Output only. A detailed breakdown of the
            token count for each modality in the prompt.
        cache_tokens_details (MutableSequence[google.cloud.aiplatform_v1beta1.types.ModalityTokenCount]):
            Output only. A detailed breakdown of the
            token count for each modality in the cached
            content.
        candidates_tokens_details (MutableSequence[google.cloud.aiplatform_v1beta1.types.ModalityTokenCount]):
            Output only. A detailed breakdown of the
            token count for each modality in the generated
            candidates.
        tool_use_prompt_tokens_details (MutableSequence[google.cloud.aiplatform_v1beta1.types.ModalityTokenCount]):
            Output only. A detailed breakdown by modality
            of the token counts from the results of tool
            executions, which are provided back to the model
            as input.
        traffic_type (google.cloud.aiplatform_v1beta1.types.UsageMetadata.TrafficType):
            Output only. The traffic type for this
            request.
    """

    class TrafficType(proto.Enum):
        r"""The type of traffic that this request was processed with,
        indicating which quota gets consumed.

        Values:
            TRAFFIC_TYPE_UNSPECIFIED (0):
                Unspecified request traffic type.
            ON_DEMAND (1):
                Type for Pay-As-You-Go traffic.
            PROVISIONED_THROUGHPUT (2):
                Type for Provisioned Throughput traffic.
        """

        TRAFFIC_TYPE_UNSPECIFIED = 0
        ON_DEMAND = 1
        PROVISIONED_THROUGHPUT = 2

    prompt_token_count: int = proto.Field(
        proto.INT32,
        number=1,
    )
    candidates_token_count: int = proto.Field(
        proto.INT32,
        number=2,
    )
    total_token_count: int = proto.Field(
        proto.INT32,
        number=3,
    )
    tool_use_prompt_token_count: int = proto.Field(
        proto.INT32,
        number=13,
    )
    thoughts_token_count: int = proto.Field(
        proto.INT32,
        number=14,
    )
    cached_content_token_count: int = proto.Field(
        proto.INT32,
        number=5,
    )
    prompt_tokens_details: MutableSequence[content.ModalityTokenCount] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=9,
            message=content.ModalityTokenCount,
        )
    )
    cache_tokens_details: MutableSequence[content.ModalityTokenCount] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=10,
            message=content.ModalityTokenCount,
        )
    )
    candidates_tokens_details: MutableSequence[content.ModalityTokenCount] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=11,
            message=content.ModalityTokenCount,
        )
    )
    tool_use_prompt_tokens_details: MutableSequence[content.ModalityTokenCount] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=12,
            message=content.ModalityTokenCount,
        )
    )
    traffic_type: TrafficType = proto.Field(
        proto.ENUM,
        number=8,
        enum=TrafficType,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
