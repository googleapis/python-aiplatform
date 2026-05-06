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
"""Handlers for computing evaluation metrics."""

import abc
import collections
from concurrent import futures
import json
import logging
import random
import statistics
import time
from typing import Any, Callable, Generic, Optional, TypeVar, Union

from google.genai import errors as genai_errors
from google.genai import _common
from google.genai import types as genai_types
from tqdm import tqdm
from typing_extensions import override

from . import _evals_common
from . import _evals_constant
from . import _evals_utils
from . import evals
from . import types


logger = logging.getLogger(__name__)
_MAX_RETRIES = 5
# HTTP status codes that are safe to retry with backoff.
_RETRYABLE_STATUS_CODES = frozenset(
    {
        408,  # RequestTimeout (DEADLINE_EXCEEDED)
        409,  # Conflict / Aborted (ABORTED)
        429,  # TooManyRequests / ResourceExhausted (RESOURCE_EXHAUSTED)
        499,  # Client Closed Request (CANCELLED)
        500,  # InternalServerError (INTERNAL)
        502,  # BadGateway
        503,  # ServiceUnavailable (UNAVAILABLE)
        504,  # GatewayTimeout (DEADLINE_EXCEEDED)
    }
)

R = TypeVar("R")
T = TypeVar("T", types.Metric, types.MetricSource, types.LLMMetric)


def _call_with_retry(
    fn: Callable[[], R],
    metric_name: str,
) -> R:
    """Calls ``fn()`` with exponential backoff + jitter on retryable errors.

    Retries up to ``_MAX_RETRIES`` times on errors whose HTTP status code is
    in ``_RETRYABLE_STATUS_CODES`` (Aborted, DeadlineExceeded,
    ResourceExhausted, ServiceUnavailable, Cancelled). Non-retryable errors
    are re-raised immediately. If all retries are exhausted the last
    exception is re-raised so the caller can decide how to handle it.

    Args:
        fn: A zero-argument callable that performs the API call.
        metric_name: Name of the metric, used for log messages.

    Returns:
        The return value of ``fn()``.

    Raises:
        genai_errors.APIError: If all retries are exhausted or the error is
            not retryable.
    """
    for attempt in range(_MAX_RETRIES):
        try:
            return fn()
        except genai_errors.APIError as e:
            if e.code in _RETRYABLE_STATUS_CODES:
                backoff = 2**attempt + random.uniform(0, 1)
                logger.warning(
                    "Retryable error (code=%s) on attempt %d/%d for metric"
                    " '%s': %s. Retrying in %.1f seconds...",
                    e.code,
                    attempt + 1,
                    _MAX_RETRIES,
                    metric_name,
                    e,
                    backoff,
                )
                if attempt == _MAX_RETRIES - 1:
                    raise
                time.sleep(backoff)
            else:
                raise
    raise genai_errors.APIError(
        code=504, response_json={"message": "Retries exhausted"}
    )


def _has_tool_call(events: Optional[list[Any]]) -> bool:
    """Checks if any event in events has a function call."""
    if not events:
        return False
    for event in events:
        if getattr(event, "content", None) and getattr(event.content, "parts", None):
            for part in event.content.parts:
                if hasattr(part, "function_call") and part.function_call:
                    return True
    return False


def _extract_text_from_content(
    content: Optional[genai_types.Content], warn_property: str = "text"
) -> Optional[str]:
    """Extracts and concatenates all text parts from a Content object."""
    if not content or not content.parts:
        return None

    text_accumulator = ""
    any_text_part_found = False
    non_text_part_names = []

    for part_obj in content.parts:
        part_dump = part_obj.model_dump(exclude={"text", "thought"})
        for field_name, field_value in part_dump.items():
            if field_value is not None:
                if field_name not in non_text_part_names:
                    non_text_part_names.append(field_name)

        if isinstance(part_obj.text, str):
            if (
                hasattr(part_obj, "thought")
                and isinstance(part_obj.thought, bool)
                and part_obj.thought
            ):
                continue
            any_text_part_found = True
            text_accumulator += part_obj.text

    if non_text_part_names and any_text_part_found:
        logger.warning(
            "Warning: content contains non-text parts: %s. Returning"
            " concatenated %s result from text parts. Inspect individual parts"
            " for full content.",
            non_text_part_names,
            warn_property,
        )
    return text_accumulator if any_text_part_found else None


def _get_prompt_from_eval_case(
    eval_case: types.EvalCase,
) -> Optional[genai_types.Content]:
    """Extracts prompt content from eval_case.prompt or starting_prompt."""
    if eval_case.prompt:
        return eval_case.prompt

    user_scenario = getattr(eval_case, "user_scenario", None)
    if user_scenario and user_scenario.starting_prompt:
        return genai_types.Content(
            parts=[genai_types.Part(text=user_scenario.starting_prompt)]
        )

    return None


def _get_response_from_eval_case(
    eval_case: types.EvalCase, response_index: int, metric_name: str
) -> Optional[genai_types.Content]:
    """Extracts response content from eval_case.responses."""
    response_content = None
    if eval_case.responses and response_index < len(eval_case.responses):
        response_content = eval_case.responses[response_index].response

    return response_content


def _value_to_content_list(value: Any) -> list[genai_types.Content]:
    """Converts a value to a list of Content objects."""
    if isinstance(value, genai_types.Content):
        return [value]
    if isinstance(value, types.ResponseCandidate):
        return [value.response] if value.response else []
    if isinstance(value, list) and value:
        if isinstance(value[0], genai_types.Content):
            return value
        if isinstance(value[0], types.evals.Message):
            history_texts = []
            for msg_obj in value:
                msg_text = _extract_text_from_content(msg_obj.content)
                if msg_text:
                    role = msg_obj.content.role or msg_obj.author or "user"
                    history_texts.append(f"{role}: {msg_text}")
            return [
                genai_types.Content(
                    parts=[genai_types.Part(text="\n".join(history_texts))]
                )
            ]
        return [genai_types.Content(parts=[genai_types.Part(text=json.dumps(value))])]
    if isinstance(value, dict):
        return [genai_types.Content(parts=[genai_types.Part(text=json.dumps(value))])]
    return [genai_types.Content(parts=[genai_types.Part(text=str(value))])]


