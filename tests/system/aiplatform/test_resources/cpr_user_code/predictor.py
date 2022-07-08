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

import joblib
import numpy as np
from typing import Any

from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.prediction.predictor import Predictor


class SklearnPredictor(Predictor):
    """Interface for Predictor class that users would be implementing."""

    def __init__(self):
        return

    def load(self, artifacts_uri: str):
        """Loads the model artifact.

        Args:
            artifacts_uri (str):
                Required. The value of the environment variable AIP_STORAGE_URI.
        """
        prediction_utils.download_model_artifacts(artifacts_uri)
        self._model = joblib.load("model.joblib")

    def predict(self, instances: Any) -> Any:
        """Performs prediction.

        Args:
            instances (Any):
                Required. The instances to perform prediction.

        Returns:
            Prediction results.
        """
        instances = instances["instances"]
        inputs = np.asarray(instances)
        outputs = self._model.predict(inputs)
        return {"predictions": outputs.tolist()}
