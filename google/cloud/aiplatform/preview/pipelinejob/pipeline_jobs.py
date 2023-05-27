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

import datetime
import re
from typing import Any, Dict, Optional

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import (
    pipeline_job_v1beta1 as gca_pipeline_job,
)
from google.cloud.aiplatform.constants import pipeline as pipeline_constants
from google.cloud.aiplatform.metadata import constants as metadata_constants
from google.cloud.aiplatform.metadata import experiment_resources
from google.cloud.aiplatform.utils import gcs_utils
from google.cloud.aiplatform.utils import pipeline_utils
from google.cloud.aiplatform.utils import yaml_utils

from google.protobuf import json_format

_LOGGER = base.Logger(__name__)

_PIPELINE_COMPLETE_STATES = pipeline_constants._PIPELINE_COMPLETE_STATES

_PIPELINE_ERROR_STATES = pipeline_constants._PIPELINE_ERROR_STATES

# Pattern for valid names used as a Vertex resource name.
_VALID_NAME_PATTERN = pipeline_constants._VALID_NAME_PATTERN

# Pattern for an Artifact Registry URL.
_VALID_AR_URL = pipeline_constants._VALID_AR_URL

# Pattern for any JSON or YAML file over HTTPS.
_VALID_HTTPS_URL = pipeline_constants._VALID_HTTPS_URL

_READ_MASK_FIELDS = pipeline_constants._READ_MASK_FIELDS


def _get_current_time() -> datetime.datetime:
    """Gets the current timestamp."""
    return datetime.datetime.now()


def _set_enable_caching_value(
    pipeline_spec: Dict[str, Any], enable_caching: bool
) -> None:
    """Sets pipeline tasks caching options.

    Args:
     pipeline_spec (Dict[str, Any]):
          Required. The dictionary of pipeline spec.
     enable_caching (bool):
          Required. Whether to enable caching.
    """
    for component in [pipeline_spec["root"]] + list(
        pipeline_spec["components"].values()
    ):
        if "dag" in component:
            for task in component["dag"]["tasks"].values():
                task["cachingOptions"] = {"enableCache": enable_caching}