def _get_autorater_config(metric: types.Metric) -> dict[str, Any]:
    """Extracts autorater config settings from a metric."""
    autorater_config: dict[str, Any] = {}
    if metric.judge_model:
        autorater_config["autorater_model"] = metric.judge_model
    if metric.judge_model_generation_config:
        autorater_config["generation_config"] = metric.judge_model_generation_config
    if metric.judge_model_sampling_count:
        autorater_config["sampling_count"] = metric.judge_model_sampling_count
    return autorater_config


def _default_aggregate_scores(
    metric_name: str,
    eval_case_metric_results: list[types.EvalCaseMetricResult],
    calculate_pass_rate: bool = False,
) -> types.AggregatedMetricResult:
    """Default aggregation logic using mean and standard deviation."""
    scores = []
    num_error = 0
    num_valid = 0
    num_passing = 0

    for result in eval_case_metric_results:
        if result.error_message is None and result.score is not None:
            try:
                score = float(result.score)
                scores.append(score)
                num_valid += 1
                if calculate_pass_rate and score == 1.0:
                    num_passing += 1
            except (ValueError, TypeError):
                logger.warning(
                    "Could not convert score '%s' to float for metric '%s' during"
                    " default aggregation. Counting as error.",
                    result.score,
                    metric_name,
                )
                num_error += 1
        else:
            num_error += 1

    mean_score = None
    stdev_score = None
    pass_rate = None

    if num_valid > 0:
        try:
            mean_score = statistics.mean(scores)
        except statistics.StatisticsError as e:
            logger.warning("Could not calculate mean for %s: %s", metric_name, e)
        if calculate_pass_rate:
            pass_rate = num_passing / num_valid

    if num_valid > 1:
        try:
            stdev_score = statistics.stdev(scores)
        except statistics.StatisticsError as e:
            logger.warning("Could not calculate stdev for %s: %s", metric_name, e)

    return types.AggregatedMetricResult(
        metric_name=metric_name,
        num_cases_total=len(eval_case_metric_results),
        num_cases_valid=num_valid,
        num_cases_error=num_error,
        mean_score=mean_score,
        stdev_score=stdev_score,
        pass_rate=pass_rate if calculate_pass_rate else None,
    )


class MetricHandler(abc.ABC, Generic[T]):
    """Abstract base class for metric handlers."""

    def __init__(self, module: "evals.Evals", metric: T):
        self.module = module
        self.metric: T = metric

    @property
    @abc.abstractmethod
    def metric_name(self) -> str:
        """Returns the name of the metric polymorphically."""
        raise NotImplementedError()

    @abc.abstractmethod
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case for a specific metric."""
        raise NotImplementedError()

    @abc.abstractmethod
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a specific metric."""
        raise NotImplementedError()


class ComputationMetricHandler(MetricHandler[types.Metric]):
    """Metric handler for computation metrics."""

    SUPPORTED_COMPUTATION_METRICS = frozenset(
        {
            "exact_match",
            "bleu",
            "rouge_1",
            "rouge_l_sum",
            "tool_call_valid",
            "tool_name_match",
            "tool_parameter_key_match",
            "tool_parameter_kv_match",
            # TODO b/423934249 - Add trajectory metrics once they are supported.
        }
    )

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    def __init__(self, module: "evals.Evals", metric: types.Metric):
        super().__init__(module=module, metric=metric)
        if self.metric.name not in self.SUPPORTED_COMPUTATION_METRICS:
            raise ValueError(
                f"Metric '{self.metric.name}' is not supported for computation."
            )

    def _build_request_payload(
        self, eval_case: types.EvalCase, response_index: int
    ) -> dict[str, Any]:
        """Builds the request parameters for evaluate instances."""
        request_payload = {}

        response_content = _get_response_from_eval_case(
            eval_case, response_index, self.metric.name
        )
        prediction_text = _extract_text_from_content(response_content)

        if prediction_text is None:
            raise ValueError(
                f"Response text missing for candidate {response_index} in eval_case"
                f" {eval_case.eval_case_id or 'Unknown ID'}."
            )

        if (
            eval_case.reference is None
            or _extract_text_from_content(eval_case.reference.response) is None
        ):
            raise ValueError(
                "Reference text missing for eval_case"
                f" {eval_case.eval_case_id or 'Unknown ID'}."
            )
        logger.debug("eval_case: %s", eval_case)

        if self.metric.name and self.metric.name.startswith("rouge"):
            request_payload["rouge_input"] = {
                "metric_spec": {
                    "rouge_type": (
                        "rougeLsum" if self.metric.name == "rouge_l_sum" else "rouge1"
                    ),
                },
                "instances": [
                    {
                        "prediction": prediction_text,
                        "reference": _extract_text_from_content(
                            eval_case.reference.response
                        ),
                    }
                ],
            }
        else:
            request_payload[f"{self.metric.name}_input"] = {
                "metric_spec": {},
                "instances": [
                    {
                        "prediction": prediction_text,
                        "reference": _extract_text_from_content(
                            eval_case.reference.response
                        ),
                    }
                ],
            }
        logger.debug("request_payload: %s", request_payload)
        return request_payload

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case for a specific computation metric."""

        metric_name = self.metric.name
        logger.debug(
            "ComputationMetricHandler: Processing '%s' for case: %s",
            metric_name,
            eval_case.model_dump(exclude_none=True),
        )
        response = _call_with_retry(
            lambda: self.module.evaluate_instances(
                metric_config=self._build_request_payload(eval_case, response_index)
            ).model_dump(exclude_none=True),
            metric_name,
        )
        logger.debug("response: %s", response)
        score = None
        for _, result_value in response.items():
            if isinstance(result_value, dict) and result_value:
                for _, metric_value in result_value.items():
                    if isinstance(metric_value, list) and metric_value:
                        score = metric_value[0]["score"]
                        break
        logger.debug("Metric result: %s", score)
        return types.EvalCaseMetricResult(
            metric_name=metric_name,
            score=score,
        )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a computation metric."""
        logger.debug("Aggregating results for computation metric: %s", self.metric.name)
        return _default_aggregate_scores(self.metric.name, eval_case_metric_results)


