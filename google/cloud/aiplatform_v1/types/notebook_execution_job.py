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

from google.cloud.aiplatform_v1.types import job_state as gca_job_state
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "NotebookExecutionJob",
    },
)


class NotebookExecutionJob(proto.Message):
    r"""NotebookExecutionJob represents an instance of a notebook
    execution.

    This message has `oneof`_ fields (mutually exclusive fields).
    For each oneof, at most one member field can be set at the same time.
    Setting any member of the oneof automatically clears all other
    members.

    .. _oneof: https://proto-plus-python.readthedocs.io/en/stable/fields.html#oneofs-mutually-exclusive-fields

    Attributes:
        dataform_repository_source (google.cloud.aiplatform_v1.types.NotebookExecutionJob.DataformRepositorySource):
            The Dataform Repository pointing to a single
            file notebook repository.

            This field is a member of `oneof`_ ``notebook_source``.
        gcs_notebook_source (google.cloud.aiplatform_v1.types.NotebookExecutionJob.GcsNotebookSource):
            The Cloud Storage url pointing to the ipynb file. Format:
            ``gs://bucket/notebook_file.ipynb``

            This field is a member of `oneof`_ ``notebook_source``.
        direct_notebook_source (google.cloud.aiplatform_v1.types.NotebookExecutionJob.DirectNotebookSource):
            The contents of an input notebook file.

            This field is a member of `oneof`_ ``notebook_source``.
        notebook_runtime_template_resource_name (str):
            The NotebookRuntimeTemplate to source compute
            configuration from.

            This field is a member of `oneof`_ ``environment_spec``.
        gcs_output_uri (str):
            The Cloud Storage location to upload the result to. Format:
            ``gs://bucket-name``

            This field is a member of `oneof`_ ``execution_sink``.
        execution_user (str):
            The user email to run the execution as. Only
            supported by Colab runtimes.

            This field is a member of `oneof`_ ``execution_identity``.
        service_account (str):
            The service account to run the execution as.

            This field is a member of `oneof`_ ``execution_identity``.
        name (str):
            Output only. The resource name of this NotebookExecutionJob.
            Format:
            ``projects/{project_id}/locations/{location}/notebookExecutionJobs/{job_id}``
        display_name (str):
            The display name of the NotebookExecutionJob.
            The name can be up to 128 characters long and
            can consist of any UTF-8 characters.
        execution_timeout (google.protobuf.duration_pb2.Duration):
            Max running time of the execution job in
            seconds (default 86400s / 24 hrs).
        schedule_resource_name (str):
            Output only. The Schedule resource name if this job is
            triggered by one. Format:
            ``projects/{project_id}/locations/{location}/schedules/{schedule_id}``
        job_state (google.cloud.aiplatform_v1.types.JobState):
            Output only. The state of the
            NotebookExecutionJob.
        status (google.rpc.status_pb2.Status):
            Output only. Populated when the
            NotebookExecutionJob is completed. When there is
            an error during notebook execution, the error
            details are populated.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            NotebookExecutionJob was created.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this
            NotebookExecutionJob was most recently updated.
        labels (MutableMapping[str, str]):
            The labels with user-defined metadata to
            organize NotebookExecutionJobs.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.

            See https://goo.gl/xmQnxf for more information
            and examples of labels. System reserved label
            keys are prefixed with
            "aiplatform.googleapis.com/" and are immutable.
    """

    class DataformRepositorySource(proto.Message):
        r"""The Dataform Repository containing the input notebook.

        Attributes:
            dataform_repository_resource_name (str):
                The resource name of the Dataform Repository. Format:
                ``projects/{project_id}/locations/{location}/repositories/{repository_id}``
            commit_sha (str):
                The commit SHA to read repository with. If
                unset, the file will be read at HEAD.
        """

        dataform_repository_resource_name: str = proto.Field(
            proto.STRING,
            number=1,
        )
        commit_sha: str = proto.Field(
            proto.STRING,
            number=2,
        )

    class GcsNotebookSource(proto.Message):
        r"""The Cloud Storage uri for the input notebook.

        Attributes:
            uri (str):
                The Cloud Storage uri pointing to the ipynb file. Format:
                ``gs://bucket/notebook_file.ipynb``
            generation (str):
                The version of the Cloud Storage object to
                read. If unset, the current version of the
                object is read. See
                https://cloud.google.com/storage/docs/metadata#generation-number.
        """

        uri: str = proto.Field(
            proto.STRING,
            number=1,
        )
        generation: str = proto.Field(
            proto.STRING,
            number=2,
        )

    class DirectNotebookSource(proto.Message):
        r"""The content of the input notebook in ipynb format.

        Attributes:
            content (bytes):
                The base64-encoded contents of the input
                notebook file.
        """

        content: bytes = proto.Field(
            proto.BYTES,
            number=1,
        )

    dataform_repository_source: DataformRepositorySource = proto.Field(
        proto.MESSAGE,
        number=3,
        oneof="notebook_source",
        message=DataformRepositorySource,
    )
    gcs_notebook_source: GcsNotebookSource = proto.Field(
        proto.MESSAGE,
        number=4,
        oneof="notebook_source",
        message=GcsNotebookSource,
    )
    direct_notebook_source: DirectNotebookSource = proto.Field(
        proto.MESSAGE,
        number=17,
        oneof="notebook_source",
        message=DirectNotebookSource,
    )
    notebook_runtime_template_resource_name: str = proto.Field(
        proto.STRING,
        number=14,
        oneof="environment_spec",
    )
    gcs_output_uri: str = proto.Field(
        proto.STRING,
        number=8,
        oneof="execution_sink",
    )
    execution_user: str = proto.Field(
        proto.STRING,
        number=9,
        oneof="execution_identity",
    )
    service_account: str = proto.Field(
        proto.STRING,
        number=18,
        oneof="execution_identity",
    )
    name: str = proto.Field(
        proto.STRING,
        number=1,
    )
    display_name: str = proto.Field(
        proto.STRING,
        number=2,
    )
    execution_timeout: duration_pb2.Duration = proto.Field(
        proto.MESSAGE,
        number=5,
        message=duration_pb2.Duration,
    )
    schedule_resource_name: str = proto.Field(
        proto.STRING,
        number=6,
    )
    job_state: gca_job_state.JobState = proto.Field(
        proto.ENUM,
        number=10,
        enum=gca_job_state.JobState,
    )
    status: status_pb2.Status = proto.Field(
        proto.MESSAGE,
        number=11,
        message=status_pb2.Status,
    )
    create_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=12,
        message=timestamp_pb2.Timestamp,
    )
    update_time: timestamp_pb2.Timestamp = proto.Field(
        proto.MESSAGE,
        number=13,
        message=timestamp_pb2.Timestamp,
    )
    labels: MutableMapping[str, str] = proto.MapField(
        proto.STRING,
        proto.STRING,
        number=19,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
