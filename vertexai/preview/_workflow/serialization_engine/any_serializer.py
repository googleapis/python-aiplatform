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
import json
import os
import pathlib
import tempfile
from typing import Any, Dict, Union, List, TypeVar, Type

from google.cloud.aiplatform import base
from google.cloud.aiplatform.utils import gcs_utils
from vertexai.preview._workflow.serialization_engine import (
    serializers,
    serializers_base,
)
from vertexai.preview._workflow.shared import (
    supported_frameworks,
)

from packaging import requirements

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

    PandasData = pd.DataFrame
except ImportError:
    pd = None
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
except ImportError:
    torch = None
    TorchModel = Any
    TorchDataLoader = Any

try:
    import lightning.pytorch as pl

    LightningTrainer = pl.Trainer
except ImportError:
    pl = None
    LightningTrainer = Any


T = TypeVar("T")

Types = Union[
    PandasData,
    BigframesData,
    SklearnEstimator,
    KerasModel,
    TorchModel,
    LightningTrainer,
]

_LOGGER = base.Logger("vertexai.serialization_engine")

SERIALIZATION_METADATA_FILENAME = "serialization_metadata"
SERIALIZATION_METADATA_SERIALIZER_KEY = "serializer"
SERIALIZATION_METADATA_DEPENDENCIES_KEY = "dependencies"
SERIALIZATION_METADATA_FRAMEWORK_KEY = "framework"

_LIGHTNING_ROOT_DIR = "/vertex_lightning_root_dir/"


def _get_metadata_path_from_file_gcs_uri(gcs_uri: str) -> str:
    gcs_pathlibpath = pathlib.Path(gcs_uri)
    prefix = _get_uri_prefix(gcs_uri=gcs_uri)
    return os.path.join(
        prefix,
        f"{SERIALIZATION_METADATA_FILENAME}_{gcs_pathlibpath.stem}.json",
    )


def _get_uri_prefix(gcs_uri: str) -> str:
    """Gets the directory of the gcs_uri.

    Example:
      1) file uri:
        _get_uri_prefix("gs://<bucket>/directory/file.extension") == "gs://
        <bucket>/directory/"
      2) folder uri:
        _get_uri_prefix("gs://<bucket>/parent_dir/dir") == "gs://<bucket>/
        parent_dir/"
    Args:
        gcs_uri: A string starting with "gs://" that represent a gcs uri.
    Returns:
        The parent gcs directory in string format.
    """
    # For tensorflow, the uri may be "gs://my-bucket/saved_model/"
    if gcs_uri.endswith("/"):
        gcs_uri = gcs_uri[:-1]
    gcs_pathlibpath = pathlib.Path(gcs_uri)
    file_name = gcs_pathlibpath.name
    return gcs_uri[: -len(file_name)]


def _check_dependency_versions(required_packages: List[str]):
    for package in required_packages:
        requirement = requirements.Requirement(package)
        package_name = requirement.name
        current_version = supported_frameworks._get_version_for_package(package_name)
        if not requirement.specifier.contains(current_version):
            _LOGGER.warning(
                "%s's version is %s, while the required version is %s",
                package_name,
                current_version,
                requirement.specifier,
            )


def _get_custom_serializer_path_from_file_gcs_uri(
    gcs_uri: str, serializer_name: str
) -> str:
    prefix = _get_uri_prefix(gcs_uri=gcs_uri)
    return os.path.join(prefix, f"{serializer_name}")


