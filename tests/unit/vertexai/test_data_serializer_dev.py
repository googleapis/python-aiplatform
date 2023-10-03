# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
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

from vertexai.preview._workflow.serialization_engine import (
    serializers,
)
import numpy as np
import pandas as pd
import pytest


_TEST_BUCKET = "gs://staging-bucket"
_TEST_FILE_NAME = "data.parquet"
_TEST_GCS_URI = f"{_TEST_BUCKET}/{_TEST_FILE_NAME}"


@pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
class TestPandasDataSerializerDev:
    def test_base_case(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_base_case_with_nans(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.iat[0, 0] = np.nan
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_string_col_names_and_nans(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["0", "1", "2"]
        df.iat[0, 0] = np.nan
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_mixed_data_types_and_nans(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["0", "1", "2"]
        df.insert(3, "string_col", ["0", np.nan, "2"])
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_mixed_data_types_and_row_indices(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["0", "1", "2"]
        df.insert(3, "string_col", ["0", np.nan, "2"])
        df.index = ["0", "1", "2"]
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_mixed_data_types_and_non_string_col_names(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["str_col_0", "str_col_1", 2]
        df.insert(3, "string_col", ["0", np.nan, "2"])
        df.index = ["0", "1", "2"]
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_mixed_data_types_and_non_string_row_indices(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["0", "1", "2"]
        df.insert(3, "string_col", ["0", np.nan, "2"])
        df.index = ["0", "1", 2]
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_mixed_data_types_and_categorical_data(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["0", "1", "2"]
        df.insert(3, "string_col", ["0", np.nan, "2"])
        df.index = ["0", "1", 2]
        df.insert(4, "categorical_str_col", ["A", "B", "C"])
        df["categorical_str_col"] = df["categorical_str_col"].astype("category")
        df.insert(5, "categorical_int_col", [0, np.nan, 2])
        df["categorical_int_col"] = df["categorical_int_col"].astype("category")
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_mixed_data_types_and_ordered_categorical_data(self, tmp_path):
        df = pd.DataFrame(np.zeros(shape=[3, 3]))
        df.columns = ["0", "1", "2"]
        df.insert(3, "string_col", ["0", np.nan, "2"])
        df.index = ["0", "1", 2]
        df.insert(4, "categorical_str_col", ["A", "B", "C"])
        df["categorical_str_col"] = df["categorical_str_col"].astype("category")
        df.insert(5, "categorical_int_col", [0, np.nan, 2])
        df["categorical_int_col"] = df["categorical_int_col"].astype("category")
        df.insert(
            6,
            "orderd_categorical",
            pd.Categorical([1, 2, 3], ordered=True, categories=[2, 1, 3]),
        )
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)

    def test_df_with_multiindex_and_all_string_indices(self, tmp_path):
        arrays = [
            ["bar", "bar", "baz", "baz", "foo", "foo"],
            ["one", "two", "one", "two", "one", "two"],
        ]

        index = pd.MultiIndex.from_tuples(list(zip(*arrays)), names=["first", "second"])
        df = pd.DataFrame(np.zeros(shape=[6, 6]), index=index[:6], columns=index[:6])
        df_serializer = serializers.PandasDataSerializerDev()

        df_serializer.serialize(df, _TEST_GCS_URI)
        restored_df = df_serializer.deserialize(tmp_path / _TEST_FILE_NAME)
        pd.testing.assert_frame_equal(df, restored_df)
