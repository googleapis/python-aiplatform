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

from typing import Union

DEFAULT_API_SCHEMA_VERSION = "1.0.0"
PROMPT_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/text_prompt_1.0.0.yaml"
)


def _format_part_for_prompt(part: types.PartUnion) -> types.Part:
    """Formats a PartUnion into a Part."""
    # TODO: decide if we want to support PIL_Image and File types from genai_types.PartUnion
    if isinstance(part, genai_types.Part) or isinstance(part, types.Part):
        return part
    elif isinstance(part, str):
        return types.Part(text=part)
    else:
        raise ValueError(
            "Prompt data must be a Part or a string, but got" f" {type(part).__name__}"
        )


def _create_dataset_metadata_from_prompt(
    prompt: types.Prompt,
) -> types.SchemaTextPromptDatasetMetadata:
    """Convert a types.Prompt into types.SchemaTextPromptDatasetMetadata."""
    prompt_metadata = types.SchemaTextPromptDatasetMetadata()

    prompt_api_schema = types.SchemaPromptApiSchema()
    if prompt.prompt_data:
        prompt_message = types.SchemaPromptSpecPromptMessage()
        parts = []
        if not isinstance(prompt.prompt_data, list):
            prompt.prompt_data = [prompt.prompt_data]
        for part in prompt.prompt_data:
            parts.append(_format_part_for_prompt(part))
        prompt_message.contents = [types.Content(parts=parts)]
        prompt_message.model = prompt.model_name
        prompt_message.generation_config = prompt.generation_config
        if prompt.safety_settings:
            prompt_message.safety_settings = [prompt.safety_settings]
        if prompt.system_instruction:
            prompt_message.system_instruction = types.Content(
                parts=[types.Part(text=prompt.system_instruction)]
            )
        prompt_message.tool_config = prompt.tool_config
        prompt_message.tools = prompt.tools
        prompt_api_schema.multimodal_prompt = types.SchemaPromptSpecMultimodalPrompt(
            prompt_message=prompt_message
        )

    prompt_api_schema.api_schema_version = DEFAULT_API_SCHEMA_VERSION

    prompt_metadata.has_prompt_variable = bool(prompt.variables)

    if prompt.variables:
        prompt_execution_list = []
        for prompt_var in prompt.variables:
            prompt_instance_execution = types.SchemaPromptInstancePromptExecution()
            prompt_instance_execution.arguments = {}
            for key, val in prompt_var.items():
                prompt_instance_execution.arguments[
                    key
                ] = types.SchemaPromptInstanceVariableValue(
                    part_list=types.SchemaPromptSpecPartList(parts=[val])
                )
            prompt_execution_list.append(prompt_instance_execution)
        prompt_api_schema.executions = prompt_execution_list
    prompt_metadata.prompt_api_schema = prompt_api_schema

    # TODO: confirm if this field needs to be set
    prompt_metadata.prompt_type = _check_multimodal_inputs(prompt.prompt_data)
    return prompt_metadata


def _check_multimodal_inputs(
    prompt_data: Union[types.PartUnion, list[types.PartUnion]],
) -> str:
    if isinstance(prompt_data, str):
        return "freeform"
    elif isinstance(prompt_data, types.Part):
        if not prompt_data.text or prompt_data.inline_data or prompt_data.file_data:
            return "multimodal_freeform"
        else:
            return "freeform"
    return "multimodal_freeform"


def _check_operation_status_from_response_body(operation_response: types.HttpResponse):
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
    prompt.encryption_spec = dataset.encryption_spec

    if api_schema.multimodal_prompt:

        prompt_message = api_schema.multimodal_prompt.prompt_message
        if prompt_message:

            prompt.model_name = prompt_message.model

            if prompt_message.contents and prompt_message.contents[0].parts:
                prompt.prompt_data = prompt_message.contents[0].parts

            system_instruction_content = prompt_message.system_instruction
            if system_instruction_content and system_instruction_content.parts:
                prompt.system_instruction = system_instruction_content.parts[0].text

            gen_config = prompt_message.generation_config
            if gen_config:
                prompt.generation_config = gen_config

            safety_settings_list = prompt_message.safety_settings
            if safety_settings_list:
                safety_settings = safety_settings_list[0]
                prompt.safety_settings = types.SafetySetting(
                    category=safety_settings.category,
                    threshold=safety_settings.threshold,
                    method=safety_settings.method,
                )
            if prompt_message.tool_config:
                prompt.tool_config = prompt_message.tool_config
            if prompt_message.tools:
                prompt.tools = prompt_message.tools

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
