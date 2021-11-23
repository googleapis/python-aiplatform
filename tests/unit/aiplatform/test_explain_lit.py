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

import pytest
import collections
from unittest import TestCase

import pandas as pd
from lit_nlp.api import dataset as lit_dataset
from lit_nlp.api import types as lit_types

from google.cloud.aiplatform.explain.lit import create_lit_dataset


class TestLit:
    def test_create_lit_dataset_from_pandas_returns_dataset(self):
        pd_dataset = pd.DataFrame.from_dict(
            {"feature_1": [1, 2], "feature_2": ["a", "b"]}
        )
        lit_columns = collections.OrderedDict(
            [("feature_1", lit_types.Scalar()), ("feature_2", lit_types.String())]
        )
        created_dataset = create_lit_dataset(pd_dataset, lit_columns)
        expected_spec = {
            "feature_1": lit_types.Scalar(),
            "feature_2": lit_types.String(),
        }
        expected_examples = [
            {"feature_1": 1, "feature_2": "a"},
            {"feature_1": 2, "feature_2": "b"},
        ]

        assert TestCase().assertDictEqual(expected_spec, create_lit_dataset.spec())
        assert TestCase().assertDictEqual(
            expected_examples, create_lit_dataset._examples
        )
