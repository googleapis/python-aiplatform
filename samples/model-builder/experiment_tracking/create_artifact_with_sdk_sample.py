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

from typing import Dict, Optional

from google.cloud.aiplatform.metadata.schema.system import artifact_schema


#  [START aiplatform_sdk_create_artifact_with_sdk_sample]
def create_artifact_sample(
    project: str,
    location: str,
    uri: Optional[str] = None,
    artifact_id: Optional[str] = None,
    display_name: Optional[str] = None,
    schema_version: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict] = None,
):
    system_artifact_schema = artifact_schema.Artifact(
        uri=uri,
        artifact_id=artifact_id,
        display_name=display_name,
        schema_version=schema_version,
        description=description,
        metadata=metadata,
    )
    return system_artifact_schema.create(project=project, location=location,)

#  [END aiplatform_sdk_create_artifact_with_sdk_sample]
