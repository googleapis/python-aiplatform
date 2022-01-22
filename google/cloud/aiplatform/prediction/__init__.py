# -*- coding: utf-8 -*-

# Copyright 2022 Google LLC
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

from google.cloud.aiplatform.prediction.handler import (
    DefaultHandler,
    Handler,
)
from google.cloud.aiplatform.prediction.model_server import ModelServer
from google.cloud.aiplatform.prediction.predictor import Predictor
from google.cloud.aiplatform.prediction.serializer import (
    DefaultSerializer,
    Serializer,
)

__all__ = (
    "DefaultHandler",
    "DefaultSerializer",
    "Handler",
    "ModelServer",
    "Predictor",
    "Serializer",
)
