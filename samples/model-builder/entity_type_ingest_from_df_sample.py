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


import pandas as pd

from google.cloud import aiplatform

#  [START aiplatform_sdk_entity_type_ingest_feature_values_from_df_sample]
def entity_type_ingest_feature_values_from_df_with_feature_time_field_sample(
    project: str, location: str, entity_type_name: str,
):
    aiplatform.init(project=project, location=location)

    et = aiplatform.EntityType(entity_type_name=entity_type_name)

    df_source = pd.DataFrame(
        data=[
            {
                "movie_id": "movie_01",
                "average_rating": 4.9,
                "title": "The Shawshank Redemption",
                "genres": "Drama",
                "update_time": "2021-08-20 20:44:11.094375+00:00",
            },
            {
                "movie_id": "movie_02",
                "average_rating": 4.2,
                "title": "The Shining",
                "genres": "Horror",
                "update_time": "2021-08-20 20:44:11.094375+00:00",
            },
        ],
        columns=["movie_id", "average_rating", "title", "genres", "update_time"],
    )

    et.ingest_from_df(
        feature_ids=["movid_id", "average_rating", "title", "genres"],
        feature_time="update_time",
        df_source=df_source,
        entity_id_field="movie_id",
    )

    return et


#  [END aiplatform_sdk_entity_type_ingest_feature_values_from_df_sample]
