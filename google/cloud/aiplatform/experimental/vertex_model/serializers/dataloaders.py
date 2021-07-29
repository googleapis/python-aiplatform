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

import pathlib
import tempfile
import torch

from torch.data.utils import DataLoader

from google.cloud import storage
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils


def _serialize_remote_dataloader(
    artifact_uri: str,
    dataloader_path: str,
    obj: torch.utils.data.DataLoader,
    dataset_type: str,
) -> str:
    """writes the referenced data to the run-time bucket"""
    # Create a client object
    client = storage.Client(
        project=initializer.global_config.project,
        credentials=initializer.global_config.credentials,
    )

    # Retrieve the source and blob names from the dataloader path
    (
        source_bucket_name,
        source_blob_prefix,
    ) = utils.extract_bucket_and_prefix_from_gcs_path(dataloader_path)

    # Retrieve the source and blob names from the artifact URI
    (
        destination_bucket_name,
        destination_blob_prefix,
    ) = utils.extract_bucket_and_prefix_from_gcs_path(artifact_uri)

    # Retrieve the blob and bucket name of the original GCS object
    dataloader_path = pathlib.Path(dataloader_path)
    local_file_name = dataset_type + "_" + dataloader_path.name
    source_blob_name = local_file_name

    if source_blob_prefix:
        source_blob_name = "/".join([source_blob_prefix, source_blob_name])

    source_bucket = client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)

    # Create a bucket and blob using the artifact URI
    destination_bucket = client.bucket(destination_bucket_name)

    destination_blob_name = source_blob_name
    if destination_blob_prefix:
        destination_blob_name = "/".join(
            [destination_blob_prefix, destination_blob_name]
        )

    # Copy over the object from the source bucket to the new bucket
    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name
    )

    data_gcs_path = "".join(
        ["gs://", "/".join([destination_bucket_name, blob_copy.name])]
    )

    # Return the final GCS path (of the DataLoader) with data path
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = pathlib.Path(tmpdirname) / ("my_" + dataset_type + "_dataloader.pth")
        path_to_dataloader = pathlib.Path(temp_dir)
        torch.save(obj, temp_dir)

        local_file_name = path_to_dataloader.name
        blob_path = local_file_name

        if destination_blob_prefix:
            blob_path = "/".join([destination_blob_prefix, blob_path])

        blob = destination_bucket.blob(blob_path)
        blob.upload_from_filename(str(path_to_dataloader))

        gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
        return gcs_path, data_gcs_path


def _serialize_local_dataloader(
    artifact_uri: str,
    dataloader_path: str,
    obj: torch.utils.data.DataLoader,
    dataset_type: str,
) -> str:

    dataloader_path = pathlib.Path(dataloader_path)

    gcs_bucket, gcs_blob_prefix = utils.extract_bucket_and_prefix_from_gcs_path(
        artifact_uri
    )

    data_local_file_name = dataset_type + "_" + dataloader_path.name
    data_blob_path = data_local_file_name

    if gcs_blob_prefix:
        data_blob_path = "/".join([gcs_blob_prefix, data_blob_path])

    client = storage.Client(
        project=initializer.global_config.project,
        credentials=initializer.global_config.credentials,
    )

    bucket = client.bucket(gcs_bucket)
    data_blob = bucket.blob(data_blob_path)
    data_blob.upload_from_filename(str(dataloader_path))

    data_gcs_path = "".join(
        ["gs://", "/".join([data_blob.bucket.name, data_blob.name])]
    )

    # Return the final GCS path (of the DataLoader) with data path
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = pathlib.Path(tmpdirname) / ("my_" + dataset_type + "_dataloader.pth")
        path_to_dataloader = pathlib.Path(temp_dir)
        torch.save(obj, temp_dir)

        local_file_name = path_to_dataloader.name
        blob_path = local_file_name

        if gcs_blob_prefix:
            blob_path = "/".join([gcs_blob_prefix, blob_path])

        blob = gcs_bucket.blob(blob_path)
        blob.upload_from_filename(str(path_to_dataloader))

        gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
        return gcs_path, data_gcs_path


def _serialize_dataloader(
    artifact_uri: str, obj: torch.data.utils.DataLoader, dataset_type: str
) -> str:
    # First, access the Dataset
    my_dataset = getattr(obj, "dataset")

    # Then, get the source path
    root = getattr(my_dataset, "root")

    # Decide whether to pass to remote or local serialization
    if root[0:6] == "gs://":
        return _serialize_remote_dataloader(artifact_uri, root, obj, dataset_type)
    else:
        return _serialize_local_dataloader(artifact_uri, root, obj, dataset_type)


def _deserialize_dataloader(artifact_uri: str) -> DataLoader:
    # Tentatively using torch.load, which should support dataloader
    # serialization.
    dataloader = torch.load(artifact_uri)
    return dataloader
