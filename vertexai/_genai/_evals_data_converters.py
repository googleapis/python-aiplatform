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
"""Dataset converters for evals."""

import abc
import logging
from typing import Any, Optional

from google.genai import _common
from google.genai import types as genai_types
from typing_extensions import override

from . import types


logger = logging.getLogger("vertexai_genai._evals_data_converters")

_PLACEHOLDER_RESPONSE_TEXT = "Error: Missing response for this candidate"


def _create_placeholder_response_candidate(
    text: str = _PLACEHOLDER_RESPONSE_TEXT,
) -> types.ResponseCandidate:
    """Creates a ResponseCandidate with placeholder text."""
    return types.ResponseCandidate(
        response=genai_types.Content(parts=[genai_types.Part(text=text)])
    )


class EvalDatasetSchema(_common.CaseInSensitiveEnum):
    """Represents the schema of an evaluation dataset."""

    GEMINI = "gemini"
    FLATTEN = "flatten"
    UNKNOWN = "unknown"


class _EvalDataConverter(abc.ABC):
    """Abstract base class for dataset converters."""

    @abc.abstractmethod
    def convert(self, raw_data: Any) -> types.EvaluationDataset:
        """Converts a loaded raw dataset into an EvaluationDataset."""
        raise NotImplementedError()


class _GeminiEvalDataConverter(_EvalDataConverter):
    """Converter for dataset in the Gemini format."""

    def _parse_request(
        self, request_data: dict[str, Any]
    ) -> tuple[
        genai_types.Content,
        genai_types.Content,
        list[types.Message],
        types.ResponseCandidate,
    ]:
        """Parses a request from a Gemini dataset."""
        system_instruction = genai_types.Content()
        prompt = genai_types.Content()
        reference = types.ResponseCandidate()
        conversation_history = []

        if "system_instruction" in request_data:
            system_instruction = genai_types.Content.model_validate(
                request_data["system_instruction"]
            )
        for turn_id, content_dict in enumerate(request_data.get("contents", [])):
            if not isinstance(content_dict, dict):
                raise TypeError(
                    f"Expected a dictionary for content at turn {turn_id}, but got"
                    f" {type(content_dict).__name__}: {content_dict}"
                )
            if "parts" not in content_dict:
                raise ValueError(
                    f"Missing 'parts' key in content structure at turn {turn_id}:"
                    f" {content_dict}"
                )
            conversation_history.append(
                types.Message(
                    turn_id=str(turn_id),
                    content=genai_types.Content.model_validate(content_dict),
                )
            )
        if conversation_history:
            last_message = conversation_history.pop()
            if last_message.content and last_message.content.role == "user":
                prompt = last_message.content
            elif last_message.content and last_message.content.role == "model":
                # If the last message is from the model, then it's the reference.
                reference = types.ResponseCandidate(response=last_message.content)
                if conversation_history:  # Ensure there's a previous message
                    second_to_last_message = conversation_history.pop()
                    prompt = second_to_last_message.content
                else:  # If only one model message, prompt is invalid.
                    prompt = genai_types.Content()

        return prompt, system_instruction, conversation_history, reference

    @override
    def convert(self, raw_data: list[dict[str, Any]]) -> types.EvaluationDataset:
        """Converts a list of raw data into an EvaluationDataset."""
        eval_cases = []

        for i, item in enumerate(raw_data):
            eval_case_id = f"gemini_eval_case_{i}"
            request_data = item.get("request", {})
            response_data = item.get("response", {})

            (
                prompt,
                system_instruction,
                conversation_history,
                reference,
            ) = self._parse_request(request_data)

            responses = []
            if isinstance(response_data, str):
                responses.append(
                    types.ResponseCandidate(
                        response=genai_types.Content(
                            parts=[genai_types.Part(text=response_data)]
                        )
                    )
                )
            elif isinstance(response_data, dict):
                try:
                    generate_content_response = (
                        genai_types.GenerateContentResponse.model_validate(
                            response_data
                        )
                    )
                    if generate_content_response.candidates:
                        candidate = generate_content_response.candidates[0]
                        if candidate.content:
                            responses.append(
                                types.ResponseCandidate(
                                    response=genai_types.Content.model_validate(
                                        candidate.content
                                    )
                                )
                            )
                    else:  # Handle cases where there are no candidates.
                        responses.append(_create_placeholder_response_candidate())
                except Exception:
                    # Fallback for dicts that don't match the schema, treat as empty.
                    responses.append(_create_placeholder_response_candidate())
            else:
                # For any other type, treat as an empty/invalid response.
                responses.append(_create_placeholder_response_candidate())

            eval_case = types.EvalCase(
                eval_case_id=eval_case_id,
                prompt=prompt,
                responses=responses,
                reference=reference,
                system_instruction=system_instruction,
                conversation_history=conversation_history,
            )
            eval_cases.append(eval_case)

        return types.EvaluationDataset(eval_cases=eval_cases)


