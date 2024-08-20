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
# pylint: disable=protected-access, g-multiple-import
"""System tests for Gen AI evaluation."""

from google import auth
from google.cloud import aiplatform
from tests.system.aiplatform import e2e_base
from vertexai.generative_models import GenerativeModel
from vertexai.preview.evaluation import EvalTask
from vertexai.preview.evaluation import (
    MetricPromptTemplateExamples,
)
import pandas as pd
import pytest


_METRICS = [
    "rouge_l_sum",
    MetricPromptTemplateExamples.Pointwise.SAFETY,
]
_GEMINI_MODEL_NAME = "gemini-1.0-pro"
_EXPERIMENT_NAME = "test_experiment"
_EXPERIMENT__RUN_NAME = "test_experiment_run"


@pytest.mark.usefixtures(
    "tear_down_resources",
)
class TestEvaluation(e2e_base.TestEndToEnd):
    """System tests for Gen AI evaluation."""

    def setup_method(self):
        super().setup_method()
        credentials, _ = auth.default(
            scopes=["https://www.googleapis.com/auth/cloud-platform"]
        )
        aiplatform.init(
            project=e2e_base._PROJECT,
            location=e2e_base._LOCATION,
            credentials=credentials,
        )

    def test_run_eval_task(self):
        test_eval_task = EvalTask(
            dataset=pd.DataFrame(
                {
                    "prompt": ["Why is sky blue?"],
                    "reference": [
                        "The sky appears blue due to a phenomenon called "
                        "Rayleigh scattering."
                    ],
                }
            ),
            metrics=_METRICS,
            experiment=_EXPERIMENT_NAME,
        )

        eval_result = test_eval_task.evaluate(
            model=GenerativeModel(_GEMINI_MODEL_NAME),
            experiment_run_name=_EXPERIMENT__RUN_NAME,
        )

        assert eval_result.summary_metrics["row_count"] == 1
        assert set(eval_result.summary_metrics.keys()) == set(
            [
                "row_count",
                "rouge_l_sum/mean",
                "rouge_l_sum/std",
                "safety/mean",
                "safety/std",
            ]
        )
        assert set(eval_result.metrics_table.columns.values) == set(
            [
                "prompt",
                "reference",
                "response",
                "rouge_l_sum/score",
                "safety/score",
                "safety/explanation",
            ]
        )
