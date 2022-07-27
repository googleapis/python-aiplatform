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

from typing import Any, Dict, Optional

from google.cloud import aiplatform
from google.cloud.aiplatform.metadata.schema.system import context_schema


#  [START aiplatform_sdk_create_context_with_sdk_sample]
def create_context_sample(
    display_name: str,
    project: str,
    location: str,
    context_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    schema_version: Optional[str] = None,
    description: Optional[str] = None,
):
    aiplatform.init(project=project, location=location)

    return context_schema.Experiment(
        display_name=display_name,
        context_id=context_id,
        metadata=metadata,
        schema_version=schema_version,
        description=description,
    ).create()

#  [END aiplatform_sdk_create_context_with_sdk_sample]
