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

import mock
import pytest

import cloudpickle
import logging
import json
import os
from typing import Any

from vertexai.preview import developer
from vertexai.preview._workflow.serialization_engine import (
    any_serializer,
    serializers,
    serializers_base,
)
from vertexai.preview._workflow.shared import constants

import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
import tensorflow as tf
from tensorflow import keras
import torch

try:
    # pylint: disable=g-import-not-at-top
    import lightning.pytorch as pl
except ImportError:
    pl = None

try:
    import bigframes as bf
except ImportError:
    bf = None

# lightning trainer and bigframes dataframe are not in this scheme since
# the test environment may not have these packages.
_TEST_SERIALIZATION_SCHEME = {
    object: serializers.CloudPickleSerializer,
    sklearn.base.BaseEstimator: serializers.SklearnEstimatorSerializer,
    keras.models.Model: serializers.KerasModelSerializer,
    keras.callbacks.History: serializers.KerasHistoryCallbackSerializer,
    tf.data.Dataset: serializers.TFDatasetSerializer,
    torch.nn.Module: serializers.TorchModelSerializer,
    torch.utils.data.DataLoader: serializers.TorchDataLoaderSerializer,
    pd.DataFrame: serializers.PandasDataSerializer,
}


@pytest.fixture
def any_serializer_instance():
    return any_serializer.AnySerializer()


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
def mock_keras_model_serialize():
    def stateful_serialize(self, to_serialize, gcs_path):
        del self, to_serialize
        serializers.KerasModelSerializer._metadata.dependencies = ["keras==1.0.0"]
        return gcs_path

    with mock.patch.object(
        serializers.KerasModelSerializer, "serialize", new=stateful_serialize
    ) as keras_model_serialize:
        yield keras_model_serialize
        serializers.KerasModelSerializer._metadata.dependencies = []


@pytest.fixture
def mock_keras_model_deserialize():
    with mock.patch.object(
        serializers.KerasModelSerializer, "deserialize", autospec=True
    ) as keras_model_deserialize:
        yield keras_model_deserialize


@pytest.fixture
def mock_sklearn_estimator_serialize():
    def stateful_serialize(self, to_serialize, gcs_path):
        del self, to_serialize
        serializers.SklearnEstimatorSerializer._metadata.dependencies = [
            "sklearn_dependency1==1.0.0"
        ]
        return gcs_path

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
        del self, to_serialize
        serializers.TorchModelSerializer._metadata.dependencies = ["torch==1.0.0"]
        return gcs_path

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
        del self, to_serialize
        serializers.TorchDataLoaderSerializer._metadata.dependencies = ["torch==1.0.0"]
        return gcs_path

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
def mock_tf_dataset_serialize(tmp_path):
    def stateful_serialize(self, to_serialize, gcs_path):
        serializers.TFDatasetSerializer._metadata.dependencies = ["tensorflow==1.0.0"]
        try:
            to_serialize.save(str(tmp_path / "tf_dataset"))
        except AttributeError:
            tf.data.experimental.save(to_serialize, str(tmp_path / "tf_dataset"))
        return gcs_path

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
        del self, to_serialize
        serializers.PandasDataSerializer._metadata.dependencies = ["pandas==1.0.0"]
        return gcs_path

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


# TODO(b/295338623): Test correctness of Bigframes serialize/deserialize
@pytest.fixture
def mock_bigframe_deserialize_sklearn():
    with mock.patch.object(
        serializers.BigframeSerializer, "_deserialize_sklearn", autospec=True
    ) as bigframe_deserialize_sklearn:
        yield bigframe_deserialize_sklearn


# TODO(b/295338623): Test correctness of Bigframes serialize/deserialize
@pytest.fixture
def mock_bigframe_deserialize_torch():
    with mock.patch.object(
        serializers.BigframeSerializer, "_deserialize_torch", autospec=True
    ) as bigframe_deserialize_torch:
        yield bigframe_deserialize_torch


