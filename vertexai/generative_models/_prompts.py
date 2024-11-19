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

from __future__ import annotations

from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
from google.cloud.aiplatform.compat.services import dataset_service_client
from google.cloud.aiplatform.compat.types import dataset as gca_dataset
from google.cloud.aiplatform_v1.types import (
    dataset_version as gca_dataset_version,
)
from google.cloud.aiplatform_v1beta1.types import (
    prediction_service as gapic_prediction_service_types,
)
from vertexai.generative_models import (
    Content,
    Image,
    Part,
    GenerativeModel,
    GenerationConfig,
    SafetySetting,
    Tool,
    ToolConfig,
)
from vertexai.generative_models._generative_models import (
    _to_content,
    _proto_to_dict,
    _dict_to_proto,
    _tool_types_to_gapic_tools,
    _validate_generate_content_parameters,
    _reconcile_model_name,
    _get_resource_name_from_model_name,
    ContentsType,
    GenerationConfigType,
    GenerationResponse,
    PartsType,
    SafetySettingsType,
)
from google.protobuf import field_mask_pb2 as field_mask

import dataclasses
import re
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Union,
)

_LOGGER = base.Logger(__name__)

DEFAULT_API_SCHEMA_VERSION = "1.0.0"
DEFAULT_MODEL_NAME = "gemini-1.5-flash-002"
PROMPT_SCHEMA_URI = (
    "gs://google-cloud-aiplatform/schema/dataset/metadata/text_prompt_1.0.0.yaml"
)
VARIABLE_NAME_REGEX = r"(\{[^\W0-9]\w*\})"


def _format_function_declaration_parameters(obj: Any):
    """Recursively replaces type_ and format_ fields in-place."""
    if isinstance(obj, (str, int, float)):
        return obj
    if isinstance(obj, dict):
        new = obj.__class__()
        for key, value in obj.items():
            key = key.replace("type_", "type")
            key = key.replace("format_", "format")
            new[key] = _format_function_declaration_parameters(value)
    elif isinstance(obj, (list, set, tuple)):
        new = obj.__class__(
            _format_function_declaration_parameters(value) for value in obj
        )
    else:
        return obj
    return new


@dataclasses.dataclass
class Arguments:
    """Arguments. Child of Execution.

    Attributes:
        variables: The arguments of the execution.
    """

    variables: dict[str, list[Part]]

    def to_dict(self) -> Dict[str, Any]:
        dct = {}
        for variable_name in self.variables:
            dct[variable_name] = {
                "partList": {
                    "parts": [part.to_dict() for part in self.variables[variable_name]]
                }
            }
        return dct

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "Arguments":
        variables = {}
        for variable_name in dct:
            variables[variable_name] = [
                Part.from_dict(part) for part in dct[variable_name]["partList"]["parts"]
            ]
        arguments = cls(variables=variables)
        return arguments


@dataclasses.dataclass
class Execution:
    """Execution. Child of MultimodalPrompt.

    Attributes:
        arguments: The arguments of the execution.
    """

    arguments: Arguments

    def __init__(self, arguments: dict[str, list[Part]]):
        self.arguments = Arguments(variables=arguments)

    def to_dict(self) -> Dict[str, Any]:
        dct = {}
        dct["arguments"] = self.arguments.to_dict()
        return dct

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "Execution":
        arguments = dct.get("arguments", None)
        execution = cls(arguments=arguments)
        return execution


@dataclasses.dataclass
class MultimodalPrompt:
    """MultimodalPrompt. Child of PromptDatasetMetadata.

    Attributes:
        prompt_message: The schema for the prompt. A subset of the GenerateContentRequest schema.
        api_schema_version: The api schema version of the prompt when it was last modified.
        executions: Contains data related to an execution of a prompt (ex. variables)
    """

    prompt_message: gapic_prediction_service_types.GenerateContentRequest
    api_schema_version: Optional[str] = DEFAULT_API_SCHEMA_VERSION
    executions: Optional[list[Execution]] = None

    def to_dict(self) -> Dict[str, Any]:
        dct = {"multimodalPrompt": {}}
        dct["apiSchemaVersion"] = self.api_schema_version
        dct["multimodalPrompt"]["promptMessage"] = _proto_to_dict(self.prompt_message)

        # Fix type_ and format_ fields
        if dct["multimodalPrompt"]["promptMessage"].get("tools", None):
            tools = dct["multimodalPrompt"]["promptMessage"]["tools"]
            for tool in tools:
                for function_declaration in tool.get("function_declarations", []):
                    function_declaration[
                        "parameters"
                    ] = _format_function_declaration_parameters(
                        function_declaration["parameters"]
                    )

        if self.executions and self.executions[0]:
            # Only add variable sets if they are non empty.
            execution_dcts = []
            for execution in self.executions:
                exeuction_dct = execution.to_dict()
                if exeuction_dct and exeuction_dct["arguments"]:
                    execution_dcts.append(exeuction_dct)
            if execution_dcts:
                dct["executions"] = execution_dcts
        return dct

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "MultimodalPrompt":
        prompt_message_dct = dct.get("multimodalPrompt", {}).get("promptMessage", None)
        # Tool function declaration will fail the proto conversion
        tools = prompt_message_dct.get("tools", None)
        if tools:
            tools = [Tool.from_dict(tool) for tool in tools]
            prompt_message_dct.pop("tools")
        prompt_message = _dict_to_proto(
            gapic_prediction_service_types.GenerateContentRequest, prompt_message_dct
        )
        if tools:
            # Convert Tools to gapic to store in the prompt_message
            prompt_message.tools = _tool_types_to_gapic_tools(tools)
        executions_dct = dct.get("executions", [])
        executions = [Execution.from_dict(execution) for execution in executions_dct]
        if not executions:
            executions = None
        multimodal_prompt = cls(
            prompt_message=prompt_message,
            api_schema_version=dct.get("apiSchemaVersion", DEFAULT_API_SCHEMA_VERSION),
            executions=executions,
        )
        return multimodal_prompt


