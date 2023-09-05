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
# pylint: disable=line-too-long, bad-continuation,protected-access
"""Defines the Serializer classes."""

import dataclasses
import functools
import json
import os
import pickle
import shutil
import tempfile
from typing import Any, Optional, Union
import uuid

from google.cloud.aiplatform.utils import gcs_utils
from vertexai.preview._workflow.shared import constants
from vertexai.preview._workflow.shared import (
    data_serializer_utils,
    supported_frameworks,
)
from vertexai.preview._workflow.serialization_engine import (
    serializers_base,
)

try:
    import cloudpickle
except ImportError:
    cloudpickle = None

SERIALIZATION_METADATA_FRAMEWORK_KEY = "framework"

# TODO(b/272263750): use the centralized module and usage pattern to guard these
# imports
# pylint: disable=g-import-not-at-top
try:
    import pandas as pd
    import bigframes as bf

    PandasData = pd.DataFrame
    BigframesData = bf.dataframe.DataFrame
except ImportError:
    pd = None
    bf = None
    PandasData = Any
    BigframesData = Any

try:
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq

    PandasData = pd.DataFrame
except ImportError:
    pd = None
    pa = None
    pq = None
    PandasData = Any

try:
    import sklearn

    SklearnEstimator = sklearn.base.BaseEstimator
except ImportError:
    sklearn = None
    SklearnEstimator = Any

try:
    from tensorflow import keras
    import tensorflow as tf

    KerasModel = keras.models.Model
    TFDataset = tf.data.Dataset
except ImportError:
    keras = None
    tf = None
    KerasModel = Any
    TFDataset = Any

try:
    import torch

    TorchModel = torch.nn.Module
    TorchDataLoader = torch.utils.data.DataLoader
    TorchTensor = torch.tensor
except ImportError:
    torch = None
    TorchModel = Any
    TorchDataLoader = Any
    TorchTensor = Any

try:
    import lightning.pytorch as pl

    LightningTrainer = pl.Trainer
except ImportError:
    pl = None
    LightningTrainer = Any


Types = Union[
    PandasData,
    BigframesData,
    SklearnEstimator,
    KerasModel,
    TorchModel,
    LightningTrainer,
]

_LIGHTNING_ROOT_DIR = "/vertex_lightning_root_dir/"


def _is_valid_gcs_path(path: str) -> bool:
    """checks if a path is a valid gcs path.

    Args:
        path (str):
            Required. A file path.

    Returns:
        A boolean that indicates whether the path is a valid gcs path.
    """
    return path.startswith(("gs://", "/gcs/", "gcs/"))


def _load_torch_model(path: str, map_location: "torch.device") -> TorchModel:
    try:
        return torch.load(path, map_location=map_location)
    except Exception:
        return torch.load(path, map_location=torch.device("cpu"))


class KerasModelSerializer(serializers_base.Serializer):
    """A serializer for tensorflow.keras.models.Model objects."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="KerasModelSerializer")
    )

    def serialize(
        self, to_serialize: KerasModel, gcs_path: str, **kwargs
    ) -> str:  # pytype: disable=invalid-annotation
        """Serializes a tensorflow.keras.models.Model to a gcs path.

        Args:
            to_serialize (keras.models.Model):
                Required. A Keras Model object.
            gcs_path (str):
                Required. A GCS uri that the model will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        KerasModelSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_tensorflow_model(to_serialize)
        )
        to_serialize.save(gcs_path)

        return gcs_path

    def deserialize(
        self, serialized_gcs_path: str, **kwargs
    ) -> KerasModel:  # pytype: disable=invalid-annotation
        """Deserialize a tensorflow.keras.models.Model given the gcs file name.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A Keras Model.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
            ImportError: if tensorflow is not installed.
        """
        del kwargs
        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")

        try:
            from tensorflow import keras

            return keras.models.load_model(serialized_gcs_path)
        except ImportError as e:
            raise ImportError("tensorflow is not installed.") from e