class PipelineJob(
    pipeline_jobs.PipelineJob,
    experiment_loggable_schemas=(
        experiment_resources._ExperimentLoggableSchema(
            title=metadata_constants.SYSTEM_PIPELINE_RUN
        ),
    ),
):
    """Preview PipelineJob resource for Vertex AI."""

    client_class = utils.PipelineJobClientWithOverride

    def __init__(
        self,
        # TODO(b/223262536): Make the display_name parameter optional in the next major release
        display_name: str,
        template_path: str,
        job_id: Optional[str] = None,
        pipeline_root: Optional[str] = None,
        parameter_values: Optional[Dict[str, Any]] = None,
        input_artifacts: Optional[Dict[str, str]] = None,
        enable_caching: Optional[bool] = None,
        encryption_spec_key_name: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        failure_policy: Optional[str] = None,
    ):
        if not display_name:
            display_name = self.__class__._generate_display_name()
        utils.validate_display_name(display_name)

        if labels:
            utils.validate_labels(labels)

        super().__init__(
            display_name=display_name,
            template_path=template_path,
            job_id=job_id,
            pipeline_root=pipeline_root,
            parameter_values=parameter_values,
            input_artifacts=input_artifacts,
            enable_caching=enable_caching,
            encryption_spec_key_name=encryption_spec_key_name,
            labels=labels,
            credentials=credentials,
            project=project,
            location=location,
            failure_policy=failure_policy,
        )

        self._parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        # this loads both .yaml and .json files because YAML is a superset of JSON
        pipeline_json = yaml_utils.load_yaml(
            template_path, self.project, self.credentials
        )

        # Pipeline_json can be either PipelineJob or PipelineSpec.
        if pipeline_json.get("pipelineSpec") is not None:
            pipeline_job = pipeline_json
            pipeline_root = (
                pipeline_root
                or pipeline_job["pipelineSpec"].get("defaultPipelineRoot")
                or pipeline_job["runtimeConfig"].get("gcsOutputDirectory")
                or initializer.global_config.staging_bucket
            )
        else:
            pipeline_job = {
                "pipelineSpec": pipeline_json,
                "runtimeConfig": {},
            }
            pipeline_root = (
                pipeline_root
                or pipeline_job["pipelineSpec"].get("defaultPipelineRoot")
                or initializer.global_config.staging_bucket
            )
        pipeline_root = (
            pipeline_root
            or gcs_utils.generate_gcs_directory_for_pipeline_artifacts(
                project=project,
                location=location,
            )
        )
        builder = pipeline_utils.PipelineRuntimeConfigBuilder.from_job_spec_json(
            pipeline_job
        )
        builder.update_pipeline_root(pipeline_root)
        builder.update_runtime_parameters(parameter_values)
        builder.update_input_artifacts(input_artifacts)

        builder.update_failure_policy(failure_policy)
        runtime_config_dict = builder.build()

        runtime_config = gca_pipeline_job.PipelineJob.RuntimeConfig()._pb
        json_format.ParseDict(runtime_config_dict, runtime_config)

        pipeline_name = pipeline_job["pipelineSpec"]["pipelineInfo"]["name"]
        self.job_id = job_id or "{pipeline_name}-{timestamp}".format(
            pipeline_name=re.sub("[^-0-9a-z]+", "-", pipeline_name.lower())
            .lstrip("-")
            .rstrip("-"),
            timestamp=_get_current_time().strftime("%Y%m%d%H%M%S"),
        )
        if not _VALID_NAME_PATTERN.match(self.job_id):
            raise ValueError(
                f"Generated job ID: {self.job_id} is illegal as a Vertex pipelines job ID. "
                "Expecting an ID following the regex pattern "
                f'"{_VALID_NAME_PATTERN.pattern[1:-1]}"'
            )

        if enable_caching is not None:
            _set_enable_caching_value(pipeline_job["pipelineSpec"], enable_caching)

        pipeline_job_args = {
            "display_name": display_name,
            "pipeline_spec": pipeline_job["pipelineSpec"],
            "labels": labels,
            "runtime_config": runtime_config,
            "encryption_spec": initializer.global_config.get_encryption_spec(
                encryption_spec_key_name=encryption_spec_key_name
            ),
        }

        if _VALID_AR_URL.match(template_path) or _VALID_HTTPS_URL.match(template_path):
            pipeline_job_args["template_uri"] = template_path

        self._gca_resource = gca_pipeline_job.PipelineJob(**pipeline_job_args)

    def create_schedule(
        self,
        cron_expression: str,
        display_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        allow_queuing: Optional[bool] = False,
        max_run_count: Optional[int] = None,
        max_concurrent_run_count: Optional[int] = 1,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        sync: Optional[bool] = True,
        create_request_timeout: Optional[float] = None,
    ) -> "pipeline_job_schedules.PipelineJobSchedule":  # noqa: F821
        """Creates a PipelineJobSchedule directly from a PipelineJob.

        Args:
            cron_expression (str):
                Required. Time specification (cron schedule expression) to launch scheduled runs.
                To explicitly set a timezone to the cron tab, apply a prefix: "CRON_TZ=${IANA_TIME_ZONE}" or "TZ=${IANA_TIME_ZONE}".
                The ${IANA_TIME_ZONE} may only be a valid string from IANA time zone database.
                For example, "CRON_TZ=America/New_York 1 * * * *", or "TZ=America/New_York 1 * * * *".
            display_name (str):
                Required. The user-defined name of this PipelineJobSchedule.
            start_time (str):
                Optional. Timestamp after which the first run can be scheduled.
                If unspecified, it defaults to the schedule creation timestamp.
            end_time (str):
                Optional. Timestamp after which no more runs will be scheduled.
                If unspecified, then runs will be scheduled indefinitely.
            allow_queuing (bool):
                Optional. Whether new scheduled runs can be queued when max_concurrent_runs limit is reached.
            max_run_count (int):
                Optional. Maximum run count of the schedule.
                If specified, The schedule will be completed when either started_run_count >= max_run_count or when end_time is reached.
            max_concurrent_run_count (int):
                Optional. Maximum number of runs that can be started concurrently for this PipelineJobSchedule.
            service_account (str):
                Optional. Specifies the service account for workload run-as account.
                Users submitting jobs must have act-as permission on this run-as account.
            network (str):
                Optional. The full name of the Compute Engine network to which the job
                should be peered. For example, projects/12345/global/networks/myVPC.
                Private services access must already be configured for the network.
                If left unspecified, the network set in aiplatform.init will be used.
                Otherwise, the job is not peered with any network.
            sync (bool):
                Optional. Whether to execute this method synchronously.
                If False, this method will unblock and it will be executed in a concurrent Future.
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.
        Returns:
            A Vertex AI PipelineJobSchedule
        """
        from google.cloud.aiplatform.preview.pipelinejobschedule import (
            pipeline_job_schedules,
        )

        if not display_name:
            display_name = self.__class__._generate_display_name(
                prefix="PipelineJobSchedule"
            )

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=self,
            display_name=display_name,
        )

        pipeline_job_schedule.create(
            cron_expression=cron_expression,
            start_time=start_time,
            end_time=end_time,
            allow_queuing=allow_queuing,
            max_run_count=max_run_count,
            max_concurrent_run_count=max_concurrent_run_count,
            service_account=service_account,
            network=network,
            sync=sync,
            create_request_timeout=create_request_timeout,
        )
        return pipeline_job_schedule

    @property
    def runtime_config(self):
        return self._gca_resource.runtime_config
