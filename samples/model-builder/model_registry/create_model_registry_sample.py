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

# [START aiplatform_model_registry_create_model_registry_sample]

from google.cloud import aiplatform


def create_model_registry_sample(model_id: str, project: str, location: str):
    """
    Create a ModelRegistry resource associated to model_id
    Args:
        model_id: The ID of the model.
        project: The project ID.
        location: The region name.
    Returns:
        ModelRegistry resource.
    """

    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Initialize the Model Registry resource with the ID 'model_id'.The parent_name of Model resource can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model_registry = aiplatform.models.ModelRegistry(model=model_id)

    return model_registry


# [END aiplatform_model_registry_create_model_registry_sample]
