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


"""Tests for keras_metadata_builder."""
import json
import os
import numpy as np
import tensorflow.compat.v1 as tf
import tensorflow.compat.v1.keras as keras
from google.cloud.aiplatform.explainable_ai.metadata.tf.v1 import keras_metadata_builder


class KerasGraphMetadataBuilderTest(tf.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super(KerasGraphMetadataBuilderTest, cls).setUpClass()
        tf.disable_eager_execution()
        cls.seq_model = keras.models.Sequential()
        cls.seq_model.add(keras.layers.Dense(32, activation="relu", input_dim=10))
        cls.seq_model.add(keras.layers.Dense(32, activation="relu"))
        cls.seq_model.add(keras.layers.Dense(1, activation="sigmoid"))

    def test_get_metadata_sequential(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        generated_md = builder.get_metadata()
        expected_md = {
            "outputs": {"dense_2/Sigmoid": {"output_tensor_name": "dense_2/Sigmoid:0"}},
            "inputs": {
                "dense_input": {
                    "input_tensor_name": "dense_input:0",
                    "modality": "numeric",
                    "encoding": "identity",
                }
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self.assertDictEqual(expected_md, generated_md)

    def test_get_metadata_functional(self):
        inputs1 = keras.Input(shape=(10,), name="model_input1")
        inputs2 = keras.Input(shape=(10,), name="model_input2")
        x = keras.layers.Dense(32, activation="relu")(inputs1)
        x = keras.layers.Dense(32, activation="relu")(x)
        x = keras.layers.concatenate([x, inputs2])
        outputs = keras.layers.Dense(1, activation="sigmoid")(x)
        fun_model = keras.Model(inputs=[inputs1, inputs2], outputs=outputs, name="fun")
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(fun_model)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {
                "model_input1": {
                    "input_tensor_name": "model_input1:0",
                    "modality": "numeric",
                    "encoding": "identity",
                },
                "model_input2": {
                    "input_tensor_name": "model_input2:0",
                    "modality": "numeric",
                    "encoding": "identity",
                },
            },
            "outputs": {"dense_2/Sigmoid": {"output_tensor_name": "dense_2/Sigmoid:0"}},
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self.assertDictEqual(expected_md, generated_md)

    def test_get_metadata_subclassed_model(self):
        class MyModel(keras.Model):
            def __init__(self, num_classes=2):
                super(MyModel, self).__init__(name="my_model")
                self.num_classes = num_classes
                self.dense_1 = keras.layers.Dense(32, activation="relu")
                self.dense_2 = keras.layers.Dense(num_classes, activation="sigmoid")

            def call(self, inputs):
                x = self.dense_1(inputs)
                return self.dense_2(x)

        subclassed_model = MyModel()
        subclassed_model.compile(loss="categorical_crossentropy")
        x_train = np.random.random((1, 100))
        y_train = np.random.randint(2, size=(1, 1))
        subclassed_model.fit(x_train, y_train, batch_size=1, epochs=1)

        builder = keras_metadata_builder.KerasGraphMetadataBuilder(subclassed_model)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {
                "input_1": {
                    "input_tensor_name": "input_1:0",
                    "modality": "numeric",
                    "encoding": "identity",
                }
            },
            "outputs": {
                "my_model/dense_1/Sigmoid": {
                    "output_tensor_name": "my_model/dense_1/Sigmoid:0"
                }
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self.assertDictEqual(expected_md, generated_md)

    def test_set_categorical_metadata(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.set_categorical_metadata(
            self.seq_model.inputs[0],
            name="my_input",
            encoded_layer=self.seq_model.layers[1],
            encoding="combined_embedding",
        )
        generated_md = builder.get_metadata()
        expected_inputs = {
            "my_input": {
                "input_tensor_name": "dense_input:0",
                "encoding": "combined_embedding",
                "encoded_tensor_name": "dense_1/Relu:0",
                "modality": "categorical",
            }
        }
        self.assertDictEqual(expected_inputs, generated_md["inputs"])

    def test_set_numeric_metadata(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.set_numeric_metadata(
            self.seq_model.inputs[0],
            name="numeric_input",
            input_baselines=[1],
            index_feature_mapping=["feat1", "feat2"],
        )
        generated_md = builder.get_metadata()
        expected_inputs = {
            "numeric_input": {
                "input_tensor_name": "dense_input:0",
                "input_baselines": [1],
                "encoding": "bag_of_features",
                "modality": "numeric",
                "index_feature_mapping": ["feat1", "feat2"],
            }
        }
        self.assertDictEqual(expected_inputs, generated_md["inputs"])

    def test_set_text_metadata(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.set_text_metadata(
            self.seq_model.inputs[0],
            name="text_input",
            encoded_layer=self.seq_model.layers[1],
            encoding="concat_embedding",
        )
        generated_md = builder.get_metadata()
        expected_inputs = {
            "text_input": {
                "input_tensor_name": "dense_input:0",
                "encoding": "concat_embedding",
                "encoded_tensor_name": "dense_1/Relu:0",
                "modality": "text",
            }
        }
        self.assertDictEqual(expected_inputs, generated_md["inputs"])

    def test_set_output_metadata(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.set_output_metadata(self.seq_model.outputs[0], name="logits")
        generated_md = builder.get_metadata()
        expected_outputs = {"logits": {"output_tensor_name": "dense_2/Sigmoid:0",}}
        self.assertDictEqual(expected_outputs, generated_md["outputs"])

    def test_set_image_metadata(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.set_image_metadata(
            self.seq_model.inputs[0],
            name="image_input",
            visualization={"type": "Pixels"},
        )
        generated_md = builder.get_metadata()
        expected_inputs = {
            "image_input": {
                "input_tensor_name": "dense_input:0",
                "encoding": "identity",
                "modality": "image",
                "visualization": {"type": "Pixels"},
            }
        }
        self.assertDictEqual(expected_inputs, generated_md["inputs"])

    def test_remove_input_metadata_valid(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.remove_input_metadata(self.seq_model.inputs[0])
        generated_md = builder.get_metadata()
        self.assertEmpty(generated_md["inputs"])

    def test_remove_input_metadata_non_existent(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        with self.assertRaisesRegex(ValueError, "Input .* does not exist."):
            builder.remove_input_metadata(tf.placeholder(shape=(1,), dtype=tf.int32))

    def test_remove_output_metadata_valid(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.remove_output_metadata(self.seq_model.outputs[0])
        generated_md = builder.get_metadata()
        self.assertEmpty(generated_md["outputs"])

    def test_remove_output_metadata_non_existent(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        with self.assertRaisesRegex(ValueError, "Output .* does not exist."):
            builder.remove_output_metadata(tf.placeholder(shape=(1,), dtype=tf.int32))

    def test_set_numeric_metadata_no_input(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        with self.assertRaisesRegex(ValueError, "Input .* does not exist."):
            builder.set_numeric_metadata(
                tf.placeholder(shape=(1,), dtype=tf.int32), name="not_input"
            )

    def test_add_numeric_metadata(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        builder.add_numeric_metadata(
            tf.placeholder(shape=(1,), dtype=tf.int32), name="new_input"
        )
        generated_md = builder.get_metadata()
        expected_inputs = {
            "dense_input": {
                "input_tensor_name": "dense_input:0",
                "modality": "numeric",
                "encoding": "identity",
            },
            "new_input": {
                "input_tensor_name": "Placeholder:0",
                "modality": "numeric",
                "encoding": "identity",
            },
        }
        self.assertDictEqual(expected_inputs, generated_md["inputs"])

    def test_add_output_metadata_already_exists(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(self.seq_model)
        with self.assertRaisesRegex(ValueError, "Only one output can be added."):
            builder.add_output_metadata(
                tf.placeholder(shape=(1,), dtype=tf.int32), name="output"
            )

    def test_get_metadata_not_inferred(self):
        builder = keras_metadata_builder.KerasGraphMetadataBuilder(
            self.seq_model, auto_infer=False
        )
        builder.add_numeric_metadata(self.seq_model.layers[1].input)
        builder.add_output_metadata(self.seq_model.layers[2].output)
        generated_md = builder.get_metadata()
        expected_md = {
            "inputs": {
                "dense/Relu": {
                    "encoding": "identity",
                    "input_tensor_name": "dense/Relu:0",
                    "modality": "numeric",
                }
            },
            "outputs": {"dense_2/Sigmoid": {"output_tensor_name": "dense_2/Sigmoid:0"}},
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self.assertDictEqual(expected_md, generated_md)

    def test_get_metadata_multiple_outputs(self):
        inputs1 = keras.Input(shape=(10,), name="model_input")
        x = keras.layers.Dense(32, activation="relu")(inputs1)
        x = keras.layers.Dense(32, activation="relu")(x)
        outputs1 = keras.layers.Dense(1, activation="sigmoid")(x)
        outputs2 = keras.layers.Dense(1, activation="relu")(x)
        fun_model = keras.Model(
            inputs=[inputs1], outputs=[outputs1, outputs2], name="fun"
        )

        builder = keras_metadata_builder.KerasGraphMetadataBuilder(
            fun_model, outputs_to_explain=[fun_model.outputs[0]]
        )
        generated_md = builder.get_metadata()
        expected_outputs = {
            "dense_2/Sigmoid": {"output_tensor_name": "dense_2/Sigmoid:0"}
        }
        self.assertDictEqual(expected_outputs, generated_md["outputs"])

    def test_get_metadata_multiple_outputs_incorrect_output(self):
        inputs1 = keras.Input(shape=(10,), name="model_input")
        x = keras.layers.Dense(32, activation="relu")(inputs1)
        x = keras.layers.Dense(32, activation="relu")(x)
        outputs1 = keras.layers.Dense(1, activation="sigmoid")(x)
        outputs2 = keras.layers.Dense(1, activation="relu")(x)
        fun_model = keras.Model(
            inputs=[inputs1], outputs=[outputs1, outputs2], name="fun"
        )

        with self.assertRaisesRegex(
            ValueError, "Provided output is not one of model outputs"
        ):
            keras_metadata_builder.KerasGraphMetadataBuilder(
                fun_model, outputs_to_explain=[fun_model.layers[0].output]
            )

    def test_save_model_with_metadata(self):
        tf.reset_default_graph()
        model = keras.models.Sequential()
        model.add(keras.layers.Dense(32, activation="relu", input_dim=10))
        model.add(keras.layers.Dense(1, activation="sigmoid"))

        builder = keras_metadata_builder.KerasGraphMetadataBuilder(model)
        model_path = os.path.join(tf.test.get_temp_dir(), "keras_model")
        builder.save_model_with_metadata(model_path)

        metadata_file_path = os.path.join(model_path, "explanation_metadata.json")
        saved_model_file_path = os.path.join(model_path, "saved_model.pb")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            written_md = json.load(f)
        self.assertDictEqual(builder.get_metadata(), written_md)
        self.assertTrue(os.path.isfile(saved_model_file_path))


if __name__ == "__main__":
    tf.test.main()