@dataclasses.dataclass
class PromptDatasetMetadata:
    """PromptDatasetMetadata.

    Attributes:
        prompt_type: Required. SDK only supports "freeform" or "multimodalFreeform"
        prompt_api_schema: Required. SDK only supports multimodalPrompt
    """

    prompt_type: str
    prompt_api_schema: MultimodalPrompt

    def to_dict(self) -> Dict[str, Any]:
        dct = {}
        dct["promptType"] = self.prompt_type  # TODO(tangmatthew): Check if multimodal
        dct["promptApiSchema"] = self.prompt_api_schema.to_dict()
        return dct

    @classmethod
    def from_dict(cls, dct: Dict[str, Any]) -> "PromptDatasetMetadata":
        metadata = cls(
            prompt_type=dct.get("promptType", None),
            prompt_api_schema=MultimodalPrompt.from_dict(
                dct.get("promptApiSchema", None)
            ),
        )
        return metadata


@dataclasses.dataclass
class PromptVersionMetadata:
    """Metadata containing the display name, prompt id, and version id of a prompt version.

    Returned by the `list_prompt_versions` method.

    Attributes:
        name: The display name of the prompt version.
        prompt_id: The id of the prompt.
        version_id: The version id of the prompt.
    """

    name: str
    prompt_id: str
    version_id: str


