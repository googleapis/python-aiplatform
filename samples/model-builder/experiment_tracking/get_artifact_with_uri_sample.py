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

from google.cloud import aiplatform


#  [START aiplatform_sdk_get_artifact_with_uri_sample]
def get_artifact_with_uri_sample(
    uri: str,
    project: str,
    location: str,
):
    artifact = aiplatform.Artifact.get_with_uri(
        uri=uri, project=project, location=location
    )
    return artifact

#  [END aiplatform_sdk_get_artifact_with_uri_sample]
