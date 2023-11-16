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

from importlib import reload
import json
import os
import pickle
import types
from unittest.mock import ANY

import cloudpickle
from google.cloud import aiplatform
import vertexai
from google.cloud.aiplatform.utils import gcs_utils
from vertexai.preview._workflow.serialization_engine import (
    any_serializer as any_serializer_lib,
)
from vertexai.preview._workflow.serialization_engine import (
    serializers,
)
from vertexai.preview._workflow.shared import constants
from vertexai.preview._workflow.shared import (
    supported_frameworks,
)

import mock
import numpy as np
import pandas as pd
from pyfakefs import fake_filesystem_unittest
import pytest
from sklearn.linear_model import _logistic
import tensorflow as tf
from tensorflow import keras
import torch


@pytest.fixture
def mock_isvalid_gcs_path():
    """Allow using a local path in test."""
    with mock.patch.object(
        serializers,
        "_is_valid_gcs_path",
        autospec=True,
        return_value=True,
    ) as always_return_true_mock_path_check:
        yield always_return_true_mock_path_check


@pytest.fixture
def cloudpickle_serializer():
    return serializers.CloudPickleSerializer()


@pytest.fixture
def any_serializer():
    return any_serializer_lib.AnySerializer()


@pytest.fixture
def sklearn_estimator_serializer():
    return serializers.SklearnEstimatorSerializer()


@pytest.fixture
def keras_model_serializer():
    return serializers.KerasModelSerializer()


@pytest.fixture
def keras_history_callback_serializer():
    return serializers.KerasHistoryCallbackSerializer()


@pytest.fixture
def torch_model_serializer():
    return serializers.TorchModelSerializer()


@pytest.fixture
def pandas_data_serializer():
    return serializers.PandasDataSerializer()


@pytest.fixture
def torch_dataloader_serializer():
    return serializers.TorchDataLoaderSerializer()


@pytest.fixture
def bigframe_serializer():
    return serializers.BigframeSerializer()


@pytest.fixture
def tf_dataset_serializer():
    return serializers.TFDatasetSerializer()


@pytest.fixture
def mock_keras_model_deserialize():
    with mock.patch.object(
        serializers.KerasModelSerializer, "deserialize", autospec=True
    ) as keras_model_deserialize:
        yield keras_model_deserialize


@pytest.fixture
def mock_sklearn_estimator_serialize():
    def stateful_serialize(self, to_serialize, gcs_path):
        del self, to_serialize, gcs_path
        serializers.SklearnEstimatorSerializer._metadata.dependencies = [
            "sklearn_dependency1==1.0.0"
        ]

    with mock.patch.object(
        serializers.SklearnEstimatorSerializer,
        "serialize",
        new=stateful_serialize,
    ) as sklearn_estimator_serialize:
        yield sklearn_estimator_serialize
        serializers.SklearnEstimatorSerializer._metadata.dependencies = []


@pytest.fixture
def mock_sklearn_estimator_deserialize():
    with mock.patch.object(
        serializers.SklearnEstimatorSerializer, "deserialize", autospec=True
    ) as sklearn_estimator_deserialize:
        yield sklearn_estimator_deserialize


@pytest.fixture
def mock_torch_model_serialize():
    def stateful_serialize(self, to_serialize, gcs_path):
        del self, to_serialize, gcs_path
        serializers.TorchModelSerializer._metadata.dependencies = ["torch==1.0.0"]

    with mock.patch.object(
        serializers.TorchModelSerializer, "serialize", new=stateful_serialize
    ) as torch_model_serialize:
        yield torch_model_serialize
        serializers.TorchModelSerializer._metadata.dependencies = []


@pytest.fixture
def mock_torch_model_deserialize():
    with mock.patch.object(
        serializers.TorchModelSerializer, "deserialize", autospec=True
    ) as torch_model_deserialize:
        yield torch_model_deserialize


@pytest.fixture
def mock_torch_dataloader_serialize(tmp_path):
    def stateful_serialize(self, to_serialize, gcs_path):
        del self, to_serialize, gcs_path
        serializers.TorchDataLoaderSerializer._metadata.dependencies = ["torch==1.0.0"]

    with mock.patch.object(
        serializers.TorchDataLoaderSerializer, "serialize", new=stateful_serialize
    ) as torch_dataloader_serialize:
        yield torch_dataloader_serialize
        serializers.TorchDataLoaderSerializer._metadata.dependencies = []


@pytest.fixture
def mock_torch_dataloader_deserialize():
    with mock.patch.object(
        serializers.TorchDataLoaderSerializer, "deserialize", autospec=True
    ) as torch_dataloader_serializer:
        yield torch_dataloader_serializer


