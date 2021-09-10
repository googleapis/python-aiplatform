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

from google.cloud.aiplatform_v1beta1.types import encryption_spec as gca_encryption_spec
from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.protobuf import duration_pb2  # type: ignore
from google.protobuf import timestamp_pb2  # type: ignore
from google.rpc import status_pb2  # type: ignore


__protobuf__ = proto.module(
    package="google.cloud.aiplatform.v1beta1",
    manifest={
        "CustomJob",
        "CustomJobSpec",
        "WorkerPoolSpec",
        "ContainerSpec",
        "PythonPackageSpec",
        "Scheduling",
    },
)


class CustomJob(proto.Message):
    r"""Represents a job that runs custom workloads such as a Docker
    container or a Python package. A CustomJob can have multiple
    worker pools and each worker pool can have its own machine and
    input spec. A CustomJob will be cleaned up once the job enters
    terminal state (failed or succeeded).

    Attributes:
        name (str):
            Output only. Resource name of a CustomJob.
        display_name (str):
            Required. The display name of the CustomJob.
            The name can be up to 128 characters long and
            can be consist of any UTF-8 characters.
        job_spec (google.cloud.aiplatform_v1beta1.types.CustomJobSpec):
            Required. Job spec.
        state (google.cloud.aiplatform_v1beta1.types.JobState):
            Output only. The detailed state of the job.
        create_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the CustomJob was
            created.
        start_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the CustomJob for the first time
            entered the ``JOB_STATE_RUNNING`` state.
        end_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the CustomJob entered any of the
            following states: ``JOB_STATE_SUCCEEDED``,
            ``JOB_STATE_FAILED``, ``JOB_STATE_CANCELLED``.
        update_time (google.protobuf.timestamp_pb2.Timestamp):
            Output only. Time when the CustomJob was most
            recently updated.
        error (google.rpc.status_pb2.Status):
            Output only. Only populated when job's state is
            ``JOB_STATE_FAILED`` or ``JOB_STATE_CANCELLED``.
        labels (Sequence[google.cloud.aiplatform_v1beta1.types.CustomJob.LabelsEntry]):
            The labels with user-defined metadata to
            organize CustomJobs.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
        encryption_spec (google.cloud.aiplatform_v1beta1.types.EncryptionSpec):
            Customer-managed encryption key options for a
            CustomJob. If this is set, then all resources
            created by the CustomJob will be encrypted with
            the provided encryption key.
        web_access_uris (Sequence[google.cloud.aiplatform_v1beta1.types.CustomJob.WebAccessUrisEntry]):
            Output only. URIs for accessing `interactive
            shells <https://cloud.google.com/vertex-ai/docs/training/monitor-debug-interactive-shell>`__
            (one URI for each training node). Only available if
            [job_spec.enable_web_access][google.cloud.aiplatform.v1beta1.CustomJobSpec.enable_web_access]
            is ``true``.

            The keys are names of each node in the training job; for
            example, ``workerpool0-0`` for the primary node,
            ``workerpool1-0`` for the first node in the second worker
            pool, and ``workerpool1-1`` for the second node in the
            second worker pool.

            The values are the URIs for each node's interactive shell.
    """

    name = proto.Field(proto.STRING, number=1,)
    display_name = proto.Field(proto.STRING, number=2,)
    job_spec = proto.Field(proto.MESSAGE, number=4, message="CustomJobSpec",)
    state = proto.Field(proto.ENUM, number=5, enum=job_state.JobState,)
    create_time = proto.Field(proto.MESSAGE, number=6, message=timestamp_pb2.Timestamp,)
    start_time = proto.Field(proto.MESSAGE, number=7, message=timestamp_pb2.Timestamp,)
    end_time = proto.Field(proto.MESSAGE, number=8, message=timestamp_pb2.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=9, message=timestamp_pb2.Timestamp,)
    error = proto.Field(proto.MESSAGE, number=10, message=status_pb2.Status,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=11,)
    encryption_spec = proto.Field(
        proto.MESSAGE, number=12, message=gca_encryption_spec.EncryptionSpec,
    )
    web_access_uris = proto.MapField(proto.STRING, proto.STRING, number=16,)


