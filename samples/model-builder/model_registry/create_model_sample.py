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

# [START aiplatform_model_registry_create_default_model_sample]

from google.cloud import aiplatform

def create_default_model_sample(
        model_id: str,
        project: str,
        location: str
):
    """
    Creates a Model to represent an existing model with alias 'default'.
    Args:
        model_id: The ID of the model to create. Parent resource name of the model is also accepted.
        project: The project.
        location: The location.
    Returns:
        The new version of the model.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Initialize the model with the ID 'model_id'. The parent_name of create method can be also
    #     # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    default_model = aiplatform.Model(model_name=model_id)

    return default_model

# [END aiplatform_model_registry_create_default_model_sample]