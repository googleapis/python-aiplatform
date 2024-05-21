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

import asyncio
import collections
from typing import Any, Dict, List, Optional, Set, TYPE_CHECKING, Tuple, Union, Callable

from google.cloud.aiplatform import base
from google.cloud.aiplatform_v1beta1.types import (
    content as gapic_content_types,
)
from vertexai import generative_models
from vertexai.preview.evaluation import _base as evaluation_base
from vertexai.preview.evaluation import constants
from vertexai.preview.evaluation import (
    prompt_template as prompt_template_base,
)
from vertexai.preview.evaluation import utils
from vertexai.preview.evaluation.metrics import (
    _base as metrics_base,
)
from vertexai.preview.evaluation.metrics import (
    _instance_evaluation,
)


if TYPE_CHECKING:
    import pandas as pd

_LOGGER = base.Logger(__name__)
_METRICS_BUNDLE_TO_METRIC_NAMES = {
    constants.MetricBundle.TEXT_GENERATION_SIMILARITY: (
        constants.Metric.EXACT_MATCH,
        constants.Metric.BLEU,
        constants.Metric.ROUGE_1,
        constants.Metric.ROUGE_2,
        constants.Metric.ROUGE_L,
        constants.Metric.ROUGE_L_SUM,
    ),
    constants.MetricBundle.TEXT_GENERATION_QUALITY: (
        constants.Metric.COHERENCE,
        constants.Metric.FLUENCY,
    ),
    constants.MetricBundle.TOOL_CALL_QUALITY: (
        constants.Metric.TOOL_CALL_VALID,
        constants.Metric.TOOL_NAME_MATCH,
        constants.Metric.TOOL_PARAMETER_KEY_MATCH,
        constants.Metric.TOOL_PARAMETER_KV_MATCH,
    ),
    constants.MetricBundle.TEXT_GENERATION_INSTRUCTION_FOLLOWING: (
        constants.Metric.FULFILLMENT,
    ),
    constants.MetricBundle.TEXT_GENERATION_SAFETY: (constants.Metric.SAFETY,),
    constants.MetricBundle.TEXT_GENERATION_FACTUALITY: (constants.Metric.GROUNDEDNESS,),
    constants.MetricBundle.SUMMARIZATION_POINTWISE_REFERENCE_FREE: (
        constants.Metric.SUMMARIZATION_QUALITY,
        constants.Metric.SUMMARIZATION_HELPFULNESS,
        constants.Metric.SUMMARIZATION_VERBOSITY,
    ),
    constants.MetricBundle.QA_POINTWISE_REFERENCE_FREE: (
        constants.Metric.QUESTION_ANSWERING_QUALITY,
        constants.Metric.QUESTION_ANSWERING_RELEVANCE,
        constants.Metric.QUESTION_ANSWERING_HELPFULNESS,
    ),
    constants.MetricBundle.QA_POINTWISE_REFERENCE_BASED: (
        constants.Metric.QUESTION_ANSWERING_CORRECTNESS,
    ),
}
_SUCCESSFUL_FINISH_REASONS = [
    gapic_content_types.Candidate.FinishReason.STOP,
    gapic_content_types.Candidate.FinishReason.MAX_TOKENS,
    # Many responses have this finish reason
    gapic_content_types.Candidate.FinishReason.FINISH_REASON_UNSPECIFIED,
]


def _replace_metric_bundle_with_metrics(
    metrics: List[Union[str, metrics_base.CustomMetric, metrics_base.PairwiseMetric]],
) -> List[Union[str, metrics_base.CustomMetric, metrics_base.PairwiseMetric]]:
    """Replaces metric bundles with corresponding metrics.

    Args:
      metrics: The original metrics list containing metric bundle names.

    Returns:
      The modified metrics list with metric bundle names replaced.
    """
    modified_list = []

    for item in metrics:
        if item in _METRICS_BUNDLE_TO_METRIC_NAMES.keys():
            modified_list.extend(_METRICS_BUNDLE_TO_METRIC_NAMES[item])
        else:
            modified_list.append(item)

    return modified_list