class CustomJobSpec(proto.Message):
    r"""Represents the spec of a CustomJob.
    Attributes:
        worker_pool_specs (Sequence[google.cloud.aiplatform_v1beta1.types.WorkerPoolSpec]):
            Required. The spec of the worker pools
            including machine type and Docker image. All
            worker pools except the first one are optional
            and can be skipped by providing an empty value.
        scheduling (google.cloud.aiplatform_v1beta1.types.Scheduling):
            Scheduling options for a CustomJob.
        service_account (str):
            Specifies the service account for workload run-as account.
            Users submitting jobs must have act-as permission on this
            run-as account. If unspecified, the `Vertex AI Custom Code
            Service
            Agent <https://cloud.google.com/vertex-ai/docs/general/access-control#service-agents>`__
            for the CustomJob's project is used.
        network (str):
            The full name of the Compute Engine
            `network </compute/docs/networks-and-firewalls#networks>`__
            to which the Job should be peered. For example,
            ``projects/12345/global/networks/myVPC``.
            `Format </compute/docs/reference/rest/v1/networks/insert>`__
            is of the form
            ``projects/{project}/global/networks/{network}``. Where
            {project} is a project number, as in ``12345``, and
            {network} is a network name.

            Private services access must already be configured for the
            network. If left unspecified, the job is not peered with any
            network.
        base_output_directory (google.cloud.aiplatform_v1beta1.types.GcsDestination):
            The Cloud Storage location to store the output of this
            CustomJob or HyperparameterTuningJob. For
            HyperparameterTuningJob, the baseOutputDirectory of each
            child CustomJob backing a Trial is set to a subdirectory of
            name [id][google.cloud.aiplatform.v1beta1.Trial.id] under
            its parent HyperparameterTuningJob's baseOutputDirectory.

            The following Vertex AI environment variables will be passed
            to containers or python modules when this field is set:

            For CustomJob:

            -  AIP_MODEL_DIR = ``<base_output_directory>/model/``
            -  AIP_CHECKPOINT_DIR =
               ``<base_output_directory>/checkpoints/``
            -  AIP_TENSORBOARD_LOG_DIR =
               ``<base_output_directory>/logs/``

            For CustomJob backing a Trial of HyperparameterTuningJob:

            -  AIP_MODEL_DIR =
               ``<base_output_directory>/<trial_id>/model/``
            -  AIP_CHECKPOINT_DIR =
               ``<base_output_directory>/<trial_id>/checkpoints/``
            -  AIP_TENSORBOARD_LOG_DIR =
               ``<base_output_directory>/<trial_id>/logs/``
        tensorboard (str):
            Optional. The name of a Vertex AI
            [Tensorboard][google.cloud.aiplatform.v1beta1.Tensorboard]
            resource to which this CustomJob will upload Tensorboard
            logs. Format:
            ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``
        enable_web_access (bool):
            Optional. Whether you want Vertex AI to enable `interactive
            shell
            access <https://cloud.google.com/vertex-ai/docs/training/monitor-debug-interactive-shell>`__
            to training containers.

            If set to ``true``, you can access interactive shells at the
            URIs given by
            [CustomJob.web_access_uris][google.cloud.aiplatform.v1beta1.CustomJob.web_access_uris]
            or
            [Trial.web_access_uris][google.cloud.aiplatform.v1beta1.Trial.web_access_uris]
            (within
            [HyperparameterTuningJob.trials][google.cloud.aiplatform.v1beta1.HyperparameterTuningJob.trials]).
    """

    worker_pool_specs = proto.RepeatedField(
        proto.MESSAGE, number=1, message="WorkerPoolSpec",
    )
    scheduling = proto.Field(proto.MESSAGE, number=3, message="Scheduling",)
    service_account = proto.Field(proto.STRING, number=4,)
    network = proto.Field(proto.STRING, number=5,)
    base_output_directory = proto.Field(
        proto.MESSAGE, number=6, message=io.GcsDestination,
    )
    tensorboard = proto.Field(proto.STRING, number=7,)
    enable_web_access = proto.Field(proto.BOOL, number=10,)


