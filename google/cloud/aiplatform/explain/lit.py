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

from typing import Dict, List, Tuple, Union

try:
    from lit_nlp.api import dataset as lit_dataset
    from lit_nlp.api import model as lit_model
    from lit_nlp.api import types as lit_types
    from lit_nlp import notebook
except ImportError:
    raise ImportError(
        "LIT is not installed and is required to get Dataset as the return format. "
        'Please install the SDK using "pip install python-aiplatform[lit]"'
    )

try:
    import tensorflow as tf
except ImportError:
    raise ImportError(
        "Tensorflow is not installed and is required to load saved model. "
        'Please install the SDK using "pip install pip install python-aiplatform[lit]"'
    )

try:
    import pandas as pd
except ImportError:
    raise ImportError(
        "Pandas is not installed and is required to read the dataset. "
        'Please install Pandas using "pip install python-aiplatform[lit]"'
    )


class _VertexLitDataset(lit_dataset.Dataset):
    """LIT dataset class for the Vertex LIT integration.

    This is used in the create_lit_dataset function.
    """

    def __init__(
        self,
        dataset: pd.DataFrame,
        column_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
    ):
        """Construct a VertexLitDataset.
        Args:
          dataset:
            Required. A Pandas DataFrame that includes feature column names and data.
          column_types:
            Required. An OrderedDict of string names matching the columns of the dataset
            as the key, and the associated LitType of the column.
        """
        self._examples = dataset.to_dict(orient="records")
        self._column_types = column_types

    def spec(self):
        """Return a spec describing dataset elements."""
        return dict(self._column_types)


class _VertexLitModel(lit_model.Model):
    """LIT model class for the Vertex LIT integration.

    This is used in the create_lit_model function.
    """

    def __init__(
        self,
        model: str,
        input_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
        output_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
    ):
        """Construct a VertexLitModel.
            Args:
              model:
                Required. A string reference to a local TensorFlow saved model directory.
                The model must have at most one input and one output tensor.
              input_types:
                Required. An OrderedDict of string names matching the features of the model
                as the key, and the associated LitType of the feature.
              output_types:
                Required. An OrderedDict of string names matching the labels of the model
                as the key, and the associated LitType of the label.
        """
        self._loaded_model = tf.saved_model.load(model)
        serving_default = self._loaded_model.signatures[
            tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        ]
        _, self._kwargs_signature = serving_default.structured_input_signature
        self._output_signature = serving_default.structured_outputs

        if len(self._kwargs_signature) != 1:
            raise ValueError("Please use a model with only one input tensor.")

        if len(self._output_signature) != 1:
            raise ValueError("Please use a model with only one output tensor.")

        self._input_types = input_types
        self._output_types = output_types

    def predict_minibatch(
        self, inputs: List[lit_types.JsonDict]
    ) -> List[lit_types.JsonDict]:
        """Returns predictions for a single batch of examples.
            Args:
              inputs:
                sequence of inputs, following model.input_spec()
            Returns:
                list of outputs, following model.output_spec()
        """
        instances = []
        for input in inputs:
            instance = [input[feature] for feature in self._input_types]
            instances.append(instance)
        prediction_input_dict = {
            next(iter(self._kwargs_signature)): tf.convert_to_tensor(instances)
        }
        prediction_dict = self._loaded_model.signatures[
            tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        ](**prediction_input_dict)
        predictions = prediction_dict[next(iter(self._output_signature))].numpy()
        outputs = []
        for prediction in predictions:
            outputs.append(
                {
                    label: value
                    for label, value in zip(self._output_types.keys(), prediction)
                }
            )
        return outputs

    def input_spec(self) -> lit_types.Spec:
        """Return a spec describing model inputs."""
        return dict(self._input_types)

    def output_spec(self) -> lit_types.Spec:
        """Return a spec describing model outputs."""
        return self._output_types


def create_lit_dataset(
    dataset: pd.DataFrame,
    column_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
) -> lit_dataset.Dataset:
    """Creates a LIT Dataset object.
        Args:
          dataset:
              Required. A Pandas DataFrame that includes feature column names and data.
          column_types:
              Required. An OrderedDict of string names matching the columns of the dataset
              as the key, and the associated LitType of the column.
        Returns:
            A LIT Dataset object that has the data from the dataset provided.
    """
    return _VertexLitDataset(dataset, column_types)


def create_lit_model(
    model: str,
    input_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
    output_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
) -> lit_model.Model:
    """Creates a LIT Model object.
        Args:
          model:
              Required. A string reference to a local TensorFlow saved model directory.
              The model must have at most one input and one output tensor.
          input_types:
              Required. An OrderedDict of string names matching the features of the model
              as the key, and the associated LitType of the feature.
          output_types:
              Required. An OrderedDict of string names matching the labels of the model
              as the key, and the associated LitType of the label.
        Returns:
            A LIT Model object that has the same functionality as the model provided.
    """
    return _VertexLitModel(model, input_types, output_types)


def open_lit(
    models: Dict[str, lit_model.Model],
    datasets: Dict[str, lit_dataset.Dataset],
    open_in_new_tab: bool = True,
):
    """Open LIT from the provided models and datasets.
        Args:
          models:
              Required. A list of LIT models to open LIT with.
          input_types:
              Required. A lit of LIT datasets to open LIT with.
          open_in_new_tab:
              Optional. A boolean to choose if LIT open in a new tab or not.
        Raises:
            ImportError if LIT is not installed.
    """
    widget = notebook.LitWidget(models, datasets)
    widget.render(open_in_new_tab=open_in_new_tab)


def set_up_and_open_lit(
    dataset: Union[pd.DataFrame, lit_dataset.Dataset],
    column_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
    model: Union[str, lit_model.Model],
    input_types: Union[List[str], Dict[str, lit_types.LitType]],
    output_types: Union[str, List[str], Dict[str, lit_types.LitType]],
    open_in_new_tab: bool = True,
) -> Tuple[lit_dataset.Dataset, lit_model.Model]:
    """Creates a LIT dataset and model and opens LIT.
        Args:
        dataset:
            Required. A Pandas DataFrame that includes feature column names and data.
        column_types:
            Required. An OrderedDict of string names matching the columns of the dataset
            as the key, and the associated LitType of the column.
        model:
            Required. A string reference to a TensorFlow saved model directory.
            The model must have at most one input and one output tensor.
        input_types:
            Required. An OrderedDict of string names matching the features of the model
            as the key, and the associated LitType of the feature.
        output_types:
            Required. An OrderedDict of string names matching the labels of the model
            as the key, and the associated LitType of the label.
        Returns:
            A Tuple of the LIT dataset and model created.
        Raises:
            ImportError if LIT or TensorFlow is not installed.
            ValueError if the model doesn't have only 1 input and output tensor.
    """
    if not isinstance(dataset, lit_dataset.Dataset):
        dataset = create_lit_dataset(dataset, column_types)

    if not isinstance(model, lit_model.Model):
        model = create_lit_model(model, input_types, output_types)

    open_lit({"model": model}, {"dataset": dataset}, open_in_new_tab=open_in_new_tab)

    return dataset, model
