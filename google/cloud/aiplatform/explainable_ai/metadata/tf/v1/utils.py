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


"""Utility functions for explainability SDK."""
from __future__ import absolute_import
from __future__ import division

from __future__ import print_function


import tensorflow.compat.v1 as tf


def _create_signature_def(
    inputs, outputs, method_name=tf.saved_model.PREDICT_METHOD_NAME
):
    """Creates a Tensorflow signature from given parameters.

  Args:
    inputs: Dictionary mapping from input name to input tensor.
    outputs: Dictionary mapping from output name to output tensor.
    method_name: tf.saved_model output name.

  Returns:
    A Tensorflow saved model signature definition.
  """
    return tf.saved_model.signature_def_utils.build_signature_def(
        inputs={
            name: tf.saved_model.utils.build_tensor_info(tensor)
            for name, tensor in inputs.items()
        },
        outputs={
            name: tf.saved_model.utils.build_tensor_info(tensor)
            for name, tensor in outputs.items()
        },
        method_name=method_name,
    )


def save_graph_model(
    session, export_dir, sig_def_inputs, sig_def_outputs, tags, **kwargs
):
    """Saves the model in the session with given inputs and outputs."""
    with session.graph.as_default():
        builder = tf.saved_model.Builder(export_dir)
        sig_def_map = {
            tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY: _create_signature_def(
                sig_def_inputs, sig_def_outputs
            )
        }
        builder.add_meta_graph_and_variables(
            session, tags, signature_def_map=sig_def_map, **kwargs
        )
        print("Writing signature def for the model.")
        print(
            "Signature def key: %s." % tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY
        )
        print(
            "Signature def: \n%s"
            % sig_def_map[tf.saved_model.DEFAULT_SERVING_SIGNATURE_DEF_KEY]
        )
        print("Tags: %s." % tags)
        builder.save()