class _FlattenEvalDataConverter(_EvalDataConverter):
    """Converter for datasets in a structured table format."""

    def convert(self, raw_data: list[dict[str, Any]]) -> types.EvaluationDataset:
        """Converts a list of raw data into an EvaluationDataset."""
        eval_cases = []
        for i, item_dict in enumerate(raw_data):
            if not isinstance(item_dict, dict):
                raise TypeError(
                    f"Expected a dictionary for item at index {i}, but got"
                    f" {type(item_dict).__name__}: {item_dict}"
                )
            item = item_dict.copy()
            eval_case_id = f"eval_case_{i}"
            prompt_data = item.pop("prompt", None)
            if not prompt_data:
                prompt_data = item.pop("source", None)

            conversation_history_data = item.pop("history", None)
            response_data = item.pop("response", None)
            reference_data = item.pop("reference", None)
            system_instruction_data = item.pop("instruction", None)

            if not response_data:
                raise ValueError(
                    f"Response is required but missing for {eval_case_id}."
                )
            if not prompt_data:
                raise ValueError(f"Prompt is required but missing for {eval_case_id}.")

            prompt: genai_types.Content
            if isinstance(prompt_data, str):
                prompt = genai_types.Content(parts=[genai_types.Part(text=prompt_data)])
            elif isinstance(prompt_data, dict):
                prompt = genai_types.Content.model_validate(prompt_data)
            elif isinstance(prompt_data, genai_types.Content):
                prompt = prompt_data
            else:
                raise ValueError(
                    f"Invalid prompt type for case {i}: {type(prompt_data)}"
                )

            conversation_history: Optional[list[types.Message]] = None
            if isinstance(conversation_history_data, list):
                conversation_history = [
                    types.Message(
                        turn_id=str(turn_id),
                        content=genai_types.Content.model_validate(content),
                    )
                    for turn_id, content in enumerate(conversation_history_data)
                ]

            responses: list[types.ResponseCandidate]
            if isinstance(response_data, dict):
                responses = [
                    types.ResponseCandidate(
                        response=genai_types.Content.model_validate(response_data)
                    )
                ]
            elif isinstance(response_data, str):
                responses = [
                    types.ResponseCandidate(
                        response=genai_types.Content(
                            parts=[genai_types.Part(text=response_data)]
                        )
                    )
                ]
            elif isinstance(response_data, genai_types.Content):
                responses = [types.ResponseCandidate(response=response_data)]
            else:
                raise ValueError(
                    f"Invalid response type for case {i}: {type(response_data)}"
                )

            reference: Optional[types.ResponseCandidate] = None
            if reference_data:
                if isinstance(reference_data, dict):
                    reference = types.ResponseCandidate(
                        response=genai_types.Content.model_validate(reference_data)
                    )
                elif isinstance(reference_data, str):
                    reference = types.ResponseCandidate(
                        response=genai_types.Content(
                            parts=[genai_types.Part(text=reference_data)]
                        )
                    )
                elif isinstance(reference_data, genai_types.Content):
                    reference = types.ResponseCandidate(response=reference_data)

            system_instruction: Optional[genai_types.Content] = None
            if system_instruction_data:
                if isinstance(system_instruction_data, dict):
                    system_instruction = genai_types.Content.model_validate(
                        system_instruction_data
                    )
                elif isinstance(system_instruction_data, str):
                    system_instruction = genai_types.Content(
                        parts=[genai_types.Part(text=system_instruction_data)]
                    )
                elif isinstance(system_instruction_data, genai_types.Content):
                    system_instruction = system_instruction_data

            eval_case = types.EvalCase(
                eval_case_id=eval_case_id,
                prompt=prompt,
                responses=responses,
                reference=reference,
                conversation_history=conversation_history,
                system_instruction=system_instruction,
                **item,  # Pass remaining columns as extra fields to EvalCase.
                # They can be used for custom metric prompt templates.
            )
            eval_cases.append(eval_case)

        return types.EvaluationDataset(eval_cases=eval_cases)