# TODO(b/295338623): Test correctness of Bigframes serialize/deserialize
@pytest.fixture
def mock_bigframe_deserialize_tensorflow():
    with mock.patch.object(
        serializers.BigframeSerializer, "_deserialize_tensorflow", autospec=True
    ) as bigframe_deserialize_tensorflow:
        yield bigframe_deserialize_tensorflow


@pytest.fixture
def mock_cloudpickle_serialize():
    def stateful_serialize(self, to_serialize, gcs_path, **kwargs):
        del self, to_serialize, kwargs
        serializers.CloudPickleSerializer._metadata.dependencies = [
            "cloudpickle==1.0.0"
        ]
        return gcs_path

    with mock.patch.object(
        serializers.CloudPickleSerializer, "serialize", new=stateful_serialize
    ) as cloudpickle_serialize:
        yield cloudpickle_serialize
        serializers.CloudPickleSerializer._metadata.dependencies = []


@pytest.fixture
def mock_cloudpickle_deserialize():
    with mock.patch.object(
        serializers.CloudPickleSerializer, "deserialize", autospec=True
    ) as cloudpickle_deserialize:
        yield cloudpickle_deserialize


class TestTorchClass(torch.nn.Module):
    def __init__(self, input_size=4):
        super().__init__()
        self.linear_relu_stack = torch.nn.Sequential(
            torch.nn.Linear(input_size, 3), torch.nn.ReLU(), torch.nn.Linear(3, 2)
        )

    def forward(self, x):
        logits = self.linear_relu_stack(x)
        return logits


