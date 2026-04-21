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
"""Utility functions for evals."""

import abc
import asyncio
import json
import logging
import os
import threading
import time
from typing import Any, Optional, Union

from google.genai._api_client import BaseApiClient
from google.genai._common import get_value_by_path as getv
from google.genai._common import set_value_by_path as setv
import pandas as pd

from . import _bigquery_utils
from . import _gcs_utils
from . import _transformers
from . import types


logger = logging.getLogger(__name__)


GCS_PREFIX = "gs://"
BQ_PREFIX = "bq://"
_DEFAULT_EVAL_SERVICE_QPS = 10


class RateLimiter:
    """Helper class for rate-limiting requests to Vertex AI to improve QoS.

    Implements a token bucket algorithm to limit the rate at which API calls
    can occur. Designed for cases where the batch size is always 1 for traffic
    shaping and rate limiting.

    Attributes:
        seconds_per_event: The time interval (in seconds) between events to
            maintain the desired rate.
        last: The timestamp of the last event.
        _lock: A lock to ensure thread safety.
    """

    def __init__(self, rate: float) -> None:
        """Initializes the rate limiter.

        Args:
            rate: The number of queries allowed per second.

        Raises:
            ValueError: If the rate is not positive.
        """
        if not rate or rate <= 0:
            raise ValueError("Rate must be a positive number")
        self.seconds_per_event = 1.0 / rate
        self._next_allowed = time.monotonic()
        self._lock = threading.Lock()

    def sleep_and_advance(self) -> None:
        """Blocks the current thread until the next event can be admitted.

        The lock is held only long enough to reserve a time slot. The
        actual sleep happens outside the lock so that multiple threads
        can be sleeping concurrently with staggered wake-up times.
        """
        with self._lock:
            now = time.monotonic()
            wait_until = max(now, self._next_allowed)
            delay = wait_until - now
            self._next_allowed = wait_until + self.seconds_per_event

        if delay > 0:
            time.sleep(delay)


class EvalDatasetLoader:
    """A loader for datasets from various sources, using a shared client."""

    def __init__(self, api_client: BaseApiClient) -> None:
        self.api_client = api_client
        self.gcs_utils = _gcs_utils.GcsUtils(self.api_client)
        self.bigquery_utils = _bigquery_utils.BigQueryUtils(self.api_client)

    def _load_file(
        self, filepath: str, file_type: str
    ) -> Union[list[dict[str, Any]], Any]:
        """Loads data from a file into a list of dictionaries."""
        if filepath.startswith(GCS_PREFIX):
            df = self.gcs_utils.read_gcs_file_to_dataframe(filepath, file_type)
            return df.to_dict(orient="records")
        else:
            if file_type == "jsonl":
                df = pd.read_json(filepath, lines=True)
                return df.to_dict(orient="records")
            elif file_type == "csv":
                df = pd.read_csv(filepath, encoding="utf-8")
                return df.to_dict(orient="records")
            else:
                raise ValueError(
                    f"Unsupported file type: '{file_type}'. Please provide 'jsonl' or"
                    " 'csv'."
                )

    def load(
        self, source: Union[str, "pd.DataFrame"]
    ) -> Union[list[dict[str, Any]], Any]:
        """Loads dataset from various sources into a list of dictionaries."""
        if isinstance(source, pd.DataFrame):
            return source.to_dict(orient="records")
        elif isinstance(source, str):
            if source.startswith(BQ_PREFIX):
                df = self.bigquery_utils.load_bigquery_to_dataframe(
                    source[len(BQ_PREFIX) :]
                )
                return df.to_dict(orient="records")

            _, extension = os.path.splitext(source)
            file_type = extension.lower()[1:]

            if file_type == "jsonl":
                return self._load_file(source, "jsonl")
            elif file_type == "csv":
                return self._load_file(source, "csv")
            else:
                raise TypeError(
                    f"Unsupported file type: {file_type} from {source}. Please"
                    " provide a valid GCS path with `jsonl` or `csv` suffix, "
                    "a local file path, or a valid BigQuery table URI."
                )
        else:
            raise TypeError(
                "Unsupported dataset type. Must be a `pd.DataFrame`, Python"
                " a valid GCS path with `jsonl` or `csv` suffix, a local"
                " file path, or a valid BigQuery table URI."
            )


