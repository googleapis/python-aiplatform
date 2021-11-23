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

import pandas as pd
import sys
import tensorflow as tf

from typing import Any, List, OrderedDict


def create_lit_dataset(
    dataset: "pd.Dataframe", column_types: OrderedDict[str, "lit_types.LitType"] = None
) -> "lit_dataset.Dataset":
    """Creates a LIT Dataset object.
        Args:
          dataset:
              Required. A Pandas Dataframe that includes feature column names and data.
          column_types:
              Required. An OrderedDict of string names matching the columns of the dataset
              as the key, and the associated LitType of the column.
        Returns:
            A LIT Dataset object that has the data from the dataset provided.
        Raises:
            ImportError if LIT or Pandas is not installed.
    """
    if "pandas" not in sys.modules:
        raise ImportError(
            "Pandas is not installed and is required to read the dataset. "
            'Please install Pandas using "pip install python-aiplatform[lit]"'
        )
    try:
        from lit_nlp.api import dataset as lit_dataset
        from lit_nlp.api import types as lit_types
    except ImportError:
        raise ImportError(
            "LIT is not installed and is required to get Dataset as the return format. "
            'Please install the SDK using "pip install python-aiplatform[lit]"'
        )

    class VertexLitDataset(lit_dataset.Dataset):
        def __init__(self):
            self._examples = dataset.to_dict(orient="records")

        def spec(self):
            return column_types

    return VertexLitDataset()


def create_lit_model(
    model: str,
    input_types: OrderedDict[str, "lit_types.LitType"],
    output_types: OrderedDict[str, "lit_types.LitType"],
) -> "lit_model.Model":
    """Creates a LIT Model object.
        Args:
          model:
              Required. A string reference to a TensorFlow saved model directory.
          input_types:
              Required. An OrderedDict of string names matching the features of the model
              as the key, and the associated LitType of the feature.
          output_types:
              Required. An OrderedDict of string names matching the labels of the model
              as the key, and the associated LitType of the label.
        Returns:
            A LIT Model object that has the same functionality as the model provided.
        Raises:
            ImportError if LIT or TensorFlow is not installed.
    """
    try:
        import tensorflow as tf
    except:
        raise ImportError(
            "Tensorflow is not installed and is required to load saved model. "
            'Please install the SDK using "pip install pip install python-aiplatform[lit]"'
        )

    try:
        from lit_nlp.api import model as lit_model
        from lit_nlp.api import types as lit_types
    except ImportError:
        raise ImportError(
            "LIT is not installed and is required to get Dataset as the return format. "
            'Please install the SDK using "pip install python-aiplatform[lit]"'
        )

    loaded_model = tf.saved_model.load(model)

    class VertexLitModel(lit_model.Model):
        def predict_minibatch(
            self, inputs: List["lit_types.JsonDict"]
        ) -> List["lit_types.JsonDict"]:
            predictions = []
            for input in inputs:
                instance = []
                for feature in input_types:
                    instance.append(input[feature])
                prediction_dict = loaded_model.signatures["serving_default"](
                    tf.constant(instance)
                )
                predictions.append(
                    {
                        label: prediction
                        for label, prediction in zip(
                            output_types.keys, prediction_dict.values()
                        )
                    }
                )
            return predictions

        def input_spec(self) -> "lit_types.Spec":
            return input_types

        def output_spec(self) -> "lit_types.Spec":
            return output_types

    return VertexLitModel()
