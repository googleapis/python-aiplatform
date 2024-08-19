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

from google.cloud.aiplatform import base
from google.cloud.aiplatform import initializer as aiplatform_initializer
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
    _validate_generate_content_parameters,
    _reconcile_model_name,
    _get_resource_name_from_model_name,
    ContentsType,
    GenerationConfigType,
    GenerationResponse,
    PartsType,
    SafetySettingsType,
)

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

VARIABLE_NAME_REGEX = r"(\{[^\W0-9]\w*\})"


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
        prompt_data: PartsType,
        *,
        variables: Optional[List[Dict[str, PartsType]]] = None,
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
            generation_config: A GenerationConfig object containing parameters for generation.
            model_name: Model Garden model resource name.
                Alternatively, a tuned model endpoint resource name can be provided.
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

        self.prompt_data = prompt_data
        self.variables = variables if variables else [{}]
        self.model_name = model_name
        self.generation_config = generation_config
        self.safety_settings = safety_settings
        self.system_instruction = system_instruction
        self.tools = tools
        self.tool_config = tool_config

    @property
    def prompt_data(self) -> PartsType:
        return self._prompt_data

    @property
    def variables(self) -> Optional[List[Dict[str, PartsType]]]:
        return self._variables

    @property
    def generation_config(self) -> Optional[GenerationConfig]:
        return self._generation_config

    @property
    def model_name(self) -> Optional[str]:
        return self._model_name

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

    @prompt_data.setter
    def prompt_data(self, prompt_data: PartsType) -> None:
        """Overwrites the existing saved local prompt_data.

        Args:
            prompt_data: A PartsType prompt.
        """
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

        generation_config = generation_config or self.generation_config
        safety_settings = safety_settings or self.safety_settings
        model_name = model_name or self.model_name
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

    def get_unassembled_prompt_data(self) -> PartsType:
        """Returns the prompt data, without any variables replaced."""
        return self.prompt_data

    def __str__(self) -> str:
        """Returns the prompt data as a string, without any variables replaced."""
        return str(self.prompt_data)

    def __repr__(self) -> str:
        """Returns a string representation of the unassembled prompt."""
        return f"Prompt(prompt_data='{self.prompt_data}', variables={self.variables})"
