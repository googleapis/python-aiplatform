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

import logging
import os

from typing import Dict, List, Optional, Tuple, Union

try:
    from lit_nlp.api import dataset as lit_dataset
    from lit_nlp.api import dtypes as lit_dtypes
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
        attribution_method: str = "sampled_shapley",
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
              attribution_method:
                Optional. A string to choose what attribution configuration to
                set up the explainer with. Valid options are 'sampled_shapley'
                or 'integrated_gradients'.
        """
        self._load_model(model)
        self._input_types = input_types
        self._output_types = output_types
        self._input_tensor_name = next(iter(self._kwargs_signature))
        self._attribution_explainer = None
        if os.environ.get("LIT_PROXY_URL"):
            self._set_up_attribution_explainer(model, attribution_method)

    @property
    def attribution_explainer(self,) -> Optional["AttributionExplainer"]:  # noqa: F821
        """Gets the attribution explainer property if set."""
        return self._attribution_explainer

    def predict_minibatch(
        self, inputs: List[lit_types.JsonDict]
    ) -> List[lit_types.JsonDict]:
        instances = []
        for input in inputs:
            instance = [input[feature] for feature in self._input_types]
            instances.append(instance)
        prediction_input_dict = {
            self._input_tensor_name: tf.convert_to_tensor(instances)
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
        # Get feature attributions
        if self.attribution_explainer:
            attributions = self.attribution_explainer.explain(
                [{self._input_tensor_name: i} for i in instances]
            )
            for i, attribution in enumerate(attributions):
                outputs[i]["feature_attribution"] = lit_dtypes.FeatureSalience(
                    attribution.feature_importance()
                )
        return outputs

    def input_spec(self) -> lit_types.Spec:
        """Return a spec describing model inputs."""
        return dict(self._input_types)

    def output_spec(self) -> lit_types.Spec:
        """Return a spec describing model outputs."""
        output_spec_dict = dict(self._output_types)
        if self.attribution_explainer:
            output_spec_dict["feature_attribution"] = lit_types.FeatureSalience(
                signed=True
            )
        return output_spec_dict

    def _load_model(self, model: str):
        """Loads a TensorFlow saved model and populates the input and output signature attributes of the class.
            Args:
              model: Required. A string reference to a TensorFlow saved model directory.
            Raises:
                ValueError if the model has more than one input tensor or more than one output tensor.
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

    def _set_up_attribution_explainer(
        self, model: str, attribution_method: str = "integrated_gradients"
    ):
        """Populates the attribution explainer attribute of the class.
            Args:
              model: Required. A string reference to a TensorFlow saved model directory.
            attribution_method:
              Optional. A string to choose what attribution configuration to
              set up the explainer with. Valid options are 'sampled_shapley'
              or 'integrated_gradients'.
        """
        try:
            import explainable_ai_sdk
            from explainable_ai_sdk.metadata.tf.v2 import SavedModelMetadataBuilder
        except ImportError:
            logging.info(
                "Skipping explanations because the Explainable AI SDK is not installed."
                'Please install the SDK using "pip install explainable-ai-sdk"'
            )
            return

        builder = SavedModelMetadataBuilder(model)
        builder.get_metadata()
        builder.set_numeric_metadata(
            self._input_tensor_name,
            index_feature_mapping=list(self._input_types.keys()),
        )
        builder.save_metadata(model)
        if attribution_method == "integrated_gradients":
            explainer_config = explainable_ai_sdk.IntegratedGradientsConfig()
        else:
            explainer_config = explainable_ai_sdk.SampledShapleyConfig()

        self._attribution_explainer = explainable_ai_sdk.load_model_from_local_path(
            model, explainer_config
        )
        self._load_model(model)


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
    attribution_method: str = "sampled_shapley",
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
          attribution_method:
            Optional. A string to choose what attribution configuration to
            set up the explainer with. Valid options are 'sampled_shapley'
            or 'integrated_gradients'.
        Returns:
            A LIT Model object that has the same functionality as the model provided.
    """
    return _VertexLitModel(model, input_types, output_types, attribution_method)


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
    widget = notebook.LitWidget(models, datasets, open_in_new_tab=open_in_new_tab)
    widget.render()


def set_up_and_open_lit(
    dataset: Union[pd.DataFrame, lit_dataset.Dataset],
    column_types: "OrderedDict[str, lit_types.LitType]",  # noqa: F821
    model: Union[str, lit_model.Model],
    input_types: Union[List[str], Dict[str, lit_types.LitType]],
    output_types: Union[str, List[str], Dict[str, lit_types.LitType]],
    attribution_method: str = "sampled_shapley",
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
          attribution_method:
            Optional. A string to choose what attribution configuration to
            set up the explainer with. Valid options are 'sampled_shapley'
            or 'integrated_gradients'.
          open_in_new_tab:
            Optional. A boolean to choose if LIT open in a new tab or not.
        Returns:
            A Tuple of the LIT dataset and model created.
        Raises:
            ImportError if LIT or TensorFlow is not installed.
            ValueError if the model doesn't have only 1 input and output tensor.
    """
    if not isinstance(dataset, lit_dataset.Dataset):
        dataset = create_lit_dataset(dataset, column_types)

    if not isinstance(model, lit_model.Model):
        model = create_lit_model(
            model, input_types, output_types, attribution_method=attribution_method
        )

    open_lit(
        {"model": model}, {"dataset": dataset}, open_in_new_tab=open_in_new_tab,
    )

    return dataset, model
