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

from typing import Any, Dict, List, Optional

from google.cloud import aiplatform


#  [START aiplatform_sdk_start_execution_sample]
def start_execution_sample(
    schema_title: str,
    display_name: str,
    input_artifacts: List[aiplatform.Artifact],
    output_artifacts: List[aiplatform.Artifact],
    project: str,
    location: str,
    resource_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    schema_version: Optional[str] = None,
    resume: bool = False,
):
    aiplatform.init(project=project, location=location)

    with aiplatform.start_execution(
        schema_title=schema_title,
        display_name=display_name,
        resource_id=resource_id,
        metadata=metadata,
        schema_version=schema_version,
        resume=resume,
    ) as execution:
        execution.assign_input_artifacts(input_artifacts)
        execution.assign_output_artifacts(output_artifacts)
        return execution


#  [END aiplatform_sdk_start_execution_sample]