class TestAnySerializer:
    """Tests that AnySerializer is acting as 'controller' and router."""

    def test_any_serializer_register_predefined_serializers(self, caplog):
        with caplog.at_level(
            level=logging.DEBUG, logger="vertexai.serialization_engine"
        ):
            serializers_base.Serializer._instances = {}
            serializer_instance = any_serializer.AnySerializer()

            if pl:
                _TEST_SERIALIZATION_SCHEME[
                    pl.Trainer
                ] = serializers.LightningTrainerSerializer
            else:
                # Lightning trainer is not registered.
                # Check the logs to make sure we tried to register them.
                assert (
                    f"Failed to register {serializers.LightningTrainerSerializer} due to"
                    in caplog.text
                )

            if bf:
                _TEST_SERIALIZATION_SCHEME[
                    bf.dataframe.DataFrame
                ] = serializers.BigframeSerializer
            else:
                # Bigframes dataframe is not registered.
                # Check the logs to make sure we tried to register them.
                assert (
                    f"Failed to register {serializers.BigframeSerializer} due to"
                    in caplog.text
                )

            assert (
                serializer_instance._serialization_scheme == _TEST_SERIALIZATION_SCHEME
            )

    def test_any_serializer_global_metadata_created(
        self, mock_cloudpickle_serialize, any_serializer_instance, tmp_path
    ):
        # Arrange
        class RandomClass:
            pass

        class Nested:
            pass

        obj = RandomClass()
        os.makedirs(tmp_path / "job_id/input")
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/random_obj")

        param_to_be_serialized = Nested()
        # param_to_be_serialized will be serialized to this path
        expected_extra_obj_param_path = os.fspath(
            tmp_path / "job_id/input/serialization_args/extra_obj_param"
        )
        expected_serialized = {
            str(fake_gcs_path): any_serializer.SerializedEntryMetadata(
                serialization_id=id(obj),
                obj=obj,
                serializer_args={
                    "extra_int_param": any_serializer.SerializerArg(value=1),
                    "extra_float_param": any_serializer.SerializerArg(value=1.0),
                    "extra_dict_param": any_serializer.SerializerArg(
                        value={"key1": 10}
                    ),
                    "extra_list_param": any_serializer.SerializerArg(value=[0, 1, 2]),
                    "extra_obj_param": any_serializer.SerializerArg(
                        gcs_path=expected_extra_obj_param_path
                    ),
                },
            ),
            expected_extra_obj_param_path: any_serializer.SerializedEntryMetadata(
                serialization_id=id(param_to_be_serialized),
                obj=param_to_be_serialized,
                serializer_args={},
            ),
        }
        expected_on_disk_global_metadata = {
            "serializer": "AnySerializer",
            "dependencies": [],
            "custom_commands": [],
            "serialized": {
                str(fake_gcs_path): {
                    "serialization_id": id(obj),
                    "serializer_args": {
                        "extra_int_param": {"value": 1, "gcs_path": None},
                        "extra_float_param": {"value": 1.0, "gcs_path": None},
                        "extra_dict_param": {"value": {"key1": 10}, "gcs_path": None},
                        "extra_list_param": {"value": [0, 1, 2], "gcs_path": None},
                        "extra_obj_param": {
                            "value": None,
                            "gcs_path": expected_extra_obj_param_path,
                        },
                    },
                },
                expected_extra_obj_param_path: {
                    "serialization_id": id(param_to_be_serialized),
                    "serializer_args": {},
                },
            },
        }

        # Act
        any_serializer_instance.serialize(
            obj,
            fake_gcs_path,
            extra_int_param=1,
            extra_float_param=1.0,
            extra_dict_param={"key1": 10},
            extra_list_param=[0, 1, 2],
            extra_obj_param=param_to_be_serialized,
        )

        # Assert
        # first, assert the content of the in-memory global metadata
        assert expected_serialized == any_serializer_instance._metadata.serialized

        # now, assert the content of the global metadata saved to the disk after
        # saving to the disk
        # Act again
        global_metadata_path = os.fspath(
            tmp_path / "job_id/input" / "serialization_global_metadata.json"
        )

        any_serializer_instance.save_global_metadata(global_metadata_path)
        with open(global_metadata_path, "rb") as f:
            metadata = json.load(f)
        assert metadata == expected_on_disk_global_metadata
        print("the read metadata is ", metadata)

    @mock.patch.object(serializers.CloudPickleSerializer, "serialize", autospec=True)
    def test_any_serializer_serialize_custom_model_with_custom_serializer(
        self, mock_cloudpickle_serializer_serialize, any_serializer_instance, tmp_path
    ):
        # Arrange
        class CustomModel:
            def __init__(self, weight: int = 0):
                self.weight = weight

            @developer.mark.train()
            def fit(self, X_train, y_train) -> "CustomModel":
                self.weight += 1
                return self

        class CustomSerializer(developer.Serializer):
            _metadata = developer.SerializationMetadata()

            def serialize(
                self, to_serialize: CustomModel, gcs_path: str, extra_para: Any
            ) -> str:
                del extra_para
                return gcs_path

            def deserialize(self, serialized_gcs_path: str) -> CustomModel:
                # Pretend that the model is trained
                return CustomModel(weight=1)

        CustomSerializer.register_requirements(["custom_dependency==1.0.0"])
        developer.register_serializer(CustomModel, CustomSerializer)

        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        custom_model = CustomModel()

        # Act
        any_serializer_instance.serialize(custom_model, fake_gcs_path, extra_para=1)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        # Metadata should record the dependency specifiers
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "CustomSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "custom_dependency==1.0.0"
        ]

        # During the serialization of the CustomModel object, we also serialize
        # the serializer with CloudPicleSerializer.
        custom_serializer_path = tmp_path / "job_id/input/CustomSerializer"
        mock_cloudpickle_serializer_serialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.CloudPickleSerializer],
            any_serializer_instance._instances[CustomSerializer],
            str(custom_serializer_path),
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_serialize_sklearn_estimator(
        self, any_serializer_instance, tmp_path, mock_sklearn_estimator_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        sklearn_estimator = LogisticRegression()

        # Act
        any_serializer_instance.serialize(sklearn_estimator, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "SklearnEstimatorSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "sklearn_dependency1==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_serialize_keras_model(
        self, any_serializer_instance, tmp_path, mock_keras_model_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        keras_model = keras.Sequential(
            [keras.layers.Dense(5, input_shape=(4,)), keras.layers.Softmax()]
        )

        # Act
        any_serializer_instance.serialize(keras_model, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "KerasModelSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "keras==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_serialize_torch_model(
        self, any_serializer_instance, tmp_path, mock_torch_model_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        torch_model = TestTorchClass()

        # Act
        any_serializer_instance.serialize(torch_model, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "TorchModelSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "torch==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_serialize_dataframe(
        self, any_serializer_instance, tmp_path, mock_pandas_data_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/X")
        os.makedirs(tmp_path / "job_id/input")
        df = pd.DataFrame({"a": [1, 2, 3], "b": [1, 2, 3]})

        # Act
        any_serializer_instance.serialize(df, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_X.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "PandasDataSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "pandas==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_serialize_general_object(
        self, any_serializer_instance, tmp_path, mock_cloudpickle_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/general_object.cpkl")
        os.makedirs(tmp_path / "job_id/input")

        class TestClass:
            pass

        obj = TestClass()

        # Act
        any_serializer_instance.serialize(obj, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_general_object.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "CloudPickleSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "cloudpickle==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_serialize_torch_dataloader(
        self, any_serializer_instance, tmp_path, mock_torch_dataloader_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "dataloader")

        dataloader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(
                torch.tensor([[1, 2, 3] for i in range(100)]),
                torch.tensor([1] * 100),
            ),
            batch_size=10,
            shuffle=True,
        )

        # Act
        any_serializer_instance.serialize(dataloader, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"{serializers_base.SERIALIZATION_METADATA_FILENAME}_dataloader.json"
        )
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)

        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "TorchDataLoaderSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "torch==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_tf_dataset_serialize")
    def test_any_serializer_serialize_tf_dataset(
        self, any_serializer_instance, tmp_path, tf_dataset_serializer
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "tf_dataset")

        tf_dataset = tf.data.Dataset.from_tensor_slices([1, 2, 3])

        # Act
        any_serializer_instance.serialize(tf_dataset, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"{serializers_base.SERIALIZATION_METADATA_FILENAME}_tf_dataset.json"
        )
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)

        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "TFDatasetSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "tensorflow==1.0.0"
        ]

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_typed_serializer_failed_falling_back_to_cloudpickle(
        self, any_serializer_instance, tmp_path, mock_cloudpickle_serialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        keras_model = keras.Sequential(
            [keras.layers.Dense(5, input_shape=(4,)), keras.layers.Softmax()]
        )

        with mock.patch.object(
            serializers.KerasModelSerializer, "serialize", autospec=True
        ) as mock_keras_model_serializer_serialize:
            mock_keras_model_serializer_serialize.side_effect = Exception
            # Act
            any_serializer_instance.serialize(keras_model, fake_gcs_path)

        # Assert
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )

        # Metadata should have the correct serializer information
        with open(metadata_path, "rb") as f:
            metadata = json.load(f)
        assert (
            metadata[serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY]
            == "CloudPickleSerializer"
        )
        assert metadata[serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY] == [
            "cloudpickle==1.0.0"
        ]

    def test_any_serializer_cloudpickle_serializer_failed_raise_serialization_error(
        self, any_serializer_instance, tmp_path
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/general_object.cpkl")

        class TestClass:
            pass

        obj = TestClass()

        with mock.patch.object(
            serializers.CloudPickleSerializer, "serialize", autospec=True
        ) as mock_cloudpickle_serializer_serialize:
            mock_cloudpickle_serializer_serialize.side_effect = Exception
            # Act & Assert
            with pytest.raises(serializers_base.SerializationError):
                any_serializer_instance.serialize(obj, fake_gcs_path)

    @pytest.mark.usefixtures("mock_gcs_upload")
    @mock.patch.object(any_serializer, "_check_dependency_versions", autospec=True)
    def test_any_serializer_deserialize_custom_model_with_custom_serializer(
        self, mocked_check_dependency_versions, any_serializer_instance, tmp_path
    ):
        # Arrange
        class CustomModel:
            def __init__(self, weight: int = 0):
                self.weight = weight

            @developer.mark.train()
            def fit(self, X_train, y_train):
                self.weight += 1
                return self

        class CustomSerializer(developer.Serializer):
            _metadata = developer.SerializationMetadata()

            def serialize(self, to_serialize: CustomModel, gcs_path: str) -> str:
                return gcs_path

            def deserialize(self, serialized_gcs_path: str, **kwargs) -> CustomModel:
                assert "param1" in kwargs
                # Pretend that the model is trained
                return CustomModel(weight=1)  # noqa: F821

        developer.register_serializer(CustomModel, CustomSerializer)
        CustomSerializer.register_requirements(["custom_dependency==1.0.0"])

        fake_gcs_path = os.fspath(tmp_path / "job_id/input/custom_model")
        os.makedirs(tmp_path / "job_id/input")
        local_metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_custom_model.json"
        )

        # Write the local metadata
        with open(local_metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "CustomSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                            "custom_dependency==1.0.0"
                        ],
                    }
                ).encode("utf-8")
            )
        # Write the global metadata
        global_metadata_path = (
            tmp_path / "job_id/input/serialization_global_metadata.json"
        )
        global_metadata = {
            "serializer": "AnySerializer",
            "dependencies": [],
            "serialized": {
                str(fake_gcs_path): {
                    "serialization_id": "id_holder",
                    "serializer_args": {"param1": {"value": 1}},
                },
            },
        }
        with open(global_metadata_path, "wb") as f:
            f.write(json.dumps(global_metadata).encode("utf-8"))

        custom_serializer_path = tmp_path / "job_id/input/CustomSerializer"

        # Load global metadata
        any_serializer_instance.load_global_metadata(str(global_metadata_path))

        # Act
        with mock.patch.object(
            serializers.CloudPickleSerializer,
            "deserialize",
            autospec=True,
            return_value=CustomSerializer(),
        ) as mock_cloudpickle_deserialize:
            deserialized_custom_model = any_serializer_instance.deserialize(
                fake_gcs_path
            )

        # Assert
        del CustomModel
        deserialized_custom_model.weight = 1
        # CloudPickleSerializer.deserialize() is called to deserialize the
        # CustomSerializer.
        mock_cloudpickle_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.CloudPickleSerializer],
            serialized_gcs_path=str(custom_serializer_path),
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_sklearn_estimator(
        self, any_serializer_instance, tmp_path, mock_sklearn_estimator_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "SklearnEstimatorSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                    }
                ).encode("utf-8")
            )

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_sklearn_estimator_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.SklearnEstimatorSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_keras_model(
        self, any_serializer_instance, tmp_path, mock_keras_model_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "KerasModelSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                    }
                ).encode("utf-8")
            )

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_keras_model_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.KerasModelSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_torch_model(
        self, any_serializer_instance, tmp_path, mock_torch_model_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/input_estimator")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_input_estimator.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "TorchModelSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                    }
                ).encode("utf-8")
            )

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_torch_model_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.TorchModelSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_dataframe(
        self, any_serializer_instance, tmp_path, mock_pandas_data_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/X")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_X.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "PandasDataSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                    }
                ).encode("utf-8")
            )

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_pandas_data_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.PandasDataSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_torch_dataloader(
        self, any_serializer_instance, tmp_path, mock_torch_dataloader_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/dataloader")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_dataloader.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "TorchDataLoaderSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                    }
                ).encode("utf-8")
            )

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_torch_dataloader_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.TorchDataLoaderSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_bigframe_sklearn(
        self, any_serializer_instance, tmp_path, mock_bigframe_deserialize_sklearn
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/X")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_X.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "BigframeSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                        serializers.SERIALIZATION_METADATA_FRAMEWORK_KEY: "sklearn",
                    }
                ).encode("utf-8")
            )

        # Act (step 2)
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_bigframe_deserialize_sklearn.assert_called_once_with(
            any_serializer_instance._instances[serializers.BigframeSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_bigframe_torch(
        self, any_serializer_instance, tmp_path, mock_bigframe_deserialize_torch
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/X")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_X.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "BigframeSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                        serializers.SERIALIZATION_METADATA_FRAMEWORK_KEY: "torch",
                    }
                ).encode("utf-8")
            )

        # Act (step 2)
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_bigframe_deserialize_torch.assert_called_once_with(
            any_serializer_instance._instances[serializers.BigframeSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_bigframe_tensorflow(
        self, any_serializer_instance, tmp_path, mock_bigframe_deserialize_tensorflow
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/X")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_X.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "BigframeSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                        serializers.SERIALIZATION_METADATA_FRAMEWORK_KEY: "tensorflow",
                    }
                ).encode("utf-8")
            )

        # Act (step 2)
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_bigframe_deserialize_tensorflow.assert_called_once_with(
            any_serializer_instance._instances[serializers.BigframeSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    def test_any_serializer_deserialize_tf_dataset(
        self, any_serializer_instance, tmp_path, mock_tf_dataset_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/X")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_X.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "TFDatasetSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                            "tensorflow==1.0.0"
                        ],
                    }
                ).encode("utf-8")
            )

        # Act
        any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_tf_dataset_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.TFDatasetSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    @pytest.mark.usefixtures("mock_gcs_upload")
    def test_any_serializer_deserialize_general_object(
        self, any_serializer_instance, tmp_path, mock_cloudpickle_deserialize
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/general_object.cpkl")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_general_object.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "CloudPickleSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [],
                    }
                ).encode("utf-8")
            )

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)

        # Assert
        mock_cloudpickle_deserialize.assert_called_once_with(
            any_serializer_instance._instances[serializers.CloudPickleSerializer],
            serialized_gcs_path=fake_gcs_path,
        )

    def test_any_serializer_deserialize_raise_runtime_error_when_dependency_cannot_be_imported(
        self, tmp_path, any_serializer_instance
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/general_object.cpkl")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_general_object.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "CloudPickleSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                            "nonexisting_module==1.0.0",
                        ],
                    }
                ).encode("utf-8")
            )

        # Act & Assert
        with pytest.raises(RuntimeError, match="nonexisting_module is not installed"):
            _ = any_serializer_instance.deserialize(fake_gcs_path)

    @mock.patch.object(serializers, "_is_valid_gcs_path", return_value=True)
    def test_any_serializer_deserialize_raises_warning_when_version_mismatched(
        self, mock_gcs_path_validation, tmp_path, caplog, any_serializer_instance
    ):
        # Arrange
        fake_gcs_path = os.fspath(tmp_path / "job_id/input/general_object.cpkl")
        os.makedirs(tmp_path / "job_id/input")
        metadata_path = (
            tmp_path
            / f"job_id/input/{serializers_base.SERIALIZATION_METADATA_FILENAME}_general_object.json"
        )
        with open(metadata_path, "wb") as f:
            f.write(
                json.dumps(
                    {
                        serializers_base.SERIALIZATION_METADATA_SERIALIZER_KEY: "CloudPickleSerializer",
                        serializers_base.SERIALIZATION_METADATA_DEPENDENCIES_KEY: [
                            "sklearn==1.0.0",
                        ],
                    }
                ).encode("utf-8")
            )
        with open(fake_gcs_path, "wb") as f:
            f.write(cloudpickle.dumps([1, 2, 3], protocol=constants.PICKLE_PROTOCOL))

        # Act
        _ = any_serializer_instance.deserialize(fake_gcs_path)
        # Assert
        # The current sklearn version in google3 will changing, but it's a later
        # version than 1.0.0
        with caplog.at_level(level=20, logger="vertexai.serialization_engine"):
            assert "sklearn's version is" in caplog.text
            assert "while the required version is ==1.0.0" in caplog.text


