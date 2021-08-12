# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
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

import functools
import pathlib
import tempfile
import torch

from google.cloud import storage
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.experimental.vertex_model.serializers import (
    serializer_utils,
)


def _serialize_local_model(artifact_uri: str, obj: torch.nn.Module, model_type: str):
    """Serializes torch.nn.Module object to GCS.

    Args:
        artifact_uri (str): the GCS bucket where the serialized object will reside.
        obj (torch.nn.Module): the model to serialize.
        dataset_type (str): the model name and usage

    Returns:
        The GCS path pointing to the serialized objet.
    """

    compiled_custom_model = torch.jit.script(obj)

    if not artifact_uri.startswith("gs://"):
        path_to_model = artifact_uri + "/my_" + model_type + "_model.pth"
        torch.jit.save(compiled_custom_model, path_to_model)
        return path_to_model

    gcs_bucket, gcs_blob_prefix = utils.extract_bucket_and_prefix_from_gcs_path(
        artifact_uri
    )

    path_to_model = serializer_utils.serialize_to_tmp_and_copy_to_gcs(
        "my_" + model_type + "_model.pth",
        gcs_bucket,
        gcs_blob_prefix,
        functools.partial(torch.jit.save, compiled_custom_model),
    )


def _deserialize_remote_model(artifact_uri: str) -> torch.nn.Module:
    """Deserializes a model on GCS to a torch.nn.Module object.

    Args:
        artifact_uri (str): the GCS bucket where the serialized object resides.

    Returns:
        The deserialized model.

    Raises:
        Runtime Error should the model object referenced by artifact_uri be invalid.
    """

    if not artifact_uri.startswith("gs://"):
        loaded_compiled_custom_model = torch.jit.load(artifact_uri)
        return loaded_compiled_custom_model

    gcs_bucket, gcs_blob = utils.extract_bucket_and_prefix_from_gcs_path(artifact_uri)

    client = storage.Client(
        project=initializer.global_config.project,
        credentials=initializer.global_config.credentials,
    )

    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(gcs_blob)
    loaded_compiled_custom_model = None

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest_file = pathlib.Path(tmpdirname) / "deserialized_model.pt"
            blob.download_to_filename(dest_file)
            loaded_compiled_custom_model = torch.jit.load(dest_file)

    except (ValueError, RuntimeError) as err:
        raise RuntimeError(
            "There was a problem reading the model at '{}': {}".format(
                artifact_uri, err
            )
        )

    # Return a pandas DataFrame read from the csv in the cloud
    return loaded_compiled_custom_model
