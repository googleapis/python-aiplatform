# -*- coding: utf-8 -*-

# Copyright 2020 Google LLC
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

import abc
from concurrent import futures
import datetime
import functools
import inspect
import logging
import pandas as pd
import sys
import threading
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

from google.api_core import operation
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import encryption_spec as gca_encryption_spec


class VertexModel:

    _data_serialization_mapping = {
        pd.DataFrame : (deserialize_data_in_memory, serialize_data_in_memory)
    }

    # Default to local training on creation, at least for this prototype.
    self.training_mode = 'local'

    """ Parent class that users can extend to use the Vertex AI SDK """
    def __init__(self):
        if self.training_mode == 'cloud':
            self.fit = vertex_function_wrapper(self.fit)
            self.predict = vertex_function_wrapper(self.predict)
            self.batch_predict = vertex_function_wrapper(self.batch_predict)
            self.eval = vertex_function_wrapper(self.eval)

    def serialize_data_in_memory(self, artifact_uri, obj: pd.Dataframe, temp_dir: str, dataset_type: str):
        """ Provides out-of-the-box serialization for input """

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
                                credentials=initializer.global_config.credentials))

        bucket = client.bucket(gcs_bucket)
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(path_to_csv)

        gcs_path = "".join(["gs://", "/".join([blob.bucket.name, blob.name])])
        return gcs_path

    def deserialize_data_in_memory(cls, artifact_uri):
        """ Provides out-of-the-box deserialization after training and prediction is complete """
        
        gcs_bucket, gcs_blob = utils.extract_bucket_and_prefix_from_gcs_path(
            artifact_uri
        )

        client = storage.Client(project=initializer.global_config.project, 
                                credentials=initializer.global_config.credentials)
        bucket = client.bucket(gcs_bucket)
        blob = bucket.blob(gcs_blob)

        # Incrementally download the CSV file until the header is retrieved
        first_new_line_index = -1
        start_index = 0
        increment = 1000
        line = ""

        try:
            logger = logging.getLogger("google.resumable_media._helpers")
            logging_warning_filter = utils.LoggingFilter(logging.INFO)
            logger.addFilter(logging_warning_filter)

            while first_new_line_index == -1:
                line += blob.download_as_bytes(
                    start=start_index, end=start_index + increment
                ).decode("utf-8")

                first_new_line_index = line.find("\n")
                start_index += increment

            header_line = line[:first_new_line_index]

            # Split to make it an iterable
            header_line = header_line.split("\n")[:1]

            csv_reader = csv.reader(header_line, delimiter=",")
        except (ValueError, RuntimeError) as err:
            raise RuntimeError(
                "There was a problem extracting the headers from the CSV file at '{}': {}".format(
                    gcs_csv_file_path, err
                )
            )
        finally:
            logger.removeFilter(logging_warning_filter)

        # Return a pandas DataFrame read from the csv in the cloud
        return pandas.read_csv(next(csv_reader))

    def serialize_remote_dataloader:
        # writes the referenced data to the run-time bucket
        pass

    def deserialize_remote_dataloader:
        # read the data from a run-time bucket 
        # and reformat to a DataLoader
        pass

    def serialize_local_dataloader:
        # finds the local source, and copies 
        # data to the user-designated staging bucket
        pass

    def deserialize_local_dataloader:
        # read the data from user-designated staging bucket and
        # reformat to a DataLoader
        pass

    def serialize_dataloader:
        # introspect to determine which method is called
        pass

    def deserialize_dataloader:
        # introspect to determine which method is called
        pass

    @abc.abstractmethod
    def fit(self, data, epochs, learning_rate, dataset: pd.DataFrame):
        """ Train model. """
        pass

    @abc.abstractmethod
    def predict(self, data):
        """ Make predictions on training data. """
        pass

    @abc.abstractmethod
    def batch_predict(self, data, target):
        """ Make predictions on training data. """
        pass

    @abc.abstractmethod
    def eval(self, data):
        """ Evaluate model. """
        pass

    def vertex_function_wrapper(method):

        # how to determine function type within another function??
        def f(*args, **kwargs):
            dataset = kwargs['dataset']

            serializer = fit_method.__self__.__class__._data_serialization_mapping[type(dataset)][1]
            serializer(dataset, staging_bucket + 'dataset.csv', args[1], '~/temp_dir', 'training')

            """            
            # Edit run of job here?
            job = aiplatform.CustomTrainingJob(...)
            job.run(
                args = ['dataset',  staging_bucket + 'dataset.csv',
                        'dataset_type', dataset] 
            ) 
            """

        if (fit_method.__name__ == 'fit'):
            f(inspect.signature(fit_method))

        # TODO: wrapper for predict and/or eval (could be the same function)

        # def p(*args, **kwargs):
        
        

