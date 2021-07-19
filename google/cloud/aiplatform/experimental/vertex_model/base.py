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
import torch 

from google.api_core import operation
from google.auth import credentials as auth_credentials
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.compat.types import encryption_spec as gca_encryption_spec
from google.cloud import aiplatform
                         
from torch.utils.data import Dataset, Dataloader
from . import serializers  
from . import source

# Wrapper function to handle cloud training extension of user code
def vertex_fit_function_wrapper(method):

    @functools.wraps(method)
    def f(*args, **kwargs):
        if method.__self__.training_mode == 'local':
            return method(*args, **kwargs)
        
        obj = method.__self__
        cls_name = obj.__class__.__name__

        training_source = _make_class_source(obj)

        source = _make_source(
            cls_source=training_source,
            cls_name=cls_name,
            instance_method=method.__name__)
            
        with tempfile.TemporaryDirectory() as tmpdirname:
            script_path = pathlib.Path(tmpdirname) / "training_script.py"

            with open(script_path, 'w') as f:
                f.write(source)
        
            bound_args = inspect.signature(method).bind(*args, **kwargs)
            dataset = bound_args.arguments.get('dataset')
              
            # may need to throw here if this is not set, users must
            # call aiplatform.init(staging_bucket='gs://....')
            staging_bucket = aiplatform.initializer.global_config.staging_bucket

            # TODO: serialize data to GCS
            # serializer = method.__self__.__class__._data_serialization_mapping[type(dataset)][1]
            # training_data_uri = 
            #   serializer(staging_bucket + 'dataset.csv', data, args[1], '~/temp_dir/', 'training')

            obj._training_job = aiplatform.CustomTrainingJob(
                display_name='my_training_job',
                script_path=str(script_path),

                # programatically determine the dependency in the future
                requirements = ['pandas>=1.8'],

                # https://cloud.google.com/vertex-ai/docs/training/pre-built-containers
                container_uri='us-docker.pkg.dev/vertex-ai/training/pytorch-xla.1-7:latest')
            
            # In the custom training job, a MODEL directory will be provided as an env var
            # our code should serialize our MODEL to that directory

            method.__self__._training_job.run(replica_count=1)

    return f


class VertexModel:

    _data_serialization_mapping = {
        pd.DataFrame : (_deserialize_dataframe, _serialize_dataframe).
        # DataLoader: (deserialize_dataloader, serialize_dataloader)
    }

    """ Parent class that users can extend to use the Vertex AI SDK """
    def __init__(self):
        # Default to local training on creation, at least for this prototype.
        self.training_mode = 'local'

        # TODO: define default output directory for results (timestapped in user's
        #       GCS bucket)

        self._model = None

        self.fit = vertex_function_wrapper(self.fit) 
        # self.predict = vertex_function_wrapper(self.predict, self.training_mode)
        # self.batch_predict = vertex_function_wrapper(self.batch_predict, self.training_mode)
        # self.eval = vertex_function_wrapper(self.eval, self.training_mode)

    @abc.abstractmethod
    def fit(self, data, epochs, learning_rate, dataset: pd.DataFrame, output_directory):
        """ Train model. """
        pass

    @abc.abstractmethod
    def predict(self, data, target, dataset: pd.DataFrame):
        """ Make predictions on training data. """
        pass

    @abc.abstractmethod
    def batch_predict(self, data, target, dataset: pd.DataFrame):
        """ Make predictions on training data. """
        pass

    @abc.abstractmethod
    def eval(self, data, target, dataset: pd.DataFrame):
        """ Evaluate model. """
        pass
