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
"""Tests that `vertexai.types` metrics resolve in the `vertexai` evals client.

`vertexai.types` resolves to the agentplatform classes, so these objects reach
`vertexai._genai._evals_common` as agentplatform instances.
"""

from unittest import mock

import vertexai
from vertexai._genai import _evals_common
from vertexai._genai import _evals_metric_loaders
from vertexai._genai import types as legacy_types
from google.genai import types as genai_types
import pytest


@pytest.fixture(autouse=True)
def gcs_utils():
    with mock.patch.object(_evals_metric_loaders._gcs_utils, "GcsUtils") as gcs:
        yield gcs


def test_rubric_metric_resolves_to_predefined_spec_in_evaluation_run(gcs_utils):
    resolved = _evals_common._resolve_evaluation_run_metrics(
        [vertexai.types.RubricMetric.TOOL_USE_QUALITY(version="v2")], mock.Mock()
    )

    assert len(resolved) == 1
    assert isinstance(resolved[0], legacy_types.EvaluationRunMetric)
    assert resolved[0].metric == "tool_use_quality_v2"
    assert (
        resolved[0].metric_config.predefined_metric_spec.metric_spec_name
        == "tool_use_quality_v2"
    )
    gcs_utils.assert_not_called()


def test_rubric_metric_keeps_requested_version(gcs_utils):
    resolved = _evals_common._resolve_evaluation_run_metrics(
        [vertexai.types.RubricMetric.TOOL_USE_QUALITY(version="v1")], mock.Mock()
    )

    assert resolved[0].metric == "tool_use_quality_v1"
    gcs_utils.assert_not_called()


def test_rubric_metric_resolves_in_evaluate(gcs_utils):
    resolved = _evals_common._resolve_metrics(
        [vertexai.types.RubricMetric.TOOL_USE_QUALITY(version="v2")], mock.Mock()
    )

    assert len(resolved) == 1
    assert isinstance(resolved[0], legacy_types.Metric)
    assert resolved[0].name == "tool_use_quality_v2"
    gcs_utils.assert_not_called()


def test_llm_metric_resolves_in_evaluation_run():
    resolved = _evals_common._resolve_evaluation_run_metrics(
        [vertexai.types.LLMMetric(name="my_metric", prompt_template="Rate {response}")],
        mock.Mock(),
    )

    assert resolved[0].metric == "my_metric"
    assert resolved[0].metric_config is not None


def test_llm_metric_converts_to_legacy_class_in_evaluate():
    metric = vertexai.types.LLMMetric(
        name="my_metric", prompt_template="Rate {response}"
    )

    resolved = _evals_common._resolve_metrics([metric], mock.Mock())

    assert type(resolved[0]) is legacy_types.LLMMetric
    assert resolved[0].name == "my_metric"
    assert resolved[0].prompt_template == "Rate {response}"


def test_evaluation_run_metric_passes_through():
    metric = vertexai.types.EvaluationRunMetric(
        metric="my_metric",
        metric_config=vertexai.types.UnifiedMetric(
            predefined_metric_spec=genai_types.PredefinedMetricSpec(
                metric_spec_name="my_metric"
            )
        ),
    )

    resolved = _evals_common._resolve_evaluation_run_metrics([metric], mock.Mock())

    assert type(resolved[0]) is legacy_types.EvaluationRunMetric
    assert resolved[0].metric == "my_metric"


@pytest.mark.parametrize(
    "resolve",
    [
        _evals_common._resolve_evaluation_run_metrics,
        _evals_common._resolve_metrics,
    ],
)
def test_unsupported_metric_type_raises_type_error(resolve, gcs_utils):
    with pytest.raises(TypeError, match="Unsupported metric type"):
        resolve([object()], mock.Mock())
    gcs_utils.assert_not_called()
