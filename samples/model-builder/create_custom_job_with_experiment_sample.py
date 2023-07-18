# Copyright 2023 Google LLC
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


#  [START aiplatform_sdk_create_custom_job_with_experiment_sample]
def create_custom_job_with_experiment_sample(
    project: str,
    location: str,
    staging_bucket: str,
    display_name: str,
    script_path: str,
    container_uri: str,
    service_account: str,
    experiment: str,
    experiment_run: Optional[str] = None,
) -> None:
    aiplatform.init(project=project, location=location, staging_bucket=staging_bucket)

    job = aiplatform.CustomJob.from_local_script(
        display_name=display_name,
        script_path=script_path,
        container_uri=container_uri,
    )

    job.run(
        service_account=service_account,
        experiment=experiment,
        experiment_run=experiment_run,
    )


#  [END aiplatform_sdk_create_custom_job_with_experiment_sample]