class TranslationMetricHandler(MetricHandler[types.Metric]):
    """Metric handler for translation metrics."""

    SUPPORTED_TRANSLATION_METRICS = frozenset({"comet", "metricx"})

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    def __init__(self, module: "evals.Evals", metric: types.Metric):
        super().__init__(module=module, metric=metric)

        if self.metric.name not in self.SUPPORTED_TRANSLATION_METRICS:
            raise ValueError(
                f"Metric '{self.metric.name}' is not supported for translation."
            )

    def _build_request_payload(
        self, eval_case: types.EvalCase, response_index: int
    ) -> dict[str, Any]:
        """Builds the request parameters for evaluate instances."""
        request_payload = {}
        metric_input_name = f"{self.metric.name}_input"
        version = None
        if hasattr(self.metric, "version"):
            version = self.metric.version
        elif self.metric.name == "comet":
            version = "COMET_22_SRC_REF"
        elif self.metric.name == "metricx":
            version = "METRICX_24_SRC_REF"

        source_language = None
        target_language = None
        if hasattr(self.metric, "source_language"):
            source_language = self.metric.source_language
        if hasattr(self.metric, "target_language"):
            target_language = self.metric.target_language

        response_content = _get_response_from_eval_case(
            eval_case, response_index, self.metric.name
        )
        prediction_text = _extract_text_from_content(response_content)
        prompt_text = _extract_text_from_content(_get_prompt_from_eval_case(eval_case))

        if prediction_text is None:
            raise ValueError(
                f"Response text missing for candidate {response_index} in eval_case"
                f" {eval_case.eval_case_id or 'Unknown ID'}."
            )

        if (
            eval_case.reference is None
            or _extract_text_from_content(eval_case.reference.response) is None
        ):
            raise ValueError(
                "Reference text missing for eval_case"
                f" {eval_case.eval_case_id or 'Unknown ID'}."
            )
        if prompt_text is None:
            raise ValueError(
                "Prompt text (source for translation) missing for eval_case"
                f" {eval_case.eval_case_id or 'Unknown ID'}."
            )

        request_payload[metric_input_name] = {
            "metric_spec": {
                "version": version,
                "source_language": source_language,
                "target_language": target_language,
            },
            "instance": {
                "prediction": prediction_text,
                "reference": _extract_text_from_content(eval_case.reference.response),
                "source": prompt_text,
            },
        }
        return request_payload

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case for a specific translation metric."""
        metric_name = self.metric.name
        logger.debug(
            "TranslationMetricHandler: Processing '%s' for case: %s",
            metric_name,
            eval_case,
        )
        api_response = _call_with_retry(
            lambda: self.module.evaluate_instances(
                metric_config=self._build_request_payload(eval_case, response_index)
            ),
            metric_name,
        )
        logger.debug("API Response: %s", api_response)

        score = None
        error_message = None

        try:
            if metric_name == "comet":
                if api_response and api_response.comet_result:
                    score = api_response.comet_result.score
                else:
                    logger.warning(
                        "Comet result missing in API response for metric '%s'."
                        " API response: %s",
                        metric_name,
                        (
                            api_response.model_dump_json(exclude_none=True)
                            if api_response
                            else "None"
                        ),
                    )
            elif metric_name == "metricx":
                if api_response and api_response.metricx_result:
                    score = api_response.metricx_result.score
                else:
                    logger.warning(
                        "MetricX result missing in API response for metric '%s'."
                        " API response: %s",
                        metric_name,
                        (
                            api_response.model_dump_json(exclude_none=True)
                            if api_response
                            else "None"
                        ),
                    )
            if score is None and not error_message:
                logger.warning(
                    "Score could not be extracted for translation metric '%s'."
                    " API response: %s",
                    metric_name,
                    (
                        api_response.model_dump_json(exclude_none=True)
                        if api_response
                        else "None"
                    ),
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error processing/extracting score for translation metric '%s': %s."
                " API response: %s",
                metric_name,
                e,
                (
                    api_response.model_dump_json(exclude_none=True)
                    if api_response
                    else "None"
                ),
                exc_info=True,
            )
            error_message = f"Error extracting score: {e}"

        return types.EvalCaseMetricResult(
            metric_name=metric_name,
            score=score,
            error_message=error_message,
        )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a translation metric."""
        logger.debug("Aggregating results for translation metric: %s", self.metric.name)
        return _default_aggregate_scores(self.metric.name, eval_case_metric_results)


def _content_to_instance_data(
    content: Optional[genai_types.Content],
) -> Optional[types.evals.InstanceData]:
    """Converts a genai_types.Content object to a types.InstanceData object."""
    if not content:
        return None
    return types.evals.InstanceData(
        contents=types.evals.InstanceDataContents(contents=[content])
    )


def _eval_case_to_agent_data(
    eval_case: types.EvalCase,
    prompt_content: Optional[genai_types.Content] = None,
    response_content: Optional[genai_types.Content] = None,
) -> Optional[types.evals.AgentData]:
    """Converts an EvalCase object to a single turn AgentData object.

    If `eval_case.agent_data` is provided, it is returned directly, and
    `prompt_content` and `response_content` are ignored.
    """
    if getattr(eval_case, "agent_data", None):
        return eval_case.agent_data

    if (
        not eval_case.agent_info
        and not eval_case.intermediate_events
        and not prompt_content
        and not response_content
    ):
        return None

    agents_map = eval_case.agent_info.agents if eval_case.agent_info else None
    events = []
    if prompt_content:
        events.append(types.evals.AgentEvent(author="user", content=prompt_content))

    if eval_case.intermediate_events:
        for event in eval_case.intermediate_events:
            events.append(
                types.evals.AgentEvent(
                    author=event.author,
                    content=event.content,
                    event_time=event.creation_timestamp,
                )
            )

    if response_content:
        events.append(types.evals.AgentEvent(author="model", content=response_content))

    turns = (
        [types.evals.ConversationTurn(turn_index=0, turn_id="turn_0", events=events)]
        if events
        else None
    )
    return types.evals.AgentData(agents=agents_map, turns=turns)


