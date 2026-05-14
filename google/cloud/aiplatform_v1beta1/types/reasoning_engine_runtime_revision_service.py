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

from google.cloud.aiplatform_v1beta1.types import operation
from google.cloud.aiplatform_v1beta1.types import reasoning_engine_runtime_revision


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "DeleteReasoningEngineRuntimeRevisionOperationMetadata",
        "GetReasoningEngineRuntimeRevisionRequest",
        "ListReasoningEngineRuntimeRevisionsRequest",
        "ListReasoningEngineRuntimeRevisionsResponse",
        "DeleteReasoningEngineRuntimeRevisionRequest",
    },
)


class DeleteReasoningEngineRuntimeRevisionOperationMetadata(proto.Message):
    r"""Metadata associated with DeleteReasoningEngineRuntimeRevision
    operation.

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            The common part of the operation metadata.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class GetReasoningEngineRuntimeRevisionRequest(proto.Message):
    r"""Request message for
    [ReasoningEngineRuntimeRevisionService.GetReasoningEngineRuntimeRevision][google.cloud.aiplatform.v1beta1.ReasoningEngineRuntimeRevisionService.GetReasoningEngineRuntimeRevision].

    Attributes:
        name (str):
            Required. The name of the ReasoningEngineRuntimeRevision
            resource. Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}/runtimeRevisions/{runtimeRevision}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListReasoningEngineRuntimeRevisionsRequest(proto.Message):
    r"""Request message for
    [ReasoningEngineRuntimeRevisionService.ListReasoningEngineRuntimeRevisions][google.cloud.aiplatform.v1beta1.ReasoningEngineRuntimeRevisionService.ListReasoningEngineRuntimeRevisions].

    Attributes:
        parent (str):
            Required. The resource name of the ReasoningEngine to list
            the ReasoningEngineRuntimeRevisions from. Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}``
        filter (str):
            Optional. The standard list filter. More detail in
            `AIP-160 <https://google.aip.dev/160>`__.
        page_size (int):
            Optional. The maximum number of
            ReasoningEngineRuntimeRevisions to return. The
            service may return fewer than this value.

            If unspecified, at most 50 revisions will be
            returned.

            The maximum value is 100; values above 100 will
            be coerced to 100.
        page_token (str):
            Optional. The standard list page token.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=2,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=3,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=4,
    )


class ListReasoningEngineRuntimeRevisionsResponse(proto.Message):
    r"""Response message for
    [ReasoningEngineRuntimeRevisionService.ListReasoningEngineRuntimeRevisions][google.cloud.aiplatform.v1beta1.ReasoningEngineRuntimeRevisionService.ListReasoningEngineRuntimeRevisions]

    Attributes:
        reasoning_engine_runtime_revisions (MutableSequence[google.cloud.aiplatform_v1beta1.types.ReasoningEngineRuntimeRevision]):
            List of ReasoningEngineRuntimeRevisions in
            the requested page.
        next_page_token (str):
            A token to retrieve the next page of results. Pass to
            [ListReasoningEngineRuntimeRevisionsRequest.page_token][google.cloud.aiplatform.v1beta1.ListReasoningEngineRuntimeRevisionsRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    reasoning_engine_runtime_revisions: MutableSequence[
        reasoning_engine_runtime_revision.ReasoningEngineRuntimeRevision
    ] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=reasoning_engine_runtime_revision.ReasoningEngineRuntimeRevision,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteReasoningEngineRuntimeRevisionRequest(proto.Message):
    r"""Request message for
    [ReasoningEngineRuntimeRevisionService.DeleteReasoningEngineRuntimeRevision][google.cloud.aiplatform.v1beta1.ReasoningEngineRuntimeRevisionService.DeleteReasoningEngineRuntimeRevision].

    Attributes:
        name (str):
            Required. The name of the ReasoningEngineRuntimeRevision
            resource to be deleted. Format:
            ``projects/{project}/locations/{location}/reasoningEngines/{reasoning_engine}/runtimeRevisions/{runtime_revision}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
