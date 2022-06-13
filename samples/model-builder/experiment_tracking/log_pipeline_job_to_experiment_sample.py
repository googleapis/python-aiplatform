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


#  [START aiplatform_sdk_log_pipeline_job_to_experiment_sample]
def log_pipeline_job_to_experiment_sample(
    experiment_name: str,
    pipeline_job_display_name: str,
    template_path: str,
    pipeline_root: str,
    parameter_values: Optional[Dict[str, Any]],
    project: str,
    location: str,
):
    aiplatform.init(project=project, location=location)

    pipeline_job = aiplatform.PipelineJob(
        display_name=pipeline_job_display_name,
        template_path=template_path,
        pipeline_root=pipeline_root,
        parameter_values=parameter_values,
    )

    pipeline_job.submit(experiment=experiment_name)


#  [END aiplatform_sdk_log_pipeline_job_to_experiment_sample]
