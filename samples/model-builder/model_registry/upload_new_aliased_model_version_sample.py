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

# [START aiplatform_model_registry_upload_new_aliased_model_version_sample]

from typing import List

from google.cloud import aiplatform


def upload_new_aliased_model_version_sample(
        model_id: str,
        artifact_uri: str,
        serving_container_image: str,
        is_default_version: bool,
        version_aliases: List[str],
        version_description: str,
        project: str,
        location: str,
):
    """
    Uploads a new aliased version of a model with ID 'model_id'.
    Args:
        model_id: The ID of the model to upload a new version. Parent resource name of the model is also accepted.
        artifact_uri: The URI of the model artifact to upload.
        serving_container_image: The name of the serving container image to use.
        is_default_version: Whether this version is the default version of the model.
        version_aliases: The aliases of the model version.
        version_description: The description of the model version.
        project: The project.
        location: The location.
    Returns:
        The new version of the model.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Upload the model with the ID 'model_id'. The parent_name of upload method can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model = aiplatform.Model.upload(
        artifact_uri=artifact_uri,
        serving_container_image=serving_container_image,
        is_default_version=is_default_version,
        version_aliases=version_aliases,
        version_description=version_description,
        parent_name=model_id
    )

    return model

# [END aiplatform_model_registry_upload_new_aliased_model_version_sample]
