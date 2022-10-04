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

# [START aiplatform_model_registry_delete_model_sample]

from google.cloud import aiplatform


def delete_model_sample(model_id: str, project: str, location: str):
    """
    Delete a Model resource.
    Args:
        model_id: The ID of the model to delete. Parent resource name of the model is also accepted.
        project: The project.
        location: The region name.
    Returns
        None.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Get the model with the ID 'model_id'. The parent_name of Model resource can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model = aiplatform.Model(model_name=model_id)

    # Delete the model.
    model.delete()


# [END aiplatform_model_registry_delete_model_sample]
