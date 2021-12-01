# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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
import tensorflow as tf
import pandas as pd

from lit_nlp.api import types as lit_types
from google.cloud.aiplatform.explain.lit import (
    create_lit_dataset,
    create_lit_model,
)


class TestLit(tf.test.TestCase):
    def _set_up_sequential(self):
        # Set up a sequential model
        self.seq_model = tf.keras.models.Sequential()
        self.seq_model.add(
            tf.keras.layers.Dense(32, activation="relu", input_shape=(2,))
        )
        self.seq_model.add(tf.keras.layers.Dense(32, activation="relu"))
        self.seq_model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
        self.saved_model_path = self.get_temp_dir()
        tf.saved_model.save(self.seq_model, self.saved_model_path)
        feature_types = collections.OrderedDict(
            [("feature_1", lit_types.Scalar()), ("feature_2", lit_types.Scalar())]
        )
        label_types = collections.OrderedDict([("label", lit_types.RegressionScore())])
        return feature_types, label_types

    def _set_up_pandas_dataframe_and_columns(self):
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
        return dataframe, columns

    def test_create_lit_dataset_from_pandas_returns_dataset(self):
        pd_dataset, lit_columns = self._set_up_pandas_dataframe_and_columns()
        lit_dataset = create_lit_dataset(pd_dataset, lit_columns)
        expected_examples = [
            {"feature_1": 1.0, "feature_2": 3.0, "label": 1.0},
            {"feature_1": 2.0, "feature_2": 4.0, "label": 0.0},
        ]

        assert lit_dataset.spec() == dict(lit_columns)
        assert expected_examples == lit_dataset._examples

    def test_create_lit_model_from_tensorflow_returns_model(self):
        feature_types, label_types = self._set_up_sequential()
        lit_model = create_lit_model(self.saved_model_path, feature_types, label_types)
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
