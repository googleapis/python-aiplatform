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

import pytest
import sys

if sys.version_info >= (3, 13):
    pytest.skip("Tensorflow not available for Python 3.13+", allow_module_level=True)

import tensorflow as tf
import numpy as np

from google.cloud.aiplatform import models
from google.cloud.aiplatform.explain.metadata.tf.v2 import (
    saved_model_metadata_builder,
)
from google.cloud.aiplatform.compat.types import explanation_metadata
import constants as test_constants


@pytest.mark.usefixtures("google_auth_mock")
class SavedModelMetadataBuilderTF2Test(tf.test.TestCase):
    def _set_up_sequential(self):
        # Set up for the sequential.
        self.seq_model = tf.keras.models.Sequential()
        self.seq_model.add(tf.keras.layers.Dense(32, activation="relu", input_dim=10))
        self.seq_model.add(tf.keras.layers.Dense(32, activation="relu"))
        self.seq_model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
        self.saved_model_path = self.get_temp_dir()
        tf.saved_model.save(self.seq_model, self.saved_model_path)

    def test_get_metadata_sequential(self):
        self._set_up_sequential()

        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.saved_model_path
        )
        generated_md = builder.get_metadata()
        expected_md = {
            "outputs": {"dense_2": {"outputTensorName": "dense_2"}},
            "inputs": {"dense_input": {"inputTensorName": "dense_input"}},
        }
        assert expected_md == generated_md

    def test_get_metadata_protobuf_sequential(self):
        self._set_up_sequential()

        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.saved_model_path
        )
        generated_object = builder.get_metadata_protobuf()
        expected_object = explanation_metadata.ExplanationMetadata(
            inputs={"dense_input": {"input_tensor_name": "dense_input"}},
            outputs={"dense_2": {"output_tensor_name": "dense_2"}},
        )
        assert expected_object == generated_object

    def test_get_metadata_functional(self):
        inputs1 = tf.keras.Input(shape=(10,), name="model_input1")
        inputs2 = tf.keras.Input(shape=(10,), name="model_input2")
        x = tf.keras.layers.Dense(32, activation="relu")(inputs1)
        x = tf.keras.layers.Dense(32, activation="relu")(x)
        x = tf.keras.layers.concatenate([x, inputs2])
        outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
        fun_model = tf.keras.Model(
            inputs=[inputs1, inputs2], outputs=outputs, name="fun"
        )
        model_dir = self.get_temp_dir()
        tf.saved_model.save(fun_model, model_dir)
        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(model_dir)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {
                "model_input1": {"inputTensorName": "model_input1"},
                "model_input2": {"inputTensorName": "model_input2"},
            },
            "outputs": {"dense_2": {"outputTensorName": "dense_2"}},
        }
        assert expected_md == generated_md

    def test_get_metadata_subclassed_model(self):
        class MyModel(tf.keras.Model):
            def __init__(self, num_classes=2):
                super(MyModel, self).__init__(name="my_model")
                self.num_classes = num_classes
                self.dense_1 = tf.keras.layers.Dense(32, activation="relu")
                self.dense_2 = tf.keras.layers.Dense(num_classes, activation="sigmoid")

            def call(self, inputs):
                x = self.dense_1(inputs)
                return self.dense_2(x)

        subclassed_model = MyModel()
        subclassed_model.compile(loss="categorical_crossentropy")
        np.random.seed(0)
        x_train = np.random.random((1, 100))
        y_train = np.random.randint(2, size=(1, 2))
        subclassed_model.fit(x_train, y_train, batch_size=1, epochs=1)
        model_dir = self.get_temp_dir()
        tf.saved_model.save(subclassed_model, model_dir)

        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(model_dir)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {"input_1": {"inputTensorName": "input_1"}},
            "outputs": {"output_1": {"outputTensorName": "output_1"}},
        }
        assert expected_md == generated_md

    @pytest.mark.skip(reason="Failing for Python 3.11, tracked in b/293506827.")
    def test_non_keras_model(self):
        class CustomModuleWithOutputName(tf.Module):
            def __init__(self):
                super(CustomModuleWithOutputName, self).__init__()
                self.v = tf.Variable(1.0)

            @tf.function(input_signature=[tf.TensorSpec([], tf.float32)])
            def __call__(self, x):
                return {"custom_output_name": x * self.v}

        module_output = CustomModuleWithOutputName()
        call_output = module_output.__call__.get_concrete_function(
            tf.TensorSpec(None, tf.float32)
        )
        model_dir = self.get_temp_dir()
        tf.saved_model.save(
            module_output, model_dir, signatures={"serving_default": call_output}
        )

        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(model_dir)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {"x": {"inputTensorName": "x"}},
            "outputs": {
                "custom_output_name": {"outputTensorName": "custom_output_name"}
            },
        }
        assert expected_md == generated_md

    def test_model_with_feature_column(self):
        feature_columns = [
            tf.feature_column.embedding_column(
                tf.feature_column.categorical_column_with_vocabulary_list(
                    "mode", ["fixed", "normal", "reversible"]
                ),
                dimension=8,
            ),
            tf.feature_column.numeric_column("age"),
        ]
        feature_layer = tf.keras.layers.DenseFeatures(feature_columns)

        model = tf.keras.Sequential(
            [
                feature_layer,
                tf.keras.layers.Dense(128, activation="relu"),
                tf.keras.layers.Dense(1),
            ]
        )

        model.compile(
            optimizer="adam",
            loss=tf.keras.losses.BinaryCrossentropy(from_logits=True),
            metrics=["accuracy"],
        )

        model.fit(
            {"age": np.array([20, 1]), "mode": np.array(["fixed", "normal"])},
            np.array([0, 1]),
        )
        model_dir = self.get_temp_dir()
        tf.saved_model.save(model, model_dir)
        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(model_dir)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {
                "age": {"inputTensorName": "age", "modality": "categorical"},
                "mode": {"inputTensorName": "mode", "modality": "categorical"},
            },
            "outputs": {"output_1": {"outputTensorName": "output_1"}},
        }
        assert expected_md == generated_md

    @pytest.mark.usefixtures("upload_model_mock", "get_model_mock")
    def test_model_upload_compatibility(self):
        self._set_up_sequential()

        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.saved_model_path
        )
        generated_md = builder.get_metadata_protobuf()

        try:
            models.Model.upload(
                display_name=test_constants.ModelConstants._TEST_MODEL_NAME,
                serving_container_image_uri=test_constants.ModelConstants._TEST_SERVING_CONTAINER_IMAGE,
                explanation_parameters=test_constants.ModelConstants._TEST_EXPLANATION_PARAMETERS,
                explanation_metadata=generated_md,  # Test metadata from builder
                labels=test_constants.ModelConstants._TEST_LABEL,
            )
        except TypeError as e:
            if "Parameter to MergeFrom() must be instance of same class" in str(e):
                pytest.fail(
                    f"Model.upload() expects different proto version, more info: {e}"
                )
            else:
                raise e
