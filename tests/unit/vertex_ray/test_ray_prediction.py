"""Tests for prediction."""

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

import importlib
import pickle
import tempfile

from google.cloud import aiplatform
from google.cloud.aiplatform.vertex_ray.predict import (
    sklearn as prediction_sklearn,
)
from google.cloud.aiplatform.vertex_ray.predict import (
    tensorflow as prediction_tensorflow,
)
from google.cloud.aiplatform.vertex_ray.predict import (
    torch as prediction_torch,
)
from google.cloud.aiplatform.vertex_ray.predict import (
    xgboost as prediction_xgboost,
)
from google.cloud.aiplatform.utils import gcs_utils
import test_constants as tc
import test_prediction_utils

import mock
import numpy as np
import pytest
import ray
import tensorflow as tf
import torch
import xgboost


@pytest.fixture()
def upload_tensorflow_saved_model_mock():
    with mock.patch.object(
        aiplatform.Model, "upload_tensorflow_saved_model"
    ) as upload_tensorflow_saved_model_mock:
        upload_tensorflow_saved_model_mock.return_value = None
        yield upload_tensorflow_saved_model_mock


@pytest.fixture()
def ray_tensorflow_checkpoint():
    defined_model = test_prediction_utils.get_tensorflow_trained_model()
    checkpoint = ray.train.tensorflow.TensorflowCheckpoint.from_model(defined_model)
    return checkpoint


@pytest.fixture()
def ray_checkpoint_from_dict():
    try:
        return ray.train.Checkpoint.from_directory("/tmp/checkpoint")
    except AttributeError:
        raise RuntimeError("Unsupported Ray version.")


@pytest.fixture()
def save_tf_model():
    with mock.patch.object(tf.keras.Model, "save") as save_tf_model_mock:
        save_tf_model_mock.return_value = None
        yield save_tf_model_mock


@pytest.fixture()
def ray_sklearn_checkpoint():
    if ray.__version__ >= "2.42.0":
        return None
    else:
        estimator = test_prediction_utils.get_sklearn_estimator()
        temp_dir = tempfile.mkdtemp()
        checkpoint = ray.train.sklearn.SklearnCheckpoint.from_estimator(
            estimator, path=temp_dir
        )
        return checkpoint


@pytest.fixture()
def ray_xgboost_checkpoint():
    if ray.__version__ == "2.9.3":
        from ray.train import xgboost as ray_xgboost

        model = test_prediction_utils.get_xgboost_model()
        checkpoint = ray_xgboost.XGBoostCheckpoint.from_model(model.get_booster())
        return checkpoint
    else:
        return None


@pytest.fixture()
def pickle_dump():
    with mock.patch.object(pickle, "dump") as pickle_dump:
        pickle_dump.return_value = None
        yield pickle_dump


@pytest.fixture
def mock_vertex_model():
    model = mock.MagicMock(aiplatform.Model)
    model.uri = tc.ProjectConstants.TEST_MODEL_GCS_URI
    model.container_spec.image_uri = "us-docker.xxx/sklearn-cpu.1-0:latest"
    model.labels = {"registered_by_vertex_ai": "true"}
    yield model


@pytest.fixture()
def upload_sklearn_mock(mock_vertex_model):
    with mock.patch.object(
        aiplatform.Model, "upload_scikit_learn_model_file"
    ) as upload_sklearn_mock:
        upload_sklearn_mock.return_value = mock_vertex_model
        yield upload_sklearn_mock


@pytest.fixture
def mock_xgboost_vertex_model():
    model = mock.MagicMock(aiplatform.Model)
    model.uri = tc.ProjectConstants.TEST_MODEL_GCS_URI
    model.container_spec.image_uri = "us-docker.xxx/xgboost-cpu.1-6:latest"
    model.labels = {"registered_by_vertex_ai": "true"}
    yield model


@pytest.fixture()
def upload_xgboost_mock(mock_xgboost_vertex_model):
    with mock.patch.object(
        aiplatform.Model, "upload_xgboost_model_file"
    ) as upload_xgboost_mock:
        upload_xgboost_mock.return_value = mock_xgboost_vertex_model
        yield upload_xgboost_mock


@pytest.fixture()
def gcs_utils_upload_to_gcs():
    with mock.patch.object(gcs_utils, "upload_to_gcs") as gcs_utils_upload_to_gcs:
        gcs_utils.return_value = None
        yield gcs_utils_upload_to_gcs


