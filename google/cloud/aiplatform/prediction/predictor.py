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

from typing import Any


class Predictor:
    """Interface for Predictor class that users would be implementing."""

    def __init__(self):
        raise NotImplementedError("Predictor.__init__ has not been implemented yet.")

    def load(self, gcs_artifacts_uri: str):
        """Loads the model artifact.

        Args:
            gcs_artifacts_uri (str):
                Required. The value of the environment variable AIP_STORAGE_URI.
        """
        raise NotImplementedError("Predictor.load has not been implemented yet.")

    def preprocess(self, prediction_input: Any) -> Any:
        """Preprocesses the prediction input before doing the prediction.

        Args:
            prediction_input (Any):
                Required. The prediction input needs to be preprocessed.

        Returns:
            The preprocessed prediction input.
        """
        return prediction_input

    def predict(self, instances: Any) -> Any:
        """Performs prediction.

        Args:
            instances (Any):
                Required. The instances to perform prediction.

        Returns:
            Prediction results.
        """
        raise NotImplementedError("Predictor.predict has not been implemented yet.")

    def postprocess(self, prediction_results: Any) -> Any:
        """Postprocesses the prediction results.

        Args:
            prediction_results (Any):
                Required. The prediction results.

        Returns:
            The postprocessed prediction results.
        """
        return prediction_results
