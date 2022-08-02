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

from google.cloud import aiplatform


#  [START aiplatform_sdk_create_artifact_sample]
def create_artifact_sample(
    schema_title: str,
    project: str,
    location: str,
    uri: Optional[str] = None,
    resource_id: Optional[str] = None,
    display_name: Optional[str] = None,
    schema_version: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict] = None,
):
    artifact = aiplatform.Artifact.create(
        schema_title=schema_title,
        uri=uri,
        resource_id=resource_id,
        display_name=display_name,
        schema_version=schema_version,
        description=description,
        metadata=metadata,
        project=project,
        location=location,
    )
    return artifact

#  [END aiplatform_sdk_create_artifact_sample]
