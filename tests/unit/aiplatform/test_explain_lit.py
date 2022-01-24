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
import explainable_ai_sdk
import os
import pandas as pd
import pytest
import tensorflow as tf

from google.cloud.aiplatform.explain.lit import (
    create_lit_dataset,
    create_lit_model,
    open_lit,
    set_up_and_open_lit,
)
from lit_nlp.api import types as lit_types
from lit_nlp import notebook
from unittest import mock


@pytest.fixture
def widget_render_mock():
    with mock.patch.object(notebook.LitWidget, "render") as render_mock:
        yield render_mock


@pytest.fixture
def sampled_shapley_explainer_mock():
    with mock.patch.object(
        explainable_ai_sdk, "SampledShapleyConfig", create=True
    ) as config_mock:
        yield config_mock


@pytest.fixture
def load_model_from_local_path_mock():
    with mock.patch.object(
        explainable_ai_sdk, "load_model_from_local_path", autospec=True
    ) as explainer_mock:
        model_mock = mock.Mock()
        explanation_mock = mock.Mock()
        explanation_mock.feature_importance.return_value = {
            "feature_1": 0.01,
            "feature_2": 0.1,
        }
        model_mock.explain.return_value = [
            explanation_mock
            # , explanation_mock
        ]
        explainer_mock.return_value = model_mock
        yield explainer_mock


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
        {"feature_1": [1.0], "feature_2": [3.0], "label": [1.0]}
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
    ]

    assert lit_dataset.spec() == dict(lit_columns)
    assert expected_examples == lit_dataset._examples


def test_create_lit_model_from_tensorflow_returns_model(set_up_sequential):
    feature_types, label_types, saved_model_path = set_up_sequential
    lit_model = create_lit_model(saved_model_path, feature_types, label_types)
    test_inputs = [
        {"feature_1": 1.0, "feature_2": 2.0},
    ]
    outputs = lit_model.predict_minibatch(test_inputs)

    assert lit_model.input_spec() == dict(feature_types)
    assert lit_model.output_spec() == dict(label_types)
    assert len(outputs) == 1
    for item in outputs:
        assert item.keys() == {"label"}
        assert len(item.values()) == 1


@mock.patch.dict(os.environ, {"LIT_PROXY_URL": "auto"})
@pytest.mark.usefixtures(
    "sampled_shapley_explainer_mock", "load_model_from_local_path_mock"
)
def test_create_lit_model_from_tensorflow_with_xai_returns_model(set_up_sequential):
    feature_types, label_types, saved_model_path = set_up_sequential
    lit_model = create_lit_model(saved_model_path, feature_types, label_types)
    test_inputs = [
        {"feature_1": 1.0, "feature_2": 2.0},
    ]
    outputs = lit_model.predict_minibatch(test_inputs)

    assert lit_model.input_spec() == dict(feature_types)
    assert lit_model.output_spec() == dict(
        {**label_types, "feature_attribution": lit_types.FeatureSalience(signed=True)}
    )
    assert len(outputs) == 1
    for item in outputs:
        assert item.keys() == {"label", "feature_attribution"}
        assert len(item.values()) == 2


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
    ]
    test_inputs = [
        {"feature_1": 1.0, "feature_2": 2.0},
    ]
    outputs = lit_model.predict_minibatch(test_inputs)

    assert lit_dataset.spec() == dict(lit_columns)
    assert expected_examples == lit_dataset._examples

    assert lit_model.input_spec() == dict(feature_types)
    assert lit_model.output_spec() == dict(label_types)
    assert len(outputs) == 1
    for item in outputs:
        assert item.keys() == {"label"}
        assert len(item.values()) == 1

    widget_render_mock.assert_called_once()


@mock.patch.dict(os.environ, {"LIT_PROXY_URL": "auto"})
@pytest.mark.usefixtures(
    "sampled_shapley_explainer_mock", "load_model_from_local_path_mock"
)
def test_set_up_and_open_lit_with_xai(
    set_up_sequential, set_up_pandas_dataframe_and_columns, widget_render_mock
):
    pd_dataset, lit_columns = set_up_pandas_dataframe_and_columns
    feature_types, label_types, saved_model_path = set_up_sequential
    lit_dataset, lit_model = set_up_and_open_lit(
        pd_dataset, lit_columns, saved_model_path, feature_types, label_types
    )

    expected_examples = [
        {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
    ]
    test_inputs = [
        {"feature_1": 1.0, "feature_2": 2.0},
    ]
    outputs = lit_model.predict_minibatch(test_inputs)

    assert lit_dataset.spec() == dict(lit_columns)
    assert expected_examples == lit_dataset._examples

    assert lit_model.input_spec() == dict(feature_types)
    assert lit_model.output_spec() == dict(
        {**label_types, "feature_attribution": lit_types.FeatureSalience(signed=True)}
    )
    assert len(outputs) == 1
    for item in outputs:
        assert item.keys() == {"label", "feature_attribution"}
        assert len(item.values()) == 2

    widget_render_mock.assert_called_once()