def _compute_custom_metrics(
    row_dict: Dict[str, Any],
    custom_metrics: List[metrics_base.CustomMetric],
) -> Dict[str, Any]:
    """Computes custom metrics for a row.

    Args:
        row_dict: A dictionary of an instance in the eval dataset.
        custom_metrics: A list of CustomMetrics.

    Returns:
        A dictionary of an instance containing custom metric results.

    Raises:
        KeyError: If the custom metric function does not return a valid output.
    """
    for custom_metric in custom_metrics:
        metric_output = custom_metric.metric_function(row_dict)
        if custom_metric.name in metric_output:
            row_dict[custom_metric.name] = metric_output[custom_metric.name]
        else:
            raise KeyError(
                f"Custom metric score `{custom_metric.name}` not found in the metric"
                f" output {metric_output}. Please make sure the custom metric"
                " function is valid, and the output dictionary uses"
                f" `{custom_metric.name}` as the key for metric value."
            )
        # Include additional metric results like explanation.
        for key, value in metric_output.items():
            if key != custom_metric.name:
                row_dict[f"{custom_metric.name}/{key}"] = value
    return row_dict


def _separate_custom_metrics(
    metrics: List[Union[str, metrics_base.CustomMetric, metrics_base.PairwiseMetric]],
) -> Tuple[
    List[Union[str, metrics_base.PairwiseMetric]], List[metrics_base.CustomMetric]
]:
    """Separates the metrics list into API and custom metrics."""
    custom_metrics = []
    api_metrics = []
    for metric in metrics:
        if isinstance(metric, metrics_base.CustomMetric):
            custom_metrics.append(metric)
        else:
            api_metrics.append(metric)
    return api_metrics, custom_metrics


def _compute_summary_metrics(
    evaluation_run_config: evaluation_base.EvaluationRunConfig,
    metrics_table: "pd.DataFrame",
) -> Dict[str, Any]:
    """Computes summary metrics.

    Args:
        evaluation_run_config: Evaluation Run Configurations.
        metrics_table: A dataframe containing per-instance metrics results.

    Returns:
        A dictionary containing summary metrics results and statistics.
    """
    summary_metrics = {}
    summary_metrics[constants.MetricResult.ROW_COUNT_KEY] = metrics_table.shape[0]
    for metric in evaluation_run_config.metrics:
        try:
            if isinstance(metric, metrics_base.PairwiseMetric):
                summary_metrics[
                    f"{metric.pairwise_metric_name}/candidate_model_win_rate"
                ] = (
                    metrics_table[f"{metric.pairwise_metric_name}/pairwise_choice"]
                    == "CANDIDATE"
                ).mean()
                summary_metrics[
                    f"{metric.pairwise_metric_name}/baseline_model_win_rate"
                ] = (
                    metrics_table[f"{metric.pairwise_metric_name}/pairwise_choice"]
                    == "BASELINE"
                ).mean()
            else:
                # TODO(b/325078638): implement additional aggregate methods.
                summary_metrics[f"{str(metric)}/mean"] = metrics_table.loc[
                    :, str(metric)
                ].mean()
                summary_metrics[f"{str(metric)}/std"] = metrics_table.loc[
                    :, str(metric)
                ].std()
        except (ValueError, KeyError) as e:
            _LOGGER.warning(
                f"Failed to compute metric statistics for {metric}. This metric"
                " output contains error from the Autorater.\n"
                f"{type(e).__name__}: {e}"
            )
            continue
    return summary_metrics


def _generate_response_from_gemini(
    model: generative_models.GenerativeModel, prompt: str
) -> str:
    """Generates a text response from Gemini model from a text prompt.

    Args:
        model: The Gemini model instance.
        prompt: The prompt to send to the model.

    Returns:
        The response from the model.

    Raises:
        RuntimeError if the prompt or the response for the prompt is blocked for
        safety reasons.
    """
    response = model.generate_content(prompt)
    try:
        if not response.candidates:
            raise RuntimeError(
                f"The model response was blocked due to {response._raw_response.prompt_feedback.block_reason.name}.\n"
                f"Blocked reason message: {response._raw_response.prompt_feedback.block_reason_message}.\n"
                "The input prompt may be blocked for safety reasons.",
                f"Prompt: {prompt}.",
            )
        else:
            candidate = response.candidates[0]
            if candidate.finish_reason not in _SUCCESSFUL_FINISH_REASONS:
                raise RuntimeError(
                    "The model response did not completed successfully.\n"
                    f"Finish reason: {candidate.finish_reason}.\n"
                    f"Finish message: {candidate.finish_message}.\n"
                    f"Safety ratings: {candidate.safety_ratings}.\n"
                    "Please adjsut the model safety_settings, or try a different prompt."
                )
            return response.candidates[0].content.parts[0].text
    except Exception:
        raise RuntimeError(
            f"Failed to generate response candidates from Gemini model {model._model_name}.\n"
            f"Response: {response}.\n"
            f"Prompt: {prompt}."
        )


