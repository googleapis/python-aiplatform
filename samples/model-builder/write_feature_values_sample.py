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

# Serve feature values from a single entity for a particular entity type.
# See https://cloud.google.com/vertex-ai/docs/featurestore/setup before running
# the code snippet

# [START aiplatform_write_feature_values_sample]
from google.cloud import aiplatform


def write_feature_values_sample(
    project: str, location: str, entity_type_id: str, featurestore_id: str
):

    aiplatform.init(project=project, location=location)

    my_entity_type = aiplatform.featurestore.EntityType(
        entity_type_name=entity_type_id, featurestore_id=featurestore_id
    )

    my_data = {
        "movie_01": {
            "title": "The Shawshank Redemption",
            "average_rating": 4.7,
            "genre": "Drama",
        },
    }

    my_entity_type.write_feature_values(instances=my_data)


# [END aiplatform_write_feature_values_sample]
