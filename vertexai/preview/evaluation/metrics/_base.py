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

from typing import Any, Callable, Dict, Literal, Optional, Union
from vertexai import generative_models


class PairwiseMetric:
    """The Side-by-side(SxS) Pairwise Metric."""

    def __init__(
        self,
        *,
        metric: Literal["summarization_quality", "question_answering_quality"],
        baseline_model: Union[
            generative_models.GenerativeModel, Callable[[str], str]
        ] = None,
        use_reference: bool = False,
        version: Optional[int] = None,
    ):
        """Initializes the Side-by-side(SxS) Pairwise evaluation metric.

        Args:
          metric: The Side-by-side(SxS) pairwise evaluation metric name.
          baseline_model: The baseline model for the Side-by-side(SxS) comparison.
          use_reference: Whether to use reference to compute the metric. If specified,
            the reference column is required in the dataset.
          version: The metric version to use for evaluation.
        """
        self._metric = metric
        self._baseline_model = baseline_model
        self._use_reference = use_reference
        self._version = version

    def __str__(self):
        return self.pairwise_metric_name

    @property
    def pairwise_metric_name(self) -> str:
        return f"pairwise_{self._metric}"

    @property
    def baseline_model(
        self,
    ) -> Union[generative_models.GenerativeModel, Callable[[str], str]]:
        return self._baseline_model

    @property
    def use_reference(self) -> bool:
        return self._use_reference

    @property
    def version(self) -> int:
        return self._version


class CustomMetric:
    """The custom evaluation metric.

    Attributes:
      name: The name of the metric.
      metric_function: The evaluation function. Must use the dataset row/instance
       as the metric_function input. Returns per-instance metric result as a
       dictionary. The metric score must mapped to the CustomMetric.name as key.
    """

    def __init__(
        self,
        name: str,
        metric_function: Callable[
            [Dict[str, Any]],
            Dict[str, Any],
        ],
    ):
        """Initializes the evaluation metric."""
        self.name = name
        self.metric_function = metric_function

    def __str__(self):
        return self.name


def make_metric(
    name: str, metric_function: Callable[[Dict[str, Any]], Dict[str, Any]]
) -> CustomMetric:
    """Makes a custom metric.

    Args:
      name: The name of the metric
      metric_function: The evaluation function. Must use the dataset row/instance
        as the metric_function input. Returns per-instance metric result as a
        dictionary. The metric score must mapped to the CustomMetric.name as key.

    Returns:
      A CustomMetric instance, can be passed to evaluate() function.
    """
    return CustomMetric(name, metric_function)
