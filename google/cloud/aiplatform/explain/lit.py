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

import sys

from typing import List, OrderedDict


def create_lit_dataset(
    dataset: "pd.Dataframe",  # noqa: F821
    column_types: OrderedDict[str, "lit_types.LitType"] = None,  # noqa: F821
) -> "lit_dataset.Dataset":  # noqa: F821
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
    except ImportError:
        raise ImportError(
            "LIT is not installed and is required to get Dataset as the return format. "
            'Please install the SDK using "pip install python-aiplatform[lit]"'
        )

    class VertexLitDataset(lit_dataset.Dataset):
        def __init__(self):
            self._examples = dataset.to_dict(orient="records")

        def spec(self):
            return dict(column_types)

    return VertexLitDataset()


def create_lit_model(
    model: str,
    input_types: OrderedDict[str, "lit_types.LitType"],  # noqa: F821
    output_types: OrderedDict[str, "lit_types.LitType"],  # noqa: F821
) -> "lit_model.Model":  # noqa: F821
    """Creates a LIT Model object.
        Args:
          model:
              Required. A string reference to a TensorFlow saved model directory. The model must have at most one input and one output tensor.
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
            ValueError if the model doesn't have only 1 input tensor.
    """
    try:
        import tensorflow as tf
    except ImportError:
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
    serving_default = loaded_model.signatures[
        tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
    ]
    _, kwargs_signature = serving_default.structured_input_signature
    output_signature = serving_default.structured_outputs

    if len(kwargs_signature) != 1:
        raise ValueError("Please use a model with only one input tensor.")

    if len(output_signature) != 1:
        raise ValueError("Please use a model with only one output tensor.")

    class VertexLitModel(lit_model.Model):
        def predict_minibatch(
            self, inputs: List["lit_types.JsonDict"]
        ) -> List["lit_types.JsonDict"]:
            instances = []
            for input in inputs:
                instance = [input[feature] for feature in input_types]
                instances.append(instance)
            prediction_input_dict = {
                next(iter(kwargs_signature)): tf.convert_to_tensor(instances)
            }
            prediction_dict = loaded_model.signatures[
                tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
            ](**prediction_input_dict)
            predictions = prediction_dict[next(iter(output_signature))].numpy()
            outputs = []
            for prediction in predictions:
                outputs.append(
                    {
                        label: value
                        for label, value in zip(output_types.keys(), prediction)
                    }
                )
            return outputs

        def input_spec(self) -> "lit_types.Spec":
            return input_types

        def output_spec(self) -> "lit_types.Spec":
            return output_types

    return VertexLitModel()