class BatchEvaluateRequestPreparer:
    """Prepares data for requests."""

    @staticmethod
    def _EvaluationDataset_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}

        if getv(from_object, ["gcs_source"]) is not None:
            setv(
                to_object,
                ["gcs_source"],
                getv(from_object, ["gcs_source"]),
            )

        if getv(from_object, ["bigquery_source"]) is not None:
            setv(
                to_object,
                ["bigquery_source"],
                getv(from_object, ["bigquery_source"]),
            )

        return to_object

    @staticmethod
    def _Metric_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}

        if getv(from_object, ["prompt_template"]) is not None:
            setv(
                to_object,
                ["pointwise_metric_spec", "prompt_template"],
                getv(from_object, ["prompt_template"]),
            )

        if getv(from_object, ["judge_model"]) is not None:
            setv(
                parent_object,
                ["autorater_config", "autorater_model"],
                getv(from_object, ["judge_model"]),
            )

        if getv(from_object, ["judge_model_sampling_count"]) is not None:
            setv(
                parent_object,
                ["autorater_config", "sampling_count"],
                getv(from_object, ["judge_model_sampling_count"]),
            )

        if getv(from_object, ["judge_model_system_instruction"]) is not None:
            setv(
                to_object,
                ["pointwise_metric_spec", "system_instruction"],
                getv(from_object, ["judge_model_system_instruction"]),
            )

        if getv(from_object, ["return_raw_output"]) is not None:
            setv(
                to_object,
                [
                    "pointwise_metric_spec",
                    "custom_output_format_config",
                    "return_raw_output",
                ],
                getv(from_object, ["return_raw_output"]),
            )

        return to_object

    @staticmethod
    def _OutputConfig_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["gcs_destination"]) is not None:
            setv(
                to_object,
                ["gcsDestination"],
                getv(from_object, ["gcs_destination"]),
            )

        return to_object

    @staticmethod
    def _EvaluationDataset_from_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}

        if getv(from_object, ["dataset", "gcs_source"]) is not None:
            setv(
                to_object,
                ["gcs_source"],
                getv(from_object, ["dataset", "gcs_source"]),
            )

        if getv(from_object, ["dataset", "bigquery_source"]) is not None:
            setv(
                to_object,
                ["bigquery_source"],
                getv(from_object, ["dataset", "bigquery_source"]),
            )

        return to_object

    @staticmethod
    def _AutoraterConfig_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["sampling_count"]) is not None:
            setv(to_object, ["samplingCount"], getv(from_object, ["sampling_count"]))

        if getv(from_object, ["flip_enabled"]) is not None:
            setv(to_object, ["flipEnabled"], getv(from_object, ["flip_enabled"]))

        if getv(from_object, ["autorater_model"]) is not None:
            setv(
                to_object,
                ["autoraterModel"],
                getv(from_object, ["autorater_model"]),
            )

        return to_object

    @staticmethod
    def EvaluateDatasetOperation_from_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["name"]) is not None:
            setv(to_object, ["name"], getv(from_object, ["name"]))

        if getv(from_object, ["metadata"]) is not None:
            setv(to_object, ["metadata"], getv(from_object, ["metadata"]))

        if getv(from_object, ["done"]) is not None:
            setv(to_object, ["done"], getv(from_object, ["done"]))

        if getv(from_object, ["error"]) is not None:
            setv(to_object, ["error"], getv(from_object, ["error"]))

        if getv(from_object, ["response"]) is not None:
            setv(
                to_object,
                ["response"],
                BatchEvaluateRequestPreparer._EvaluationDataset_from_vertex(
                    getv(from_object, ["response"]), to_object
                ),
            )

        return to_object

    @staticmethod
    def EvaluateDatasetRequestParameters_to_vertex(
        from_object: Union[dict[str, Any], object],
        parent_object: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        to_object: dict[str, Any] = {}
        if getv(from_object, ["dataset"]) is not None:
            setv(
                to_object,
                ["dataset"],
                BatchEvaluateRequestPreparer._EvaluationDataset_to_vertex(
                    getv(from_object, ["dataset"]), to_object
                ),
            )

        if getv(from_object, ["metrics"]) is not None:
            setv(
                to_object,
                ["metrics"],
                [
                    BatchEvaluateRequestPreparer._Metric_to_vertex(item, to_object)
                    for item in getv(from_object, ["metrics"])
                ],
            )

        if getv(from_object, ["output_config"]) is not None:
            setv(
                to_object,
                ["outputConfig"],
                BatchEvaluateRequestPreparer._OutputConfig_to_vertex(
                    getv(from_object, ["output_config"]), to_object
                ),
            )

        if getv(from_object, ["autorater_config"]) is not None:
            setv(
                to_object,
                ["autoraterConfig"],
                BatchEvaluateRequestPreparer._AutoraterConfig_to_vertex(
                    getv(from_object, ["autorater_config"]), to_object
                ),
            )

        if getv(from_object, ["config"]) is not None:
            setv(to_object, ["config"], getv(from_object, ["config"]))

        return to_object

    @staticmethod
    def prepare_metric_payload(
        request_dict: dict[str, Any], resolved_metrics: list["types.MetricSubclass"]
    ) -> dict[str, Any]:
        """Prepares the metric payload for the evaluation request.

        Args:
            request_dict: The dictionary containing the request details.
            resolved_metrics: A list of resolved metric objects.

        Returns:
            The updated request dictionary with the prepared metric payload.
        """
        request_dict["metrics"] = _transformers.t_metrics(
            resolved_metrics, set_default_aggregation_metrics=True
        )
        return request_dict


class EvalDataConverter(abc.ABC):
    """Abstract base class for dataset converters."""

    @abc.abstractmethod
    def convert(self, raw_data: Any) -> "types.EvaluationDataset":
        """Converts a loaded raw dataset into an EvaluationDataset."""
        raise NotImplementedError()


def _postprocess_user_scenarios_response(
    response: types.GenerateUserScenariosResponse,
) -> types.EvaluationDataset:
    """Postprocesses the response from generating user scenarios."""
    eval_cases = []
    data_for_df = []
    if hasattr(response, "user_scenarios") and response.user_scenarios:
        for scenario in response.user_scenarios:
            eval_case = types.EvalCase(
                user_scenario=scenario,
            )
            eval_cases.append(eval_case)
            data_for_df.append(
                {
                    "starting_prompt": scenario.starting_prompt,
                    "conversation_plan": scenario.conversation_plan,
                }
            )
    eval_dataset_df = None
    if pd is not None:
        eval_dataset_df = pd.DataFrame(data_for_df)
    else:
        logger.warning("Pandas is not installed. eval_dataset_df will be None.")
    return types.EvaluationDataset(
        eval_cases=eval_cases, eval_dataset_df=eval_dataset_df
    )


def _display_loss_analysis_result(
    result: types.LossAnalysisResult,
) -> None:
    """Displays a LossAnalysisResult as a formatted pandas DataFrame."""
    metric = result.config.metric if result.config else None
    candidate = result.config.candidate if result.config else None
    rows: list[dict[str, Any]] = []
    for cluster in result.clusters or []:
        entry = cluster.taxonomy_entry
        row = {
            "metric": metric,
            "candidate": candidate,
            "cluster_id": cluster.cluster_id,
            "l1_category": entry.l1_category if entry else None,
            "l2_category": entry.l2_category if entry else None,
            "description": entry.description if entry else None,
            "item_count": cluster.item_count,
        }
        rows.append(row)

    if not rows:
        logger.info("No loss clusters found.")
        return

    df = pd.DataFrame(rows)
    try:
        from IPython.display import display  # pylint: disable=g-import-not-at-top

        display(df)
    except ImportError:
        print(df.to_string())  # pylint: disable=print-function


def _resolve_metric_name(
    metric: Optional[Any],
) -> Optional[str]:
    """Extracts a metric name string from a metric argument.

    Accepts a string, a Metric object, or a LazyLoadedPrebuiltMetric
    (RubricMetric) and returns the metric name as a string.

    For LazyLoadedPrebuiltMetric (e.g., RubricMetric.MULTI_TURN_TASK_SUCCESS),
    this resolves to the API metric spec name (e.g.,
    "multi_turn_task_success_v1") so it matches the keys in eval results.

    Args:
        metric: A metric name string, Metric object, RubricMetric enum value, or
          None.

    Returns:
        The metric name as a string, or None if metric is None.
    """
    if metric is None:
        return None
    if isinstance(metric, str):
        return metric
    # LazyLoadedPrebuiltMetric: resolve to versioned API spec name.
    if hasattr(metric, "_get_api_metric_spec_name"):
        spec_name: Optional[str] = metric._get_api_metric_spec_name()
        if spec_name:
            return spec_name
    # Metric objects and other types with a .name attribute.
    if hasattr(metric, "name"):
        return str(metric.name)
    return str(metric)


def _resolve_eval_run_loss_configs(
    loss_analysis_metrics: Optional[list[Any]] = None,
    loss_analysis_configs: Optional[list[Any]] = None,
    inference_configs: Optional[dict[str, Any]] = None,
) -> Optional[list[types.LossAnalysisConfig]]:
    """Resolves loss analysis configs for create_evaluation_run.

    Supports two modes:
    1. ``loss_analysis_metrics``: A simplified list of metrics. The candidate
       is auto-inferred from ``inference_configs`` when there is exactly one
       candidate. Each metric is resolved via ``_resolve_metric_name()``.
    2. ``loss_analysis_configs``: Explicit ``LossAnalysisConfig`` objects or
       dicts for full control.

    Args:
        loss_analysis_metrics: Optional list of metric references (strings,
            Metric objects, or RubricMetric enums).
        loss_analysis_configs: Optional list of LossAnalysisConfig or dicts.
        inference_configs: The resolved inference_configs dict (candidate name
            -> config). Used to auto-infer candidate for the metrics path.

    Returns:
        A list of resolved LossAnalysisConfig objects, or None if neither
        loss_analysis_metrics nor loss_analysis_configs is provided.

    Raises:
        ValueError: If candidate cannot be inferred for loss_analysis_metrics.
    """
    if not loss_analysis_metrics and not loss_analysis_configs:
        return None

    if loss_analysis_configs:
        return [
            types.LossAnalysisConfig.model_validate(c) if isinstance(c, dict) else c
            for c in loss_analysis_configs
        ]

    # loss_analysis_metrics path: auto-infer candidate from inference_configs
    candidate = None
    if inference_configs and len(inference_configs) == 1:
        candidate = next(iter(inference_configs))
    elif inference_configs and len(inference_configs) > 1:
        raise ValueError(
            "Cannot infer candidate for loss analysis: multiple candidates"
            f" found in inference_configs: {list(inference_configs.keys())}."
            " Please use loss_analysis_configs with explicit candidate values"
            " instead."
        )

    configs = []
    for m in loss_analysis_metrics or []:
        metric_name = _resolve_metric_name(m)
        configs.append(
            types.LossAnalysisConfig(metric=metric_name, candidate=candidate)
        )
    return configs


def _resolve_loss_analysis_config(
    eval_result: types.EvaluationResult,
    config: Optional[types.LossAnalysisConfig] = None,
    metric: Optional[str] = None,
    candidate: Optional[str] = None,
) -> types.LossAnalysisConfig:
    """Resolves and validates the LossAnalysisConfig for generate_loss_clusters.

    Auto-infers `metric` and `candidate` from the EvaluationResult when not
    explicitly provided. Validates that provided values exist in the eval result.

    Args:
        eval_result: The EvaluationResult from client.evals.evaluate().
        config: Optional explicit LossAnalysisConfig. If provided, metric and
          candidate from config take precedence over the separate arguments.
        metric: Optional metric name override.
        candidate: Optional candidate name override.

    Returns:
        A resolved LossAnalysisConfig with metric and candidate populated.

    Raises:
        ValueError: If metric/candidate cannot be inferred or are invalid.
    """
    # Start from config if provided, otherwise create a new one.
    if config is not None:
        resolved_metric = metric or config.metric
        resolved_candidate = candidate or config.candidate
        resolved_config = config.model_copy(
            update={"metric": resolved_metric, "candidate": resolved_candidate}
        )
    else:
        resolved_config = types.LossAnalysisConfig(metric=metric, candidate=candidate)

    # Collect available metric names from the eval result.
    available_metrics: set[str] = set()
    if eval_result.eval_case_results:
        for case_result in eval_result.eval_case_results:
            for resp_cand in case_result.response_candidate_results or []:
                for m_name in (resp_cand.metric_results or {}).keys():
                    available_metrics.add(m_name)

    # Collect available candidate names from metadata.
    available_candidates: list[str] = []
    if eval_result.metadata and eval_result.metadata.candidate_names:
        available_candidates = list(eval_result.metadata.candidate_names)

    # Auto-infer metric if not provided.
    if not resolved_config.metric:
        if len(available_metrics) == 1:
            resolved_config = resolved_config.model_copy(
                update={"metric": next(iter(available_metrics))}
            )
        elif len(available_metrics) == 0:
            raise ValueError(
                "Cannot infer metric: no metric results found in eval_result."
                " Please provide metric explicitly via"
                " config=types.LossAnalysisConfig(metric='...')."
            )
        else:
            raise ValueError(
                "Cannot infer metric: multiple metrics found in eval_result:"
                f" {sorted(available_metrics)}. Please provide metric"
                " explicitly via config=types.LossAnalysisConfig(metric='...')."
            )

    # Validate metric if provided explicitly.
    if available_metrics and resolved_config.metric not in available_metrics:
        raise ValueError(
            f"Metric '{resolved_config.metric}' not found in eval_result."
            f" Available metrics: {sorted(available_metrics)}."
        )

    # Auto-infer candidate if not provided.
    if not resolved_config.candidate:
        if len(available_candidates) == 1:
            resolved_config = resolved_config.model_copy(
                update={"candidate": available_candidates[0]}
            )
        elif len(available_candidates) == 0:
            # Fallback: use default candidate naming convention from SDK.
            resolved_config = resolved_config.model_copy(
                update={"candidate": "candidate_1"}
            )
            logger.warning(
                "No candidate names found in eval_result.metadata."
                " Defaulting to 'candidate_1'. If this is incorrect, provide"
                " candidate explicitly via"
                " config=types.LossAnalysisConfig(candidate='...')."
            )
        else:
            raise ValueError(
                "Cannot infer candidate: multiple candidates found in"
                f" eval_result: {available_candidates}. Please provide"
                " candidate explicitly via"
                " config=types.LossAnalysisConfig(candidate='...')."
            )

    # Validate candidate if provided explicitly and candidates are known.
    if available_candidates and resolved_config.candidate not in available_candidates:
        raise ValueError(
            f"Candidate '{resolved_config.candidate}' not found in"
            f" eval_result. Available candidates: {available_candidates}."
        )

    return resolved_config


def _build_rubric_description_map(
    eval_result: types.EvaluationResult,
) -> dict[str, str]:
    """Builds a rubric_id -> description map from the EvaluationResult."""
    rubric_map: dict[str, str] = {}
    for case_result in eval_result.eval_case_results or []:
        for resp_cand in case_result.response_candidate_results or []:
            for metric_res in (resp_cand.metric_results or {}).values():
                for verdict in metric_res.rubric_verdicts or []:
                    rubric = verdict.evaluated_rubric
                    if rubric and rubric.rubric_id and rubric.content:
                        if (
                            rubric.content.property
                            and rubric.content.property.description
                        ):
                            rubric_map[rubric.rubric_id] = (
                                rubric.content.property.description
                            )
    return rubric_map


def _extract_scenario_preview_from_dict(
    eval_result_dict: dict[str, Any],
) -> Optional[str]:
    """Extracts the first user message from an evaluation_result dict.

    Handles both snake_case (SDK-side) and camelCase (API echo-back) keys.
    """
    request = eval_result_dict.get("request")
    if not request:
        return None
    prompt = request.get("prompt")
    if not prompt:
        return None
    # Try agent_data (snake_case or camelCase)
    agent_data = prompt.get("agent_data") or prompt.get("agentData")
    if agent_data and isinstance(agent_data, dict):
        turns = agent_data.get("turns", [])
        for turn in turns:
            events = turn.get("events", [])
            for event in events:
                author = event.get("author", "")
                content = event.get("content")
                if author.lower() == "user" and content and isinstance(content, dict):
                    parts = content.get("parts", [])
                    for part in parts:
                        text = str(part.get("text", "")).strip()
                        if text:
                            if len(text) > 150:
                                return text[:150] + "..."
                            return text
    # Try simple prompt path
    parts = prompt.get("parts", [])
    for part in parts:
        text = str(part.get("text", "")).strip()
        if text:
            if len(text) > 150:
                return text[:150] + "..."
            return text
    return None


def _extract_scenario_from_agent_data(agent_data: Any) -> Optional[str]:
    """Extracts the first user message from an AgentData object or dict."""
    if agent_data is None:
        return None
    if hasattr(agent_data, "model_dump"):
        agent_data = agent_data.model_dump()
    if isinstance(agent_data, str):
        try:
            agent_data = json.loads(agent_data)
        except (json.JSONDecodeError, ValueError):
            return None
    if not isinstance(agent_data, dict):
        return None
    turns = agent_data.get("turns", [])
    if not isinstance(turns, list):
        return None
    for turn in turns:
        if not isinstance(turn, dict):
            continue
        events = turn.get("events", [])
        if not isinstance(events, list):
            continue
        for event in events:
            if not isinstance(event, dict):
                continue
            author = event.get("author", "")
            if not isinstance(author, str) or author.lower() != "user":
                continue
            content = event.get("content")
            if not content or not isinstance(content, dict):
                continue
            parts = content.get("parts", [])
            if not isinstance(parts, list):
                continue
            for part in parts:
                if not isinstance(part, dict):
                    continue
                text = str(part.get("text", "")).strip()
                if text:
                    if len(text) > 150:
                        return text[:150] + "..."
                    return text
    return None


def _truncate_scenario(text: str, max_len: int = 150) -> str:
    """Truncates a scenario preview to max_len characters."""
    text = text.strip()
    if len(text) > max_len:
        return text[:max_len] + "..."
    return text


def _build_scenario_preview_list(
    eval_result: types.EvaluationResult,
) -> list[Optional[str]]:
    """Builds an ordered list of scenario previews from the EvaluationResult.

    Returns one scenario preview per eval_case_result, in the same order as
    eval_case_results. This extracts the first user message from the original
    SDK EvaluationResult (via eval_cases or DataFrame), rather than relying
    on the API echo-back which may not preserve the request data.

    Extraction priority per eval case:
    1. eval_case.agent_data → first user message in turns
    2. eval_case.user_scenario.starting_prompt
    3. eval_case.prompt → text content
    4. DataFrame agent_data column → first user message
    5. DataFrame starting_prompt column
    """
    eval_dataset = eval_result.evaluation_dataset
    eval_cases: list[Any] = []
    if isinstance(eval_dataset, list) and eval_dataset:
        eval_cases = getv(eval_dataset[0], ["eval_cases"]) or []

    eval_case_results = eval_result.eval_case_results or []
    scenarios: list[Optional[str]] = []

    for case_result in eval_case_results:
        case_idx = case_result.eval_case_index or 0
        scenario: Optional[str] = None

        eval_case = None
        if 0 <= case_idx < len(eval_cases):
            eval_case = eval_cases[case_idx]

        if eval_case:
            # 1. Try agent_data (populated after run_inference)
            agent_data = getv(eval_case, ["agent_data"])
            if agent_data:
                scenario = _extract_scenario_from_agent_data(agent_data)

            # 2. Try user_scenario.starting_prompt (from
            #    generate_conversation_scenarios)
            if scenario is None:
                user_scenario = getv(eval_case, ["user_scenario"])
                if user_scenario:
                    starting_prompt = getv(user_scenario, ["starting_prompt"])
                    if starting_prompt and isinstance(starting_prompt, str):
                        scenario = _truncate_scenario(starting_prompt)

            # 3. Try prompt text
            if scenario is None:
                prompt = getv(eval_case, ["prompt"])
                if prompt:
                    from . import _evals_data_converters

                    text = _evals_data_converters._get_content_text(prompt)
                    if text:
                        scenario = _truncate_scenario(str(text))

        # 4. Fallback: extract agent_data from DataFrame
        if scenario is None and eval_dataset:
            df_agent_data = _transformers._extract_agent_data_from_df(
                eval_dataset, case_idx
            )
            if df_agent_data is not None:
                scenario = _extract_scenario_from_agent_data(df_agent_data)

        # 5. Fallback: extract starting_prompt from DataFrame
        if scenario is None and eval_dataset:
            ds = eval_dataset[0] if isinstance(eval_dataset, list) else eval_dataset
            df = getv(ds, ["eval_dataset_df"])
            if df is not None and hasattr(df, "iloc"):
                if 0 <= case_idx < len(df):
                    row = df.iloc[case_idx]
                    sp = row.get("starting_prompt")
                    if sp and isinstance(sp, str) and sp.strip():
                        scenario = _truncate_scenario(sp)

        scenarios.append(scenario)

    return scenarios


def _enrich_loss_response_with_rubric_descriptions(
    response: types.GenerateLossClustersResponse,
    eval_result: types.EvaluationResult,
) -> None:
    """Enriches loss response with rubric descriptions and scenario previews.

    Rubric descriptions and scenario previews are extracted from the original
    SDK EvaluationResult object, because the API echo-back in
    LossExample.evaluation_result may not preserve all request data (e.g.,
    agent_data turns with user messages).
    """
    rubric_map = _build_rubric_description_map(eval_result)
    scenario_list = _build_scenario_preview_list(eval_result)
    logger.debug(
        "Enriching loss response: %d scenarios extracted, %d rubric" " descriptions",
        sum(1 for s in scenario_list if s),
        len(rubric_map),
    )
    for result in response.results or []:
        for cluster in result.clusters or []:
            for example in cluster.examples or []:
                if example.evaluation_result is None:
                    example.evaluation_result = {}
                if rubric_map:
                    example.evaluation_result["rubric_descriptions"] = rubric_map
                # Try extracting scenario from the API echo-back first
                if "scenario_preview" not in example.evaluation_result:
                    scenario = _extract_scenario_preview_from_dict(
                        example.evaluation_result
                    )
                    if scenario:
                        example.evaluation_result["scenario_preview"] = scenario
                # Fallback: match against scenarios from original eval_result
                if "scenario_preview" not in example.evaluation_result:
                    if scenario_list:
                        for s in scenario_list:
                            if s:
                                example.evaluation_result["scenario_preview"] = s
                                break


def _poll_operation(
    api_client: BaseApiClient,
    operation: types.GenerateLossClustersOperation,
    poll_interval_seconds: float = 5.0,
) -> types.GenerateLossClustersOperation:
    """Polls a long-running operation until completion.

    Args:
        api_client: The API client to use for polling.
        operation: The initial operation returned from the API call.
        poll_interval_seconds: Time between polls.

    Returns:
        The completed operation.
    """
    if operation.done:
        return operation
    start_time = time.time()
    while True:
        response = api_client.request("get", operation.name, {}, None)
        response_dict = {} if not response.body else json.loads(response.body)
        polled = types.GenerateLossClustersOperation._from_response(
            response=response_dict, kwargs={}
        )
        if polled.done:
            return polled
        elapsed = int(time.time() - start_time)
        logger.info(
            "Loss analysis operation still running... Elapsed time: %d seconds",
            elapsed,
        )
        time.sleep(poll_interval_seconds)


async def _poll_operation_async(
    api_client: BaseApiClient,
    operation: types.GenerateLossClustersOperation,
    poll_interval_seconds: float = 5.0,
) -> types.GenerateLossClustersOperation:
    """Polls a long-running operation until completion (async).

    Args:
        api_client: The API client to use for polling.
        operation: The initial operation returned from the API call.
        poll_interval_seconds: Time between polls.

    Returns:
        The completed operation.
    """
    if operation.done:
        return operation
    start_time = time.time()
    while True:
        response = await api_client.async_request("get", operation.name, {}, None)
        response_dict = {} if not response.body else json.loads(response.body)
        polled = types.GenerateLossClustersOperation._from_response(
            response=response_dict, kwargs={}
        )
        if polled.done:
            return polled
        elapsed = int(time.time() - start_time)
        logger.info(
            "Loss analysis operation still running... Elapsed time: %d seconds",
            elapsed,
        )
        await asyncio.sleep(poll_interval_seconds)


def _validate_dataset_agent_data(
    dataset: types.EvaluationDataset,
    inference_configs: Optional[dict[str, Any]] = None,
) -> None:
    """Validates agent_data in the EvaluationDataset.

    Checks that agent_data matches the expected AgentData type and that
    'agents' are not defined in both the dataset's agent_data and inference_configs.
    """
    has_inference_agent_configs = False
    if inference_configs:
        for cand_config in inference_configs.values():
            if isinstance(cand_config, dict) and cand_config.get("agent_configs"):
                has_inference_agent_configs = True
            elif hasattr(cand_config, "agent_configs") and cand_config.agent_configs:
                has_inference_agent_configs = True

    def _validate_single_agent_data(agent_data_val: Any, identifier: str) -> None:

        if not agent_data_val:
            return

        agent_data_obj = None
        if isinstance(agent_data_val, str):
            try:
                agent_data_val = json.loads(agent_data_val)
                if "error" in agent_data_val:
                    return
                agent_data_obj = types.evals.AgentData.model_validate(agent_data_val)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"{identifier}: 'agent_data' is not valid JSON: {e}"
                ) from e
        elif isinstance(agent_data_val, dict) and "error" in agent_data_val:
            return
        elif isinstance(agent_data_val, dict):
            try:
                agent_data_obj = types.evals.AgentData.model_validate(agent_data_val)
            except Exception as e:
                raise ValueError(
                    f"{identifier}: 'agent_data' "
                    f"is inconsistent with AgentData type: {e}"
                ) from e
        elif isinstance(agent_data_val, types.evals.AgentData):
            agent_data_obj = agent_data_val
        else:
            raise ValueError(
                f"{identifier}: 'agent_data' is inconsistent with AgentData type. "
                f"Got {type(agent_data_val)}"
            )

        if agent_data_obj and agent_data_obj.agents and has_inference_agent_configs:
            raise ValueError(
                f"{identifier}: Cannot provide 'agents' in the dataset's 'agent_data' "
                "and 'agent_configs' in inference_configs at the same time."
            )

    if (
        dataset.eval_dataset_df is not None
        and "agent_data" in dataset.eval_dataset_df.columns
    ):
        for idx, row in dataset.eval_dataset_df.iterrows():
            _validate_single_agent_data(row.get("agent_data"), f"Row {idx}")

    if dataset.eval_cases:
        for idx, eval_case in enumerate(dataset.eval_cases):
            agent_data = None
            if isinstance(eval_case, dict):
                agent_data = eval_case.get("agent_data", None)
            elif hasattr(eval_case, "agent_data"):
                agent_data = eval_case.agent_data
            _validate_single_agent_data(agent_data, f"EvalCase {idx}")