class KerasHistoryCallbackSerializer(serializers_base.Serializer):
    """A serializer for tensorflow.keras.callbacks.History objects."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(
            serializer="KerasHistoryCallbackSerializer"
        )
    )

    def serialize(self, to_serialize, gcs_path: str, **kwargs):
        """Serializes a keras History callback to a gcs path.

        Args:
            to_serialize (keras.callbacks.History):
                Required. A History object.
            gcs_path (str):
                Required. A GCS uri that History object will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        KerasHistoryCallbackSerializer._metadata.dependencies = ["cloudpickle"]

        to_serialize_dict = to_serialize.__dict__
        del to_serialize_dict["model"]
        with open(gcs_path, "wb") as f:
            cloudpickle.dump(to_serialize_dict, f)

        return gcs_path

    def deserialize(self, serialized_gcs_path: str, **kwargs):
        """Deserialize a keras.callbacks.History given the gcs file name.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A keras.callbacks.History object.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
        """

        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")
        model = kwargs.get("model", None)
        # Only "model" is needed.
        del kwargs

        history_dict = {}
        if serialized_gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                gcs_utils.download_file_from_gcs(serialized_gcs_path, temp_file.name)
                with open(temp_file.name, mode="rb") as f:
                    history_dict = cloudpickle.load(f)
        else:
            with open(serialized_gcs_path, mode="rb") as f:
                history_dict = cloudpickle.load(f)

        history_obj = keras.callbacks.History()

        for attr_name, attr_value in history_dict.items():
            setattr(history_obj, attr_name, attr_value)

        if model:
            history_obj.set_model(model)

        return history_obj


