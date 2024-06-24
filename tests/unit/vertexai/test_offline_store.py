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

from typing import List, Optional
from unittest import mock
import pytest
import sys
from vertexai.resources.preview.feature_store import (
    offline_store,
    FeatureGroup,
    Feature,
)

try:
    import pandas as pd
except ImportError:
    pd = None


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

FAKE_ENTITY_DF_QUERY = """ENTITY DF QUERY Line 1
ENTITY DF QUERY Line 2
ENTITY DF QUERY Line 3"""


class FakeBigframe:
    @property
    def columns(self):
        pass

    @property
    def sql(self):
        pass

    def select_dtypes(self, *args):
        pass


# Mock bigframe import
bpd_module = type(sys)("bigframes.pandas")
bpd_module.DataFrame = FakeBigframe
bpd_module.read_gbq_query = lambda x: x
sys.modules["bigframes.pandas"] = bpd_module

bigframe_module = type(sys)("bigframes")
bigframe_module.BigQueryOptions = mock.Mock()
bigframe_module.connect = mock.Mock()
bigframe_module.enums = mock.Mock()
bigframe_module.pandas = bpd_module
bigframe_module.session = mock.Mock()
sys.modules["bigframes"] = bigframe_module

# And now import bigframes
import bigframes  # noqa: E402
import bigframes.pandas as bpd  # noqa: E402


pytestmark = pytest.mark.usefixtures("google_auth_mock")


@pytest.fixture()
def mock_convert_to_bigquery_dataframe():
    with mock.patch.object(
        offline_store._DataFrameToBigQueryDataFramesConverter, "to_bigquery_dataframe"
    ) as mock_convert_to_bigquery_dataframe:
        yield mock_convert_to_bigquery_dataframe


def mock_bdf(
    non_ts_cols: List[str],
    ts_cols: Optional[List[str]] = None,
    sql: Optional[str] = None,
):
    class MockBdf(bpd.DataFrame):
        def __init__(self):
            pass

        def __contains__(self, key):
            pass

    if not ts_cols:
        ts_cols = []
    all_columns = non_ts_cols + ts_cols

    m = mock.MagicMock(spec_set=MockBdf)
    m.__contains__ = lambda s, k: k in all_columns
    m.columns = all_columns
    m.sql = sql

    # Mock returned dtypes (FS code only uses `select_dtypes`).
    dtypes_mock = mock.MagicMock()
    dtypes_mock.columns = ts_cols
    m.select_dtypes.return_value = dtypes_mock

    return m


@pytest.mark.parametrize(
    "features",
    [
        None,
        [],
    ],
)
def test_no_features_raises_error(features):
    with pytest.raises(ValueError) as excinfo:
        offline_store.fetch_historical_feature_values(
            entity_df=pd.DataFrame(),
            features=features,
        )
    assert str(excinfo.value) == "Please specify a non-empty list of features."


def test_entity_df_no_timestamp_column_raises_error(mock_convert_to_bigquery_dataframe):
    with pytest.raises(ValueError) as excinfo:
        mock_convert_to_bigquery_dataframe.return_value = mock_bdf(
            non_ts_cols=["hi"], sql=None
        )

        offline_store.fetch_historical_feature_values(
            entity_df=pd.DataFrame(),
            features=["fake.feature"],
        )

    assert 'No timestamp column ("datetime" dtype) found in entity DataFrame.' == str(
        excinfo.value
    )


def test_entity_df_too_many_timestamp_columns_raises_error(
    mock_convert_to_bigquery_dataframe,
):
    with pytest.raises(ValueError) as excinfo:
        bdf = mock_bdf(non_ts_cols=["hi"], ts_cols=["ts1", "ts2"], sql=None)
        mock_convert_to_bigquery_dataframe.return_value = bdf

        offline_store.fetch_historical_feature_values(
            entity_df=pd.DataFrame(),
            features=["fake.feature"],
        )

    assert (
        'Multiple timestamp columns ("datetime" dtype) found in entity DataFrame. '
        "Only one timestamp column is allowed. "
        "Timestamp columns: ts1, ts2"
    ) == str(excinfo.value)


