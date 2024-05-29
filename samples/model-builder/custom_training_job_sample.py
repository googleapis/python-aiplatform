# Copyright 2021 Google LLC
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


from google.cloud import aiplatform


#  [START aiplatform_sdk_custom_training_job_sample]
def custom_training_job_sample(
    project: str,
    location: str,
    bucket: str,
    display_name: str,
    script_path: str,
    script_args: str,
    container_uri: str,
    model_serving_container_image_uri: str,
    requirements: str,
    replica_count: int,
):
    aiplatform.init(project=project, location=location, staging_bucket=bucket)

    job = aiplatform.CustomTrainingJob(
        display_name=display_name,
        script_path=script_path,
        container_uri=container_uri,
        requirements=requirements,
        model_serving_container_image_uri=model_serving_container_image_uri,
    )

    model = job.run(
        args=script_args, replica_count=replica_count, model_display_name=display_name
    )

    return model


#  [END aiplatform_sdk_custom_training_job_sample]