def _build_evaluation_instance(
    eval_case: types.EvalCase,
    response_content: Optional[genai_types.Content],
    prompt_instance_data: Optional[types.evals.InstanceData] = None,
    prompt_template: Optional[str] = None,
) -> types.EvaluationInstance:
    """Builds a unified EvaluationInstance. Multi-turn logic is handled by the caller."""
    extracted_prompt = _get_prompt_from_eval_case(eval_case)

    # 1. Use caller-provided prompt data (multi-turn) or default to simple content
    if prompt_instance_data is None:
        prompt_instance_data = _content_to_instance_data(extracted_prompt)

    # 2. Collect placeholders for other_data
    other_data_map: dict[str, Any] = {}
    if hasattr(eval_case, "context") and eval_case.context:
        if isinstance(eval_case.context, str):
            other_data_map["context"] = types.evals.InstanceData(text=eval_case.context)
        elif isinstance(eval_case.context, genai_types.Content):
            other_data_map["context"] = _content_to_instance_data(eval_case.context)

    # 3. Extract custom variables from LLMMetric templates
    if prompt_template:
        template_vars = types.PromptTemplate(text=prompt_template).variables
        standard_fields = {"prompt", "response", "reference", "context", "agent_data"}
        for full_path in template_vars:
            # Extract the root variable (e.g. 'metadata' from 'metadata.user_id')
            root_var = full_path.split(".")[0].split("[")[0]

            if root_var not in standard_fields and hasattr(eval_case, root_var):
                val = getattr(eval_case, root_var)
                # Add the root object to other_data so the backend can traverse it
                other_data_map[root_var] = types.evals.InstanceData(
                    contents=types.evals.InstanceDataContents(
                        contents=_value_to_content_list(val)
                    )
                )

    return types.EvaluationInstance(
        prompt=prompt_instance_data,
        response=_content_to_instance_data(response_content),
        reference=(
            _content_to_instance_data(eval_case.reference.response)
            if eval_case.reference
            else None
        ),
        rubric_groups=eval_case.rubric_groups,
        other_data=(
            types.MapInstance(map_instance=other_data_map) if other_data_map else None
        ),
        agent_data=_eval_case_to_agent_data(
            eval_case, extracted_prompt, response_content
        ),
    )


class LLMMetricHandler(MetricHandler[types.LLMMetric]):
    """Metric handler for LLM metrics."""

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    def __init__(self, module: "evals.Evals", metric: types.LLMMetric):
        super().__init__(module=module, metric=metric)

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case using the unified backend interface."""
        try:
            response_content = _get_response_from_eval_case(
                eval_case, response_index, self.metric_name
            )
            if not response_content:
                raise ValueError(
                    f"Response content missing for candidate {response_index}."
                )

            instance = _build_evaluation_instance(
                eval_case, response_content, prompt_template=self.metric.prompt_template
            )
            api_response = _call_with_retry(
                lambda: self.module._evaluate_instances(
                    metrics=[self.metric],
                    instance=instance,
                ),
                self.metric_name,
            )

            if api_response and api_response.metric_results:
                result = api_response.metric_results[0]
                error_msg = None
                if result.error and getattr(result.error, "code"):
                    error_msg = f"Error in metric result: {result.error}"

                return types.EvalCaseMetricResult(
                    metric_name=self.metric_name,
                    score=result.score,
                    explanation=result.explanation,
                    rubric_verdicts=result.rubric_verdicts,
                    error_message=error_msg,
                )
            else:
                return types.EvalCaseMetricResult(
                    metric_name=self.metric_name,
                    error_message="Metric results missing in API response.",
                )

        except Exception as e:
            logger.error(
                "Error processing metric %s for case %s.",
                self.metric_name,
                eval_case.eval_case_id,
                exc_info=True,
            )
            return types.EvalCaseMetricResult(
                metric_name=self.metric_name, error_message=str(e)
            )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a LLM metric."""
        if self.metric.aggregate_summary_fn and callable(
            self.metric.aggregate_summary_fn
        ):
            logger.info(
                "Using custom aggregate_summary_fn for metric '%s'", self.metric.name
            )
            try:
                custom_summary_dict = self.metric.aggregate_summary_fn(
                    eval_case_metric_results
                )
                if not isinstance(custom_summary_dict, dict):
                    raise TypeError("aggregate_summary_fn must return a dictionary.")

                num_cases_total = len(eval_case_metric_results)
                num_cases_error = len(
                    [
                        result
                        for result in eval_case_metric_results
                        if result.error_message is not None
                    ]
                )
                num_cases_valid = num_cases_total - num_cases_error
                required_fields = {
                    "num_cases_total": num_cases_total,
                    "num_cases_error": num_cases_error,
                    "num_cases_valid": num_cases_valid,
                }
                final_summary_dict = {**required_fields, **custom_summary_dict}

                return types.AggregatedMetricResult(
                    metric_name=self.metric.name,
                    **final_summary_dict,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Error executing custom aggregate_summary_fn for metric '%s': %s."
                    " Falling back to default aggregation.",
                    self.metric.name,
                    e,
                    exc_info=True,
                )
                return _default_aggregate_scores(
                    self.metric.name, eval_case_metric_results
                )
        else:
            logger.debug(
                "Using default aggregation for LLM metric '%s'", self.metric.name
            )
            return _default_aggregate_scores(self.metric.name, eval_case_metric_results)


class CustomMetricHandler(MetricHandler[types.Metric]):
    """Metric handler for custom metrics."""

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    def __init__(self, module: "evals.Evals", metric: types.Metric):
        super().__init__(module=module, metric=metric)

        if not self.metric.custom_function:
            raise ValueError(
                f"CustomMetricHandler for '{self.metric.name}' needs "
                " Metric.custom_function to be set."
            )
        if not isinstance(self.metric.custom_function, Callable):
            raise ValueError(
                f"CustomMetricHandler for '{self.metric.name}' needs "
                " Metric.custom_function to be a callable function."
            )

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case for a custom metric."""
        metric_name = self.metric.name
        logger.debug(
            "CustomMetricHandler: Processing '%s' for case: %s",
            metric_name,
            eval_case.model_dump(exclude_none=True),
        )

        try:
            response_content = _get_response_from_eval_case(
                eval_case, response_index, metric_name
            )
        except ValueError as e:
            return types.EvalCaseMetricResult(
                metric_name=metric_name,
                error_message=str(e),
            )

        if not response_content:
            return types.EvalCaseMetricResult(
                metric_name=metric_name,
                error_message=(
                    f"No response found for candidate {response_index} in EvalCase"
                    f" {eval_case.eval_case_id}."
                ),
            )

        instance_for_custom_fn = eval_case.model_dump(
            exclude={"responses"}, mode="json", exclude_none=True
        )
        instance_for_custom_fn["response"] = response_content.model_dump(
            mode="json", exclude_none=True
        )
        extracted_prompt = _get_prompt_from_eval_case(eval_case)
        if extracted_prompt:
            instance_for_custom_fn["prompt"] = extracted_prompt.model_dump(
                mode="json", exclude_none=True
            )

        error_msg = None
        score = None
        explanation = None
        try:
            if self.metric.custom_function and callable(self.metric.custom_function):
                custom_function_result = self.metric.custom_function(
                    instance_for_custom_fn
                )

                if isinstance(custom_function_result, types.EvalCaseMetricResult):
                    return custom_function_result
                elif (
                    isinstance(custom_function_result, dict)
                    and "score" in custom_function_result
                ):
                    score = custom_function_result["score"]
                    explanation = custom_function_result.get("explanation", None)
                elif isinstance(custom_function_result, (float, int)):
                    score = custom_function_result
                    explanation = None
                else:
                    error_msg = (
                        f"CustomFunctionError({self.metric.custom_function}): Returned"
                        f" unexpected type {type(custom_function_result)}"
                    )

        except Exception as e:  # pylint: disable=broad-exception-caught
            if self.metric.custom_function and hasattr(
                self.metric.custom_function, "__name__"
            ):
                custom_function_name = self.metric.custom_function.__name__
            else:
                custom_function_name = "unknown_custom_function"
            error_msg = f"CustomFunctionError({custom_function_name}): {e}"
            score = None
            explanation = None

        return types.EvalCaseMetricResult(
            metric_name=self.metric.name,
            score=score,
            explanation=explanation,
            error_message=error_msg,
        )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a custom metric."""
        logger.debug("Aggregating results for custom metric: %s", self.metric.name)
        return _default_aggregate_scores(self.metric.name, eval_case_metric_results)


