# -*- coding: utf-8 -*-
# Copyright 2020 Google LLC
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

from google.cloud.aiplatform_v1.types import artifact
from google.cloud.aiplatform_v1.types import context
from google.cloud.aiplatform_v1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1.types import execution as gca_execution
from google.cloud.aiplatform_v1.types import pipeline_state
from google.cloud.aiplatform_v1.types import value as gca_value
from google.protobuf import struct_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1",
    manifest={
        "PipelineJob",
        "PipelineJobDetail",
        "PipelineTaskDetail",
        "PipelineTaskExecutorDetail",
    },
)


class PipelineJob(proto.Message):
    r"""An instance of a machine learning PipelineJob.
    Attributes:
        name (str):
            Output only. The resource name of the
            PipelineJob.
        display_name (str):
            The display name of the Pipeline.
            The name can be up to 128 characters long and
            can be consist of any UTF-8 characters.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Pipeline creation time.
        start_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Pipeline start time.
        end_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Pipeline end time.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Timestamp when this PipelineJob
            was most recently updated.
        pipeline_spec (google.protobuf.struct_pb2.Struct):
            Required. The spec of the pipeline.
        state (google.cloud.aiplatform_v1.types.PipelineState):
            Output only. The detailed state of the job.
        job_detail (google.cloud.aiplatform_v1.types.PipelineJobDetail):
            Output only. The details of pipeline run. Not
            available in the list view.
        error (google.rpc.status_pb2.Status):
            Output only. The error that occurred during
            pipeline execution. Only populated when the
            pipeline's state is FAILED or CANCELLED.
        labels (Sequence[google.cloud.aiplatform_v1.types.PipelineJob.LabelsEntry]):
            The labels with user-defined metadata to
            organize PipelineJob.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        runtime_config (google.cloud.aiplatform_v1.types.PipelineJob.RuntimeConfig):
            Runtime config of the pipeline.
        encryption_spec (google.cloud.aiplatform_v1.types.EncryptionSpec):
            Customer-managed encryption key spec for a
            pipelineJob. If set, this PipelineJob and all of
            its sub-resources will be secured by this key.
        service_account (str):
            The service account that the pipeline workload runs as. If
            not specified, the Compute Engine default service account in
            the project will be used. See
            https://cloud.google.com/compute/docs/access/service-accounts#default_service_account

            Users starting the pipeline must have the
            ``iam.serviceAccounts.actAs`` permission on this service
            account.
        network (str):
            The full name of the Compute Engine
            `network </compute/docs/networks-and-firewalls#networks>`__
            to which the Pipeline Job's workload should be peered. For
            example, ``projects/12345/global/networks/myVPC``.
            `Format </compute/docs/reference/rest/v1/networks/insert>`__
            is of the form
            ``projects/{project}/global/networks/{network}``. Where
            {project} is a project number, as in ``12345``, and
            {network} is a network name.

            Private services access must already be configured for the
            network. Pipeline job will apply the network configuration
            to the GCP resources being launched, if applied, such as
            Vertex AI Training or Dataflow job. If left unspecified, the
            workload is not peered with any network.
    """

    class RuntimeConfig(proto.Message):
        r"""The runtime config of a PipelineJob.
        Attributes:
            parameters (Sequence[google.cloud.aiplatform_v1.types.PipelineJob.RuntimeConfig.ParametersEntry]):
                The runtime parameters of the PipelineJob. The parameters
                will be passed into
                [PipelineJob.pipeline_spec][google.cloud.aiplatform.v1.PipelineJob.pipeline_spec]
                to replace the placeholders at runtime.
            gcs_output_directory (str):
                Required. A path in a Cloud Storage bucket, which will be
                treated as the root output directory of the pipeline. It is
                used by the system to generate the paths of output
                artifacts. The artifact paths are generated with a sub-path
                pattern ``{job_id}/{task_id}/{output_key}`` under the
                specified output directory. The service account specified in
                this pipeline must have the ``storage.objects.get`` and
                ``storage.objects.create`` permissions for this bucket.
        """

        parameters = proto.MapField(
            proto.STRING, proto.MESSAGE, number=1, message=gca_value.Value,
        )
        gcs_output_directory = proto.Field(proto.STRING, number=2,)

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    create_time = proto.Field(proto.MESSAGE, number=3, message=timestamp_pb2.Timestamp,)
    start_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    end_time = proto.Field(proto.MESSAGE, number=5, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=6, message=timestamp_pb2.Timestamp,)
    pipeline_spec = proto.Field(proto.MESSAGE, number=7, message=struct_pb2.Struct,)
    state = proto.Field(proto.ENUM, number=8, enum=pipeline_state.PipelineState,)
    job_detail = proto.Field(proto.MESSAGE, number=9, message="PipelineJobDetail",)
    error = proto.Field(proto.MESSAGE, number=10, message=status_pb2.Status,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=11,)
    runtime_config = proto.Field(proto.MESSAGE, number=12, message=RuntimeConfig,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=16, message=gca_encryption_spec.EncryptionSpec,
    )
    service_account = proto.Field(proto.STRING, number=17,)
    network = proto.Field(proto.STRING, number=18,)


