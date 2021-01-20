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


"""Tests for graph_metadata_builder."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import tensorflow.compat.v1 as tf
from google.cloud.aiplatform.explainable_ai.metadata.tf.v1 import graph_metadata_builder


class GraphMetadataBuilderTest(tf.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super(GraphMetadataBuilderTest, cls).setUpClass()
        cls.sess = tf.Session(graph=tf.Graph())
        with cls.sess.graph.as_default():
            cls.x = tf.placeholder(shape=[None, 10], dtype=tf.float32, name="inp")
            weights = tf.constant(1.0, shape=(10, 2), name="weights")
            bias_weight = tf.constant(1.0, shape=(2,), name="bias")
            cls.linear_layer = tf.add(tf.matmul(cls.x, weights), bias_weight)
            cls.prediction = tf.nn.relu(cls.linear_layer)

    def test_add_categorical_metadata(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_categorical_metadata(
            self.x,
            name="my_input",
            encoded_tensor=self.linear_layer,
            encoding="combined_embedding",
        )
        md_dict = builder.get_metadata()
        expected_input_md = {
            "my_input": {
                "input_tensor_name": "inp:0",
                "encoding": "combined_embedding",
                "encoded_tensor_name": "Add:0",
                "modality": "categorical",
            }
        }
        self.assertDictEqual(expected_input_md, md_dict["inputs"])

    def test_add_numeric_metadata_no_name(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_numeric_metadata(self.x)
        md_dict = builder.get_metadata()
        expected_input_md = {
            "inp": {
                "input_tensor_name": "inp:0",
                "encoding": "identity",
                "modality": "numeric",
            }
        }
        self.assertDictEqual(expected_input_md, md_dict["inputs"])

    def test_add_numeric_metadata_same_name(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_numeric_metadata(self.x, name="same")
        with self.assertRaisesRegex(ValueError, "Input name .* exists"):
            builder.add_numeric_metadata(name="same", input_tensor=self.linear_layer)

    def test_add_numeric_metadata_same_tensor(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_numeric_metadata(self.x, name="same")
        with self.assertRaisesRegex(ValueError, "Input tensor .* exists"):
            builder.add_numeric_metadata(name="different", input_tensor=self.x)

    def test_add_numeric_metadata_index_feature_mapping(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_numeric_metadata(
            self.x, name="mapped", index_feature_mapping=["a", "b"]
        )
        md_dict = builder.get_metadata()
        expected_input_md = {
            "mapped": {
                "input_tensor_name": "inp:0",
                "encoding": "bag_of_features",
                "modality": "numeric",
                "index_feature_mapping": ["a", "b"],
            }
        }
        self.assertDictEqual(expected_input_md, md_dict["inputs"])

    def test_add_image_metadata(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_image_metadata(self.x, visualization={"type": "Pixels"})
        md_dict = builder.get_metadata()
        expected_input_md = {
            "inp": {
                "visualization": {"type": "Pixels"},
                "input_tensor_name": "inp:0",
                "encoding": "identity",
                "modality": "image",
            }
        }
        self.assertDictEqual(expected_input_md, md_dict["inputs"])

    def test_add_text_metadata(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_text_metadata(
            self.x, encoded_tensor=self.linear_layer, encoding="combined_embedding"
        )
        md_dict = builder.get_metadata()
        expected_input_md = {
            "inp": {
                "input_tensor_name": "inp:0",
                "encoding": "combined_embedding",
                "encoded_tensor_name": "Add:0",
                "modality": "text",
            }
        }
        self.assertDictEqual(expected_input_md, md_dict["inputs"])

    def test_add_output_metadata(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_output_metadata(self.prediction, "my_output")
        md_dict = builder.get_metadata()
        expected_out_md = {"my_output": {"output_tensor_name": "Relu:0"}}

        self.assertDictEqual(expected_out_md, md_dict["outputs"])

    def test_add_output_metadata_no_name(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_output_metadata(self.prediction)
        md_dict = builder.get_metadata()
        expected_out_md = {"Relu": {"output_tensor_name": "Relu:0"}}
        self.assertDictEqual(expected_out_md, md_dict["outputs"])

    def test_add_output_metadata_multiple(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_output_metadata(self.prediction, "my_output1")
        with self.assertRaisesRegex(ValueError, "Only one output can be added"):
            builder.add_output_metadata(self.x, "my_output2")

    def test_get_metadata_multiple_inputs(self):
        builder = graph_metadata_builder.GraphMetadataBuilder()
        builder.add_image_metadata(self.linear_layer, visualization={"type": "Pixels"})
        builder.add_numeric_metadata(self.x, name="my_input")
        builder.add_output_metadata(self.prediction)
        md_dict = builder.get_metadata()
        expected_md = {
            "framework": "Tensorflow",
            "inputs": {
                "Add": {
                    "visualization": {"type": "Pixels"},
                    "input_tensor_name": "Add:0",
                    "encoding": "identity",
                    "modality": "image",
                },
                "my_input": {
                    "input_tensor_name": "inp:0",
                    "encoding": "identity",
                    "modality": "numeric",
                },
            },
            "outputs": {"Relu": {"output_tensor_name": "Relu:0"}},
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self.assertDictEqual(expected_md, md_dict)

    def test_save_model_with_metadata(self):
        builder = graph_metadata_builder.GraphMetadataBuilder(session=self.sess)
        builder.add_image_metadata(self.linear_layer, visualization={"type": "Pixels"})
        builder.add_numeric_metadata(self.x, name="my_input")
        builder.add_output_metadata(self.prediction)
        model_path = os.path.join(tf.test.get_temp_dir(), "multi_modal")
        builder.save_model_with_metadata(model_path)

        metadata_file_path = os.path.join(model_path, "explanation_metadata.json")
        saved_model_file_path = os.path.join(model_path, "saved_model.pb")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            written_md = json.load(f)
        self.assertDictEqual(builder.get_metadata(), written_md)
        self.assertTrue(os.path.isfile(saved_model_file_path))

    def test_save_model_with_metadata_kwargs(self):
        builder = graph_metadata_builder.GraphMetadataBuilder(
            session=self.sess, tags=["testing"], strip_default_attrs=False
        )
        builder.add_image_metadata(self.linear_layer, visualization={"type": "Pixels"})
        builder.add_numeric_metadata(self.x, name="my_input")
        builder.add_output_metadata(self.prediction)
        model_path = os.path.join(tf.test.get_temp_dir(), "model_kwargs")
        builder.save_model_with_metadata(model_path)

        metadata_file_path = os.path.join(model_path, "explanation_metadata.json")
        saved_model_file_path = os.path.join(model_path, "saved_model.pb")
        self.assertTrue(os.path.isfile(metadata_file_path))
        self.assertTrue(os.path.isfile(saved_model_file_path))


if __name__ == "__main__":
    tf.test.main()