class WorkerPoolSpec(proto.Message):
    r"""Represents the spec of a worker pool in a job.
    Attributes:
        container_spec (google.cloud.aiplatform_v1beta1.types.ContainerSpec):
            The custom container task.
        python_package_spec (google.cloud.aiplatform_v1beta1.types.PythonPackageSpec):
            The Python packaged task.
        machine_spec (google.cloud.aiplatform_v1beta1.types.MachineSpec):
            Optional. Immutable. The specification of a
            single machine.
        replica_count (int):
            Optional. The number of worker replicas to
            use for this worker pool.
        disk_spec (google.cloud.aiplatform_v1beta1.types.DiskSpec):
            Disk spec.
    """

    container_spec = proto.Field(
        proto.MESSAGE, number=6, oneof="task", message="ContainerSpec",
    )
    python_package_spec = proto.Field(
        proto.MESSAGE, number=7, oneof="task", message="PythonPackageSpec",
    )
    machine_spec = proto.Field(
        proto.MESSAGE, number=1, message=machine_resources.MachineSpec,
    )
    replica_count = proto.Field(proto.INT64, number=2,)
    disk_spec = proto.Field(
        proto.MESSAGE, number=5, message=machine_resources.DiskSpec,
    )


class ContainerSpec(proto.Message):
    r"""The spec of a Container.
    Attributes:
        image_uri (str):
            Required. The URI of a container image in the
            Container Registry that is to be run on each
            worker replica.
        command (Sequence[str]):
            The command to be invoked when the container
            is started. It overrides the entrypoint
            instruction in Dockerfile when provided.
        args (Sequence[str]):
            The arguments to be passed when starting the
            container.
    """

    image_uri = proto.Field(proto.STRING, number=1,)
    command = proto.RepeatedField(proto.STRING, number=2,)
    args = proto.RepeatedField(proto.STRING, number=3,)


class PythonPackageSpec(proto.Message):
    r"""The spec of a Python packaged code.
    Attributes:
        executor_image_uri (str):
            Required. The URI of a container image in Artifact Registry
            that will run the provided Python package. Vertex AI
            provides a wide range of executor images with pre-installed
            packages to meet users' various use cases. See the list of
            `pre-built containers for
            training <https://cloud.google.com/vertex-ai/docs/training/pre-built-containers>`__.
            You must use an image from this list.
        package_uris (Sequence[str]):
            Required. The Google Cloud Storage location
            of the Python package files which are the
            training program and its dependent packages. The
            maximum number of package URIs is 100.
        python_module (str):
            Required. The Python module name to run after
            installing the packages.
        args (Sequence[str]):
            Command line arguments to be passed to the
            Python task.
    """

    executor_image_uri = proto.Field(proto.STRING, number=1,)
    package_uris = proto.RepeatedField(proto.STRING, number=2,)
    python_module = proto.Field(proto.STRING, number=3,)
    args = proto.RepeatedField(proto.STRING, number=4,)


class Scheduling(proto.Message):
    r"""All parameters related to queuing and scheduling of custom
    jobs.

    Attributes:
        timeout (google.protobuf.duration_pb2.Duration):
            The maximum job running time. The default is
            7 days.
        restart_job_on_worker_restart (bool):
            Restarts the entire CustomJob if a worker
            gets restarted. This feature can be used by
            distributed training jobs that are not resilient
            to workers leaving and joining a job.
    """

    timeout = proto.Field(proto.MESSAGE, number=1, message=duration_pb2.Duration,)
    restart_job_on_worker_restart = proto.Field(proto.BOOL, number=3,)


__all__ = tuple(sorted(__protobuf__.manifest))
