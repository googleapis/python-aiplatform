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

# Wrapper function to handle cloud training extension of user code
def vertex_function_wrapper(method, training_mode):

    # Check we are using the subclass definition
    print(method.__self__.__class__)

    if training_mode == 'local':
        return method

    def f(*args, **kwargs):
        dataset = kwargs['dataset']

        serializer = 
            method.__self__.__class__._data_serialization_mapping[type(dataset)][1]
        serializer(dataset, staging_bucket + 'dataset.csv', args[1], '~/temp_dir', 'training')

        """            
        # Edit run of job here
        job = aiplatform.CustomTrainingJob(...)
        job.run(
            args = ['dataset',  staging_bucket + 'dataset.csv',
                    'dataset_type', dataset] 
        ) 
        """

    def p(*args, **kwargs):
        pass

    def bp(*args, **kwargs):
        pass
    
    def e(*args, **kwargs):
        pass

    if method.__name__ == 'fit':
        return f
    elif method.__name__ == 'predict':
        return p
    elif method.__name__ == 'batch_predict':
        return bp
    else:
        return e


class VertexModel:

    _data_serialization_mapping = {
        pd.DataFrame : (deserialize_data_in_memory, serialize_data_in_memory).
        DataLoader: (deserialize_dataloader, serialize_dataloader)
    }

    """ Parent class that users can extend to use the Vertex AI SDK """
    def __init__(self):
        # Default to local training on creation, at least for this prototype.
        self.training_mode = 'local'

        self.fit = vertex_function_wrapper(self.fit, self.training_mode)
        self.predict = vertex_function_wrapper(self.predict, self.training_mode)
        self.batch_predict = vertex_function_wrapper(self.batch_predict, self.training_mode)
        self.eval = vertex_function_wrapper(self.eval, self.training_mode)

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

