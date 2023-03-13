# -*- coding: utf-8 -*-

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

import inspect
from typing import Any

from google.cloud.aiplatform.private_preview.vertex_ai._workflow.launcher import (
    training,
    predict
)

REMOTE_FRAMEWORKS = ["sklearn"]
REMOTE_TRAINING_OVERRIDE_LIST = ["fit", "transform", "fit_transform"]
REMOTE_PREDICT_OVERRIDE_LIST = ["predict"]


def remote(cls: Any) -> Any:
    """Add Vertex attributes to a class object."""

    module_name = cls.__module__
    if not any([module_name.startswith(framework) for framework in REMOTE_FRAMEWORKS]):
        raise ValueError(
            f"Class {cls.__name__} not supported. "
            f"Currently support remote execution on {REMOTE_FRAMEWORKS} classes."
        )

    setattr(cls, "TrainingConfig", training.TrainingConfig())
    setattr(cls, "PredictConfig", predict.PredictConfig())


    for attr_name, attr_value in inspect.getmembers(cls):
        if attr_name in REMOTE_TRAINING_OVERRIDE_LIST:
            setattr(cls, attr_name, training.remote_training(attr_value))
    
    for attr_name, attr_value in inspect.getmembers(cls):
        if attr_name in REMOTE_PREDICT_OVERRIDE_LIST:
            setattr(cls, attr_name, predict.remote_predict(attr_value))

    return cls