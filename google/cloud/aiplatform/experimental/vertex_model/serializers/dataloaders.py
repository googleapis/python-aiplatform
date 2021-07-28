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
import torch

from google.cloud import storage
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils


def _serialize_remote_dataloader(
    artifact_uri: str, dataloader_path: str, dataset_type: str
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
    local_file_name = dataloader_path.name
    source_blob_name = local_file_name

    if source_blob_prefix:
        source_blob_name = "/".join([source_blob_prefix, source_blob_name])

    source_bucket = client.bucket(source_bucket_name)
    source_blob = source_bucket.blob(source_blob_name)

    # Create a bucket and blob using the artifact URI
    destination_bucket = client.bucket(destination_bucket_name)

    destination_blob_name = source_blob_name
    if destination_blob_prefix:
        destination_blob_name = "/".join([destination_blob_prefix, destination_blob_name])

    # Copy over the object from the source bucket to the new bucket
    blob_copy = source_bucket.copy_blob(
        source_blob, destination_bucket, destination_blob_name
    )

    # Return the final GCS path
    gcs_path = "".join(["gs://", "/".join([destination_bucket_name, blob_copy.name])])
    return gcs_path


def _deserialize_remote_dataloader():
    # read the data from a run-time bucket
    # and reformat to a DataLoader
    raise NotImplementedError


def _serialize_local_dataloader(
    artifact_uri: str, dataloader_path: str, dataset_type: str
) -> str:

    dataloader_path = pathlib.Path(dataloader_path)

    gcs_bucket, gcs_blob_prefix = utils.extract_bucket_and_prefix_from_gcs_path(
        artifact_uri
    )

    local_file_name = dataloader_path.name
    blob_path = local_file_name

    if gcs_blob_prefix:
        blob_path = "/".join([gcs_blob_prefix, blob_path])

    client = storage.Client(
        project=initializer.global_config.project,
        credentials=initializer.global_config.credentials,
    )

    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(str(dataloader_path))

    gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
    return gcs_path


def _deserialize_local_dataloader():
    # read the data from user-designated staging bucket and
    # reformat to a DataLoader
    raise NotImplementedError


def _serialize_dataloader(
    artifact_uri: str, obj: torch.data.utils.DataLoader, dataset_type: str
) -> str:
    # First, access the Dataset
    my_dataset = getattr(obj, "dataset")

    # Then, get the source path
    root = getattr(my_dataset, "root")

    # Decide whether to pass to remote or local serialization
    if root[0:6] == "gs://":
        return _serialize_remote_dataloader(
            artifact_uri, root, dataset_type
        )
    else:
        return _serialize_local_dataloader(
            artifact_uri, root, dataset_type
        )


def _deserialize_dataloader():
    # introspect to determine which method is called
    raise NotImplementedError
