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

import pandas as pd
import sys

from lit_nlp.api import dataset as lit_dataset
from lit_nlp.api import types as lit_types
from typing import Any, List, OrderedDict


def create_lit_dataset(
    dataset: "pd.Dataframe", columns: OrderedDict[str, "lit_types.LitType"] = None
) -> "lit_dataset.Dataset":
    """Creates a LIT Dataset object.
        Args:
          dataset:
              Required. A Pandas Dataframe that includes feature column names and data.
          columns:
              Required. An OrderedDict of string names matching the columns of the dataset
              as the key, and the associated LitType of the column.
        Returns:
            A LIT Dataset object that has the data from the dataset provided.
        Raises:
            ImportError if LIT or Pandas is not installed.
    """
    if "pandas" not in sys.modules:
        raise ImportError(
            "Pandas is not installed and is required to read the dataset. "
            'Please install Pandas using "pip install python-aiplatform[lit]"'
        )
    try:
        from lit_nlp.api import dataset as lit_dataset
    except ImportError:
        raise ImportError(
            "LIT is not installed and is required to get Dataset as the return format. "
            'Please install the SDK using "pip install python-aiplatform[lit]"'
        )

    class VertexLitDataset(lit_dataset.Dataset):
        def __init__(self):
            self._examples = dataset.to_dict(orient="records")

        def spec(self):
            return columns

    return VertexLitDataset()
