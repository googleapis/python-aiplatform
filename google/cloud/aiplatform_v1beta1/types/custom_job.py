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


from google.cloud.aiplatform_v1beta1.types import io
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import machine_resources
from google.protobuf import duration_pb2 as duration  # type: ignore
from google.protobuf import timestamp_pb2 as timestamp  # type: ignore
from google.rpc import status_pb2 as status  # type: ignore


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
        job_spec (~.custom_job.CustomJobSpec):
            Required. Job spec.
        state (~.job_state.JobState):
            Output only. The detailed state of the job.
        create_time (~.timestamp.Timestamp):
            Output only. Time when the CustomJob was
            created.
        start_time (~.timestamp.Timestamp):
            Output only. Time when the CustomJob for the first time
            entered the ``JOB_STATE_RUNNING`` state.
        end_time (~.timestamp.Timestamp):
            Output only. Time when the CustomJob entered any of the
            following states: ``JOB_STATE_SUCCEEDED``,
            ``JOB_STATE_FAILED``, ``JOB_STATE_CANCELLED``.
        update_time (~.timestamp.Timestamp):
            Output only. Time when the CustomJob was most
            recently updated.
        error (~.status.Status):
            Output only. Only populated when job's state is
            ``JOB_STATE_FAILED`` or ``JOB_STATE_CANCELLED``.
        labels (Sequence[~.custom_job.CustomJob.LabelsEntry]):
            The labels with user-defined metadata to
            organize CustomJobs.
            Label keys and values can be no longer than 64
            characters (Unicode codepoints), can only
            contain lowercase letters, numeric characters,
            underscores and dashes. International characters
            are allowed.
            See https://goo.gl/xmQnxf for more information
            and examples of labels.
    """

    name = proto.Field(proto.STRING, number=1)
    display_name = proto.Field(proto.STRING, number=2)
    job_spec = proto.Field(proto.MESSAGE, number=4, message="CustomJobSpec",)
    state = proto.Field(proto.ENUM, number=5, enum=job_state.JobState,)
    create_time = proto.Field(proto.MESSAGE, number=6, message=timestamp.Timestamp,)
    start_time = proto.Field(proto.MESSAGE, number=7, message=timestamp.Timestamp,)
    end_time = proto.Field(proto.MESSAGE, number=8, message=timestamp.Timestamp,)
    update_time = proto.Field(proto.MESSAGE, number=9, message=timestamp.Timestamp,)
    error = proto.Field(proto.MESSAGE, number=10, message=status.Status,)
    labels = proto.MapField(proto.STRING, proto.STRING, number=11)


class CustomJobSpec(proto.Message):
    r"""Represents the spec of a CustomJob.

    Attributes:
        worker_pool_specs (Sequence[~.custom_job.WorkerPoolSpec]):
            Required. The spec of the worker pools
            including machine type and Docker image.
        scheduling (~.custom_job.Scheduling):
            Scheduling options for a CustomJob.
        base_output_directory (~.io.GcsDestination):
            The Google Cloud Storage location to store the output of
            this CustomJob or HyperparameterTuningJob. For
            HyperparameterTuningJob,
            ``base_output_directory``
            of each child CustomJob backing a Trial is set to a
            subdirectory of name
            ``id`` under parent
            HyperparameterTuningJob's

            ``base_output_directory``.

            Following AI Platform environment variables will be passed
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
    """

    worker_pool_specs = proto.RepeatedField(
        proto.MESSAGE, number=1, message="WorkerPoolSpec",
    )
    scheduling = proto.Field(proto.MESSAGE, number=3, message="Scheduling",)
    base_output_directory = proto.Field(
        proto.MESSAGE, number=6, message=io.GcsDestination,
    )


class WorkerPoolSpec(proto.Message):
    r"""Represents the spec of a worker pool in a job.

    Attributes:
        container_spec (~.custom_job.ContainerSpec):
            The custom container task.
        python_package_spec (~.custom_job.PythonPackageSpec):
            The Python packaged task.
        machine_spec (~.machine_resources.MachineSpec):
            Required. Immutable. The specification of a
            single machine.
        replica_count (int):
            Required. The number of worker replicas to
            use for this worker pool.
    """

    container_spec = proto.Field(proto.MESSAGE, number=6, message="ContainerSpec",)
    python_package_spec = proto.Field(
        proto.MESSAGE, number=7, message="PythonPackageSpec",
    )
    machine_spec = proto.Field(
        proto.MESSAGE, number=1, message=machine_resources.MachineSpec,
    )
    replica_count = proto.Field(proto.INT64, number=2)


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

    image_uri = proto.Field(proto.STRING, number=1)
    command = proto.RepeatedField(proto.STRING, number=2)
    args = proto.RepeatedField(proto.STRING, number=3)


class PythonPackageSpec(proto.Message):
    r"""The spec of a Python packaged code.

    Attributes:
        executor_image_uri (str):
            Required. The URI of a container image in the
            Container Registry that will run the provided
            python package. AI Platform provides wide range
            of executor images with pre-installed packages
            to meet users' various use cases. Only one of
            the provided images can be set here.
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

    executor_image_uri = proto.Field(proto.STRING, number=1)
    package_uris = proto.RepeatedField(proto.STRING, number=2)
    python_module = proto.Field(proto.STRING, number=3)
    args = proto.RepeatedField(proto.STRING, number=4)


class Scheduling(proto.Message):
    r"""All parameters related to queuing and scheduling of custom
    jobs.

    Attributes:
        timeout (~.duration.Duration):
            The maximum job running time. The default is
            7 days.
        restart_job_on_worker_restart (bool):
            Restarts the entire CustomJob if a worker
            gets restarted. This feature can be used by
            distributed training jobs that are not resilient
            to workers leaving and joining a job.
    """

    timeout = proto.Field(proto.MESSAGE, number=1, message=duration.Duration,)
    restart_job_on_worker_restart = proto.Field(proto.BOOL, number=3)


__all__ = tuple(sorted(__protobuf__.manifest))