@pytest.fixture()
def ray_torch_checkpoint():
    defined_model = test_prediction_utils.get_pytorch_trained_model()
    checkpoint = ray.train.torch.TorchCheckpoint.from_model(defined_model)
    return checkpoint


@pytest.mark.usefixtures("google_auth_mock")
class TestPredictionFunctionality:
    """Tests for Prediction."""

    def setup_method(self):
        importlib.reload(aiplatform.initializer)
        importlib.reload(aiplatform)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    # Tensorflow Tests
    @tc.rovminversion
    def test_convert_checkpoint_to_tf_model_raise_exception(
        self, ray_checkpoint_from_dict
    ) -> None:
        """Test if a checkpoint is not an instance of TensflowCheckpoint should
        fail with exception ValueError."""
        with pytest.raises(ValueError) as ve:
            prediction_tensorflow.register._get_tensorflow_model_from(
                ray_checkpoint_from_dict
            )

        assert ve.match(
            regexp=r".* arg checkpoint should be a "
            "ray.train.tensorflow.TensorflowCheckpoint .*"
        )

    @tc.rovminversion
    def test_convert_checkpoint_to_tensorflow_model_succeed(
        self, ray_tensorflow_checkpoint
    ) -> None:
        """Test if a TensorflowCheckpoint conversion is successful."""
        # Act
        model = prediction_tensorflow.register._get_tensorflow_model_from(
            ray_tensorflow_checkpoint, model=test_prediction_utils.create_tf_model
        )

        # Assert
        assert model is not None
        values = model.predict([[1, 1, 1, 1]])
        assert values[0] is not None

    @tc.rovminversion
    def test_register_tensorflow_succeed(
        self,
        ray_tensorflow_checkpoint,
        upload_tensorflow_saved_model_mock,
        save_tf_model,
    ) -> None:
        """Test if a TensorflowCheckpoint upload is successful."""
        # Act
        prediction_tensorflow.register_tensorflow(
            ray_tensorflow_checkpoint,
            artifact_uri=tc.ProjectConstants.TEST_ARTIFACT_URI,
            _model=test_prediction_utils.create_tf_model,
            use_gpu=False,
        )

        # Assert
        upload_tensorflow_saved_model_mock.assert_called_once()
        save_tf_model.assert_called_once_with(
            f"{tc.ProjectConstants.TEST_ARTIFACT_URI}/ray-on-vertex-registered-tensorflow-model"
        )

    @tc.rovminversion
    def test_register_tensorflow_initialized_succeed(
        self,
        ray_tensorflow_checkpoint,
        upload_tensorflow_saved_model_mock,
        save_tf_model,
    ) -> None:
        """Test if a TensorflowCheckpoint upload is successful when artifact_uri is None but initialized."""
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )
        # Act
        prediction_tensorflow.register_tensorflow(
            ray_tensorflow_checkpoint,
            _model=test_prediction_utils.create_tf_model,
            use_gpu=False,
        )

        # Assert
        upload_tensorflow_saved_model_mock.assert_called_once()
        save_tf_model.assert_called_once_with(
            f"{tc.ProjectConstants.TEST_ARTIFACT_URI}/ray-on-vertex-registered-tensorflow-model"
        )

    def test_register_tensorflowartifact_uri_is_none_raise_error(
        self, ray_tensorflow_checkpoint
    ) -> None:
        """Test if a TensorflowCheckpoint upload gives ValueError."""
        # Act and Assert
        with pytest.raises(ValueError) as ve:
            prediction_tensorflow.register_tensorflow(
                checkpoint=ray_tensorflow_checkpoint,
                artifact_uri=None,
                _model=test_prediction_utils.create_tf_model,
            )
        assert ve.match(regexp=r".*'artifact_uri' should " "start with 'gs://'.*")

    def test_register_tensorflowartifact_uri_not_gcs_uri_raise_error(
        self, ray_tensorflow_checkpoint
    ) -> None:
        """Test if a TensorflowCheckpoint upload gives ValueError."""
        # Act and Assert
        with pytest.raises(ValueError) as ve:
            prediction_tensorflow.register_tensorflow(
                checkpoint=ray_tensorflow_checkpoint,
                artifact_uri=tc.ProjectConstants.TEST_BAD_ARTIFACT_URI,
                _model=test_prediction_utils.create_tf_model,
            )
        assert ve.match(regexp=r".*'artifact_uri' should " "start with 'gs://'.*")

    # Sklearn Tests
    @tc.rovminversion
    @tc.predictionrayversion
    def test_convert_checkpoint_to_sklearn_raise_exception(
        self, ray_checkpoint_from_dict
    ) -> None:
        """Test if a checkpoint is not an instance of SklearnCheckpoint should
        fail with exception ValueError."""

        with pytest.raises(ValueError) as ve:
            prediction_sklearn.register._get_estimator_from(ray_checkpoint_from_dict)
        assert ve.match(
            regexp=r".* arg checkpoint should be a "
            "ray.train.sklearn.SklearnCheckpoint .*"
        )

    @tc.rovminversion
    @tc.predictionrayversion
    def test_convert_checkpoint_to_sklearn_model_succeed(
        self, ray_sklearn_checkpoint
    ) -> None:
        """Test if a SklearnCheckpoint conversion is successful."""
        # Act
        estimator = prediction_sklearn.register._get_estimator_from(
            ray_sklearn_checkpoint
        )

        # Assert
        assert estimator is not None
        y_pred = estimator.predict([[10, 11]])
        assert y_pred[0] is not None

    @tc.rovminversion
    @tc.predictionrayversion
    def test_register_sklearn_succeed(
        self,
        ray_sklearn_checkpoint,
        upload_sklearn_mock,
        pickle_dump,
        gcs_utils_upload_to_gcs,
    ) -> None:
        """Test if a SklearnCheckpoint upload is successful."""
        # Act
        vertex_ai_model = prediction_sklearn.register_sklearn(
            ray_sklearn_checkpoint,
            artifact_uri=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )

        # Assert
        vertex_ai_model.uri = tc.ProjectConstants.TEST_MODEL_GCS_URI
        vertex_ai_model.container_spec.image_uri = (
            "us-docker.xxx/sklearn-cpu.1-0:latest"
        )
        upload_sklearn_mock.assert_called_once()
        pickle_dump.assert_called_once()
        gcs_utils_upload_to_gcs.assert_called_once()

    @tc.rovminversion
    @tc.predictionrayversion
    def test_register_sklearn_initialized_succeed(
        self,
        ray_sklearn_checkpoint,
        upload_sklearn_mock,
        pickle_dump,
        gcs_utils_upload_to_gcs,
    ) -> None:
        """Test if a SklearnCheckpoint upload is successful when artifact_uri is None but initialized."""
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )
        # Act
        vertex_ai_model = prediction_sklearn.register_sklearn(
            ray_sklearn_checkpoint,
        )

        # Assert
        vertex_ai_model.uri = tc.ProjectConstants.TEST_MODEL_GCS_URI
        vertex_ai_model.container_spec.image_uri = (
            "us-docker.xxx/sklearn-cpu.1-0:latest"
        )
        upload_sklearn_mock.assert_called_once()
        pickle_dump.assert_called_once()
        gcs_utils_upload_to_gcs.assert_called_once()

    @tc.predictionrayversion
    def test_register_sklearnartifact_uri_is_none_raise_error(
        self, ray_sklearn_checkpoint
    ) -> None:
        """Test if a SklearnCheckpoint upload gives ValueError."""
        # Act and Assert
        with pytest.raises(ValueError) as ve:
            prediction_sklearn.register_sklearn(
                checkpoint=ray_sklearn_checkpoint,
                artifact_uri=None,
            )
        assert ve.match(regexp=r".*'artifact_uri' should " "start with 'gs://'.*")

    @tc.predictionrayversion
    def test_register_sklearnartifact_uri_not_gcs_uri_raise_error(
        self, ray_sklearn_checkpoint
    ) -> None:
        """Test if a SklearnCheckpoint upload gives ValueError."""
        # Act and Assert
        with pytest.raises(ValueError) as ve:
            prediction_sklearn.register_sklearn(
                checkpoint=ray_sklearn_checkpoint,
                artifact_uri=tc.ProjectConstants.TEST_BAD_ARTIFACT_URI,
            )
        assert ve.match(regexp=r".*'artifact_uri' should " "start with 'gs://'.*")

    # XGBoost Tests
    @tc.xgbversion
    @tc.rovminversion
    def test_convert_checkpoint_to_xgboost_raise_exception(
        self, ray_checkpoint_from_dict
    ) -> None:
        """Test if a checkpoint is not an instance of XGBoostCheckpoint should

        fail with exception ValueError.
        """

        with pytest.raises(ValueError) as ve:
            prediction_xgboost.register._get_xgboost_model_from(
                ray_checkpoint_from_dict
            )
        assert ve.match(
            regexp=r".* arg checkpoint should be a "
            "ray.train.xgboost.XGBoostCheckpoint .*"
        )

    @tc.xgbversion
    def test_convert_checkpoint_to_xgboost_model_succeed(
        self, ray_xgboost_checkpoint
    ) -> None:
        """Test if a XGBoostCheckpoint conversion is successful."""
        # Act
        model = prediction_xgboost.register._get_xgboost_model_from(
            ray_xgboost_checkpoint
        )

        # Assert
        assert model is not None
        y_pred = model.predict(xgboost.DMatrix(np.array([[1, 2]])))
        assert y_pred[0] is not None

    @tc.xgbversion
    def test_register_xgboost_succeed(
        self,
        ray_xgboost_checkpoint,
        upload_xgboost_mock,
        pickle_dump,
        gcs_utils_upload_to_gcs,
    ) -> None:
        """Test if a XGBoostCheckpoint upload is successful."""
        # Act
        vertex_ai_model = prediction_xgboost.register_xgboost(
            ray_xgboost_checkpoint,
            artifact_uri=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )

        # Assert
        vertex_ai_model.uri = tc.ProjectConstants.TEST_MODEL_GCS_URI
        vertex_ai_model.container_spec.image_uri = (
            "us-docker.xxx/xgboost-cpu.1-6:latest"
        )
        upload_xgboost_mock.assert_called_once()
        pickle_dump.assert_called_once()
        gcs_utils_upload_to_gcs.assert_called_once()

    @tc.xgbversion
    def test_register_xgboost_initialized_succeed(
        self,
        ray_xgboost_checkpoint,
        upload_xgboost_mock,
        pickle_dump,
        gcs_utils_upload_to_gcs,
    ) -> None:
        """Test if a XGBoostCheckpoint upload is successful when artifact_uri is None but initialized."""
        aiplatform.init(
            project=tc.ProjectConstants.TEST_GCP_PROJECT_ID,
            staging_bucket=tc.ProjectConstants.TEST_ARTIFACT_URI,
        )
        # Act
        vertex_ai_model = prediction_xgboost.register_xgboost(
            ray_xgboost_checkpoint,
        )

        # Assert
        vertex_ai_model.uri = tc.ProjectConstants.TEST_MODEL_GCS_URI
        vertex_ai_model.container_spec.image_uri = (
            "us-docker.xxx/xgboost-cpu.1-6:latest"
        )
        upload_xgboost_mock.assert_called_once()
        pickle_dump.assert_called_once()
        gcs_utils_upload_to_gcs.assert_called_once()

    @tc.xgbversion
    def test_register_xgboostartifact_uri_is_none_raise_error(
        self, ray_xgboost_checkpoint
    ) -> None:
        """Test if a XGBoostCheckpoint upload gives ValueError."""
        # Act and Assert
        with pytest.raises(ValueError) as ve:
            prediction_xgboost.register_xgboost(
                checkpoint=ray_xgboost_checkpoint,
                artifact_uri=None,
            )
        assert ve.match(regexp=r".*'artifact_uri' should " "start with 'gs://'.*")

    @tc.xgbversion
    def test_register_xgboostartifact_uri_not_gcs_uri_raise_error(
        self, ray_xgboost_checkpoint
    ) -> None:
        """Test if a XGBoostCheckpoint upload gives ValueError."""
        # Act and Assert
        with pytest.raises(ValueError) as ve:
            prediction_xgboost.register_xgboost(
                checkpoint=ray_xgboost_checkpoint,
                artifact_uri=tc.ProjectConstants.TEST_BAD_ARTIFACT_URI,
            )
        assert ve.match(regexp=r".*'artifact_uri' should " "start with 'gs://'.*")

    # Pytorch Tests
    @tc.rovminversion
    def test_convert_checkpoint_to_torch_model_raises_exception(
        self, ray_checkpoint_from_dict
    ) -> None:
        """Test if a checkpoint is not an instance of TorchCheckpoint should
        fail with exception ValueError."""
        with pytest.raises(ValueError):
            prediction_torch.register.get_pytorch_model_from(ray_checkpoint_from_dict)

    @tc.predictionrayversion
    def test_convert_checkpoint_to_pytorch_model_succeed(
        self, ray_torch_checkpoint
    ) -> None:
        """Test if a TorchCheckpoint conversion is successful."""
        # Act
        model = prediction_torch.register.get_pytorch_model_from(ray_torch_checkpoint)

        # Assert
        assert model is not None
        values = model(torch.tensor([10000], dtype=torch.float))
        print(values[0])
        assert values[0] is not None
