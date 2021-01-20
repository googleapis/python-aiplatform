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

"""Tests for google3.third_party.explainable_ai_sdk.sdk.metadata.utils."""
import json
import os
import sys
import tensorflow as tf
from google.cloud.aiplatform.explainable_ai.metadata import utils
from absl import flags


class UtilsTest(tf.test.TestCase):
    @classmethod
    def setUpClass(cls):
        tmpdir_flag = flags.FLAGS["test_tmpdir"]
        tmpdir_flag.parse(tmpdir_flag.value)

    def test_write_metadata_to_file(self):
        sample_dict = {"a": 123, "b": "123", "c": {"d": 0.12}}
        temp_folder = self.create_tempdir().full_path
        utils.write_metadata_to_file(sample_dict, temp_folder)
        metadata_file_path = os.path.join(temp_folder, "explanation_metadata.json")
        self.assertTrue(os.path.isfile(metadata_file_path))
        with tf.io.gfile.GFile(metadata_file_path, "r") as f:
            written_md = json.load(f)
        self.assertEqual(sample_dict, written_md)


if __name__ == "__main__":
    tf.test.main()