class SklearnEstimatorSerializer(serializers_base.Serializer):
    """A serializer that uses pickle to save/load sklearn estimators."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="SklearnEstimatorSerializer")
    )

    def serialize(self, to_serialize: SklearnEstimator, gcs_path: str, **kwargs) -> str:
        """Serializes a sklearn estimator to a gcs path.

        Args:
            to_serialize (sklearn.base.BaseEstimator):
                Required. A sklearn estimator.
            gcs_path (str):
                Required. A GCS uri that the estimator will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        SklearnEstimatorSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_sklearn_model(to_serialize)
        )
        serialized = pickle.dumps(to_serialize, protocol=constants.PICKLE_PROTOCOL)
        serializers_base.write_and_upload_data(data=serialized, gcs_filename=gcs_path)

        return gcs_path

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> SklearnEstimator:
        """Deserialize a sklearn estimator given the gcs file name.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A sklearn estimator.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")

        if serialized_gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                gcs_utils.download_file_from_gcs(serialized_gcs_path, temp_file.name)
                with open(temp_file.name, mode="rb") as f:
                    obj = pickle.load(f)
        else:
            with open(serialized_gcs_path, mode="rb") as f:
                obj = pickle.load(f)

        return obj


class TorchModelSerializer(serializers_base.Serializer):
    """A serializer for torch.nn.Module objects."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="TorchModelSerializer")
    )

    def serialize(self, to_serialize: TorchModel, gcs_path: str, **kwargs) -> str:
        """Serializes a torch.nn.Module to a gcs path.

        Args:
            to_serialize (torch.nn.Module):
                Required. A PyTorch model object.
            gcs_path (str):
                Required. A GCS uri that the model will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        TorchModelSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_torch_model(to_serialize)
        )

        if gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                torch.save(
                    to_serialize,
                    temp_file.name,
                    pickle_module=cloudpickle,
                    pickle_protocol=constants.PICKLE_PROTOCOL,
                )
                gcs_utils.upload_to_gcs(temp_file.name, gcs_path)
        else:
            torch.save(
                to_serialize,
                gcs_path,
                pickle_module=cloudpickle,
                pickle_protocol=constants.PICKLE_PROTOCOL,
            )

        return gcs_path

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> TorchModel:
        """Deserialize a torch.nn.Module given the gcs file name.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A torch.nn.Module model.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
            ImportError: if torch is not installed.
        """
        del kwargs
        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")

        try:
            import torch
        except ImportError as e:
            raise ImportError("torch is not installed.") from e

        map_location = (
            torch._GLOBAL_DEVICE_CONTEXT.device
            if torch._GLOBAL_DEVICE_CONTEXT
            else None
        )

        if serialized_gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                gcs_utils.download_file_from_gcs(serialized_gcs_path, temp_file.name)
                model = _load_torch_model(temp_file.name, map_location=map_location)
        else:
            model = _load_torch_model(serialized_gcs_path, map_location=map_location)

        return model


# TODO(b/289386023) Add unit tests for LightningTrainerSerialzier
class LightningTrainerSerializer(serializers_base.Serializer):
    """A serializer for lightning.pytorch.Trainer objects."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="LightningTrainerSerializer")
    )

    def _serialize_to_local(self, to_serialize: LightningTrainer, path: str):
        """Serializes a lightning.pytorch.Trainer to a local path.

        Args:
            to_serialize (lightning.pytorch.Trainer):
                Required. A lightning trainer object.
            path (str):
                Required. A local_path that the trainer will be saved to.
        """
        # In remote environment, we store local accelerator connector and default root
        # dir as attributes when we deserialize the trainer. And we need to serialize
        # them in order to retrieve in local environment.
        if getattr(to_serialize, "_vertex_local_accelerator_connector", None):
            with open(f"{path}/local_accelerator_connector", "wb") as f:
                cloudpickle.dump(
                    to_serialize._vertex_local_accelerator_connector,
                    f,
                    protocol=constants.PICKLE_PROTOCOL,
                )
            delattr(to_serialize, "_vertex_local_accelerator_connector")
        else:
            with open(f"{path}/local_accelerator_connector", "wb") as f:
                cloudpickle.dump(
                    to_serialize._accelerator_connector,
                    f,
                    protocol=constants.PICKLE_PROTOCOL,
                )

        if getattr(to_serialize, "_vertex_local_default_root_dir", None):
            with open(f"{path}/local_default_root_dir", "wb") as f:
                cloudpickle.dump(
                    to_serialize._vertex_local_default_root_dir,
                    f,
                    protocol=constants.PICKLE_PROTOCOL,
                )
            delattr(to_serialize, "_vertex_local_default_root_dir")
        else:
            with open(f"{path}/local_default_root_dir", "wb") as f:
                cloudpickle.dump(
                    to_serialize._default_root_dir,
                    f,
                    protocol=constants.PICKLE_PROTOCOL,
                )

        with open(f"{path}/trainer", "wb") as f:
            cloudpickle.dump(to_serialize, f, protocol=constants.PICKLE_PROTOCOL)

        if os.path.exists(to_serialize.logger.root_dir):
            shutil.copytree(
                to_serialize.logger.root_dir,
                f"{path}/{to_serialize.logger.name}",
                dirs_exist_ok=True,
            )

    def serialize(self, to_serialize: LightningTrainer, gcs_path: str, **kwargs) -> str:
        """Serializes a lightning.pytorch.Trainer to a gcs path.

        Args:
            to_serialize (lightning.pytorch.Trainer):
                Required. A lightning trainer object.
            gcs_path (str):
                Required. A GCS uri that the trainer will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        LightningTrainerSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_lightning_model(to_serialize)
            + supported_frameworks._get_cloudpickle_deps()
        )

        if gcs_path.startswith("gs://"):
            with tempfile.TemporaryDirectory() as temp_dir:
                self._serialize_to_local(to_serialize, temp_dir)
                gcs_utils.upload_to_gcs(temp_dir, gcs_path)
        else:
            os.makedirs(gcs_path)
            self._serialize_to_local(to_serialize, gcs_path)

        return gcs_path

    def _deserialize_from_local(self, path: str) -> LightningTrainer:
        """Deserialize a lightning.pytorch.Trainer given a local path.

        Args:
            path (str):
                Required. A local path to the serialized trainer.

        Returns:
            A lightning.pytorch.Trainer object.
        """
        with open(f"{path}/trainer", "rb") as f:
            trainer = cloudpickle.load(f)

        if os.getenv("_IS_VERTEX_REMOTE_TRAINING") == "True":
            # Store the logs in the cwd of remote environment.
            trainer._default_root_dir = _LIGHTNING_ROOT_DIR
            for logger in trainer.loggers:
                # for TensorBoardLogger
                if getattr(logger, "_root_dir", None):
                    logger._root_dir = trainer.default_root_dir
                # for CSVLogger
                if getattr(logger, "_save_dir", None):
                    logger._save_dir = trainer.default_root_dir

            # Store local accelerator connector and root dir as attributes, so that
            # we can retrieve them in local environment.
            with open(f"{path}/local_accelerator_connector", "rb") as f:
                trainer._vertex_local_accelerator_connector = cloudpickle.load(f)

            with open(f"{path}/local_default_root_dir", "rb") as f:
                trainer._vertex_local_default_root_dir = cloudpickle.load(f)
        else:
            with open(f"{path}/local_accelerator_connector", "rb") as f:
                trainer._accelerator_connector = cloudpickle.load(f)

            with open(f"{path}/local_default_root_dir", "rb") as f:
                trainer._default_root_dir = cloudpickle.load(f)

            for logger in trainer.loggers:
                if getattr(logger, "_root_dir", None):
                    logger._root_dir = trainer.default_root_dir
                if getattr(logger, "_save_dir", None):
                    logger._save_dir = trainer.default_root_dir

            for callback in trainer.checkpoint_callbacks:
                callback.dirpath = os.path.join(
                    trainer.default_root_dir,
                    callback.dirpath.replace(_LIGHTNING_ROOT_DIR, ""),
                )
                if callback.best_model_path:
                    callback.best_model_path = os.path.join(
                        trainer.default_root_dir,
                        callback.best_model_path.replace(_LIGHTNING_ROOT_DIR, ""),
                    )
                if callback.kth_best_model_path:
                    callback.kth_best_model_path = os.path.join(
                        trainer.default_root_dir,
                        callback.kth_best_model_path.replace(_LIGHTNING_ROOT_DIR, ""),
                    )
                if callback.last_model_path:
                    callback.last_model_path = os.path.join(
                        trainer.default_root_dir,
                        callback.last_model_path.replace(_LIGHTNING_ROOT_DIR, ""),
                    )

        if os.path.exists(f"{path}/{trainer.logger.name}"):
            shutil.copytree(
                f"{path}/{trainer.logger.name}",
                trainer.logger.root_dir,
                dirs_exist_ok=True,
            )

        return trainer

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> LightningTrainer:
        """Deserialize a lightning.pytorch.Trainer given the gcs path.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A lightning.pytorch.Trainer object.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")

        if serialized_gcs_path.startswith("gs://"):
            with tempfile.TemporaryDirectory() as temp_dir:
                gcs_utils.download_from_gcs(serialized_gcs_path, temp_dir)
                trainer = self._deserialize_from_local(temp_dir)
        else:
            trainer = self._deserialize_from_local(serialized_gcs_path)

        return trainer


