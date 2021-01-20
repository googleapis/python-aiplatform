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


"""Tests for metadata utils."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import tensorflow.compat.v1 as tf
from google.cloud.aiplatform.explainable_ai.metadata.tf.v1 import utils


class UtilsTest(tf.test.TestCase):
    def test_save_graph_model_explicit_session(self):
        sess = tf.Session(graph=tf.Graph())
        with sess.graph.as_default():
            x = tf.placeholder(shape=[None, 10], dtype=tf.float32, name="inp")
            weights = tf.constant(1.0, shape=(10, 2), name="weights")
        model_path = os.path.join(tf.test.get_temp_dir(), "explicit")
        utils.save_graph_model(sess, model_path, {"x": x}, {"w": weights}, ["tag"])
        self.assertTrue(os.path.isfile(os.path.join(model_path, "saved_model.pb")))
        tf.reset_default_graph()
        loading_session = tf.Session(graph=tf.Graph())
        with loading_session.graph.as_default():
            tf.saved_model.loader.load(loading_session, ["tag"], model_path)
            self.assertIn(
                x.op.name, [n.name for n in loading_session.graph.as_graph_def().node]
            )
            self.assertIn(
                weights.op.name,
                [n.name for n in loading_session.graph.as_graph_def().node],
            )

    def test_save_graph_model_default_session(self):
        x = tf.placeholder(shape=[None, 10], dtype=tf.float32, name="inp")
        weights = tf.constant(1.0, shape=(10, 2), name="weights")
        model_path = os.path.join(tf.test.get_temp_dir(), "default")
        utils.save_graph_model(
            tf.Session(), model_path, {"x": x}, {"w": weights}, ["tag"]
        )
        self.assertTrue(os.path.isfile(os.path.join(model_path, "saved_model.pb")))

    def test_save_graph_model_kwargs(self):
        x = tf.placeholder(shape=[None, 10], dtype=tf.float32, name="inp")
        weights = tf.constant(1.0, shape=(10, 2), name="weights")
        model_path = os.path.join(tf.test.get_temp_dir(), "kwargs")
        utils.save_graph_model(
            tf.Session(),
            model_path,
            {"x": x},
            {"w": weights},
            ["tag"],
            main_op=tf.tables_initializer(),
            strip_default_attrs=False,
        )
        self.assertTrue(os.path.isfile(os.path.join(model_path, "saved_model.pb")))


if __name__ == "__main__":
    tf.test.main()