def test_get_arg_path_from_file_gcs_uri():
    gcs_uri = "gs://bucket/job_path/input/estimator"
    arg_path = any_serializer.get_arg_path_from_file_gcs_uri(
        gcs_uri=gcs_uri, arg_name="input_func"
    )
    assert arg_path == "gs://bucket/job_path/input/serialization_args/input_func"


class TestSerializerArg:
    @pytest.mark.parametrize(
        "d, expected_value, expected_gcs_path",
        [
            ({"value": 1}, 1, None),
            (
                {"gcs_path": "gs://path-of-serializer-arg"},
                None,
                "gs://path-of-serializer-arg",
            ),
        ],
        ids=[
            "Value Present",
            "GCS Path Present",
        ],
    )
    def test_from_dict(self, d, expected_value, expected_gcs_path):
        serializer_args = any_serializer.SerializerArg.from_dict(d)
        assert serializer_args.value == expected_value
        assert serializer_args.gcs_path == expected_gcs_path

    @pytest.mark.parametrize(
        "d",
        [
            {"value": 1, "gcs_path": "gs://path-of-serializer-arg"},
            {"value": 0, "gcs_path": "gs://path-of-serializer-arg"},
        ],
        ids=[
            "Nonzero Value Present",
            "Zero Value Present",
        ],
    )
    def test_from_dict_raises_value_error(self, d):
        with pytest.raises(
            ValueError, match="Only one of value or gcs_path should be provided"
        ):
            _ = any_serializer.SerializerArg.from_dict(d)

    @pytest.mark.parametrize(
        "serializer_arg, expected_dict",
        [
            (any_serializer.SerializerArg(value=1), {"value": 1, "gcs_path": None}),
            (
                any_serializer.SerializerArg(gcs_path="gs://path-of-serializer-arg"),
                {"value": None, "gcs_path": "gs://path-of-serializer-arg"},
            ),
        ],
        ids=[
            "Value Presents",
            "GCS Path Presents",
        ],
    )
    def test_to_dict(self, serializer_arg, expected_dict):
        returned_dict = serializer_arg.to_dict()
        assert returned_dict == expected_dict

    @pytest.mark.parametrize(
        "serializer_arg, expected_dict",
        [
            (any_serializer.SerializerArg(value=1), {"value": 1, "gcs_path": None}),
            (
                any_serializer.SerializerArg(gcs_path="gs://path-of-serializer-arg"),
                {"value": None, "gcs_path": "gs://path-of-serializer-arg"},
            ),
        ],
        ids=[
            "Value Presents",
            "GCS Path Presents",
        ],
    )
    def test_to_jsonable_dict(self, serializer_arg, expected_dict):
        returned_dict = serializer_arg.to_jsonable_dict()
        assert returned_dict == expected_dict


