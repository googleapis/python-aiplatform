# Copyright 2025 Google LLC
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

"""Transformers module for Vertex addons."""
import re
from typing import Any

from google.genai._common import get_value_by_path as getv

from . import _evals_constant
from . import types

_METRIC_RES_NAME_RE = r"^projects/[^/]+/locations/[^/]+/evaluationMetrics/[^/]+$"


def t_metrics(
    metrics: "list[types.MetricSubclass]",
    set_default_aggregation_metrics: bool = False,
) -> list[dict[str, Any]]:
    """Prepares the metric payload for the evaluation request.

    Args:
        metrics: A list of metrics used for evaluation.
        set_default_aggregation_metrics: Whether to set default aggregation metrics.
    Returns:
        A list of resolved metric payloads for the evaluation request.
    """
    metrics_payload = []

    for metric in metrics:
        metric_payload_item: dict[str, Any] = {}

        metric_id = getv(metric, ["metric"]) or getv(metric, ["name"])
        metric_name = metric_id.lower() if metric_id else None

        if set_default_aggregation_metrics:
            metric_payload_item["aggregation_metrics"] = [
                "AVERAGE",
                "STANDARD_DEVIATION",
            ]

        if metric_name == "exact_match":
            metric_payload_item["exact_match_spec"] = {}
        elif metric_name == "bleu":
            metric_payload_item["bleu_spec"] = {}
        elif metric_name and metric_name.startswith("rouge"):
            rouge_type = metric_name.replace("_", "")
            metric_payload_item["rouge_spec"] = {"rouge_type": rouge_type}
        # API Pre-defined metrics
        elif (
            metric_name and metric_name in _evals_constant.SUPPORTED_PREDEFINED_METRICS
        ):
            metric_payload_item["predefined_metric_spec"] = {
                "metric_spec_name": metric_name,
                "metric_spec_parameters": metric.metric_spec_parameters,
            }
        # Custom Code Execution Metric
        elif (
            hasattr(metric, "remote_custom_function") and metric.remote_custom_function
        ):
            metric_payload_item["custom_code_execution_spec"] = {
                "evaluation_function": metric.remote_custom_function
            }
        # Pointwise metrics
        elif hasattr(metric, "prompt_template") and metric.prompt_template:
            llm_based_spec = {"metric_prompt_template": metric.prompt_template}
            system_instruction = getv(metric, ["judge_model_system_instruction"])
            if system_instruction:
                llm_based_spec["system_instruction"] = system_instruction
            rubric_group_name = getv(metric, ["rubric_group_name"])
            if rubric_group_name:
                llm_based_spec["rubric_group_key"] = rubric_group_name
            return_raw_output = getv(metric, ["return_raw_output"])
            if return_raw_output:
                llm_based_spec["custom_output_format_config"] = {
                    "return_raw_output": return_raw_output
                }
            metric_payload_item["llm_based_metric_spec"] = llm_based_spec
        elif getattr(metric, "metric_resource_name", None) is not None:
            # Safe pass
            pass
        else:
            raise ValueError(
                f"Unsupported metric type or invalid metric name: {metric_name}"
            )
        metrics_payload.append(metric_payload_item)
    return metrics_payload


def t_metric_sources(metrics: list[Any]) -> list[dict[str, Any]]:
    """Prepares the MetricSource payload."""
    sources_payload = []
    for metric in metrics:
        resource_name = getattr(metric, "metric_resource_name", None)
        if (
            not resource_name
            and isinstance(metric, str)
            and re.match(_METRIC_RES_NAME_RE, metric)
        ):
            resource_name = metric

        if resource_name:
            sources_payload.append({"metric_resource_name": resource_name})
        else:
            if hasattr(metric, "metric") and not isinstance(metric, str):
                metric = metric.metric

            if not hasattr(metric, "name"):
                metric = types.Metric(name=str(metric))

            metric_payload = t_metrics([metric])[0]
            sources_payload.append({"metric": metric_payload})
    return sources_payload


def t_user_scenario_generation_config(
    config: "types.evals.UserScenarioGenerationConfigOrDict",
) -> dict[str, Any]:
    """Transforms UserScenarioGenerationConfig to Vertex AI format."""
    payload: dict[str, Any] = {}
    config_dict = config if isinstance(config, dict) else config.model_dump()

    if getv(config_dict, ["count"]) is not None:
        payload["user_scenario_count"] = getv(config_dict, ["count"])
    if getv(config_dict, ["generation_instruction"]) is not None:
        payload["simulation_instruction"] = getv(
            config_dict, ["generation_instruction"]
        )
    if getv(config_dict, ["environment_context"]) is not None:
        payload["environment_data"] = getv(config_dict, ["environment_context"])
    if getv(config_dict, ["model_name"]) is not None:
        payload["model_name"] = getv(config_dict, ["model_name"])

    return payload


def t_metric_for_registry(
    metric: "types.Metric",
) -> dict[str, Any]:
    """Prepares the metric payload specifically for EvaluationMetric registration."""
    metric_payload_item: dict[str, Any] = {}
    metric_name = getattr(metric, "name", None)
    if metric_name:
        metric_name = metric_name.lower()

    # Handle standard computation metrics
    if metric_name == "exact_match":
        metric_payload_item["exact_match_spec"] = {}
    elif metric_name == "bleu":
        metric_payload_item["bleu_spec"] = {}
    elif metric_name and metric_name.startswith("rouge"):
        rouge_type = metric_name.replace("_", "")
        metric_payload_item["rouge_spec"] = {"rouge_type": rouge_type}
    # API Pre-defined metrics
    elif metric_name and metric_name in _evals_constant.SUPPORTED_PREDEFINED_METRICS:
        metric_payload_item["predefined_metric_spec"] = {
            "metric_spec_name": metric_name,
            "metric_spec_parameters": metric.metric_spec_parameters,
        }
    # Custom Code Execution Metric
    elif hasattr(metric, "remote_custom_function") and metric.remote_custom_function:
        metric_payload_item["custom_code_execution_spec"] = {
            "evaluation_function": metric.remote_custom_function
        }

    # Map LLM-based metrics to the new llm_based_metric_spec
    elif (hasattr(metric, "prompt_template") and metric.prompt_template) or (
        hasattr(metric, "rubric_group_name") and metric.rubric_group_name
    ):
        llm_based_spec = {}

        if hasattr(metric, "prompt_template") and metric.prompt_template:
            llm_based_spec["metric_prompt_template"] = metric.prompt_template
        system_instruction = getv(metric, ["judge_model_system_instruction"])
        if system_instruction:
            llm_based_spec["system_instruction"] = system_instruction
        rubric_group_name = getv(metric, ["rubric_group_name"])
        if rubric_group_name:
            llm_based_spec["rubric_group_key"] = rubric_group_name

        metric_payload_item["llm_based_metric_spec"] = llm_based_spec

    else:
        raise ValueError(f"Unsupported metric type: {metric_name}")

    return metric_payload_item
