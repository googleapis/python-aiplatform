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

import random

from google.cloud import aiplatform
from google.cloud.aiplatform import models
from google.cloud.aiplatform.constants import prediction
from tests.system.aiplatform import e2e_base
import numpy as np
import pytest
import sklearn
from sklearn.linear_model import LinearRegression
import tensorflow as tf
import xgboost as xgb


CONTAINER_MAP = prediction._SERVING_CONTAINER_URI_MAP[
    e2e_base._LOCATION.split("-", 1)[0]
]


@pytest.mark.usefixtures(
    "prepare_staging_bucket", "delete_staging_bucket", "tear_down_resources"
)
class TestExperimentModel(e2e_base.TestEndToEnd):

    _temp_prefix = "test-vertex-sdk-e2e-experiment-model"
    registered_models_cpu = []
    registered_models_gpu = []

    def test_sklearn_model(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        model = LinearRegression()
        model.fit(train_x, train_y)

        # Test save sklearn model
        aiplatform.save_model(model, "sk-model")

        # Test get ExperimentModel with aritfact id
        model_artifact = aiplatform.get_experiment_model("sk-model")
        assert model_artifact.uri.endswith("sklearn-model")

        shared_state["resources"] = [model_artifact]

        # Test get model info from ExperimentModel
        model_info = model_artifact.get_model_info()
        assert model_info == {
            "model_class": "sklearn.linear_model._base.LinearRegression",
            "framework_name": "sklearn",
            "framework_version": sklearn.__version__,
        }

        # Test load model and make prediction
        loaded_model = model_artifact.load_model()
        preds = loaded_model.predict(train_x)
        assert isinstance(preds, np.ndarray)

        # Test register model
        # Check the highest pre-built container's version, if lower than the
        # ML framework version, use the highest version we have.
        version, container_uri = max(CONTAINER_MAP["sklearn"]["cpu"].items())
        if version >= sklearn.__version__:
            registered_model = model_artifact.register_model()
        else:
            registered_model = model_artifact.register_model(
                serving_container_image_uri=container_uri
            )
        assert registered_model.display_name.startswith("sklearn model")

        self.registered_models_cpu.append(registered_model)
        shared_state["resources"].append(registered_model)

    def test_xgboost_booster_with_custom_uri(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.array([1, 1, 0, 0])
        dtrain = xgb.DMatrix(data=train_x, label=train_y)
        booster = xgb.train(
            params={"num_parallel_tree": 4, "subsample": 0.5, "num_class": 2},
            dtrain=dtrain,
        )

        # Test save xgboost booster model with custom uri
        uri = f"gs://{shared_state['staging_bucket_name']}/custom-uri"
        aiplatform.save_model(
            model=booster,
            artifact_id="xgb-booster",
            uri=uri,
        )

        # Test get ExperimentModel with aritfact id
        model_artifact = aiplatform.get_experiment_model("xgb-booster")
        assert model_artifact.uri == uri

        shared_state["resources"].append(model_artifact)

        # Test get model info from ExperimentModel
        model_info = model_artifact.get_model_info()
        assert model_info == {
            "model_class": "xgboost.core.Booster",
            "framework_name": "xgboost",
            "framework_version": xgb.__version__,
        }

        # Test load model and make prediction
        loaded_model = model_artifact.load_model()
        preds = loaded_model.predict(xgb.DMatrix(data=train_x))
        assert isinstance(preds, np.ndarray)

        # Test register model
        # Check the highest pre-built container's version, if lower than the
        # ML framework version, use the highest version we have.
        version, container_uri = max(CONTAINER_MAP["xgboost"]["cpu"].items())
        if version >= xgb.__version__:
            registered_model = model_artifact.register_model()
        else:
            registered_model = model_artifact.register_model(
                serving_container_image_uri=container_uri
            )
        assert registered_model.display_name.startswith("xgboost model")

        self.registered_models_cpu.append(registered_model)
        shared_state["resources"].append(registered_model)

    def test_xgboost_xgbmodel_with_custom_names(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.array([1, 1, 0, 0])
        xgb_model = xgb.XGBClassifier()
        xgb_model.fit(train_x, train_y)

        # Test save xgboost xgbmodel with custom display_name
        aiplatform.save_model(
            model=xgb_model,
            artifact_id="xgboost-xgbmodel",
            display_name="custom-experiment-model-name",
        )

        # Test get ExperimentModel with aritfact id
        model_artifact = aiplatform.get_experiment_model("xgboost-xgbmodel")
        assert model_artifact.uri.endswith("xgboost-model")
        assert model_artifact.display_name == "custom-experiment-model-name"

        shared_state["resources"].append(model_artifact)

        # Test get model info from ExperimentModel
        model_info = model_artifact.get_model_info()
        assert model_info == {
            "model_class": "xgboost.sklearn.XGBClassifier",
            "framework_name": "xgboost",
            "framework_version": xgb.__version__,
        }

        # Test load model and make prediction
        loaded_model = model_artifact.load_model()
        preds = loaded_model.predict(train_x)
        assert isinstance(preds, np.ndarray)

        # Test register model with custom display name
        # Check the highest pre-built container's version, if lower than the
        # ML framework version, use the highest version we have.
        version, container_uri = max(CONTAINER_MAP["xgboost"]["cpu"].items())
        if version >= xgb.__version__:
            registered_model = model_artifact.register_model(
                display_name="custom-registered-model-name",
            )
        else:
            registered_model = model_artifact.register_model(
                serving_container_image_uri=container_uri,
                display_name="custom-registered-model-name",
            )
        assert registered_model.display_name == "custom-registered-model-name"

        self.registered_models_cpu.append(registered_model)
        shared_state["resources"].append(registered_model)

    def test_tensorflow_keras_model_with_input_example(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        train_x = np.random.random((100, 2))
        train_y = np.random.random((100, 1))
        model = tf.keras.Sequential(
            [tf.keras.layers.Dense(5, input_shape=(2,)), tf.keras.layers.Softmax()]
        )
        model.compile(optimizer="adam", loss="mean_squared_error")
        model.fit(train_x, train_y)

        # Test save tf.keras model with input example
        aiplatform.save_model(
            model=model,
            artifact_id="keras-model",
            input_example=train_x,
        )

        # Test get ExperimentModel with aritfact id
        model_artifact = aiplatform.get_experiment_model("keras-model")
        assert model_artifact.uri.endswith("tensorflow-model")

        shared_state["resources"].append(model_artifact)

        # Test get model info from ExperimentModel
        model_info = model_artifact.get_model_info()
        assert model_info == {
            "model_class": "tensorflow.keras.Model",
            "framework_name": "tensorflow",
            "framework_version": tf.__version__,
            "input_example": {
                "data": train_x[:5].tolist(),
                "type": "numpy.ndarray",
            },
        }

        # Test load model and make prediction
        loaded_model = model_artifact.load_model()
        preds = loaded_model.predict(train_x)
        assert isinstance(preds, np.ndarray)

        # Test register model
        # Check the highest pre-built container's version, if lower than the
        # ML framework version, use the highest version we have.
        version, container_uri = max(CONTAINER_MAP["tensorflow"]["cpu"].items())
        if version >= tf.__version__:
            registered_model = model_artifact.register_model()
        else:
            registered_model = model_artifact.register_model(
                serving_container_image_uri=container_uri
            )
        assert registered_model.display_name.startswith("tensorflow model")

        self.registered_models_cpu.append(registered_model)
        shared_state["resources"].append(registered_model)

    def test_tensorflow_module_with_gpu_container(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        class Adder(tf.Module):
            @tf.function(
                input_signature=[
                    tf.TensorSpec(
                        shape=[
                            2,
                        ],
                        dtype=tf.float32,
                    )
                ]
            )
            def add(self, x):
                return x + x

        model = Adder()

        # Test save tf.Module model
        aiplatform.save_model(model, "tf-module")

        # Test get ExperimentModel with aritfact id
        model_artifact = aiplatform.get_experiment_model("tf-module")
        assert model_artifact.uri.endswith("tensorflow-model")

        shared_state["resources"].append(model_artifact)

        # Test get model info from ExperimentModel
        model_info = model_artifact.get_model_info()
        assert model_info == {
            "model_class": "tensorflow.Module",
            "framework_name": "tensorflow",
            "framework_version": tf.__version__,
        }

        # Test load model and make prediction
        loaded_model = model_artifact.load_model()
        preds = loaded_model.add([1, 2])
        assert isinstance(preds, tf.Tensor)

        # Test register model with gpu container
        # Check the highest pre-built container's version, if lower than the
        # ML framework version, use the highest version we have.
        version, container_uri = max(CONTAINER_MAP["tensorflow"]["gpu"].items())
        if version >= tf.__version__:
            registered_model = model_artifact.register_model(use_gpu=True)
        else:
            registered_model = model_artifact.register_model(
                serving_container_image_uri=container_uri,
                use_gpu=True,
            )
        assert registered_model.display_name.startswith("tensorflow model")

        self.registered_models_gpu.append(registered_model)
        shared_state["resources"].append(registered_model)

    def test_deploy_model_with_cpu_container(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        # It takes long time to deploy a model. To reduce the system test run
        # time, we randomly choose one registered model to test deployment.
        registered_model = random.choice(self.registered_models_cpu)

        # Deploy the registered model
        endpoint = registered_model.deploy()

        pred = endpoint.predict([[1, 2]])
        assert isinstance(pred, models.Prediction)
        shared_state["resources"].append(endpoint)

    def test_deploy_model_with_gpu_container(self, shared_state):
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            staging_bucket=f"gs://{shared_state['staging_bucket_name']}",
        )

        # It takes long time to deploy a model. To reduce the system test run
        # time, we randomly choose one registered model to test deployment.
        registered_model = random.choice(self.registered_models_gpu)

        # Deploy the registered model
        # Since we are using gpu, we need to specify accelerator_type and count
        endpoint = registered_model.deploy(
            accelerator_type="NVIDIA_TESLA_T4", accelerator_count=1, sync=False
        )

        pred = endpoint.predict([[1, 2]])
        assert isinstance(pred, models.Prediction)
        shared_state["resources"].append(endpoint)