class TestSerializationEntryMetadata:
    def test_from_dict(self):
        # Arrange
        class RandomClass:
            pass

        serialized_obj = RandomClass()
        d = {
            "serialization_id": "serialized_with_two_args",
            "obj": serialized_obj,
            "serializer_args": {
                "arg1": {"value": 1, "gcs_path": None},
                "arg2": {"value": None, "gcs_path": "gs://path-of-serializer-arg"},
            },
        }

        expected_serialized_entry_metadata = any_serializer.SerializedEntryMetadata(
            serialization_id="serialized_with_two_args",
            serializer_args={
                "arg1": any_serializer.SerializerArg(value=1),
                "arg2": any_serializer.SerializerArg(
                    gcs_path="gs://path-of-serializer-arg"
                ),
            },
            obj=serialized_obj,
        )

        # Act
        serialized_entry_metadata = any_serializer.SerializedEntryMetadata.from_dict(d)

        # Assert
        assert (
            serialized_entry_metadata.serialization_id
            == expected_serialized_entry_metadata.serialization_id
        )
        assert (
            serialized_entry_metadata.serializer_args
            == expected_serialized_entry_metadata.serializer_args
        )
        assert serialized_entry_metadata.obj == expected_serialized_entry_metadata.obj

    def test_to_jsonable_dict(self):
        # Arrange
        class RandomClass:
            pass

        serialized_args = {
            "arg1": any_serializer.SerializerArg(value=1),
            "arg2": any_serializer.SerializerArg(
                gcs_path="gs://path-of-serializer-arg"
            ),
        }
        serialized_entry = any_serializer.SerializedEntryMetadata(
            serialization_id="serialized_with_two_args",
            serializer_args=serialized_args,
            obj=RandomClass(),
        )

        expected_dict = {
            "serialization_id": "serialized_with_two_args",
            "serializer_args": {
                "arg1": {"value": 1, "gcs_path": None},
                "arg2": {"value": None, "gcs_path": "gs://path-of-serializer-arg"},
            },
        }

        # Act
        returned_dict = serialized_entry.to_jsonable_dict()

        # Assert
        assert returned_dict == expected_dict

    def test_to_json(self):
        # Arrange
        class RandomClass:
            pass

        serialized_args = {
            "arg1": any_serializer.SerializerArg(value=1),
            "arg2": any_serializer.SerializerArg(
                gcs_path="gs://path-of-serializer-arg"
            ),
        }
        serialized_obj = RandomClass()
        serialized_entry = any_serializer.SerializedEntryMetadata(
            serialization_id="serialized_with_two_args",
            serializer_args=serialized_args,
            obj=serialized_obj,
        )

        expected_dict = {
            "serialization_id": "serialized_with_two_args",
            "obj": serialized_obj,
            "serializer_args": {
                "arg1": {"value": 1, "gcs_path": None},
                "arg2": {"value": None, "gcs_path": "gs://path-of-serializer-arg"},
            },
        }

        # Act
        returned_dict = serialized_entry.to_dict()

        # Assert
        assert returned_dict == expected_dict


