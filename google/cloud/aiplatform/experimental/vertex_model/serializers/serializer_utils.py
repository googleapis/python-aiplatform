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
from typing import Callable

from google.cloud import storage
from google.cloud.aiplatform import initializer


def serialize_to_tmp_and_copy_to_gcs(
    file_name: str,
    destination_bucket: storage.Bucket,
    blob_prefix: str,
    serialize_fn: Callable[[str], None],
):
    """Serializes an object to a specified GCS bucket by first
       writing the object to a temporary directory then copying
       over that file.

    Args:
        file_name (str): the file name of the temporary file created during runtime
        destination_bucket (storage.Bucket): the bucket where the serialized object
                                             will reside
        blob_prefix (str): the blob prefix for the serialized object's file
        serialize_fn (Callable[[str], None]): the function used to serialize the object
                                              to a file.

    Returns:
        The object stored at the given location.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = tmpdirname + "/" + file_name
        tmp_dir_path = pathlib.Path(temp_dir)
        serialize_fn(temp_dir)

        blob_path = tmp_dir_path.name

        if blob_prefix:
            blob_path = "/".join([blob_prefix, blob_path])

        # Create a client object
        client = storage.Client(
            project=initializer.global_config.project,
            credentials=initializer.global_config.credentials,
        )

        bucket = client.bucket(destination_bucket)
        blob = bucket.blob(blob_path)

        blob.upload_from_filename(temp_dir)

        gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
        return gcs_path
