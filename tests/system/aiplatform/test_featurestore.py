# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

import logging

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base

_TEST_USERS_ENTITY_TYPE_GCS_SRC = (
    "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/users.avro"
)
_TEST_MOVIES_ENTITY_TYPE_GCS_SRC = (
    "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/movies.avro"
)

_TEST_FEATURESTORE_ID = "movie_prediction"
_TEST_USER_ENTITY_TYPE_ID = "users"
_TEST_MOVIE_ENTITY_TYPE_ID = "movies"

_TEST_USER_AGE_FEATURE_ID = "age"
_TEST_USER_GENDER_FEATURE_ID = "gender"
_TEST_USER_LIKED_GENRES_FEATURE_ID = "liked_genres"

_TEST_MOVIE_TITLE_FEATURE_ID = "title"
_TEST_MOVIE_GENRES_FEATURE_ID = "genres"
_TEST_MOVIE_AVERAGE_RATING_FEATURE_ID = "average_rating"


class TestFeaturestore(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_featurestore_test"

    def test_end_to_end(self, shared_state, caplog):

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        base_list_featurestores = len(aiplatform.Featurestore.list())
        base_list_searched_features = len(aiplatform.Feature.search())

        # Featurestore
        featurestore_id = self._make_display_name(key=_TEST_FEATURESTORE_ID).replace(
            "-", "_"
        )[:60]
        featurestore = aiplatform.Featurestore.create(featurestore_id=featurestore_id)
        shared_state["resources"] = [featurestore]

        get_featurestore = aiplatform.Featurestore(
            featurestore_name=featurestore.resource_name
        )
        assert featurestore.resource_name == get_featurestore.resource_name

        list_featurestores = aiplatform.Featurestore.list()
        assert len(list_featurestores) - base_list_featurestores == 1

        # EntityType

        # User EntityType
        user_entity_type_id = _TEST_USER_ENTITY_TYPE_ID
        user_entity_type = featurestore.create_entity_type(
            entity_type_id=user_entity_type_id
        )

        get_user_entity_type = featurestore.get_entity_type(
            entity_type_id=user_entity_type_id
        )
        assert user_entity_type.resource_name == get_user_entity_type.resource_name

        # Movie EntityType
        movie_entity_type_id = _TEST_MOVIE_ENTITY_TYPE_ID
        movie_entity_type = aiplatform.EntityType.create(
            entity_type_id=movie_entity_type_id,
            featurestore_name=featurestore.resource_name,
        )

        get_movie_entity_type = aiplatform.EntityType(
            entity_type_name=movie_entity_type.resource_name
        )
        assert movie_entity_type.resource_name == get_movie_entity_type.resource_name

        list_entity_types = aiplatform.EntityType.list(
            featurestore_name=featurestore.resource_name
        )
        assert len(list_entity_types) == 2

        # Feature

        # User Features
        user_age_feature_id = _TEST_USER_AGE_FEATURE_ID
        user_age_feature = user_entity_type.create_feature(
            feature_id=user_age_feature_id, value_type="INT64"
        )

        get_user_age_feature = user_entity_type.get_feature(
            feature_id=user_age_feature_id
        )
        assert user_age_feature.resource_name == get_user_age_feature.resource_name

        user_gender_feature_id = _TEST_USER_GENDER_FEATURE_ID
        user_gender_feature = aiplatform.Feature.create(
            feature_id=user_gender_feature_id,
            value_type="STRING",
            entity_type_name=user_entity_type.resource_name,
        )

        get_user_gender_feature = aiplatform.Feature(
            feature_name=user_gender_feature.resource_name
        )
        assert (
            user_gender_feature.resource_name == get_user_gender_feature.resource_name
        )

        user_liked_genres_feature_id = _TEST_USER_LIKED_GENRES_FEATURE_ID
        user_feature_configs = {
            user_liked_genres_feature_id: {"value_type": "STRING_ARRAY"},
        }
        user_entity_type.batch_create_features(feature_configs=user_feature_configs)

        list_user_features = user_entity_type.list_features()
        assert len(list_user_features) == 3

        user_entity_type = user_entity_type.ingest_from_gcs(
            feature_ids=[
                user_age_feature_id,
                user_gender_feature_id,
                user_liked_genres_feature_id,
            ],
            feature_time="update_time",
            gcs_source_uris=_TEST_USERS_ENTITY_TYPE_GCS_SRC,
            gcs_source_type="avro",
            entity_id_field="user_id",
            worker_count=2,
            sync=False,
        )

        movie_title_feature_id = _TEST_MOVIE_TITLE_FEATURE_ID
        movie_genres_feature_id = _TEST_MOVIE_GENRES_FEATURE_ID
        movie_average_rating_id = _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID

        movie_feature_configs = {
            movie_title_feature_id: {"value_type": "STRING"},
            movie_genres_feature_id: {"value_type": "STRING"},
            movie_average_rating_id: {"value_type": "DOUBLE"},
        }

        list_movie_features = movie_entity_type.list_features()
        assert len(list_movie_features) == 0

        movie_entity_type = movie_entity_type.ingest_from_gcs(
            feature_ids=[
                movie_title_feature_id,
                movie_genres_feature_id,
                movie_average_rating_id,
            ],
            feature_time="update_time",
            gcs_source_uris=_TEST_MOVIES_ENTITY_TYPE_GCS_SRC,
            gcs_source_type="avro",
            entity_id_field="movie_id",
            worker_count=2,
            batch_create_feature_configs=movie_feature_configs,
            sync=False,
        )

        user_entity_type.wait()
        movie_entity_type.wait()

        assert "EntityType feature values imported." in caplog.text

        list_movie_features = movie_entity_type.list_features()
        assert len(list_movie_features) == 3

        list_searched_features = aiplatform.Feature.search()
        assert len(list_searched_features) - base_list_searched_features == 6

        caplog.clear()
