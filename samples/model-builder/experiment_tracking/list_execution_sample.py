# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_create_execution_with_sdk_sample]
def list_execution_sample(
    project: str,
    location: str,
    display_name_filter: Optional[str] = "display_name=\"my_execution_*\"",
    create_date_filter:  Optional[str] = "create_time>\"2022-06-11T12:30:00-08:00\"",
):
    aiplatform.init(
        project=project,
        location=location)

    combined_filters = f"{display_name_filter} AND {create_date_filter}"

    return aiplatform.Execution.list(filter=combined_filters)


#  [END aiplatform_sdk_create_execution_with_sdk_sample]