def _generate_response_from_gemini_model(
    model: generative_models.GenerativeModel,
    evaluation_run_config: evaluation_base.EvaluationRunConfig,
    is_baseline_model: bool = False,
) -> None:
    """Generates responses from Gemini model.

    Args:
        model: The Gemini model instance.
        evaluation_run_config: Evaluation Run Configurations.
        is_baseline_model: Whether the model is a baseline model for PairwiseMetric.
    """
    response_column_name = (
        constants.Dataset.BASELINE_MODEL_RESPONSE_COLUMN
        if is_baseline_model
        else constants.Dataset.MODEL_RESPONSE_COLUMN
    )
    _LOGGER.info(
        f"Generating a total of {evaluation_run_config.dataset.shape[0]} "
        f"responses from Gemini model {model._model_name.split('/')[-1]}."
    )
    if (
        constants.Dataset.COMPLETED_PROMPT_COLUMN
        in evaluation_run_config.dataset.columns
    ):
        evaluation_run_config.dataset[
            response_column_name
        ] = evaluation_run_config.dataset[
            constants.Dataset.COMPLETED_PROMPT_COLUMN
        ].apply(
            lambda x: _generate_response_from_gemini(model, x)
        )
    else:
        evaluation_run_config.dataset[
            response_column_name
        ] = evaluation_run_config.dataset[
            evaluation_run_config.column_map[constants.Dataset.CONTENT_COLUMN]
        ].apply(
            lambda x: _generate_response_from_gemini(model, x)
        )
    _LOGGER.info(
        f"All {evaluation_run_config.dataset.shape[0]} responses are successfully"
        f" generated from Gemini model {model._model_name.split('/')[-1]}."
    )


def _generate_response_from_custom_model_fn(
    model_fn: Callable[[str], str],
    evaluation_run_config: evaluation_base.EvaluationRunConfig,
    is_baseline_model: bool = False,
) -> None:
    """Generates responses from a custom model function.

    Args:
        model_fn: The custom model function.
        evaluation_run_config: Evaluation Run Configurations.
        is_baseline_model: Whether the model is a baseline model for
          PairwiseMetric.
    """
    response_column_name = (
        constants.Dataset.BASELINE_MODEL_RESPONSE_COLUMN
        if is_baseline_model
        else constants.Dataset.MODEL_RESPONSE_COLUMN
    )
    _LOGGER.info(
        f"Generating a total of {evaluation_run_config.dataset.shape[0]} "
        "responses from the custom model function."
    )
    try:
        if (
            constants.Dataset.COMPLETED_PROMPT_COLUMN
            in evaluation_run_config.dataset.columns
        ):
            evaluation_run_config.dataset[
                response_column_name
            ] = evaluation_run_config.dataset[
                constants.Dataset.COMPLETED_PROMPT_COLUMN
            ].apply(
                model_fn
            )
        else:
            evaluation_run_config.dataset[
                response_column_name
            ] = evaluation_run_config.dataset[
                evaluation_run_config.column_map[constants.Dataset.CONTENT_COLUMN]
            ].apply(
                model_fn
            )
    except (ValueError, IndexError) as e:
        _LOGGER.warning(f"Failed to generate response from model function: {e}")

    _LOGGER.info(
        f"All {evaluation_run_config.dataset.shape[0]} responses are successfully"
        " generated from the custom model function."
    )


def _check_placeholder_columns_exist(
    dataset: "pd.DataFrame", placeholder_names_set: Set[str]
) -> None:
    """Checks if all placeholder names exist in the dataset columns.

    Args:
        dataset: The dataset to evaluate.
        placeholder_names_set: A set of placeholder names.

    Raises:
        ValueError: If any placeholder names do not exist in the dataset columns
        or the prompt template is invalid.
    """
    actual_column_names_set = set(dataset.columns)
    if not placeholder_names_set.issubset(actual_column_names_set):
        missing_columns = placeholder_names_set - actual_column_names_set
        raise ValueError(
            "Failed to complete prompt template: The following column(s) are"
            f" missing: {', '.join(missing_columns)}"
        )