def auto_detect_dataset_schema(
    raw_dataset: list[dict[str, Any]],
) -> EvalDatasetSchema:
    """Detects the schema of a raw dataset."""
    if not raw_dataset:
        logger.debug("Empty dataset, returning UNKNOWN schema.")
        return EvalDatasetSchema.UNKNOWN

    first_item = raw_dataset[0]
    if not isinstance(first_item, dict):
        logger.warning(
            "First item in dataset is not a dictionary. Cannot determine schema."
        )
        return EvalDatasetSchema.UNKNOWN

    keys = set(first_item.keys())

    request_field = first_item.get("request")
    if isinstance(request_field, dict) and isinstance(
        request_field.get("contents"), list
    ):
        try:
            _GeminiEvalDataConverter().convert([first_item])
            logger.debug(
                "Detected GEMINI schema based on 'request.contents' presence and"
                " successful conversion."
            )
            return EvalDatasetSchema.GEMINI
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            logger.debug(
                "First item looked like Gemini schema (due to 'request.contents') but"
                " conversion failed (error: %s). Will try other schemas.",
                e,
            )

    # Check for flatten schema if Gemini check failed or wasn't applicable
    if {"prompt", "response"}.issubset(keys) or {
        "response",
        "reference",
    }.issubset(keys):
        try:
            _FlattenEvalDataConverter().convert([first_item])
            logger.debug(
                "Detected FLATTEN schema based on key presence and successful"
                " conversion."
            )
            return EvalDatasetSchema.FLATTEN
        except (ValueError, KeyError, AttributeError, TypeError) as e:
            logger.debug(
                "Flatten schema key check passed, but conversion failed (error: %s).",
                e,
            )

    logger.debug("Could not confidently determine schema. Returning UNKNOWN.")
    return EvalDatasetSchema.UNKNOWN


_SCHEMA_TO_CONVERTER = {
    EvalDatasetSchema.GEMINI: _GeminiEvalDataConverter,
    EvalDatasetSchema.FLATTEN: _FlattenEvalDataConverter,
}


def get_dataset_converter(
    dataset_schema: EvalDatasetSchema,
) -> _EvalDataConverter:
    """Returns the appropriate dataset converter for the given schema."""
    if dataset_schema in _SCHEMA_TO_CONVERTER:
        return _SCHEMA_TO_CONVERTER[dataset_schema]()
    else:
        raise ValueError(f"Unsupported dataset schema: {dataset_schema}")


def _get_first_part_text(content: genai_types.Content) -> str:
    """Safely extracts text from the first part of a content."""
    if (
        content
        and hasattr(content, "parts")
        and isinstance(content.parts, list)
        and content.parts
    ):
        first_part = content.parts[0]
        if hasattr(first_part, "text"):
            return str(first_part.text)
    return ""


def _get_text_from_reference(
    reference: Optional[types.ResponseCandidate],
) -> Optional[str]:
    """Safely extracts text from a reference field."""
    if reference and hasattr(reference, "response") and reference.response:
        return _get_first_part_text(reference.response)
    return None


def _validate_case_consistency(
    base_case: types.EvalCase,
    current_case: types.EvalCase,
    case_idx: int,
    dataset_idx: int,
):
    """Logs warnings if prompt or reference mismatches occur."""
    if base_case.prompt != current_case.prompt:
        base_prompt_text_preview = _get_first_part_text(base_case.prompt)[:50]
        current_prompt_text_preview = _get_first_part_text(current_case.prompt)[:50]
        logger.warning(
            f"Prompt mismatch for case index {case_idx} between base dataset (0)"
            f" and dataset {dataset_idx}. Using prompt from base. Base prompt"
            f" preview: '{base_prompt_text_preview}...', Dataset"
            f" {dataset_idx} prompt preview: '{current_prompt_text_preview}...'"
        )

    base_ref_text = _get_text_from_reference(base_case.reference)
    current_ref_text = _get_text_from_reference(current_case.reference)

    if bool(base_case.reference) != bool(current_case.reference):
        logger.warning(
            f"Reference presence mismatch for case index {case_idx} between base"
            f" dataset (0) and dataset {dataset_idx}. Using reference (or lack"
            " thereof) from base."
        )
    elif base_ref_text != current_ref_text:
        logger.warning(
            f"Reference text mismatch for case index {case_idx} between base"
            f" dataset (0) and dataset {dataset_idx}. Using reference from base."
            f" Base ref: '{str(base_ref_text)[:50]}...', Current ref:"
            f" '{str(current_ref_text)[:50]}...'"
        )


