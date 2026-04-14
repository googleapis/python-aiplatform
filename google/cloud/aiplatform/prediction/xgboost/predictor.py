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
import logging
import os
import pickle
import warnings
import msgpack

import numpy as np
import xgboost as xgb

from google.cloud.aiplatform.constants import prediction
from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.utils import security_utils
from google.cloud.aiplatform.prediction.predictor import Predictor


class XgboostPredictor(Predictor):
    """Default Predictor implementation for Xgboost models."""

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
                "No 'allowed_extensions' provided. Models are now required to be in "
                "signed msgpack or native .bst format for security.",
                UserWarning,
            )

        # 1. First, check for the new secure format (Signed Msgpack)
        if os.path.exists(prediction.MODEL_FILENAME_MSGPACK):
            with open(prediction.MODEL_FILENAME_MSGPACK, "rb") as f:
                signed_data = f.read()
                # Verify HMAC integrity before unpacking
                verified_data = security_utils.verify_blob(signed_data)
                # Unpack the booster state
                # Note: This requires a compatible msgpack-to-XGBoost strategy.
                booster = msgpack.unpackb(verified_data, raw=False)
            self._booster = booster
            return

        # 2. Check for native .bst (Safer but requires validation)
        if os.path.exists(prediction.MODEL_FILENAME_BST):
            booster = xgb.Booster(model_file=prediction.MODEL_FILENAME_BST)
            self._booster = booster
            return

        # 3. Block insecure formats
        prediction_utils.download_model_artifacts(artifacts_uri)

        if os.path.exists(prediction.MODEL_FILENAME_JOBLIB) or os.path.exists(prediction.MODEL_FILENAME_PKL):
            raise RuntimeError(
                "Security Error: Insecure model formats (.pkl, .joblib) are no longer "
                "supported by this version of the SDK. Please migrate your models to "
                "signed msgpack or native .bst using the migration utility."
            )

        valid_filenames = [
            prediction.MODEL_FILENAME_MSGPACK,
            prediction.MODEL_FILENAME_BST,
        ]
        raise ValueError(
            f"One of the following model files must be provided and allowed: {valid_filenames}."
        )

    def preprocess(self, prediction_input: dict) -> xgb.DMatrix:
        """Converts the request body to a Data Matrix before prediction.
        Args:
            prediction_input (dict):
                Required. The prediction input that needs to be preprocessed.
        Returns:
            The preprocessed prediction input.
        """
        instances = prediction_input["instances"]
        return xgb.DMatrix(instances)

    def predict(self, instances: xgb.DMatrix) -> np.ndarray:
        """Performs prediction.

        Args:
            instances (xgb.DMatrix):
                Required. The instance(s) used for performing prediction.

        Returns:
            Prediction results.
        """
        return self._booster.predict(instances)

    def postprocess(self, prediction_results: np.ndarray) -> dict:
        """Converts numpy array to a dict.
        Args:
            prediction_results (np.ndarray):
                Required. The prediction results.
        Returns:
            The postprocessed prediction results.
        """
        return {"predictions": prediction_results.tolist()}