class PredefinedMetricHandler(MetricHandler[types.Metric]):
    """Metric handler for predefined metrics."""

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    def __init__(self, module: "evals.Evals", metric: types.Metric):
        super().__init__(module=module, metric=metric)
        if self.metric.name not in _evals_constant.SUPPORTED_PREDEFINED_METRICS:
            raise ValueError(
                f"Metric '{self.metric.name}' is not a supported predefined metric."
            )

    def _build_request_payload(
        self, eval_case: types.EvalCase, response_index: int
    ) -> dict[str, Any]:
        """Builds the request parameters for evaluate instances request."""
        response_content = _get_response_from_eval_case(
            eval_case, response_index, self.metric.name
        )

        if not response_content and not getattr(eval_case, "agent_data", None):
            raise ValueError(
                f"Response content missing for candidate {response_index}."
            )

        if self.metric.name == "tool_use_quality_v1":
            has_tool_call = _has_tool_call(eval_case.intermediate_events)

            # Check agent_data for tool calls if intermediate_events is empty
            agent_data = getattr(eval_case, "agent_data", None)
            if not has_tool_call and agent_data:
                for turn in agent_data.turns or []:
                    if _has_tool_call(turn.events):
                        has_tool_call = True
                        break

            if not has_tool_call:
                logger.warning(
                    "Metric 'tool_use_quality_v1' requires tool usage in "
                    "'intermediate_events' or 'agent_data', but no tool usage was found for case %s.",
                    eval_case.eval_case_id,
                )

        extracted_prompt = _get_prompt_from_eval_case(eval_case)
        prompt_instance_data = None
        if self.metric.name and self.metric.name.startswith("multi_turn"):
            prompt_contents = [
                msg.content for msg in (eval_case.conversation_history or [])
            ]
            if extracted_prompt:
                prompt_contents.append(extracted_prompt)
            prompt_instance_data = types.evals.InstanceData(
                contents=types.evals.InstanceDataContents(contents=prompt_contents)
            )

        instance_payload = _build_evaluation_instance(
            eval_case=eval_case,
            response_content=response_content,
            prompt_instance_data=prompt_instance_data,
        )

        request_payload: dict[str, Any] = {
            "instance": instance_payload,
        }

        autorater_config = _get_autorater_config(self.metric)
        if autorater_config:
            request_payload["autorater_config"] = genai_types.AutoraterConfig(
                **autorater_config
            )
        return request_payload

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case for a specific predefined metric."""
        metric_name = self.metric.name
        try:
            payload = self._build_request_payload(eval_case, response_index)
            api_response = _call_with_retry(
                lambda: self.module._evaluate_instances(
                    metrics=[self.metric],
                    instance=payload.get("instance"),
                    autorater_config=payload.get("autorater_config"),
                ),
                metric_name,
            )

            if (
                api_response
                and hasattr(api_response, "metric_results")
                and api_response.metric_results
            ):
                result_data = api_response.metric_results[0]

                error_message = None
                if result_data.error and getattr(result_data.error, "code"):
                    error_message = f"Error in metric result: {result_data.error}"
                return types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    score=result_data.score,
                    explanation=result_data.explanation,
                    rubric_verdicts=result_data.rubric_verdicts,
                    error_message=error_message,
                )
            else:
                logger.error(
                    "Metric results missing in API response for predefined metric '%s'."
                    " API response: %s",
                    metric_name,
                    (
                        api_response.model_dump_json(exclude_none=True)
                        if api_response
                        else "None"
                    ),
                )
                return types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    error_message="Metric results missing in API response.",
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error processing metric %s for case %s: %s",
                metric_name,
                eval_case.eval_case_id,
                e,
                exc_info=True,
            )
            return types.EvalCaseMetricResult(
                metric_name=metric_name, error_message=str(e)
            )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a predefined metric."""
        logger.debug("Aggregating results for predefined metric: %s", self.metric.name)
        return _default_aggregate_scores(
            self.metric.name, eval_case_metric_results, calculate_pass_rate=True
        )


