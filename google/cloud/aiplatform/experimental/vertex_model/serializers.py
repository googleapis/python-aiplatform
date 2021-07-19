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
import inspect
import logging
import pandas as pd
import sys
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Iterable,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

import proto
import torch 

from google.api_core import operation
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import encryption_spec as gca_encryption_spec
from google.cloud import aiplatform
                         
from torch.utils.data import Dataset, Dataloader

def _serialize_dataframe(artifact_uri: str, obj: pd.DataFrame, 
                                 temp_dir: str, dataset_type: str) -> str:

    """Serializes pandas DataFrame object to GCS.

    Args:
        artifact_uri: the GCS bucket where the serialized object will reside.
        obj: the pandas DataFrame to serialize.
        temp_dir: the temporary path where this method will write a csv representation
                  of obj.

    Returns:
        The GCS path pointing to the serialized DataFrame.
    """   
        
    # Designate csv path and write the pandas DataFrame to the path
    # Convention: file name is my_training_dataset, my_test_dataset, etc.
    path_to_csv = temp_dir + "/" + "my_" + dataset_type + "_dataset.csv"
    obj.to_csv(path_to_csv)

    gcs_bucket, gcs_blob_prefix = extract_bucket_and_prefix_from_gcs_path(artifact_uri)

    local_file_name = pathlib.Path(path_to_csv).name
    blob_path = local_file_name

    if gcs_blob_prefix:
        blob_path = "/".join([gcs_blob_prefix, blob_path])

    client = storage.Client(project=initializer.global_config.project, 
                            credentials=initializer.global_config.credentials)

    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(path_to_csv)

    gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
    return gcs_path

def _deserialize_dataframe(cls, artifact_uri: str) -> str:
    """ Provides out-of-the-box deserialization after training and prediction is complete """
    
    gcs_bucket, gcs_blob = utils.extract_bucket_and_prefix_from_gcs_path(
        artifact_uri
    )

    client = storage.Client(project=initializer.global_config.project, 
                            credentials=initializer.global_config.credentials)
    bucket = client.bucket(gcs_bucket)
    blob = bucket.blob(gcs_blob)

    raise NotImplementedError

def _serialize_remote_dataloader:
    # writes the referenced data to the run-time bucket
    raise NotImplementedError

def _deserialize_remote_dataloader:
    # read the data from a run-time bucket 
    # and reformat to a DataLoader
    raise NotImplementedError

def _serialize_local_dataloader:
    # finds the local source, and copies 
    # data to the user-designated staging bucket
    raise NotImplementedError

def _deserialize_local_dataloader:
    # read the data from user-designated staging bucket and
    # reformat to a DataLoader
    raise NotImplementedError

def _serialize_dataloader:
    # introspect to determine which method is called
    raise NotImplementedError

def _deserialize_dataloader:
    # introspect to determine which method is called
    raise NotImplementedError
