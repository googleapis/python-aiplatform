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


#  [START aiplatform_sdk_create_entity_type_sample]
from google.cloud import aiplatform


def create_entity_type_sample(
    project: str,
    location: str,
    entity_type_id: str,
    featurestore_name: str,
):

    aiplatform.init(project=project, location=location)

    my_entity_type = aiplatform.EntityType.create(
        entity_type_id=entity_type_id, featurestore_name=featurestore_name
    )

    my_entity_type.wait()

    return my_entity_type


#  [END aiplatform_sdk_create_entity_type_sample]
