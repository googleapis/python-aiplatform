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

import pytest
import tensorflow.compat.v1 as tf

from google.cloud.aiplatform import models
from google.cloud.aiplatform.explain.metadata.tf.v1 import saved_model_metadata_builder
from google.cloud.aiplatform.compat.types import explanation_metadata

import test_models
from test_models import upload_model_mock, get_model_mock  # noqa: F401


class SavedModelMetadataBuilderTF1Test(tf.test.TestCase):
    def _set_up(self):
        self.sess = tf.Session(graph=tf.Graph())
        with self.sess.graph.as_default():
            self.x = tf.placeholder(shape=[None, 10], dtype=tf.float32, name="inp")
            weights = tf.constant(1.0, shape=(10, 2), name="weights")
            bias_weight = tf.constant(1.0, shape=(2,), name="bias")
            self.linear_layer = tf.add(tf.matmul(self.x, weights), bias_weight)
            self.prediction = tf.nn.relu(self.linear_layer)
            # save the model
            self.model_path = self.get_temp_dir()
            builder = tf.saved_model.builder.SavedModelBuilder(self.model_path)
            tensor_info_x = tf.saved_model.utils.build_tensor_info(self.x)
            tensor_info_pred = tf.saved_model.utils.build_tensor_info(self.prediction)
            tensor_info_lin = tf.saved_model.utils.build_tensor_info(self.linear_layer)
            prediction_signature = tf.saved_model.signature_def_utils.build_signature_def(
                inputs={"x": tensor_info_x},
                outputs={"y": tensor_info_pred},
                method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME,
            )
            double_output_signature = tf.saved_model.signature_def_utils.build_signature_def(
                inputs={"x": tensor_info_x},
                outputs={"y": tensor_info_pred, "lin": tensor_info_lin},
                method_name=tf.saved_model.signature_constants.PREDICT_METHOD_NAME,
            )

            builder.add_meta_graph_and_variables(
                self.sess,
                [tf.saved_model.tag_constants.SERVING],
                signature_def_map={
                    tf.saved_model.signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY: prediction_signature,
                    "double": double_output_signature,
                },
            )
            builder.save()

    def test_get_metadata_correct_inputs(self):
        self._set_up()
        md_builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.model_path, tags=[tf.saved_model.tag_constants.SERVING]
        )
        expected_md = {
            "inputs": {"x": {"inputTensorName": "inp:0"}},
            "outputs": {"y": {"outputTensorName": "Relu:0"}},
        }

        assert md_builder.get_metadata() == expected_md

    def test_get_metadata_protobuf_correct_inputs(self):
        self._set_up()
        md_builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.model_path, tags=[tf.saved_model.tag_constants.SERVING]
        )
        expected_object = explanation_metadata.ExplanationMetadata(
            inputs={"x": {"input_tensor_name": "inp:0"}},
            outputs={"y": {"output_tensor_name": "Relu:0"}},
        )

        assert md_builder.get_metadata_protobuf() == expected_object

    def test_get_metadata_double_output(self):
        self._set_up()
        md_builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.model_path, signature_name="double", outputs_to_explain=["lin"]
        )

        expected_md = {
            "inputs": {"x": {"inputTensorName": "inp:0"}},
            "outputs": {"lin": {"outputTensorName": "Add:0"}},
        }

        assert md_builder.get_metadata() == expected_md

    def test_get_metadata_protobuf_double_output(self):
        self._set_up()
        md_builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.model_path, signature_name="double", outputs_to_explain=["lin"]
        )

        expected_object = explanation_metadata.ExplanationMetadata(
            inputs={"x": {"input_tensor_name": "inp:0"}},
            outputs={"lin": {"output_tensor_name": "Add:0"}},
        )

        assert md_builder.get_metadata_protobuf() == expected_object

    @pytest.mark.usefixtures("upload_model_mock", "get_model_mock")
    def test_model_upload_compatibility(self):
        self._set_up()
        md_builder = saved_model_metadata_builder.SavedModelMetadataBuilder(
            self.model_path, tags=[tf.saved_model.tag_constants.SERVING]
        )

        generated_md = md_builder.get_metadata_protobuf()

        try:
            models.Model.upload(
                display_name=test_models._TEST_MODEL_NAME,
                serving_container_image_uri=test_models._TEST_SERVING_CONTAINER_IMAGE,
                explanation_parameters=test_models._TEST_EXPLANATION_PARAMETERS,
                explanation_metadata=generated_md,  # Test metadata from builder
                labels=test_models._TEST_LABEL,
            )
        except TypeError as e:
            if "Parameter to MergeFrom() must be instance of same class" in str(e):
                pytest.fail(
                    f"Model.upload() expects different proto version, more info: {e}"
                )
            else:
                raise e
