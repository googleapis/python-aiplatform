# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Custom types for the explainers library."""
from typing import Dict, List, Text, Union, NamedTuple, Any
import numpy as np

# Struct type for uCAIP.
StructType = Dict[Text, Any]
# Values a tensor can contain. Dict[Any] represent struct input type.
TensorValue = Union[
    int, float, bool, Text, np.ndarray, List["TensorValue"], StructType
]  # pytype: disable=not-supported-yet
# A tensor can be a list of values or cast to numpy arrays.
Tensor = Union[np.ndarray, List[TensorValue]]  # pytype: disable=not-supported-yet
# Tensors in the explainers library are passed around in a dictionary, where
# keys are the tensor names and values are the tensor values.
TensorMap = Dict[Text, Tensor]
# An instance is a dictionary from input name to the input value format accepted
# by Tensorflow, AI Platform, etc.
Instance = Dict[Text, TensorValue]  # pytype: disable=not-supported-yet
# Instances are usually passed around as a list.
Instances = List[Instance]

SparseTensorNames = NamedTuple(
    "SparseTensorNames", [("values", Text), ("indices", Text), ("dense_shape", Text)]
)
