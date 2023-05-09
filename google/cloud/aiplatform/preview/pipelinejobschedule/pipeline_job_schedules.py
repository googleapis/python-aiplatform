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
from typing import List, Optional

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import (
    schedule_v1beta1 as gca_schedule,
)
from google.cloud.aiplatform.constants import schedule as schedule_constants
from google.cloud.aiplatform.preview.pipelinejob.pipeline_jobs import (
    PipelineJob,
)
from google.cloud.aiplatform.preview.schedule.schedules import Schedule
from google.protobuf import field_mask_pb2 as field_mask


_LOGGER = base.Logger(__name__)

# Pattern for valid names used as a Vertex resource name.
_VALID_NAME_PATTERN = schedule_constants._VALID_NAME_PATTERN

# Pattern for an Artifact Registry URL.
_VALID_AR_URL = schedule_constants._VALID_AR_URL

# Pattern for any JSON or YAML file over HTTPS.
_VALID_HTTPS_URL = schedule_constants._VALID_HTTPS_URL

_READ_MASK_FIELDS = schedule_constants._PIPELINE_JOB_SCHEDULE_READ_MASK_FIELDS


def _get_current_time() -> datetime.datetime:
    """Gets the current timestamp."""
    return datetime.datetime.now()


class PipelineJobSchedule(
    Schedule,
):
    def __init__(
        self,
        pipeline_job: PipelineJob,
        display_name: str,
        credentials: Optional[auth_credentials.Credentials] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
    ):
        """Retrieves a PipelineJobSchedule resource and instantiates its
        representation.
        Args:
            pipeline_job (PipelineJob):
                Required. PipelineJob used to init the schedule.
            display_name (str):
                Required. The user-defined name of this PipelineJobSchedule.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create this PipelineJobSchedule.
                Overrides credentials set in aiplatform.init.
            project (str):
                Optional. The project that you want to run this PipelineJobSchedule in.
                If not set, the project set in aiplatform.init will be used.
            location (str):
                Optional. Location to create PipelineJobSchedule. If not set,
                location set in aiplatform.init will be used.
        """
        if not display_name:
            display_name = self.__class__._generate_display_name()
        utils.validate_display_name(display_name)

        super().__init__(project=project, location=location, credentials=credentials)

        self._parent = initializer.global_config.common_location_path(
            project=project, location=location
        )

        create_pipeline_job_request = {
            "parent": self._parent,
            "pipeline_job": {
                "runtime_config": pipeline_job.runtime_config,
                "pipeline_spec": {"fields": pipeline_job.pipeline_spec},
            },
        }
        pipeline_job_schedule_args = {
            "display_name": display_name,
            "create_pipeline_job_request": create_pipeline_job_request,
        }

        self._gca_resource = gca_schedule.Schedule(**pipeline_job_schedule_args)

    def create(
        self,
        cron_expression: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        allow_queuing: Optional[bool] = False,
        max_run_count: Optional[int] = None,
        max_concurrent_run_count: Optional[int] = 1,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        sync: Optional[bool] = True,
        create_request_timeout: Optional[float] = None,
    ) -> None:
        """Create a PipelineJobSchedule.

        Args:
            cron_expression (str):
                Required. Time specification (cron schedule expression) to launch scheduled runs.
                To explicitly set a timezone to the cron tab, apply a prefix: "CRON_TZ=${IANA_TIME_ZONE}" or "TZ=${IANA_TIME_ZONE}".
                The ${IANA_TIME_ZONE} may only be a valid string from IANA time zone database.
                For example, "CRON_TZ=America/New_York 1 * * * *", or "TZ=America/New_York 1 * * * *".
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
        """
        network = network or initializer.global_config.network

        self._create(
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

    @base.optional_sync()
    def _create(
        self,
        cron_expression: str,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        allow_queuing: Optional[bool] = False,
        max_run_count: Optional[int] = None,
        max_concurrent_run_count: Optional[int] = 1,
        service_account: Optional[str] = None,
        network: Optional[str] = None,
        sync: Optional[bool] = True,
        create_request_timeout: Optional[float] = None,
    ) -> None:
        """Helper method to create the PipelineJobSchedule.

        Args:
            cron_expression (str):
                Required. Time specification (cron schedule expression) to launch scheduled runs.
                To explicitly set a timezone to the cron tab, apply a prefix: "CRON_TZ=${IANA_TIME_ZONE}" or "TZ=${IANA_TIME_ZONE}".
                The ${IANA_TIME_ZONE} may only be a valid string from IANA time zone database.
                For example, "CRON_TZ=America/New_York 1 * * * *", or "TZ=America/New_York 1 * * * *".
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
        """
        if cron_expression:
            self._gca_resource.cron = cron_expression
        if start_time:
            self._gca_resource.start_time = start_time
        if end_time:
            self._gca_resource.end_time = end_time
        if allow_queuing:
            self._gca_resource.allow_queueing = allow_queuing
        if max_run_count:
            self._gca_resource.max_run_count = max_run_count
        if max_concurrent_run_count:
            self._gca_resource.max_concurrent_run_count = max_concurrent_run_count

        network = network or initializer.global_config.network

        if service_account:
            self._gca_resource.create_pipeline_job_request.pipeline_job.service_account = (
                service_account
            )

        if network:
            self._gca_resource.create_pipeline_job_request.pipeline_job.network = (
                network
            )

        _LOGGER.log_create_with_lro(self.__class__)

        self._gca_resource = self.api_client.create_schedule(
            parent=self._parent,
            schedule=self._gca_resource,
            timeout=create_request_timeout,
        )

        _LOGGER.log_create_complete_with_getter(
            self.__class__, self._gca_resource, "schedule"
        )

        _LOGGER.info("View Schedule:\n%s" % self._dashboard_uri())

    @classmethod
    def list(
        cls,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        enable_simple_view: bool = False,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["PipelineJobSchedule"]:
        """List all instances of this PipelineJobSchedule resource.

        Example Usage:

        aiplatform.PipelineJobSchedule.list(
            filter='display_name="experiment_a27"',
            order_by='create_time desc'
        )

        Args:
            filter (str):
                Optional. An expression for filtering the results of the request.
                For field names both snake_case and camelCase are supported.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for descending.
                Supported fields: `display_name`, `create_time`, `update_time`
            enable_simple_view (bool):
                Optional. Whether to pass the `read_mask` parameter to the list call.
                Defaults to False if not provided. This will improve the performance of calling
                list(). However, the returned PipelineJobSchedule list will not include all fields for
                each PipelineJobSchedule. Setting this to True will exclude the following fields in your
                response: 'create_pipeline_job_request', 'next_run_time', 'last_pause_time',
                'last_resume_time', 'max_concurrent_run_count', 'allow_queueing','last_scheduled_run_response'.
                The following fields will be included in each PipelineJobSchedule resource in your
                response: 'name', 'display_name', 'start_time', 'end_time', 'max_run_count',
                'started_run_count', 'state', 'create_time', 'update_time', 'cron', 'catch_up'.
            project (str):
                Optional. Project to retrieve list from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve list from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve list. Overrides
                credentials set in aiplatform.init.

        Returns:
            List[PipelineJobSchedule] - A list of PipelineJobSchedule resource objects
        """

        read_mask_fields = None

        if enable_simple_view:
            read_mask_fields = field_mask.FieldMask(paths=_READ_MASK_FIELDS)
            _LOGGER.warn(
                "By enabling simple view, the PipelineJobSchedule resources returned from this method will not contain all fields."
            )

        return cls._list_with_local_order(
            filter=filter,
            order_by=order_by,
            read_mask=read_mask_fields,
            project=project,
            location=location,
            credentials=credentials,
        )

    def list_jobs(
        self,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["PipelineJob"]:
        """List all PipelineJob 's created by this PipelineJobSchedule.

        Example usage:

        pipeline_job_schedule.list_jobs(order_by='create_time_desc')

        Args:
            filter (str):
                Optional. An expression for filtering the results of the request.
                For field names both snake_case and camelCase are supported.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for descending.
                Supported fields: `display_name`, `create_time`, `update_time`
            project (str):
                Optional. Project to retrieve list from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve list from. If not set, location
                set in aiplatform.init will be used.
            schedule_id (str):
                Optional. Schedule ID of the schedule to list. If not set,
                foo
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve list. Overrides
                credentials set in aiplatform.init.
        """
        schedule_id = self._gca_resource.name.split("/")[-1]
        if filter:
            filter = f"schedule_id={schedule_id} AND " + filter
        else:
            filter = f"schedule_id={schedule_id}"
        return self._list_with_local_order(
            filter=filter,
            order_by=order_by,
            read_mask=None,
            project=project,
            location=location,
            credentials=credentials,
        )