@pytest.fixture
def mock_download_from_gcs_for_torch_dataloader(tmp_path, torch_dataloader_serializer):
    def fake_download_from_gcs(serialized_gcs_path, temp_dir):
        dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor([[1, 2, 3] for i in range(100)]),
                torch.tensor([1] * 100),
            ),
            batch_size=10,
            shuffle=True,
        )
        torch_dataloader_serializer._serialize_to_local(
            dataloader, os.fspath(tmp_path / temp_dir)
        )

    with mock.patch.object(
        gcs_utils, "download_from_gcs", new=fake_download_from_gcs
    ) as download_from_gcs:
        yield download_from_gcs


@pytest.fixture
def mock_download_from_gcs_for_keras_model(tmp_path):
    def fake_download_from_gcs(serialized_gcs_path, temp_dir):
        keras_model = keras.models.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )
        keras_model.save(tmp_path / temp_dir, save_format="tf")

    with mock.patch.object(
        gcs_utils, "download_from_gcs", new=fake_download_from_gcs
    ) as download_from_gcs:
        yield download_from_gcs


@pytest.fixture
def mock_tf_dataset_serialize(tmp_path):
    def stateful_serialize(self, to_serialize, gcs_path):
        del gcs_path
        serializers.TFDatasetSerializer._metadata.dependencies = ["tensorflow==1.0.0"]
        try:
            to_serialize.save(str(tmp_path / "tf_dataset"))
        except AttributeError:
            tf.data.experimental.save(to_serialize, str(tmp_path / "tf_dataset"))

    with mock.patch.object(
        serializers.TFDatasetSerializer, "serialize", new=stateful_serialize
    ) as tf_dataset_serialize:
        yield tf_dataset_serialize
        serializers.TFDatasetSerializer._metadata.dependencies = []


@pytest.fixture
def mock_tf_dataset_deserialize():
    with mock.patch.object(
        serializers.TFDatasetSerializer, "deserialize", autospec=True
    ) as tf_dataset_serializer:
        yield tf_dataset_serializer


@pytest.fixture
def mock_pandas_data_serialize():
    def stateful_serialize(self, to_serialize, gcs_path):
        del self, to_serialize, gcs_path
        serializers.PandasDataSerializer._metadata.dependencies = ["pandas==1.0.0"]

    with mock.patch.object(
        serializers.PandasDataSerializer, "serialize", new=stateful_serialize
    ) as data_serialize:
        yield data_serialize
        serializers.PandasDataSerializer._metadata.dependencies = []


@pytest.fixture
def mock_pandas_data_deserialize():
    with mock.patch.object(
        serializers.PandasDataSerializer, "deserialize", autospec=True
    ) as pandas_data_deserialize:
        yield pandas_data_deserialize


@pytest.fixture
def mock_bigframe_deserialize_sklearn():
    with mock.patch.object(
        serializers.BigframeSerializer, "_deserialize_sklearn", autospec=True
    ) as bigframe_deserialize_sklearn:
        yield bigframe_deserialize_sklearn


@pytest.fixture
def mock_keras_save_model():
    with mock.patch.object(keras.models.Sequential, "save") as keras_save_model:
        yield keras_save_model


@pytest.fixture
def mock_keras_load_model():
    with mock.patch("tensorflow.keras.models.load_model") as keras_load_model:
        yield keras_load_model


@pytest.fixture
def mock_torch_save_model():
    with mock.patch.object(torch, "save", autospec=True) as torch_save_model:
        yield torch_save_model


@pytest.fixture
def mock_torch_load_model():
    with mock.patch.object(torch, "load", autospec=True) as torch_load_model:
        yield torch_load_model


@pytest.fixture
def mock_upload_to_gcs():
    with mock.patch.object(gcs_utils, "upload_to_gcs", autospec=True) as upload_to_gcs:
        yield upload_to_gcs


@pytest.fixture
def mock_json_dump():
    with mock.patch.object(json, "dump", autospec=True) as json_dump:
        yield json_dump


@pytest.fixture
def mock_cloudpickle_dump():
    with mock.patch.object(cloudpickle, "dump", autospec=True) as cloudpickle_dump:
        yield cloudpickle_dump