class TestAnySerializerMetadata:
    def test_from_dict(self):
        serialized_obj1_gcs_path = "gs://bucket/job_dir/input/random_obj1"
        serialized_obj2_gcs_path = "gs://bucket/job_dir/input/random_obj2"
        d = {
            "custom_commands": [],
            "dependencies": [],
            "serializer": "AnySerializer",
            "serialized": {
                serialized_obj1_gcs_path: {
                    "serialization_id": "random_obj",
                    "serializer_args": {
                        "arg1": {"value": 1, "gcs_path": None},
                        "arg2": {
                            "value": None,
                            "gcs_path": "gs://path-of-serializer-arg",
                        },
                    },
                },
                serialized_obj2_gcs_path: {
                    "serialization_id": "random_obj2",
                    "serializer_args": {
                        "arg1": {"value": 2.0, "gcs_path": None},
                        "arg2": {
                            "value": None,
                            "gcs_path": "gs://path-of-serializer-arg",
                        },
                    },
                },
            },
        }
        any_serilaizer_metadata = any_serializer.AnySerializationMetadata.from_dict(d)
        assert (
            any_serilaizer_metadata.serialized[
                serialized_obj1_gcs_path
            ].serialization_id
            == "random_obj"
        )
        assert any_serilaizer_metadata.serialized[
            serialized_obj1_gcs_path
        ].serializer_args == {
            "arg1": any_serializer.SerializerArg(value=1),
            "arg2": any_serializer.SerializerArg(
                gcs_path="gs://path-of-serializer-arg"
            ),
        }
        assert (
            any_serilaizer_metadata.serialized[
                serialized_obj2_gcs_path
            ].serialization_id
            == "random_obj2"
        )
        assert any_serilaizer_metadata.serialized[
            serialized_obj2_gcs_path
        ].serializer_args == {
            "arg1": any_serializer.SerializerArg(value=2.0),
            "arg2": any_serializer.SerializerArg(
                gcs_path="gs://path-of-serializer-arg"
            ),
        }
