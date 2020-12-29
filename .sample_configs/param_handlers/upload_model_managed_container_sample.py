# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

def make_parent(parent: str) -> str:
    # Sample function parameter parent in upload_model_using_managed_container_sample
    parent = parent

    return parent


def make_model(
    display_name: str, container_spec_image_uri: str, artifact_uri: str
) -> google.cloud.aiplatform_v1beta1.types.model.Model:

    container_spec = {"image_uri": container_spec_image_uri}

    model = {
        "display_name": display_name,
        # The artifact_uri should be the path to a GCS directory containing
        # saved model artifacts.  The bucket must be accessible for the
        # project's AI Platform service account and in the same region as
        # the api endpoint.
        "artifact_uri": artifact_uri,
        "container_spec": container_spec,
    }

    return model
