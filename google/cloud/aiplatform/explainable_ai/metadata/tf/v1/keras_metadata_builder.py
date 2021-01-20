# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


"""Metadata builder helper for models built with Keras API.

Currently, there are 3 different model-building styles in Keras: sequential,
functional and subclassed models. This module supports all 3 different flavors
for Tensorflow 1.X. In order to make use of it, a KerasGraphMetadataBuilder
should be initialized with a Keras model object and other optional parameters
such as session (if using other than Keras' default), serving_inputs (signature
definition dictionary if saving the model with this module), etc.

The module creates default metadata from given Keras model. Users have the
option to supplement input and output metadata with additional configuration
parameters using set_* functions. In addition, auxiliary input and output can be
added using add_* functions or deleted using remove_* functions. Final metadata
can either be fetched as a dictionary using get_metadata function or written
to a directory along with the model using save_model_with_metadata function.

Example usage is as follows:

  model = keras.models.Sequential()
  model.add(keras.layers.Dense(32, activation='relu', input_dim=10))
  model.add(keras.layers.Dense(1, activation='sigmoid'))
  model.compile(optimizer='rmsprop', loss='binary_crossentropy')

  builder = KerasGraphMetadataBuilder(model)
  builder.save_model_with_metadata("gs://xai/model/keras/")
"""

import tensorflow.compat.v1 as tf
import tensorflow.compat.v1.keras as keras
from google.cloud.aiplatform.explainable_ai.metadata.tf.v1 import graph_metadata_builder


