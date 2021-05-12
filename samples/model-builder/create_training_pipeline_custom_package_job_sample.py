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

from typing import List, Optional, Union

from google.cloud import aiplatform


#  [START aiplatform_sdk_create_training_pipeline_custom_package_job_sample]
def create_training_pipeline_custom_package_job_sample(
    project: str,
    location: str,
    staging_bucket: str,
    display_name: str,
    python_package_gcs_uri: str,
    python_module_name: str,
    container_uri: str,
    model_serving_container_image_uri: str,
    dataset_id: Optional[str] = None,
    model_display_name: Optional[str] = None,
    args: Optional[List[Union[str, float, int]]] = None,
    replica_count: int = 1,
    machine_type: str = "n1-standard-4",
    accelerator_type: str = "ACCELERATOR_TYPE_UNSPECIFIED",
    accelerator_count: int = 0,
    training_fraction_split: float = 0.8,
    validation_fraction_split: float = 0.1,
    test_fraction_split: float = 0.1,
    sync: bool = True,
):
    aiplatform.init(project=project, location=location, staging_bucket=staging_bucket)

    job = aiplatform.CustomPythonPackageTrainingJob(
        display_name=display_name,
        python_package_gcs_uri=python_package_gcs_uri,
        python_module_name=python_module_name,
        container_uri=container_uri,
        model_serving_container_image_uri=model_serving_container_image_uri,
    )

    # This example uses an ImageDataset, but you can use another type
    dataset = aiplatform.ImageDataset(dataset_id) if dataset_id else None

    model = job.run(
        dataset=dataset,
        model_display_name=model_display_name,
        args=args,
        replica_count=replica_count,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        training_fraction_split=training_fraction_split,
        validation_fraction_split=validation_fraction_split,
        test_fraction_split=test_fraction_split,
        sync=sync,
    )

    model.wait()

    print(model.display_name)
    print(model.resource_name)
    print(model.uri)
    return model


#  [END aiplatform_sdk_create_training_pipeline_custom_package_job_sample]
