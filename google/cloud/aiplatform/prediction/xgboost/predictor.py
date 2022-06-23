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

from fastapi import HTTPException

import numpy as np
import xgboost as xgb

from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.prediction.predictor import Predictor

MODEL_FILENAME_BST = "model.bst"
MODEL_FILENAME_JOBLIB = "model.joblib"
MODEL_FILENAME_PKL = "model.pkl"


class XgboostPredictor(Predictor):
    """Default Predictor implementation for Xgboost models."""

    def __init__(self):
        return

    def load(self, artifacts_uri: str):
        """Loads the model artifact.

        Args:
            artifacts_uri (str):
                Required. The value of the environment variable AIP_STORAGE_URI.
        """
        prediction_utils.download_model_artifacts(artifacts_uri)
        if os.path.exists(MODEL_FILENAME_BST):
            booster = xgb.Booster(model_file=MODEL_FILENAME_BST)
        elif os.path.exists(MODEL_FILENAME_JOBLIB):
            try:
                booster = joblib.load(MODEL_FILENAME_JOBLIB)
            except KeyError:
                logging.info(
                    "Loading model using joblib failed. "
                    "Loading model using xgboost.Booster instead.")
                booster = xgb.Booster()
                booster.load_model(MODEL_FILENAME_JOBLIB)
        elif os.path.exists(MODEL_FILENAME_PKL):
            booster = pickle.load(open(MODEL_FILENAME_PKL, "rb"))
        else:
            valid_filenames = [
                MODEL_FILENAME_BST, MODEL_FILENAME_JOBLIB, MODEL_FILENAME_PKL
            ]
            raise ValueError(
                f"One of the following model files must be provided: {valid_filenames}.")
        self._booster = booster
            

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
