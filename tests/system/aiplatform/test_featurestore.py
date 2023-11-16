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

import datetime
import logging
import pytest

from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base

import pandas as pd

_TEST_USERS_ENTITY_TYPE_GCS_SRC = (
    "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/users.avro"
)

_TEST_READ_INSTANCE_SRC = "gs://cloud-samples-data-us-central1/vertex-ai/feature-store/datasets/movie_prediction.csv"

_TEST_FEATURESTORE_ID = "movie_prediction"
_TEST_USER_ENTITY_TYPE_ID = "users"
_TEST_MOVIE_ENTITY_TYPE_ID = "movies"
_TEST_MOVIE_ENTITY_TYPE_UPDATE_LABELS = {"my_key_update": "my_value_update"}

_TEST_USER_AGE_FEATURE_ID = "age"
_TEST_USER_GENDER_FEATURE_ID = "gender"
_TEST_USER_LIKED_GENRES_FEATURE_ID = "liked_genres"

_TEST_MOVIE_TITLE_FEATURE_ID = "title"
_TEST_MOVIE_GENRES_FEATURE_ID = "genres"
_TEST_MOVIE_AVERAGE_RATING_FEATURE_ID = "average_rating"


@pytest.mark.usefixtures(
    "prepare_staging_bucket",
    "delete_staging_bucket",
    "prepare_bigquery_dataset",
    "delete_bigquery_dataset",
    "tear_down_resources",
)
class TestFeaturestore(e2e_base.TestEndToEnd):

    _temp_prefix = "temp_vertex_sdk_e2e_featurestore_test"

    def test_create_get_list_featurestore(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        featurestore_id = self._make_display_name(key=_TEST_FEATURESTORE_ID).replace(
            "-", "_"
        )[:60]
        featurestore = aiplatform.Featurestore.create(
            featurestore_id=featurestore_id, online_store_fixed_node_count=1
        )

        shared_state["resources"] = [featurestore]
        shared_state["featurestore"] = featurestore
        shared_state["featurestore_name"] = featurestore.resource_name

        get_featurestore = aiplatform.Featurestore(
            featurestore_name=featurestore.resource_name
        )
        assert featurestore.resource_name == get_featurestore.resource_name

        list_featurestores = aiplatform.Featurestore.list()
        assert get_featurestore.resource_name in [
            featurestore.resource_name for featurestore in list_featurestores
        ]

    def test_create_get_list_entity_types(self, shared_state):

        assert shared_state["featurestore"]
        assert shared_state["featurestore_name"]

        featurestore = shared_state["featurestore"]
        featurestore_name = shared_state["featurestore_name"]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
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
        assert get_movie_entity_type.resource_name in [
            entity_type.resource_name for entity_type in list_entity_types
        ]

        # Update information about the movie entity type.
        assert movie_entity_type.labels != _TEST_MOVIE_ENTITY_TYPE_UPDATE_LABELS

        movie_entity_type.update(
            labels=_TEST_MOVIE_ENTITY_TYPE_UPDATE_LABELS,
        )

        assert movie_entity_type.labels == _TEST_MOVIE_ENTITY_TYPE_UPDATE_LABELS

    def test_create_get_list_features(self, shared_state):

        assert shared_state["user_entity_type"]
        assert shared_state["user_entity_type_name"]
        user_entity_type = shared_state["user_entity_type"]
        user_entity_type_name = shared_state["user_entity_type_name"]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        # User Features
        user_age_feature = user_entity_type.create_feature(
            feature_id=_TEST_USER_AGE_FEATURE_ID, value_type="INT64"
        )
        shared_state["user_age_feature_resource_name"] = user_age_feature.resource_name
        get_user_age_feature = user_entity_type.get_feature(
            feature_id=_TEST_USER_AGE_FEATURE_ID
        )
        assert user_age_feature.resource_name == get_user_age_feature.resource_name

        user_gender_feature = aiplatform.Feature.create(
            feature_id=_TEST_USER_GENDER_FEATURE_ID,
            value_type="STRING",
            entity_type_name=user_entity_type_name,
        )
        shared_state[
            "user_gender_feature_resource_name"
        ] = user_gender_feature.resource_name

        get_user_gender_feature = aiplatform.Feature(
            feature_name=user_gender_feature.resource_name
        )
        assert (
            user_gender_feature.resource_name == get_user_gender_feature.resource_name
        )

        user_liked_genres_feature = user_entity_type.create_feature(
            feature_id=_TEST_USER_LIKED_GENRES_FEATURE_ID,
            value_type="STRING_ARRAY",
        )
        shared_state[
            "user_liked_genres_feature_resource_name"
        ] = user_liked_genres_feature.resource_name

        get_user_liked_genres_feature = aiplatform.Feature(
            feature_name=user_liked_genres_feature.resource_name
        )
        assert (
            user_liked_genres_feature.resource_name
            == get_user_liked_genres_feature.resource_name
        )

        list_user_features = user_entity_type.list_features()
        list_user_feature_resource_names = [
            feature.resource_name for feature in list_user_features
        ]

        assert get_user_age_feature.resource_name in list_user_feature_resource_names
        assert get_user_gender_feature.resource_name in list_user_feature_resource_names
        assert (
            get_user_liked_genres_feature.resource_name
            in list_user_feature_resource_names
        )

    def test_ingest_feature_values(self, shared_state, caplog):

        assert shared_state["user_entity_type"]
        user_entity_type = shared_state["user_entity_type"]

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
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
            worker_count=1,
        )

        assert "EntityType feature values imported." in caplog.text

        caplog.clear()

    def test_batch_create_features(self, shared_state):
        assert shared_state["movie_entity_type"]
        movie_entity_type = shared_state["movie_entity_type"]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        movie_feature_configs = {
            _TEST_MOVIE_TITLE_FEATURE_ID: {"value_type": "STRING"},
            _TEST_MOVIE_GENRES_FEATURE_ID: {"value_type": "STRING_ARRAY"},
            _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID: {"value_type": "DOUBLE"},
        }

        movie_entity_type.batch_create_features(feature_configs=movie_feature_configs)

        get_movie_title_feature = movie_entity_type.get_feature(
            feature_id=_TEST_MOVIE_TITLE_FEATURE_ID
        )
        get_movie_genres_feature = movie_entity_type.get_feature(
            feature_id=_TEST_MOVIE_GENRES_FEATURE_ID
        )
        get_movie_avg_rating_feature = movie_entity_type.get_feature(
            feature_id=_TEST_MOVIE_AVERAGE_RATING_FEATURE_ID
        )

        list_movie_features = movie_entity_type.list_features()
        movie_feature_resource_names = [
            feature.resource_name for feature in list_movie_features
        ]

        assert get_movie_title_feature.resource_name in movie_feature_resource_names
        assert get_movie_genres_feature.resource_name in movie_feature_resource_names
        assert (
            get_movie_avg_rating_feature.resource_name in movie_feature_resource_names
        )

    def test_ingest_feature_values_from_df_using_feature_time_column_and_online_read_multiple_entities(
        self, shared_state, caplog
    ):

        assert shared_state["movie_entity_type"]
        movie_entity_type = shared_state["movie_entity_type"]

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        read_feature_ids = ["average_rating", "title", "genres"]

        movie_entity_views_df_before_ingest = movie_entity_type.read(
            entity_ids=["movie_01", "movie_02"],
            feature_ids=read_feature_ids,
        )
        expected_data_before_ingest = [
            {
                "entity_id": "movie_01",
                "average_rating": None,
                "title": None,
                "genres": None,
            },
            {
                "entity_id": "movie_02",
                "average_rating": None,
                "title": None,
                "genres": None,
            },
        ]
        expected_movie_entity_views_df_before_ingest = pd.DataFrame(
            data=expected_data_before_ingest, columns=read_feature_ids
        )

        movie_entity_views_df_before_ingest.equals(
            expected_movie_entity_views_df_before_ingest
        )

        movies_df = pd.DataFrame(
            data=[
                {
                    "movie_id": "movie_01",
                    "average_rating": 4.9,
                    "title": "The Shawshank Redemption",
                    "genres": ["Drama"],
                    "update_time": "2021-08-20 20:44:11.094375+00:00",
                },
                {
                    "movie_id": "movie_02",
                    "average_rating": 4.2,
                    "title": "The Shining",
                    "genres": ["Horror"],
                    "update_time": "2021-08-20 20:44:11.094375+00:00",
                },
            ],
            columns=["movie_id", "average_rating", "title", "genres", "update_time"],
        )
        movies_df["update_time"] = pd.to_datetime(movies_df["update_time"], utc=True)
        feature_time_column = "update_time"

        movie_entity_type.ingest_from_df(
            feature_ids=[
                _TEST_MOVIE_TITLE_FEATURE_ID,
                _TEST_MOVIE_GENRES_FEATURE_ID,
                _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID,
            ],
            feature_time=feature_time_column,
            df_source=movies_df,
            entity_id_field="movie_id",
        )

        movie_entity_views_df_after_ingest = movie_entity_type.read(
            entity_ids=["movie_01", "movie_02"],
            feature_ids=read_feature_ids,
        )
        expected_data_after_ingest = [
            {
                "movie_id": "movie_01",
                "average_rating": 4.9,
                "title": "The Shawshank Redemption",
                "genres": ["Drama"],
            },
            {
                "movie_id": "movie_02",
                "average_rating": 4.2,
                "title": "The Shining",
                "genres": ["Horror"],
            },
        ]
        expected_movie_entity_views_df_after_ingest = pd.DataFrame(
            data=expected_data_after_ingest, columns=read_feature_ids
        )

        movie_entity_views_df_after_ingest.equals(
            expected_movie_entity_views_df_after_ingest
        )

        assert "EntityType feature values imported." in caplog.text
        caplog.clear()

    def test_ingest_feature_values_from_df_using_feature_time_datetime_and_online_read_single_entity(
        self, shared_state, caplog
    ):
        assert shared_state["movie_entity_type"]
        movie_entity_type = shared_state["movie_entity_type"]

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        movies_df = pd.DataFrame(
            data=[
                {
                    "movie_id": "movie_03",
                    "average_rating": 4.5,
                    "title": "Cinema Paradiso",
                    "genres": ["Romance"],
                },
                {
                    "movie_id": "movie_04",
                    "average_rating": 4.6,
                    "title": "The Dark Knight",
                    "genres": ["Action"],
                },
            ],
            columns=["movie_id", "average_rating", "title", "genres"],
        )

        feature_time_datetime_str = datetime.datetime.now().isoformat(
            sep=" ", timespec="milliseconds"
        )
        feature_time_datetime = datetime.datetime.strptime(
            feature_time_datetime_str, "%Y-%m-%d %H:%M:%S.%f"
        )

        movie_entity_type.ingest_from_df(
            feature_ids=[
                _TEST_MOVIE_TITLE_FEATURE_ID,
                _TEST_MOVIE_GENRES_FEATURE_ID,
                _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID,
            ],
            feature_time=feature_time_datetime,
            df_source=movies_df,
            entity_id_field="movie_id",
        )

        movie_entity_views_df_avg_rating = movie_entity_type.read(
            entity_ids="movie_04",
            feature_ids="average_rating",
        )
        expected_data_avg_rating = [
            {"movie_id": "movie_04", "average_rating": 4.6},
        ]
        expected_movie_entity_views_df_avg_rating = pd.DataFrame(
            data=expected_data_avg_rating, columns=["average_rating"]
        )

        movie_entity_views_df_avg_rating.equals(
            expected_movie_entity_views_df_avg_rating
        )

        assert "EntityType feature values imported." in caplog.text

        caplog.clear()

    def test_write_features(self, shared_state, caplog):
        assert shared_state["movie_entity_type"]
        movie_entity_type = shared_state["movie_entity_type"]

        caplog.set_level(logging.INFO)

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        # Create pandas DataFrame
        movies_df = pd.DataFrame(
            data=[
                {
                    "entity_id": "movie_01",
                    "average_rating": 4.9,
                    "title": "The Shawshank Redemption",
                    "genres": ["Drama", "Action"],
                },
                {
                    "entity_id": "movie_02",
                    "average_rating": 4.4,
                    "title": "The Shining",
                    "genres": ["Horror", "Action"],
                },
            ],
            columns=["entity_id", "average_rating", "title", "genres"],
        )
        movies_df = movies_df.set_index("entity_id")

        # Write feature values
        movie_entity_type.preview.write_feature_values(instances=movies_df)
        movie_entity_type.write_feature_values(
            instances={"movie_02": {"average_rating": 4.5}}
        )

        # Ensure writing feature values overwrites previous values
        movie_entity_df_avg_rating_genres = movie_entity_type.read(
            entity_ids="movie_02", feature_ids=["average_rating", "genres"]
        )
        expected_data_avg_rating = [
            {
                "entity_id": "movie_02",
                "average_rating": 4.5,
                "genres": ["Horror", "Action"],
            },
        ]
        expected_movie_entity_df_avg_rating_genres = pd.DataFrame(
            data=expected_data_avg_rating,
            columns=["entity_id", "average_rating", "genres"],
        )
        expected_movie_entity_df_avg_rating_genres.equals(
            movie_entity_df_avg_rating_genres
        )

        assert "EntityType feature values written." in caplog.text

        caplog.clear()

    def test_search_features(self, shared_state):

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        list_searched_features = aiplatform.Feature.search()
        assert len(list_searched_features) >= 1

    def test_batch_serve_to_df(self, shared_state, caplog):

        assert shared_state["featurestore"]
        assert shared_state["user_age_feature_resource_name"]
        assert shared_state["user_gender_feature_resource_name"]
        assert shared_state["user_liked_genres_feature_resource_name"]

        featurestore = shared_state["featurestore"]

        user_age_feature_resource_name = shared_state["user_age_feature_resource_name"]
        user_gender_feature_resource_name = shared_state[
            "user_gender_feature_resource_name"
        ]
        user_liked_genres_feature_resource_name = shared_state[
            "user_liked_genres_feature_resource_name"
        ]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        caplog.set_level(logging.INFO)

        read_instances_df = pd.DataFrame(
            data=[
                ["alice", "movie_01", "2021-09-15T08:28:14Z"],
                ["bob", "movie_02", "2021-09-15T08:28:14Z"],
                ["dav", "movie_03", "2021-09-15T08:28:14Z"],
                ["eve", "movie_04", "2021-09-15T08:28:14Z"],
                ["alice", "movie_03", "2021-09-14T09:35:15Z"],
                ["bob", "movie_04", "2020-02-14T09:35:15Z"],
            ],
            columns=["users", "movies", "timestamp"],
        )
        read_instances_df["timestamp"] = pd.to_datetime(
            read_instances_df["timestamp"], utc=True
        )

        df = featurestore.batch_serve_to_df(
            serving_feature_ids={
                _TEST_USER_ENTITY_TYPE_ID: [
                    _TEST_USER_AGE_FEATURE_ID,
                    _TEST_USER_GENDER_FEATURE_ID,
                    _TEST_USER_LIKED_GENRES_FEATURE_ID,
                ],
                _TEST_MOVIE_ENTITY_TYPE_ID: [
                    _TEST_MOVIE_TITLE_FEATURE_ID,
                    _TEST_MOVIE_GENRES_FEATURE_ID,
                    _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID,
                ],
            },
            read_instances_df=read_instances_df,
            feature_destination_fields={
                user_age_feature_resource_name: "user_age_dest",
                user_gender_feature_resource_name: "user_gender_dest",
                user_liked_genres_feature_resource_name: "user_liked_genres_dest",
            },
        )

        expected_df_columns = [
            "timestamp",
            "entity_type_users",
            "user_age_dest",
            "user_gender_dest",
            "user_liked_genres_dest",
            "entity_type_movies",
            "title",
            "genres",
            "average_rating",
        ]

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == expected_df_columns
        assert df.size == 54
        assert "Featurestore feature values served." in caplog.text

        caplog.clear()

    def test_batch_serve_to_gcs(self, shared_state, caplog):

        assert shared_state["featurestore"]
        assert shared_state["bucket"]
        assert shared_state["user_age_feature_resource_name"]
        assert shared_state["user_gender_feature_resource_name"]
        assert shared_state["user_liked_genres_feature_resource_name"]

        featurestore = shared_state["featurestore"]
        bucket_name = shared_state["staging_bucket_name"]
        user_age_feature_resource_name = shared_state["user_age_feature_resource_name"]
        user_gender_feature_resource_name = shared_state[
            "user_gender_feature_resource_name"
        ]
        user_liked_genres_feature_resource_name = shared_state[
            "user_liked_genres_feature_resource_name"
        ]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        caplog.set_level(logging.INFO)

        featurestore.batch_serve_to_gcs(
            serving_feature_ids={
                _TEST_USER_ENTITY_TYPE_ID: [
                    _TEST_USER_AGE_FEATURE_ID,
                    _TEST_USER_GENDER_FEATURE_ID,
                    _TEST_USER_LIKED_GENRES_FEATURE_ID,
                ],
                _TEST_MOVIE_ENTITY_TYPE_ID: [
                    _TEST_MOVIE_TITLE_FEATURE_ID,
                    _TEST_MOVIE_GENRES_FEATURE_ID,
                    _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID,
                ],
            },
            read_instances_uri=_TEST_READ_INSTANCE_SRC,
            feature_destination_fields={
                user_age_feature_resource_name: "user_age_dest",
                user_gender_feature_resource_name: "user_gender_dest",
                user_liked_genres_feature_resource_name: "user_liked_genres_dest",
            },
            gcs_destination_output_uri_prefix=f"gs://{bucket_name}/featurestore_test/tfrecord",
            gcs_destination_type="tfrecord",
        )
        assert "Featurestore feature values served." in caplog.text

        caplog.clear()

    def test_batch_serve_to_bq(self, shared_state, caplog):

        assert shared_state["featurestore"]
        assert shared_state["bigquery_dataset"]
        assert shared_state["user_age_feature_resource_name"]
        assert shared_state["user_gender_feature_resource_name"]
        assert shared_state["user_liked_genres_feature_resource_name"]

        featurestore = shared_state["featurestore"]
        bigquery_dataset_id = shared_state["bigquery_dataset_id"]
        user_age_feature_resource_name = shared_state["user_age_feature_resource_name"]
        user_gender_feature_resource_name = shared_state[
            "user_gender_feature_resource_name"
        ]
        user_liked_genres_feature_resource_name = shared_state[
            "user_liked_genres_feature_resource_name"
        ]

        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
        )

        caplog.set_level(logging.INFO)

        featurestore.batch_serve_to_bq(
            serving_feature_ids={
                _TEST_USER_ENTITY_TYPE_ID: [
                    _TEST_USER_AGE_FEATURE_ID,
                    _TEST_USER_GENDER_FEATURE_ID,
                    _TEST_USER_LIKED_GENRES_FEATURE_ID,
                ],
                _TEST_MOVIE_ENTITY_TYPE_ID: [
                    _TEST_MOVIE_TITLE_FEATURE_ID,
                    _TEST_MOVIE_GENRES_FEATURE_ID,
                    _TEST_MOVIE_AVERAGE_RATING_FEATURE_ID,
                ],
            },
            read_instances_uri=_TEST_READ_INSTANCE_SRC,
            feature_destination_fields={
                user_age_feature_resource_name: "user_age_dest",
                user_gender_feature_resource_name: "user_gender_dest",
                user_liked_genres_feature_resource_name: "user_liked_genres_dest",
            },
            bq_destination_output_uri=f"bq://{bigquery_dataset_id}.test_table",
        )

        assert "Featurestore feature values served." in caplog.text
        caplog.clear()

    def test_online_reads(self, shared_state):
        assert shared_state["user_entity_type"]
        assert shared_state["movie_entity_type"]

        user_entity_type = shared_state["user_entity_type"]
        movie_entity_type = shared_state["movie_entity_type"]

        user_entity_views = user_entity_type.read(entity_ids="alice")
        assert isinstance(user_entity_views, pd.DataFrame)

        movie_entity_views = movie_entity_type.read(
            entity_ids=["movie_01", "movie_04"],
            feature_ids=[_TEST_MOVIE_TITLE_FEATURE_ID, _TEST_MOVIE_GENRES_FEATURE_ID],
        )
        assert isinstance(movie_entity_views, pd.DataFrame)

        movie_entity_views = movie_entity_type.read(
            entity_ids="movie_01",
            feature_ids=[_TEST_MOVIE_TITLE_FEATURE_ID, _TEST_MOVIE_GENRES_FEATURE_ID],
        )
        assert isinstance(movie_entity_views, pd.DataFrame)
