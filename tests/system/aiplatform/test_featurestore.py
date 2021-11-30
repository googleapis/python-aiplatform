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

from google.cloud import aiplatform
from google.cloud.aiplatform import _featurestores as featurestores
from tests.system.aiplatform import e2e_base

_USERS_ENTITY_TYPE_SRC = (
    "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/users.avro"
)
_MOVIES_ENTITY_TYPE_SRC = (
    "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/movies.avro"
)


class TestFeaturestore(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertex-sdk-e2e-test"

    def _make_resource_id(self, key: str) -> str:
        """Helper method to make unique resource_ids.

        Args:
            key (str): Required. Identifier for the resource id.
        Returns:
            Unique resource id.
        """
        return self._make_display_name(key=key).replace("-", "_")[:60]

    def test_end_to_end(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT, location=e2e_base._LOCATION,
        )

        # Featurestore
        featurestore_id = self._make_resource_id(key="movie_prediction")
        featurestore = featurestores.Featurestore.create(
            featurestore_id=featurestore_id
        )
        shared_state["resources"] = [featurestore]

        get_featurestore = featurestores.Featurestore(
            featurestore_name=featurestore.resource_name
        )
        assert featurestore.resource_name == get_featurestore.resource_name

        list_featurestores = featurestores.Featurestore.list()
        assert len(list_featurestores) > 0

        # EntityType

        # User EntityType
        user_entity_type_id = self._make_resource_id(key="users")
        user_entity_type = featurestore.create_entity_type(
            entity_type_id=user_entity_type_id
        )
        get_user_entity_type = featurestore.get_entity_type(
            entity_type_name=user_entity_type.resource_name
        )
        assert user_entity_type.resource_name == get_user_entity_type.resource_name

        # Movie EntityType
        movie_entity_type_id = self._make_resource_id(key="movies")
        movie_entity_type = featurestore.create_entity_type(
            entity_type_id=movie_entity_type_id
        )
        get_movie_entity_type = featurestore.get_entity_type(
            entity_type_name=movie_entity_type.resource_name
        )
        assert movie_entity_type.resource_name == get_movie_entity_type.resource_name

        list_entity_types = featurestore.list_entity_types()
        assert len(list_entity_types) > 0

        # Feature

        # User Features
        age_feature_id = self._make_resource_id(key="age")
        age_feature = user_entity_type.create_feature(
            feature_id=age_feature_id, value_type="INT64"
        )

        get_age_feature = user_entity_type.get_feature(
            feature_name=age_feature.resource_name
        )
        assert age_feature.resource_name == get_age_feature.resource_name

        gender_feature_id = self._make_resource_id(key="gender")
        liked_genres_feature_id = self._make_resource_id(key="liked_genres")
        user_feature_configs = {
            gender_feature_id: {"value_type": "STRING"},
            liked_genres_feature_id: {"value_type": "STRING_ARRAY"},
        }
        user_entity_type.batch_create_features(feature_configs=user_feature_configs)

        list_user_features = user_entity_type.list_features()
        assert len(list_user_features) > 0

        user_entity_type.ingest_from_gcs(
            gcs_source_uris=_USERS_ENTITY_TYPE_SRC,
            gcs_source_type="avro",
            feature_ids=[age_feature_id, gender_feature_id, liked_genres_feature_id],
        )

        # Movie Features

        title_feature_id = self._make_resource_id(key="title")
        genres_feature_id = self._make_resource_id(key="genres")
        average_rating_id = self._make_resource_id(key="average_rating")
        movie_feature_configs = {
            title_feature_id: {"value_type": "STRING"},
            genres_feature_id: {"value_type": "STRING"},
            average_rating_id: {"value_type": "DOUBLE"},
        }
        movie_entity_type.ingest_from_gcs(
            gcs_source_uris=_MOVIES_ENTITY_TYPE_SRC,
            gcs_source_type="avro",
            feature_ids=[title_feature_id, genres_feature_id, average_rating_id],
            feature_configs=movie_feature_configs,
        )

        list_movie_features = movie_entity_type.list_features()
        assert len(list_movie_features) > 0

        user_entity_type.ingest_from_gcs(
            gcs_source_uris=_USERS_ENTITY_TYPE_SRC,
            gcs_source_type="avro",
            feature_ids=[age_feature_id, gender_feature_id, liked_genres_feature_id],
        )

        # All Features
        list_searched_features = featurestores.Feature.search()
        assert len(list_searched_features) >= 1
