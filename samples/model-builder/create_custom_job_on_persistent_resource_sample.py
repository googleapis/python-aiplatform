# Copyright 2024 Google LLC
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


#  [START aiplatform_sdk_create_custom_job_on_persistent_resource_sample]
def create_custom_job_on_persistent_resource_sample(
    project: str,
    location: str,
    staging_bucket: str,
    display_name: str,
    container_uri: str,
    persistent_resource_id: str,
    service_account: Optional[str] = None,
) -> None:
    aiplatform.init(
        project=project, location=location, staging_bucket=staging_bucket
    )

    worker_pool_specs = [{
        "machine_spec": {
            "machine_type": "n1-standard-4",
            "accelerator_type": "NVIDIA_TESLA_K80",
            "accelerator_count": 1,
        },
        "replica_count": 1,
        "container_spec": {
            "image_uri": container_uri,
            "command": [],
            "args": [],
        },
    }]

    custom_job = aiplatform.CustomJob(
        display_name=display_name,
        worker_pool_specs=worker_pool_specs,
        persistent_resource_id=persistent_resource_id,
    )

    custom_job.run(service_account=service_account)


#  [END aiplatform_sdk_create_custom_job_on_persistent_resource_sample]
