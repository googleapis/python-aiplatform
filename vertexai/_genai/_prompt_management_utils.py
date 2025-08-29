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
"""Utility functions for prompt management."""

from . import types
from google.genai import types as genai_types
import json
import re

from typing import Optional

DEFAULT_API_SCHEMA_VERSION = "1.0.0"
PROMPT_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/text_prompt_1.0.0.yaml"
)
PROMPT_TYPE = "multimodal_freeform"


def _create_dataset_metadata_from_prompt(
    prompt: types.Prompt,
    variables: Optional[list[dict[str, genai_types.Part]]] = None,
) -> types.SchemaTextPromptDatasetMetadata:
    """Convert a types.Prompt into types.SchemaTextPromptDatasetMetadata."""

    prompt_metadata = types.SchemaTextPromptDatasetMetadata()

    prompt_api_schema = types.SchemaPromptApiSchema()
    prompt_api_schema.multimodal_prompt = types.SchemaPromptSpecMultimodalPrompt(
        prompt_message=prompt.prompt_data
    )

    prompt_api_schema.api_schema_version = DEFAULT_API_SCHEMA_VERSION

    prompt_metadata.has_prompt_variable = bool(variables)

    if variables:
        prompt_execution_list = []
        for prompt_var in variables:
            prompt_instance_execution = types.SchemaPromptInstancePromptExecution()
            prompt_instance_execution.arguments = {}
            for key, val in prompt_var.items():
                prompt_instance_execution.arguments[key] = (
                    types.SchemaPromptInstanceVariableValue(
                        part_list=types.SchemaPromptSpecPartList(parts=[val])
                    )
                )
            prompt_execution_list.append(prompt_instance_execution)
        prompt_api_schema.executions = prompt_execution_list
    prompt_metadata.prompt_api_schema = prompt_api_schema

    prompt_metadata.prompt_type = PROMPT_TYPE
    return prompt_metadata


def _check_operation_status_from_response_body(
    operation_response: genai_types.HttpResponse,
):
    """Checks the operation status from the response body."""
    if not hasattr(operation_response, "body"):
        raise ValueError("Error creating prompt dataset resource.")
    done = False
    body = json.loads(operation_response.body)
    if body.get("done"):
        done = True
    return done


def _create_prompt_from_dataset_metadata(
    dataset: types.Dataset,
) -> types.Prompt:
    """Constructs a types.Prompt from a types.Dataset resource returned from the API.

    Args:
      dataset: The types.Dataset object containing the prompt metadata.

    Returns:
      A types.Prompt object reconstructed from the dataset metadata.
    """
    if (
        not hasattr(dataset, "metadata")
        or dataset.metadata is None
        or not isinstance(dataset.metadata, types.SchemaTextPromptDatasetMetadata)
    ):
        raise ValueError(
            "Error retrieving prompt: prompt dataset resource is missing 'metadata'."
        )
    api_schema = dataset.metadata.prompt_api_schema
    prompt = types.Prompt()

    if api_schema.multimodal_prompt:

        prompt_message = api_schema.multimodal_prompt.prompt_message
        prompt.prompt_data = prompt_message

        executions = api_schema.executions
        if executions:
            prompt.variables = []
            for execution in executions:
                if execution.arguments:
                    args = execution.arguments
                    var_map = {}
                    for key, val in args.items():
                        part_list = val.part_list.parts
                        if part_list and part_list[0].text:
                            var_map[key] = part_list[0]
                    if var_map:
                        prompt.variables.append(var_map)

    return prompt


def _camel_to_snake(camel_case_string: str) -> str:
    """
    Converts a camelCase string to snake_case.

    Args:
        camel_case_string: The input string in camelCase.

    Returns:
        The converted string in snake_case.
    """
    snake_case_string = re.sub(r"(?<!^)([A-Z])", r"_\1", camel_case_string)
    return snake_case_string.lower()
