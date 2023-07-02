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

from typing import Optional

from google.cloud.aiplatform import base
from google.cloud.aiplatform import pipeline_jobs
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.constants import pipeline as pipeline_constants
from google.cloud.aiplatform.metadata import constants as metadata_constants
from google.cloud.aiplatform.metadata import experiment_resources

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


class _PipelineJob(
    pipeline_jobs.PipelineJob,
    experiment_loggable_schemas=(
        experiment_resources._ExperimentLoggableSchema(
            title=metadata_constants.SYSTEM_PIPELINE_RUN
        ),
    ),
):
    """Preview PipelineJob resource for Vertex AI."""

    def create_schedule(
        self,
        cron_expression: str,
        display_name: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        allow_queueing: bool = False,
        max_run_count: Optional[int] = None,
        max_concurrent_run_count: int = 1,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        create_request_timeout: Optional[float] = None,
    ) -> "pipeline_job_schedules.PipelineJobSchedule":  # noqa: F821
        """Creates a PipelineJobSchedule directly from a PipelineJob.

        Example Usage:

        pipeline_job = aiplatform.PipelineJob(
            display_name='job_display_name',
            template_path='your_pipeline.yaml',
        )
        pipeline_job.run()
        pipeline_job_schedule = pipeline_job.create_schedule(
            cron_expression='* * * * *',
            display_name='schedule_display_name',
        )

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
            allow_queueing (bool):
                Optional. Whether new scheduled runs can be queued when max_concurrent_runs limit is reached.
            max_run_count (int):
                Optional. Maximum run count of the schedule.
                If specified, The schedule will be completed when either started_run_count >= max_run_count or when end_time is reached.
                Must be positive and <= 2^63-1.
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
            create_request_timeout (float):
                Optional. The timeout for the create request in seconds.

        Returns:
            A Vertex AI PipelineJobSchedule.
        """
        from google.cloud.aiplatform.preview.pipelinejobschedule import (
            pipeline_job_schedules,
        )

        if not display_name:
            display_name = self._generate_display_name(prefix="PipelineJobSchedule")
        utils.validate_display_name(display_name)

        pipeline_job_schedule = pipeline_job_schedules.PipelineJobSchedule(
            pipeline_job=self,
            display_name=display_name,
        )

        pipeline_job_schedule.create(
            cron_expression=cron_expression,
            start_time=start_time,
            end_time=end_time,
            allow_queueing=allow_queueing,
            max_run_count=max_run_count,
            max_concurrent_run_count=max_concurrent_run_count,
            service_account=service_account,
            network=network,
            create_request_timeout=create_request_timeout,
        )
        return pipeline_job_schedule
