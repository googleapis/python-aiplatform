# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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

from typing import List, Generator
import uuid
import logging
import bigframes.pandas as bpd
import pandas as pd
import pytest

from tests.system.aiplatform import e2e_base
import vertexai
from vertexai.resources.preview.feature_store import (
    offline_store,
    FeatureGroup,
    Feature,
    utils as fs_utils,
)


# Constants used in tests
ENTITY_ID_COL = "customer_id"

# Data used to construct customer entity DF
ENTITY_DF_TS_COL = "timestamp"
ENTITY_DF_COLUMNS = ["customer_id", "neg_id", ENTITY_DF_TS_COL]

CUSTOMER_1_OLD_ENTITY_DF_TIMESTAMP = pd.Timestamp("2023-12-12T12:23")
CUSTOMER_1_OLD_ENTITY_DF_ENTRY = ["customer1", -1, CUSTOMER_1_OLD_ENTITY_DF_TIMESTAMP]
CUSTOMER_2_OLD_ENTITY_DF_TIMESTAMP = pd.Timestamp("2023-12-12T13:13")
CUSTOMER_2_OLD_ENTITY_DF_ENTRY = ["customer2", -2, CUSTOMER_2_OLD_ENTITY_DF_TIMESTAMP]

CUSTOMER_1_NEW_ENTITY_DF_TIMESTAMP = pd.Timestamp("2025-01-01T17:00")
CUSTOMER_1_NEW_ENTITY_DF_ENTRY = ["customer1", -1, CUSTOMER_1_NEW_ENTITY_DF_TIMESTAMP]
CUSTOMER_2_NEW_ENTITY_DF_TIMESTAMP = pd.Timestamp("2025-12-12T18:22")
CUSTOMER_2_NEW_ENTITY_DF_ENTRY = ["customer2", -2, CUSTOMER_2_NEW_ENTITY_DF_TIMESTAMP]

# Data used to construct expected output of fetch historical feature values
OUTPUT_DF_COLUMNS = [
    "customer_id",
    "neg_id",
    "customer_number",
    "customer_value",
    "customer_truth",
    ENTITY_DF_TS_COL,
]
CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT = [
    "customer1",
    -1,
    1,
    2,
    False,
    CUSTOMER_1_OLD_ENTITY_DF_TIMESTAMP,
]
CUSTOMER_2_OLD_DATA_EXPECTED_OUTPUT = [
    "customer2",
    -2,
    2,
    4,
    False,
    CUSTOMER_2_OLD_ENTITY_DF_TIMESTAMP,
]
CUSTOMER_1_NEW_DATA_EXPECTED_OUTPUT = [
    "customer1",
    -1,
    1,
    1,
    True,
    CUSTOMER_1_NEW_ENTITY_DF_TIMESTAMP,
]
CUSTOMER_2_NEW_DATA_EXPECTED_OUTPUT = [
    "customer2",
    -2,
    2,
    2,
    True,
    CUSTOMER_2_NEW_ENTITY_DF_TIMESTAMP,
]


def df_eq(expected, actual):
    assert expected.shape[0] != 0
    assert expected.shape[1] != 0
    assert (
        expected.shape == actual.shape
    ), f"Shapes are different.\n * entity df: {expected}\n * rsp df: {actual}"

    if isinstance(actual, bpd.DataFrame):
        actual = actual.to_pandas()
    actual = actual.sort_values(
        by="customer_id",
        key=lambda s: s.str.lstrip("customer").astype(int),
    )
    # Row by row comparison.
    for i in range(0, expected.shape[0]):
        assert expected.iloc[i].equals(actual.iloc[i]), (
            f"Row {i} is different:\n * expected row: {expected.iloc[i]}\n *  rsp df row: {actual.iloc[i]}"
            + f"\n\n\n\nexpected: {expected}\n-----\nactual: {actual}"
        )


def test_df_eq_good():
    expected_df = pd.DataFrame(
        data=[
            CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT,
            CUSTOMER_2_OLD_DATA_EXPECTED_OUTPUT,
        ],
        columns=OUTPUT_DF_COLUMNS,
    )
    actual_df = pd.DataFrame(
        data=[
            CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT,
            CUSTOMER_2_OLD_DATA_EXPECTED_OUTPUT,
        ],
        columns=OUTPUT_DF_COLUMNS,
    )

    df_eq(expected_df, actual_df)


