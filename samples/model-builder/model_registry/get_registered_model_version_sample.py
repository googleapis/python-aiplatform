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

# [START aiplatform_model_registry_get_registered_model_version_sample]

from typing import Optional

from google.cloud import aiplatform


def get_registered_model_version_sample(
    model_id: str, project: str, location: str, version: Optional[str] = None
):
    """
    Get a registered model version.
    Args:
        model_id: The ID of the model. Parent resource name of the model is also accepted.
        project: The project.
        location: The location.
        version: The version of the model.
    Returns:
        Model resource.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Initialize the Model Registry. The parent_name of get method can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model_registry = aiplatform.models.ModelRegistry(model=model_id)

    # Get the registered model version.
    registered_model_version = model_registry.get_model(version=version)

    return registered_model_version


# [END aiplatform_model_registry_get_registered_model_version_sample]
