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


#  [START aiplatform_sdk_create_feature_sample]
from google.cloud import aiplatform


def create_feature_sample(
    project: str,
    location: str,
    feature_id: str,
    value_type: str,
    entity_type_id: str,
    featurestore_id: str,
):

    aiplatform.init(project=project, location=location)

    my_feature = aiplatform.Feature.create(
        feature_id=feature_id,
        value_type=value_type,
        entity_type_name=entity_type_id,
        featurestore_id=featurestore_id,
    )

    my_feature.wait()

    return my_feature


#  [END aiplatform_sdk_create_feature_sample]