class CustomCodeExecutionMetricHandler(MetricHandler[types.Metric]):
    """Metric handler for custom code execution metrics."""

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    def __init__(self, module: "evals.Evals", metric: types.Metric):
        super().__init__(module=module, metric=metric)

        if not self.metric.remote_custom_function and not self.metric.custom_function:
            raise ValueError(
                f"CustomCodeExecutionMetricHandler for '{self.metric.name}' needs "
                " custom function to be set."
            )

    def _build_request_payload(
        self, eval_case: types.EvalCase, response_index: int
    ) -> dict[str, Any]:
        """Builds the request parameters for evaluate instances request."""
        response_content = _get_response_from_eval_case(
            eval_case, response_index, self.metric.name
        )

        if not response_content and not getattr(eval_case, "agent_data", None):
            raise ValueError(
                f"Response content missing for candidate {response_index}."
            )

        reference_instance_data = None
        if eval_case.reference:
            reference_instance_data = _content_to_instance_data(
                eval_case.reference.response
            )

        extracted_prompt = _get_prompt_from_eval_case(eval_case)
        prompt_instance_data = _content_to_instance_data(extracted_prompt)

        instance_payload = types.EvaluationInstance(
            prompt=prompt_instance_data,
            response=_content_to_instance_data(response_content),
            reference=reference_instance_data,
            agent_data=_eval_case_to_agent_data(eval_case),
        )

        return {
            "instance": instance_payload,
        }

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case for a specific custom code execution metric."""
        metric_name = self.metric.name
        try:
            payload = self._build_request_payload(eval_case, response_index)
            api_response = _call_with_retry(
                lambda: self.module._evaluate_instances(
                    metrics=[self.metric],
                    instance=payload.get("instance"),
                ),
                metric_name,
            )

            if (
                api_response
                and hasattr(api_response, "metric_results")
                and api_response.metric_results
            ):
                result_data = api_response.metric_results[0]

                error_message = None
                if result_data.error and getattr(result_data.error, "code"):
                    error_message = f"Error in metric result: {result_data.error}"
                return types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    score=result_data.score,
                    explanation=result_data.explanation,
                    error_message=error_message,
                )
            else:
                logger.error(
                    "Metric results missing in API response for metric '%s'."
                    " API response: %s",
                    metric_name,
                    (
                        api_response.model_dump_json(exclude_none=True)
                        if api_response
                        else "None"
                    ),
                )
                return types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    error_message="Metric results missing in API response.",
                )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error processing metric %s for case %s",
                metric_name,
                eval_case.eval_case_id,
                exc_info=True,
            )
            return types.EvalCaseMetricResult(
                metric_name=metric_name, error_message=str(e)
            )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a custom code execution metric."""
        logger.debug(
            "Aggregating results for custom code execution metric: %s", self.metric.name
        )
        return _default_aggregate_scores(
            self.metric.name, eval_case_metric_results, calculate_pass_rate=True
        )


class RegisteredMetricHandler(MetricHandler[types.Metric]):
    """Metric handler for registered metrics."""

    def __init__(
        self,
        module: "evals.Evals",
        metric: types.Metric,
    ):
        if isinstance(metric, dict):
            metric = types.MetricSource(**metric)
        super().__init__(module=module, metric=metric)

    def _build_request_payload(
        self, eval_case: types.EvalCase, response_index: int
    ) -> dict[str, Any]:
        """Builds request payload for registered metric by assembling EvaluationInstance."""
        response_content = _get_response_from_eval_case(
            eval_case, response_index, self.metric_name
        )

        if not response_content and not getattr(eval_case, "agent_data", None):
            raise ValueError(
                f"Response content missing for candidate {response_index}."
            )

        reference_instance_data = None
        if eval_case.reference:
            reference_instance_data = _content_to_instance_data(
                eval_case.reference.response
            )

        extracted_prompt = _get_prompt_from_eval_case(eval_case)
        prompt_instance_data = _content_to_instance_data(extracted_prompt)

        instance_payload = types.EvaluationInstance(
            prompt=prompt_instance_data,
            response=_content_to_instance_data(response_content),
            reference=reference_instance_data,
            rubric_groups=eval_case.rubric_groups,
            agent_data=_eval_case_to_agent_data(eval_case),
        )

        request_payload = {
            "instance": instance_payload,
        }
        return request_payload

    @property
    def metric_name(self) -> str:
        return self.metric.name or "unknown_metric"

    @override
    def get_metric_result(
        self, eval_case: types.EvalCase, response_index: int
    ) -> types.EvalCaseMetricResult:
        """Processes a single evaluation case using a MetricSource reference."""
        metric_name = self.metric_name
        metric_source = types.MetricSource(
            metric_resource_name=self.metric.metric_resource_name
        )

        try:
            payload = self._build_request_payload(eval_case, response_index)
            api_response = _call_with_retry(
                lambda: self.module._evaluate_instances(
                    metric_sources=[metric_source],
                    instance=payload.get("instance"),
                    autorater_config=payload.get("autorater_config"),
                ),
                metric_name,
            )

            if api_response and api_response.metric_results:
                result_data = api_response.metric_results[0]
                error_message = None
                if result_data.error and getattr(result_data.error, "code"):
                    error_message = f"Error in metric result: {result_data.error}"
                return types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    score=result_data.score,
                    explanation=result_data.explanation,
                    rubric_verdicts=result_data.rubric_verdicts,
                    error_message=error_message,
                )
            else:
                return types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    error_message="Metric results missing in API response.",
                )
        except Exception as e:
            return types.EvalCaseMetricResult(
                metric_name=metric_name, error_message=str(e)
            )

    @override
    def aggregate(
        self, eval_case_metric_results: list[types.EvalCaseMetricResult]
    ) -> types.AggregatedMetricResult:
        """Aggregates the metric results for a registered metric."""
        return _default_aggregate_scores(
            self.metric_name, eval_case_metric_results, calculate_pass_rate=True
        )


_METRIC_HANDLER_MAPPING = [
    (
        lambda m: (
            # Recognize the user-facing class
            isinstance(m, types.CodeExecutionMetric)
            and (hasattr(m, "custom_function") and m.custom_function)
        )
        or (hasattr(m, "remote_custom_function") and m.remote_custom_function)
        # Recognize base Metric objects that have been coerced by Pydantic
        or (
            isinstance(m, types.Metric)
            and isinstance(getattr(m, "custom_function", None), str)
        ),
        CustomCodeExecutionMetricHandler,
    ),
    (
        lambda m: m.custom_function and isinstance(m.custom_function, Callable),
        CustomMetricHandler,
    ),
    (
        lambda m: getattr(m, "metric_resource_name", None) is not None,
        RegisteredMetricHandler,
    ),
    (
        lambda m: m.name in ComputationMetricHandler.SUPPORTED_COMPUTATION_METRICS,
        ComputationMetricHandler,
    ),
    (
        lambda m: m.name in TranslationMetricHandler.SUPPORTED_TRANSLATION_METRICS,
        TranslationMetricHandler,
    ),
    (
        lambda m: m.name in _evals_constant.SUPPORTED_PREDEFINED_METRICS,
        PredefinedMetricHandler,
    ),
    (lambda m: isinstance(m, types.LLMMetric), LLMMetricHandler),
]