class TestTorchClass(torch.nn.Module):
    def __init__(self, input_size=4):
        super().__init__()
        self.linear_relu_stack = torch.nn.Sequential(
            torch.nn.Linear(input_size, 3), torch.nn.ReLU(), torch.nn.Linear(3, 2)
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits


class TestSklearnEstimatorSerializer:
    def setup_method(self):
        reload(vertexai)
        reload(vertexai.preview.initializer)
        reload(_logistic)

    def teardown_method(self):
        aiplatform.initializer.global_pool.shutdown(wait=True)

    @pytest.mark.usefixtures("mock_storage_blob", "google_auth_mock")
    def test_serialize_path_start_with_gs(self, sklearn_estimator_serializer):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        sklearn_estimator = _logistic.LogisticRegression()
        sklearn_estimator.fit(train_x, train_y)

        # Act
        sklearn_estimator_serializer.serialize(sklearn_estimator, fake_gcs_uri)

        # Assert
        # The serialized file is written to a local path "fake_gcs_uri" via
        # mock_upload_to_gcs for hermicity.
        with open(fake_gcs_uri.split("/")[-1], "rb") as f:
            restored_estimator = pickle.load(f)

        assert isinstance(restored_estimator, _logistic.LogisticRegression)
        assert sklearn_estimator.get_params() == restored_estimator.get_params()
        assert (sklearn_estimator.coef_ == restored_estimator.coef_).all()

    def test_serialize_path_start_with_gcs(self, sklearn_estimator_serializer):
        # Arrange
        fake_gcs_uri = "/gcs/staging-bucket/fake_gcs_uri"

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        sklearn_estimator = _logistic.LogisticRegression()
        sklearn_estimator.fit(train_x, train_y)

        # Act
        with fake_filesystem_unittest.Patcher() as filesystem:
            filesystem.fs.create_file(fake_gcs_uri)
            sklearn_estimator_serializer.serialize(sklearn_estimator, fake_gcs_uri)

            # Assert
            # The serialized file is written to a local path "fake_gcs_uri" via
            # mock_upload_to_gcs for hermicity.
            with open(fake_gcs_uri, "rb") as f:
                restored_estimator = pickle.load(f)

            assert isinstance(restored_estimator, _logistic.LogisticRegression)
            assert sklearn_estimator.get_params() == restored_estimator.get_params()
            assert (sklearn_estimator.coef_ == restored_estimator.coef_).all()

    def test_serialize_invalid_gcs_path(self, sklearn_estimator_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        sklearn_estimator = _logistic.LogisticRegression()
        sklearn_estimator.fit(train_x, train_y)

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            sklearn_estimator_serializer.serialize(sklearn_estimator, fake_gcs_uri)

    @pytest.mark.usefixtures("mock_storage_blob", "google_auth_mock")
    def test_deserialize_path_start_with_gs(
        self, sklearn_estimator_serializer, mock_storage_blob
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        sklearn_estimator = _logistic.LogisticRegression()
        sklearn_estimator.fit(train_x, train_y)

        def fake_download_file_from_gcs(self, filename):
            with open(filename, "wb") as f:
                pickle.dump(sklearn_estimator, f)

        mock_storage_blob.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob
        )

        # Act
        restored_estimator = sklearn_estimator_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert isinstance(restored_estimator, _logistic.LogisticRegression)
        assert sklearn_estimator.get_params() == restored_estimator.get_params()
        assert (sklearn_estimator.coef_ == restored_estimator.coef_).all()

    def test_deserialize_path_start_with_gcs(self, sklearn_estimator_serializer):
        # Arrange
        fake_gcs_uri = "/gcs/staging-bucket/fake_gcs_uri"

        train_x = np.array([[1, 1], [1, 2], [2, 2], [2, 3]])
        train_y = np.dot(train_x, np.array([1, 2])) + 3
        sklearn_estimator = _logistic.LogisticRegression()
        sklearn_estimator.fit(train_x, train_y)

        with fake_filesystem_unittest.Patcher() as filesystem:
            filesystem.fs.create_file(fake_gcs_uri)
            with open(fake_gcs_uri, "wb") as f:
                pickle.dump(sklearn_estimator, f)
            # Act
            restored_estimator = sklearn_estimator_serializer.deserialize(fake_gcs_uri)

            # Assert
            assert isinstance(restored_estimator, _logistic.LogisticRegression)
            assert sklearn_estimator.get_params() == restored_estimator.get_params()
            assert (sklearn_estimator.coef_ == restored_estimator.coef_).all()

    def test_deserialize_invalid_gcs_path(self, sklearn_estimator_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            sklearn_estimator_serializer.deserialize(fake_gcs_uri)


class TestKerasModelSerializer:
    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir")
    def test_serialize_gcs_path_default_save_format(
        self, keras_model_serializer, tmp_path
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        keras_model = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )

        # Act
        keras_model_serializer.serialize(keras_model, fake_gcs_uri)

        # Assert
        # We mocked the storage blob, which writes the content to a temp path
        # instead of fake_gcs_uri. The same filename will be used, though.
        saved_keras_model_path = tmp_path / "fake_gcs_uri.keras"
        assert os.path.exists(saved_keras_model_path)
        saved_keras_model = keras.models.load_model(saved_keras_model_path)
        assert isinstance(saved_keras_model, keras.models.Sequential)

    @pytest.mark.parametrize("save_format", ["keras", "h5"], ids=["keras", "h5"])
    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir")
    def test_serialize_gcs_path(self, keras_model_serializer, tmp_path, save_format):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        keras_model = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )

        # Act
        keras_model_serializer.serialize(
            keras_model, fake_gcs_uri, save_format=save_format
        )

        # Assert
        # We mocked the storage blob, which writes the content to a temp path
        # instead of fake_gcs_uri. The same filename will be used, though.
        saved_keras_model_path = tmp_path / ("fake_gcs_uri." + save_format)
        assert os.path.exists(saved_keras_model_path)
        saved_keras_model = keras.models.load_model(saved_keras_model_path)
        assert isinstance(saved_keras_model, keras.models.Sequential)

    @pytest.mark.usefixtures("mock_gcs_upload", "mock_isvalid_gcs_path")
    def test_serialize_gcs_path_tf_format(self, keras_model_serializer, tmp_path):
        # Arrange
        fake_gcs_uri = str(tmp_path / "fake_gcs_uri")

        keras_model = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )

        # Act
        keras_model_serializer.serialize(keras_model, fake_gcs_uri, save_format="tf")

        # Assert
        # We mocked the storage blob, which writes the content to a temp path
        # instead of fake_gcs_uri. The same filename will be used, though.
        saved_keras_model_path = tmp_path / ("fake_gcs_uri")
        assert os.path.exists(saved_keras_model_path)
        saved_keras_model = keras.models.load_model(saved_keras_model_path)
        assert isinstance(saved_keras_model, keras.models.Sequential)

    def test_serialize_invalid_gcs_path(self, keras_model_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        keras_model = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            keras_model_serializer.serialize(keras_model, fake_gcs_uri)

    @pytest.mark.parametrize("save_format", ["keras", "h5"], ids=["keras", "h5"])
    def test_deserialize_gcs_path(
        self,
        keras_model_serializer,
        mock_storage_blob_tmp_dir,
        mock_keras_load_model,
        save_format,
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        # This only mocks the metadata loading.
        def fake_download_file_from_gcs(self, filename):
            with open(filename, "w") as f:
                json.dump({"save_format": save_format}, f)

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        _ = keras_model_serializer.deserialize(fake_gcs_uri)

        # Assert
        # We didn't mock the loading process with concrete data, so we simply
        # test that it's called.
        mock_keras_load_model.assert_called_once()

    @pytest.mark.usefixtures("mock_download_from_gcs_for_keras_model")
    def test_deserialize_tf_format(
        self,
        keras_model_serializer,
        mock_storage_blob_tmp_dir,
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        # This only mocks the metadata loading.
        def fake_download_file_from_gcs(self, filename):
            with open(filename, "w") as f:
                json.dump({"save_format": "tf"}, f)

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        loaded_keras_model = keras_model_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert isinstance(loaded_keras_model, keras.models.Sequential)

    def test_deserialize_invalid_gcs_path(self, keras_model_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            keras_model_serializer.deserialize(fake_gcs_uri)


class TestKerasHistoryCallbackSerializer:
    @pytest.mark.usefixtures("mock_isvalid_gcs_path")
    def test_serialize_gcs_path(self, keras_history_callback_serializer, tmp_path):
        # Arrange
        fake_gcs_uri = tmp_path / "fake_gcs_uri"

        keras_model = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )
        history = keras.callbacks.History()
        history.history = {"loss": [1.0, 0.5, 0.2]}
        history.params = {"verbose": 1, "epochs": 3, "steps": 1}
        history.epoch = [0, 1, 2]
        history.model = keras_model

        # Act
        keras_history_callback_serializer.serialize(history, str(fake_gcs_uri))

        with open(tmp_path / "fake_gcs_uri", "rb") as f:
            deserialized = cloudpickle.load(f)

        assert "model" not in deserialized
        assert deserialized["history"]["loss"] == history.history["loss"]
        assert deserialized["params"] == history.params
        assert deserialized["epoch"] == history.epoch

    def test_serialize_invalid_gcs_path(self, keras_history_callback_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        history = keras.callbacks.History()

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            keras_history_callback_serializer.serialize(history, fake_gcs_uri)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_gcs_path(
        self,
        keras_history_callback_serializer,
        mock_storage_blob_tmp_dir,
        tmp_path,
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        _ = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )
        history = keras.callbacks.History()
        history.history = {"loss": [1.0, 0.5, 0.2]}
        history.params = {"verbose": 1, "epochs": 3, "steps": 1}
        history.epoch = [0, 1, 2]

        def fake_download_file_from_gcs(self, filename):
            with open(tmp_path / filename, "wb") as f:
                cloudpickle.dump(
                    history.__dict__,
                    f,
                )

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_history = keras_history_callback_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert isinstance(restored_history, keras.callbacks.History)
        assert restored_history.model is None

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_gcs_path_with_model(
        self,
        keras_history_callback_serializer,
        mock_storage_blob_tmp_dir,
        tmp_path,
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        keras_model = keras.Sequential(
            [keras.layers.Dense(8, input_shape=(2,)), keras.layers.Dense(4)]
        )
        history = keras.callbacks.History()
        history.history = {"loss": [1.0, 0.5, 0.2]}
        history.params = {"verbose": 1, "epochs": 3, "steps": 1}
        history.epoch = [0, 1, 2]

        def fake_download_file_from_gcs(self, filename):
            with open(tmp_path / filename, "wb") as f:
                cloudpickle.dump(
                    history.__dict__,
                    f,
                )

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_history = keras_history_callback_serializer.deserialize(
            fake_gcs_uri, model=keras_model
        )

        # Assert
        assert isinstance(restored_history, keras.callbacks.History)
        assert restored_history.model == keras_model

    def test_deserialize_invalid_gcs_path(self, keras_history_callback_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            keras_history_callback_serializer.deserialize(fake_gcs_uri)


class TestTorchModelSerializer:
    def test_serialize_path_start_with_gs(
        self, torch_model_serializer, mock_torch_save_model, mock_upload_to_gcs
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        torch_model = TestTorchClass()

        # Act
        torch_model_serializer.serialize(torch_model, fake_gcs_uri)

        # Assert
        mock_torch_save_model.assert_called_once_with(
            torch_model,
            ANY,
            pickle_module=cloudpickle,
            pickle_protocol=constants.PICKLE_PROTOCOL,
        )

        mock_upload_to_gcs.assert_called_once_with(ANY, fake_gcs_uri)

    def test_serialize_path_start_with_gcs(
        self, torch_model_serializer, mock_torch_save_model
    ):
        # Arrange
        fake_gcs_uri = "/gcs/staging-bucket/fake_gcs_uri"

        torch_model = TestTorchClass()

        # Act

        torch_model_serializer.serialize(torch_model, fake_gcs_uri)

        # Assert
        mock_torch_save_model.assert_called_once_with(
            torch_model,
            fake_gcs_uri,
            pickle_module=cloudpickle,
            pickle_protocol=constants.PICKLE_PROTOCOL,
        )

    def test_serialize_invalid_gcs_path(self, torch_model_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        torch_model = TestTorchClass()

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            torch_model_serializer.serialize(torch_model, fake_gcs_uri)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_path_start_with_gs(
        self, torch_model_serializer, mock_storage_blob_tmp_dir, tmp_path
    ):
        # TorchModelSerializer only supports torch>=2.0, which supports python>=3.8
        # Skip this test for python 3.7
        if supported_frameworks._get_python_minor_version() == "3.7":
            return

        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        torch_model = TestTorchClass()

        def fake_download_file_from_gcs(self, filename):
            torch.save(
                torch_model,
                os.fspath(tmp_path / filename),
                pickle_module=cloudpickle,
                pickle_protocol=constants.PICKLE_PROTOCOL,
            )

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_model = torch_model_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert isinstance(restored_model, TestTorchClass)
        assert str(torch_model.state_dict()) == str(restored_model.state_dict())

    def test_deserialize_path_start_with_gcs(
        self, torch_model_serializer, mock_torch_load_model
    ):
        # TorchModelSerializer only supports torch>=2.0, which supports python>=3.8
        # Skip this test for python 3.7
        if supported_frameworks._get_python_minor_version() == "3.7":
            return

        # Arrange
        fake_gcs_uri = "/gcs/staging-bucket/fake_gcs_uri"

        # Act
        _ = torch_model_serializer.deserialize(fake_gcs_uri)

        # Assert
        mock_torch_load_model.assert_called_once_with(
            fake_gcs_uri,
            map_location=None,
        )

    def test_deserialize_invalid_gcs_path(self, torch_model_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            torch_model_serializer.deserialize(fake_gcs_uri)


class TestTorchDataLoaderSerializer:
    def test_serialize_dataloader(
        self,
        torch_dataloader_serializer,
        mock_json_dump,
        mock_cloudpickle_dump,
        mock_upload_to_gcs,
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor([[1, 2, 3] for i in range(100)]),
                torch.tensor([1] * 100),
            ),
            batch_size=10,
            shuffle=True,
        )

        # Act
        torch_dataloader_serializer.serialize(dataloader, fake_gcs_uri)

        # Assert
        mock_json_dump.assert_called_once_with(
            {
                "batch_size": dataloader.batch_size,
                "num_workers": dataloader.num_workers,
                "pin_memory": dataloader.pin_memory,
                "drop_last": dataloader.drop_last,
                "timeout": dataloader.timeout,
                "prefetch_factor": dataloader.prefetch_factor,
                "persistent_workers": dataloader.persistent_workers,
                "pin_memory_device": dataloader.pin_memory_device,
                "generator_device": None,
            },
            ANY,
        )

        assert mock_cloudpickle_dump.call_count == 4

        mock_upload_to_gcs.assert_called_once_with(ANY, fake_gcs_uri)

    def test_serialize_invalid_gcs_path(self, torch_dataloader_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor([[1, 2, 3] for i in range(100)]),
                torch.tensor([1] * 100),
            ),
            batch_size=10,
            shuffle=True,
        )

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            torch_dataloader_serializer.serialize(dataloader, fake_gcs_uri)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_dataloader(
        self,
        torch_dataloader_serializer,
        mock_download_from_gcs_for_torch_dataloader,
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri"

        expected_dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor([[1, 2, 3] for i in range(100)]),
                torch.tensor([1] * 100),
            ),
            batch_size=10,
            shuffle=True,
        )

        # Act
        dataloader = torch_dataloader_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert dataloader.batch_size == expected_dataloader.batch_size
        assert dataloader.num_workers == expected_dataloader.num_workers
        assert dataloader.pin_memory == expected_dataloader.pin_memory
        assert dataloader.drop_last == expected_dataloader.drop_last
        assert dataloader.timeout == expected_dataloader.timeout
        assert dataloader.prefetch_factor == expected_dataloader.prefetch_factor
        assert dataloader.persistent_workers == expected_dataloader.persistent_workers

    def test_deserialize_invalid_gcs_path(self, torch_dataloader_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            torch_dataloader_serializer.deserialize(fake_gcs_uri)


class TestCloudPickleSerializer:
    @pytest.mark.usefixtures("mock_storage_blob", "google_auth_mock")
    def test_serialize_func(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.cpkl"

        def function_to_be_serialized():
            return "return_str"

        # Act
        cloudpickle_serializer.serialize(function_to_be_serialized, fake_gcs_uri)

        # Assert
        del function_to_be_serialized
        # The serialized file is written to a local path "fake_gcs_uri.cpkl" via
        # mock_upload_to_gcs for hermicity.
        with open(fake_gcs_uri.split("/")[-1], "rb") as f:
            restored_fn = cloudpickle.load(f)
        assert restored_fn() == "return_str"

    def test_serialize_func_path_start_with_gcs(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "/gcs/staging-bucket/fake_gcs_uri.cpkl"

        def function_to_be_serialized():
            return "return_str"

        # Act
        with fake_filesystem_unittest.Patcher() as filesystem:
            filesystem.fs.create_file(fake_gcs_uri)
            cloudpickle_serializer.serialize(function_to_be_serialized, fake_gcs_uri)

            # Assert
            del function_to_be_serialized
            # The serialized file is written to a local path "fake_gcs_uri.cpkl" via
            # mock_upload_to_gcs for hermicity.
            with open(fake_gcs_uri, "rb") as f:
                restored_fn = cloudpickle.load(f)
            assert restored_fn() == "return_str"

    def test_serialize_invalid_gcs_path(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri.cpkl"

        def function_to_be_serialized():
            return "return_str"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            cloudpickle_serializer.serialize(function_to_be_serialized, fake_gcs_uri)

    @pytest.mark.usefixtures("mock_storage_blob", "google_auth_mock")
    def test_serialize_object(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.cpkl"

        class TestClass:
            def test_method(self):
                return "return_str"

        test_object = TestClass()
        # Act
        cloudpickle_serializer.serialize(test_object, fake_gcs_uri)

        # Assert
        del test_object
        # The serialized file is written to a local path "fake_gcs_uri.cpkl" via
        # mock_upload_to_gcs for hermicity.
        with open(fake_gcs_uri.split("/")[-1], "rb") as f:
            restored_object = cloudpickle.load(f)
        assert restored_object.test_method() == "return_str"

    @pytest.mark.usefixtures("mock_storage_blob", "google_auth_mock")
    def test_serialize_class(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.cpkl"

        class TestClass:
            def test_method(self):
                return "return_str"

        # Act
        cloudpickle_serializer.serialize(TestClass, fake_gcs_uri)

        # Assert
        del TestClass
        # The serialized file is written to a local path "fake_gcs_uri.cpkl" via
        # mock_upload_to_gcs for hermicity.
        with open(fake_gcs_uri.split("/")[-1], "rb") as f:
            restored_class = cloudpickle.load(f)
        assert restored_class().test_method() == "return_str"

    @pytest.mark.usefixtures("mock_storage_blob", "google_auth_mock")
    def test_deserialize_func(self, cloudpickle_serializer, mock_storage_blob):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.cpkl"

        def test_function():
            return "return_str"

        def fake_download_file_from_gcs(self, filename):
            with open(filename, "wb") as f:
                cloudpickle.dump(test_function, f)

        mock_storage_blob.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob
        )

        # Act
        restored_fn = cloudpickle_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert restored_fn() == "return_str"

    def test_deserialize_func_path_start_with_gcs(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "/gcs/staging-bucket/fake_gcs_uri.cpkl"

        def test_function():
            return "return_str"

        with fake_filesystem_unittest.Patcher() as filesystem:
            filesystem.fs.create_file(fake_gcs_uri)
            with open(fake_gcs_uri, "wb") as f:
                cloudpickle.dump(test_function, f)
            # Act
            restored_fn = cloudpickle_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert restored_fn() == "return_str"

    def test_deserialize_func_invalid_gcs_path(self, cloudpickle_serializer):
        # Arrange
        fake_gcs_uri = "fake_gcs_uri.cpkl"

        def test_function():
            return "return_str"

        # Act
        with pytest.raises(ValueError, match=f"Invalid gcs path: {fake_gcs_uri}"):
            cloudpickle_serializer.serialize(test_function, fake_gcs_uri)

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_object(self, cloudpickle_serializer, mock_storage_blob):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.cpkl"

        class TestClass:
            def test_method(self):
                return "return_str"

        def fake_download_file_from_gcs(self, filename: str):
            with open(filename, "wb") as f:
                cloudpickle.dump(TestClass(), f)

        mock_storage_blob.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob
        )

        # Act
        restored_object = cloudpickle_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert restored_object.test_method() == "return_str"

    @pytest.mark.usefixtures("google_auth_mock")
    def test_deserialize_class(self, cloudpickle_serializer, mock_storage_blob):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.cpkl"

        class TestClass:
            def test_method(self):
                return "return_str"

        def fake_download_file_from_gcs(self, filename):
            with open(filename, "wb") as f:
                cloudpickle.dump(TestClass, f)

        mock_storage_blob.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob
        )

        # Act
        restored_class = cloudpickle_serializer.deserialize(fake_gcs_uri)

        # Assert
        assert restored_class().test_method() == "return_str"


class TestTFDatasetSerializer:
    @pytest.mark.usefixtures("mock_tf_dataset_serialize")
    def test_serialize_tf_dataset(self, tf_dataset_serializer, tmp_path):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/tf_dataset"
        tf_dataset = tf.data.Dataset.from_tensor_slices(np.array([1, 2, 3]))

        # Act
        tf_dataset_serializer.serialize(tf_dataset, fake_gcs_uri)

        # Assert
        try:
            loaded_dataset = tf.data.Dataset.load(str(tmp_path / "tf_dataset"))
        except AttributeError:
            loaded_dataset = tf.data.experimental.load(str(tmp_path / "tf_dataset"))
        for original_ele, loaded_ele in zip(tf_dataset, loaded_dataset):
            assert original_ele == loaded_ele

    def test_deserialize_tf_dataset(self, tf_dataset_serializer, tmp_path):
        # Arrange
        tf_dataset = tf.data.Dataset.from_tensor_slices(np.array([1, 2, 3]))
        try:
            tf_dataset.save(str(tmp_path / "tf_dataset"))
        except AttributeError:
            tf.data.experimental.save(tf_dataset, str(tmp_path / "tf_dataset"))

        # Act
        loaded_dataset = tf_dataset_serializer.deserialize(str(tmp_path / "tf_dataset"))

        # Assert
        for original_ele, loaded_ele in zip(tf_dataset, loaded_dataset):
            assert original_ele == loaded_ele


class TestPandasDataSerializer:
    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_serialize_float_only_default_index_dataframe(
        self, pandas_data_serializer, tmp_path
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(np.zeros(shape=[3, 3]), columns=["col1", "col2", "col3"])

        # Act
        pandas_data_serializer.serialize(df, fake_gcs_uri)

        # Assert
        # For hermicity, The serialized file is written to a local path
        # "tmp_path/fake_gcs_uri.parquet" via mock_storage_blob_tmp_dir.
        parquet_file_path = os.fspath(tmp_path / fake_gcs_uri.split("/")[-1])
        restored_df = pd.read_parquet(parquet_file_path)

        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_serialize_float_only_str_index(self, pandas_data_serializer, tmp_path):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(
            np.zeros(shape=[3, 3]),
            columns=["col1", "col2", "col3"],
            index=["row1", "row2", "row3"],
        )

        # Act
        pandas_data_serializer.serialize(df, fake_gcs_uri)

        # Assert
        # For hermicity, The serialized file is written to a local path
        # "tmp_path/fake_gcs_uri.parquet" via mock_storage_blob_tmp_dir.
        parquet_file_path = os.fspath(tmp_path / fake_gcs_uri.split("/")[-1])
        restored_df = pd.read_parquet(parquet_file_path)

        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_serialize_common_typed_columns_with_nan(
        self, pandas_data_serializer, tmp_path
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(
            np.zeros(shape=[3, 4]),
            columns=["str_col", "float_col", "bool_col", "timestamp_col"],
        )

        # object type
        df["str_col"] = ["a", np.nan, "b"]
        # float type
        df["float_clo"] = [1.0, np.nan, np.nan]
        # object type
        df["bool_col"] = [True, False, np.nan]
        # object type
        df["timestamp_col"] = [
            pd.Timestamp("20110101"),
            np.nan,
            pd.Timestamp("20110101"),
        ]

        # Act
        pandas_data_serializer.serialize(df, fake_gcs_uri)

        # Assert
        # For hermicity, The serialized file is written to a local path
        # "tmp_path/fake_gcs_uri.parquet" via mock_storage_blob_tmp_dir.
        parquet_file_path = os.fspath(tmp_path / fake_gcs_uri.split("/")[-1])
        restored_df = pd.read_parquet(parquet_file_path)

        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_serialize_common_typed_columns_with_none(
        self, pandas_data_serializer, tmp_path
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(
            np.zeros(shape=[3, 8]),
            columns=[
                "str_to_object_col",
                "str_col",
                "float_col",
                "int_to_float_col",
                "int_col",
                "bool_to_object_col",
                "bool_col",
                "timestamp_col",
            ],
        )

        df["str_to_object_col"] = ["a", None, "b"]
        df["str_col"] = ["a", "b", "c"]

        df["float_col"] = [1.0, None, None]  # None -> NaN

        df["int_to_float_col"] = [1, 2, None]  # None -> NaN
        df["int_col"] = [1, 2, 3]

        df["bool_to_object_col"] = [True, False, None]
        df["bool_col"] = [True, False, True]

        df["timestamp_col"] = [
            pd.Timestamp("20110101"),
            None,
            pd.Timestamp("20110101"),
        ]  # None -> NaT

        # Act
        pandas_data_serializer.serialize(df, fake_gcs_uri)

        # Assert
        # For hermicity, The serialized file is written to a local path
        # "tmp_path/fake_gcs_uri.parquet" via mock_storage_blob_tmp_dir.
        parquet_file_path = os.fspath(tmp_path / fake_gcs_uri.split("/")[-1])
        restored_df = pd.read_parquet(parquet_file_path)

        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_deserialize_all_floats_cols(
        self, pandas_data_serializer, mock_storage_blob_tmp_dir
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(np.zeros(shape=[3, 3]), columns=["col1", "col2", "col3"])

        def fake_download_file_from_gcs(self, filename):
            df.to_parquet(filename)

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_df = pandas_data_serializer.deserialize(fake_gcs_uri)

        # Assert
        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_deserialize_all_floats_cols_str_index(
        self, pandas_data_serializer, mock_storage_blob_tmp_dir
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(
            np.zeros(shape=[3, 3]),
            columns=["col1", "col2", "col3"],
            index=["row1", "row2", "row3"],
        )

        def fake_download_file_from_gcs(self, filename):
            df.to_parquet(filename)

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_df = pandas_data_serializer.deserialize(fake_gcs_uri)

        # Assert
        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_deserialize_common_types_with_none(
        self, pandas_data_serializer, mock_storage_blob_tmp_dir
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(
            np.zeros(shape=[3, 8]),
            columns=[
                "str_to_object_col",
                "str_col",
                "float_col",
                "int_to_float_col",
                "int_col",
                "bool_to_object_col",
                "bool_col",
                "timestamp_col",
            ],
        )

        df["str_to_object_col"] = ["a", None, "b"]
        df["str_col"] = ["a", "b", "c"]

        df["float_col"] = [1.0, None, None]  # None -> NaN

        df["int_to_float_col"] = [1, 2, None]  # None -> NaN
        df["int_col"] = [1, 2, 3]

        df["bool_to_object_col"] = [True, False, None]
        df["bool_col"] = [True, False, True]

        df["timestamp_col"] = [
            pd.Timestamp("20110101"),
            None,
            pd.Timestamp("20110101"),
        ]  # None -> NaT

        def fake_download_file_from_gcs(self, filename):
            df.to_parquet(filename)

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_df = pandas_data_serializer.deserialize(fake_gcs_uri)

        # Assert
        pd.testing.assert_frame_equal(df, restored_df)

    @pytest.mark.usefixtures("mock_storage_blob_tmp_dir", "google_auth_mock")
    def test_deserialize_common_types_with_nan(
        self, pandas_data_serializer, mock_storage_blob_tmp_dir
    ):
        # Arrange
        fake_gcs_uri = "gs://staging-bucket/fake_gcs_uri.parquet"

        df = pd.DataFrame(
            np.zeros(shape=[3, 4]),
            columns=["str_col", "float_col", "bool_col", "timestamp_col"],
        )

        # object type
        df["str_col"] = ["a", np.nan, "b"]
        # float type
        df["float_clo"] = [1.0, np.nan, np.nan]
        # object type
        df["bool_col"] = [True, False, np.nan]
        # object type
        df["timestamp_col"] = [
            pd.Timestamp("20110101"),
            np.nan,
            pd.Timestamp("20110101"),
        ]

        def fake_download_file_from_gcs(self, filename):
            df.to_parquet(filename)

        mock_storage_blob_tmp_dir.download_to_filename = types.MethodType(
            fake_download_file_from_gcs, mock_storage_blob_tmp_dir
        )

        # Act
        restored_df = pandas_data_serializer.deserialize(fake_gcs_uri)

        # Assert
        pd.testing.assert_frame_equal(df, restored_df)
