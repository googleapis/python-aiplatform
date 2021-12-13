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

    def test_create_get_list_featurestore(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        base_list_featurestores = len(aiplatform.Featurestore.list())
        shared_state["base_list_searched_features"] = len(aiplatform.Feature.search())

        featurestore_id = self._make_display_name(key=_TEST_FEATURESTORE_ID).replace(
            "-", "_"
        )[:60]
        featurestore = aiplatform.Featurestore.create(featurestore_id=featurestore_id)

        shared_state["resources"] = [featurestore]
        shared_state["featurestore"] = featurestore
        shared_state["featurestore_name"] = featurestore.resource_name

        get_featurestore = aiplatform.Featurestore(
            featurestore_name=featurestore.resource_name
        )
        assert featurestore.resource_name == get_featurestore.resource_name

        list_featurestores = aiplatform.Featurestore.list()
        assert (len(list_featurestores) - base_list_featurestores) == 1

    def test_create_get_list_entity_types(self, shared_state):

        assert shared_state["featurestore"]
        assert shared_state["featurestore_name"]

        featurestore = shared_state["featurestore"]
        featurestore_name = shared_state["featurestore_name"]

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        # Users
        user_entity_type = featurestore.create_entity_type(
            entity_type_id=_TEST_USER_ENTITY_TYPE_ID
        )
        shared_state["user_entity_type"] = user_entity_type
        shared_state["user_entity_type_name"] = user_entity_type.resource_name

        get_user_entity_type = featurestore.get_entity_type(
            entity_type_id=_TEST_USER_ENTITY_TYPE_ID
        )
        assert user_entity_type.resource_name == get_user_entity_type.resource_name

        # Movies
        movie_entity_type = aiplatform.EntityType.create(
            entity_type_id=_TEST_MOVIE_ENTITY_TYPE_ID,
            featurestore_name=featurestore_name,
        )
        shared_state["movie_entity_type"] = movie_entity_type
        shared_state["movie_entity_type_name"] = movie_entity_type.resource_name

        get_movie_entity_type = aiplatform.EntityType(
            entity_type_name=movie_entity_type.resource_name
        )
        assert movie_entity_type.resource_name == get_movie_entity_type.resource_name

        list_entity_types = aiplatform.EntityType.list(
            featurestore_name=featurestore_name
        )
        assert len(list_entity_types) == 2

    def test_create_get_list_features(self, shared_state):

        assert shared_state["user_entity_type"]
        assert shared_state["user_entity_type_name"]
        user_entity_type = shared_state["user_entity_type"]
        user_entity_type_name = shared_state["user_entity_type_name"]

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        list_user_features = user_entity_type.list_features()
        assert len(list_user_features) == 0

        # User Features
        user_age_feature = user_entity_type.create_feature(
            feature_id=_TEST_USER_AGE_FEATURE_ID, value_type="INT64"
        )

        get_user_age_feature = user_entity_type.get_feature(
            feature_id=_TEST_USER_AGE_FEATURE_ID
        )
        assert user_age_feature.resource_name == get_user_age_feature.resource_name

        user_gender_feature = aiplatform.Feature.create(
            feature_id=_TEST_USER_GENDER_FEATURE_ID,
            value_type="STRING",
            entity_type_name=user_entity_type_name,
        )

        get_user_gender_feature = aiplatform.Feature(
            feature_name=user_gender_feature.resource_name
        )
        assert (
            user_gender_feature.resource_name == get_user_gender_feature.resource_name
        )

        user_liked_genres_feature = user_entity_type.create_feature(
            feature_id=_TEST_USER_LIKED_GENRES_FEATURE_ID, value_type="STRING_ARRAY",
        )

        get_user_liked_genres_feature = aiplatform.Feature(
            feature_name=user_liked_genres_feature.resource_name
        )
        assert (
            user_liked_genres_feature.resource_name
            == get_user_liked_genres_feature.resource_name
        )

        list_user_features = user_entity_type.list_features()
        assert len(list_user_features) == 3

    def test_ingest_feature_values(self, shared_state, caplog):

        assert shared_state["user_entity_type"]
        user_entity_type = shared_state["user_entity_type"]

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        user_entity_type.ingest_from_gcs(
            feature_ids=[
                _TEST_USER_AGE_FEATURE_ID,
                _TEST_USER_GENDER_FEATURE_ID,
                _TEST_USER_LIKED_GENRES_FEATURE_ID,
            ],
            feature_time="update_time",
            gcs_source_uris=_TEST_USERS_ENTITY_TYPE_GCS_SRC,
            gcs_source_type="avro",
            entity_id_field="user_id",
            worker_count=2,
        )

        assert "EntityType feature values imported." in caplog.text

        caplog.clear()

    def test_ingest_feature_values_with_config(self, shared_state, caplog):

        assert shared_state["movie_entity_type"]
        movie_entity_type = shared_state["movie_entity_type"]

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        movie_feature_configs = {
            _TEST_MOVIE_TITLE_FEATURE_ID: {"value_type": "STRING"},
            _TEST_MOVIE_GENRES_FEATURE_ID: {"value_type": "STRING"},
            _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID: {"value_type": "DOUBLE"},
        }

        list_movie_features = movie_entity_type.list_features()
        assert len(list_movie_features) == 0

        movie_entity_type.batch_create_features(feature_configs=movie_feature_configs)

        movie_entity_type.ingest_from_gcs(
            feature_ids=[
                _TEST_MOVIE_TITLE_FEATURE_ID,
                _TEST_MOVIE_GENRES_FEATURE_ID,
                _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID,
            ],
            feature_time="update_time",
            gcs_source_uris=_TEST_MOVIES_ENTITY_TYPE_GCS_SRC,
            gcs_source_type="avro",
            entity_id_field="movie_id",
            worker_count=2,
        )

        list_movie_features = movie_entity_type.list_features()
        assert len(list_movie_features) == 3

        assert "EntityType feature values imported." in caplog.text

        caplog.clear()

    def test_search_features(self, shared_state):

        assert shared_state["base_list_searched_features"] is not None

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        list_searched_features = aiplatform.Feature.search()
        assert (
            len(list_searched_features) - shared_state["base_list_searched_features"]
        ) == 6
