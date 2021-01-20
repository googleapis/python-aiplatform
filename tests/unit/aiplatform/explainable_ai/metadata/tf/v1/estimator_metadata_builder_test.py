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


"""Tests for estimator_metadata_builder."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import json
import os
import tensorflow.compat.v1 as tf
from google.cloud.aiplatform.explainable_ai.metadata.tf.v1 import (
    estimator_metadata_builder,
)


class EstimatorMetadataBuilderTest(tf.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super(EstimatorMetadataBuilderTest, cls).setUpClass()
        cls.language = tf.feature_column.categorical_column_with_vocabulary_list(
            key="language", vocabulary_list=("english", "korean"), num_oov_buckets=1
        )
        cls.language_indicator = tf.feature_column.indicator_column(cls.language)
        cls.language_embedding = tf.feature_column.embedding_column(
            cls.language, dimension=1
        )
        cls.language_weighted = tf.feature_column.weighted_categorical_column(
            cls.language, "language_weights"
        )

        cls.class_identity = tf.feature_column.categorical_column_with_identity(
            key="class_identity", num_buckets=4
        )
        cls.class_id_indicator = tf.feature_column.indicator_column(cls.class_identity)
        cls.language_x_class = tf.feature_column.crossed_column(
            [cls.language, cls.class_identity], 5000
        )

        cls.age = tf.feature_column.numeric_column(key="age", default_value=0.0)

    def _train_input_fn(self):
        """Train input function."""
        return (
            {
                "age": tf.constant([[1.0], [2.0], [3.0], [4.0]]),
                "language": tf.constant([["english"], ["english"], ["korean"], ["a"]]),
                "class_identity": tf.constant([[2], [3], [0], [1]]),
                "language_weights": tf.SparseTensor(
                    tf.constant([[0, 0], [1, 0], [2, 0], [3, 0]], dtype=tf.int64),
                    tf.constant([2, 3, 0, 1], dtype=tf.float32),
                    tf.constant([4, 1], dtype=tf.int64),
                ),
            },
            tf.constant([1, 0, 0, 1]),
        )

    def _get_json_serving_input_fn(self):
        inputs = {
            "age": tf.placeholder(shape=[None], name="age", dtype=tf.float32),
            "language": tf.placeholder(shape=[None], name="language", dtype=tf.string),
            "class_identity": tf.placeholder(
                shape=[None], name="class_identity", dtype=tf.int32
            ),
        }
        return tf.estimator.export.ServingInputReceiver(inputs, inputs)

    def _get_weighted_json_serving_input_fn(self):
        inputs = {
            "age": tf.placeholder(shape=[None], name="age", dtype=tf.float32),
            "language": tf.placeholder(shape=[None], name="language", dtype=tf.string),
            "class_identity": tf.placeholder(
                shape=[None], name="class_identity", dtype=tf.int32
            ),
            "language_weights": tf.sparse_placeholder(tf.float32),
        }
        return tf.estimator.export.ServingInputReceiver(inputs, inputs)

    def _assertMetadataEqualsWithPrefix(self, expected, actual):
        if isinstance(expected, dict) and isinstance(actual, dict):
            for key in expected:
                self.assertIn(key, actual)
                self._assertMetadataEqualsWithPrefix(expected[key], actual[key])
        elif isinstance(expected, list) and isinstance(actual, list):
            self.assertAllEqual(expected, actual)
        else:
            self.assertTrue(actual.startswith(expected))

    def test_save_model_with_metadata_no_encodings(self):
        columns = [self.age]
        boosted_tree = tf.estimator.BoostedTreesClassifier(columns, 5)
        boosted_tree.train(input_fn=self._train_input_fn, steps=5)
        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            boosted_tree, columns, self._get_json_serving_input_fn, "logits"
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        metadata_file_path = os.path.join(saved_path, b"explanation_metadata.json")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            generated_md = json.load(f)
        expected_md = {
            "outputs": {
                "logits": {"output_tensor_name": "boosted_trees/BoostedTreesPredict:0"}
            },
            "inputs": {
                "age": {
                    "input_tensor_name": "boosted_trees/transform_features/age/ExpandDims:0",
                    "encoding": "identity",
                }
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self._assertMetadataEqualsWithPrefix(expected_md, generated_md)

    def test_save_model_with_metadata_single_encoding_with_crossed(self):
        columns = [self.age, self.language_indicator, self.language_x_class]
        classifier_linear = tf.estimator.LinearClassifier(columns)
        classifier_linear.train(input_fn=self._train_input_fn, steps=5)
        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            classifier_linear,
            [self.age, self.language, self.class_identity],
            self._get_json_serving_input_fn,
            "probabilities",
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        metadata_file_path = os.path.join(saved_path, b"explanation_metadata.json")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            generated_md = json.load(f)
        expected_md = {
            "outputs": {
                "probabilities": {
                    "output_tensor_name": "linear/head/predictions/probabilities:0"
                }
            },
            "inputs": {
                "age": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/age/"
                    "ExpandDims:0",
                    "encoding": "identity",
                },
                "language": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity_X_language/hash_table_Lookup",
                    "encoding": "identity",
                    "indices_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity_X_language/to_sparse_input",
                    "dense_shape_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity_X_language/to_sparse_input",
                },
                "class_identity": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity_X_language",
                    "encoding": "identity",
                    "indices_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity_X_language/to_sparse_input_1",
                    "dense_shape_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity_X_language/to_sparse_input_1",
                },
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self._assertMetadataEqualsWithPrefix(expected_md, generated_md)

    def test_save_model_with_metadata_multiple_encodings(self):
        columns = [self.age, self.language_indicator, self.language_embedding]
        classifier_dnn = tf.estimator.DNNClassifier(
            hidden_units=[4], feature_columns=columns
        )
        classifier_dnn.train(input_fn=self._train_input_fn, steps=5)
        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            classifier_dnn,
            [self.age, self.language],
            self._get_json_serving_input_fn,
            "logits",
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        metadata_file_path = os.path.join(saved_path, b"explanation_metadata.json")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            generated_md = json.load(f)
        expected_md = {
            "outputs": {"logits": {"output_tensor_name": "dnn/logits/BiasAdd:0"}},
            "inputs": {
                "age": {
                    "input_tensor_name": "dnn/input_from_feature_columns/input_layer/age/"
                    "ExpandDims:0",
                    "encoding": "identity",
                },
                "language": {
                    "input_tensor_name": "dnn/input_from_feature_columns/input_layer/language_"
                    "embedding/hash_table_Lookup/",
                    "encoding": "identity",
                    "indices_tensor_name": "dnn/input_from_feature_columns/input_layer/language_"
                    "embedding/to_sparse_input/",
                    "dense_shape_tensor_name": "dnn/input_from_feature_columns/input_layer/language_"
                    "embedding/to_sparse_input",
                },
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self._assertMetadataEqualsWithPrefix(expected_md, generated_md)

    def test_save_model_with_metadata_weighted_column(self):
        columns = [self.age, self.language_weighted]
        classifier_linear = tf.estimator.LinearClassifier(columns)
        classifier_linear.train(input_fn=self._train_input_fn, steps=5)
        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            classifier_linear,
            [self.age, self.language],
            self._get_weighted_json_serving_input_fn,
            "logits",
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        metadata_file_path = os.path.join(saved_path, b"explanation_metadata.json")
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            generated_md = json.load(f)
        expected_md = {
            "outputs": {
                "logits": {
                    "output_tensor_name": "linear/linear_model/linear_model/linear_model/"
                    "weighted_sum:0"
                }
            },
            "inputs": {
                "age": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/age/"
                    "ExpandDims:0",
                    "encoding": "identity",
                },
                "language": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/hash_table_Lookup/",
                    "encoding": "combined_embedding",
                    "indices_tensor_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/to_sparse_input",
                    "dense_shape_tensor_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/to_sparse_input",
                    "encoded_tensor_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/weighted_sum",
                    "weight_values_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/cond",
                    "weight_indices_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/cond",
                    "weight_dense_shape_name": "linear/linear_model/linear_model/linear_model/language_"
                    "weighted_by_language_weights/cond",
                },
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self._assertMetadataEqualsWithPrefix(expected_md, generated_md)

    def test_save_model_with_metadata_multiple_tensor_groups(self):
        dnn_columns = [self.age, self.class_id_indicator]
        wide_columns = [self.age, self.class_identity]
        wide_deep_classifier = tf.estimator.DNNLinearCombinedClassifier(
            linear_feature_columns=wide_columns,
            dnn_feature_columns=dnn_columns,
            dnn_hidden_units=[4, 2],
        )
        wide_deep_classifier.train(input_fn=self._train_input_fn, steps=5)

        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            wide_deep_classifier,
            wide_columns,
            self._get_weighted_json_serving_input_fn,
            "logits",
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        metadata_file_path = os.path.join(saved_path, b"explanation_metadata.json")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            generated_md = json.load(f)
        expected_md = {
            "outputs": {"logits": {"output_tensor_name": "add:0"}},
            "inputs": {
                "age_dnn": {
                    "input_tensor_name": "dnn/input_from_feature_columns/input_layer/age/"
                    "ExpandDims:0",
                    "encoding": "identity",
                },
                "age_linear": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/age/"
                    "ExpandDims:0",
                    "encoding": "identity",
                },
                "class_identity_dnn": {
                    "input_tensor_name": "dnn/input_from_feature_columns/input_layer/class_identity_"
                    "indicator/",
                    "encoding": "combined_embedding",
                    "indices_tensor_name": "dnn/input_from_feature_columns/input_layer/class_identity_"
                    "indicator/to_sparse_input/",
                    "dense_shape_tensor_name": "dnn/input_from_feature_columns/input_layer/class_identity_"
                    "indicator/to_sparse_input/",
                    "encoded_tensor_name": "dnn/input_from_feature_columns/input_layer/class_identity_"
                    "indicator/",
                },
                "class_identity_linear": {
                    "input_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity/",
                    "encoding": "combined_embedding",
                    "indices_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity/to_sparse_input/",
                    "dense_shape_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity/to_sparse_input/",
                    "encoded_tensor_name": "linear/linear_model/linear_model/linear_model/class_"
                    "identity/weighted_sum/",
                },
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self._assertMetadataEqualsWithPrefix(expected_md, generated_md)

    def test_save_model_with_metadata_selected_columns(self):
        classifier_dnn = tf.estimator.DNNClassifier(
            hidden_units=[4],
            feature_columns=[
                self.age,
                self.language_indicator,
                self.language_embedding,
            ],
        )
        classifier_dnn.train(input_fn=self._train_input_fn, steps=5)

        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            classifier_dnn, [self.age], self._get_json_serving_input_fn, "logits"
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        metadata_file_path = os.path.join(saved_path, b"explanation_metadata.json")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            generated_md = json.load(f)
        expected_md = {
            "outputs": {"logits": {"output_tensor_name": "dnn/logits/BiasAdd:0"}},
            "inputs": {
                "age": {
                    "input_tensor_name": "dnn/input_from_feature_columns/input_layer/age/"
                    "ExpandDims:0",
                    "encoding": "identity",
                }
            },
            "framework": "Tensorflow",
            "tags": ["google.cloud.aiplatform.explainable_ai"],
        }
        self._assertMetadataEqualsWithPrefix(expected_md, generated_md)

    def test_save_model_with_metadata_estimator_saved(self):
        classifier_linear = tf.estimator.LinearClassifier([self.age, self.language])
        classifier_linear.train(input_fn=self._train_input_fn, steps=5)
        md_builder = estimator_metadata_builder.EstimatorMetadataBuilder(
            classifier_linear,
            [self.age, self.language],
            self._get_weighted_json_serving_input_fn,
            "logits",
        )
        saved_path = md_builder.save_model_with_metadata(tf.test.get_temp_dir())
        proto_file_path = os.path.join(saved_path, b"saved_model.pb")
        self.assertTrue(os.path.isfile(proto_file_path))
        variables_dir_path = os.path.join(saved_path, b"variables")
        self.assertTrue(os.path.isdir(variables_dir_path))

    def test_constructor_empty_feature_columns(self):
        with self.assertRaisesRegex(ValueError, "feature_columns cannot be empty"):
            estimator_metadata_builder.EstimatorMetadataBuilder(
                tf.estimator.LinearClassifier([self.age, self.language]),
                [],
                self._get_json_serving_input_fn,
                "logits",
            )

    def test_constructor_none_estimator(self):
        with self.assertRaisesRegex(
            ValueError, "A valid estimator needs to be provided"
        ):
            estimator_metadata_builder.EstimatorMetadataBuilder(
                None, [], self._get_json_serving_input_fn, "logits"
            )


if __name__ == "__main__":
    tf.test.main()
