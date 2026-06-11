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

from google.cloud.aiplatform_v1beta1.types import (
    online_evaluator as gca_online_evaluator,
)
from google.cloud.aiplatform_v1beta1.types import operation
import google.protobuf.field_mask_pb2 as field_mask_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "CreateOnlineEvaluatorRequest",
        "CreateOnlineEvaluatorOperationMetadata",
        "GetOnlineEvaluatorRequest",
        "UpdateOnlineEvaluatorRequest",
        "UpdateOnlineEvaluatorOperationMetadata",
        "DeleteOnlineEvaluatorRequest",
        "DeleteOnlineEvaluatorOperationMetadata",
        "ListOnlineEvaluatorsRequest",
        "ListOnlineEvaluatorsResponse",
        "ActivateOnlineEvaluatorRequest",
        "ActivateOnlineEvaluatorOperationMetadata",
        "SuspendOnlineEvaluatorRequest",
        "SuspendOnlineEvaluatorOperationMetadata",
    },
)


class CreateOnlineEvaluatorRequest(proto.Message):
    r"""Request message for CreateOnlineEvaluator.

    Attributes:
        parent (str):
            Required. The parent resource where the
            OnlineEvaluator will be created. Format:
            projects/{project}/locations/{location}.
        online_evaluator (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator):
            Required. The OnlineEvaluator to create.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    online_evaluator: gca_online_evaluator.OnlineEvaluator = proto.Field(
        proto.MESSAGE,
        number=2,
        message=gca_online_evaluator.OnlineEvaluator,
    )


class CreateOnlineEvaluatorOperationMetadata(proto.Message):
    r"""Metadata for the CreateOnlineEvaluator operation.

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Common part of operation metadata.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class GetOnlineEvaluatorRequest(proto.Message):
    r"""Request message for GetOnlineEvaluator.

    Attributes:
        name (str):
            Required. The name of the OnlineEvaluator to
            retrieve. Format:
            projects/{project}/locations/{location}/onlineEvaluators/{id}.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class UpdateOnlineEvaluatorRequest(proto.Message):
    r"""Request message for UpdateOnlineEvaluator.

    Attributes:
        online_evaluator (google.cloud.aiplatform_v1beta1.types.OnlineEvaluator):
            Required. The OnlineEvaluator to update.
            Format:
            projects/{project}/locations/{location}/onlineEvaluators/{id}.
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Optional. Field mask is used to control which
            fields get updated. If the mask is not present,
            all fields will be updated.
    """

    online_evaluator: gca_online_evaluator.OnlineEvaluator = proto.Field(
        proto.MESSAGE,
        number=1,
        message=gca_online_evaluator.OnlineEvaluator,
    )
    update_mask: field_mask_pb2.FieldMask = proto.Field(
        proto.MESSAGE,
        number=2,
        message=field_mask_pb2.FieldMask,
    )


class UpdateOnlineEvaluatorOperationMetadata(proto.Message):
    r"""Metadata for the UpdateOnlineEvaluator operation.

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Generic operation metadata.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class DeleteOnlineEvaluatorRequest(proto.Message):
    r"""Request message for DeleteOnlineEvaluator.

    Attributes:
        name (str):
            Required. The name of the OnlineEvaluator to
            delete. Format:
            projects/{project}/locations/{location}/onlineEvaluators/{id}.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class DeleteOnlineEvaluatorOperationMetadata(proto.Message):
    r"""Metadata for the DeleteOnlineEvaluator operation.

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Generic operation metadata.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class ListOnlineEvaluatorsRequest(proto.Message):
    r"""Request message for ListOnlineEvaluators.

    Attributes:
        parent (str):
            Required. The parent resource of the
            OnlineEvaluators to list. Format:
            projects/{project}/locations/{location}.
        page_size (int):
            Optional. The maximum number of
            OnlineEvaluators to return. The service may
            return fewer than this value. If unspecified, at
            most 50 OnlineEvaluators will be returned. The
            maximum value is 100; values above 100 will be
            coerced to 100. Based on aip.dev/158.
        page_token (str):
            Optional. A token identifying a page of
            results the server should return. Based on
            aip.dev/158.
        filter (str):
            Optional. Standard list filter. Supported fields: \*
            ``create_time`` \* ``update_time`` \* ``agent_resource``
            Example: ``create_time>"2026-01-01T00:00:00-04:00"`` where
            the timestamp is in RFC 3339 format) Based on aip.dev/160.
        order_by (str):
            Optional. A comma-separated list of fields to order by. The
            default sorting order is ascending. Use "desc" after a field
            name for descending. Supported fields:

            - ``create_time``
            - ``update_time``

            Example: ``create_time desc``. Based on aip.dev/132.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    page_size: int = proto.Field(
        proto.INT32,
        number=2,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=3,
    )
    filter: str = proto.Field(
        proto.STRING,
        number=4,
    )
    order_by: str = proto.Field(
        proto.STRING,
        number=5,
    )


class ListOnlineEvaluatorsResponse(proto.Message):
    r"""Response message for ListOnlineEvaluators.

    Attributes:
        online_evaluators (MutableSequence[google.cloud.aiplatform_v1beta1.types.OnlineEvaluator]):
            A list of OnlineEvaluators matching the
            request.
        next_page_token (str):
            A token to retrieve the next page. Absence of
            this field indicates there are no subsequent
            pages.
    """

    @property
    def raw_page(self):
        return self

    online_evaluators: MutableSequence[gca_online_evaluator.OnlineEvaluator] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message=gca_online_evaluator.OnlineEvaluator,
        )
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class ActivateOnlineEvaluatorRequest(proto.Message):
    r"""Request message for ActivateOnlineEvaluator.

    Attributes:
        name (str):
            Required. The name of the OnlineEvaluator to
            activate. Format:
            projects/{project}/locations/{location}/onlineEvaluators/{id}.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ActivateOnlineEvaluatorOperationMetadata(proto.Message):
    r"""Metadata for the ActivateOnlineEvaluator operation.

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Common part of operation metadata.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class SuspendOnlineEvaluatorRequest(proto.Message):
    r"""Request message for SuspendOnlineEvaluator.

    Attributes:
        name (str):
            Required. The name of the OnlineEvaluator to
            suspend. Format:
            projects/{project}/locations/{location}/onlineEvaluators/{id}.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class SuspendOnlineEvaluatorOperationMetadata(proto.Message):
    r"""Metadata for the SuspendOnlineEvaluator operation.

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1beta1.types.GenericOperationMetadata):
            Common part of operation metadata.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
