# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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


import tensorflow as tf

from google.cloud.aiplatform.explain.metadata.tf.v2 import saved_model_metadata_builder


class SavedModelMetadataBuilderTest(tf.test.TestCase):
    def _set_up(self):
        self.seq_model = tf.keras.models.Sequential()
        self.seq_model.add(tf.keras.layers.Dense(32, activation="relu", input_dim=10))
        self.seq_model.add(tf.keras.layers.Dense(32, activation="relu"))
        self.seq_model.add(tf.keras.layers.Dense(1, activation="sigmoid"))
        self.saved_model_path = self.get_temp_dir()
        tf.saved_model.save(self.seq_model, self.saved_model_path)

    def test_get_metadata_sequential(self):
        self._set_up()
        builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.saved_model_path
        )
        generated_md = builder.get_metadata()
        expected_md = {
            "outputs": {"dense_2": {"outputTensorName": "dense_2"}},
            "inputs": {"dense_input": {"inputTensorName": "dense_input"}},
        }
        assert expected_md == generated_md
