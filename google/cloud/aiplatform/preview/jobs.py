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

from typing import Dict, List, Optional, Union
import uuid

from google.api_core import retry
from google.auth import credentials as auth_credentials
from google.cloud import aiplatform
from google.cloud.aiplatform import base
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import jobs
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import (
    custom_job_v1beta1 as gca_custom_job_compat,
    job_state as gca_job_state,
    job_state_v1beta1 as gca_job_state_v1beta1,
)
from google.cloud.aiplatform.compat.types import (
    execution_v1beta1 as gcs_execution_compat,
)
from google.cloud.aiplatform.compat.types import io_v1beta1 as gca_io_compat
from google.cloud.aiplatform.metadata import constants as metadata_constants
from google.cloud.aiplatform.utils import console_utils
import proto

from google.protobuf import duration_pb2  # type: ignore


_LOGGER = base.Logger(__name__)
_DEFAULT_RETRY = retry.Retry()
# TODO(b/242108750): remove temporary logic once model monitoring for batch prediction is GA
_JOB_COMPLETE_STATES = (
    gca_job_state.JobState.JOB_STATE_SUCCEEDED,
    gca_job_state.JobState.JOB_STATE_FAILED,
    gca_job_state.JobState.JOB_STATE_CANCELLED,
    gca_job_state.JobState.JOB_STATE_PAUSED,
    gca_job_state_v1beta1.JobState.JOB_STATE_SUCCEEDED,
    gca_job_state_v1beta1.JobState.JOB_STATE_FAILED,
    gca_job_state_v1beta1.JobState.JOB_STATE_CANCELLED,
    gca_job_state_v1beta1.JobState.JOB_STATE_PAUSED,
)

_JOB_ERROR_STATES = (
    gca_job_state.JobState.JOB_STATE_FAILED,
    gca_job_state.JobState.JOB_STATE_CANCELLED,
    gca_job_state_v1beta1.JobState.JOB_STATE_FAILED,
    gca_job_state_v1beta1.JobState.JOB_STATE_CANCELLED,
)


