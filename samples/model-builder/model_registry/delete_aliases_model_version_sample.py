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

# [START aiplatform_model_registry_delete_aliases_model_version_sample]

from typing import List

from google.cloud import aiplatform


def delete_aliases_model_version_sample(
    model_id: str,
    version_aliases: List[str],
    version_id: str,
    project: str,
    location: str,
):
    """
    Delete aliases to a model version.
    Args:
        model_id: The ID of the model.
        version_aliases: The version aliases to assign.
        version_id: The version ID of the model to assign the aliases to.
        project: The project ID.
        location: The region name.
    Returns
        None.
    """
    # Initialize the client.
    aiplatform.init(project=project, location=location)

    # Initialize the Model Registry resource with the ID 'model_id'.The parent_name of Model resource can be also
    # 'projects/<your-project-id>/locations/<your-region>/models/<your-model-id>'
    model_registry = aiplatform.models.ModelRegistry(model=model_id)

    # Remove the version aliases to the model version with the version 'version'.
    model_registry.remove_version_aliases(
        target_aliases=version_aliases, version=version_id
    )


# [END aiplatform_model_registry_delete_aliases_model_version_sample]
