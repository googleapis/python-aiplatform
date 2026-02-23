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
import os
import pickle
import warnings

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.prediction.predictor import Predictor


class SklearnPredictor(Predictor):
    """Default Predictor implementation for Sklearn models."""

    def __init__(self):
        return

    def load(self, artifacts_uri: str, **kwargs) -> None:
        """Loads the model artifact.

        Args:
            artifacts_uri (str):
                Required. The value of the environment variable AIP_STORAGE_URI.
            **kwargs:
                Optional. Additional keyword arguments for security or
                configuration. Supported arguments:
                    allowed_extensions (list[str]):
                        The allowed file extensions for model artifacts.
                        If not provided, a UserWarning is issued.

        Raises:
            ValueError: If there's no required model files provided in the artifacts
                uri.
        """

        allowed_extensions = kwargs.get("allowed_extensions", None)

        if allowed_extensions is None:
            warnings.warn(
                "No 'allowed_extensions' provided. Loading model artifacts from "
                "untrusted sources may lead to remote code execution.",
                UserWarning,
            )

        prediction_utils.download_model_artifacts(artifacts_uri)
        if os.path.exists(
            prediction.MODEL_FILENAME_JOBLIB
        ) and prediction_utils.is_allowed(
            filename=prediction.MODEL_FILENAME_JOBLIB,
            allowed_extensions=allowed_extensions,
        ):
            warnings.warn(
                f"Loading {prediction.MODEL_FILENAME_JOBLIB} using joblib pickle, which is unsafe. "
                "Only load files from trusted sources.",
                RuntimeWarning,
            )
            self._model = joblib.load(prediction.MODEL_FILENAME_JOBLIB)
        elif os.path.exists(
            prediction.MODEL_FILENAME_PKL
        ) and prediction_utils.is_allowed(
            filename=prediction.MODEL_FILENAME_PKL,
            allowed_extensions=allowed_extensions,
        ):
            warnings.warn(
                f"Loading {prediction.MODEL_FILENAME_PKL} using pickle, which is unsafe. "
                "Only load files from trusted sources.",
                RuntimeWarning,
            )
            self._model = pickle.load(open(prediction.MODEL_FILENAME_PKL, "rb"))
        else:
            valid_filenames = [
                prediction.MODEL_FILENAME_JOBLIB,
                prediction.MODEL_FILENAME_PKL,
            ]
            raise ValueError(
                f"One of the following model files must be provided and allowed: {valid_filenames}."
            )

    def preprocess(self, prediction_input: dict) -> np.ndarray:
        """Converts the request body to a numpy array before prediction.
        Args:
            prediction_input (dict):
                Required. The prediction input that needs to be preprocessed.
        Returns:
            The preprocessed prediction input.
        """
        instances = prediction_input["instances"]
        return np.asarray(instances)

    def predict(self, instances: np.ndarray) -> np.ndarray:
        """Performs prediction.

        Args:
            instances (np.ndarray):
                Required. The instance(s) used for performing prediction.

        Returns:
            Prediction results.
        """
        return self._model.predict(instances)

    def postprocess(self, prediction_results: np.ndarray) -> dict:
        """Converts numpy array to a dict.
        Args:
            prediction_results (np.ndarray):
                Required. The prediction results.
        Returns:
            The postprocessed prediction results.
        """
        return {"predictions": prediction_results.tolist()}
