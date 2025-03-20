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

from google.cloud.aiplatform_v1.types import (
    notebook_execution_job as gca_notebook_execution_job,
)
from google.cloud.aiplatform_v1.types import notebook_runtime as gca_notebook_runtime
from google.cloud.aiplatform_v1.types import operation
from google.protobuf import field_mask_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "NotebookExecutionJobView",
        "CreateNotebookRuntimeTemplateRequest",
        "CreateNotebookRuntimeTemplateOperationMetadata",
        "GetNotebookRuntimeTemplateRequest",
        "ListNotebookRuntimeTemplatesRequest",
        "ListNotebookRuntimeTemplatesResponse",
        "DeleteNotebookRuntimeTemplateRequest",
        "UpdateNotebookRuntimeTemplateRequest",
        "AssignNotebookRuntimeRequest",
        "AssignNotebookRuntimeOperationMetadata",
        "GetNotebookRuntimeRequest",
        "ListNotebookRuntimesRequest",
        "ListNotebookRuntimesResponse",
        "DeleteNotebookRuntimeRequest",
        "UpgradeNotebookRuntimeRequest",
        "UpgradeNotebookRuntimeOperationMetadata",
        "UpgradeNotebookRuntimeResponse",
        "StartNotebookRuntimeRequest",
        "StartNotebookRuntimeOperationMetadata",
        "StartNotebookRuntimeResponse",
        "StopNotebookRuntimeRequest",
        "StopNotebookRuntimeOperationMetadata",
        "StopNotebookRuntimeResponse",
        "CreateNotebookExecutionJobRequest",
        "CreateNotebookExecutionJobOperationMetadata",
        "GetNotebookExecutionJobRequest",
        "ListNotebookExecutionJobsRequest",
        "ListNotebookExecutionJobsResponse",
        "DeleteNotebookExecutionJobRequest",
    },
)


class NotebookExecutionJobView(proto.Enum):
    r"""Views for Get/List NotebookExecutionJob

    Values:
        NOTEBOOK_EXECUTION_JOB_VIEW_UNSPECIFIED (0):
            When unspecified, the API defaults to the
            BASIC view.
        NOTEBOOK_EXECUTION_JOB_VIEW_BASIC (1):
            Includes all fields except for direct
            notebook inputs.
        NOTEBOOK_EXECUTION_JOB_VIEW_FULL (2):
            Includes all fields.
    """
    NOTEBOOK_EXECUTION_JOB_VIEW_UNSPECIFIED = 0
    NOTEBOOK_EXECUTION_JOB_VIEW_BASIC = 1
    NOTEBOOK_EXECUTION_JOB_VIEW_FULL = 2