class KerasGraphMetadataBuilder(graph_metadata_builder.GraphMetadataBuilder):
    """Class for generating metadata for models built with Keras API."""

    def __init__(
        self,
        model,
        outputs_to_explain=(),
        session=None,
        serving_inputs=None,
        serving_outputs=None,
        tags=(tf.saved_model.tag_constants.SERVING,),
        auto_infer=True,
        **kwargs
    ):
        """Initializes a KerasGraphMetadataBuilder object.

    Args:
      model: Keras model to write the metadata for.
      outputs_to_explain: List of output tensors (model.outputs) to explain.
        Only single output is supported for now. Hence, the list should
        contain one element. This parameter is required if the model has
        multiple outputs.
      session: Optional TF Session, if using a session different than of Keras
        backend.
      serving_inputs: A dictionary mapping from serving key to corresponding
        input tensors. If not provided or empty, added and/or inferred input
        metadata will be used.
      serving_outputs: A dictionary mapping from serving key to model outputs.
        If not provided or empty, added and/or inferred output metadata will be
        used.
      tags: The set of tags to annotate the meta graph def with.
      auto_infer: A boolean flag to indicate whether inputs and outputs should
        be inferred from the model itself. If set to False, the model's inputs
        and an output must be provided.
      **kwargs: Any keyword arguments to be passed to saved model builder's
        add_meta_graph() function.
    """
        if outputs_to_explain and len(outputs_to_explain) > 1:
            raise ValueError(
                '"outputs_to_explain" can only contain 1 element.\n'
                "Got: %s" % len(outputs_to_explain)
            )
        if not outputs_to_explain and len(model.outputs) > 1:
            raise ValueError(
                "Model has multiple outputs. Please specify which one to"
                ' explain via "outputs_to_explain" parameter.'
            )
        self._model = model
        self._output_tensors = outputs_to_explain
        self._inputs, self._outputs = {}, {}
        if auto_infer:
            self._create_metadata_entries_from_model()
        self._session = session if session else keras.backend.get_session()
        self._serving_inputs = serving_inputs
        self._serving_outputs = serving_outputs
        self._saved_model_args = kwargs
        self._tags = tags

    def _create_metadata_entries_from_model(self):
        """Creates input and output metadata from models inputs and outputs."""
        for model_input in self._model.inputs:
            self.add_numeric_metadata(model_input, model_input.op.name)

        for model_output in self._model.outputs:
            if (
                not self._output_tensors
                or model_output.name == self._output_tensors[0].name
            ):
                self.add_output_metadata(model_output, model_output.op.name)
                break
        else:
            raise ValueError("Provided output is not one of model outputs.")

    def set_categorical_metadata(
        self,
        model_input,
        encoded_layer,
        encoding,
        name=None,
        input_baselines=None,
        encoded_baselines=None,
    ):
        """Sets an existing metadata identified by input as categorical with params.

    Args:
      model_input: One of model inputs.
      encoded_layer: Encoded model layer for input layer if it exists. Output of
        this layer will be used as the encoded tensor.
      encoding: Encoding type if encoded_layer is provided. Possible values are
        {identity, bag_of_features, bag_of_features_sparse, indicator,
        combined_embedding, concat_embedding}.
      name: Unique friendly name for this feature.
      input_baselines: A list of baseline values. Each baseline value can be a
        single entity or of the same shape as the model_input (except for the
        batch dimension).
      encoded_baselines: A list of baseline values for encoded layer output.
        Each baseline value can be a single entity or of the same shape as the
        encoded tensor (except for the batch dimension).
    """
        self.remove_input_metadata(model_input)
        self.add_categorical_metadata(
            model_input,
            encoded_layer.output,
            encoding,
            name,
            input_baselines,
            encoded_baselines,
        )

    def set_numeric_metadata(
        self, model_input, name=None, input_baselines=None, index_feature_mapping=None
    ):
        """Sets an existing metadata identified by input as numeric with params.

    Args:
      model_input: One of model inputs.
      name: Unique friendly name for this feature.
      input_baselines: A list of baseline values. Each baseline value can be a
        single entity or of the same shape as the model_input (except for the
        batch dimension).
      index_feature_mapping: A list of feature names for each index in the input
        tensor.
    """
        self.remove_input_metadata(model_input)
        self.add_numeric_metadata(
            model_input,
            name,
            input_baselines,
            index_feature_mapping=index_feature_mapping,
        )

    def set_text_metadata(
        self,
        model_input,
        encoded_layer,
        encoding,
        name=None,
        input_baselines=None,
        encoded_baselines=None,
    ):
        """Sets an existing metadata identified by input as text with params.

    Args:
      model_input: One of model inputs.
      encoded_layer: Encoded model layer for input layer if it exists. Output of
        this layer will be used as the encoded tensor.
      encoding: Encoding type if encoded_layer is provided. Possible values are
        {identity, bag_of_features, bag_of_features_sparse, indicator,
        combined_embedding, concat_embedding}.
      name: Unique friendly name for this feature.
      input_baselines: A list of baseline values. Each baseline value can be a
        single entity or of the same shape as the model_input (except for the
        batch dimension).
      encoded_baselines: A list of baseline values for encoded layer output.
        Each baseline value can be a single entity or of the same shape as the
        encoded tensor (except for the batch dimension).
    """
        self.remove_input_metadata(model_input)
        self.add_text_metadata(
            model_input,
            encoded_layer.output,
            encoding,
            name,
            input_baselines,
            encoded_baselines,
        )

    def set_image_metadata(
        self, model_input, name=None, input_baselines=None, visualization=None
    ):
        """Sets an existing metadata identified by input as image with params.

    Args:
      model_input: One of model inputs.
      name: Unique friendly name for this feature.
      input_baselines: A list of baseline values. Each baseline value can be a
        single entity or of the same shape as the model_input (except for the
        batch dimension).
      visualization: A dictionary mapping from keys {type} to values {pixel,
        region}.
    """
        self.remove_input_metadata(model_input)
        self.add_image_metadata(model_input, name, input_baselines, visualization)

    def set_output_metadata(self, model_output, name=None):
        """Adds output tensor as output metadata.

    Args:
      model_output: Model output to get the explanations for. Needs to be a
        tensor of float type, such as probabilities, logits.
      name: Unique friendly name for the output.
    """
        self.remove_output_metadata(model_output)
        self.add_output_metadata(model_output, name)

    def remove_input_metadata(self, model_input):
        """Removes a metadata entry identified by the tensor.

    Args:
      model_input: Model input to be removed from input metadata entries.
    """
        if model_input.name not in self._inputs:
            raise ValueError('Input "%s" does not exist.' % model_input.name)
        del self._inputs[model_input.name]

    def remove_output_metadata(self, model_output):
        """Removes a metadata entry identified by the tensor.

    Args:
      model_output: Model output to be removed from output metadata.
    """
        if model_output.name not in self._outputs:
            raise ValueError('Output "%s" does not exist.' % model_output.name)
        del self._outputs[model_output.name]