class PipelineJobDetail(proto.Message):
    r"""The runtime detail of PipelineJob.
    Attributes:
        pipeline_context (google.cloud.aiplatform_v1.types.Context):
            Output only. The context of the pipeline.
        pipeline_run_context (google.cloud.aiplatform_v1.types.Context):
            Output only. The context of the current
            pipeline run.
        task_details (Sequence[google.cloud.aiplatform_v1.types.PipelineTaskDetail]):
            Output only. The runtime details of the tasks
            under the pipeline.
    """

    pipeline_context = proto.Field(proto.MESSAGE, number=1, message=context.Context,)
    pipeline_run_context = proto.Field(
        proto.MESSAGE, number=2, message=context.Context,
    )
    task_details = proto.RepeatedField(
        proto.MESSAGE, number=3, message="PipelineTaskDetail",
    )


class PipelineTaskDetail(proto.Message):
    r"""The runtime detail of a task execution.
    Attributes:
        task_id (int):
            Output only. The system generated ID of the
            task.
        parent_task_id (int):
            Output only. The id of the parent task if the
            task is within a component scope. Empty if the
            task is at the root level.
        task_name (str):
            Output only. The user specified name of the task that is
            defined in [PipelineJob.spec][].
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Task create time.
        start_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Task start time.
        end_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Task end time.
        executor_detail (google.cloud.aiplatform_v1.types.PipelineTaskExecutorDetail):
            Output only. The detailed execution info.
        state (google.cloud.aiplatform_v1.types.PipelineTaskDetail.State):
            Output only. State of the task.
        execution (google.cloud.aiplatform_v1.types.Execution):
            Output only. The execution metadata of the
            task.
        error (google.rpc.status_pb2.Status):
            Output only. The error that occurred during
            task execution. Only populated when the task's
            state is FAILED or CANCELLED.
        inputs (Sequence[google.cloud.aiplatform_v1.types.PipelineTaskDetail.InputsEntry]):
            Output only. The runtime input artifacts of
            the task.
        outputs (Sequence[google.cloud.aiplatform_v1.types.PipelineTaskDetail.OutputsEntry]):
            Output only. The runtime output artifacts of
            the task.
    """

    class State(proto.Enum):
        r"""Specifies state of TaskExecution"""
        STATE_UNSPECIFIED = 0
        PENDING = 1
        RUNNING = 2
        SUCCEEDED = 3
        CANCEL_PENDING = 4
        CANCELLING = 5
        CANCELLED = 6
        FAILED = 7
        SKIPPED = 8
        NOT_TRIGGERED = 9

    class ArtifactList(proto.Message):
        r"""A list of artifact metadata.
        Attributes:
            artifacts (Sequence[google.cloud.aiplatform_v1.types.Artifact]):
                Output only. A list of artifact metadata.
        """

        artifacts = proto.RepeatedField(
            proto.MESSAGE, number=1, message=artifact.Artifact,
        )

    task_id = proto.Field(proto.INT64, number=1,)
    parent_task_id = proto.Field(proto.INT64, number=12,)
    task_name = proto.Field(proto.STRING, number=2,)
    create_time = proto.Field(proto.MESSAGE, number=3, message=timestamp_pb2.Timestamp,)
    start_time = proto.Field(proto.MESSAGE, number=4, message=timestamp_pb2.Timestamp,)
    end_time = proto.Field(proto.MESSAGE, number=5, message=timestamp_pb2.Timestamp,)
    executor_detail = proto.Field(
        proto.MESSAGE, number=6, message="PipelineTaskExecutorDetail",
    )
    state = proto.Field(proto.ENUM, number=7, enum=State,)
    execution = proto.Field(proto.MESSAGE, number=8, message=gca_execution.Execution,)
    error = proto.Field(proto.MESSAGE, number=9, message=status_pb2.Status,)
    inputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=10, message=ArtifactList,
    )
    outputs = proto.MapField(
        proto.STRING, proto.MESSAGE, number=11, message=ArtifactList,
    )


class PipelineTaskExecutorDetail(proto.Message):
    r"""The runtime detail of a pipeline executor.
    Attributes:
        container_detail (google.cloud.aiplatform_v1.types.PipelineTaskExecutorDetail.ContainerDetail):
            Output only. The detailed info for a
            container executor.
        custom_job_detail (google.cloud.aiplatform_v1.types.PipelineTaskExecutorDetail.CustomJobDetail):
            Output only. The detailed info for a custom
            job executor.
    """

    class ContainerDetail(proto.Message):
        r"""The detail of a container execution. It contains the job
        names of the lifecycle of a container execution.

        Attributes:
            main_job (str):
                Output only. The name of the
                [CustomJob][google.cloud.aiplatform.v1.CustomJob] for the
                main container execution.
            pre_caching_check_job (str):
                Output only. The name of the
                [CustomJob][google.cloud.aiplatform.v1.CustomJob] for the
                pre-caching-check container execution. This job will be
                available if the
                [PipelineJob.pipeline_spec][google.cloud.aiplatform.v1.PipelineJob.pipeline_spec]
                specifies the ``pre_caching_check`` hook in the lifecycle
                events.
        """

        main_job = proto.Field(proto.STRING, number=1,)
        pre_caching_check_job = proto.Field(proto.STRING, number=2,)

    class CustomJobDetail(proto.Message):
        r"""The detailed info for a custom job executor.
        Attributes:
            job (str):
                Output only. The name of the
                [CustomJob][google.cloud.aiplatform.v1.CustomJob].
        """

        job = proto.Field(proto.STRING, number=1,)

    container_detail = proto.Field(
        proto.MESSAGE, number=1, oneof="details", message=ContainerDetail,
    )
    custom_job_detail = proto.Field(
        proto.MESSAGE, number=2, oneof="details", message=CustomJobDetail,
    )


__all__ = tuple(sorted(__protobuf__.manifest))