def test_wrong_type_in_feature_list_raises_error(mock_convert_to_bigquery_dataframe):
    with pytest.raises(ValueError) as excinfo:
        bdf = mock_bdf(non_ts_cols=["hi"], ts_cols=["ts1"], sql=None)
        mock_convert_to_bigquery_dataframe.return_value = bdf

        offline_store.fetch_historical_feature_values(
            entity_df=pd.DataFrame(),
            features=[("hi", "bye")],
        )

    assert (
        "Unsupported feature type <class 'tuple'> found in feature list. "
        "Feature: ('hi', 'bye')"
    ) == str(excinfo.value)


# def test_feature_str_with_project_regex():
# def test_feature_str_without_project_regex():


@pytest.fixture()
def mock_session():
    with mock.patch.object(bigframes, "connect") as mock_session:
        yield mock_session


@pytest.fixture()
def mock_fg():
    with mock.patch.object(FeatureGroup, "__new__") as mock_fg:
        yield mock_fg


def create_mock_fg(
    name: str,
    entity_id_cols: List[str],
    bq_uri: str,
):
    fg = mock.MagicMock()
    fg.name = name
    fg._gca_resource.big_query.entity_id_columns = entity_id_cols
    fg._gca_resource.big_query.big_query_source.input_uri = bq_uri
    return fg


@pytest.fixture()
def mock_feature():
    with mock.patch.object(Feature, "__new__") as mock_feature:
        yield mock_feature


def create_mock_feature(
    name: str,
    version_column_name: str,
):
    feature = mock.MagicMock()
    feature.name = name
    feature.version_column_name = version_column_name
    return feature


def expected_sql_for_one_feature(
    feature_name: str,
    bq_column_name: str,
):
    return f"""WITH
  entity_df_without_row_num AS (
    ENTITY DF QUERY Line 1
    ENTITY DF QUERY Line 2
    ENTITY DF QUERY Line 3
  ),
  entity_df AS (
    SELECT *, ROW_NUMBER() OVER() AS row_num,
    FROM entity_df_without_row_num
  ),

  # Features
  fake__my_feature AS (
    SELECT
      customer_id,
      {bq_column_name} AS {feature_name},
      feature_timestamp
    FROM my.table
  ),

  # Features with PITL
  fake__my_feature_pitl AS (
    SELECT
      entity_df.row_num,
      fake__my_feature.my_feature,
    FROM entity_df
    LEFT JOIN fake__my_feature
    ON (
      entity_df.customer_id = fake__my_feature.customer_id AND
      CAST(fake__my_feature.feature_timestamp AS TIMESTAMP) <= CAST(entity_df.timestamp AS TIMESTAMP)
    )
    QUALIFY ROW_NUMBER() OVER (PARTITION BY entity_df.row_num ORDER BY fake__my_feature.feature_timestamp DESC) = 1
  )


SELECT
  entity_df.customer_id, entity_df.feature_1,
  fake__my_feature_pitl.my_feature,
  entity_df.timestamp

FROM entity_df
JOIN fake__my_feature_pitl USING (row_num)
"""


@pytest.mark.parametrize(
    "feature_name, bq_column_name",
    [
        ("my_feature", "my_feature"),
        ("my_feature", "bq_col_name"),
    ],
)
def test_one_feature_same_and_different_bq_col_name(
    feature_name,
    bq_column_name,
    mock_convert_to_bigquery_dataframe,
    mock_session,
    mock_fg,
    mock_feature,
):
    entity_df = pd.DataFrame(
        [
            CUSTOMER_1_OLD_ENTITY_DF_ENTRY,
            CUSTOMER_2_OLD_ENTITY_DF_ENTRY,
        ],
        columns=ENTITY_DF_COLUMNS,
    )

    mock_convert_to_bigquery_dataframe.return_value = mock_bdf(
        non_ts_cols=["customer_id", "feature_1"],
        ts_cols=["timestamp"],
        sql=FAKE_ENTITY_DF_QUERY,
    )
    mock_session.return_value.read_gbq_query.return_value = "SOME SQL QUERY OUTPUT"

    mock_fg.return_value = create_mock_fg(
        name="fake", entity_id_cols=["customer_id"], bq_uri="bq://my.table"
    )
    mock_feature.return_value = create_mock_feature(
        name=feature_name, version_column_name=bq_column_name
    )
    mock_fg.return_value.get_feature = mock_feature

    rsp = offline_store.fetch_historical_feature_values(
        entity_df=entity_df,
        features=[f"fake.{feature_name}"],
    )

    mock_session.assert_called_once_with(
        bigframes.BigQueryOptions(project=None, location=None),
    )
    mock_session.return_value.read_gbq_query.assert_called_once_with(
        expected_sql_for_one_feature(feature_name, bq_column_name),
        index_col=bigframes.enums.DefaultIndexKind.NULL,
    )

    assert rsp == "SOME SQL QUERY OUTPUT"