def _complete_prompt_for_dataset(
    evaluation_run_config: evaluation_base.EvaluationRunConfig,
    prompt_template: Union[prompt_template_base.PromptTemplate, str],
) -> None:
    """Adds a column in dataset for completed prompts from placeholder columns.

    Args:
        evaluation_run_config: Evaluation Run Configurations.
        prompt_template:  A `PromptTemplate` object or a prompt template string
          with placeholders that can be assembled from the evaluation dataset. The
          placeholders can be represented in curly braces `{placeholder}`, and
          must be included in the dataset columns if specified. The placeholder
          names cannot contain spaces.

    Returns:
        The completed prompt template string to send to the model.

    Raises:
        ValueError: If any placeholder names do not exist in the dataset columns
        or the prompt template is invalid.
    """
    if not prompt_template:
        raise ValueError("Prompt template cannot be an empty string.")

    _LOGGER.info(
        'Completing prompts from the prompt_template. The "completed_prompt" '
        "column in the EvalResult.metrics_table has the completed prompts "
        "used for model content generation."
    )
    if isinstance(prompt_template, str):
        prompt_template = prompt_template_base.PromptTemplate(prompt_template)
    _check_placeholder_columns_exist(
        evaluation_run_config.dataset, prompt_template.placeholders
    )

    try:
        evaluation_run_config.dataset[
            constants.Dataset.COMPLETED_PROMPT_COLUMN
        ] = evaluation_run_config.dataset.apply(
            lambda row: str(
                prompt_template.assemble(
                    **row[list(prompt_template.placeholders)].astype(str).to_dict(),
                )
            ),
            axis=1,
        )
    except Exception as e:
        raise ValueError(f"Failed to complete prompt: {e}") from e


def _parse_metric_results_to_dataframe(
    instance_df: "pd.DataFrame", results: Dict[str, Any]
) -> Dict[str, Any]:
    """Parses metric results to a pandas dataframe.

    Args:
        instance_df: A dataframe containing per-instance metrics results.
        results: A dictionary containing metric results.

    Returns:
        A dataframe containing per-instance metrics results. Each metric result
        can contain metric score, explanation, and confidence.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            'Pandas is not installed. Please install the SDK using "pip install'
            ' google-cloud-aiplatform[rapid_evaluation]"'
        )
    metrics_table = pd.DataFrame(dict(zip(instance_df.columns, instance_df.values.T)))

    for metric_name, metric_results in results.items():
        if (
            metric_name
            in constants.Metric.MODEL_BASED_METRIC_LIST
            + constants.Metric.PAIRWISE_METRIC_LIST
        ):
            explanations = [
                result.get(constants.MetricResult.EXPLANATION_KEY)
                for result in metric_results
            ]
            confidences = [
                result.get(constants.MetricResult.CONFIDENCE_KEY)
                for result in metric_results
            ]
            metrics_table[
                f"{metric_name}/{constants.MetricResult.EXPLANATION_KEY}"
            ] = explanations
            metrics_table[
                f"{metric_name}/{constants.MetricResult.CONFIDENCE_KEY}"
            ] = confidences
        if metric_name in constants.Metric.PAIRWISE_METRIC_LIST:
            pairwise_choices = [
                result.get(constants.MetricResult.PAIRWISE_CHOICE_KEY)
                for result in metric_results
            ]
            metrics_table[
                f"{metric_name}/{constants.MetricResult.PAIRWISE_CHOICE_KEY}"
            ] = pairwise_choices
        if (
            metric_name
            in constants.Metric.AUTOMATIC_METRIC_LIST
            + constants.Metric.MODEL_BASED_METRIC_LIST
        ):
            scores = [
                result.get(constants.MetricResult.SCORE_KEY)
                for result in metric_results
            ]
            metrics_table[metric_name] = scores

    return metrics_table


async def _compute_metrics(
    evaluation_run_config: evaluation_base.EvaluationRunConfig,
) -> Tuple[Dict[str, Any], "pd.DataFrame"]:
    """Computes the metrics for the dataset.

    Args:
      evaluation_run_config: Evaluation Run Configurations.

    Returns:
      The evaluation results for the input metrics.

    Raises:
      RuntimeError: The number of responses does not match the number of metrics.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            'Pandas is not installed. Please install the SDK using "pip install'
            ' google-cloud-aiplatform[rapid_evaluation]"'
        )

    api_metrics, custom_metrics = _separate_custom_metrics(
        evaluation_run_config.metrics
    )
    instance_list = []
    tasks_by_metric = collections.defaultdict(list)
    for _, row in evaluation_run_config.dataset.iterrows():
        row_dict = _compute_custom_metrics(row.to_dict(), custom_metrics)

        instance_list.append(row_dict)

        for metric in api_metrics:
            task = asyncio.create_task(
                _instance_evaluation.evaluate_instances_async(
                    client=evaluation_run_config.client,
                    request=_instance_evaluation.build_request(
                        metric=metric,
                        row_dict=row_dict,
                        evaluation_run_config=evaluation_run_config,
                    ),
                )
            )
            if isinstance(metric, metrics_base.PairwiseMetric):
                metric_name = metric.pairwise_metric_name
            else:
                metric_name = metric
            tasks_by_metric[metric_name].append(task)

    api_request_count = len(api_metrics) * len(evaluation_run_config.dataset)
    _LOGGER.info(
        f"Computing metrics with a total of {api_request_count} Vertex online"
        " evaluation service requests."
    )
    results_dict = {
        metric_name: await asyncio.gather(*tasks)
        for metric_name, tasks in tasks_by_metric.items()
    }

    instance_df = pd.DataFrame.from_dict(instance_list)
    metrics_table = _parse_metric_results_to_dataframe(instance_df, results_dict)

    _LOGGER.info(f"All {api_request_count} metrics are successfully computed.")
    summary_metrics = _compute_summary_metrics(evaluation_run_config, metrics_table)
    return summary_metrics, metrics_table


