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

import os
from unittest import mock

from google.cloud import aiplatform
import vertexai
from tests.system.aiplatform import e2e_base
from vertexai.preview._workflow.executor import training
from vertexai.preview._workflow.serialization_engine import (
    serializers,
)
import pytest
from sklearn.datasets import load_iris
import tensorflow as tf
from tensorflow import keras
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


# Wrap classes
keras.Sequential = vertexai.preview.remote(keras.Sequential)


@mock.patch.object(
    training,
    "VERTEX_AI_DEPENDENCY_PATH",
    "google-cloud-aiplatform[preview] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else "google-cloud-aiplatform[preview] @ git+https://github.com/googleapis/python-aiplatform.git@main",
)
@mock.patch.object(
    training,
    "VERTEX_AI_DEPENDENCY_PATH_AUTOLOGGING",
    "google-cloud-aiplatform[preview,autologging] @ git+https://github.com/googleapis/"
    f"python-aiplatform.git@{os.environ['KOKORO_GIT_COMMIT']}"
    if os.environ.get("KOKORO_GIT_COMMIT")
    else "google-cloud-aiplatform[preview,autologging] @ git+https://github.com/googleapis/python-aiplatform.git@main",
)
@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestRemoteExecutionTensorflow(e2e_base.TestEndToEnd):

    _temp_prefix = "temp-vertexai-remote-execution"

    def test_remote_execution_keras(self, shared_state):
        # Initialize vertexai
        vertexai.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        # Prepare dataset
        dataset = load_iris()

        X, X_retrain, y, y_retrain = train_test_split(
            dataset.data, dataset.target, test_size=0.60, random_state=42
        )
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.20, random_state=42
        )

        transformer = StandardScaler()
        X_train = transformer.fit_transform(X_train)
        X_test = transformer.transform(X_test)
        X_retrain = transformer.transform(X_retrain)

        tf_train_dataset = tf.data.Dataset.from_tensor_slices((X_train, y_train))
        tf_train_dataset = tf_train_dataset.shuffle(buffer_size=64).batch(32)

        tf_retrain_dataset = tf.data.Dataset.from_tensor_slices((X_retrain, y_retrain))
        tf_retrain_dataset = tf_retrain_dataset.shuffle(buffer_size=64).batch(32)

        tf_test_dataset = tf.data.Dataset.from_tensor_slices((X_test, y_test))
        tf_prediction_test_data = tf_test_dataset
        tf_remote_prediction_test_data = tf_prediction_test_data.batch(32)

        # Remote GPU training on Keras
        vertexai.preview.init(remote=True)

        model = keras.Sequential(
            [keras.layers.Dense(5, input_shape=(4,)), keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit.vertex.set_config(
            enable_cuda=True, display_name=self._make_display_name("keras-gpu-training")
        )
        model.fit(tf_train_dataset, epochs=10)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{model.fit.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "KerasModelSerializer"

        output_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "output/output_estimator")
        )
        assert output_estimator_metadata["serializer"] == "KerasModelSerializer"

        train_x_metadata = serializers._get_metadata(os.path.join(base_path, "input/x"))
        assert train_x_metadata["serializer"] == "TFDatasetSerializer"

        shared_state["resources"] = [remote_job]

        # Remote prediction on keras
        model.predict.vertex.remote_config.display_name = self._make_display_name(
            "keras-prediction"
        )
        model.predict(tf_remote_prediction_test_data)

        # Register trained model
        registered_model = vertexai.preview.register(model)
        shared_state["resources"].append(registered_model)

        # Load the registered model
        pulled_model = vertexai.preview.from_pretrained(
            model_name=registered_model.resource_name
        )

        # Uptrain the pretrained model on CPU
        pulled_model.fit.vertex.remote_config.enable_cuda = False
        pulled_model.fit.vertex.remote_config.display_name = self._make_display_name(
            "keras-cpu-uptraining"
        )
        pulled_model.fit(tf_retrain_dataset, epochs=10)

        # Assert the right serializer is being used
        remote_job = aiplatform.CustomJob.list(
            filter=f'display_name="{pulled_model.fit.vertex.remote_config.display_name}"'
        )[0]
        base_path = remote_job.job_spec.base_output_directory.output_uri_prefix

        input_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "input/input_estimator")
        )
        assert input_estimator_metadata["serializer"] == "KerasModelSerializer"

        output_estimator_metadata = serializers._get_metadata(
            os.path.join(base_path, "output/output_estimator")
        )
        assert output_estimator_metadata["serializer"] == "KerasModelSerializer"

        train_x_metadata = serializers._get_metadata(os.path.join(base_path, "input/x"))
        assert train_x_metadata["serializer"] == "TFDatasetSerializer"

        shared_state["resources"].append(remote_job)