def test_df_not_eq_raises_error():
    with pytest.raises(AssertionError, match=r"Row 1 is different.*"):
        expected_df = pd.DataFrame(
            data=[
                CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT,
                CUSTOMER_2_OLD_DATA_EXPECTED_OUTPUT,
            ],
            columns=OUTPUT_DF_COLUMNS,
        )
        actual_df = pd.DataFrame(
            data=[
                CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT,
                CUSTOMER_2_NEW_DATA_EXPECTED_OUTPUT,
            ],
            columns=OUTPUT_DF_COLUMNS,
        )

        df_eq(expected_df, actual_df)


@pytest.mark.usefixtures(
    "delete_bigquery_dataset",
    "tear_down_resources",
)
class TestOfflineStore(e2e_base.TestEndToEnd):
    _temp_prefix = "temp-vertex-fs-offline-store"

    @pytest.fixture(scope="class")
    def project(self):
        yield e2e_base._PROJECT

    @pytest.fixture(scope="class")
    def location(self):
        yield e2e_base._LOCATION

    @pytest.fixture(autouse=True)
    def vertexai_init(self, project, location):
        vertexai.init(
            project=project,
            location=location,
        )
        yield

    @pytest.fixture(scope="class")
    def bq_dataset(self, prepare_bigquery_dataset, shared_state):
        yield shared_state["bigquery_dataset_id"]

    @pytest.fixture(scope="class")
    def bq_client(self, prepare_bigquery_dataset, shared_state):
        yield shared_state["bigquery_client"]

    @pytest.fixture(scope="class")
    def bq_table(self, bq_dataset, bq_client):
        query_create_customer_table_with_new_features = f"""CREATE OR REPLACE TABLE `{bq_dataset}.customer_features` AS
(SELECT
  CONCAT("customer", a) AS customer_id,
  a AS customer_number,
  a AS customer_value,
  TRUE AS customer_truth,
  TIMESTAMP('2024-01-01 23:23:00') AS feature_timestamp,
  FROM UNNEST(GENERATE_ARRAY(1, 1000)) AS a);
"""

        query_append_to_customer_table_with_old_features = f"""INSERT `{bq_dataset}.customer_features` (customer_id, customer_number, customer_value, customer_truth, feature_timestamp)
(SELECT
  CONCAT("customer", a) AS customer_id,
  a AS customer_number,
  a * 2 AS customer_value,
  FALSE AS customer_truth,
  TIMESTAMP('2023-09-01T13:00:00') AS feature_timestamp,
  FROM UNNEST(GENERATE_ARRAY(1, 500)) AS a);
"""
        bq_client.query_and_wait(query_create_customer_table_with_new_features)
        bq_client.query_and_wait(query_append_to_customer_table_with_old_features)
        yield f"{bq_dataset}.customer_features"

    @pytest.fixture(scope="class")
    def customer_fg(
        self, bq_table, shared_state
    ) -> Generator[FeatureGroup, None, None]:
        logging.info(f"creating FG using bq://{bq_table}")
        fg = FeatureGroup.create(
            f"customer_fg_{uuid.uuid4()}".replace("-", "_"),
            fs_utils.FeatureGroupBigQuerySource(
                uri=f"bq://{bq_table}",
                entity_id_columns=["customer_id"],
            ),
        )
        shared_state.setdefault("resources", [])
        shared_state["resources"].append(fg)
        yield fg

    @pytest.fixture(scope="class")
    def customer_features(self, customer_fg) -> Generator[List[Feature], None, None]:
        features = []
        features.append(customer_fg.create_feature("customer_number"))
        features.append(customer_fg.create_feature("customer_value"))
        features.append(customer_fg.create_feature("customer_truth"))
        yield features

    @pytest.fixture(scope="class")
    def customer_features_as_str_list(
        self, customer_fg, customer_features
    ) -> Generator[List[str], None, None]:
        str_feature_list: List[str] = []
        for feature in customer_features:
            str_feature_list.append(f"{customer_fg.name}.{feature.name}")
        yield str_feature_list

    def test_entity_df_no_timestamp_column_raises_error(self):
        entity_df = pd.DataFrame(
            data=[
                ["customer1", 1, "not-a-real-timestamp"],
                ["customer2", 2, "also-not-a-real-timestamp"],
            ],
            columns=ENTITY_DF_COLUMNS,
        )
        entity_df = bpd.DataFrame(entity_df)

        with pytest.raises(ValueError) as excinfo:
            offline_store.fetch_historical_feature_values(
                entity_df=entity_df,
                features=["fake.feature"],
            )

        assert (
            'No timestamp column ("datetime" dtype) found in entity DataFrame.'
            == str(excinfo.value)
        )

    def test_entity_df_too_many_timestamp_columns_raises_error(self):
        entity_df = pd.DataFrame(
            data=[
                [
                    "customer1",
                    pd.Timestamp("2023-12-12T11:11"),
                    pd.Timestamp("2024-12-12T11:11"),
                ],
                [
                    "customer2",
                    pd.Timestamp("2023-12-12T12:12"),
                    pd.Timestamp("2024-12-12T2:12"),
                ],
            ],
            columns=["id", "ts1", "ts2"],
        )
        entity_df = bpd.DataFrame(entity_df)

        with pytest.raises(ValueError) as excinfo:
            offline_store.fetch_historical_feature_values(
                entity_df=entity_df,
                features=["fake.feature"],
            )

        assert str(excinfo.value) == (
            'Multiple timestamp columns ("datetime" dtype) found in entity DataFrame. '
            "Only one timestamp column is allowed. "
            "Timestamp columns: ts1, ts2"
        )

    def test_with_features_old_data(self, customer_features_as_str_list):
        entity_df = pd.DataFrame(
            [
                CUSTOMER_1_OLD_ENTITY_DF_ENTRY,
                CUSTOMER_2_OLD_ENTITY_DF_ENTRY,
            ],
            columns=ENTITY_DF_COLUMNS,
        )

        df = offline_store.fetch_historical_feature_values(
            entity_df=entity_df,
            features=customer_features_as_str_list,
        )

        expected_df = pd.DataFrame(
            data=[
                CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT,
                CUSTOMER_2_OLD_DATA_EXPECTED_OUTPUT,
            ],
            columns=OUTPUT_DF_COLUMNS,
        )
        df_eq(expected_df, df)

    def test_with_features_new_data(self, customer_features_as_str_list):
        entity_df = pd.DataFrame(
            [
                CUSTOMER_1_NEW_ENTITY_DF_ENTRY,
                CUSTOMER_2_NEW_ENTITY_DF_ENTRY,
            ],
            columns=ENTITY_DF_COLUMNS,
        )

        df = offline_store.fetch_historical_feature_values(
            entity_df=entity_df,
            features=customer_features_as_str_list,
        )

        expected_df = pd.DataFrame(
            data=[
                CUSTOMER_1_NEW_DATA_EXPECTED_OUTPUT,
                CUSTOMER_2_NEW_DATA_EXPECTED_OUTPUT,
            ],
            columns=OUTPUT_DF_COLUMNS,
        )
        df_eq(expected_df, df)

    def test_with_features_mixed1_data(self, customer_features_as_str_list):
        entity_df = pd.DataFrame(
            [
                CUSTOMER_1_NEW_ENTITY_DF_ENTRY,
                CUSTOMER_2_OLD_ENTITY_DF_ENTRY,
            ],
            columns=ENTITY_DF_COLUMNS,
        )

        df = offline_store.fetch_historical_feature_values(
            entity_df=entity_df,
            features=customer_features_as_str_list,
        )

        expected_df = pd.DataFrame(
            data=[
                CUSTOMER_1_NEW_DATA_EXPECTED_OUTPUT,
                CUSTOMER_2_OLD_DATA_EXPECTED_OUTPUT,
            ],
            columns=OUTPUT_DF_COLUMNS,
        )
        df_eq(expected_df, df)

    def test_with_features_mixed2_data(self, customer_features_as_str_list):
        entity_df = pd.DataFrame(
            [
                CUSTOMER_1_OLD_ENTITY_DF_ENTRY,
                CUSTOMER_2_NEW_ENTITY_DF_ENTRY,
            ],
            columns=ENTITY_DF_COLUMNS,
        )

        df = offline_store.fetch_historical_feature_values(
            entity_df=entity_df,
            features=customer_features_as_str_list,
        )

        expected_df = pd.DataFrame(
            data=[
                CUSTOMER_1_OLD_DATA_EXPECTED_OUTPUT,
                CUSTOMER_2_NEW_DATA_EXPECTED_OUTPUT,
            ],
            columns=OUTPUT_DF_COLUMNS,
        )
        df_eq(expected_df, df)
