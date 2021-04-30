# Copyright 2021 Google LLC
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


#  [START aiplatform_sdk_get_model_sample]
def get_model_sample(project: str, location: str, model_name: str):

    aiplatform.init(project=project, location=location)

    model = aiplatform.Model(model_name=model_name)

    print(model.display_name)
    print(model.resource_name)
    return model


#  [END aiplatform_sdk_get_model_sample]
