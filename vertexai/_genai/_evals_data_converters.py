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
"""Dataset converter for evals."""
import abc
import enum
import logging
from typing import Any, Optional

from google.genai import types as genai_types
from typing_extensions import override

from . import types

logger = logging.getLogger("vertexai_genai._evals_data_converters")


class _EvalDatasetSchema(enum.Enum):
    """Represents the schema of an evaluation dataset."""

    GEMINI = "gemini"
    FLATTEN = "flatten"
    UNKNOWN = "unknown"


class _EvalDataConverter(abc.ABC):
    """Abstract base class for dataset converters."""

    @abc.abstractmethod
    def convert(self, raw_data: Any) -> list[types.EvalCase]:
        """Converts a loaded raw dataset into a list of EvalCase objects."""
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

            generate_content_response = (
                genai_types.GenerateContentResponse.model_validate(response_data)
            )

            responses = []
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
            else:  # Handle cases where there are no candidates (e.g., prompt blocked)
                responses.append(types.ResponseCandidate(response=None))

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
