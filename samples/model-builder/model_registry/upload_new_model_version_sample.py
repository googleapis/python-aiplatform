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

# [START aiplatform_model_registry_upload_new_model_version_sample]

from google.cloud import aiplatform
def upload_new_model_version_sample(
    model_id: str,
    artifact_uri: str,
    serving_container_image: str,
    project: str,
    location: str,
):
    """
    Uploads a new version of a model to Vertex AI.
    Args:
        model_id: The ID of the model to upload a new version to. Parent resource name of the model is also accepted.
        artifact_uri: The URI of the model artifact to upload.
        serving_container_image: The name of the serving container image to use.
        project: The project.
        location: The location.

    Returns:
        The new version of the model.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Initialize the model.
    model = aiplatform.Model(model_name=model_id)

    # Upload the model with the ID 'model_id'. The parent_name of upload method can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model = model.upload(
        artifact_uri=artifact_uri,
        serving_container_image=serving_container_image,
        parent_name=model_id
    )

    print(model.display_name)
    print(model.resource_name)

    return model


# [END aiplatform_model_registry_upload_new_model_version_sample]
