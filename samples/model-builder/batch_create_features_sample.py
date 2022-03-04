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


#  [START aiplatform_sdk_batch_create_features_sample]
from google.cloud import aiplatform


def batch_create_features_sample(
    project: str,
    location: str,
    entity_type_id: str,
    featurestore_id: str,
    sync: bool = True,
):

    aiplatform.init(project=project, location=location)

    my_entity_type = aiplatform.featurestore.EntityType(
        entity_type_name=entity_type_id, featurestore_id=featurestore_id
    )

    FEATURE_CONFIGS = {
        "age": {"value_type": "INT64", "description": "User age"},
        "gender": {"value_type": "STRING", "description": "User gender"},
        "liked_genres": {
            "value_type": "STRING_ARRAY",
            "description": "An array of genres this user liked",
        },
    }

    my_entity_type.batch_create_features(feature_configs=FEATURE_CONFIGS, sync=sync)


#  [END aiplatform_sdk_batch_create_features_sample]