def merge_response_datasets_into_canonical_format(
    raw_datasets: list[list[dict[str, Any]]],
    schemas: list[str],
) -> types.EvaluationDataset:
    """Merges multiple raw response datasets into a single EvaluationDataset.

    Assumes that each dataset in raw_datasets has responses corresponding
    to the same set of prompts, in the same order. The prompt, reference,
    system_instruction, and conversation_history are taken from the first dataset.
    """
    if not isinstance(raw_datasets, list):
        raise TypeError(
            f"Input 'raw_datasets' must be a list, got {type(raw_datasets)}."
        )
    if not raw_datasets or not all(isinstance(ds, list) for ds in raw_datasets):
        raise ValueError(
            "Input 'raw_datasets' cannot be empty and must be a list of lists."
        )
    if not schemas or len(schemas) != len(raw_datasets):
        raise ValueError(
            "A list of schemas must be provided, one for each raw dataset. "
            f"Got {len(schemas)} schemas for {len(raw_datasets)} datasets."
        )

    num_expected_cases = len(raw_datasets[0])
    if num_expected_cases == 0:
        logger.warning(
            "The first dataset has no evaluation cases. Result will be empty."
        )
        return types.EvaluationDataset(eval_cases=[])

    parsed_evaluation_datasets: list[types.EvaluationDataset] = []
    for i, (raw_ds_entry, schema) in enumerate(zip(raw_datasets, schemas)):
        if len(raw_ds_entry) != num_expected_cases:
            raise ValueError(
                "All datasets must have the same number of evaluation cases. "
                f"Base dataset (0) has {num_expected_cases}, but dataset {i} "
                f"(schema: {schema}) has {len(raw_ds_entry)}."
            )
        converter = get_dataset_converter(schema)
        parsed_evaluation_datasets.append(converter.convert(raw_ds_entry))

    merged_eval_cases: list[types.EvalCase] = []
    base_parsed_dataset = parsed_evaluation_datasets[0]

    for case_idx in range(num_expected_cases):
        base_eval_case: types.EvalCase = base_parsed_dataset.eval_cases[case_idx]
        candidate_responses: list[types.ResponseCandidate] = []

        if base_eval_case.responses:
            candidate_responses.append(base_eval_case.responses[0])
        else:
            logger.warning(
                "No response found for base dataset (index 0) in case %s. "
                "Adding placeholder.",
                case_idx,
            )
            candidate_responses.append(
                _create_placeholder_response_candidate(
                    f"Missing response from base dataset (0) for case {case_idx}"
                )
            )

        eval_case_custom_columns = base_eval_case.model_dump(
            exclude={
                "eval_case_id",
                "prompt",
                "responses",
                "reference",
                "system_instruction",
                "conversation_history",
            },
            exclude_none=True,
        )
        for dataset_idx_offset, current_parsed_ds in enumerate(
            parsed_evaluation_datasets[1:], start=1
        ):
            current_ds_eval_case: types.EvalCase = current_parsed_ds.eval_cases[
                case_idx
            ]

            _validate_case_consistency(
                base_eval_case, current_ds_eval_case, case_idx, dataset_idx_offset
            )

            current_ds_extra_attrs = current_ds_eval_case.model_dump(
                exclude={
                    "eval_case_id",
                    "prompt",
                    "responses",
                    "reference",
                    "system_instruction",
                    "conversation_history",
                },
                exclude_none=True,
            )
            eval_case_custom_columns.update(current_ds_extra_attrs)

            if current_ds_eval_case.responses:
                candidate_responses.append(current_ds_eval_case.responses[0])
            else:
                logger.warning(
                    "No response found for dataset %s in case %s. Adding placeholder.",
                    dataset_idx_offset,
                    case_idx,
                )
                candidate_responses.append(
                    _create_placeholder_response_candidate(
                        f"Missing response from dataset {dataset_idx_offset} "
                        f"for case {case_idx}"
                    )
                )

        merged_case = types.EvalCase(
            eval_case_id=base_eval_case.eval_case_id or f"merged_eval_case_{case_idx}",
            prompt=base_eval_case.prompt,
            responses=candidate_responses,
            reference=base_eval_case.reference,
            system_instruction=base_eval_case.system_instruction,
            conversation_history=base_eval_case.conversation_history,
            **eval_case_custom_columns,
        )
        merged_eval_cases.append(merged_case)

    return types.EvaluationDataset(eval_cases=merged_eval_cases)