def _run_model_inference(
    model: Union[generative_models.GenerativeModel, Callable[[str], str]],
    evaluation_run_config: evaluation_base.EvaluationRunConfig,
    is_baseline_model: bool = False,
) -> None:
    """Runs model inference on dataset for evaluation.

    Args:
      model: The GenerativeModel instance or a custom model function to generate
        responses to evaluate. If not provided, the evaluation is computed with
        the `response` column in the `dataset`.
      evaluation_run_config: Evaluation Run Configurations.
      is_baseline_model: Whether the model is a baseline model for PairwiseMetric.

    Raises:
        ValueError: If the model or baseline model is not supported.
    """
    if isinstance(model, generative_models.GenerativeModel):
        _generate_response_from_gemini_model(
            model, evaluation_run_config, is_baseline_model
        )
    elif callable(model):
        _generate_response_from_custom_model_fn(
            model, evaluation_run_config, is_baseline_model
        )
    else:
        raise ValueError(f"Unsupported model or baseline model type: {type(model)}")


def evaluate(
    dataset: "pd.DataFrame",
    metrics: List[Union[str, metrics_base.CustomMetric, metrics_base.PairwiseMetric]],
    *,
    model: Optional[
        Union[generative_models.GenerativeModel, Callable[[str], str]]
    ] = None,
    prompt_template: Optional[Union[str, prompt_template_base.PromptTemplate]] = None,
    content_column_name: str = "content",
    reference_column_name: str = "reference",
    response_column_name: str = "response",
    context_column_name: str = "context",
    instruction_column_name: str = "instruction",
) -> evaluation_base.EvalResult:
    """Runs the evaluation for metrics.

    Args:
      dataset: The dataset to evaluate.
      metrics: The list of metric names, or metric bundle names, or CustomMetric
        instances, or PairwiseMetric instances to evaluate. Prompt template is
        required for PairwiseMetric.
      model: The GenerativeModel instance or a custom model function to generate
        responses to evaluate. If not provided, the evaluation is computed with
        the `response` column in the `dataset`.
      prompt_template: A `PromptTemplate` or a prompt template string compatible
        with `PromptTemplate` class with placeholders that can be formatted with
        dataset columns to create completed prompts. The placeholders can be
        represented in curly braces `{placeholder}`, and must be included in the
        dataset columns if specified. The placeholder names cannot contain spaces.
      content_column_name: The column name of content in the dataset to send to
        the model. If not set, default to `content`.
      reference_column_name: The column name of ground truth in the dataset. If
        not set, default to `reference`.
      response_column_name: The column name of model response in the dataset. If
        not set, default to `response`.
      context_column_name: The column name of summary context in the dataset. If
        not set, default to `context`.
      instruction_column_name: The column name of the instruction prompt in the
        dataset. If not set, default to `instruction`.

    Returns:
      EvalResult with summary metrics and a metrics table for per-instance
      metrics.

    Raises:
      ValueError: If the metrics list is empty, or the prompt template is not
      provided for PairwiseMetric, or multiple baseline models are specified for
      PairwiseMetric instances, or both model and dataset model response column
      are present.
    """

    if not metrics:
        raise ValueError("Metrics cannot be empty.")

    evaluation_run_config = evaluation_base.EvaluationRunConfig(
        dataset=dataset,
        metrics=_replace_metric_bundle_with_metrics(metrics),
        column_map={
            constants.Dataset.CONTENT_COLUMN: content_column_name,
            constants.Dataset.REFERENCE_COLUMN: reference_column_name,
            constants.Dataset.MODEL_RESPONSE_COLUMN: response_column_name,
            constants.Dataset.CONTEXT_COLUMN: context_column_name,
            constants.Dataset.INSTRUCTION_COLUMN: instruction_column_name,
        },
        client=utils.create_evaluation_service_async_client(),
    )

    if set(evaluation_run_config.metrics).intersection(
        set(constants.Metric.AUTOMATIC_METRIC_LIST)
    ):
        evaluation_run_config.validate_dataset_column(
            constants.Dataset.REFERENCE_COLUMN
        )

    if (
        model
        and evaluation_run_config.column_map.get(
            constants.Dataset.MODEL_RESPONSE_COLUMN
        )
        in dataset.columns
    ):
        raise ValueError(
            "The `model` parameter is specified, but the evaluation `dataset`"
            f" contains model response column `{response_column_name}` to perform"
            " bring-your-own-prediction(BYOP) evaluation. If you would like to"
            " perform rapid evaluation using the dataset with the existing model"
            f" response column `{response_column_name}`, please remove the"
            " `model` input parameter."
        )

    baseline_model = None
    pairwise_metric_exists = any(
        isinstance(metric, metrics_base.PairwiseMetric)
        for metric in evaluation_run_config.metrics
    )
    if pairwise_metric_exists:
        pairwise_metric_instances = [
            metric
            for metric in evaluation_run_config.metrics
            if isinstance(metric, metrics_base.PairwiseMetric)
        ]
        if (
            len(set(instance.baseline_model for instance in pairwise_metric_instances))
            > 1
        ):
            # TODO(b/330598854): support multiple baseline models to compare
            # with the candidate model.
            raise ValueError(
                "Not all PairwiseMetric instances have the same baseline_model"
            )
        baseline_model = pairwise_metric_instances[0].baseline_model

    if prompt_template:
        _complete_prompt_for_dataset(evaluation_run_config, prompt_template)
        evaluation_run_config.validate_dataset_column(
            constants.Dataset.COMPLETED_PROMPT_COLUMN
        )
    elif baseline_model:
        raise ValueError("Prompt template is required for computing PairwiseMetric.")
    elif model:
        evaluation_run_config.validate_dataset_column(constants.Dataset.CONTENT_COLUMN)

    if model:
        _run_model_inference(model, evaluation_run_config)
    evaluation_run_config.validate_dataset_column(
        constants.Dataset.MODEL_RESPONSE_COLUMN
    )

    if baseline_model:
        _run_model_inference(
            model=baseline_model,
            evaluation_run_config=evaluation_run_config,
            is_baseline_model=True,
        )
    if pairwise_metric_exists:
        evaluation_run_config.validate_dataset_column(
            constants.Dataset.BASELINE_MODEL_RESPONSE_COLUMN
        )

    if asyncio.get_event_loop().is_running():
        asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()

    summary_metrics, metrics_table = loop.run_until_complete(
        _compute_metrics(evaluation_run_config)
    )

    return evaluation_base.EvalResult(
        summary_metrics=summary_metrics, metrics_table=metrics_table
    )
