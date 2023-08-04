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

# [START aiplatform_model_registry_upload_new_default_model_version_sample]

from google.cloud import aiplatform


def upload_new_default_model_version_sample(
    parent_name: str,
    artifact_uri: str,
    serving_container_image: str,
    project: str,
    location: str,
):
    """
    Uploads a new default version of a model with ID 'model_id'.
    Args:
        parent_name: The parent resource name of the existing model.
        artifact_uri: The URI of the model artifact to upload.
        serving_container_image: The name of the serving container image to use.
        project: The project ID.
        location: The region name.

    Returns:
        The new version of the model.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Upload a new default version of the Model resource with the ID 'model_id'. The parent_name of Model resource can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model = aiplatform.Model.upload(
        artifact_uri=artifact_uri,
        serving_container_image=serving_container_image,
        parent_name=parent_name,
    )

    return model


# [END aiplatform_model_registry_upload_new_default_model_version_sample]
