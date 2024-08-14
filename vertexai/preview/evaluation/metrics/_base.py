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

from abc import ABC
from typing import Any, Callable, Dict, Literal, Optional, Union
import warnings

from vertexai import generative_models
from vertexai.preview.evaluation import constants


_DEPRECATION_WARNING_MESSAGE = (
    "After google-cloud-aiplatform>1.60.0, using metric name `summarization_quality`"
    "and `question_answering_quality` will result in an error. "
    "Please use `pairwise_summarization_quality` and "
    "`pairwise_question_answering_quality` instead."
)


class _Metric(ABC):
    """The abstract class for evaluation metric."""

    def __init__(self, metric: str):
        self._metric = metric

    def __str__(self):
        return self.metric_name

    @property
    def metric_name(self) -> str:
        return self._metric


class PairwiseMetric(_Metric):
    """The Side-by-side(SxS) Pairwise Metric.

    A model-based evaluation metric that compares two generative models
    side-by-side, and allows users to A/B test their generative models to
    determine which model is performing better on the given evaluation task.

    For more details on when to use pairwise metrics, see
    [Evaluation methods and
    metrics](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval#pointwise_versus_pairwise).

    Result Details:

        * In `EvalResult.summary_metrics`, win rates for both the baseline and
        candidate model are computed, showing the rate of each model performs
        better on the given task. The win rate is computed as the number of times
        the candidate model performs better than the baseline model divided by the
        total number of examples. The win rate is a number between 0 and 1.

        * In `EvalResult.metrics_table`, a pairwise metric produces three
        evaluation results for each row in the dataset:
            * `pairwise_choice`: the `pairwise_choice` in the evaluation result is
              an enumeration that indicates whether the candidate or baseline
              model perform better.
            * `explanation`: The model AutoRater's rationale behind each verdict
              using chain-of-thought reasoning. These explanations help users
              scrutinize the AutoRater's judgment and build appropriate trust in
              its decisions.
            * `confidence`: A score between 0 and 1, which signifies how confident
              the AutoRater was with its verdict. A score closer to 1 means higher
              confidence.

        See [documentation
        page](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval#understand-results)
        for more details on understanding the metric results.

    Usages:

        ```
        from vertexai.generative_models import GenerativeModel
        from vertexai.preview.evaluation import EvalTask, PairwiseMetric

        baseline_model = GenerativeModel("gemini-1.0-pro")
        candidate_model = GenerativeModel("gemini-1.5-pro")

        pairwise_summarization_quality = PairwiseMetric(
          metric = "pairwise_summarization_quality",
          baseline_model=baseline_model,
        )

        eval_task =  EvalTask(
          dataset = pd.DataFrame({
              "instruction": [...],
              "context": [...],
          }),
          metrics=[pairwise_summarization_quality],
        )

        pairwise_results = eval_task.evaluate(
            prompt_template="instruction: {instruction}. context: {context}",
            model=candidate_model,
        )
        ```
    """

    def __init__(
        self,
        *,
        metric: Literal[
            constants.Metric.PAIRWISE_SUMMARIZATION_QUALITY,
            constants.Metric.PAIRWISE_QUESTION_ANSWERING_QUALITY,
        ],
        baseline_model: Optional[
            Union[generative_models.GenerativeModel, Callable[[str], str]]
        ] = None,
        use_reference: bool = False,
        version: Optional[int] = None,
    ):
        """Initializes the Side-by-side(SxS) Pairwise evaluation metric.

        Args:
          metric: The Side-by-side(SxS) pairwise evaluation metric name.
          baseline_model: The baseline model for the Side-by-side(SxS) comparison.
            If not specified, `baseline_model_response` column is required in the dataset.
          use_reference: Whether to use reference to compute the metric. If
            specified, the reference column is required in the dataset.
          version: The metric version to use for evaluation.
        """
        # TODO(b/311221071): Remove the legacy metric names for GA.
        if metric in ("summarization_quality", "question_answering_quality"):
            metric = f"pairwise_{metric}"
            warnings.warn(
                _DEPRECATION_WARNING_MESSAGE, DeprecationWarning, stacklevel=2
            )
        self._metric = metric
        self._baseline_model = baseline_model
        self._use_reference = use_reference
        self._version = version

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


class _ModelBasedMetric(_Metric):
    """The Model-based Metric.

    A model-based evaluation metric that evaluate a generative model's response
    on the given evaluation task. It is a type of pointwise evaluation metric.

    For more details on when to use model-based pointwise metrics, see
    [Evaluation methods and metrics](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval).
    """

    def __init__(
        self,
        *,
        metric: Literal[
            constants.Metric.COHERENCE,
            constants.Metric.FLUENCY,
            constants.Metric.SAFETY,
            constants.Metric.GROUNDEDNESS,
            constants.Metric.FULFILLMENT,
            constants.Metric.SUMMARIZATION_QUALITY,
            constants.Metric.SUMMARIZATION_HELPFULNESS,
            constants.Metric.SUMMARIZATION_VERBOSITY,
            constants.Metric.QUESTION_ANSWERING_QUALITY,
            constants.Metric.QUESTION_ANSWERING_RELEVANCE,
            constants.Metric.QUESTION_ANSWERING_HELPFULNESS,
            constants.Metric.QUESTION_ANSWERING_CORRECTNESS,
        ],
        use_reference: bool = False,
        version: Optional[int] = None,
    ):
        """Initializes the model-based evaluation metric.

        Args:
          metric: The model-based evaluation metric name.
          use_reference: Whether to use reference to compute the metric. If
            specified, the reference column is required in the dataset.
          version: The metric version to use for evaluation.
        """
        self._metric = metric
        self._use_reference = use_reference
        self._version = version

    @property
    def use_reference(self) -> bool:
        return self._use_reference

    @property
    def version(self) -> int:
        return self._version


class _AutomaticMetric(_Metric):
    """The automatic metric that computes deterministic score based on reference.

    An lexicon-based evaluation metric that evaluate a generative model's
    response on the given evaluation task with reference ground truth answers.
    It is a type of pointwise evaluation metric.

    For more details on when to use automatic pointwise metrics, see
    [Evaluation methods and
    metrics](https://cloud.google.com/vertex-ai/generative-ai/docs/models/determine-eval).
    """

    def __init__(
        self,
        metric: Literal[constants.Metric.ROUGE],
        rouge_type: Optional[str] = None,
        use_stemmer: bool = False,
        split_summaries: bool = False,
    ):
        """Initializes the automatic evaluation metric.

        Args:
          metric: The automatic evaluation metric name.
          rouge_type: Supported rouge types are rougen[1-9], rougeL, and rougeLsum.
          use_stemmer: Whether to use stemmer to compute rouge score.
          split_summaries: Whether to split summaries while using 'rougeLsum' to
            compute rouge score.
        """
        self._metric = metric

        if metric == constants.Metric.ROUGE:
            self._rouge_type = rouge_type
            self._use_stemmer = use_stemmer
            self._split_summaries = split_summaries

    @property
    def rouge_type(self) -> str:
        return self._rouge_type

    @property
    def use_stemmer(self) -> bool:
        return self._use_stemmer

    @property
    def split_summaries(self) -> bool:
        return self._split_summaries


class CustomMetric(_Metric):
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
        super().__init__(name)
        self.name = name
        self.metric_function = metric_function


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
