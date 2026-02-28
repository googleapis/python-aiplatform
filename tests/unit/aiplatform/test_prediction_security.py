# -*- coding: utf-8 -*-

# Copyright 2026 Google LLC
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

import pytest
from unittest import mock
from google.cloud.aiplatform.prediction.xgboost.predictor import (
    XgboostPredictor,
)
from google.cloud.aiplatform.prediction.sklearn.predictor import (
    SklearnPredictor,
)

from google.cloud.aiplatform.utils import prediction_utils
from google.cloud.aiplatform.prediction.xgboost import (
    predictor as xgboost_predictor,
)


class TestPredictorSecurity:
    @pytest.mark.parametrize("predictor_class", [XgboostPredictor, SklearnPredictor])
    def test_load_warns_no_allowed_extensions(self, predictor_class):
        """Verifies UserWarning is issued when allowed_extensions is missing."""
        predictor = predictor_class()
        with mock.patch.object(
            prediction_utils, "download_model_artifacts"
        ), mock.patch("os.path.exists", return_value=True), mock.patch(
            "joblib.load"
        ), mock.patch(
            "pickle.load"
        ), mock.patch.object(
            xgboost_predictor.xgb, "Booster"
        ), mock.patch(
            "builtins.open", mock.mock_open()
        ):
            with pytest.warns(UserWarning, match="No 'allowed_extensions' provided"):
                predictor.load("gs://test-bucket")

    def test_xgboost_load_warns_on_joblib(self):
        """Verifies RuntimeWarning is issued when loading a .joblib file."""
        predictor = XgboostPredictor()
        with mock.patch.object(
            prediction_utils, "download_model_artifacts"
        ), mock.patch(
            "os.path.exists", side_effect=lambda p: p.endswith(".joblib")
        ), mock.patch(
            "joblib.load"
        ), mock.patch.object(
            xgboost_predictor.xgb, "Booster"
        ):
            with pytest.warns(
                RuntimeWarning, match="using joblib pickle, which is unsafe"
            ):
                predictor.load("gs://test-bucket", allowed_extensions=[".joblib"])

    def test_xgboost_load_raises_not_allowed(self):
        """Verifies ValueError is raised if the file exists but is not allowed."""
        predictor = XgboostPredictor()
        with mock.patch.object(
            prediction_utils, "download_model_artifacts"
        ), mock.patch.object(xgboost_predictor.xgb, "Booster"), mock.patch(
            "os.path.exists", side_effect=lambda p: p.endswith(".pkl")
        ):
            with pytest.raises(ValueError, match="must be provided and allowed"):
                predictor.load("gs://test-bucket", allowed_extensions=[".bst"])

    def test_sklearn_load_warns_on_pickle(self):
        """Verifies RuntimeWarning is issued when loading a .pkl file."""
        predictor = SklearnPredictor()
        with mock.patch.object(
            prediction_utils, "download_model_artifacts"
        ), mock.patch(
            "os.path.exists", side_effect=lambda p: p.endswith(".pkl")
        ), mock.patch(
            "builtins.open", mock.mock_open()
        ), mock.patch(
            "pickle.load"
        ):

            with pytest.warns(RuntimeWarning, match="using pickle, which is unsafe"):
                predictor.load("gs://test-bucket", allowed_extensions=[".pkl"])

    def test_sklearn_load_warns_on_joblib(self):
        """Verifies RuntimeWarning is issued when loading a .joblib file in Scikit-learn."""
        predictor = SklearnPredictor()
        with mock.patch.object(
            prediction_utils, "download_model_artifacts"
        ), mock.patch(
            "os.path.exists", side_effect=lambda p: p.endswith(".joblib")
        ), mock.patch(
            "joblib.load"
        ):
            with pytest.warns(
                RuntimeWarning, match=r"using joblib pickle, which is unsafe"
            ):
                predictor.load("gs://test-bucket", allowed_extensions=[".joblib"])