class Prompt:
    """A prompt which may be a template with variables.

    The `Prompt` class allows users to define a template string with
    variables represented in curly braces `{variable}`. The variable
    name must be a valid Python variable name (no spaces, must start with a
    letter). These placeholders can be replaced with specific values using the
    `assemble_contents` method, providing flexibility in generating dynamic prompts.

    Usage:
        Generate content from a single set of variables:
        ```
        prompt = Prompt(
            prompt_data="Hello, {name}! Today is {day}. How are you?",
            variables=[{"name": "Alice", "day": "Monday"}]
            generation_config=GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
                stop_sequences=["\n\n\n"],
            ),
            model_name="gemini-1.0-pro-002",
            safety_settings=[SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                method=SafetySetting.HarmBlockMethod.SEVERITY,
            )],
            system_instruction="Please answer in a short sentence.",
        )

        # Generate content using the assembled prompt.
        prompt.generate_content(
            contents=prompt.assemble_contents(**prompt.variables)
        )
        ```
        Generate content with multiple sets of variables:
        ```
        prompt = Prompt(
            prompt_data="Hello, {name}! Today is {day}. How are you?",
            variables=[
                {"name": "Alice", "day": "Monday"},
                {"name": "Bob", "day": "Tuesday"},
            ],
            generation_config=GenerationConfig(
                temperature=0.1,
                top_p=0.95,
                top_k=20,
                candidate_count=1,
                max_output_tokens=100,
                stop_sequences=["\n\n\n"],
            ),
            model_name="gemini-1.0-pro-002",
            safety_settings=[SafetySetting(
                category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                method=SafetySetting.HarmBlockMethod.SEVERITY,
            )],
            system_instruction="Please answer in a short sentence.",
        )

        # Generate content using the assembled prompt for each variable set.
        for i in range(len(prompt.variables)):
            prompt.generate_content(
                contents=prompt.assemble_contents(**prompt.variables[i])
            )
        ```
    """

    def __init__(
        self,
        prompt_data: Optional[PartsType] = None,
        *,
        variables: Optional[List[Dict[str, PartsType]]] = None,
        prompt_name: Optional[str] = None,
        generation_config: Optional[GenerationConfig] = None,
        model_name: Optional[str] = None,
        safety_settings: Optional[SafetySetting] = None,
        system_instruction: Optional[PartsType] = None,
        tools: Optional[List[Tool]] = None,
        tool_config: Optional[ToolConfig] = None,
    ):
        """Initializes the Prompt with a given prompt, and variables.

        Args:
            prompt: A PartsType prompt which may be a template with variables or a prompt with no variables.
            variables: A list of dictionaries containing the variable names and values.
            prompt_name: The name of the prompt if stored in an online resource.
            generation_config: A GenerationConfig object containing parameters for generation.
            model_name: Model Garden model resource name.
                Alternatively, a tuned model endpoint resource name can be provided.
                If no model is provided, the default latest model will be used.
            safety_settings: A SafetySetting object containing safety settings for generation.
            system_instruction: A PartsType object representing the system instruction.
            tools: A list of Tool objects for function calling.
            tool_config: A ToolConfig object for function calling.
        """
        self._prompt_data = None
        self._variables = None
        self._model_name = None
        self._generation_config = None
        self._safety_settings = None
        self._system_instruction = None
        self._tools = None
        self._tool_config = None

        # Prompt Management
        self._dataset_client_value = None
        self._dataset = None
        self._prompt_name = None
        self._version_id = None
        self._version_name = None

        self.prompt_data = prompt_data
        self.variables = variables if variables else [{}]
        self.prompt_name = prompt_name
        self.model_name = model_name
        self.generation_config = generation_config
        self.safety_settings = safety_settings
        self.system_instruction = system_instruction
        self.tools = tools
        self.tool_config = tool_config

    @property
    def prompt_data(self) -> Optional[PartsType]:
        return self._prompt_data

    @property
    def variables(self) -> Optional[List[Dict[str, PartsType]]]:
        return self._variables

    @property
    def prompt_name(self) -> Optional[str]:
        return self._prompt_name

    @property
    def generation_config(self) -> Optional[GenerationConfig]:
        return self._generation_config

    @property
    def model_name(self) -> Optional[str]:
        if self._model_name:
            return self._model_name
        else:
            return Prompt._format_model_resource_name(DEFAULT_MODEL_NAME)

    @property
    def safety_settings(self) -> Optional[List[SafetySetting]]:
        return self._safety_settings

    @property
    def system_instruction(self) -> Optional[PartsType]:
        return self._system_instruction

    @property
    def tools(self) -> Optional[List[Tool]]:
        return self._tools

    @property
    def tool_config(self) -> Optional[ToolConfig]:
        return self._tool_config

    @property
    def prompt_id(self) -> Optional[str]:
        if self._dataset:
            return self._dataset.name.split("/")[-1]
        return None

    @property
    def version_id(self) -> Optional[str]:
        return self._version_id

    @property
    def version_name(self) -> Optional[str]:
        return self._version_name

    @prompt_data.setter
    def prompt_data(self, prompt_data: PartsType) -> None:
        """Overwrites the existing saved local prompt_data.

        Args:
            prompt_data: A PartsType prompt.
        """
        if prompt_data is not None:
            self._validate_parts_type_data(prompt_data)
        self._prompt_data = prompt_data

    @variables.setter
    def variables(self, variables: List[Dict[str, PartsType]]) -> None:
        """Overwrites the existing saved local variables.

        Args:
            variables: A list of dictionaries containing the variable names and values.
        """
        if isinstance(variables, list):
            for i in range(len(variables)):
                variables[i] = variables[i].copy()
                Prompt._format_variable_value_to_parts(variables[i])
            self._variables = variables
        else:
            raise TypeError(
                f"Variables must be a list of dictionaries, not {type(variables)}"
            )

    @prompt_name.setter
    def prompt_name(self, prompt_name: Optional[str]) -> None:
        """Overwrites the existing saved local prompt_name."""
        if prompt_name:
            self._prompt_name = prompt_name
        else:
            self._prompt_name = None

    @model_name.setter
    def model_name(self, model_name: Optional[str]) -> None:
        """Overwrites the existing saved local model_name."""
        if model_name:
            self._model_name = Prompt._format_model_resource_name(model_name)
        else:
            self._model_name = None

    def _format_model_resource_name(model_name: Optional[str]) -> str:
        """Formats the model resource name."""
        project = aiplatform_initializer.global_config.project
        location = aiplatform_initializer.global_config.location
        model_name = _reconcile_model_name(model_name, project, location)

        prediction_resource_name = _get_resource_name_from_model_name(
            model_name, project, location
        )
        return prediction_resource_name

    def _validate_configs(
        self,
        generation_config: Optional[GenerationConfig] = None,
        safety_settings: Optional[SafetySetting] = None,
        system_instruction: Optional[PartsType] = None,
        tools: Optional[List[Tool]] = None,
        tool_config: Optional[ToolConfig] = None,
    ):
        generation_config = generation_config or self._generation_config
        safety_settings = safety_settings or self._safety_settings
        tools = tools or self._tools
        tool_config = tool_config or self._tool_config
        system_instruction = system_instruction or self._system_instruction
        return _validate_generate_content_parameters(
            contents="test",
            generation_config=generation_config,
            safety_settings=safety_settings,
            system_instruction=system_instruction,
            tools=tools,
            tool_config=tool_config,
        )

    @generation_config.setter
    def generation_config(self, generation_config: Optional[GenerationConfig]) -> None:
        """Overwrites the existing saved local generation_config.

        Args:
            generation_config: A GenerationConfig object containing parameters for generation.
        """
        self._validate_configs(generation_config=generation_config)
        self._generation_config = generation_config

    @safety_settings.setter
    def safety_settings(self, safety_settings: Optional[SafetySetting]) -> None:
        """Overwrites the existing saved local safety_settings.

        Args:
            safety_settings: A SafetySetting object containing safety settings for generation.
        """
        self._validate_configs(safety_settings=safety_settings)
        self._safety_settings = safety_settings

    @system_instruction.setter
    def system_instruction(self, system_instruction: Optional[PartsType]) -> None:
        """Overwrites the existing saved local system_instruction.

        Args:
            system_instruction: A PartsType object representing the system instruction.
        """
        if system_instruction:
            self._validate_parts_type_data(system_instruction)
        self._system_instruction = system_instruction

    @tools.setter
    def tools(self, tools: Optional[List[Tool]]) -> None:
        """Overwrites the existing saved local tools.

        Args:
            tools: A list of Tool objects for function calling.
        """
        self._validate_configs(tools=tools)
        self._tools = tools

    @tool_config.setter
    def tool_config(self, tool_config: Optional[ToolConfig] = None) -> None:
        """Overwrites the existing saved local tool_config.

        Args:
            tool_config: A ToolConfig object for function calling.
        """
        self._validate_configs(tool_config=tool_config)
        self._tool_config = tool_config

    def _format_variable_value_to_parts(variables_dict: Dict[str, PartsType]) -> None:
        """Formats the variables values to be List[Part].

        Args:
            variables_dict: A single dictionary containing the variable names and values.

        Raises:
            TypeError: If a variable value is not a PartsType Object.
        """
        for key in variables_dict.keys():
            # Disallow Content as variable value.
            if isinstance(variables_dict[key], Content):
                raise TypeError(
                    "Variable values must be a PartsType object, not Content"
                )

            # Rely on type checks in _to_content for validation.
            content = Content._from_gapic(_to_content(value=variables_dict[key]))
            variables_dict[key] = content.parts

    def _validate_parts_type_data(self, data: Any) -> None:
        """
        Args:
            prompt_data: The prompt input to validate

        Raises:
            TypeError: If prompt_data is not a PartsType Object.
        """
        # Disallow Content as prompt_data.
        if isinstance(data, Content):
            raise TypeError("Prompt data must be a PartsType object, not Content")

        # Rely on type checks in _to_content.
        _to_content(value=data)

    def assemble_contents(self, **variables_dict: PartsType) -> List[Content]:
        """Returns the prompt data, as a List[Content], assembled with variables if applicable.
        Can be ingested into model.generate_content to make API calls.

        Returns:
            A List[Content] prompt.
        Usage:
            ```
            prompt = Prompt(
                prompt_data="Hello, {name}! Today is {day}. How are you?",
            )

            model.generate_content(
                contents=prompt.assemble_contents(name="Alice", day="Monday")
            )
            ```
        """
        # If prompt_data is None, throw an error.
        if self.prompt_data is None:
            raise ValueError("prompt_data must not be empty.")

        variables_dict = variables_dict.copy()

        # If there are no variables, return the prompt_data as a Content object.
        if not variables_dict:
            return [Content._from_gapic(_to_content(value=self.prompt_data))]

        # Step 1) Convert the variables values to List[Part].
        Prompt._format_variable_value_to_parts(variables_dict)

        # Step 2) Assemble the prompt.
        # prompt_data must have been previously validated using _validate_parts_type_data.
        assembled_prompt = []
        assembled_variables_cnt = {}
        if isinstance(self.prompt_data, list):
            # User inputted a List of Parts as prompt_data.
            for part in self.prompt_data:
                assembled_prompt.extend(
                    self._assemble_singular_part(
                        part, variables_dict, assembled_variables_cnt
                    )
                )
        else:
            # User inputted a single str, Image, or Part as prompt_data.
            assembled_prompt.extend(
                self._assemble_singular_part(
                    self.prompt_data, variables_dict, assembled_variables_cnt
                )
            )

        # Step 3) Simplify adjacent string Parts
        simplified_assembled_prompt = [assembled_prompt[0]]
        for i in range(1, len(assembled_prompt)):
            # If the previous Part and current Part is a string, concatenate them.
            try:
                prev_text = simplified_assembled_prompt[-1].text
                curr_text = assembled_prompt[i].text
                if isinstance(prev_text, str) and isinstance(curr_text, str):
                    simplified_assembled_prompt[-1] = Part.from_text(
                        prev_text + curr_text
                    )
                else:
                    simplified_assembled_prompt.append(assembled_prompt[i])
            except AttributeError:
                simplified_assembled_prompt.append(assembled_prompt[i])
                continue

        # Step 4) Validate that all variables were used, if specified.
        for key in variables_dict:
            if key not in assembled_variables_cnt:
                raise ValueError(f"Variable {key} is not present in prompt_data.")

        assemble_cnt_msg = "Assembled prompt replacing: "
        for key in assembled_variables_cnt:
            assemble_cnt_msg += (
                f"{assembled_variables_cnt[key]} instances of variable {key}, "
            )
        if assemble_cnt_msg[-2:] == ", ":
            assemble_cnt_msg = assemble_cnt_msg[:-2]
        _LOGGER.info(assemble_cnt_msg)

        # Step 5) Wrap List[Part] as a single Content object.
        return [
            Content(
                parts=simplified_assembled_prompt,
                role="user",
            )
        ]

    def _assemble_singular_part(
        self,
        prompt_data_part: Union[str, Image, Part],
        formatted_variables_set: Dict[str, List[Part]],
        assembled_variables_cnt: Dict[str, int],
    ) -> List[Part]:
        """Assemble a str, Image, or Part."""
        if isinstance(prompt_data_part, Image):
            # Templating is not supported for Image prompt_data.
            return [Part.from_image(prompt_data_part)]
        elif isinstance(prompt_data_part, str):
            # Assemble a single string
            return self._assemble_single_str(
                prompt_data_part, formatted_variables_set, assembled_variables_cnt
            )
        elif isinstance(prompt_data_part, Part):
            # If the Part is a text Part, assemble it.
            try:
                text = prompt_data_part.text
            except AttributeError:
                return [prompt_data_part]
            return self._assemble_single_str(
                text, formatted_variables_set, assembled_variables_cnt
            )

    def _assemble_single_str(
        self,
        prompt_data_str: str,
        formatted_variables_set: Dict[str, List[Part]],
        assembled_variables_cnt: Dict[str, int],
    ) -> List[Part]:
        """Assemble a single string with 0 or more variables within the string."""
        # Step 1) Find and isolate variables as their own string.
        prompt_data_str_split = re.split(VARIABLE_NAME_REGEX, prompt_data_str)

        assembled_data = []
        # Step 2) Assemble variables with their values, creating a list of Parts.
        for s in prompt_data_str_split:
            if not s:
                continue
            variable_name = s[1:-1]
            if (
                re.match(VARIABLE_NAME_REGEX, s)
                and variable_name in formatted_variables_set
            ):
                assembled_data.extend(formatted_variables_set[variable_name])
                assembled_variables_cnt[variable_name] = (
                    assembled_variables_cnt.get(variable_name, 0) + 1
                )
            else:
                assembled_data.append(Part.from_text(s))

        return assembled_data

    def generate_content(
        self,
        contents: ContentsType,
        *,
        generation_config: Optional[GenerationConfigType] = None,
        safety_settings: Optional[SafetySettingsType] = None,
        model_name: Optional[str] = None,
        tools: Optional[List["Tool"]] = None,
        tool_config: Optional["ToolConfig"] = None,
        stream: bool = False,
        system_instruction: Optional[PartsType] = None,
    ) -> Union["GenerationResponse", Iterable["GenerationResponse"],]:
        """Generates content using the saved Prompt configs.

        Args:
            contents: Contents to send to the model.
                Supports either a list of Content objects (passing a multi-turn conversation)
                or a value that can be converted to a single Content object (passing a single message).
                Supports
                * str, Image, Part,
                * List[Union[str, Image, Part]],
                * List[Content]
            generation_config: Parameters for the generation.
            model_name: Prediction model resource name.
            safety_settings: Safety settings as a mapping from HarmCategory to HarmBlockThreshold.
            tools: A list of tools (functions) that the model can try calling.
            tool_config: Config shared for all tools provided in the request.
            stream: Whether to stream the response.
            system_instruction: System instruction to pass to the model.

        Returns:
            A single GenerationResponse object if stream == False
            A stream of GenerationResponse objects if stream == True

        Usage:
            ```
            prompt = Prompt(
                prompt_data="Hello, {name}! Today is {day}. How are you?",
                variables={"name": "Alice", "day": "Monday"},
                generation_config=GenerationConfig(temperature=0.1,),
                system_instruction="Please answer in a short sentence.",
                model_name="gemini-1.0-pro-002",
            )

            prompt.generate_content(
                contents=prompt.assemble_contents(**prompt.variables)
            )
            ```
        """
        if not (model_name or self._model_name):
            _LOGGER.info(
                "No model name specified, falling back to default model: %s",
                self.model_name,
            )
        model_name = model_name or self.model_name

        generation_config = generation_config or self.generation_config
        safety_settings = safety_settings or self.safety_settings
        tools = tools or self.tools
        tool_config = tool_config or self.tool_config
        system_instruction = system_instruction or self.system_instruction

        if not model_name:
            raise ValueError(
                "Model name must be specified to use Prompt.generate_content()"
            )
        model_name = Prompt._format_model_resource_name(model_name)

        model = GenerativeModel(
            model_name=model_name, system_instruction=system_instruction
        )
        return model.generate_content(
            contents=contents,
            generation_config=generation_config,
            safety_settings=safety_settings,
            tools=tools,
            tool_config=tool_config,
            stream=stream,
        )

    @property
    def _dataset_client(self) -> dataset_service_client.DatasetServiceClient:
        if not getattr(self, "_dataset_client_value", None):
            self._dataset_client_value = (
                aiplatform_initializer.global_config.create_client(
                    client_class=dataset_service_client.DatasetServiceClient,
                )
            )
        return self._dataset_client_value

    def create_version(
        self,
        create_new_prompt: bool = False,
        version_name: Optional[str] = None,
    ) -> None:
        """Creates a Prompt in the online prompt store

        Args:
            create_new_prompt: Whether to create a new online prompt resource.
                If True or the prompt resource does not exist yet,
                a new prompt resource will be created.
            version_name: Optional display name of the new prompt version.
            If not specified, a default name including a timestamp will be used.
        """
        if not self._dataset or create_new_prompt:
            return self._create_prompt_resource(version_name)
        else:
            return self._create_prompt_version_resource(version_name)

    def _format_dataset_metadata_dict(self) -> dict[str, Any]:
        """Helper function to convert the configs and prompt data stored in the Prompt object to a dataset metadata dict."""
        model = GenerativeModel(model_name=self.model_name)
        prompt_message = model._prepare_request(
            contents=self.prompt_data or "temporary data",
            model=self.model_name,
            system_instruction=self.system_instruction,
            tools=self.tools,
            tool_config=self.tool_config,
            safety_settings=self.safety_settings,
            generation_config=self.generation_config,
        )
        # Remove temporary contents
        if not self.prompt_data:
            prompt_message.contents = None

        return PromptDatasetMetadata(
            prompt_type="freeform",
            prompt_api_schema=MultimodalPrompt(
                prompt_message=prompt_message,
                executions=[Execution(variable_set) for variable_set in self.variables],
            ),
        ).to_dict()

    def _create_dataset(self, parent: str) -> gca_dataset.Dataset:
        dataset_metadata = self._format_dataset_metadata_dict()

        dataset = gca_dataset.Dataset(
            name=parent,
            display_name=self.prompt_name or "Untitled Prompt",
            metadata_schema_uri=PROMPT_SCHEMA_URI,
            metadata=dataset_metadata,
            model_reference=self.model_name,
        )
        operation = self._dataset_client.create_dataset(
            parent=parent,
            dataset=dataset,
        )
        dataset = operation.result()

        # Purge labels
        dataset.labels = None
        return dataset

    def _create_dataset_version(self, parent: str, version_name: Optional[str] = None):
        dataset_version = gca_dataset_version.DatasetVersion(
            display_name=version_name,
        )

        dataset_version = self._dataset_client.create_dataset_version(
            parent=parent,
            dataset_version=dataset_version,
        )
        return dataset_version.result()

    def _update_dataset(
        self, dataset: gca_dataset.Dataset
    ) -> gca_dataset_version.DatasetVersion:
        dataset.metadata = self._format_dataset_metadata_dict()

        updated_dataset = self._dataset_client.update_dataset(
            dataset=dataset,
            update_mask=field_mask.FieldMask(
                paths=["displayName", "modelReference", "metadata"]
            ),
        )
        # Remove etag to avoid error for repeated dataset updates
        updated_dataset.etag = None
        return updated_dataset

    def _create_prompt_resource(self, version_name: Optional[str] = None) -> None:
        project = aiplatform_initializer.global_config.project
        location = aiplatform_initializer.global_config.location

        # Step 1: Create prompt dataset
        parent = f"projects/{project}/locations/{location}"
        dataset = self._create_dataset(parent=parent)

        # Step 2: Create prompt version (snapshot)
        dataset_version = self._create_dataset_version(
            parent=dataset.name, version_name=version_name
        )

        # Step 3: Update Prompt object
        self._dataset = dataset
        self._version_id = dataset_version.name.split("/")[-1]
        self._version_name = dataset_version.display_name
        prompt_id = self._dataset.name.split("/")[5]
        _LOGGER.info(
            f"Created prompt resource with id {prompt_id} with version number {self._version_id}"
        )

    def _create_prompt_version_resource(
        self, version_name: Optional[str] = None
    ) -> None:
        # Step 1: Update prompt
        updated_dataset = self._update_dataset(dataset=self._dataset)

        # Step 2: Create prompt version (snapshot)
        dataset_version = self._create_dataset_version(
            parent=updated_dataset.name, version_name=version_name
        )

        # Step 3: Update Prompt object
        self._dataset = updated_dataset
        self._version_id = dataset_version.name.split("/")[-1]
        self._version_name = dataset_version.display_name
        prompt_id = self._dataset.name.split("/")[5]
        _LOGGER.info(
            f"Updated prompt resource with id {prompt_id} as version number {self._version_id}"
        )

    def _get_prompt_resource(self, prompt_id: str) -> gca_dataset.Dataset:
        """Helper function to get a prompt resource from a prompt id."""
        project = aiplatform_initializer.global_config.project
        location = aiplatform_initializer.global_config.location
        name = f"projects/{project}/locations/{location}/datasets/{prompt_id}"
        dataset = self._dataset_client.get_dataset(name=name)
        return dataset

    def _get_prompt_resource_from_version(
        self, prompt_id: str, version_id: str
    ) -> gca_dataset.Dataset:
        """Helper function to get a prompt resource from a prompt version id."""
        project = aiplatform_initializer.global_config.project
        location = aiplatform_initializer.global_config.location
        name = f"projects/{project}/locations/{location}/datasets/{prompt_id}/datasetVersions/{version_id}"

        # Step 1: Get dataset version object
        dataset_version = self._dataset_client.get_dataset_version(name=name)
        self._version_name = dataset_version.display_name

        # Step 2: Fetch dataset object to get the dataset display name
        name = f"projects/{project}/locations/{location}/datasets/{prompt_id}"
        dataset = self._dataset_client.get_dataset(name=name)

        # Step 3: Convert to DatasetVersion object to Dataset object
        dataset = gca_dataset.Dataset(
            name=name,
            display_name=dataset.display_name,
            metadata_schema_uri=PROMPT_SCHEMA_URI,
            metadata=dataset_version.metadata,
            model_reference=dataset_version.model_reference,
        )
        return dataset

    def restore_version(self, version_id: str) -> None:
        """Restores a previous version of the prompt resource and
        loads that version into the current Prompt object.

        Args:
            version_id: The version id of the online prompt resource.
        """
        # Step 1: Make restore dataset version API call
        name = f"{self._dataset.name}/datasetVersions/{version_id}"
        operation = self._dataset_client.restore_dataset_version(name=name)
        operation.result()

        # Step 2: Fetch the latest, newly restored dataset
        dataset = self._get_prompt_resource(self._dataset.name.split("/")[5])
        dataset_dict = _proto_to_dict(dataset)

        # Step 3: Populate Prompt fields from newly restored dataset
        metadata = PromptDatasetMetadata.from_dict(dataset_dict["metadata"])
        self._populate_fields_from_metadata(metadata)

    @classmethod
    def from_id(cls, prompt_id: str, version_id: Optional[str] = None) -> "Prompt":
        """Creates a Prompt object from an online resource.

        Args:
            prompt_id: The id of the prompt resource.
            version_id: Optional version id of the prompt resource.
                If not specified, the latest version will be used.

        Returns:
            A prompt loaded from the online resource as a `Prompt` object.
        """
        prompt = cls()
        if version_id:
            dataset = prompt._get_prompt_resource_from_version(prompt_id, version_id)
        else:
            dataset = prompt._get_prompt_resource(prompt_id)

        # Remove etag to avoid error for repeated dataset updates
        dataset.etag = None

        prompt._dataset = dataset
        prompt._version_id = version_id

        dataset_dict = _proto_to_dict(dataset)

        metadata = PromptDatasetMetadata.from_dict(dataset_dict["metadata"])
        prompt._populate_fields_from_metadata(metadata)
        return prompt

    def _populate_fields_from_metadata(self, metadata: PromptDatasetMetadata) -> None:
        """Helper function to populate Promptfields from metadata object"""
        # Populate model_name (Required, raw deserialized type is str)
        self.model_name = metadata.prompt_api_schema.prompt_message.model

        # Populate prompt_data (raw deserialized type is list[Content])
        contents = metadata.prompt_api_schema.prompt_message.contents
        if contents:
            if len(contents) > 1:
                raise ValueError("Multi-turn prompts are not supported yet.")
            prompt_data = [Part._from_gapic(part) for part in list(contents[0].parts)]

            # Unwrap single text part into str
            if len(prompt_data) == 1 and prompt_data[0].text:
                self.prompt_data = prompt_data[0].text

        # Populate system_instruction (raw deserialized type is single Content)
        system_instruction = (
            metadata.prompt_api_schema.prompt_message.system_instruction
        )
        if system_instruction:
            system_instruction_parts = [
                Part._from_gapic(part) for part in list(system_instruction.parts)
            ]
            # Unwrap single text part into str
            if len(system_instruction_parts) == 1 and system_instruction_parts[0].text:
                self.system_instruction = system_instruction_parts[0].text

        # Populate variables
        executions = metadata.prompt_api_schema.executions
        variables = []
        if executions:
            for execution in executions:
                serialized_variable_set = execution.arguments
                variable_set = {}
                if serialized_variable_set:
                    for name, value in serialized_variable_set.variables.items():
                        # Parts are dicts, not gapic objects for variables
                        variable_set[name] = [
                            Part.from_dict(part)
                            for part in list(value["partList"]["parts"])
                        ]
                    variables.append(variable_set)

            # Unwrap variable single text part into str
            for variable_set in variables:
                for name, value in variable_set.items():
                    if len(value) == 1 and value[0].text:
                        variable_set[name] = value[0].text
            self.variables = variables

        # Populate generation_config (raw deserialized type is GenerationConfig)
        generation_config = metadata.prompt_api_schema.prompt_message.generation_config
        if generation_config:
            self.generation_config = generation_config

        # Populate safety_settings (raw deserialized type is RepeatedComposite of SafetySetting)
        safety_settings = metadata.prompt_api_schema.prompt_message.safety_settings
        if safety_settings:
            self.safety_settings = list(safety_settings)

        # Populate tools (raw deserialized type is RepeatedComposite of Tool)
        tools = metadata.prompt_api_schema.prompt_message.tools
        if tools:
            self.tools = list(tools)

        # Populate tool_config (raw deserialized type is ToolConfig)
        tool_config = metadata.prompt_api_schema.prompt_message.tool_config
        if tool_config:
            self.tool_config = ToolConfig._from_gapic(tool_config)

    def list_prompt_versions(self) -> list[PromptVersionMetadata]:
        """Returns a list of PromptVersionMetadata objects for the prompt resource.

        Returns:
            A list of PromptVersionMetadata objects for the prompt resource.
        """
        if not self._dataset:
            raise ValueError("Prompt has no online resource associated with it.")
        versions_pager = self._dataset_client.list_dataset_versions(
            parent=self._dataset.name,
        )
        version_history = []
        for version in versions_pager:
            version_history.append(
                PromptVersionMetadata(
                    name=version.display_name,
                    prompt_id=version.name.split("/")[5],
                    version_id=version.name.split("/")[-1],
                )
            )
        return version_history

    def delete_prompt_resource(self) -> None:
        """Deletes the online prompt resource."""
        if not self._dataset:
            raise ValueError("Prompt has no online resource associated with it.")
        operation = self._dataset_client.delete_dataset(
            name=self._dataset.name,
        )
        operation.result()

        prompt_id = self._dataset.name.split("/")[5]
        _LOGGER.info(f"Deleted prompt resource with id {prompt_id}.")
        self._dataset = None
        self._version_id = None
        self._version_name = None

    def get_unassembled_prompt_data(self) -> PartsType:
        """Returns the prompt data, without any variables replaced."""
        return self.prompt_data

    def __str__(self) -> str:
        """Returns the prompt data as a string, without any variables replaced."""
        return str(self.prompt_data or "")

    def __repr__(self) -> str:
        """Returns a string representation of the unassembled prompt."""
        result = "Prompt("
        if self.prompt_data:
            result += f"prompt_data='{self.prompt_data}', "
        if self.variables and self.variables[0]:
            result += f"variables={self.variables}), "
        if self.system_instruction:
            result += f"system_instruction={self.system_instruction}), "
        if self._model_name:
            # Don't display default model in repr
            result += f"model_name={self._model_name}), "
        if self.generation_config:
            result += f"generation_config={self.generation_config}), "
        if self.safety_settings:
            result += f"safety_settings={self.safety_settings}), "
        if self.tools:
            result += f"tools={self.tools}), "
        if self.tool_config:
            result += f"tool_config={self.tool_config}, "
        if self.prompt_id:
            result += f"prompt_id={self.prompt_id}, "
        if self.version_id:
            result += f"version_id={self.version_id}, "
        if self.prompt_name:
            result += f"prompt_name={self.prompt_name}, "
        if self.version_name:
            result += f"version_name={self.version_name}, "

        # Remove trailing ", "
        if result[-2:] == ", ":
            result = result[:-2]
        result += ")"
        return result
