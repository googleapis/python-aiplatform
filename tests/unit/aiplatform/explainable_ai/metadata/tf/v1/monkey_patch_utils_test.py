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


"""Tests for monkey_patch_utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tensorflow.compat.v1 as tf
from google.cloud.aiplatform.explainable_ai.metadata.tf.v1 import monkey_patch_utils
from tensorflow_estimator.python.estimator.canned import prediction_keys


class MonkeyPatchUtilsTest(tf.test.TestCase):
    @classmethod
    def setUpClass(cls):
        super(MonkeyPatchUtilsTest, cls).setUpClass()
        language = tf.feature_column.categorical_column_with_vocabulary_list(
            key="language", vocabulary_list=("english", "korean"), num_oov_buckets=1
        )
        language_weighted = tf.feature_column.weighted_categorical_column(
            language, "language_weights"
        )
        language_embedding = tf.feature_column.embedding_column(language, dimension=1)
        language_indicator = tf.feature_column.indicator_column(language)

        class_identity = tf.feature_column.categorical_column_with_identity(
            key="class_identity", num_buckets=4
        )

        class_id_indicator = tf.feature_column.indicator_column(class_identity)

        language_x_class = tf.feature_column.crossed_column(
            [language, class_identity], 5000
        )

        crossed_embedding = tf.feature_column.embedding_column(
            language_x_class, dimension=2
        )

        age = tf.feature_column.numeric_column(key="age", default_value=0.0)
        bucketized_age_column = tf.feature_column.bucketized_column(
            source_column=age, boundaries=[2, 3]
        )
        embedded_bucketized_age = tf.feature_column.embedding_column(
            bucketized_age_column, dimension=2
        )
        cls.columns = [
            age,
            language_embedding,
            language_indicator,
            crossed_embedding,
            class_id_indicator,
            bucketized_age_column,
            embedded_bucketized_age,
        ]
        cls.base_columns = [age, language, class_identity]

        cls.classifier_dnn = tf.estimator.DNNClassifier(
            hidden_units=[4], feature_columns=cls.columns
        )

        cls.classifier_dnn.train(input_fn=cls._train_input_fn, steps=5)

        cls.classifier_linear = tf.estimator.LinearClassifier(cls.base_columns)
        cls.classifier_linear.train(input_fn=cls._train_input_fn, steps=5)

        cls.weighted_linear = tf.estimator.LinearClassifier(
            cls.base_columns + [language_weighted]
        )
        cls.weighted_linear.train(input_fn=cls._train_input_fn, steps=5)

        cls.regressor = tf.estimator.DNNRegressor(
            hidden_units=[4], feature_columns=cls.columns
        )

        cls.regressor.train(input_fn=cls._train_input_fn, steps=5)

        cls.wide_deep_classifier = tf.estimator.DNNLinearCombinedClassifier(
            linear_feature_columns=cls.base_columns,
            dnn_feature_columns=cls.columns,
            dnn_hidden_units=[4, 2],
        )

        cls.wide_deep_classifier.train(input_fn=cls._train_input_fn, steps=5)

        cls.boosted_tree = tf.estimator.BoostedTreesClassifier(
            [age, language_indicator, class_id_indicator], 5
        )
        cls.boosted_tree.train(input_fn=cls._train_input_fn, steps=5)

    @classmethod
    def _train_input_fn(cls):
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

    def test_exporting_context_dnn_classifier(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context("logits"):
            self.classifier_dnn.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        feature_tensors_dict = patcher.feature_tensors_dict
        self.assertLen(feature_tensors_dict, 3)
        for fc in self.base_columns:
            self.assertIn(fc.name, feature_tensors_dict)
            self.assertLen(feature_tensors_dict[fc.name], 1)
        self.assertEmpty(feature_tensors_dict["age"][0].encoded_tensors)
        self.assertLen(feature_tensors_dict["language"][0].encoded_tensors, 3)
        self.assertLen(feature_tensors_dict["class_identity"][0].encoded_tensors, 2)
        self.assertLen(patcher.crossed_columns, 2)
        self.assertLen(patcher.output_tensors_dict, 1)

    def test_exporting_context_linear_classifier(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context("logits"):
            self.classifier_linear.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        feature_tensors_dict = patcher.feature_tensors_dict
        self.assertLen(feature_tensors_dict, 3)
        for fc in self.base_columns:
            self.assertIn(fc.name, feature_tensors_dict)
            self.assertLen(feature_tensors_dict[fc.name], 1)
        self.assertEmpty(feature_tensors_dict["age"][0].encoded_tensors)
        self.assertLen(feature_tensors_dict["language"][0].encoded_tensors, 1)
        self.assertLen(feature_tensors_dict["class_identity"][0].encoded_tensors, 1)
        self.assertEmpty(patcher.crossed_columns)
        self.assertLen(patcher.output_tensors_dict, 1)

    def test_exporting_context_wide_deep(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context("logits"):
            self.wide_deep_classifier.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        feature_tensors_dict = patcher.feature_tensors_dict
        self.assertLen(feature_tensors_dict, 3)
        for fc in self.base_columns:
            self.assertIn(fc.name, feature_tensors_dict)
            self.assertLen(feature_tensors_dict[fc.name], 2)
        self.assertEmpty(feature_tensors_dict["age"][0].encoded_tensors)
        self.assertLen(feature_tensors_dict["language"][0].encoded_tensors, 3)
        self.assertLen(feature_tensors_dict["class_identity"][0].encoded_tensors, 2)
        self.assertLen(patcher.crossed_columns, 2)
        self.assertLen(patcher.output_tensors_dict, 1)

    def test_exporting_context_weighted_column(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context("logits"):
            self.weighted_linear.export_saved_model(
                tf.test.get_temp_dir(), self._get_weighted_json_serving_input_fn
            )
        feature_tensors_dict = patcher.feature_tensors_dict
        self.assertLen(feature_tensors_dict, 3)
        self.assertLen(feature_tensors_dict["language"][0].input_tensor, 2)

    def test_observe_with_boosted_trees(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context("logits"):
            self.boosted_tree.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        feature_tensors_dict = patcher.feature_tensors_dict
        self.assertLen(feature_tensors_dict, 3)
        for fc in self.base_columns:
            self.assertIn(fc.name, feature_tensors_dict)
            self.assertLen(feature_tensors_dict[fc.name], 1)
            self.assertEmpty(feature_tensors_dict[fc.name][0].encoded_tensors)
        self.assertEmpty(patcher.crossed_columns)
        self.assertLen(patcher.output_tensors_dict, 1)

    def test_exporting_context_incorrect_output_key(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with self.assertRaisesRegex(ValueError, "Output key .* is not found"):
            with patcher.exporting_context("none"):
                self.regressor.export_saved_model(
                    tf.test.get_temp_dir(), self._get_json_serving_input_fn
                )

    def test_exporting_context_export_works_after_exception(self):
        try:
            patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
            with patcher.exporting_context("none"):
                self.classifier_dnn.export_saved_model(
                    tf.test.get_temp_dir(), self._get_json_serving_input_fn
                )
        except ValueError:
            path = self.classifier_dnn.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        # Folder should contain 'saved_model.pb' and 'variables' files.
        self.assertLen(os.listdir(path), 2)

    def test_exporting_context_no_output_key_regressor(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context():
            self.regressor.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        self.assertIn(
            prediction_keys.PredictionKeys.PREDICTIONS, patcher.output_tensors_dict
        )

    def test_exporting_context_no_output_key_classifier(self):
        patcher = monkey_patch_utils.EstimatorMonkeyPatchHelper()
        with patcher.exporting_context():
            self.classifier_dnn.export_saved_model(
                tf.test.get_temp_dir(), self._get_json_serving_input_fn
            )
        self.assertIn(
            prediction_keys.PredictionKeys.LOGITS, patcher.output_tensors_dict
        )


if __name__ == "__main__":
    tf.test.main()
