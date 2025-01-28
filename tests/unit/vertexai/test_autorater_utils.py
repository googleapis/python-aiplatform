# -*- coding: utf-8 -*-

# Copyright 2024 Google LLC
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
"""Unit tests for autorater utils."""

import copy
import datetime
from typing import Any, Dict, List
from unittest import mock
import uuid

from google import auth
from google.auth import credentials as auth_credentials
import vertexai
from google.cloud.aiplatform import compat
from google.cloud.aiplatform import initializer
from google.cloud.aiplatform import utils as aiplatform_utils
from google.cloud.aiplatform_v1beta1.services import gen_ai_tuning_service
from google.cloud.aiplatform_v1beta1.types import job_state
from google.cloud.aiplatform_v1beta1.types import (
    tuning_job as gca_tuning_job,
)
from vertexai.preview import tuning
from vertexai.preview.evaluation import autorater_utils
from vertexai.preview.evaluation.metrics import pairwise_metric
from vertexai.preview.evaluation.metrics import pointwise_metric
import numpy as np
import pandas as pd
import pytest


AutoraterConfig = autorater_utils.AutoraterConfig
PointwiseMetric = pointwise_metric.PointwiseMetric
PairwiseMetric = pairwise_metric.PairwiseMetric

_TEST_PROJECT = "test-project"
_TEST_LOCATION = "us-central1"


_global_tuning_jobs: Dict[str, gca_tuning_job.TuningJob] = {}
_SCORE = "score"
_METRIC = "metric"
_PAIRWISE_CHOICE = "pairwise_choice"
_HUMAN_RATING = "human_rating"
_HUMAN_PAIRWISE_CHOICE = "human_pairwise_choice"
_ACCURACY_BALANCED = "accuracy_balanced"
_F1_SCORE_BALANCED = "f1_score_balanced"
_CONFUSION_MATRIX = "confusion_matrix"
_CONFUSION_MATRIX_LABELS = "confusion_matrix_labels"


@pytest.fixture
def google_auth_mock():
    with mock.patch.object(auth, "default") as google_auth_default_mock:
        google_auth_default_mock.return_value = (
            auth_credentials.AnonymousCredentials(),
            _TEST_PROJECT,
        )
        yield google_auth_default_mock


class MockGenAiTuningServiceClient(gen_ai_tuning_service.GenAiTuningServiceClient):
    """Mock GenAiTuningServiceClient."""

    @property
    def _tuning_jobs(self) -> Dict[str, gca_tuning_job.TuningJob]:
        return _global_tuning_jobs

    def create_tuning_job(
        self,
        *,
        parent: str,
        tuning_job: gca_tuning_job.TuningJob,
        **_,
    ) -> gca_tuning_job.TuningJob:
        tuning_job = copy.deepcopy(tuning_job)
        resource_id = uuid.uuid4().hex
        resource_name = f"{parent}/tuningJobs/{resource_id}"
        tuning_job.name = resource_name
        current_time = datetime.datetime.now(datetime.timezone.utc)
        tuning_job.tuned_model = gca_tuning_job.TunedModel(
            model=f"{parent}/models/123",
            endpoint=f"{parent}/endpoints/456",
        )
        tuning_job.state = job_state.JobState.JOB_STATE_SUCCEEDED
        tuning_job.create_time = current_time
        tuning_job.update_time = current_time
        self._tuning_jobs[resource_name] = tuning_job
        return tuning_job

    def get_tuning_job(self, *, name: str, **_) -> gca_tuning_job.TuningJob:
        tuning_job = self._tuning_jobs[name]
        tuning_job = copy.deepcopy(tuning_job)
        return tuning_job


class MockTuningJobClientWithOverride(aiplatform_utils.ClientWithOverride):
    _is_temporary = False
    _default_version = compat.V1
    _version_map = ((compat.V1, MockGenAiTuningServiceClient),)


