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

from google.cloud import storage
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils

try:
    import pandas as pd
except ImportError:
    raise ImportError(
        "Pandas is not installed. Please install pandas to use VertexModel"
    )


def _serialize_dataframe(
    artifact_uri: str, obj: pd.DataFrame, dataset_type: str
) -> str:

    """Serializes pandas DataFrame object to GCS.

    Args:
        artifact_uri (str): the GCS bucket where the serialized object will reside.
        obj (pd.DataFrame): the pandas DataFrame to serialize.
        dataset_type (str): the intended use of the dataset (ie. training, testing)

    Returns:
        The GCS path pointing to the serialized DataFrame.
    """

    # Designate csv path and write the pandas DataFrame to the path
    # Convention: file name is my_training_dataset, my_test_dataset, etc.
    if not artifact_uri.startswith("gs://"):
        path_to_csv = "/".join([artifact_uri, "my_" + dataset_type + "_dataset.csv"])
        obj.to_csv(path_to_csv, index=False)
        return path_to_csv

    with tempfile.TemporaryDirectory() as tmpdirname:
        temp_dir = pathlib.Path(tmpdirname) / ("my_" + dataset_type + "_dataset.csv")
        path_to_csv = pathlib.Path(temp_dir)
        obj.to_csv(path_to_csv, index=False)

        gcs_bucket, gcs_blob_prefix = utils.extract_bucket_and_prefix_from_gcs_path(
            artifact_uri
        )

        local_file_name = path_to_csv.name
        blob_path = local_file_name

        if gcs_blob_prefix:
            blob_path = "/".join([gcs_blob_prefix, blob_path])

        client = storage.Client(
            project=initializer.global_config.project,
            credentials=initializer.global_config.credentials,
        )

        bucket = client.bucket(gcs_bucket)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(str(path_to_csv))

        gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
        return gcs_path


def _deserialize_dataframe(artifact_uri: str) -> pd.DataFrame:
    """Deserializes a csv on GCS to a pandas DataFrame object.

    Args:
        artifact_uri (str): the GCS bucket where the serialized object resides.

    Returns:
        The deserialized DataFrame.

    Raises:
        Runtime Error should the CSV object referenced by artifact_uri be invalid.
    """

    if not artifact_uri.startswith("gs://"):
        return pd.read_csv(artifact_uri)

    gcs_bucket, gcs_blob = utils.extract_bucket_and_prefix_from_gcs_path(artifact_uri)

    client = storage.Client(
        project=initializer.global_config.project,
        credentials=initializer.global_config.credentials,
    )

    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(gcs_blob)
    df = pd.DataFrame()

    try:
        with tempfile.TemporaryDirectory() as tmpdirname:
            dest_file = pathlib.Path(tmpdirname) / "deserialized_data.csv"
            blob.download_to_filename(dest_file)
            df = pd.read_csv(dest_file)

    except (ValueError, RuntimeError) as err:
        raise RuntimeError(
            "There was a problem reading the CSV file at '{}': {}".format(
                artifact_uri, err
            )
        )

    # Return a pandas DataFrame read from the csv in the cloud
    return df


_DATA_SERIALIZER_MAP = {pd.DataFrame: (_deserialize_dataframe, _serialize_dataframe)}
