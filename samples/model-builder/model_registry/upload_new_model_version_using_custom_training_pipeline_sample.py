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

# [START aiplatform_model_registry_upload_new_model_version_using_custom_training_pipeline]

from typing import List

from google.cloud import aiplatform


def upload_new_model_version_using_custom_training_pipeline(
    display_name: str,
    script_path: str,
    container_uri,
    model_serving_container_image_uri: str,
    dataset_id: str,
    replica_count: int,
    machine_type: str,
    accelerator_type: str,
    accelerator_count: int,
    parent_model: str,
    args: List[str],
    model_version_aliases: List[str],
    model_version_description: str,
    is_default_version: bool,
    project: str,
    location: str,
):
    """
    Uploads a new model version using a custom training pipeline.
    Args:
        display_name: The display name of the model version.
        script_path: The path to the Python script that trains the model.
        container_uri: The URI of the container to use for training.
        model_serving_container_image_uri: The URI of the serving container image to use.
        dataset_id: The ID of the dataset to use for training.
        replica_count: The number of replicas to use for training.
        machine_type: The machine type to use for training.
        accelerator_type: The accelerator type to use for training.
        accelerator_count: The number of accelerators to use for training.
        parent_model: The parent resource name of an existing model.
        args: A list of arguments to pass to the training script.
        model_version_aliases: The aliases of the model version to create.
        model_version_description: The description of the model version.
        is_default_version: Whether the model version is the default version.
        project: The project ID.
        location: The region name.
    Returns:
        The new version of the model.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Create the training job.
    # This job will upload a new, non-default version of the my-training-job model
    job = aiplatform.CustomTrainingJob(
        display_name=display_name,
        script_path=script_path,
        container_uri=container_uri,
        model_serving_container_image_uri=model_serving_container_image_uri,
    )

    # Create dataset
    # This examples uses a TabularDataset, but you can use any dataset type.
    dataset = aiplatform.TabularDataset(dataset_id) if dataset_id else None

    # Run the training job.
    model = job.run(
        dataset=dataset,
        args=args,
        replica_count=replica_count,
        machine_type=machine_type,
        accelerator_type=accelerator_type,
        accelerator_count=accelerator_count,
        parent_model=parent_model,
        model_version_aliases=model_version_aliases,
        model_version_description=model_version_description,
        is_default_version=is_default_version,
    )

    return model


# [END aiplatform_model_registry_upload_new_model_version_using_custom_training_pipeline]