class AnySerializer(serializers_base.Serializer):
    """A serializer that can routes any object to their own serializer."""

    _metadata: serializers_base.SerializationMetadata = (
        serializers_base.SerializationMetadata(serializer="AnySerializer")
    )

    def __init__(self):
        super().__init__()
        # Register with default serializers
        AnySerializer._register(object, serializers.CloudPickleSerializer)
        if sklearn:
            AnySerializer._register(
                sklearn.base.BaseEstimator, serializers.SklearnEstimatorSerializer
            )
        if keras:
            AnySerializer._register(
                keras.models.Model, serializers.KerasModelSerializer
            )
            AnySerializer._register(
                keras.callbacks.History, serializers.KerasHistoryCallbackSerializer
            )
        if tf:
            AnySerializer._register(tf.data.Dataset, serializers.TFDatasetSerializer)
        if torch:
            AnySerializer._register(torch.nn.Module, serializers.TorchModelSerializer)
            AnySerializer._register(
                torch.utils.data.DataLoader, serializers.TorchDataLoaderSerializer
            )
        if pl:
            AnySerializer._register(pl.Trainer, serializers.LightningTrainerSerializer)
        if bf:
            AnySerializer._register(
                bf.dataframe.DataFrame, serializers.BigframeSerializer
            )
        if pd:
            AnySerializer._register(pd.DataFrame, serializers.PandasDataSerializer)

    @classmethod
    def _get_custom_serializer(cls, type_cls):
        return cls._custom_serialization_scheme.get(type_cls)

    @classmethod
    def _get_predefined_serializer(cls, type_cls):
        return cls._serialization_scheme.get(type_cls)

    def serialize(self, to_serialize: T, gcs_path: str, **kwargs) -> Dict[str, Any]:
        """Simplified version of serialize()."""
        metadata_path = _get_metadata_path_from_file_gcs_uri(gcs_path)
        # TODO(b/277906396): consider implementing object-level serialization.

        for i, step_type in enumerate(
            to_serialize.__class__.__mro__ + to_serialize.__class__.__mro__
        ):
            # Iterate through the custom serialization scheme first.
            if (
                i < len(to_serialize.__class__.__mro__)
                and step_type not in AnySerializer._custom_serialization_scheme
            ) or (
                i >= len(to_serialize.__class__.__mro__)
                and step_type not in AnySerializer._serialization_scheme
            ):
                continue
            elif i < len(to_serialize.__class__.__mro__):
                serializer = AnySerializer._get_custom_serializer(
                    step_type
                ).get_instance()  # pytype: disable=attribute-error
                # If the Serializer is a custom Serializer, serialize the
                # Custom Serializer first.
                serializer_path = _get_custom_serializer_path_from_file_gcs_uri(
                    gcs_path, serializer.__class__.__name__
                )
                serializers.CloudPickleSerializer().serialize(
                    serializer, serializer_path
                )
            else:
                serializer = AnySerializer._get_predefined_serializer(
                    step_type
                ).get_instance()

            try:
                serializer.serialize(
                    to_serialize=to_serialize, gcs_path=gcs_path, **kwargs
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                if serializer.__class__.__name__ != "CloudPickleSerializer":
                    _LOGGER.warning(
                        "Failed to serialize %s with %s due to error %s",
                        to_serialize.__class__.__name__,
                        serializer.__class__.__name__,
                        e,
                    )
                    # Falling back to Serializers of super classes
                    continue
                else:
                    raise serializers_base.SerializationError from e

            metadata = serializer._metadata.to_dict()
            serializers_base.write_and_upload_data(
                json.dumps(metadata).encode(), metadata_path
            )

            return metadata

    def deserialize(self, serialized_gcs_path: str, **kwargs) -> T:
        """Routes the corresponding Serializer based on the metadata."""
        metadata_path = _get_metadata_path_from_file_gcs_uri(serialized_gcs_path)

        if metadata_path.startswith("gs://"):
            with tempfile.NamedTemporaryFile() as temp_file:
                gcs_utils.download_file_from_gcs(metadata_path, temp_file.name)
                with open(temp_file.name, mode="rb") as f:
                    metadata = json.load(f)
        else:
            with open(metadata_path, mode="rb") as f:
                metadata = json.load(f)

        _LOGGER.debug(
            "deserializing from %s, metadata is %s", serialized_gcs_path, metadata
        )

        serializer_cls_name = metadata[SERIALIZATION_METADATA_SERIALIZER_KEY]
        packages = metadata[SERIALIZATION_METADATA_DEPENDENCIES_KEY]
        _check_dependency_versions(packages)
        serializer_class = getattr(
            serializers, serializer_cls_name, None
        ) or globals().get(serializer_cls_name)
        if not serializer_class:
            # Serializer is an unregistered custom Serializer.
            # Deserialize serializer.
            serializer_path = _get_custom_serializer_path_from_file_gcs_uri(
                serialized_gcs_path, serializer_cls_name
            )
            serializer = serializers.CloudPickleSerializer().deserialize(
                serialized_gcs_path=serializer_path
            )
        else:
            serializer = serializer_class.get_instance()

        # TODO(b/277906396): implement object-level serialization.
        if SERIALIZATION_METADATA_FRAMEWORK_KEY in metadata:
            serializer.__class__._metadata = serializers.BigframeSerializationMetadata(
                **metadata
            )
        else:
            serializer.__class__._metadata = serializers_base.SerializationMetadata(
                **metadata
            )

        obj = serializer.deserialize(serialized_gcs_path=serialized_gcs_path, **kwargs)
        if not serializer_class:
            # Register the serializer
            AnySerializer.register_custom(obj.__class__, serializer.__class__)
            AnySerializer._instances[serializer.__class__] = serializer
        return obj


def register_serializer(
    to_serialize_type: Type[Any], serializer_cls: Type[serializers_base.Serializer]
):
    """Registers a Serializer for a specific type.

    Example Usage:

        ```
        import vertexai

        # define a custom Serializer
        class KerasCustomSerializer(
                vertexai.preview.developer.Serializer):
            _metadata = vertexai.preview.developer.SerializationMetadata()

            def serialize(self, to_serialize, gcs_path):
                ...
            def deserialize(self, gcs_path):
                ...

        KerasCustomSerializer.register_requirements(
                ['library1==1.0.0', 'library2<2.0'])
        vertexai.preview.developer.register_serializer(
                keras.models.Model, KerasCustomSerializer)
        ```

    Args:
        to_serialize_type: The class that is supposed to be serialized with
            the to-be-registered custom Serializer.
        serializer_cls: The custom Serializer to be registered.
    """
    any_serializer = AnySerializer()
    any_serializer.register_custom(
        to_serialize_type=to_serialize_type, serializer_cls=serializer_cls
    )


try:
    _any_serializer = AnySerializer()
except ImportError:
    _LOGGER.warning(
        "cloudpickle is not installed. Please call `pip install google-cloud-aiplatform[preview]`."
    )