class TorchDataLoaderSerializer(serializers_base.Serializer):
    """A serializer for torch.utils.data.DataLoader objects."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="TorchDataLoaderSerializer")
    )

    def _serialize_to_local(self, to_serialize: TorchDataLoader, path: str):
        """Serializes a torch.utils.data.DataLoader to a local path.

        Args:
            to_serialize (torch.utils.data.DataLoader):
                Required. A pytorch dataloader object.
            path (str):
                Required. A local_path that the dataloader will be saved to.
        """
        # save objects by cloudpickle
        with open(f"{path}/dataset.cpkl", "wb") as f:
            cloudpickle.dump(
                to_serialize.dataset, f, protocol=constants.PICKLE_PROTOCOL
            )

        with open(f"{path}/collate_fn.cpkl", "wb") as f:
            cloudpickle.dump(
                to_serialize.collate_fn, f, protocol=constants.PICKLE_PROTOCOL
            )

        with open(f"{path}/worker_init_fn.cpkl", "wb") as f:
            cloudpickle.dump(
                to_serialize.worker_init_fn, f, protocol=constants.PICKLE_PROTOCOL
            )

        # save (str, int, float, bool) values into a json file
        pass_through_args = {
            "num_workers": to_serialize.num_workers,
            "pin_memory": to_serialize.pin_memory,
            "timeout": to_serialize.timeout,
            "prefetch_factor": to_serialize.prefetch_factor,
            "persistent_workers": to_serialize.persistent_workers,
            "pin_memory_device": to_serialize.pin_memory_device,
        }

        # dataloader.generator is a torch.Generator object that defined in c++
        # it cannot be serialized by cloudpickle, so we store its device information
        # and re-instaintiate a new Generator object with this device when deserializing
        pass_through_args["generator_device"] = (
            to_serialize.generator.device.type if to_serialize.generator else None
        )

        # batch_sampler option is mutually exclusive with batch_size, shuffle,
        # sampler, and drop_last.
        # for default batch sampler we store batch_size, drop_last, and sampler object
        # but not batch sampler object.
        if isinstance(to_serialize.batch_sampler, torch.utils.data.BatchSampler):
            pass_through_args["batch_size"] = to_serialize.batch_size
            pass_through_args["drop_last"] = to_serialize.drop_last

            with open(f"{path}/sampler.cpkl", "wb") as f:
                cloudpickle.dump(
                    to_serialize.sampler, f, protocol=constants.PICKLE_PROTOCOL
                )
        # otherwise we only serialize batch sampler and skip batch_size, drop_last,
        # and sampler object.
        else:
            with open(f"{path}/batch_sampler.cpkl", "wb") as f:
                cloudpickle.dump(
                    to_serialize.batch_sampler, f, protocol=constants.PICKLE_PROTOCOL
                )

        with open(f"{path}/pass_through_args.json", "w") as f:
            json.dump(pass_through_args, f)

    def serialize(self, to_serialize: TorchDataLoader, gcs_path: str, **kwargs) -> str:
        """Serializes a torch.utils.data.DataLoader to a gcs path.

        Args:
            to_serialize (torch.utils.data.DataLoader):
                Required. A pytorch dataloader object.
            gcs_path (str):
                Required. A GCS uri that the dataloader will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        TorchDataLoaderSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_torch_dataloader(to_serialize)
        )

        if gcs_path.startswith("gs://"):
            with tempfile.TemporaryDirectory() as temp_dir:
                self._serialize_to_local(to_serialize, temp_dir)
                gcs_utils.upload_to_gcs(temp_dir, gcs_path)
        else:
            os.makedirs(gcs_path)
            self._serialize_to_local(to_serialize, gcs_path)

        return gcs_path

    def _deserialize_from_local(self, path: str) -> TorchDataLoader:
        """Deserialize a torch.utils.data.DataLoader given a local path.

        Args:
            path (str):
                Required. A local path to the serialized dataloader.

        Returns:
            A torch.utils.data.DataLoader object.

        Raises:
            ImportError: if torch is not installed.
        """
        try:
            import torch
        except ImportError as e:
            raise ImportError(
                f"torch is not installed and required to deserialize the file from {path}."
            ) from e

        with open(f"{path}/pass_through_args.json", "r") as f:
            kwargs = json.load(f)

        # re-instantiate Generator
        if kwargs["generator_device"] is not None:
            kwargs["generator"] = torch.Generator(
                kwargs["generator_device"] if torch.cuda.is_available() else "cpu"
            )
        kwargs.pop("generator_device")

        with open(f"{path}/dataset.cpkl", "rb") as f:
            kwargs["dataset"] = cloudpickle.load(f)

        with open(f"{path}/collate_fn.cpkl", "rb") as f:
            kwargs["collate_fn"] = cloudpickle.load(f)

        with open(f"{path}/worker_init_fn.cpkl", "rb") as f:
            kwargs["worker_init_fn"] = cloudpickle.load(f)

        try:
            with open(f"{path}/sampler.cpkl", "rb") as f:
                kwargs["sampler"] = cloudpickle.load(f)
        except FileNotFoundError:
            pass

        try:
            with open(f"{path}/batch_sampler.cpkl", "rb") as f:
                kwargs["batch_sampler"] = cloudpickle.load(f)
        except FileNotFoundError:
            pass

        return torch.utils.data.DataLoader(**kwargs)

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> TorchDataLoader:
        """Deserialize a torch.utils.data.DataLoader given the gcs path.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A torch.utils.data.DataLoader object.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
            ImportError: if torch is not installed.
        """
        del kwargs
        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")

        if serialized_gcs_path.startswith("gs://"):
            with tempfile.TemporaryDirectory() as temp_dir:
                gcs_utils.download_from_gcs(serialized_gcs_path, temp_dir)
                dataloader = self._deserialize_from_local(temp_dir)
        else:
            dataloader = self._deserialize_from_local(serialized_gcs_path)

        return dataloader


