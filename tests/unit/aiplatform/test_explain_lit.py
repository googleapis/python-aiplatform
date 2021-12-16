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

import collections
import pytest
import tensorflow as tf
import pandas as pd

from lit_nlp.api import types as lit_types
from lit_nlp import notebook
from unittest import mock
from google.cloud.aiplatform.explain.lit import (
    create_lit_dataset,
    create_lit_model,
    open_lit,
    set_up_and_open_lit,
)


@pytest.fixture
def widget_render_mock():
    with mock.patch.object(notebook.LitWidget, "render") as render_mock:
        yield render_mock


@pytest.fixture
def set_up_sequential(tmpdir):
    # Set up a sequential model
    seq_model = tf.keras.models.Sequential()
    seq_model.add(tf.keras.layers.Dense(32, activation="relu", input_shape=(2,)))
    seq_model.add(tf.keras.layers.Dense(32, activation="relu"))
    seq_model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
    saved_model_path = str(tmpdir.mkdir("tmp"))
    tf.saved_model.save(seq_model, saved_model_path)
    feature_types = collections.OrderedDict(
        [("feature_1", lit_types.Scalar()), ("feature_2", lit_types.Scalar())]
    )
    label_types = collections.OrderedDict([("label", lit_types.RegressionScore())])
    yield feature_types, label_types, saved_model_path


@pytest.fixture
def set_up_pandas_dataframe_and_columns():
    dataframe = pd.DataFrame.from_dict(
        {"feature_1": [1.0, 2.0], "feature_2": [3.0, 4.0], "label": [1.0, 0.0]}
    )
    columns = collections.OrderedDict(
        [
            ("feature_1", lit_types.Scalar()),
            ("feature_2", lit_types.Scalar()),
            ("label", lit_types.RegressionScore()),
        ]
    )
    yield dataframe, columns


def test_create_lit_dataset_from_pandas_returns_dataset(
    set_up_pandas_dataframe_and_columns,
):
    pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
    lit_dataset = create_lit_dataset(pd_dataset, lit_columns)
    expected_examples = [
        {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
        {"feature_1": 2.0, "feature_2": 4.0, "label": 0.0},
    ]

    assert lit_dataset.spec() == dict(lit_columns)
    assert expected_examples == lit_dataset._examples


def test_create_lit_model_from_tensorflow_returns_model(set_up_sequential):
    feature_types, label_types, saved_model_path = set_up_sequential
    lit_model = create_lit_model(saved_model_path, feature_types, label_types)
    test_inputs = [
        {"feature_1": 1.0, "feature_2": 2.0},
        {"feature_1": 3.0, "feature_2": 4.0},
    ]
    outputs = lit_model.predict_minibatch(test_inputs)

    assert lit_model.input_spec() == dict(feature_types)
    assert lit_model.output_spec() == dict(label_types)
    assert len(outputs) == 2
    for item in outputs:
        assert item.keys() == {"label"}
        assert len(item.values()) == 1


def test_open_lit(
    set_up_sequential, set_up_pandas_dataframe_and_columns, widget_render_mock
):
    pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
    lit_dataset = create_lit_dataset(pd_dataset, lit_columns)
    feature_types, label_types, saved_model_path = set_up_sequential
    lit_model = create_lit_model(saved_model_path, feature_types, label_types)

    open_lit({"model": lit_model}, {"dataset": lit_dataset})
    widget_render_mock.assert_called_once()


def test_set_up_and_open_lit(
    set_up_sequential, set_up_pandas_dataframe_and_columns, widget_render_mock
):
    pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
    feature_types, label_types, saved_model_path = set_up_sequential
    lit_dataset, lit_model = set_up_and_open_lit(
        pd_dataset, lit_columns, saved_model_path, feature_types, label_types
    )

    expected_examples = [
        {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
        {"feature_1": 2.0, "feature_2": 4.0, "label": 0.0},
    ]
    test_inputs = [
        {"feature_1": 1.0, "feature_2": 2.0},
        {"feature_1": 3.0, "feature_2": 4.0},
    ]
    outputs = lit_model.predict_minibatch(test_inputs)

    assert lit_dataset.spec() == dict(lit_columns)
    assert expected_examples == lit_dataset._examples

    assert lit_model.input_spec() == dict(feature_types)
    assert lit_model.output_spec() == dict(label_types)
    assert len(outputs) == 2
    for item in outputs:
        assert item.keys() == {"label"}
        assert len(item.values()) == 1

    widget_render_mock.assert_called_once()
