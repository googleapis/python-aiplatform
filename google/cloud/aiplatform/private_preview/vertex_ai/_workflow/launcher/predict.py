# Copyright 2023 Google LLC
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

import dataclasses
import functools
import inspect
import os
import tempfile
from typing import Any, Callable, Dict, Optional, Union

from google.cloud import aiplatform
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.private_preview import vertex_ai

# Move it once the sdk_private_releases bucket is created
VERTEX_AI_DEPENDENCY_PATH = "google-cloud-aiplatform @ git+https://github.com/nayaknishant/python-aiplatform.git@nn-vertex-predict#egg=google-cloud-aiplatform"


@dataclasses.dataclass
class PredictConfig:
    """A class that holds the configuration for prediction in Vertex SDK 2.0."""


def remote_predict(method: Callable[..., Any]):
    """Wrapper function that makes a local predict method executable with Vertex AI Prediction."""

    @functools.wraps(method)
    def p(*args, **kwargs):
        # Local prediction
        if not vertex_ai.global_config.remote:
            return method(*args, **kwargs)

        # TODO: Add remote prediction method
    return p