MetricHandlerType = TypeVar(
    "MetricHandlerType",
    ComputationMetricHandler,
    TranslationMetricHandler,
    LLMMetricHandler,
    CustomMetricHandler,
    CustomCodeExecutionMetricHandler,
    PredefinedMetricHandler,
)


def get_handler_for_metric(
    module: "evals.Evals", metric: types.Metric
) -> Union[MetricHandlerType, Any]:
    """Returns a metric handler for the given metric."""
    for condition, handler_class in _METRIC_HANDLER_MAPPING:
        if condition(metric):  # type: ignore[no-untyped-call]
            return handler_class(module=module, metric=metric)
    raise ValueError(f"Unsupported metric: {metric.name}")


def calculate_win_rates(eval_result: types.EvaluationResult) -> dict[str, Any]:
    """Calculates win/tie rates for comparison results."""
    if not eval_result.eval_case_results:
        return {}
    max_models = max(
        (
            len(case.response_candidate_results)
            for case in eval_result.eval_case_results
            if case.response_candidate_results
        ),
        default=0,
    )
    if max_models == 0:
        return {}
    stats: collections.defaultdict[str, dict[str, Any]] = collections.defaultdict(
        lambda: {"wins": [0] * max_models, "ties": 0, "valid_comparisons": 0}
    )
    for case in eval_result.eval_case_results:
        if not case.response_candidate_results:
            continue
        scores_by_metric = collections.defaultdict(list)
        for idx, candidate in enumerate(case.response_candidate_results):
            for name, res in (
                candidate.metric_results.items() if candidate.metric_results else {}
            ):
                if res.score is not None:
                    scores_by_metric[name].append({"score": res.score, "cand_idx": idx})
        for name, scores in scores_by_metric.items():
            if not scores:
                continue
            stats[name]["valid_comparisons"] += 1
            max_score = max(s["score"] for s in scores)
            winners = [s["cand_idx"] for s in scores if s["score"] == max_score]
            if len(winners) == 1:
                stats[name]["wins"][winners[0]] += 1
            else:
                stats[name]["ties"] += 1
    win_rates = {}
    for name, metric_stats in stats.items():
        if metric_stats["valid_comparisons"] > 0:
            win_rates[name] = {
                "win_rates": [
                    w / metric_stats["valid_comparisons"] for w in metric_stats["wins"]
                ],
                "tie_rate": metric_stats["ties"] / metric_stats["valid_comparisons"],
            }
    return win_rates


def _aggregate_metric_results(
    metric_handlers: list[MetricHandler[Any]],
    eval_case_results: list[types.EvalCaseResult],
) -> list[types.AggregatedMetricResult]:
    """Aggregates results by calling the aggregate method of each handler."""
    aggregated_metric_results = []
    logger.info("Aggregating results per metric...")
    for handler in metric_handlers:
        metric_name = handler.metric_name
        results_for_this_metric: list[types.EvalCaseMetricResult] = []
        for case_result in eval_case_results:
            if case_result.response_candidate_results:
                for response_candidate_res in case_result.response_candidate_results:
                    if (
                        response_candidate_res.metric_results
                        and metric_name in response_candidate_res.metric_results
                        and isinstance(metric_name, str)
                    ):
                        results_for_this_metric.append(
                            response_candidate_res.metric_results[metric_name]
                        )
        if not results_for_this_metric:
            logger.warning(
                "No results found for metric '%s' to aggregate.", metric_name
            )
            continue

        try:
            summary = handler.aggregate(results_for_this_metric)
            aggregated_metric_results.append(summary)
        except NotImplementedError:
            logger.warning(
                "Aggregation not implemented for metric handler: %s (metric: '%s')."
                " Skipping summary.",
                type(handler).__name__,
                metric_name,
            )
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error(
                "Error during aggregation for metric '%s' using handler %s: %s",
                metric_name,
                type(handler).__name__,
                e,
                exc_info=True,
            )
            aggregated_metric_results.append(
                types.AggregatedMetricResult(
                    metric_name=metric_name,
                    num_cases_total=len(results_for_this_metric),
                    num_cases_valid=0,
                    num_cases_error=len(results_for_this_metric),
                    mean_score=None,
                    stdev_score=None,
                )
            )
    logger.debug("Finished aggregation, returning: %s", aggregated_metric_results)
    return aggregated_metric_results


class EvaluationRunConfig(_common.BaseModel):
    """Configuration for an evaluation run."""

    evals_module: Any
    """The module to be used for the evaluation run."""
    dataset: types.EvaluationDataset
    """The dataset to be used for the evaluation run."""
    metrics: list[types.Metric]
    """The list of metrics to be used for the evaluation run."""
    num_response_candidates: int
    """The number of response candidates for the evaluation run."""


def _rate_limited_get_metric_result(
    rate_limiter: _evals_utils.RateLimiter,
    handler: MetricHandler[Any],
    eval_case: types.EvalCase,
    response_index: int,
) -> types.EvalCaseMetricResult:
    """Wraps a handler's get_metric_result with rate limiting."""
    rate_limiter.sleep_and_advance()
    return handler.get_metric_result(eval_case, response_index)


