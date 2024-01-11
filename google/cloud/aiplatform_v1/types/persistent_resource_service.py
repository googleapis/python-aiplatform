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

from __future__ import annotations

from typing import Sequence

from google.cloud.aiplatform_v1.types import operation as gca_operation
from google.cloud.aiplatform_v1.types import persistent_resource as gca_persistent_resource
import proto  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "CreatePersistentResourceRequest",
        "CreatePersistentResourceOperationMetadata",
        "GetPersistentResourceRequest",
        "ListPersistentResourceRequest",
        "ListPersistentResourceResponse",
        "DeletePersistentResourceRequest",
    }
)


class CreatePersistentResourceRequest(proto.Message):
    r"""Request message for [PersistentResourceService.CreatePersistentResource][google.cloud.aiplatform.v1.PersistentResourceService.CreatePersistentResource].

    Attributes:
        parent (str):
            The resource name of the Location to create the PersistentResource
            in.nFormat: `projects/{project}/locations/{location}`
        persistent_resource (google.cloud.aiplatform_v1.types.persistent_resource):
            Required. The PersistentResource to create.
        persistent_resource_id (str):
            Required. The ID to use for the PersistentResource, which become the
            final component of the PersistentResource's resource name.

            The maximum length is 63 characters, and valid characters are
            `/^[a-z]([a-z0-9-]{0,61}[a-z0-9])?$/`.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    persistent_resource: gca_persistent_resource.PersistentResource = proto.Field(
        proto.MESSAGE,
        number=2,
        message=gca_persistent_resource.PersistentResource,
    )
    persistent_resource_id: str = proto.Field(
        proto.STRING,
        number=3,
    )


class CreatePersistentResourceOperationMetadata(proto.Message):
    r"""Details of operations that perform create PersistentResource.
    
    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.generic_metadata):
            Operation metadata for PersistentResource.
    """
    generic_metadata: gca_operation.GenericMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=gca_operation.GenericMetadata,
    )


class GetPersistentResourceRequest(proto.Message):
    r"""Request message for [PersistentResourceService.GetPersistentResource][].

    Attributes:
        name (str):
            Required. The name of the PersistentResource resource.
        Format:
        `projects/{project_id_or_number}/locations/{location_id}/persistentResources/{persistent_resource_id}`
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListPersistentResourcesRequest(proto.Message):
    r"""Request message for [PersistentResourceService.ListPersistentResource][].

    Attributes:
        parent (str):
            Required. The resource name of the Location to list the
            PersistentResources from.
            Format: `projects/{project}/locations/{location}`
        filter (str):
            An expression for filtering the results of the request.
        page_size (int):
            The standard list page size.
        page_token (str):
            The standard list page token.
            Typically obtained via
            [ListPersistentResourceResponse.next_page_token][] of the previous
            [PersistentResourceService.ListPersistentResource][] call.
        order_by (str):
            A comma-separated list of fields to order by, sorted in ascending
            order. Use "desc" after a field name for descending.
            Supported fields:

              * `display_name`
              * `create_time`
              * `update_time`

            Example: `display_name, create_time desc`.
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
        proto.INT64,
        number=3,
    )
    page_token: str = proto.Field(
        proto.STRING,
        number=4,
    )
    order_by: str = proto.Field(
        proto.STRING,
        number=6,
    )


class ListPersistentResourcesResponse(proto.Message):
    r"""Response message for [PersistentResourceService.ListPersistentResources][].
    
    Attributes:
        persistent_resources (Sequence[google.cloud.aiplatform_v1.types.PersistentResource]):
            List of PersistentResources in the requested page.
    """

    persistent_resources: Sequence[gca_persistent_resource.PersistentResource] = (
        proto.RepeatedField(
            proto.MESSAGE,
            number=1,
            message=gca_persistent_resource.PersistentResource,
        )
    )


class DeletePersistentResourceRequest(proto.Message):
    r"""Request message for [PersistentResourceService.DeletePersistentResource][].

    Attributes:
        name (str):
            Required. The name of the PersistentResource to be deleted.
            Format:
            `projects/{project}/locations/{location}/persistentResources/{persistent_resource}`
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )

__all__ = tuple(sorted(__protobuf__.manifest))