class TFDatasetSerializer(serializers_base.Serializer):
    """Serializer responsible for serializing/deserializing a tf.data.Dataset."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="TFDatasetSerializer")
    )

    def serialize(self, to_serialize: TFDataset, gcs_path: str, **kwargs) -> str:
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")
        TFDatasetSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_tensorflow_model(to_serialize)
        )

        try:
            to_serialize.save(gcs_path)
        except AttributeError:
            tf.data.experimental.save(to_serialize, gcs_path)
        return gcs_path

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> TFDataset:
        del kwargs
        try:
            deserialized = tf.data.Dataset.load(serialized_gcs_path)
        except AttributeError:
            deserialized = tf.data.experimental.load(serialized_gcs_path)
        return deserialized


class PandasDataSerializer(serializers_base.Serializer):
    """Serializer for pandas DataFrames."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="PandasDataSerializer")
    )

    def serialize(self, to_serialize: PandasData, gcs_path: str, **kwargs) -> str:
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        PandasDataSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_pandas_dataframe(to_serialize)
        )

        if gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                to_serialize.to_parquet(temp_file.name)
                temp_file.flush()
                temp_file.seek(0)

                gcs_utils.upload_to_gcs(temp_file.name, gcs_path)
        else:
            to_serialize.to_parquet(gcs_path)

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> PandasData:
        del kwargs
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                f"pandas is not installed and required to deserialize the file from {serialized_gcs_path}."
            ) from e

        if serialized_gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                gcs_utils.download_file_from_gcs(serialized_gcs_path, temp_file.name)
                return pd.read_parquet(temp_file.name)
        else:
            return pd.read_parquet(serialized_gcs_path)


