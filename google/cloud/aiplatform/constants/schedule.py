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

import re

from google.cloud.aiplatform.compat.types import (
    schedule_v1beta1 as gca_schedule,
)

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

# Pattern for valid names used as a Vertex resource name.
_VALID_NAME_PATTERN = re.compile("^[a-z][-a-z0-9]{0,127}$", re.IGNORECASE)

# Pattern for an Artifact Registry URL.
_VALID_AR_URL = re.compile(r"^https:\/\/([\w-]+)-kfp\.pkg\.dev\/.*", re.IGNORECASE)

# Pattern for any JSON or YAML file over HTTPS.
_VALID_HTTPS_URL = re.compile(r"^https:\/\/([\.\/\w-]+)\/.*(json|yaml|yml)$")

# Fields to include in returned PipelineJobSchedule when enable_simple_view=True in PipelineJobSchedule.list()
_PIPELINE_JOB_SCHEDULE_READ_MASK_FIELDS = [
    "name",
    "display_name",
    "start_time",
    "end_time",
    "max_run_count",
    "started_run_count",
    "state",
    "create_time",
    "update_time",
    "cron",
    "catch_up",
]