class CustomJob(jobs.CustomJob):
    """Vertex AI Custom Job."""

    def __init__(
        self,
        # TODO(b/223262536): Make display_name parameter fully optional in next major release
        display_name: str,
        worker_pool_specs: Union[
            List[Dict], List[gca_custom_job_compat.WorkerPoolSpec]
        ],
        base_output_dir: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        labels: Optional[Dict[str, str]] = None,
        encryption_spec_key_name: Optional[str] = None,
        staging_bucket: Optional[str] = None,
        persistent_resource_id: Optional[str] = None,
    ):
        """Constructs a Custom Job with Worker Pool Specs.

        ```
        Example usage:
        worker_pool_specs = [
                {
                    "machine_spec": {
                        "machine_type": "n1-standard-4",
                        "accelerator_type": "NVIDIA_TESLA_K80",
                        "accelerator_count": 1,
                    },
                    "replica_count": 1,
                    "container_spec": {
                        "image_uri": container_image_uri,
                        "command": [],
                        "args": [],
                    },
                }
            ]

        my_job = aiplatform.CustomJob(
            display_name='my_job',
            worker_pool_specs=worker_pool_specs,
            labels={'my_key': 'my_value'},
        )

        my_job.run()
        ```


        For more information on configuring worker pool specs please visit:
        https://cloud.google.com/ai-platform-unified/docs/training/create-custom-job


        Args:
            display_name (str):
                Required. The user-defined name of the HyperparameterTuningJob.
                The name can be up to 128 characters long and can be consist
                of any UTF-8 characters.
            worker_pool_specs (Union[List[Dict], List[aiplatform.gapic.WorkerPoolSpec]]):
                Required. The spec of the worker pools including machine type and Docker image.
                Can provided as a list of dictionaries or list of WorkerPoolSpec proto messages.
            base_output_dir (str):
                Optional. GCS output directory of job. If not provided a
                timestamped directory in the staging directory will be used.
            project (str):
                Optional.Project to run the custom job in. Overrides project set in aiplatform.init.
            location (str):
                Optional.Location to run the custom job in. Overrides location set in aiplatform.init.
            credentials (auth_credentials.Credentials):
                Optional.Custom credentials to use to run call custom job service. Overrides
                credentials set in aiplatform.init.
            labels (Dict[str, str]):
                Optional. The labels with user-defined metadata to
                organize CustomJobs.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                and examples of labels.
            encryption_spec_key_name (str):
                Optional.Customer-managed encryption key name for a
                CustomJob. If this is set, then all resources
                created by the CustomJob will be encrypted with
                the provided encryption key.
            staging_bucket (str):
                Optional. Bucket for produced custom job artifacts. Overrides
                staging_bucket set in aiplatform.init.
            persistent_resource_id (str):
                Optional. The ID of the PersistentResource in the same Project
                and Location. If this is specified, the job will be run on
                existing machines held by the PersistentResource instead of
                on-demand short-live machines. The network and CMEK configs on
                the job should be consistent with those on the PersistentResource,
                otherwise, the job will be rejected.

        Raises:
            RuntimeError: If staging bucket was not set using aiplatform.init
                and a staging bucket was not passed in.
        """

        super().__init__(
            display_name=display_name,
            worker_pool_specs=worker_pool_specs,
            base_output_dir=base_output_dir,
            project=project,
            location=location,
            credentials=credentials,
            labels=labels,
            encryption_spec_key_name=encryption_spec_key_name,
            staging_bucket=staging_bucket,
        )

        staging_bucket = staging_bucket or initializer.global_config.staging_bucket

        if not staging_bucket:
            raise RuntimeError(
                "staging_bucket should be passed to CustomJob constructor or "
                "should be set using aiplatform.init(staging_bucket='gs://my-bucket')"
            )

        if labels:
            utils.validate_labels(labels)

        # default directory if not given
        base_output_dir = base_output_dir or utils._timestamped_gcs_dir(
            staging_bucket, "aiplatform-custom-job"
        )

        if not display_name:
            display_name = self.__class__._generate_display_name()

        self._gca_resource = gca_custom_job_compat.CustomJob(
            display_name=display_name,
            job_spec=gca_custom_job_compat.CustomJobSpec(
                worker_pool_specs=worker_pool_specs,
                base_output_directory=gca_io_compat.GcsDestination(
                    output_uri_prefix=base_output_dir
                ),
                persistent_resource_id=persistent_resource_id,
            ),
            labels=labels,
            encryption_spec=initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name,
                select_version=compat.V1BETA1,
            ),
        )

        self._experiment = None
        self._experiment_run = None
        self._enable_autolog = False

    def _get_gca_resource(
        self,
        resource_name: str,
        parent_resource_name_fields: Optional[Dict[str, str]] = None,
    ) -> proto.Message:
        """Returns GAPIC service representation of client class resource.

        Args:
            resource_name (str): Required. A fully-qualified resource name or ID.
            parent_resource_name_fields (Dict[str,str]):
                Optional. Mapping of parent resource name key to values. These
                will be used to compose the resource name if only resource ID is given.
                Should not include project and location.
        """
        resource_name = utils.full_resource_name(
            resource_name=resource_name,
            resource_noun=self._resource_noun,
            parse_resource_name_method=self._parse_resource_name,
            format_resource_name_method=self._format_resource_name,
            project=self.project,
            location=self.location,
            parent_resource_name_fields=parent_resource_name_fields,
            resource_id_validator=self._resource_id_validator,
        )

        return getattr(self.api_client.select_version("v1beta1"), self._getter_method)(
            name=resource_name, retry=_DEFAULT_RETRY
        )

    def submit(
        self,
        *,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        timeout: Optional[int] = None,
        restart_job_on_worker_restart: bool = False,
        enable_web_access: bool = False,
        experiment: Optional[Union["aiplatform.Experiment", str]] = None,
        experiment_run: Optional[Union["aiplatform.ExperimentRun", str]] = None,
        tensorboard: Optional[str] = None,
        create_request_timeout: Optional[float] = None,
        disable_retries: bool = False,
    ) -> None:
        """Submit the configured CustomJob.

        Args:
            service_account (str):
                Optional. Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                Optional. The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
            timeout (int):
                The maximum job running time in seconds. The default is 7 days.
            restart_job_on_worker_restart (bool):
                Restarts the entire CustomJob if a worker
                gets restarted. This feature can be used by
                distributed training jobs that are not resilient
                to workers leaving and joining a job.
            enable_web_access (bool):
                Whether you want Vertex AI to enable interactive shell access
                to training containers.
                https://cloud.google.com/vertex-ai/docs/training/monitor-debug-interactive-shell
            experiment (Union[aiplatform.Experiment, str]):
                Optional. The instance or name of an Experiment resource to which
                this CustomJob will upload training parameters and metrics.

                `service_account` is required with provided `experiment`.
                For more information on configuring your service account please visit:
                https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-training
            experiment_run (Union[aiplatform.ExperimentRun, str]):
                Optional. The instance or name of an ExperimentRun resource to which
                this CustomJob will upload training parameters and metrics.
                This arg can only be set when `experiment` is set. If 'experiment'
                is set but 'experiment_run` is not, an ExperimentRun resource
                will still be auto-generated.
            tensorboard (str):
                Optional. The name of a Vertex AI
                [Tensorboard][google.cloud.aiplatform.v1beta1.Tensorboard]
                resource to which this CustomJob will upload Tensorboard
                logs. Format:
                ``projects/{project}/locations/{location}/tensorboards/{tensorboard}``

                The training script should write Tensorboard to following Vertex AI environment
                variable:

                AIP_TENSORBOARD_LOG_DIR

                `service_account` is required with provided `tensorboard`.
                For more information on configuring your service account please visit:
                https://cloud.google.com/vertex-ai/docs/experiments/tensorboard-training
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.
            disable_retries (bool):
                Indicates if the job should retry for internal errors after the
                job starts running. If True, overrides
                `restart_job_on_worker_restart` to False.

        Raises:
            ValueError:
                If both `experiment` and `tensorboard` are specified or if
                `enable_autolog` is True in `CustomJob.from_local_script` but
                `experiment` is not specified or the specified experiment
                doesn't have a backing tensorboard.
        """
        if experiment and tensorboard:
            raise ValueError("'experiment' and 'tensorboard' cannot be set together.")
        if self._enable_autolog and (not experiment):
            raise ValueError(
                "'experiment' is required since you've enabled autolog in 'from_local_script'."
            )
        if service_account:
            self._gca_resource.job_spec.service_account = service_account

        if network:
            self._gca_resource.job_spec.network = network

        if timeout or restart_job_on_worker_restart or disable_retries:
            timeout = duration_pb2.Duration(seconds=timeout) if timeout else None
            self._gca_resource.job_spec.scheduling = gca_custom_job_compat.Scheduling(
                timeout=timeout,
                restart_job_on_worker_restart=restart_job_on_worker_restart,
                disable_retries=disable_retries,
            )

        if enable_web_access:
            self._gca_resource.job_spec.enable_web_access = enable_web_access

        if tensorboard:
            self._gca_resource.job_spec.tensorboard = tensorboard

        # TODO(b/275105711) Update implementation after experiment/run in the proto
        if experiment:
            # short-term solution to set experiment/experimentRun in SDK
            if isinstance(experiment, aiplatform.Experiment):
                self._experiment = experiment
                # convert the Experiment instance to string to be passed to env
                experiment = experiment.name
            else:
                self._experiment = aiplatform.Experiment.get(experiment_name=experiment)
            if not self._experiment:
                raise ValueError(
                    f"Experiment '{experiment}' doesn't exist. "
                    "Please call aiplatform.init(experiment='my-exp') to create an experiment."
                )
            elif (
                not self._experiment.backing_tensorboard_resource_name
                and self._enable_autolog
            ):
                raise ValueError(
                    f"Experiment '{experiment}' doesn't have a backing tensorboard resource, "
                    "which is required by the experiment autologging feature. "
                    "Please call Experiment.assign_backing_tensorboard('my-tb-resource-name')."
                )

            # if run name is not specified, auto-generate one
            if not experiment_run:
                experiment_run = (
                    # TODO(b/223262536)Once display_name is optional this run name
                    # might be invalid as well.
                    f"{self._gca_resource.display_name}-{uuid.uuid4().hex[0:5]}"
                )

            # get or create the experiment run for the job
            if isinstance(experiment_run, aiplatform.ExperimentRun):
                self._experiment_run = experiment_run
                # convert the ExperimentRun instance to string to be passed to env
                experiment_run = experiment_run.name
            else:
                self._experiment_run = aiplatform.ExperimentRun.get(
                    run_name=experiment_run,
                    experiment=self._experiment,
                )
            if not self._experiment_run:
                self._experiment_run = aiplatform.ExperimentRun.create(
                    run_name=experiment_run,
                    experiment=self._experiment,
                )
            self._experiment_run.update_state(
                gcs_execution_compat.Execution.State.RUNNING
            )

            worker_pool_specs = self._gca_resource.job_spec.worker_pool_specs
            for spec in worker_pool_specs:
                if not spec:
                    continue

                if "python_package_spec" in spec:
                    container_spec = spec.python_package_spec
                else:
                    container_spec = spec.container_spec

                experiment_env = [
                    {
                        "name": metadata_constants.ENV_EXPERIMENT_KEY,
                        "value": experiment,
                    },
                    {
                        "name": metadata_constants.ENV_EXPERIMENT_RUN_KEY,
                        "value": experiment_run,
                    },
                ]
                if "env" in container_spec:
                    container_spec.env.extend(experiment_env)
                else:
                    container_spec.env = experiment_env

        _LOGGER.log_create_with_lro(self.__class__)

        self._gca_resource = self.api_client.select_version(
            "v1beta1"
        ).create_custom_job(
            parent=self._parent,
            custom_job=self._gca_resource,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_complete_with_getter(
            self.__class__, self._gca_resource, "custom_job"
        )

        _LOGGER.info("View Custom Job:\n%s" % self._dashboard_uri())

        if tensorboard:
            _LOGGER.info(
                "View Tensorboard:\n%s"
                % console_utils.custom_job_tensorboard_console_uri(
                    tensorboard, self.resource_name
                )
            )

        if experiment:
            custom_job = {
                metadata_constants._CUSTOM_JOB_RESOURCE_NAME: self.resource_name,
                metadata_constants._CUSTOM_JOB_CONSOLE_URI: self._dashboard_uri(),
            }

            run_context = self._experiment_run._metadata_node
            custom_jobs = run_context._gca_resource.metadata.get(
                metadata_constants._CUSTOM_JOB_KEY
            )
            if custom_jobs:
                custom_jobs.append(custom_job)
            else:
                custom_jobs = [custom_job]
            run_context.update({metadata_constants._CUSTOM_JOB_KEY: custom_jobs})
