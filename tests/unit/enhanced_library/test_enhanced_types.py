# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import

from google.cloud.aiplatform.v1.schema.trainingjob import definition
from google.cloud.aiplatform.v1beta1.schema.trainingjob import (
    definition as definition_v1beta1,
)

ModelType = definition.AutoMlImageClassificationInputs().ModelType
test_training_input = definition.AutoMlImageClassificationInputs(
    multi_label=True,
    model_type=ModelType.CLOUD,
    budget_milli_node_hours=8000,
    disable_early_stopping=False,
)

ModelType_v1beta1 = definition_v1beta1.AutoMlImageClassificationInputs().ModelType
test_training_input_v1beta1 = definition.AutoMlImageClassificationInputs(
    multi_label=True,
    model_type=ModelType_v1beta1.CLOUD,
    budget_milli_node_hours=8000,
    disable_early_stopping=False,
)


# Test the v1 enhanced types.
def test_exposes_to_value_method_v1():
    assert hasattr(test_training_input, "to_value")


def test_exposes_from_value_method_v1():
    assert hasattr(test_training_input, "from_value")


def test_exposes_from_map_method_v1():
    assert hasattr(test_training_input, "from_map")


# Test the v1beta1 enhanced types.
def test_exposes_to_value_method_v1beta1():
    assert hasattr(test_training_input_v1beta1, "to_value")


def test_exposes_from_value_method_v1beta1():
    assert hasattr(test_training_input_v1beta1, "from_value")


def test_exposes_from_map_method_v1beta1():
    assert hasattr(test_training_input_v1beta1, "from_map")