def compute_metrics_and_aggregate(
    evaluation_run_config: EvaluationRunConfig,
    evaluation_service_qps: Optional[float] = None,
) -> types.EvaluationResult:
    """Computes metrics and aggregates them for a given evaluation run config.

    Args:
        evaluation_run_config: The configuration for the evaluation run.
        evaluation_service_qps: Optional QPS limit for the evaluation service.
            Defaults to _DEFAULT_EVAL_SERVICE_QPS (10). Users with higher
            quotas can increase this value.
    """
    metric_handlers = []
    all_futures = []
    results_by_case_response_metric: collections.defaultdict[
        Any, collections.defaultdict[Any, dict[Any, Any]]
    ] = collections.defaultdict(lambda: collections.defaultdict(dict))
    submission_errors = []
    execution_errors = []
    case_indices_with_errors = set()

    if evaluation_service_qps is not None and evaluation_service_qps <= 0:
        raise ValueError("evaluation_service_qps must be a positive number.")
    qps = evaluation_service_qps or _evals_utils._DEFAULT_EVAL_SERVICE_QPS
    rate_limiter = _evals_utils.RateLimiter(rate=qps)
    logger.info("Rate limiting evaluation service requests to %.1f QPS.", qps)

    for eval_metric in evaluation_run_config.metrics:
        metric_handlers.append(
            get_handler_for_metric(evaluation_run_config.evals_module, eval_metric)
        )

    eval_case_count = len(evaluation_run_config.dataset.eval_cases)
    logger.info("Total number of evaluation cases: %d", eval_case_count)
    logger.info(
        "Number of response candidates: %d",
        evaluation_run_config.num_response_candidates,
    )
    total_metric_computations = (
        eval_case_count
        * len(metric_handlers)
        * evaluation_run_config.num_response_candidates
    )
    logger.info("Total number of metric computations: %d", total_metric_computations)

    with tqdm(
        total=total_metric_computations,
        desc="Computing Metrics for Evaluation Dataset",
    ) as pbar:
        with futures.ThreadPoolExecutor(
            max_workers=_evals_common.MAX_WORKERS
        ) as executor:
            for metric_handler_instance in metric_handlers:
                for eval_case_index, eval_case in enumerate(
                    evaluation_run_config.dataset.eval_cases
                ):
                    num_responses = (
                        len(eval_case.responses) if eval_case.responses else 0
                    )
                    if num_responses == 0 and getattr(eval_case, "agent_data", None):
                        num_responses = 1

                    actual_num_candidates_for_case = min(
                        evaluation_run_config.num_response_candidates,
                        num_responses,
                    )
                    for response_index in range(actual_num_candidates_for_case):
                        try:
                            future = executor.submit(
                                _rate_limited_get_metric_result,
                                rate_limiter,
                                metric_handler_instance,
                                eval_case,
                                response_index,
                            )
                            future.add_done_callback(lambda _: pbar.update(1))
                            logger.debug(
                                "Submitting metric computation for case %d, "
                                "response %d for metric %s.",
                                eval_case_index,
                                response_index,
                                metric_handler_instance.metric_name,
                            )
                            all_futures.append(
                                (
                                    future,
                                    metric_handler_instance.metric_name,
                                    eval_case_index,
                                    response_index,
                                )
                            )
                        except Exception as e:  # pylint: disable=broad-exception-caught
                            logger.error(
                                "Error submitting metric computation for case %d, "
                                "response %d for metric %s: %s",
                                eval_case_index,
                                response_index,
                                metric_handler_instance.metric_name,
                                e,
                                exc_info=True,
                            )
                            submission_errors.append(
                                (
                                    metric_handler_instance.metric_name,
                                    eval_case_index,
                                    response_index,
                                    f"Error: {e}",
                                )
                            )
                            error_result = types.EvalCaseMetricResult(
                                metric_name=metric_handler_instance.metric_name,
                                error_message=f"Submission Error: {e}",
                            )
                            results_by_case_response_metric[eval_case_index][
                                response_index
                            ][metric_handler_instance.metric_name] = error_result
                            case_indices_with_errors.add(eval_case_index)
                            pbar.update(1)

        for future, metric_name, eval_case_index, response_index in all_futures:
            try:
                eval_case_metric_result = future.result()
                logger.debug(
                    "Successfully obtained result for metric '%s', case %d, response"
                    " %d: %s.",
                    metric_name,
                    eval_case_index,
                    response_index,
                    eval_case_metric_result,
                )
                results_by_case_response_metric[eval_case_index][response_index][
                    metric_name
                ] = eval_case_metric_result
                logger.debug(
                    "Stored result for metric '%s', case %d, response %d.",
                    metric_name,
                    eval_case_index,
                    response_index,
                )
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(
                    "Error executing metric '%s' for case %s, response %s: %s",
                    metric_name,
                    eval_case_index,
                    response_index,
                    e,
                    exc_info=True,
                )
                error_msg = (
                    f"Error executing metric '{metric_name}' for case"
                    f" {eval_case_index}, response {response_index}: {e}"
                )
                execution_errors.append(
                    (
                        metric_name,
                        eval_case_index,
                        response_index,
                        error_msg,
                    )
                )
                case_indices_with_errors.add(eval_case_index)
                error_result = types.EvalCaseMetricResult(
                    metric_name=metric_name,
                    error_message=error_msg,
                )
                results_by_case_response_metric[eval_case_index][response_index][
                    metric_name
                ] = error_result

    final_eval_case_results = []
    sorted_eval_case_indices = sorted(results_by_case_response_metric.keys())
    for eval_case_index in sorted_eval_case_indices:
        per_response_results_for_this_case = results_by_case_response_metric[
            eval_case_index
        ]

        current_response_candidate_results_list = []
        sorted_response_indices = sorted(per_response_results_for_this_case.keys())

        for response_index in sorted_response_indices:
            metric_results_for_this_response = per_response_results_for_this_case[
                response_index
            ]

            response_candidate_result_obj = types.ResponseCandidateResult(
                response_index=response_index,
                metric_results=metric_results_for_this_response,
            )
            current_response_candidate_results_list.append(
                response_candidate_result_obj
            )

        if current_response_candidate_results_list:
            eval_case_result = types.EvalCaseResult(
                eval_case_index=eval_case_index,
                response_candidate_results=current_response_candidate_results_list,
            )
            final_eval_case_results.append(eval_case_result)
        elif eval_case_index in case_indices_with_errors or any(
            err_case_idx == eval_case_index
            for _, err_case_idx, _, _ in submission_errors
        ):
            logger.warning(
                "EvalCase %d had errors but no metric results were"
                " processed into the structure.",
                eval_case_index,
            )
            eval_case_result = types.EvalCaseResult(
                eval_case_index=eval_case_index,
                response_candidate_results=[],
            )
            final_eval_case_results.append(eval_case_result)

    if submission_errors:
        logger.warning("Encountered %d submission errors.", len(submission_errors))
        logger.warning("Submission errors: %s", submission_errors)
    if execution_errors:
        logger.warning("Encountered %d execution errors.", len(execution_errors))
        logger.warning("Execution errors: %s", execution_errors)

    aggregated_metric_results = _aggregate_metric_results(
        metric_handlers, final_eval_case_results
    )
    eval_result = types.EvaluationResult(
        eval_case_results=final_eval_case_results,
        summary_metrics=aggregated_metric_results,
    )
    if evaluation_run_config.num_response_candidates > 1:
        try:
            eval_result.win_rates = calculate_win_rates(eval_result)
        except Exception as e:  # pylint: disable=broad-exception-caught
            logger.error("Error calculating win rates: %s", e, exc_info=True)
    return eval_result
