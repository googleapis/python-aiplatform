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

#  [START aiplatform_sdk_featurestore_batch_serve_feature_values_to_df_sample]
def featurestore_batch_serve_feature_values_to_df_sample(
    project: str, location: str, featurestore_name: str,
):
    aiplatform.init(project=project, location=location)

    fs = aiplatform.Featurestore(featurestore_name=featurestore_name)

    read_instances_df = pd.DataFrame(
        data=[
            ["alice", "movie_01", "2021-09-15T08:28:14Z"],
            ["bob", "movie_02", "2021-09-15T08:28:14Z"],
            ["dav", "movie_03", "2021-09-15T08:28:14Z"],
            ["eve", "movie_04", "2021-09-15T08:28:14Z"],
            ["alice", "movie_03", "2021-09-14T09:35:15Z"],
            ["bob", "movie_04", "2020-02-14T09:35:15Z"],
        ],
        columns=["users_entity_type_id", "movies_entity_type_id", "timestamp"],
    )
    read_instances_df = read_instances_df.astype({"timestamp": "datetime64"})

    df = fs.batch_serve_to_df(
        serving_feature_ids={
            "users_entity_type_id": [
                "user_age_feature_id",
                "user_gender_feature_id",
                "user_liked_genres_feature_id",
            ],
            "movies_entity_type_id": [
                "movie_title_feature_id",
                "movie_genres_feature_id",
                "movie_average_rating_feature_id",
            ],
        },
        read_instances_df=read_instances_df,
    )

    return df


#  [END aiplatform_sdk_featurestore_batch_serve_feature_values_to_df_sample]
