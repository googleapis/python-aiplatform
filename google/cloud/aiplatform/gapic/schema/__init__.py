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

from google.cloud.aiplatform.helpers import _decorators
from google.cloud.aiplatform.v1beta1.schema import predict
from google.cloud.aiplatform.v1beta1.schema import trainingjob
from google.cloud.aiplatform.v1beta1.schema.predict.instance_v1beta1 import (
    types as instance,
)
from google.cloud.aiplatform.v1beta1.schema.predict.params_v1beta1 import (
    types as params,
)
from google.cloud.aiplatform.v1beta1.schema.predict.prediction_v1beta1 import (
    types as prediction,
)
from google.cloud.aiplatform.v1beta1.schema.trainingjob.definition_v1beta1 import (
    types as definition,
)

__all__ = (
    "predict",
    "trainingjob",
)

enhanced_types_packages = [
    instance,
    params,
    prediction,
    definition,
]

for pkg in enhanced_types_packages:
    _decorators._add_methods_to_classes_in_package(pkg)