def test_one_feature_with_explicit_bigframes_session(
    mock_convert_to_bigquery_dataframe,
    mock_fg,
    mock_feature,
):
    entity_df = pd.DataFrame(
        [
            CUSTOMER_1_OLD_ENTITY_DF_ENTRY,
            CUSTOMER_2_OLD_ENTITY_DF_ENTRY,
        ],
        columns=ENTITY_DF_COLUMNS,
    )

    mock_convert_to_bigquery_dataframe.return_value = mock_bdf(
        non_ts_cols=["customer_id", "feature_1"],
        ts_cols=["timestamp"],
        sql=FAKE_ENTITY_DF_QUERY,
    )

    mock_fg.return_value = create_mock_fg(
        name="fake", entity_id_cols=["customer_id"], bq_uri="bq://my.table"
    )
    mock_feature.return_value = create_mock_feature(
        name="my_feature", version_column_name="my_feature"
    )
    mock_fg.return_value.get_feature = mock_feature

    session = mock.Mock()
    session.read_gbq_query.return_value = "SOME SQL QUERY OUTPUT"

    rsp = offline_store.fetch_historical_feature_values(
        entity_df=entity_df,
        features=["fake.my_feature"],
        session=session,
    )

    session.read_gbq_query.assert_called_once_with(
        expected_sql_for_one_feature("my_feature", "my_feature"),
        index_col=bigframes.enums.DefaultIndexKind.NULL,
    )

    assert rsp == "SOME SQL QUERY OUTPUT"


def test_one_feature_with_explicit_project_and_location(
    mock_convert_to_bigquery_dataframe,
    mock_session,
    mock_fg,
    mock_feature,
):
    entity_df = pd.DataFrame(
        [
            CUSTOMER_1_OLD_ENTITY_DF_ENTRY,
            CUSTOMER_2_OLD_ENTITY_DF_ENTRY,
        ],
        columns=ENTITY_DF_COLUMNS,
    )

    mock_convert_to_bigquery_dataframe.return_value = mock_bdf(
        non_ts_cols=["customer_id", "feature_1"],
        ts_cols=["timestamp"],
        sql=FAKE_ENTITY_DF_QUERY,
    )

    mock_fg.return_value = create_mock_fg(
        name="fake", entity_id_cols=["customer_id"], bq_uri="bq://my.table"
    )
    mock_feature.return_value = create_mock_feature(
        name="my_feature", version_column_name="my_feature"
    )
    mock_fg.return_value.get_feature = mock_feature

    mock_session.return_value.read_gbq_query.return_value = "SOME SQL QUERY OUTPUT"

    rsp = offline_store.fetch_historical_feature_values(
        entity_df=entity_df,
        features=["fake.my_feature"],
        project="my-project",
        location="my-location",
    )

    mock_session.assert_called_once_with(
        bigframes.BigQueryOptions(project="my-project", location="my-location"),
    )
    mock_session.return_value.read_gbq_query.assert_called_once_with(
        expected_sql_for_one_feature("my_feature", "my_feature"),
        index_col=bigframes.enums.DefaultIndexKind.NULL,
    )

    assert rsp == "SOME SQL QUERY OUTPUT"