class CreateNotebookRuntimeTemplateRequest(proto.Message):
    r"""Request message for
    [NotebookService.CreateNotebookRuntimeTemplate][google.cloud.aiplatform.v1.NotebookService.CreateNotebookRuntimeTemplate].

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            NotebookRuntimeTemplate. Format:
            ``projects/{project}/locations/{location}``
        notebook_runtime_template (google.cloud.aiplatform_v1.types.NotebookRuntimeTemplate):
            Required. The NotebookRuntimeTemplate to
            create.
        notebook_runtime_template_id (str):
            Optional. User specified ID for the notebook
            runtime template.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    notebook_runtime_template: gca_notebook_runtime.NotebookRuntimeTemplate = (
        proto.Field(
            proto.MESSAGE,
            number=2,
            message=gca_notebook_runtime.NotebookRuntimeTemplate,
        )
    )
    notebook_runtime_template_id: str = proto.Field(
        proto.STRING,
        number=3,
    )


class CreateNotebookRuntimeTemplateOperationMetadata(proto.Message):
    r"""Metadata information for
    [NotebookService.CreateNotebookRuntimeTemplate][google.cloud.aiplatform.v1.NotebookService.CreateNotebookRuntimeTemplate].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class GetNotebookRuntimeTemplateRequest(proto.Message):
    r"""Request message for
    [NotebookService.GetNotebookRuntimeTemplate][google.cloud.aiplatform.v1.NotebookService.GetNotebookRuntimeTemplate]

    Attributes:
        name (str):
            Required. The name of the NotebookRuntimeTemplate resource.
            Format:
            ``projects/{project}/locations/{location}/notebookRuntimeTemplates/{notebook_runtime_template}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListNotebookRuntimeTemplatesRequest(proto.Message):
    r"""Request message for
    [NotebookService.ListNotebookRuntimeTemplates][google.cloud.aiplatform.v1.NotebookService.ListNotebookRuntimeTemplates].

    Attributes:
        parent (str):
            Required. The resource name of the Location from which to
            list the NotebookRuntimeTemplates. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            Optional. An expression for filtering the results of the
            request. For field names both snake_case and camelCase are
            supported.

            -  ``notebookRuntimeTemplate`` supports = and !=.
               ``notebookRuntimeTemplate`` represents the
               NotebookRuntimeTemplate ID, i.e. the last segment of the
               NotebookRuntimeTemplate's [resource name]
               [google.cloud.aiplatform.v1.NotebookRuntimeTemplate.name].
            -  ``display_name`` supports = and !=
            -  ``labels`` supports general map functions that is:

               -  ``labels.key=value`` - key:value equality
               -  \`labels.key:\* or labels:key - key existence
               -  A key including a space must be quoted.
                  ``labels."a key"``.

            -  ``notebookRuntimeType`` supports = and !=.
               notebookRuntimeType enum: [USER_DEFINED, ONE_CLICK].
            -  ``machineType`` supports = and !=.
            -  ``acceleratorType`` supports = and !=.

            Some examples:

            -  ``notebookRuntimeTemplate=notebookRuntimeTemplate123``
            -  ``displayName="myDisplayName"``
            -  ``labels.myKey="myValue"``
            -  ``notebookRuntimeType=USER_DEFINED``
            -  ``machineType=e2-standard-4``
            -  ``acceleratorType=NVIDIA_TESLA_T4``
        page_size (int):
            Optional. The standard list page size.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListNotebookRuntimeTemplatesResponse.next_page_token][google.cloud.aiplatform.v1.ListNotebookRuntimeTemplatesResponse.next_page_token]
            of the previous
            [NotebookService.ListNotebookRuntimeTemplates][google.cloud.aiplatform.v1.NotebookService.ListNotebookRuntimeTemplates]
            call.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Optional. Mask specifying which fields to
            read.
        order_by (str):
            Optional. A comma-separated list of fields to order by,
            sorted in ascending order. Use "desc" after a field name for
            descending. Supported fields:

            -  ``display_name``
            -  ``create_time``
            -  ``update_time``

            Example: ``display_name, create_time desc``.
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
    read_mask: field_mask_pb2.FieldMask = proto.Field(
        proto.MESSAGE,
        number=5,
        message=field_mask_pb2.FieldMask,
    )
    order_by: str = proto.Field(
        proto.STRING,
        number=6,
    )


class ListNotebookRuntimeTemplatesResponse(proto.Message):
    r"""Response message for
    [NotebookService.ListNotebookRuntimeTemplates][google.cloud.aiplatform.v1.NotebookService.ListNotebookRuntimeTemplates].

    Attributes:
        notebook_runtime_templates (MutableSequence[google.cloud.aiplatform_v1.types.NotebookRuntimeTemplate]):
            List of NotebookRuntimeTemplates in the
            requested page.
        next_page_token (str):
            A token to retrieve next page of results. Pass to
            [ListNotebookRuntimeTemplatesRequest.page_token][google.cloud.aiplatform.v1.ListNotebookRuntimeTemplatesRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    notebook_runtime_templates: MutableSequence[
        gca_notebook_runtime.NotebookRuntimeTemplate
    ] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=gca_notebook_runtime.NotebookRuntimeTemplate,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteNotebookRuntimeTemplateRequest(proto.Message):
    r"""Request message for
    [NotebookService.DeleteNotebookRuntimeTemplate][google.cloud.aiplatform.v1.NotebookService.DeleteNotebookRuntimeTemplate].

    Attributes:
        name (str):
            Required. The name of the NotebookRuntimeTemplate resource
            to be deleted. Format:
            ``projects/{project}/locations/{location}/notebookRuntimeTemplates/{notebook_runtime_template}``
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class UpdateNotebookRuntimeTemplateRequest(proto.Message):
    r"""Request message for
    [NotebookService.UpdateNotebookRuntimeTemplate][google.cloud.aiplatform.v1.NotebookService.UpdateNotebookRuntimeTemplate].

    Attributes:
        notebook_runtime_template (google.cloud.aiplatform_v1.types.NotebookRuntimeTemplate):
            Required. The NotebookRuntimeTemplate to
            update.
        update_mask (google.protobuf.field_mask_pb2.FieldMask):
            Required. The update mask applies to the resource. For the
            ``FieldMask`` definition, see
            [google.protobuf.FieldMask][google.protobuf.FieldMask].
            Input format: ``{paths: "${updated_filed}"}`` Updatable
            fields:

            -  ``encryption_spec.kms_key_name``
    """

    notebook_runtime_template: gca_notebook_runtime.NotebookRuntimeTemplate = (
        proto.Field(
            proto.MESSAGE,
            number=1,
            message=gca_notebook_runtime.NotebookRuntimeTemplate,
        )
    )
    update_mask: field_mask_pb2.FieldMask = proto.Field(
        proto.MESSAGE,
        number=2,
        message=field_mask_pb2.FieldMask,
    )


class AssignNotebookRuntimeRequest(proto.Message):
    r"""Request message for
    [NotebookService.AssignNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.AssignNotebookRuntime].

    Attributes:
        parent (str):
            Required. The resource name of the Location to get the
            NotebookRuntime assignment. Format:
            ``projects/{project}/locations/{location}``
        notebook_runtime_template (str):
            Required. The resource name of the
            NotebookRuntimeTemplate based on which a
            NotebookRuntime will be assigned (reuse or
            create a new one).
        notebook_runtime (google.cloud.aiplatform_v1.types.NotebookRuntime):
            Required. Provide runtime specific
            information (e.g. runtime owner, notebook id)
            used for NotebookRuntime assignment.
        notebook_runtime_id (str):
            Optional. User specified ID for the notebook
            runtime.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    notebook_runtime_template: str = proto.Field(
        proto.STRING,
        number=2,
    )
    notebook_runtime: gca_notebook_runtime.NotebookRuntime = proto.Field(
        proto.MESSAGE,
        number=3,
        message=gca_notebook_runtime.NotebookRuntime,
    )
    notebook_runtime_id: str = proto.Field(
        proto.STRING,
        number=4,
    )


class AssignNotebookRuntimeOperationMetadata(proto.Message):
    r"""Metadata information for
    [NotebookService.AssignNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.AssignNotebookRuntime].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        progress_message (str):
            A human-readable message that shows the
            intermediate progress details of
            NotebookRuntime.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    progress_message: str = proto.Field(
        proto.STRING,
        number=2,
    )


class GetNotebookRuntimeRequest(proto.Message):
    r"""Request message for
    [NotebookService.GetNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.GetNotebookRuntime]

    Attributes:
        name (str):
            Required. The name of the NotebookRuntime
            resource. Instead of checking whether the name
            is in valid NotebookRuntime resource name
            format, directly throw NotFound exception if
            there is no such NotebookRuntime in spanner.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class ListNotebookRuntimesRequest(proto.Message):
    r"""Request message for
    [NotebookService.ListNotebookRuntimes][google.cloud.aiplatform.v1.NotebookService.ListNotebookRuntimes].

    Attributes:
        parent (str):
            Required. The resource name of the Location from which to
            list the NotebookRuntimes. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            Optional. An expression for filtering the results of the
            request. For field names both snake_case and camelCase are
            supported.

            -  ``notebookRuntime`` supports = and !=.
               ``notebookRuntime`` represents the NotebookRuntime ID,
               i.e. the last segment of the NotebookRuntime's [resource
               name] [google.cloud.aiplatform.v1.NotebookRuntime.name].
            -  ``displayName`` supports = and != and regex.
            -  ``notebookRuntimeTemplate`` supports = and !=.
               ``notebookRuntimeTemplate`` represents the
               NotebookRuntimeTemplate ID, i.e. the last segment of the
               NotebookRuntimeTemplate's [resource name]
               [google.cloud.aiplatform.v1.NotebookRuntimeTemplate.name].
            -  ``healthState`` supports = and !=. healthState enum:
               [HEALTHY, UNHEALTHY, HEALTH_STATE_UNSPECIFIED].
            -  ``runtimeState`` supports = and !=. runtimeState enum:
               [RUNTIME_STATE_UNSPECIFIED, RUNNING, BEING_STARTED,
               BEING_STOPPED, STOPPED, BEING_UPGRADED, ERROR, INVALID].
            -  ``runtimeUser`` supports = and !=.
            -  API version is UI only: ``uiState`` supports = and !=.
               uiState enum: [UI_RESOURCE_STATE_UNSPECIFIED,
               UI_RESOURCE_STATE_BEING_CREATED,
               UI_RESOURCE_STATE_ACTIVE,
               UI_RESOURCE_STATE_BEING_DELETED,
               UI_RESOURCE_STATE_CREATION_FAILED].
            -  ``notebookRuntimeType`` supports = and !=.
               notebookRuntimeType enum: [USER_DEFINED, ONE_CLICK].
            -  ``machineType`` supports = and !=.
            -  ``acceleratorType`` supports = and !=.

            Some examples:

            -  ``notebookRuntime="notebookRuntime123"``
            -  ``displayName="myDisplayName"`` and
               ``displayName=~"myDisplayNameRegex"``
            -  ``notebookRuntimeTemplate="notebookRuntimeTemplate321"``
            -  ``healthState=HEALTHY``
            -  ``runtimeState=RUNNING``
            -  ``runtimeUser="test@google.com"``
            -  ``uiState=UI_RESOURCE_STATE_BEING_DELETED``
            -  ``notebookRuntimeType=USER_DEFINED``
            -  ``machineType=e2-standard-4``
            -  ``acceleratorType=NVIDIA_TESLA_T4``
        page_size (int):
            Optional. The standard list page size.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListNotebookRuntimesResponse.next_page_token][google.cloud.aiplatform.v1.ListNotebookRuntimesResponse.next_page_token]
            of the previous
            [NotebookService.ListNotebookRuntimes][google.cloud.aiplatform.v1.NotebookService.ListNotebookRuntimes]
            call.
        read_mask (google.protobuf.field_mask_pb2.FieldMask):
            Optional. Mask specifying which fields to
            read.
        order_by (str):
            Optional. A comma-separated list of fields to order by,
            sorted in ascending order. Use "desc" after a field name for
            descending. Supported fields:

            -  ``display_name``
            -  ``create_time``
            -  ``update_time``

            Example: ``display_name, create_time desc``.
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
    read_mask: field_mask_pb2.FieldMask = proto.Field(
        proto.MESSAGE,
        number=5,
        message=field_mask_pb2.FieldMask,
    )
    order_by: str = proto.Field(
        proto.STRING,
        number=6,
    )


class ListNotebookRuntimesResponse(proto.Message):
    r"""Response message for
    [NotebookService.ListNotebookRuntimes][google.cloud.aiplatform.v1.NotebookService.ListNotebookRuntimes].

    Attributes:
        notebook_runtimes (MutableSequence[google.cloud.aiplatform_v1.types.NotebookRuntime]):
            List of NotebookRuntimes in the requested
            page.
        next_page_token (str):
            A token to retrieve next page of results. Pass to
            [ListNotebookRuntimesRequest.page_token][google.cloud.aiplatform.v1.ListNotebookRuntimesRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    notebook_runtimes: MutableSequence[
        gca_notebook_runtime.NotebookRuntime
    ] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=gca_notebook_runtime.NotebookRuntime,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteNotebookRuntimeRequest(proto.Message):
    r"""Request message for
    [NotebookService.DeleteNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.DeleteNotebookRuntime].

    Attributes:
        name (str):
            Required. The name of the NotebookRuntime
            resource to be deleted. Instead of checking
            whether the name is in valid NotebookRuntime
            resource name format, directly throw NotFound
            exception if there is no such NotebookRuntime in
            spanner.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class UpgradeNotebookRuntimeRequest(proto.Message):
    r"""Request message for
    [NotebookService.UpgradeNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.UpgradeNotebookRuntime].

    Attributes:
        name (str):
            Required. The name of the NotebookRuntime
            resource to be upgrade. Instead of checking
            whether the name is in valid NotebookRuntime
            resource name format, directly throw NotFound
            exception if there is no such NotebookRuntime in
            spanner.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class UpgradeNotebookRuntimeOperationMetadata(proto.Message):
    r"""Metadata information for
    [NotebookService.UpgradeNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.UpgradeNotebookRuntime].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        progress_message (str):
            A human-readable message that shows the
            intermediate progress details of
            NotebookRuntime.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    progress_message: str = proto.Field(
        proto.STRING,
        number=2,
    )


class UpgradeNotebookRuntimeResponse(proto.Message):
    r"""Response message for
    [NotebookService.UpgradeNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.UpgradeNotebookRuntime].

    """


class StartNotebookRuntimeRequest(proto.Message):
    r"""Request message for
    [NotebookService.StartNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.StartNotebookRuntime].

    Attributes:
        name (str):
            Required. The name of the NotebookRuntime
            resource to be started. Instead of checking
            whether the name is in valid NotebookRuntime
            resource name format, directly throw NotFound
            exception if there is no such NotebookRuntime in
            spanner.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class StartNotebookRuntimeOperationMetadata(proto.Message):
    r"""Metadata information for
    [NotebookService.StartNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.StartNotebookRuntime].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        progress_message (str):
            A human-readable message that shows the
            intermediate progress details of
            NotebookRuntime.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    progress_message: str = proto.Field(
        proto.STRING,
        number=2,
    )


class StartNotebookRuntimeResponse(proto.Message):
    r"""Response message for
    [NotebookService.StartNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.StartNotebookRuntime].

    """


class StopNotebookRuntimeRequest(proto.Message):
    r"""Request message for
    [NotebookService.StopNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.StopNotebookRuntime].

    Attributes:
        name (str):
            Required. The name of the NotebookRuntime
            resource to be stopped. Instead of checking
            whether the name is in valid NotebookRuntime
            resource name format, directly throw NotFound
            exception if there is no such NotebookRuntime in
            spanner.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


class StopNotebookRuntimeOperationMetadata(proto.Message):
    r"""Metadata information for
    [NotebookService.StopNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.StopNotebookRuntime].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )


class StopNotebookRuntimeResponse(proto.Message):
    r"""Response message for
    [NotebookService.StopNotebookRuntime][google.cloud.aiplatform.v1.NotebookService.StopNotebookRuntime].

    """


class CreateNotebookExecutionJobRequest(proto.Message):
    r"""Request message for [NotebookService.CreateNotebookExecutionJob]

    Attributes:
        parent (str):
            Required. The resource name of the Location to create the
            NotebookExecutionJob. Format:
            ``projects/{project}/locations/{location}``
        notebook_execution_job (google.cloud.aiplatform_v1.types.NotebookExecutionJob):
            Required. The NotebookExecutionJob to create.
        notebook_execution_job_id (str):
            Optional. User specified ID for the
            NotebookExecutionJob.
    """

    parent: str = proto.Field(
        proto.STRING,
        number=1,
    )
    notebook_execution_job: gca_notebook_execution_job.NotebookExecutionJob = (
        proto.Field(
            proto.MESSAGE,
            number=2,
            message=gca_notebook_execution_job.NotebookExecutionJob,
        )
    )
    notebook_execution_job_id: str = proto.Field(
        proto.STRING,
        number=3,
    )


class CreateNotebookExecutionJobOperationMetadata(proto.Message):
    r"""Metadata information for
    [NotebookService.CreateNotebookExecutionJob][google.cloud.aiplatform.v1.NotebookService.CreateNotebookExecutionJob].

    Attributes:
        generic_metadata (google.cloud.aiplatform_v1.types.GenericOperationMetadata):
            The operation generic information.
        progress_message (str):
            A human-readable message that shows the
            intermediate progress details of
            NotebookRuntime.
    """

    generic_metadata: operation.GenericOperationMetadata = proto.Field(
        proto.MESSAGE,
        number=1,
        message=operation.GenericOperationMetadata,
    )
    progress_message: str = proto.Field(
        proto.STRING,
        number=2,
    )


class GetNotebookExecutionJobRequest(proto.Message):
    r"""Request message for [NotebookService.GetNotebookExecutionJob]

    Attributes:
        name (str):
            Required. The name of the
            NotebookExecutionJob resource.
        view (google.cloud.aiplatform_v1.types.NotebookExecutionJobView):
            Optional. The NotebookExecutionJob view.
            Defaults to BASIC.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    view: "NotebookExecutionJobView" = proto.Field(
        proto.ENUM,
        number=6,
        enum="NotebookExecutionJobView",
    )


class ListNotebookExecutionJobsRequest(proto.Message):
    r"""Request message for [NotebookService.ListNotebookExecutionJobs]

    Attributes:
        parent (str):
            Required. The resource name of the Location from which to
            list the NotebookExecutionJobs. Format:
            ``projects/{project}/locations/{location}``
        filter (str):
            Optional. An expression for filtering the results of the
            request. For field names both snake_case and camelCase are
            supported.

            -  ``notebookExecutionJob`` supports = and !=.
               ``notebookExecutionJob`` represents the
               NotebookExecutionJob ID.
            -  ``displayName`` supports = and != and regex.
            -  ``schedule`` supports = and != and regex.

            Some examples:

            -  ``notebookExecutionJob="123"``
            -  ``notebookExecutionJob="my-execution-job"``
            -  ``displayName="myDisplayName"`` and
               ``displayName=~"myDisplayNameRegex"``
        page_size (int):
            Optional. The standard list page size.
        page_token (str):
            Optional. The standard list page token. Typically obtained
            via
            [ListNotebookExecutionJobsResponse.next_page_token][google.cloud.aiplatform.v1.ListNotebookExecutionJobsResponse.next_page_token]
            of the previous
            [NotebookService.ListNotebookExecutionJobs][google.cloud.aiplatform.v1.NotebookService.ListNotebookExecutionJobs]
            call.
        order_by (str):
            Optional. A comma-separated list of fields to order by,
            sorted in ascending order. Use "desc" after a field name for
            descending. Supported fields:

            -  ``display_name``
            -  ``create_time``
            -  ``update_time``

            Example: ``display_name, create_time desc``.
        view (google.cloud.aiplatform_v1.types.NotebookExecutionJobView):
            Optional. The NotebookExecutionJob view.
            Defaults to BASIC.
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
    order_by: str = proto.Field(
        proto.STRING,
        number=5,
    )
    view: "NotebookExecutionJobView" = proto.Field(
        proto.ENUM,
        number=6,
        enum="NotebookExecutionJobView",
    )


class ListNotebookExecutionJobsResponse(proto.Message):
    r"""Response message for [NotebookService.CreateNotebookExecutionJob]

    Attributes:
        notebook_execution_jobs (MutableSequence[google.cloud.aiplatform_v1.types.NotebookExecutionJob]):
            List of NotebookExecutionJobs in the
            requested page.
        next_page_token (str):
            A token to retrieve next page of results. Pass to
            [ListNotebookExecutionJobsRequest.page_token][google.cloud.aiplatform.v1.ListNotebookExecutionJobsRequest.page_token]
            to obtain that page.
    """

    @property
    def raw_page(self):
        return self

    notebook_execution_jobs: MutableSequence[
        gca_notebook_execution_job.NotebookExecutionJob
    ] = proto.RepeatedField(
        proto.MESSAGE,
        number=1,
        message=gca_notebook_execution_job.NotebookExecutionJob,
    )
    next_page_token: str = proto.Field(
        proto.STRING,
        number=2,
    )


class DeleteNotebookExecutionJobRequest(proto.Message):
    r"""Request message for [NotebookService.DeleteNotebookExecutionJob]

    Attributes:
        name (str):
            Required. The name of the
            NotebookExecutionJob resource to be deleted.
    """

    name: str = proto.Field(
        proto.STRING,
        number=1,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