@pytest.mark.usefixtures("google_auth_mock")
class TestAutoraterUtils:
    """Unit tests for generative model tuning."""

    def setup_method(self):
        vertexai.init(
            project=_TEST_PROJECT,
            location=_TEST_LOCATION,
        )

    def teardown_method(self):
        initializer.global_pool.shutdown(wait=True)

    @mock.patch.object(
        target=tuning.TuningJob,
        attribute="client_class",
        new=MockTuningJobClientWithOverride,
    )
    def test_tune_autorater(self):
        """Test tune_autorater."""
        autorater_config = autorater_utils.tune_autorater(
            base_model="gemini-1.0-pro-001",
            train_dataset="gs://test-bucket/train_dataset.jsonl",
            validation_dataset="gs://test-bucket/validation_dataset.jsonl",
            epochs=300,
            learning_rate_multiplier=1.0,
            time_out_hours=0,
        )
        assert autorater_config.autorater_model == (
            "projects/test-project/locations/us-central1/endpoints/456"
        )

    def test_evaluate_autorater(self):
        """Test evaluate_autorater."""
        autorater_config = autorater_utils.AutoraterConfig(
            autorater_model="projects/test-project/locations/us-central1/endpoints/456"
        )
        y_true_2_class = [1, 0, 1, 0, 1, 0]
        y_pred_2_class = [1, 0, 0, 1, 1, 0]
        y_true_multi_class = ["1", "2", "1", "1", "2", "3"]
        y_pred_multi_class = [
            "2",
            "2",
            "1",
            "1",
            "2",
            "1",
        ]
        metrics = [
            PairwiseMetric(
                metric="test_pairwise_2_class",
                metric_prompt_template="test prompt1",
            ),
            PointwiseMetric(
                metric="test_pointwise_multi_class",
                metric_prompt_template="test prompt2",
            ),
        ]
        autorater_eval_result = autorater_utils.evaluate_autorater(
            evaluate_autorater_input=pd.DataFrame(
                {
                    f"test_pairwise_2_class/{_PAIRWISE_CHOICE}": y_pred_2_class,
                    f"test_pairwise_2_class/{_HUMAN_PAIRWISE_CHOICE}": y_true_2_class,
                    f"test_pointwise_multi_class/{_SCORE}": y_pred_multi_class,
                    f"test_pointwise_multi_class/{_HUMAN_RATING}": y_true_multi_class,
                }
            ),
            eval_metrics=metrics,
            autorater_config=autorater_config,
            eval_dataset_metadata={
                "eval_dataset_path": "gs://test-bucket/eval_dataset.jsonl",
                "eval_dataset_size": 6,
            },
            unused_params=10,
        )
        expected_eval_results = [
            {
                _METRIC: metrics[0].metric_name,
                _ACCURACY_BALANCED: 2 / 3,
                _F1_SCORE_BALANCED: 2 / 3,
                _CONFUSION_MATRIX: np.array([[2, 1], [1, 2]]),
                _CONFUSION_MATRIX_LABELS: ["0", "1"],
            },
            {
                _METRIC: metrics[1].metric_name,
                _ACCURACY_BALANCED: 5 / 9,
                _F1_SCORE_BALANCED: 3 / 5,
                _CONFUSION_MATRIX: np.array([[2, 1, 0], [0, 2, 0], [1, 0, 0]]),
                _CONFUSION_MATRIX_LABELS: ["1.0", "2.0", "3.0"],
            },
        ]

        assert _compare_autorater_eval_result(
            autorater_eval_result.eval_result, expected_eval_results
        )
        assert autorater_eval_result.eval_dataset_metadata == {
            "eval_dataset_path": "gs://test-bucket/eval_dataset.jsonl",
            "eval_dataset_size": 6,
        }
        assert autorater_eval_result.autorater_config == autorater_config
        assert autorater_eval_result.unused_params == 10

    def test_evaluate_autorater_exceed_pointwise_limit(self):
        """Test evaluate_autorater."""
        autorater_config = autorater_utils.AutoraterConfig(
            autorater_model="projects/test-project/locations/us-central1/endpoints/456"
        )
        y_true_multi_class = [_ for _ in range(12)]
        y_pred_multi_class = [_ for _ in range(12)]
        metrics = [
            PointwiseMetric(
                metric="test_pointwise_multi_class",
                metric_prompt_template="test prompt2",
            ),
        ]
        autorater_eval_result = autorater_utils.evaluate_autorater(
            evaluate_autorater_input=pd.DataFrame(
                {
                    f"test_pointwise_multi_class/{_SCORE}": y_pred_multi_class,
                    f"test_pointwise_multi_class/{_HUMAN_RATING}": y_true_multi_class,
                }
            ),
            eval_metrics=metrics,
            autorater_config=autorater_config,
            eval_dataset_metadata={
                "eval_dataset_path": "gs://test-bucket/eval_dataset.jsonl",
                "eval_dataset_size": 6,
            },
            unused_params=10,
        )
        assert autorater_eval_result.eval_result == [
            {
                _METRIC: metrics[0].metric_name,
                _ACCURACY_BALANCED: 1.0,
                _F1_SCORE_BALANCED: 1.0,
            },
        ]
        assert autorater_eval_result.eval_dataset_metadata == {
            "eval_dataset_path": "gs://test-bucket/eval_dataset.jsonl",
            "eval_dataset_size": 6,
        }
        assert autorater_eval_result.autorater_config == autorater_config
        assert autorater_eval_result.unused_params == 10

    @mock.patch.object(
        target=tuning.TuningJob,
        attribute="client_class",
        new=MockTuningJobClientWithOverride,
    )
    def test_evaluate_autorater_with_skipped_results(self):
        """Test evaluate_autorater."""
        autorater_config = autorater_utils.AutoraterConfig(
            autorater_model="projects/test-project/locations/us-central1/endpoints/456"
        )
        y_true_2_class = ["1", "0", "1", "0", "1", "0", "Error", "1"]
        y_pred_2_class = ["1", "0", "0", "1", "1", "0", "0", "ERROR"]
        y_true_multi_class = ["1", "2", "1", 1, "2", "3", "1", "NaN"]
        y_pred_multi_class = ["2", "2.0", "1", 1.0, "2", "1", "NaN", "1"]
        metrics = [
            PairwiseMetric(
                metric="test_pairwise_2_class",
                metric_prompt_template="test prompt1",
            ),
            PointwiseMetric(
                metric="test_pointwise_multi_class",
                metric_prompt_template="test prompt2",
            ),
        ]
        autorater_eval_result = autorater_utils.evaluate_autorater(
            evaluate_autorater_input=pd.DataFrame(
                {
                    f"test_pairwise_2_class/{_PAIRWISE_CHOICE}": y_pred_2_class,
                    f"test_pairwise_2_class/{_HUMAN_PAIRWISE_CHOICE}": y_true_2_class,
                    f"test_pointwise_multi_class/{_SCORE}": y_pred_multi_class,
                    f"test_pointwise_multi_class/{_HUMAN_RATING}": y_true_multi_class,
                }
            ),
            eval_metrics=metrics,
            autorater_config=autorater_config,
            eval_dataset_metadata={
                "eval_dataset_path": "gs://test-bucket/eval_dataset.jsonl",
                "eval_dataset_size": 6,
            },
            unused_params=10,
        )
        expected_eval_results = [
            {
                _METRIC: metrics[0].metric_name,
                _ACCURACY_BALANCED: 2 / 3,
                _F1_SCORE_BALANCED: 2 / 3,
                _CONFUSION_MATRIX: np.array([[2, 1], [1, 2]]),
                _CONFUSION_MATRIX_LABELS: ["0", "1"],
            },
            {
                _METRIC: metrics[1].metric_name,
                _ACCURACY_BALANCED: 5 / 9,
                _F1_SCORE_BALANCED: 3 / 5,
                _CONFUSION_MATRIX: np.array([[2, 1, 0], [0, 2, 0], [1, 0, 0]]),
                _CONFUSION_MATRIX_LABELS: ["1.0", "2.0", "3.0"],
            },
        ]
        assert _compare_autorater_eval_result(
            autorater_eval_result.eval_result, expected_eval_results
        )
        assert autorater_eval_result.eval_dataset_metadata == {
            "eval_dataset_path": "gs://test-bucket/eval_dataset.jsonl",
            "eval_dataset_size": 6,
        }
        assert autorater_eval_result.autorater_config == autorater_config
        assert autorater_eval_result.unused_params == 10


def _compare_autorater_eval_result(
    actual_eval_results: List[Dict[str, Any]],
    expected_eval_results: List[Dict[str, Any]],
) -> bool:
    """Compare autorater eval result."""
    for actual, expected in zip(actual_eval_results, expected_eval_results):
        if actual[_METRIC] != expected[_METRIC]:
            return False
        if not _almost_equal(actual[_ACCURACY_BALANCED], expected[_ACCURACY_BALANCED]):
            return False
        if not _almost_equal(actual[_F1_SCORE_BALANCED], expected[_F1_SCORE_BALANCED]):
            return False
        if not (actual[_CONFUSION_MATRIX] == expected[_CONFUSION_MATRIX]).all():
            return False
        if actual[_CONFUSION_MATRIX_LABELS] != expected[_CONFUSION_MATRIX_LABELS]:
            return False
    return True


def _almost_equal(a: Any, b: Any) -> bool:
    """Compare two numbers with a small tolerance."""
    return abs(a - b) <= 1e-6