class PandasDataSerializerDev(serializers_base.Serializer):
    """Serializer responsible for serializing/deserializing a pandas DataFrame."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="PandasDataSerializerDev")
    )

    def __init__(self):
        super().__init__()
        self.helper = data_serializer_utils._Helper()

    def serialize(self, to_serialize: PandasData, gcs_path: str, **kwargs) -> str:
        del kwargs
        PandasDataSerializerDev._metadata.dependencies = (
            supported_frameworks._get_deps_if_pandas_dataframe(to_serialize)
        )
        try:
            if not (
                isinstance(to_serialize.index, pd.MultiIndex)
                or isinstance(to_serialize.columns, pd.MultiIndex)
            ):
                self.helper.create_placeholder_col_names(to_serialize)
                self.helper.cast_int_to_str(
                    to_serialize, action=data_serializer_utils.ActionType.CAST_COL_NAME
                )
                self.helper.cast_int_to_str(
                    to_serialize, action=data_serializer_utils.ActionType.CAST_ROW_INDEX
                )
                self.helper.cast_int_to_str(
                    to_serialize,
                    action=data_serializer_utils.ActionType.CAST_CATEGORICAL,
                )
            table = pa.Table.from_pandas(to_serialize)
            custom_metadata = {
                data_serializer_utils.df_restore_func_metadata_key.encode(): json.dumps(
                    self.helper.restore_df_actions
                ).encode(),
                data_serializer_utils.df_restore_func_args_metadata_key.encode(): json.dumps(
                    self.helper.restore_df_actions_args
                ).encode(),
                **table.schema.metadata,
            }
            table = table.replace_schema_metadata(custom_metadata)

            with tempfile.TemporaryDirectory() as temp_dir:
                fp = os.path.join(temp_dir, f"{uuid.uuid4()}.parquet")
                pq.write_table(table, fp, compression="GZIP")
                gcs_utils.upload_to_gcs(fp, gcs_path)
        finally:
            # undo ad-hoc mutations on the dataframe
            self.helper.restore_df_actions.reverse()
            self.helper.restore_df_actions_args.reverse()
            for func_str, args in zip(
                self.helper.restore_df_actions, self.helper.restore_df_actions_args
            ):
                func = getattr(self.helper, func_str)
                func(to_serialize, *args) if len(args) > 0 else func(to_serialize)
            return gcs_path

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> PandasData:
        del kwargs
        restored_table = pq.read_table(serialized_gcs_path)
        restored_df = restored_table.to_pandas()

        # get custom metadata
        restore_func_array_json = restored_table.schema.metadata[
            data_serializer_utils.df_restore_func_metadata_key.encode()
        ]
        restore_func_array = json.loads(restore_func_array_json)
        restore_func_array_args_json = restored_table.schema.metadata[
            data_serializer_utils.df_restore_func_args_metadata_key.encode()
        ]
        restore_func_array_args = json.loads(restore_func_array_args_json)
        restore_func_array.reverse()
        restore_func_array_args.reverse()

        for func_str, args in zip(restore_func_array, restore_func_array_args):
            func = getattr(self.helper, func_str)
            func(restored_df, *args) if len(args) > 0 else func(restored_df)
        return restored_df


@dataclasses.dataclass
class BigframeSerializationMetadata(serializers_base.SerializationMetadata):
    """Metadata of BigframeSerializer class.

    Stores extra framework attribute
    """

    framework: Optional[str] = None

    def to_dict(self):
        dct = super().to_dict()
        dct.update({SERIALIZATION_METADATA_FRAMEWORK_KEY: self.framework})
        return dct


class BigframeSerializer(serializers_base.Serializer):
    """Serializer responsible for serializing/deserializing a BigFrames DataFrame.

    Serialization: All frameworks serialize bigframes.dataframe.DataFrame -> parquet (GCS)
    Deserialization: Framework specific deserialize methods are called
    """

    _metadata: serializers_base.SerializationMetadata = BigframeSerializationMetadata(
        serializer="BigframeSerializer", framework=None
    )

    def serialize(
        self,
        to_serialize: Union[BigframesData, PandasData],
        gcs_path: str,
        **kwargs,
    ) -> str:
        # All bigframe serializers will be identical (bigframes.dataframe.DataFrame --> parquet)
        # Record the framework in metadata for deserialization
        BigframeSerializer._metadata.framework = kwargs.get("framework")
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        BigframeSerializer._metadata.dependencies = (
            supported_frameworks._get_deps_if_bigframe(to_serialize)
        )

        # Check if index.name is default and set index.name if not
        if to_serialize.index.name and to_serialize.index.name != "index":
            raise ValueError("Index name must be 'index'")
        if to_serialize.index.name is None:
            to_serialize.index.name = "index"

        # Convert BigframesData to Parquet (GCS)
        parquet_gcs_path = gcs_path + "/*"  # path is required to contain '*'
        to_serialize.to_parquet(parquet_gcs_path, index=True)

    def deserialize(
        self, serialized_gcs_path: str, **kwargs
    ) -> Union[PandasData, BigframesData]:
        del kwargs

        detected_framework = BigframeSerializer._metadata.framework
        if detected_framework == "sklearn":
            return self._deserialize_sklearn(serialized_gcs_path)
        elif detected_framework == "torch":
            return self._deserialize_torch(serialized_gcs_path)
        elif detected_framework == "tensorflow":
            return self._deserialize_tensorflow(serialized_gcs_path)
        else:
            raise ValueError(f"Unsupported framework: {detected_framework}")

    def _deserialize_sklearn(self, serialized_gcs_path: str) -> PandasData:
        """Sklearn deserializes parquet (GCS) --> pandas.DataFrame

        By default, sklearn returns a numpy array which uses CloudPickleSerializer.
        If a bigframes.dataframe.DataFrame is desired for the return type,
        b/291147206 (cl/548228568) is required

        serialized_gcs_path is a folder containing one or more parquet files.
        """
        # Deserialization at remote environment
        try:
            import pandas as pd
        except ImportError as e:
            raise ImportError(
                f"pandas is not installed and required to deserialize the file from {serialized_gcs_path}."
            ) from e

        # Deserialization always happens at remote, so gcs filesystem is mounted to /gcs/
        # pd.read_parquet auto-merges a directory of parquet files
        pd_dataframe = pd.read_parquet(serialized_gcs_path)

        # Drop index now that ordering is guaranteed
        if "index" in pd_dataframe.columns:
            pd_dataframe.drop(columns=["index"], inplace=True)

        return pd_dataframe

    def _deserialize_torch(self, serialized_gcs_path: str) -> TorchTensor:
        """Torch deserializes parquet (GCS) --> torch.tensor

        serialized_gcs_path is a folder containing one or more parquet files.
        """
        # Deserialization at remote environment
        try:
            from torchdata.datapipes.iter import FileLister
        except ImportError as e:
            raise ImportError(
                f"torchdata is not installed and required to deserialize the file from {serialized_gcs_path}."
            ) from e

        # Deserialization always happens at remote, so gcs filesystem is mounted to /gcs/
        # TODO(b/295335262): Implement torch lazy read
        source_dp = FileLister(serialized_gcs_path, masks="")
        parquet_df_dp = source_dp.load_parquet_as_df()

        def preprocess(torch_df):
            torch_df = torch_df.drop("index")
            df_tensor = torch_df.to_tensor()

            # Convert from TorchStruct to Tensor
            cols = []
            for i in range(len(df_tensor)):
                col = df_tensor[i].values
                col = col[:, None]
                cols.append(col)
            deserialized_tensor = torch.cat(cols, 1)
            return deserialized_tensor

        parquet_df_dp = parquet_df_dp.map(preprocess)

        def reduce_tensors(a, b):
            return torch.concat((a, b), axis=0)

        return functools.reduce(reduce_tensors, list(parquet_df_dp))

    def _deserialize_tensorflow(self, serialized_gcs_path: str) -> TFDataset:
        """Tensorflow deserializes parquet (GCS) --> tf.data.Dataset

        serialized_gcs_path is a folder containing one or more parquet files.
        """
        # Deserialization at remote environment
        try:
            import tensorflow_io as tfio
        except ImportError as e:
            raise ImportError(
                f"tensorflow_io is not installed and required to deserialize the file from {serialized_gcs_path}."
            ) from e

        # Deserialization always happens at remote, so gcs filesystem is mounted to /gcs/
        files = os.listdir(serialized_gcs_path + "/")
        files = list(
            map(lambda file_name: serialized_gcs_path + "/" + file_name, files)
        )
        ds = tfio.IODataset.from_parquet(files[0])

        for file_name in files[1:]:
            ds_shard = tfio.IODataset.from_parquet(file_name)
            ds = ds.concatenate(ds_shard)

        # TODO(b/296474656) Parquet must have "target" column for y
        def map_fn(row):
            target = row[b"target"]
            row = {
                k: tf.expand_dims(v, -1)
                for k, v in row.items()
                if k != b"target" and k != b"index"
            }

            def reduce_fn(a, b):
                return tf.concat((a, b), axis=0)

            return functools.reduce(reduce_fn, row.values()), target

        # TODO(b/295535730): Remove hardcoded batch_size of 32
        return ds.map(map_fn).batch(32)


class CloudPickleSerializer(serializers_base.Serializer):
    """Serializer that uses cloudpickle to serialize the object."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="CloudPickleSerializer")
    )

    def serialize(self, to_serialize: Any, gcs_path: str, **kwargs) -> str:
        """Use cloudpickle to serialize a python object to a gcs file path.

        Args:
            to_serialize (Any):
                Required. A python object.
            gcs_path (str):
                Required. A GCS uri that the estimator will be saved to.

        Returns:
            The GCS uri.

        Raises:
            ValueError: if `gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(gcs_path):
            raise ValueError(f"Invalid gcs path: {gcs_path}")

        CloudPickleSerializer._metadata.dependencies = (
            supported_frameworks._get_estimator_requirement(to_serialize)
        )
        serialized = cloudpickle.dumps(to_serialize, protocol=constants.PICKLE_PROTOCOL)
        serializers_base.write_and_upload_data(data=serialized, gcs_filename=gcs_path)
        return gcs_path

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> Any:
        """Use cloudpickle to deserialize a python object given the object's gcs file path.

        Args:
            serialized_gcs_path (str):
                Required. A GCS path to the serialized file.

        Returns:
            A python object.

        Raises:
            ValueError: if `serialized_gcs_path` is not a valid GCS uri.
        """
        del kwargs
        if not _is_valid_gcs_path(serialized_gcs_path):
            raise ValueError(f"Invalid gcs path: {serialized_gcs_path}")

        if serialized_gcs_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                gcs_utils.download_file_from_gcs(serialized_gcs_path, temp_file.name)
                with open(temp_file.name, mode="rb") as f:
                    obj = cloudpickle.load(f)
        else:
            with open(serialized_gcs_path, mode="rb") as f:
                obj = cloudpickle.load(f)

        return obj
