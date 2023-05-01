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
import time
from typing import Any, Optional

from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import base
from google.cloud.aiplatform import utils

from google.cloud.aiplatform.compat.types import schedule as gca_schedule

_LOGGER = base.Logger(__name__)

_SCHEDULE_COMPLETE_STATES = set(
    [
        gca_schedule.Schedule.State.PAUSED,
        gca_schedule.Schedule.State.COMPLETED,
    ]
)

_SCHEDULE_ERROR_STATES = set(
    [
        gca_schedule.Schedule.State.STATE_UNSPECIFIED,
    ]
)

def _get_current_time() -> datetime.datetime:
    """Gets the current timestamp."""
    return datetime.datetime.now()


class Schedule(
    base.VertexAiStatefulResource,
):
    client_class = utils.ScheduleClientWithOverride
    _resource_noun = "schedules"
    _delete_method = "delete_schedule"
    _getter_method = "get_schedule"
    _list_method = "list_schedules"
    _pause_method = "pause_schedule"
    _resume_method = "resume_schedule"
    _parse_resource_name_method = "parse_schedule_path"
    _format_resource_name_method = "schedule_path"

    # Required by the done() method
    _valid_done_states = _SCHEDULE_COMPLETE_STATES

    def __init__(self, project, location, credentials):
        super().__init__(project=project, location=location, credentials=credentials)

    def pause(self) -> None:
        """Starts asynchronous pause on the Schedule.

        Changes Schedule state from State.ACTIVE to State.PAUSED.
        """
        self.api_client.pause_schedule(name=self.resource_name)

    def resume(
        self,
        catch_up: Optional[bool] = True,
    ) -> None:
        """Starts asynchronous resume on the Schedule.

        Changes Schedule state from State.PAUSED to State.ACTIVE.
        """
        self.api_client.resume_schedule(name=self.resource_name)

